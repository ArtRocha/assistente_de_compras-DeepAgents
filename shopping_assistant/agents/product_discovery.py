import asyncio
from typing import List
from ..tools.search_api import SearchAPI
from ..tools.scraper import Scraper
from ..schemas.product import Product
from ..services.normalization import NormalizationService

class ProductDiscoveryAgent:
    """Agent responsible for finding products matching user query."""
    
    def __init__(self):
        self.search_tool = SearchAPI()
        self.scraper_tool = Scraper()
        
    async def run(self, query: str) -> List[Product]:
        print(f"[ProductDiscoveryAgent] Searching for: {query}")
        
        # Run search and scrape in parallel
        results = await asyncio.gather(
            self.search_tool.search(query),
            self.scraper_tool.scrape(query)
        )
        
        # Flatten and normalize
        all_products = [p for sublist in results for p in sublist]
        normalized = NormalizationService.normalize_list(all_products)
        
        # Filter by relevance (mock)
        relevant = [p for p in normalized if NormalizationService.fuzzy_match(query, p.title)]
        
        print(f"[ProductDiscoveryAgent] Found {len(relevant)} relevant products.")
        return relevant
