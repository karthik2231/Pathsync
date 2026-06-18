import fitz  # PyMuPDF
import json
import logging
from typing import List, Optional
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import CandidateProfile, CandidateSkill
from app.utils.esco import get_esco_uri
from app.utils.embeddings import get_embedding

logger = logging.getLogger(__name__)
client = AsyncOpenAI() # requires OPENAI_API_KEY environment variable

class SkillExtractor(BaseModel):
    name: str
    proficiency_estimate: int

class ExperienceExtractor(BaseModel):
    company: str
    title: str
    duration_months: int
    description: str

class EducationExtractor(BaseModel):
    institution: str
    degree: str
    field: str
    year: str

class ParsedResume(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    summary: str
    skills: List[SkillExtractor]
    experience: List[ExperienceExtractor]
    education: List[EducationExtractor]
    certifications: List[str]

async def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Uses PyMuPDF to extract text from PDF robustly, handling multi-column layouts."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            # get_text("blocks") returns a list of text blocks. We sort them top-to-bottom, left-to-right.
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: (b[1], b[0]))
            for b_tuple in blocks:
                text += b_tuple[4] + "\n"
        logger.info(f"Extracted {len(text)} characters from PDF.")
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        raise ValueError("Malformed PDF or unsupported format")

async def LLM_structured_extraction(text: str) -> ParsedResume:
    """Uses GPT-4o-mini to parse unstructured resume block logic into rigid JSON schema."""
    system_prompt = '''You are a strict resume parser. Extract the following from the resume text and return ONLY valid JSON with no extra text. Use this JSON schema:
{
  "name": "string", "email": "string", "phone": "string", "location": "string",
  "summary": "string",
  "skills": [{"name": "string", "proficiency_estimate": number_1_to_5}],
  "experience": [{"company": "string", "title": "string", "duration_months": number, "description": "string"}],
  "education": [{"institution": "string", "degree": "string", "field": "string", "year": "string"}],
  "certifications": ["string"]
}'''
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text[:15000]} # Truncate to avoid exploding context windows
            ]
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return ParsedResume(**data)
    except Exception as e:
        logger.error(f"LLM parsing failed: {e}")
        raise ValueError("Failed to extract structured data from resume")

async def parse_and_store_resume(file_bytes: bytes, user_id: int, db: Session) -> ParsedResume:
    """Orchestrates PDF reading -> LLM Extraction -> ESCO map -> Embs -> Postgres Write."""
    logger.info(f"Starting resume parsing orchestration for user {user_id}")
    
    # 1. Read PDF
    raw_text = await extract_text_from_pdf(file_bytes)
    
    # 2. LLM Extraction
    parsed_data = await LLM_structured_extraction(raw_text)
    
    # 3. DB Updates (Upsert CandidateProfile)
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
    if not profile:
        profile = CandidateProfile(user_id=user_id)
        db.add(profile)
    
    profile.name = parsed_data.name
    profile.headline = parsed_data.summary[:255] if parsed_data.summary else ""
    profile.location = parsed_data.location
    profile.raw_resume_text = raw_text
    
    total_months = sum(exp.duration_months for exp in parsed_data.experience) if parsed_data.experience else 0
    profile.years_experience = round(total_months / 12.0, 1)

    # Replace old skills
    db.query(CandidateSkill).filter(CandidateSkill.candidate_id == user_id).delete()
    db.flush()
    
    # 4. Normalize (ESCO) and Embed Skills
    for skill in parsed_data.skills:
        esco_uri = await get_esco_uri(skill.name)
        embedding = get_embedding(skill.name)
        
        db_skill = CandidateSkill(
            candidate_id=user_id,
            skill_name=skill.name[:255],
            esco_uri=esco_uri,
            proficiency_level=skill.proficiency_estimate,
            source="resume",
            embedding=embedding
        )
        db.add(db_skill)
    
    db.commit()
    logger.info(f"Successfully finalized parsing and saved DB records for candidate {user_id}")
    
    return parsed_data
