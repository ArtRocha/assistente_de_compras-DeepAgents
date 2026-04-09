from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class Product(BaseModel):
    title: str = Field(..., description="The full title of the product")
    price: float = Field(..., description="The current price of the product")
    store: str = Field(..., description="The name of the store selling the product")
    url: str = Field(..., description="The direct URL to the product page")
    trust_score: Optional[float] = Field(None, description="Normalized store trust score from 0 to 1")
    final_score: Optional[float] = Field(None, description="Final ordering score used by the ranking agent")
    source: Optional[str] = Field(None, description="Source where the offer was found")
    integrity_verified: bool = Field(False, description="Whether the store passed the integrity validation")
    response_rate: Optional[float] = Field(None, description="Store complaint response rate from 0 to 1")
    resolution_rate: Optional[float] = Field(None, description="Store complaint resolution rate from 0 to 1")
    review_summary: Optional[str] = Field(None, description="Short explanation of the trust analysis")
    trust_label: Optional[str] = Field(None, description="Trust classification label such as alta, moderada or baixa")
    trust_reasons: Optional[List[str]] = Field(
        default=None,
        description="Objective reasons used to justify why the store was approved or rejected",
    )
    trust_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw trust metrics used by the validation engine",
    )
