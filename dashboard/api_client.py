"""Client HTTP pour l'API Flask finapi."""

from __future__ import annotations

from typing import Any

import requests

API_BASE = "http://localhost:5000"


class APIError(Exception):
    """Levée quand l'API renvoie une erreur ou est injoignable."""


def _get(path: str, **params) -> dict[str, Any]:
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=10)
    except requests.RequestException as e:
        raise APIError(f"API injoignable: {e}") from e
    if r.status_code != 200:
        raise APIError(f"{r.status_code}: {r.text[:200]}")
    return r.json()


def get_health() -> bool:
    try:
        return _get("/health").get("status") == "ok"
    except APIError:
        return False


def get_db_prices(ticker: str) -> list[dict]:
    return _get(f"/db/prices/{ticker}").get("prices", [])


def get_db_news(ticker: str) -> list[dict]:
    return _get(f"/db/news/{ticker}").get("news", [])


def get_sentiment_summary(ticker: str) -> dict[str, int]:
    return _get(f"/db/sentiment-summary/{ticker}").get("distribution", {})


def get_db_stats() -> dict:
    return _get("/db/stats")
