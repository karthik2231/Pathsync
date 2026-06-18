import json
import logging
from typing import List, Optional
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import JobPosting, JobRequiredSkill, Employer
from app.utils.esco import search_esco_skill
from app.utils.embeddings import get_embedding

logger = logging.getLogger(__name__)
client = AsyncOpenAI() # Requires OPENAI_API_KEY environment variable

class ExtractedSkill(BaseModel):
    name: str
    min_proficiency: int
    importance: str # "required" or "preferred"

class ParsedJD(BaseModel):
    title: str
    description: str
    location: str
    remote_ok: bool
    salary_min: Optional[int]
    salary_max: Optional[int]
    required_skills: List[ExtractedSkill]
    preferred_skills: List[ExtractedSkill]

async def LLM_jd_extraction(text: str) -> ParsedJD:
    """Uses GPT-4o-mini to convert raw Job Description text into structured metadata requirements."""
    system_prompt = '''You are an elite NLP Job Description parser. Extract out the exact hiring parameters from the provided JD text and return ONLY valid JSON with no conversational filler. Use this exact schema:
{
  "title": "string",
  "description": "string (create a concise 2-3 sentence summary of the core responsibilities)",
  "location": "string (or 'Remote')",
  "remote_ok": boolean,
  "salary_min": number (or null if not specified),
  "salary_max": number (or null if not specified),
  "required_skills": [{"name": "string", "min_proficiency": number_1_to_5, "importance": "required"}],
  "preferred_skills": [{"name": "string", "min_proficiency": number_1_to_5, "importance": "preferred"}]
}'''
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text[:15000]} # Safe truncation buffer
            ]
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return ParsedJD(**data)
    except Exception as e:
        logger.error(f"LLM parsing failed for Job Description: {e}")
        raise ValueError("Failed to extract structured schema metrics from JD")

async def parse_and_store_jd(employer_id: int, raw_text: str, db: Session) -> ParsedJD:
    """End-to-End Orchestrator: parses raw JD string, resolves ESCO uris, runs embedding model, and pushes to db."""
    logger.info(f"Initiating AI extraction sequence for employer JD ({employer_id})")
    
    # 1. Edge-case Safety: Establish employer mapping
    employer = db.query(Employer).filter(Employer.user_id == employer_id).first()
    if not employer:
        employer = Employer(user_id=employer_id, company_name=f"Enterprise {employer_id}")
        db.add(employer)
        db.commit()
        
    # 2. Run Heavy lifting text extraction
    parsed_data = await LLM_jd_extraction(raw_text)
    logger.info("LLM structural breakdown completed securely.")
    
    # 3. Mount Job configuration
    job = JobPosting(
        employer_id=employer_id,
        title=parsed_data.title,
        description=parsed_data.description,
        location=parsed_data.location,
        remote_ok=parsed_data.remote_ok,
        salary_min=parsed_data.salary_min,
        salary_max=parsed_data.salary_max,
        status="OPEN" # Assuming enum string compatibility
    )
    db.add(job)
    db.flush() # Force PostgreSQL assignment of primary key (job.id) required for relational mounts below
    
    # 4. Iteratively execute ESCO resolution bounds mapping via vector embeddings
    all_skills = parsed_data.required_skills + parsed_data.preferred_skills
    for skill in all_skills:
        
        # Async HTTP fetch to Europa API logic with exponential backoff and localized sqlite caching!
        esco_res = await search_esco_skill(skill.name)
        esco_uri = esco_res["uri"] if esco_res else None
        
        # Launch Vector math representation layer
        embedding = get_embedding(skill.name)
        
        db_skill = JobRequiredSkill(
            job_id=job.id,
            skill_name=skill.name[:255],
            esco_uri=esco_uri,
            importance=skill.importance.upper(),  # Maps mapping convention over cleanly
            min_proficiency=skill.min_proficiency,
            embedding=embedding
        )
        db.add(db_skill)
        
    db.commit()
    logger.info(f"System Successfully committed parsed representation to DB for Job ID #{job.id}")
    
    return parsed_data
