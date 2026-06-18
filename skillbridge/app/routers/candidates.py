from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads a PDF resume to be parsed by LLM (PyMuPDF + OpenAI)."""
    # Logic to call services.resume_parser
    return {"message": f"Resume {file.filename} parsed successfully.", "skills_extracted": []}

@router.get("/{id}/profile", response_model=schemas.CandidateProfileResponse)
async def get_profile(id: int, db: Session = Depends(get_db)):
    """Retrieve Candidate details (headline, location, years_experience)."""
    return schemas.CandidateProfileResponse(user_id=id, name="John Doe", headline="AI Engineer", location="Remote", years_experience=5)

@router.get("/{id}/skills")
async def get_skills(id: int, db: Session = Depends(get_db)):
    """List out all skills associated with candidate."""
    return [{"skill_name": "Python", "proficiency_level": 4}]

@router.get("/{id}/gap-report/{job_id}")
async def get_gap_report(id: int, job_id: int, db: Session = Depends(get_db)):
    """Computes specific skill gaps for a candidate relative to a job JD."""
    # Logic to call services.skill_gap
    return {"match_score": 0.82, "gaps": [{"skill": "Docker", "importance": "required"}]}
