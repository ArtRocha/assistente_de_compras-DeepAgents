import asyncio
from .product_discovery import ProductDiscoveryAgent
from .trust_analysis import TrustAnalysisAgent
from .ranking import RankingAgent
from typing import List, Dict, Any

class OrchestratorAgent:
    """Main orchestrator for the multi-agent shopping assistant."""
    
    def __init__(self):
        self.discovery_agent = ProductDiscoveryAgent()
        self.trust_agent = TrustAnalysisAgent()
        self.ranking_agent = RankingAgent()
        
    async def process_query(self, query: str) -> List[Dict[str, Any]]:
        print(f"[Orchestrator] Starting processing for: '{query}'")
        
        # 1. Discovery
        products = await self.discovery_agent.run(query)
        
        if not products:
            print("[Orchestrator] No products found.")
            return []
            
        # 2. Trust Analysis
        products_with_trust = await self.trust_agent.run(products)
        
        # 3. Ranking
        ranked_results = await self.ranking_agent.run(products_with_trust)
        
        print("[Orchestrator] Finished processing.")
        return [p.model_dump() for p in ranked_results]
