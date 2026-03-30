import asyncio
from typing import List
from ..schemas.product import Product

class SearchAPI:
    """Mock Tool for searching products across multiple stores."""
    
    async def search(self, query: str) -> List[Product]:
        # Simulate network latency
        await asyncio.sleep(0.5)
        
        # Mock data representing different stores and prices
        return [
            Product(
                title=f"{query} - 128GB",
                price=4500.0,
                store="Amazon",
                url="https://amazon.com.br/product/1"
            ),
            Product(
                title=f"{query} - Silver",
                price=4300.0,
                store="Mercado Livre",
                url="https://mercadolivre.com.br/product/2"
            ),
            Product(
                title=f"{query} Pro",
                price=5200.0,
                store="Magalu",
                url="https://magazineluiza.com.br/product/3"
            )
        ]
