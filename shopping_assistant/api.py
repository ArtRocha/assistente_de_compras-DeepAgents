from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do .env antes de qualquer import que use os.getenv()
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import Query
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


@app.get("/api/orchestrator/status")
async def orchestrator_status() -> Dict[str, Any]:
    return await orchestrator.get_runtime_status()


@app.get("/api/orchestrator/events")
async def orchestrator_events(
    limit: int = Query(default=50, ge=1, le=500),
    workflow_id: int | None = Query(default=None),
) -> List[Dict[str, Any]]:
    return await orchestrator.get_recent_events(limit=limit, workflow_id=workflow_id)


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
