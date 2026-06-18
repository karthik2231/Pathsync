from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

# --- Auth Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str # "candidate", "employer", "admin"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    class Config:
        from_attributes = True

# --- Candidate Profile Schemas ---
class CandidateProfileResponse(BaseModel):
    user_id: int
    name: str
    headline: Optional[str]
    location: Optional[str]
    years_experience: Optional[float]
    class Config:
        from_attributes = True

class CandidateSkillResponse(BaseModel):
    id: int
    skill_name: str
    esco_uri: Optional[str]
    proficiency_level: Optional[int]
    source: Optional[str]
    class Config:
        from_attributes = True

# --- Job Postings Schemas ---
class JobCreate(BaseModel):
    title: str
    description: str
    location: Optional[str]
    remote_ok: bool = False
    salary_min: Optional[int]
    salary_max: Optional[int]

class JobResponse(JobCreate):
    id: int
    employer_id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- Matching Summary Schemas ---
class MatchResultResponse(BaseModel):
    candidate_id: int
    job_id: int
    match_score: float
    gap_skills: Optional[List[dict]]
    class Config:
        from_attributes = True
