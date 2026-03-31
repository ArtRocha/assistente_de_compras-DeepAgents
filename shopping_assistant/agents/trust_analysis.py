import asyncio
from typing import List
from ..tools.reclame_aqui import ReclameAquiTool
from ..schemas.product import Product


class TrustAnalysisAgent:
    """Validates store integrity before an offer enters the shopping shortlist."""

    def __init__(self):
        self.trust_tool = ReclameAquiTool()

    async def run(self, products: List[Product]) -> List[Product]:
        print(f"[TrustAnalysisAgent] Validando integridade de {len(products)} ofertas...")

        stores = list({p.store for p in products})
        trust_tasks = [self.trust_tool.get_store_trust(store) for store in stores]
        trust_results = await asyncio.gather(*trust_tasks)
        store_trust_map = dict(zip(stores, trust_results))

        approved_products: List[Product] = []

        for product in products:
            trust_data = store_trust_map.get(product.store, {})
            product.trust_score = trust_data.get("score", 0.0)
            product.response_rate = trust_data.get("response_rate")
            product.resolution_rate = trust_data.get("resolution_rate")
            product.review_summary = trust_data.get("comment_summary")
            product.integrity_verified = bool(trust_data.get("approved", False))

            if product.integrity_verified:
                approved_products.append(product)

        print(f"[TrustAnalysisAgent] {len(approved_products)} ofertas aprovadas após validação.")
        return approved_products
