from typing import List
from ..schemas.product import Product
from ..services.scoring import ScoringEngine

class RankingAgent:
    """Agent responsible for computing scores and ranking products."""
    
    async def run(self, products: List[Product]) -> List[Product]:
        print(f"[RankingAgent] Computing scores and ranking {len(products)} products...")
        
        # Compute final scores
        scored_products = ScoringEngine.compute_scores(products)
        
        # Rank by final score
        ranked_products = ScoringEngine.rank_products(scored_products)
        
        print(f"[RankingAgent] Ranking complete.")
        return ranked_products
