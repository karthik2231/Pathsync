from unittest.mock import MagicMock, patch
import pytest
from app.services.matcher import rank_candidates_for_job

def test_stage2_correlation_with_hire_outcomes():
    # We want to prove that feedback incorporation changes rankings
    # where Stage 1 (pure vector similarity) has Cand 1 > Cand 2,
    # but Stage 2 (with gap + hire_outcomes feedback) pushes Cand 2 > Cand 1
    
    db = MagicMock()
    
    # Mocking out the complex DB querying inside `rank_candidates_for_job`
    # Instead, we will directly mock the helper vectors and gap report returns
    
    with patch('app.services.matcher._calc_job_vector') as mock_jb, \
         patch('app.services.matcher._calc_candidate_vector') as mock_cb, \
         patch('app.services.matcher.cosine_similarity') as mock_cos, \
         patch('app.services.matcher.compute_skill_gap') as mock_gap:
             
        mock_jb.return_value = [1.0, 1.0]
        mock_cb.return_value = [1.0, 1.0] # Return dummy arrays
        
        # db.query responses
        def q_side_effect(model):
            m = MagicMock()
            if model.__name__ == 'JobPosting':
                m.filter_by.return_value.first.return_value = MagicMock(id=1)
            elif model.__name__ == 'CandidateProfile':
                # Return two candidates
                m.all.return_value = [(1, "Cand 1"), (2, "Cand 2")]
            elif model.__name__ == 'HireOutcome':
                # Cand 2 was previously hired!
                hired_outcome = MagicMock()
                hired_outcome.candidate_id = 2
                hired_outcome.outcome.name = "hired"
                m.filter.return_value.all.return_value = [hired_outcome]
            return m
            
        db.query.side_effect = q_side_effect
        
        # Let Cand 1 have slightly better Cosine Similarity (Stage 1)
        # So Stage 1 ranks: Cand 1 (90%), Cand 2 (85%)
        def cos_side_effect(vec1, vec2):
            # Using nonlocal tracker inside mock, but simplified:
            pass
            
        # We can just mock the explicit returns tied to the Candidate IDs
        mock_cos.side_effect = lambda v1, v2: 0.90 if id(v1) == id(v2) else 0.85 
        # Actually it's easier to mock `cosine_similarity` such that order tracks calls
        mock_cos.side_effect = [0.90, 0.85] # Cand 1, Cand 2
        
        # Let both candidate have identical Skill Gap Report scores without feedback (e.g. 80.0)
        gap_rep = MagicMock()
        gap_rep.match_score = 80.0
        gap_rep.matched_skills = []
        gap_rep.hard_gaps = []
        gap_rep.soft_gaps = []
        gap_rep.summary = "Test summary"
        mock_gap.return_value = gap_rep
        
        # Executing the function
        results = rank_candidates_for_job(1, db, limit=10)
        
        # Mathematics check:
        # Cand 1: Cosine 0.90. Score = 0.6*80 + 0.4*90 = 48 + 36 = 84.0
        # Cand 2: Cosine 0.85. Score = 0.6*80 + 0.4*85 = 48 + 34 = 82.0
        # BUT Cand 2 gets +5.0 feedback boost. Cand 2 Score = 87.0
        
        # Thus, Correlation with hire logic reverses Stage 1!
        assert len(results) == 2
        assert results[0]["candidate_id"] == 2 # Ranked first
        assert results[0]["match_score"] == 87.0
        
        assert results[1]["candidate_id"] == 1 # Ranked second
        assert results[1]["match_score"] == 84.0
