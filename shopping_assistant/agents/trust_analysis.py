from typing import List
import asyncio

from ..tools.store_validator import StoreValidationEngine
from ..schemas.product import Product
from ..services.store_verification_repository import StoreVerificationRepository


class TrustAnalysisAgent:
    """Validates store integrity before an offer enters the shopping shortlist."""

    def __init__(self, max_concurrency: int = 6, validation_timeout_seconds: float = 8.0):
        self.trust_tool = StoreValidationEngine()
        self.max_concurrency = max(1, max_concurrency)
        self.validation_timeout_seconds = validation_timeout_seconds
        self.repository = StoreVerificationRepository.from_env()

    async def run(self, products: List[Product], workflow_id: int | None = None) -> List[Product]:
        print(f"[TrustAnalysisAgent] Validando integridade de {len(products)} ofertas...")
        await self._safe_log_event(
            "trust_analysis_started",
            {
                "products_total": len(products),
                "mongo_cache_enabled": self.repository.enabled,
            },
            workflow_id=workflow_id,
        )

        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def validate_product(product: Product):
            async with semaphore:
                cached = await self.repository.get_cached_validation(product.store, product.url)
                if cached is not None:
                    await self._safe_log_event(
                        "store_validation_cache_hit",
                        {
                            "store": product.store,
                            "url": product.url,
                        },
                        workflow_id=workflow_id,
                    )
                    return cached

                await self._safe_log_event(
                    "store_validation_cache_miss",
                    {
                        "store": product.store,
                        "url": product.url,
                    },
                    workflow_id=workflow_id,
                )

                trust_data = await asyncio.wait_for(
                    self.trust_tool.validate_store(product.store, product.url),
                    timeout=self.validation_timeout_seconds,
                )
                await self.repository.upsert_validation(product.store, product.url, trust_data)
                await self._safe_log_event(
                    "store_validated_and_cached",
                    {
                        "store": product.store,
                        "url": product.url,
                        "approved": bool(trust_data.get("approved", False)),
                        "score": trust_data.get("score"),
                    },
                    workflow_id=workflow_id,
                )
                return trust_data

        trust_tasks = [validate_product(product) for product in products]
        trust_results = await asyncio.gather(*trust_tasks, return_exceptions=True)

        approved_products: List[Product] = []
        failed_validations = 0

        for product, trust_data in zip(products, trust_results, strict=True):
            if isinstance(trust_data, Exception):
                print(
                    "[TrustAnalysisAgent] Falha ao validar loja "
                    f"'{product.store}' ({product.url}): {trust_data}"
                )
                failed_validations += 1
                await self._safe_log_event(
                    "store_validation_failed",
                    {
                        "store": product.store,
                        "url": product.url,
                        "error": str(trust_data),
                    },
                    workflow_id=workflow_id,
                )
                continue

            product.trust_score = trust_data.get("score", 0.0)
            product.response_rate = trust_data.get("response_rate")
            product.resolution_rate = trust_data.get("resolution_rate")
            product.review_summary = trust_data.get("comment_summary")
            product.trust_label = trust_data.get("trust_label")
            product.trust_reasons = trust_data.get("reasons")
            product.trust_metrics = {
                "reclame_aqui_rating": trust_data.get("rating"),
                "trustpilot_rating": trust_data.get("trustpilot_rating"),
                "years_online": trust_data.get("years_online"),
                "security_score": trust_data.get("security_score"),
                "reputation_score": trust_data.get("reputation_score"),
                "operational_score": trust_data.get("operational_score"),
                "domain_match_score": trust_data.get("domain_match_score"),
                "domain_reputation_score": trust_data.get("domain_reputation_score"),
                "domain": trust_data.get("domain"),
                "risk_flags": trust_data.get("risk_flags"),
            }
            product.integrity_verified = bool(trust_data.get("approved", False))

            if product.integrity_verified:
                approved_products.append(product)

        print(f"[TrustAnalysisAgent] {len(approved_products)} ofertas aprovadas apos validacao.")
        await self._safe_log_event(
            "trust_analysis_finished",
            {
                "products_total": len(products),
                "approved_total": len(approved_products),
                "failed_total": failed_validations,
            },
            workflow_id=workflow_id,
        )
        return approved_products

    async def _safe_log_event(self, event_type: str, payload: dict, workflow_id: int | None) -> None:
        try:
            await self.repository.log_process_event(event_type, payload, workflow_id=workflow_id)
        except Exception as exc:
            print(f"[TrustAnalysisAgent] Falha ao registrar evento '{event_type}': {exc}")
