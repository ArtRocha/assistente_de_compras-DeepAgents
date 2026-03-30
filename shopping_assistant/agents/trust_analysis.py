import asyncio
from typing import List
from ..tools.reclame_aqui import ReclameAquiTool
from ..schemas.product import Product

class TrustAnalysisAgent:
    """Agent responsible for analyzing store credibility."""
    
    def __init__(self):
        self.trust_tool = ReclameAquiTool()
        
    async def run(self, products: List[Product]) -> List[Product]:
        print(f"[TrustAnalysisAgent] Analyzing trust for {len(products)} products...")
        
        # Extract unique stores
        stores = list(set(p.store for p in products))
        
        # Get trust data in parallel
        trust_tasks = [self.trust_tool.get_store_trust(store) for store in stores]
        trust_results = await asyncio.gather(*trust_tasks)
        
        # Map store to trust score
        store_trust_map = dict(zip(stores, [res["score"] for res in trust_results]))
        
        # Assign trust scores to products
        for p in products:
            p.trust_score = store_trust_map.get(p.store, 0.5)
            
        print(f"[TrustAnalysisAgent] Trust analysis complete.")
        return products
