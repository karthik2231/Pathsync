from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import CandidateSkill, JobRequiredSkill, SkillMatch
from app.utils.embeddings import cosine_similarity

class ProficiencyGap(BaseModel):
    skill: str
    have: int
    need: int

class GapReport(BaseModel):
    match_score: float
    matched_skills: List[str]
    hard_gaps: List[str]
    soft_gaps: List[str]
    proficiency_gaps: List[ProficiencyGap]
    summary: str

def compute_skill_gap(candidate_id: int, job_id: int, db: Session) -> GapReport:
    """Computes gap analysis between Candidate profile and Job description."""
    
    # Step 1: Load Skills
    cand_skills = db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate_id).all()
    job_skills = db.query(JobRequiredSkill).filter(JobRequiredSkill.job_id == job_id).all()
    
    cand_esco_map = {cs.esco_uri: cs for cs in cand_skills if cs.esco_uri}
    cand_unmapped = [cs for cs in cand_skills if not cs.esco_uri]
    
    matched_skills = []
    hard_gaps = []
    soft_gaps = []
    proficiency_gaps = []
    
    total_required = 0
    total_preferred = 0
    matched_required = 0
    matched_preferred = 0
    
    # Step 2: Direct matches and mapping
    for req_skill in job_skills:
        is_required = req_skill.importance.name.lower() == "required"
        if is_required:
            total_required += 1
        else:
            total_preferred += 1
            
        matched_cand_skill = None
        
        # Match ESCO ontology primarily
        if req_skill.esco_uri and req_skill.esco_uri in cand_esco_map:
            matched_cand_skill = cand_esco_map[req_skill.esco_uri]
        else:
            # Match by Cosine Similarity >= 0.85
            best_sim = 0.0
            best_cs = None
            req_emb = req_skill.embedding
            
            # Sub-optimize by filtering candidates lacking ESCO URI if req_skill has one, 
            # but we'll scan all for highest confidence.
            scan_pool = cand_skills if not req_skill.esco_uri else cand_unmapped
            for cs in scan_pool:
                sim = cosine_similarity(cs.embedding, req_emb)
                if sim >= 0.85 and sim > best_sim:
                    best_sim = sim
                    best_cs = cs
            
            if best_cs:
                matched_cand_skill = best_cs
        
        if matched_cand_skill:
            matched_skills.append(req_skill.skill_name)
            if is_required:
                matched_required += 1
            else:
                matched_preferred += 1
                
            have_prof = matched_cand_skill.proficiency_level or 1
            need_prof = req_skill.min_proficiency or 1
            
            if have_prof < need_prof:
                proficiency_gaps.append(ProficiencyGap(
                    skill=req_skill.skill_name,
                    have=have_prof,
                    need=need_prof
                ))
        else:
            # Gaps
            if is_required:
                hard_gaps.append(req_skill.skill_name)
            else:
                soft_gaps.append(req_skill.skill_name)
                
    # Step 3: Gap Scoring Algorithm
    raw_score = 0.0
    if total_required > 0:
        raw_score += (matched_required / total_required) * 70.0
    elif total_preferred > 0:
        # If no hard reqs, preferred takes up 100% of score (rather than defaulting to 30)
        raw_score += (matched_preferred / total_preferred) * 100.0
        
    if total_preferred > 0 and total_required > 0:
        raw_score += (matched_preferred / total_preferred) * 30.0
        
    # Penalty calculation
    for pg in proficiency_gaps:
        raw_score -= 3.0 * (pg.need - pg.have)
        
    final_score = max(0.0, min(100.0, raw_score))
    
    # Step 4: Explanation Builder
    summary_gaps = []
    if hard_gaps:
        summary_gaps = hard_gaps[:3]
    elif soft_gaps:
        summary_gaps = soft_gaps[:3]
        
    str_gaps = ", ".join(summary_gaps) if summary_gaps else "no key skills"
    summary = f"You match {int(final_score)}% of this role. You have {len(matched_skills)} required/preferred skills, but are missing {str_gaps}."
    
    report = GapReport(
        match_score=round(final_score, 2),
        matched_skills=matched_skills,
        hard_gaps=hard_gaps,
        soft_gaps=soft_gaps,
        proficiency_gaps=proficiency_gaps,
        summary=summary
    )
    
    # DB Persistence
    match_record = db.query(SkillMatch).filter_by(candidate_id=candidate_id, job_id=job_id).first()
    if not match_record:
        match_record = SkillMatch(candidate_id=candidate_id, job_id=job_id)
        db.add(match_record)
        
    match_record.match_score = report.match_score
    match_record.gap_skills = [{"skill": s, "type": "hard"} for s in hard_gaps] + \
                              [{"skill": s, "type": "soft"} for s in soft_gaps]
    db.commit()
    
    return report
