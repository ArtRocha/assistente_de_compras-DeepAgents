import asyncio
import re
from typing import List

from ..schemas.product import Product
from ..services.normalization import NormalizationService
from .search_api import SearchAPI


class Scraper:
    """Secondary Google Shopping scraper that performs live extraction with query variations."""

    def __init__(self):
        self.search_api = SearchAPI()

    async def scrape(self, query: str) -> List[Product]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        print(f"[Scraper] Iniciando scraping para consulta base: '{normalized_query}'")
        query_variants = self._build_query_variants(normalized_query)
        print(f"[Scraper] Variações geradas: {query_variants}")
        if not query_variants:
            return []

        tasks = [self.search_api.search(variant) for variant in query_variants]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        combined: List[Product] = []
        for i, result in enumerate(results):
            variant = query_variants[i]
            if isinstance(result, Exception):
                print(f"[Scraper] ERRO na variação '{variant}': {result}")
                continue
            print(f"[Scraper] Variação '{variant}' retornou {len(result)} resultados.")
            combined.extend(result)

        if not combined:
            return []

        normalized = NormalizationService.normalize_list(combined)
        print(f"[Scraper] Total consolidado antes do filtro: {len(normalized)}")
        relevant = [p for p in normalized if NormalizationService.fuzzy_match(normalized_query, p.title)]
        print(f"[Scraper] Total após filtro de relevância (fuzzy match): {len(relevant)}")
        
        final_results = relevant[:20]
        print(f"[Scraper] Lista final retornou {len(final_results)} resultados válidos.")
        return final_results

    def _build_query_variants(self, query: str) -> List[str]:
        base = query.strip()
        compact = re.sub(r"\s+", " ", base)

        variants = [
            compact,
            f"{compact} preco",
            f"{compact} comprar",
            self._remove_common_prefixes(compact),
        ]

        seen = set()
        unique_variants: List[str] = []
        for variant in variants:
            candidate = variant.strip()
            if not candidate:
                continue
            key = candidate.lower()
            if key in seen:
                continue
            seen.add(key)
            unique_variants.append(candidate)

        return unique_variants[:4]

    def _remove_common_prefixes(self, query: str) -> str:
        lowered = query.lower().strip()
        prefixes = [
            "melhores precos de ",
            "melhores preços de ",
            "preco de ",
            "preço de ",
            "onde comprar ",
            "comprar ",
        ]
        for prefix in prefixes:
            if lowered.startswith(prefix):
                return query[len(prefix):].strip()
        return query
