from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.recommender import get_learning_path, LearningPath
from app.services.skill_gap import compute_skill_gap

router = APIRouter()

@router.get("/{candidate_id}/learning-path", response_model=LearningPath)
async def generate_learning_path_route(candidate_id: int, job_id: int, db: Session = Depends(get_db)):
    """Provides prioritized learning path recommendations mapped out week-over-week based on candidate's hard and soft gaps for a specific job."""
    
    # 1. First trigger or gather the dynamic gap calculation context
    gap_report = compute_skill_gap(candidate_id, job_id, db)
    
    # 2. Compile Path execution 
    path = get_learning_path(candidate_id, job_id, gap_report, db)
    return path
