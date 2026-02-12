import time
import httpx
from typing import Optional

BASE_URL = "https://api.artic.edu/api/v1/artworks"

_CACHE: dict[int, tuple[float, Optional[dict]]] = {}
TTL_SECONDS = 300  


def _cache_get(external_id: int) -> Optional[dict]:
    item = _CACHE.get(external_id)
    if not item:
        return None
    expires_at, value = item
    if time.time() > expires_at:
        _CACHE.pop(external_id, None)
        return None
    return value


def _cache_set(external_id: int, value: Optional[dict]) -> None:
    _CACHE[external_id] = (time.time() + TTL_SECONDS, value)


def get_artwork(external_id: int) -> dict | None:
    try:
        resp = httpx.get(f"{BASE_URL}/{external_id}", timeout=5.0)
    except httpx.RequestError:
        return None

    if resp.status_code != 200:
        return None

    payload = resp.json()
    data = payload.get("data")
    return data or None


def get_artwork_cached(external_id: int) -> dict | None:
    cached = _cache_get(external_id)
    if cached is not None:
        return cached

    data = get_artwork(external_id)
    _cache_set(external_id, data)
    return data


def validate_artworks_exist(external_ids: list[int]) -> list[int]:
    missing: list[int] = []
    for eid in external_ids:
        if not get_artwork_cached(eid):
            missing.append(eid)
    return missing
