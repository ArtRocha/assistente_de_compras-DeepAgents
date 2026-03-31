import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from shopping_assistant.agents.orchestrator import OrchestratorAgent

app = FastAPI(title="Shopping Assistant API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
orchestrator = OrchestratorAgent()


class SearchRequest(BaseModel):
    query: str


@app.post("/api/search")
@app.post("/search")
async def search_products(request: SearchRequest) -> List[Dict[str, Any]]:
    try:
        results = await orchestrator.process_query(request.query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "shopping_assistant.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["shopping_assistant"],
        reload_excludes=["frontend", "frontend/node_modules", "**/node_modules"],
    )
