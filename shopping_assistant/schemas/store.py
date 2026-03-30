from pydantic import BaseModel, Field

class Store(BaseModel):
    name: str = Field(..., description="The name of the store")
    rating: float = Field(..., description="The store rating (0 to 10)")
    reclame_aqui_id: str = Field(..., description="The ID of the store in Reclame Aqui")
