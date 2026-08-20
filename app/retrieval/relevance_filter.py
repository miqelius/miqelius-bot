from typing import List, Dict, Any
from app.core.config import settings


class RelevanceFilter:
    @staticmethod
    def filter(chunks: List[Dict[str, Any]], threshold: float = None) -> List[Dict[str, Any]]:
        if threshold is None:
            threshold = settings.RELEVANCE_THRESHOLD
        
        # Normalize distances (smaller distance = higher relevance)
        # Distance is typically between 0 and 1 for cosine similarity
        # We filter out chunks with distance > threshold (less relevant)
        filtered = [
            chunk for chunk in chunks
            if 1 - chunk.get("distance", 0) > threshold  # Convert distance to similarity
        ]
        
        return filtered if filtered else chunks[:1]  # Always return at least one chunk
