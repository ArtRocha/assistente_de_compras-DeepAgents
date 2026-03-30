import asyncio
from typing import List
from ..schemas.product import Product

class Scraper:
    """Mock Tool for scraping products as a fallback."""
    
    async def scrape(self, query: str) -> List[Product]:
        # Simulate network latency
        await asyncio.sleep(1.0)
        
        return [
            Product(
                title=f"{query} (Used)",
                price=3800.0,
                store="OLX",
                url="https://olx.com.br/product/4"
            )
        ]
