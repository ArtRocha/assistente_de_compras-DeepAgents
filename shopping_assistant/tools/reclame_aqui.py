import asyncio
from typing import Dict

class ReclameAquiTool:
    """Mock Tool for retrieving store trust data."""
    
    async def get_store_trust(self, store_name: str) -> Dict[str, float]:
        # Simulate network latency
        await asyncio.sleep(0.3)
        
        # Mock trust data for common stores
        trust_db = {
            "Amazon": {"rating": 8.5, "response_rate": 0.98, "resolution_rate": 0.92},
            "Mercado Livre": {"rating": 7.2, "response_rate": 0.85, "resolution_rate": 0.78},
            "Magalu": {"rating": 9.1, "response_rate": 0.99, "resolution_rate": 0.95},
            "OLX": {"rating": 6.0, "response_rate": 0.70, "resolution_rate": 0.65},
        }
        
        data = trust_db.get(store_name, {"rating": 5.0, "response_rate": 0.5, "resolution_rate": 0.5})
        
        # Normalize rating to [0, 1]
        score = data["rating"] / 10.0
        
        return {
            "rating": data["rating"],
            "response_rate": data["response_rate"],
            "resolution_rate": data["resolution_rate"],
            "score": score
        }
