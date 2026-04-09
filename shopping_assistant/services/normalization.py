import re
from typing import List
from ..schemas.product import Product


class NormalizationService:
    """Service to normalize product data and remove duplicates."""

    # Separa tokens alfanuméricos: "iphone13" → ["iphone", "13"]
    _TOKEN_PATTERN = re.compile(r"[a-záàâãéèêíïóôõöúüçñ]+|\d+", re.IGNORECASE)

    @staticmethod
    def normalize_list(products: List[Product]) -> List[Product]:
        seen_urls = set()
        normalized = []

        for p in products:
            if p.url not in seen_urls:
                seen_urls.add(p.url)
                p.store = p.store.strip().title()
                p.title = p.title.strip()
                normalized.append(p)

        return normalized

    @staticmethod
    def _tokenize(text: str) -> set:
        """Tokeniza texto separando letras de números e tratando espaços.

        Exemplos:
          'iphone13'     → {'iphone', '13'}
          'iphone 13'    → {'iphone', '13'}
          'PlayStation 5'→ {'playstation', '5'}
          'air fryer'    → {'air', 'fryer'}
        """
        return set(NormalizationService._TOKEN_PATTERN.findall(text.lower()))

    @staticmethod
    def fuzzy_match(query: str, target: str) -> bool:
        """Verifica se a query tem correspondência suficiente com o título do produto.

        Estratégias em cascata:
        1. Todos os tokens da query estão no título   → match forte (passa)
        2. Pelo menos 1 token da query está no título → match fraco (passes se query curta)
        3. A query (sem espaços) é substring do título sem espaços → match por compactação
        """
        query_tokens = NormalizationService._tokenize(query)
        target_tokens = NormalizationService._tokenize(target)

        if not query_tokens:
            return True  # query vazia não filtra nada

        intersection = query_tokens & target_tokens

        # Match forte: todos os tokens da query presentes no título
        if intersection == query_tokens:
            return True

        # Match fraco: pelo menos 1 token comum
        if intersection:
            return True

        # Match por compactação: "iphone13" ⊆ "iphone13128gb" (sem espaços)
        query_compact = re.sub(r"\s+", "", query.lower())
        target_compact = re.sub(r"\s+", "", target.lower())
        if query_compact and query_compact in target_compact:
            return True

        return False
