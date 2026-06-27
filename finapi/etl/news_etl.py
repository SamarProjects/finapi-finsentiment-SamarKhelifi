"""ETL des news : récupération via yfinance, dédoublonnage par URL."""

import logging
from datetime import datetime

import yfinance as yf
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from finapi.db import SessionLocal
from finapi.models import NewsItem

log = logging.getLogger(__name__)


def _parse_date(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def ingest_news(ticker: str) -> int:
    """Récupère les news récentes pour un ticker et les stocke."""
    log.info("ETL news: fetching %s", ticker)
    news_list = yf.Ticker(ticker).news or []

    rows = []
    for item in news_list:
        # yfinance >= 0.2.40 imbrique la donnée dans 'content'
        content = item.get("content", item)

        published_at = _parse_date(
            content.get("pubDate") or content.get("displayTime")
        )
        if not published_at:
            continue

        url = (content.get("clickThroughUrl") or {}).get("url")
        if not url:
            continue  # pas dédoublonnable

        rows.append({
            "ticker": ticker.upper(),
            "published_at": published_at,
            "title": content.get("title", "")[:500],
            "publisher": (content.get("provider") or {}).get("displayName", ""),
            "url": url,
            "summary": (content.get("summary") or "")[:2000],
        })

    if not rows:
        log.warning("ETL news: aucun article exploitable pour %s", ticker)
        return 0

    with SessionLocal() as session:
        stmt = sqlite_insert(NewsItem).values(rows)
        stmt = stmt.on_conflict_do_nothing(index_elements=["url"])
        result = session.execute(stmt)
        session.commit()
        inserted = result.rowcount or 0

    log.info("ETL news: %d articles insérés pour %s", inserted, ticker)
    return inserted
