from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    title: str = Field(..., description="The full title of the product")
    price: float = Field(..., description="The current price of the product")
    store: str = Field(..., description="The name of the store selling the product")
    url: str = Field(..., description="The direct URL to the product page")
    trust_score: Optional[float] = Field(None, description="The trust score of the store (0 to 1)")
    final_score: Optional[float] = Field(None, description="The computed final score for ranking")
