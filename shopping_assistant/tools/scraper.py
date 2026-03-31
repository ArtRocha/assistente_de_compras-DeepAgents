import asyncio
from typing import List
from ..schemas.product import Product


class Scraper:
    """Secondary simulated scraper that complements shopping search coverage."""

    async def scrape(self, query: str) -> List[Product]:
        await asyncio.sleep(0.6)

        normalized_query = query.strip()
        lower_query = normalized_query.lower()

        if "iphone" in lower_query:
            return [
                Product(
                    title=f"{normalized_query} Apple 128GB",
                    price=4379.90,
                    store="Casas Bahia",
                    url="https://www.casasbahia.com.br/iphone-128gb",
                    source="shopping_scraper",
                ),
                Product(
                    title=f"{normalized_query} Apple 128GB",
                    price=4550.00,
                    store="Ponto",
                    url="https://www.ponto.com.br/iphone-128gb",
                    source="shopping_scraper",
                ),
            ]

        if "ps5" in lower_query or "playstation 5" in lower_query:
            return [
                Product(
                    title=f"{normalized_query} Console Sony",
                    price=3429.90,
                    store="Casas Bahia",
                    url="https://www.casasbahia.com.br/ps5-console-sony",
                    source="shopping_scraper",
                )
            ]

        return [
            Product(
                title=f"{normalized_query} - oferta adicional",
                price=1929.90,
                store="Fast Shop",
                url="https://www.fastshop.com.br/oferta-adicional",
                source="shopping_scraper",
            )
        ]
