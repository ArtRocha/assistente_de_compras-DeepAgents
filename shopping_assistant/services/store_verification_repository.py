from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:  # pragma: no cover - handled at runtime when dependency is absent
    AsyncIOMotorClient = None  # type: ignore[assignment]


class StoreVerificationRepository:
    """Persists trust validation cache and process events in MongoDB."""

    def __init__(
        self,
        mongo_uri: str,
        database_name: str = "shopping_assistant",
        cache_collection_name: str = "store_validation_cache",
        events_collection_name: str = "orchestration_events",
        cache_ttl_hours: int = 72,
    ):
        self._mongo_uri = mongo_uri.strip()
        self._database_name = database_name
        self._cache_collection_name = cache_collection_name
        self._events_collection_name = events_collection_name
        self._cache_ttl_hours = max(1, cache_ttl_hours)

        self._client = None
        self._cache_collection = None
        self._events_collection = None
        self._init_lock = asyncio.Lock()
        self._disabled = not bool(self._mongo_uri) or AsyncIOMotorClient is None

    @classmethod
    def from_env(cls) -> "StoreVerificationRepository":
        return cls(
            mongo_uri=os.getenv("MONGODB_URI", ""),
            database_name=os.getenv("MONGODB_DATABASE", "shopping_assistant"),
            cache_collection_name=os.getenv("MONGODB_CACHE_COLLECTION", "store_validation_cache"),
            events_collection_name=os.getenv("MONGODB_EVENTS_COLLECTION", "orchestration_events"),
            cache_ttl_hours=_read_int_env("MONGODB_CACHE_TTL_HOURS", 72),
        )

    @property
    def enabled(self) -> bool:
        return not self._disabled

    async def get_cached_validation(self, store_name: str, product_url: str) -> Optional[Dict[str, Any]]:
        if not await self._ensure_initialized():
            return None

        cache_key = self._build_cache_key(store_name, product_url)
        now = _utcnow()
        document = await self._cache_collection.find_one(
            {
                "cache_key": cache_key,
                "expires_at": {"$gt": now},
            }
        )
        if not document:
            return None
        return document.get("trust_data")

    async def upsert_validation(self, store_name: str, product_url: str, trust_data: Dict[str, Any]) -> None:
        if not await self._ensure_initialized():
            return

        now = _utcnow()
        expires_at = now + timedelta(hours=self._cache_ttl_hours)
        store_normalized = self._normalize_store_name(store_name)
        domain = self._extract_domain(product_url)
        cache_key = self._build_cache_key(store_name, product_url)

        await self._cache_collection.update_one(
            {"cache_key": cache_key},
            {
                "$set": {
                    "store_name": store_name,
                    "store_name_normalized": store_normalized,
                    "domain": domain,
                    "cache_key": cache_key,
                    "trust_data": trust_data,
                    "updated_at": now,
                    "expires_at": expires_at,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )

    async def log_process_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        workflow_id: Optional[int] = None,
    ) -> None:
        if not await self._ensure_initialized():
            return

        event_document = {
            "event_type": event_type,
            "workflow_id": workflow_id,
            "payload": payload,
            "created_at": _utcnow(),
        }
        await self._events_collection.insert_one(event_document)

    async def list_recent_events(
        self,
        limit: int = 50,
        workflow_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        if not await self._ensure_initialized():
            return []

        normalized_limit = max(1, min(500, limit))
        query: Dict[str, Any] = {}
        if workflow_id is not None:
            query["workflow_id"] = workflow_id

        cursor = self._events_collection.find(query).sort("created_at", -1).limit(normalized_limit)
        documents = await cursor.to_list(length=normalized_limit)

        for document in documents:
            document["_id"] = str(document.get("_id"))

        return documents

    async def _ensure_initialized(self) -> bool:
        if self._disabled:
            return False
        if self._client is not None:
            return True

        async with self._init_lock:
            if self._client is not None:
                return True
            try:
                self._client = AsyncIOMotorClient(self._mongo_uri, serverSelectionTimeoutMS=3000)
                db = self._client[self._database_name]
                self._cache_collection = db[self._cache_collection_name]
                self._events_collection = db[self._events_collection_name]
                await self._cache_collection.create_index("cache_key", unique=True)
                await self._cache_collection.create_index("expires_at", expireAfterSeconds=0)
                await self._events_collection.create_index("created_at")
            except Exception as exc:
                self._disabled = True
                print(f"[MongoRepository] Disabled due to initialization failure: {exc}")
                return False

        return True

    def _build_cache_key(self, store_name: str, product_url: str) -> str:
        return f"{self._normalize_store_name(store_name)}::{self._extract_domain(product_url)}"

    def _normalize_store_name(self, store_name: str) -> str:
        return "".join(ch for ch in store_name.lower().strip() if ch.isalnum())

    def _extract_domain(self, url: str) -> str:
        if not url:
            return ""
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if host.startswith("www."):
            return host[4:]
        return host


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _read_int_env(env_var: str, default: int) -> int:
    raw = os.getenv(env_var, "")
    if not raw:
        return default
    try:
        parsed = int(raw)
        return parsed if parsed > 0 else default
    except ValueError:
        return default
