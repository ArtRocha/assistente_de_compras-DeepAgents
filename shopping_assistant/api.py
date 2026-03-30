import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from shopping_assistant.agents.orchestrator import OrchestratorAgent

app = FastAPI(title="Shopping Assistant API")
orchestrator = OrchestratorAgent()

class SearchRequest(BaseModel):
    query: str

@app.post("/api/search")
async def search_products(request: SearchRequest) -> List[Dict[str, Any]]:
    try:
        results = await orchestrator.process_query(request.query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("shopping_assistant.api:app", host="0.0.0.0", port=8000, reload=True)
