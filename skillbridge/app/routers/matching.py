from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas

router = APIRouter()

@router.post("/run/{candidate_id}/{job_id}", response_model=schemas.MatchResultResponse)
async def run_match(candidate_id: int, job_id: int, db: Session = Depends(get_db)):
    """Manually trigger/force a matching computation."""
    # Logic to execute bi-encoder vector similarity and cross-encoder score
    return {"candidate_id": candidate_id, "job_id": job_id, "match_score": 0.90, "gap_skills": []}

@router.get("/results/{candidate_id}")
async def get_match_results(candidate_id: int, db: Session = Depends(get_db)):
    """Fetch best job matches for a specific candidate."""
    return [{"job_id": 1, "title": "Senior AI Engineer", "match_score": 0.90}]
