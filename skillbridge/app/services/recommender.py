import json
import os
import math
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import SkillMatch, LearningRecommendation, JobPosting
from app.services.skill_gap import GapReport

class CourseCard(BaseModel):
    title: str
    platform: str
    url: str
    hours: int
    level: str

class Phase(BaseModel):
    week_range: str
    focus: str
    courses: List[CourseCard]
    milestone: str

class LearningPath(BaseModel):
    target_role: str
    total_hours: int
    weeks_to_ready: int
    phases: List[Phase]

COURSE_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'courses.json')

def load_courses():
    try:
        with open(COURSE_DB_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        import logging
        logging.getLogger(__name__).warning("courses.json not found, using empty DB.")
        return {}

def get_learning_path(candidate_id: int, job_id: int, gap_report: GapReport, db: Session) -> LearningPath:
    COURSES_DB = load_courses()
    
    # Step 1: Prioritize gaps
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    target_role = job.title if job else "Target Role"
    
    # Analyze cross-job frequent missing skills (top 5 matched jobs)
    top_matches = db.query(SkillMatch).filter(
        SkillMatch.candidate_id == candidate_id
    ).order_by(SkillMatch.match_score.desc()).limit(5).all()
    
    gap_freq = {}
    for match in top_matches:
        if match.gap_skills:
            for g in match.gap_skills:
                skill_name = g.get('skill')
                if skill_name:
                    gap_freq[skill_name] = gap_freq.get(skill_name, 0) + 1
                    
    all_gaps = list(set(gap_report.hard_gaps + gap_report.soft_gaps))
    
    def sort_key(skill):
        is_hard = 1 if skill in gap_report.hard_gaps else 0
        freq = gap_freq.get(skill, 0)
        # Sort primary by hard requirement, Secondary by overall frequency
        return (is_hard, freq) 
        
    all_gaps.sort(key=sort_key, reverse=True)
    top_5_gaps = all_gaps[:5]
    
    # Step 2 & 3: Sequencing Paths
    phases = []
    total_hours = 0
    current_week = 1
    
    # Clear prior recommendations for this candidate/job combination broadly
    db.query(LearningRecommendation).filter(
        LearningRecommendation.candidate_id == candidate_id
    ).delete()
    
    for skill in top_5_gaps:
        courses = COURSES_DB.get(skill, [])
        if not courses:
            courses = [{
                "title": f"Complete {skill} Bootcamp",
                "platform": "freeCodeCamp",
                "url": f"https://www.youtube.com/results?search_query={skill}+course",
                "hours": 10,
                "level": "Beginner"
            }]
            
        selected_course = courses[0]
        
        # Persist to DB table
        rec = LearningRecommendation(
            candidate_id=candidate_id,
            skill_name=skill,
            course_title=selected_course["title"],
            course_url=selected_course["url"],
            platform=selected_course["platform"],
            estimated_hours=selected_course["hours"]
        )
        db.add(rec)
        
        hours = selected_course["hours"]
        weeks_needed = math.ceil(hours / 10.0) # Assume 10hrs a week limit
        end_week = current_week + weeks_needed - 1
        
        week_str = f"Week {current_week}" if current_week == end_week else f"Week {current_week}-{end_week}"
        
        phases.append(Phase(
            week_range=week_str,
            focus=skill,
            courses=[CourseCard(**c) for c in courses[:2]], # Supply up to 2 options (1 priority, 1 fallback/alternative)
            milestone=f"Implement basic {skill} concepts in a functional project"
        ))
        
        total_hours += hours
        current_week = end_week + 1
        
    db.commit()
    
    weeks_to_ready = math.ceil(total_hours / 10.0)
    
    return LearningPath(
        target_role=target_role,
        total_hours=total_hours,
        weeks_to_ready=weeks_to_ready,
        phases=phases
    )
