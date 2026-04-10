import json
from pathlib import Path
from typing import List

from ..tools.search_api import SearchAPI
from ..tools.scraper import Scraper
from ..schemas.product import Product
from ..services.normalization import NormalizationService
from ..llm.client import get_llm

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "config" / "prompts" / "discovery.txt"


class ProductDiscoveryAgent:
    """Busca e filtra ofertas de produto.

    Com Ollama disponível: o LLM interpreta os resultados e gera um raciocínio
    sobre quais produtos são realmente relevantes para a consulta.
    Sem Ollama: usa filtro determinístico por fuzzy_match (comportamento original).
    """

    def __init__(self):
        self.search_tool = SearchAPI()
        self.scraper_tool = Scraper()
        self._prompt_template = _PROMPT_PATH.read_text(encoding="utf-8")

    async def run(self, query: str) -> List[Product]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        print(f"[ProductDiscoveryAgent] Pesquisando ofertas para: {normalized_query}")

        # --- Busca (sempre determinística) ---
        search_results = await self.search_tool.search(normalized_query)
        scraped_results: List[Product] = []

        if len(search_results) < 3:
            print("[ProductDiscoveryAgent] Busca principal com baixa cobertura; acionando scraper live.")
            scraped_results = await self.scraper_tool.scrape(normalized_query)

        all_products = search_results + scraped_results
        normalized = NormalizationService.normalize_list(all_products)

        # --- Filtro base (determinístico) ---
        relevant = [p for p in normalized if NormalizationService.fuzzy_match(normalized_query, p.title)]
        print(f"[ProductDiscoveryAgent] {len(relevant)} ofertas relevantes após filtro base.")

        # --- Raciocínio LLM (enriquecimento, não filtragem extra) ---
        llm = get_llm()
        if llm and relevant:
            try:
                products_json = json.dumps(
                    [{"title": p.title, "price": p.price, "store": p.store} for p in relevant[:15]],
                    ensure_ascii=False,
                    indent=2,
                )
                prompt = self._prompt_template.format(
                    query=normalized_query,
                    results=products_json,
                )
                response = llm.invoke(prompt)
                reasoning = response.content if hasattr(response, "content") else str(response)
                print(f"[ProductDiscoveryAgent][LLM] Raciocínio:\n{reasoning}\n")
            except Exception as e:
                print(f"[ProductDiscoveryAgent][LLM] ERRO ao chamar Ollama: {e} — continuando sem LLM.")

        print(f"[ProductDiscoveryAgent] Retornando {len(relevant)} ofertas para o pipeline.")
        return relevant
