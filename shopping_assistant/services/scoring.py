from typing import List
from ..schemas.product import Product


class ScoringEngine:
    """Computes a confidence-aware score and sorts approved offers by price."""

    @staticmethod
    def compute_scores(products: List[Product]) -> List[Product]:
        if not products:
            return []

        min_price = min(p.price for p in products)

        for product in products:
            price_score = min_price / product.price if product.price > 0 else 0.0
            trust_score = product.trust_score if product.trust_score is not None else 0.0
            product.final_score = round((trust_score * 0.4) + (price_score * 0.6), 4)

        return products

    @staticmethod
    def rank_products(products: List[Product]) -> List[Product]:
        return sorted(
            products,
            key=lambda product: (product.price, -(product.trust_score or 0.0), product.store),
        )
