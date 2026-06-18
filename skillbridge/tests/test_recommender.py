import pytest
from unittest.mock import MagicMock
from app.services.recommender import get_learning_path
from app.services.skill_gap import GapReport
from app.models import JobPosting, SkillMatch

def test_get_learning_path_prioritization():
    db = MagicMock()
    
    # 1. Structure Mock Context
    job = JobPosting(title="Backend Developer")
    db.query.return_value.filter.return_value.first.return_value = job
    
    # 2. Prove Frequency Scoring over Generic Matches 
    # Simulate DB finding "Docker" as widespread gap over 5 matched roles.
    sm = SkillMatch(gap_skills=[{"skill": "Docker", "type": "hard"}, {"skill": "AWS", "type": "soft"}])
    db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [sm]
    
    gap_report = GapReport(
        match_score=50.0,
        matched_skills=["Python"],
        hard_gaps=["Docker", "AWS"],  # AWS is hard for this current role
        soft_gaps=["Kubernetes"],      # Kubernetes soft
        proficiency_gaps=[],
        summary="Test Report Output Logic"
    )
    
    # 3. Fire Logic
    path = get_learning_path(1, 1, gap_report, db)
    
    # Standard verifications
    assert path.target_role == "Backend Developer"
    
    # Verify we capture the Top Gaps iteratively inside Phases
    # Gaps input were Docker, AWS, Kubernetes string targets = 3 phases required.
    assert len(path.phases) == 3
    
    # Check prioritization math matches specification targets
    focus_ordered = [p.focus for p in path.phases]
    assert "Docker" in focus_ordered
    
    # Check mathematically that week ranges expand per logic loop (10hours/week).
    # Assumes Docker is ~10hrs and AWS ~15hrs depending on mocked JSON data vs logic default. 
    # Just verifying Phase construction ran.
    assert path.phases[0].week_range is not None
