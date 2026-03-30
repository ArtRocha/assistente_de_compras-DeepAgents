from typing import List
from ..schemas.product import Product

class ScoringEngine:
    """Service to compute final scores for products."""
    
    @staticmethod
    def compute_scores(products: List[Product]) -> List[Product]:
        if not products:
            return []
            
        # Find min price for normalization
        min_price = min(p.price for p in products)
        
        for p in products:
            # price_score = min_price / product_price
            price_score = min_price / p.price if p.price > 0 else 0
            
            # trust_score defaults to 0.5 if not provided
            trust_score = p.trust_score if p.trust_score is not None else 0.5
            
            # final_score = (0.7 * trust_score) + (0.3 * price_score)
            p.final_score = (0.7 * trust_score) + (0.3 * price_score)
            
        return products

    @staticmethod
    def rank_products(products: List[Product]) -> List[Product]:
        # Sort by final_score DESC, then price ASC
        return sorted(products, key=lambda x: (-(x.final_score or 0), x.price))
