import httpx

BASE_URL = "https://api.artic.edu/api/v1/artworks"


def get_artwork(external_id: int) -> dict | None:
    try:
        resp = httpx.get(f"{BASE_URL}/{external_id}", timeout=5.0)
    except httpx.RequestError:
        return None

    if resp.status_code != 200:
        return None

    payload = resp.json()
    data = payload.get("data")
    if not data:
        return None

    return data
