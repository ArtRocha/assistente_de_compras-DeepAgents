from typing import List
from ..schemas.product import Product

class NormalizationService:
    """Service to normalize product data and remove duplicates."""
    
    @staticmethod
    def normalize_list(products: List[Product]) -> List[Product]:
        seen_urls = set()
        normalized = []
        
        for p in products:
            # Simple deduplication by URL
            if p.url not in seen_urls:
                seen_urls.add(p.url)
                
                # Normalize store names (e.g., lower case, trim)
                p.store = p.store.strip().title()
                
                # Normalize title (simple version)
                p.title = p.title.strip()
                
                normalized.append(p)
                
        return normalized

    @staticmethod
    def fuzzy_match(query: str, target: str) -> bool:
        """Basic fuzzy match check."""
        query_words = set(query.lower().split())
        target_words = set(target.lower().split())
        # If at least one keyword matches, we consider it a hit for this mock
        return len(query_words.intersection(target_words)) > 0
