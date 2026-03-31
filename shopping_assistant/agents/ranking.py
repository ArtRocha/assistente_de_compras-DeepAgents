from typing import List
from ..schemas.product import Product
from ..services.scoring import ScoringEngine


class RankingAgent:
    """Orders approved products from lowest price to highest price."""

    async def run(self, products: List[Product]) -> List[Product]:
        print(f"[RankingAgent] Ordenando {len(products)} ofertas aprovadas por preço...")

        scored_products = ScoringEngine.compute_scores(products)
        ranked_products = ScoringEngine.rank_products(scored_products)

        print("[RankingAgent] Ordenação concluída.")
        return ranked_products
