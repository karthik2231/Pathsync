import numpy as np
import logging
from typing import List

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    # all-MiniLM-L6-v2 outputs 384 dimensional vectors as required by db schema
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    logger.warning(f"Failed to load sentence-transformer model: {e}")
    model = None

def get_embedding(text: str) -> List[float]:
    """Generates a 384-dim semantic embedding using sentence-transformers."""
    if model:
        return model.encode(text).tolist()
    # Fallback placeholder if model not loaded (useful for quick CI testing)
    return [0.0] * 384

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two vectors."""
    if not v1 or not v2: 
        return 0.0
    
    vec1 = np.array(v1)
    vec2 = np.array(v2)
    
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return float(np.dot(vec1, vec2) / (norm1 * norm2))
