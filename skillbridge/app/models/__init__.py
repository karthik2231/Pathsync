import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base

class UserRole(str, enum.Enum):
    CANDIDATE = "candidate"
    EMPLOYER = "employer"
    ADMIN = "admin"

class JobStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    DRAFT = "draft"

class ImportanceLevel(str, enum.Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"

class HireOutcomeEnum(str, enum.Enum):
    HIRED = "hired"
    REJECTED = "rejected"
    NO_RESPONSE = "no_response"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    employer_profile = relationship("Employer", back_populates="user", uselist=False)

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    name = Column(String, nullable=False)
    headline = Column(String)
    location = Column(String)
    years_experience = Column(Float)
    raw_resume_text = Column(Text)
    parsed_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="candidate_profile")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    matches = relationship("SkillMatch", back_populates="candidate")
    hire_outcomes = relationship("HireOutcome", back_populates="candidate")
    recommendations = relationship("LearningRecommendation", back_populates="candidate")

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String, nullable=False)
    esco_uri = Column(String, nullable=True, index=True)
    proficiency_level = Column(Integer) # 1-5 scale
    source = Column(String) # e.g. "resume", "self-declared"
    embedding = Column(Vector(384))

    candidate = relationship("CandidateProfile", back_populates="skills")

class Employer(Base):
    __tablename__ = "employers"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    company_name = Column(String, nullable=False)
    industry = Column(String)
    size = Column(String)
    verified = Column(Boolean, default=False)

    user = relationship("User", back_populates="employer_profile")
    jobs = relationship("JobPosting", back_populates="employer", cascade="all, delete-orphan")

class JobPosting(Base):
    __tablename__ = "job_postings"
    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("employers.user_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String)
    remote_ok = Column(Boolean, default=False)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    status = Column(Enum(JobStatus), default=JobStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employer = relationship("Employer", back_populates="jobs")
    required_skills = relationship("JobRequiredSkill", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("SkillMatch", back_populates="job")
    hire_outcomes = relationship("HireOutcome", back_populates="job")

class JobRequiredSkill(Base):
    __tablename__ = "job_required_skills"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String, nullable=False)
    esco_uri = Column(String, nullable=True, index=True)
    importance = Column(Enum(ImportanceLevel), default=ImportanceLevel.PREFERRED)
    min_proficiency = Column(Integer)
    embedding = Column(Vector(384))

    job = relationship("JobPosting", back_populates="required_skills")

class SkillMatch(Base):
    __tablename__ = "skill_matches"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True)
    match_score = Column(Float, nullable=False) # e.g. 0 to 1.0 or 0 to 100
    gap_skills = Column(JSON) # e.g. [{"skill": "Docker", "importance": "required"}]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candidate = relationship("CandidateProfile", back_populates="matches")
    job = relationship("JobPosting", back_populates="matches")

class HireOutcome(Base):
    __tablename__ = "hire_outcomes"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True)
    outcome = Column(Enum(HireOutcomeEnum), nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    candidate = relationship("CandidateProfile", back_populates="hire_outcomes")
    job = relationship("JobPosting", back_populates="hire_outcomes")

class LearningRecommendation(Base):
    __tablename__ = "learning_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String, nullable=False)
    course_title = Column(String)
    course_url = Column(String)
    platform = Column(String)
    estimated_hours = Column(Float)

    candidate = relationship("CandidateProfile", back_populates="recommendations")

class SkillsTaxonomy(Base):
    __tablename__ = "skills_taxonomy"
    uri = Column(String, primary_key=True)
    preferred_label = Column(String, nullable=False, index=True)
    alt_labels = Column(JSON) # Array of synonym strings
