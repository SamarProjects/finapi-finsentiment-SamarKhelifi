"""Accès aux données de marché via yfinance.

On isole ici toute la logique de récupération des prix afin que
``app.py`` reste centré sur les responsabilités HTTP.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import yfinance as yf


class TickerNotFoundError(Exception):
    """Levée lorsqu'aucune donnée n'est trouvée pour un ticker."""


@dataclass
class PricePoint:
    """Un point de prix simple (date + clôture)."""

    date: date
    close: float


@dataclass
class LatestPrice:
    """Dernier prix connu avec sa devise."""

    ticker: str
    date: date
    close: float
    currency: str


def get_latest_price(ticker: str) -> LatestPrice:
    """Renvoie le dernier prix de clôture pour ``ticker``.

    Lève :
        TickerNotFoundError: si aucune donnée n'est disponible.
    """
    yf_ticker = yf.Ticker(ticker)
    history = yf_ticker.history(period="5d", auto_adjust=False)

    if history.empty:
        raise TickerNotFoundError(f"Ticker '{ticker}' introuvable")

    last_row = history.iloc[-1]
    last_date = history.index[-1].date()

    # info peut échouer ou ne pas contenir 'currency' selon yfinance
    try:
        currency = yf_ticker.info.get("currency", "USD") or "USD"
    except Exception:  # pragma: no cover - dépend du réseau
        currency = "USD"

    return LatestPrice(
        ticker=ticker.upper(),
        date=last_date,
        close=round(float(last_row["Close"]), 2),
        currency=currency.upper(),
    )


def get_history(ticker: str, days: int) -> list[PricePoint]:
    """Renvoie l'historique des cours de clôture sur les ``days`` derniers
    jours civils (le nombre de jours de Bourse renvoyés est inférieur).

    Lève :
        TickerNotFoundError: si aucune donnée n'est disponible.
    """
    period = f"{max(days, 1)}d"
    history = yf.Ticker(ticker).history(period=period, auto_adjust=False)

    if history.empty:
        raise TickerNotFoundError(f"Ticker '{ticker}' introuvable")

    return [
        PricePoint(date=ts.date(), close=round(float(close), 2))
        for ts, close in history["Close"].items()
    ]
