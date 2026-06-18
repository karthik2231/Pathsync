import numpy as np
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from cachetools import cached, TTLCache

from app.models import CandidateSkill, JobRequiredSkill, JobPosting, CandidateProfile, HireOutcome
from app.utils.embeddings import cosine_similarity
from app.services.skill_gap import compute_skill_gap

logger = logging.getLogger(__name__)

# TTL Cache for 1 hour
matcher_cache = TTLCache(maxsize=2000, ttl=3600)

def _calc_candidate_vector(candidate_id: int, db: Session) -> Optional[np.ndarray]:
    skills = db.query(CandidateSkill).filter_by(candidate_id=candidate_id).all()
    if not skills: return None
    
    vectors, weights = [], []
    for s in skills:
        if s.embedding:
            vectors.append(np.array(s.embedding))
            weights.append(s.proficiency_level or 1.0)
            
    if not vectors: return None
    return np.average(vectors, axis=0, weights=weights)

def _calc_job_vector(job_id: int, db: Session) -> Optional[np.ndarray]:
    skills = db.query(JobRequiredSkill).filter_by(job_id=job_id).all()
    if not skills: return None
        
    vectors, weights = [], []
    for s in skills:
        if s.embedding:
            vectors.append(np.array(s.embedding))
            weight = 1.0 if s.importance.name.lower() == "required" else 0.5
            weights.append(weight)
            
    if not vectors: return None
    return np.average(vectors, axis=0, weights=weights)

@cached(matcher_cache)
def rank_candidates_for_job(job_id: int, db: Session, limit: int = 20) -> List[Dict[str, Any]]:
    """Employer view: Ranks candidates for a specific JD posting."""
    job = db.query(JobPosting).filter_by(id=job_id).first()
    if not job: return []
        
    job_vector = _calc_job_vector(job_id, db)
    if job_vector is None: return []

    all_candidates = db.query(CandidateProfile.user_id, CandidateProfile.name).all()
    
    # STAGE 1: Bi-encoder retrieval (Fast Cosine Sim)
    stage1 = []
    for cand_id, name in all_candidates:
        cand_vector = _calc_candidate_vector(cand_id, db)
        if cand_vector is not None:
            sim = cosine_similarity(job_vector, cand_vector)
            stage1.append((cand_id, name, sim))
            
    # Sort top 50
    stage1.sort(key=lambda x: x[2], reverse=True)
    top_50 = stage1[:50]
    
    # Feedback loader
    outcomes = db.query(HireOutcome).filter(HireOutcome.job_id == job_id).all()
    hired_candidates = {o.candidate_id for o in outcomes if o.outcome.name.lower() == 'hired'}
    
    # STAGE 2: Cross-encoder reranking
    stage2_results = []
    for cand_id, name, sim in top_50:
        gap_report = compute_skill_gap(cand_id, job_id, db)
        
        # Blended final score
        final_score = (0.6 * gap_report.match_score) + (0.4 * (sim * 100))
        
        # Feedback modification penalty/boost
        if cand_id in hired_candidates:
            final_score += 5.0
            
        final_score = min(100.0, final_score)
            
        stage2_results.append({
            "candidate_id": cand_id,
            "name": name,
            "match_score": round(final_score, 2),
            "matched_skills": gap_report.matched_skills,
            "gap_count": len(gap_report.hard_gaps) + len(gap_report.soft_gaps),
            "recommendation": gap_report.summary,
            "gap_report": gap_report.model_dump()
        })
        
    stage2_results.sort(key=lambda x: x["match_score"], reverse=True)
    return stage2_results[:limit]

@cached(matcher_cache)
def rank_jobs_for_candidate(candidate_id: int, db: Session, limit: int = 20) -> List[Dict[str, Any]]:
    """Candidate view: Ranks jobs suitable for a candidate user."""
    cand_vector = _calc_candidate_vector(candidate_id, db)
    if cand_vector is None: return []

    all_jobs = db.query(JobPosting.id, JobPosting.title, JobPosting.employer_id).all()
    
    stage1 = []
    for jid, title, eid in all_jobs:
        job_vector = _calc_job_vector(jid, db)
        if job_vector is not None:
            sim = cosine_similarity(job_vector, cand_vector)
            stage1.append((jid, title, eid, sim))
            
    stage1.sort(key=lambda x: x[3], reverse=True)
    top_50 = stage1[:50]
    
    # Outcomes to observe previous hires by employers for this candidate vs roles
    # Normally check if candidate was hired in a similar role by checking role vectors, or just overall hired
    outcomes = db.query(HireOutcome).filter_by(candidate_id=candidate_id).all()
    previously_hired_job_ids = {o.job_id for o in outcomes if o.outcome.name.lower() == 'hired'}
    
    stage2_results = []
    for jid, title, eid, sim in top_50:
        gap_report = compute_skill_gap(candidate_id, jid, db)
        
        final_score = (0.6 * gap_report.match_score) + (0.4 * (sim * 100))
        if jid in previously_hired_job_ids:
            final_score += 5.0
            
        stage2_results.append({
            "job_id": jid,
            "title": title,
            "company_id": eid, # Note: Employer details usually nested
            "match_score": round(min(100.0, final_score), 2),
            "hard_gaps": gap_report.hard_gaps,
            "top_missing_skill": gap_report.hard_gaps[0] if gap_report.hard_gaps else (gap_report.soft_gaps[0] if gap_report.soft_gaps else None),
            "apply_url": f"/apply/{jid}"
        })
        
    stage2_results.sort(key=lambda x: x["match_score"], reverse=True)
    return stage2_results[:limit]
