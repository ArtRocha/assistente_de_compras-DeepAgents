import asyncio
from typing import List
from ..schemas.product import Product


class SearchAPI:
    """Simulates a Google Shopping search result set for the requested product."""

    async def search(self, query: str) -> List[Product]:
        await asyncio.sleep(0.4)

        normalized_query = query.strip()
        lower_query = normalized_query.lower()

        if "iphone" in lower_query:
            return [
                Product(
                    title=f"{normalized_query} Apple 128GB",
                    price=4299.90,
                    store="Mercado Livre",
                    url="https://www.mercadolivre.com.br/iphone-128gb",
                    source="google_shopping",
                ),
                Product(
                    title=f"{normalized_query} Apple 128GB",
                    price=4399.00,
                    store="Amazon",
                    url="https://www.amazon.com.br/iphone-128gb",
                    source="google_shopping",
                ),
                Product(
                    title=f"{normalized_query} Apple 128GB",
                    price=4499.90,
                    store="Magalu",
                    url="https://www.magazineluiza.com.br/iphone-128gb",
                    source="google_shopping",
                ),
                Product(
                    title=f"{normalized_query} Apple 128GB",
                    price=4599.00,
                    store="Fast Shop",
                    url="https://www.fastshop.com.br/iphone-128gb",
                    source="google_shopping",
                ),
            ]

        if "ps5" in lower_query or "playstation 5" in lower_query:
            return [
                Product(
                    title=f"{normalized_query} Console Sony",
                    price=3499.90,
                    store="Amazon",
                    url="https://www.amazon.com.br/ps5-console-sony",
                    source="google_shopping",
                ),
                Product(
                    title=f"{normalized_query} Console Sony",
                    price=3449.90,
                    store="Magalu",
                    url="https://www.magazineluiza.com.br/ps5-console-sony",
                    source="google_shopping",
                ),
                Product(
                    title=f"{normalized_query} Console Sony",
                    price=3399.90,
                    store="Kabum",
                    url="https://www.kabum.com.br/ps5-console-sony",
                    source="google_shopping",
                ),
            ]

        return [
            Product(
                title=f"{normalized_query} - oferta principal",
                price=1999.90,
                store="Amazon",
                url="https://www.amazon.com.br/produto-principal",
                source="google_shopping",
            ),
            Product(
                title=f"{normalized_query} - oferta comparada",
                price=1949.90,
                store="Magalu",
                url="https://www.magazineluiza.com.br/produto-comparado",
                source="google_shopping",
            ),
            Product(
                title=f"{normalized_query} - oferta marketplace",
                price=1899.90,
                store="Mercado Livre",
                url="https://www.mercadolivre.com.br/produto-marketplace",
                source="google_shopping",
            ),
        ]
