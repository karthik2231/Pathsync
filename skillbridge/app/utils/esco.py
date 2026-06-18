import httpx
import logging
import asyncio
import sqlite3
import os
import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logger = logging.getLogger(__name__)

# Guarantee correct data tree
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)
CACHE_DB = os.path.join(DATA_DIR, 'skills_cache.db')

class NormalizedSkill(BaseModel):
    name: str
    esco_uri: Optional[str]
    alt_labels: List[str]

def init_cache_db():
    with sqlite3.connect(CACHE_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS esco_skills (
                skill_name TEXT PRIMARY KEY,
                uri TEXT,
                preferred_label TEXT,
                alt_labels TEXT
            )
        """)

init_cache_db()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
)
async def fetch_esco_api(url: str, params: dict):
    """Network wrapper hitting external ESCO APIs with Exponential Backoff."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()

async def search_esco_skill(skill_name: str) -> Optional[Dict[str, Any]]:
    """Lookup skill in local SQLite fast-cache, routing to ESCO API if missing."""
    with sqlite3.connect(CACHE_DB) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM esco_skills WHERE skill_name COLLATE NOCASE = ?", (skill_name,))
        row = cur.fetchone()
        if row:
            if row['uri']:
                return {
                    "uri": row['uri'],
                    "preferredLabel": row['preferred_label'],
                    "altLabels": json.loads(row['alt_labels']) if row['alt_labels'] else []
                }
            return None # Processed a cached negative result (hit DB, but it's null explicitly)

    url = "https://ec.europa.eu/esco/api/search"
    params = {"text": skill_name, "type": "skill", "language": "en"}
    
    try:
        data = await fetch_esco_api(url, params)
        items = data.get("_embedded", {}).get("results", [])
        if items:
            best = items[0]
            uri = best.get("uri")
            pref_label = best.get("title", best.get("preferredLabel", skill_name))
            
            with sqlite3.connect(CACHE_DB) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO esco_skills (skill_name, uri, preferred_label, alt_labels) VALUES (?, ?, ?, ?)",
                    (skill_name, uri, pref_label, json.dumps([]))
                )
            return {"uri": uri, "preferredLabel": pref_label, "altLabels": []}
            
    except Exception as e:
        logger.warning(f"ESCO API lookup failed for skill '{skill_name}': {e}")
        
    with sqlite3.connect(CACHE_DB) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO esco_skills (skill_name, uri, preferred_label, alt_labels) VALUES (?, ?, ?, ?)",
            (skill_name, None, skill_name, "[]")
        )
    return None

async def normalize_skills(raw_skills: List[str]) -> List[NormalizedSkill]:
    """Batch-level deduplication handler grouping ESCO queries asynchronously."""
    unique_skills = list(set(raw_skills))
    tasks = [search_esco_skill(s) for s in unique_skills]
    api_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    results = []
    seen_uris = set()
    
    for raw_skill, esco_data in zip(unique_skills, api_results):
        if isinstance(esco_data, Exception):
            logger.error(f"Error normalizing {raw_skill}: {esco_data}")
            esco_data = None
            
        if esco_data and esco_data["uri"]:
            uri = esco_data["uri"]
            if uri not in seen_uris: # deduplicate identical ESCO URIs
                seen_uris.add(uri)
                results.append(NormalizedSkill(
                    name=esco_data["preferredLabel"],
                    esco_uri=uri,
                    alt_labels=esco_data["altLabels"]
                ))
        else:
            results.append(NormalizedSkill(
                name=raw_skill,
                esco_uri=None,
                alt_labels=[]
            ))
            
    return results

async def get_related_skills(esco_uri: str) -> List[str]:
    """Extract narrower/broader taxonomy structures for horizontal suggestions."""
    url = "https://ec.europa.eu/esco/api/resource/skill"
    params = {"uri": esco_uri, "language": "en"}
    try:
        data = await fetch_esco_api(url, params)
        related = data.get("_links", {}).get("narrowerSkill", []) + data.get("_links", {}).get("broaderSkill", [])
        return [r.get("title") for r in related if r.get("title")]
    except Exception as e:
        logger.warning(f"Failed to fetch related skills for {esco_uri}: {e}")
        return []

async def build_local_taxonomy_cache():
    """Initial bootstrapping routine to pull Top-500 nodes into Postgres DB."""
    from app.database import SessionLocal
    from app.models import SkillsTaxonomy
    
    db = SessionLocal()
    try:
        if db.query(SkillsTaxonomy).first():
            return
            
        logger.info("Initializing Top-500 ESCO Taxonomy cache...")
        url = "https://ec.europa.eu/esco/api/search"
        params = {"type": "skill", "language": "en", "limit": 500}
        
        data = await fetch_esco_api(url, params)
        items = data.get("_embedded", {}).get("results", [])
        
        for item in items:
            uri = item.get("uri")
            if not uri: continue
            
            tax = SkillsTaxonomy(
                uri=uri,
                preferred_label=item.get("title", ""),
                alt_labels=[]
            )
            # Use merge logic to emulate upserts robustly
            db.merge(tax)
            
        db.commit()
    except Exception as e:
        logger.error(f"Taxonomy cache build failed: {e}")
    finally:
        db.close()
