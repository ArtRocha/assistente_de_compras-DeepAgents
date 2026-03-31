import asyncio
from typing import List
from ..tools.search_api import SearchAPI
from ..tools.scraper import Scraper
from ..schemas.product import Product
from ..services.normalization import NormalizationService


class ProductDiscoveryAgent:
    """Finds candidate offers for the requested product."""

    def __init__(self):
        self.search_tool = SearchAPI()
        self.scraper_tool = Scraper()

    async def run(self, query: str) -> List[Product]:
        print(f"[ProductDiscoveryAgent] Pesquisando ofertas para: {query}")

        search_results, scraped_results = await asyncio.gather(
            self.search_tool.search(query),
            self.scraper_tool.scrape(query),
        )

        all_products = search_results + scraped_results
        normalized = NormalizationService.normalize_list(all_products)
        relevant = [p for p in normalized if NormalizationService.fuzzy_match(query, p.title)]

        print(f"[ProductDiscoveryAgent] {len(relevant)} ofertas relevantes encontradas.")
        return relevant
