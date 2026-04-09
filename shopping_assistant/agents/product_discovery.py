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
        normalized_query = query.strip()
        if not normalized_query:
            return []

        print(f"[ProductDiscoveryAgent] Pesquisando ofertas para: {normalized_query}")

        search_results = await self.search_tool.search(normalized_query)
        scraped_results: List[Product] = []

        # Scraper auxiliar (tambem live) apenas quando a busca principal vier fraca.
        if len(search_results) < 3:
            print("[ProductDiscoveryAgent] Busca principal com baixa cobertura; acionando scraper live.")
            scraped_results = await self.scraper_tool.scrape(normalized_query)

        all_products = search_results + scraped_results
        normalized = NormalizationService.normalize_list(all_products)
        relevant = [p for p in normalized if NormalizationService.fuzzy_match(normalized_query, p.title)]

        print(f"[ProductDiscoveryAgent] {len(relevant)} ofertas relevantes encontradas.")
        return relevant
