import pytest
from unittest.mock import MagicMock
from app.services.skill_gap import compute_skill_gap
from app.models import CandidateSkill, JobRequiredSkill, SkillMatch

class MockImportance:
    def __init__(self, name):
        self.name = name

def test_skill_gap_computation():
    db = MagicMock()

    # Job requirements
    js1 = JobRequiredSkill(skill_name="Python", importance=MockImportance("required"), min_proficiency=3, embedding=[0.9, 0.1])
    js1.esco_uri = "python"
    
    js2 = JobRequiredSkill(skill_name="Docker", importance=MockImportance("required"), min_proficiency=3, embedding=[0.1, 0.9])
    js2.esco_uri = "docker"
    
    js3 = JobRequiredSkill(skill_name="AWS", importance=MockImportance("preferred"), min_proficiency=4, embedding=[0.5, 0.5])
    js3.esco_uri = "aws"
    
    # Candidate Skills
    cs1 = CandidateSkill(skill_name="Python", proficiency_level=4, esco_uri="python", embedding=[0.9, 0.1])
    cs2 = CandidateSkill(skill_name="AWS", proficiency_level=2, esco_uri="aws", embedding=[0.5, 0.5]) # Low prof
    
    def side_effect(model):
        m = MagicMock()
        if model == CandidateSkill:
            m.filter.return_value.all.return_value = [cs1, cs2]
        elif model == JobRequiredSkill:
            m.filter.return_value.all.return_value = [js1, js2, js3]
        elif model == SkillMatch:
            # Mock DB insert check
            m.filter_by.return_value.first.return_value = None
        return m
        
    db.query.side_effect = side_effect
    
    report = compute_skill_gap(1, 1, db)
    
    assert "Python" in report.matched_skills
    assert "AWS" in report.matched_skills
    assert "Docker" in report.hard_gaps
    
    # The Gap Penalties
    # Required skills matched: 1/2 -> 50% * 70 = 35
    # Preferred skills matched: 1/1 -> 100% * 30 = 30
    # Penalty on AWS: Need=4, Have=2. (-3 * 2 = 6)
    # Total = 35 + 30 - 6 = 59.0
    assert report.match_score == 59.0
    
    # Verify summary structure matches instructions exactly
    assert "You match 59% of this role." in report.summary
    assert "missing Docker" in report.summary
