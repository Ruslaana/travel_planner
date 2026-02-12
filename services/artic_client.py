from __future__ import annotations

import asyncio
import time
from typing import Optional

import httpx

BASE_URL = "https://api.artic.edu/api/v1/artworks"

TTL_SECONDS = 300  # 5 min

_CACHE: dict[int, tuple[float, Optional[dict]]] = {}
_CACHE_LOCK = asyncio.Lock()


def _is_expired(expires_at: float) -> bool:
    return time.time() > expires_at


async def _cache_get(external_id: int) -> Optional[dict] | None:
    async with _CACHE_LOCK:
        item = _CACHE.get(external_id)
        if not item:
            return None
        expires_at, value = item
        if _is_expired(expires_at):
            _CACHE.pop(external_id, None)
            return None
        return value


async def _cache_set(external_id: int, value: Optional[dict]) -> None:
    async with _CACHE_LOCK:
        _CACHE[external_id] = (time.time() + TTL_SECONDS, value)


async def get_artwork_async(external_id: int, client: httpx.AsyncClient) -> dict | None:
    try:
        resp = await client.get(f"{BASE_URL}/{external_id}", timeout=5.0)
    except httpx.RequestError:
        return None

    if resp.status_code != 200:
        return None

    payload = resp.json()
    return payload.get("data") or None


async def get_artwork_cached_async(external_id: int, client: httpx.AsyncClient) -> dict | None:
    cached = await _cache_get(external_id)
    if cached is not None:
        return cached

    data = await get_artwork_async(external_id, client)
    await _cache_set(external_id, data)
    return data


async def validate_artworks_exist_async(external_ids: list[int]) -> list[int]:
    """Return list of missing IDs. Validates concurrently + uses TTL cache."""
    async with httpx.AsyncClient() as client:
        tasks = [get_artwork_cached_async(eid, client) for eid in external_ids]
        results = await asyncio.gather(*tasks)

    missing = [eid for eid, data in zip(external_ids, results) if not data]
    return missing
