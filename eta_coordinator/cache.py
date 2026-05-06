"""Inquiry deduplication cache.

Spec: same customer + consignment asked <1h ago → reply from cache (Section 2.1).

In-memory implementation for development/testing. Replace with Redis (or equivalent)
before deploying to production — in-memory state is lost on restart and is not shared
across multiple agent instances.

Production replacement:
    redis_client.setex(
        key=_cache_key(customer_id, consignment_id),
        time=CACHE_TTL_SECONDS,
        value=json.dumps({"message": ..., "resolution_type": ...}),
    )
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from config import CACHE_TTL_SECONDS
from models import CacheEntry, ResolutionType

logger = logging.getLogger(__name__)


def _cache_key(customer_id: str, consignment_id: str) -> str:
    return f"{customer_id}:{consignment_id}"


class InquiryCache:

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}

    def get(
        self, customer_id: str, consignment_id: str, now: Optional[datetime] = None
    ) -> Optional[CacheEntry]:
        """Return a cached entry if it exists and is within CACHE_TTL_SECONDS.

        Returns None if no entry exists or if the entry has expired.
        Expired entries are evicted lazily on get().
        """
        now = now or datetime.now(timezone.utc)
        key = _cache_key(customer_id, consignment_id)
        entry = self._store.get(key)
        if entry is None:
            return None
        age = (now - entry.cached_at).total_seconds()
        if age > CACHE_TTL_SECONDS:
            del self._store[key]
            logger.debug("Cache expired for key=%s (age=%.0fs)", key, age)
            return None
        logger.debug("Cache hit for key=%s (age=%.0fs)", key, age)
        return entry

    def set(
        self,
        customer_id: str,
        consignment_id: str,
        reply_message: str,
        resolution_type: ResolutionType,
        now: Optional[datetime] = None,
    ) -> None:
        """Store a reply in the cache, overwriting any existing entry."""
        now = now or datetime.now(timezone.utc)
        key = _cache_key(customer_id, consignment_id)
        self._store[key] = CacheEntry(
            customer_id=customer_id,
            consignment_id=consignment_id,
            reply_message=reply_message,
            resolution_type=resolution_type,
            cached_at=now,
        )
        logger.debug("Cache set for key=%s", key)

    def evict(self, customer_id: str, consignment_id: str) -> None:
        """Explicitly remove a cache entry (e.g. after a status change)."""
        key = _cache_key(customer_id, consignment_id)
        self._store.pop(key, None)

    def size(self) -> int:
        return len(self._store)
