import asyncio
import os
from .product_discovery import ProductDiscoveryAgent
from .trust_analysis import TrustAnalysisAgent
from .ranking import RankingAgent
from ..schemas.product import Product
from ..services.store_verification_repository import StoreVerificationRepository
from typing import List, Dict, Any


class OrchestratorAgent:
    """Main orchestrator for the multi-agent shopping assistant.

    Controls workflow lifecycle and limits concurrent requests to avoid overload.
    """

    def __init__(self):
        self.discovery_agent = ProductDiscoveryAgent()
        self.trust_agent = TrustAnalysisAgent(max_concurrency=self._read_int_env("TRUST_MAX_CONCURRENCY", 6))
        self.ranking_agent = RankingAgent()
        self.max_concurrent_workflows = self._read_int_env("ORCHESTRATOR_MAX_CONCURRENT_WORKFLOWS", 2)
        self.max_products_for_validation = self._read_int_env("ORCHESTRATOR_MAX_PRODUCTS_FOR_VALIDATION", 30)

        self._workflow_semaphore = asyncio.Semaphore(self.max_concurrent_workflows)
        self._state_lock = asyncio.Lock()
        self._active_workflows: set[int] = set()
        self._workflow_counter = 0
        self._repository = StoreVerificationRepository.from_env()

    async def process_query(self, query: str) -> List[Dict[str, Any]]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        print(f"[Orchestrator] Request queued for: '{normalized_query}'")
        await self._safe_log_event(
            "orchestrator_request_queued",
            {"query": normalized_query},
            workflow_id=None,
        )

        async with self._workflow_semaphore:
            workflow_id = await self._start_workflow(normalized_query)
            try:
                await self._safe_log_event(
                    "orchestrator_workflow_started",
                    {"query": normalized_query},
                    workflow_id=workflow_id,
                )
                products = await self.discovery_agent.run(normalized_query)
                if not products:
                    print(f"[Orchestrator:{workflow_id}] No products found.")
                    await self._safe_log_event(
                        "orchestrator_workflow_finished",
                        {"query": normalized_query, "products_found": 0, "products_approved": 0},
                        workflow_id=workflow_id,
                    )
                    return []

                selected_products = self._select_products_for_validation(products)
                products_with_trust = await self.trust_agent.run(selected_products, workflow_id=workflow_id)
                if not products_with_trust:
                    print(f"[Orchestrator:{workflow_id}] No approved products after trust analysis.")
                    await self._safe_log_event(
                        "orchestrator_workflow_finished",
                        {
                            "query": normalized_query,
                            "products_found": len(products),
                            "products_selected_for_validation": len(selected_products),
                            "products_approved": 0,
                        },
                        workflow_id=workflow_id,
                    )
                    return []

                ranked_results = await self.ranking_agent.run(products_with_trust, query=normalized_query)
                print(f"[Orchestrator:{workflow_id}] Finished processing.")
                await self._safe_log_event(
                    "orchestrator_workflow_finished",
                    {
                        "query": normalized_query,
                        "products_found": len(products),
                        "products_selected_for_validation": len(selected_products),
                        "products_approved": len(products_with_trust),
                        "products_ranked": len(ranked_results),
                    },
                    workflow_id=workflow_id,
                )
                return [p.model_dump() for p in ranked_results]
            finally:
                await self._finish_workflow(workflow_id)

    async def _start_workflow(self, query: str) -> int:
        async with self._state_lock:
            self._workflow_counter += 1
            workflow_id = self._workflow_counter
            self._active_workflows.add(workflow_id)
            active_count = len(self._active_workflows)

        print(
            f"[Orchestrator:{workflow_id}] Started for '{query}' "
            f"(active={active_count}/{self.max_concurrent_workflows})."
        )
        return workflow_id

    async def _finish_workflow(self, workflow_id: int) -> None:
        async with self._state_lock:
            self._active_workflows.discard(workflow_id)
            active_count = len(self._active_workflows)

        print(f"[Orchestrator:{workflow_id}] Finalized (active={active_count}/{self.max_concurrent_workflows}).")

    async def get_runtime_status(self) -> Dict[str, Any]:
        async with self._state_lock:
            active_workflows = sorted(self._active_workflows)

        return {
            "agent": "agent_orchestrador",
            "active_workflows": active_workflows,
            "active_workflows_count": len(active_workflows),
            "max_concurrent_workflows": self.max_concurrent_workflows,
            "max_products_for_validation": self.max_products_for_validation,
            "trust_max_concurrency": self.trust_agent.max_concurrency,
            "trust_validation_timeout_seconds": self.trust_agent.validation_timeout_seconds,
            "mongo_cache_enabled": self.trust_agent.repository.enabled,
        }

    async def get_recent_events(self, limit: int = 50, workflow_id: int | None = None) -> List[Dict[str, Any]]:
        return await self._repository.list_recent_events(limit=limit, workflow_id=workflow_id)

    def _select_products_for_validation(self, products: List[Product]) -> List[Product]:
        if len(products) <= self.max_products_for_validation:
            return products

        sorted_by_price = sorted(products, key=lambda product: product.price)
        selected = sorted_by_price[: self.max_products_for_validation]
        print(
            "[Orchestrator] Limiting trust analysis to "
            f"{len(selected)} offers out of {len(products)} to protect system load."
        )
        return selected

    @staticmethod
    def _read_int_env(env_var: str, default: int) -> int:
        value = os.getenv(env_var, "")
        if not value:
            return default
        try:
            parsed = int(value)
            return parsed if parsed > 0 else default
        except ValueError:
            return default

    async def _safe_log_event(self, event_type: str, payload: Dict[str, Any], workflow_id: int | None) -> None:
        try:
            await self._repository.log_process_event(event_type, payload, workflow_id=workflow_id)
        except Exception as exc:
            print(f"[Orchestrator] Failed to log event '{event_type}': {exc}")
