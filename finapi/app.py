"""Application Flask — Lab 3 : ajout des endpoints sentiment."""

from __future__ import annotations

import logging

from flask import Flask, jsonify, request
from sqlalchemy import func

from finapi.db import SessionLocal, init_db
from finapi.models import NewsItem, PriceRecord
from finapi.prices import (
    TickerNotFoundError,
    get_history,
    get_latest_price,
)
from finapi.sentiment import analyze, analyze_batch


def create_app() -> Flask:
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)
    log = app.logger

    init_db()

    # ---------- Endpoints Lab 1 ----------

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.get("/price/<ticker>")
    def price(ticker: str):
        try:
            latest = get_latest_price(ticker)
        except TickerNotFoundError as e:
            return jsonify({"error": str(e), "code": 404}), 404
        except Exception:
            log.exception("Erreur dans /price")
            return jsonify({"error": "Erreur interne", "code": 500}), 500
        return jsonify({
            "ticker": latest.ticker,
            "date": latest.date.isoformat(),
            "close": latest.close,
            "currency": latest.currency,
        })

    @app.get("/history/<ticker>")
    def history(ticker: str):
        raw_days = request.args.get("days", "30")
        try:
            days = int(raw_days)
        except ValueError:
            return jsonify({"error": "Le paramètre 'days' doit être un entier", "code": 400}), 400
        if not 1 <= days <= 365:
            return jsonify({"error": "Le paramètre 'days' doit être entre 1 et 365", "code": 400}), 400
        try:
            points = get_history(ticker, days)
        except TickerNotFoundError as e:
            return jsonify({"error": str(e), "code": 404}), 404
        except Exception:
            log.exception("Erreur dans /history")
            return jsonify({"error": "Erreur interne", "code": 500}), 500
        return jsonify({
            "ticker": ticker.upper(),
            "days_requested": days,
            "prices": [
                {"date": p.date.isoformat(), "close": p.close} for p in points
            ],
        })

    # ---------- Endpoints Lab 2 (DB) ----------

    @app.get("/db/prices/<ticker>")
    def db_prices(ticker: str):
        with SessionLocal() as session:
            rows = (
                session.query(PriceRecord)
                .filter(PriceRecord.ticker == ticker.upper())
                .order_by(PriceRecord.date.desc())
                .limit(100)
                .all()
            )
        return jsonify({
            "ticker": ticker.upper(),
            "count": len(rows),
            "prices": [
                {"date": r.date.isoformat(), "close": r.close} for r in rows
            ],
        })

    @app.get("/db/news/<ticker>")
    def db_news(ticker: str):
        with SessionLocal() as session:
            rows = (
                session.query(NewsItem)
                .filter(NewsItem.ticker == ticker.upper())
                .order_by(NewsItem.published_at.desc())
                .limit(20)
                .all()
            )
        return jsonify({
            "ticker": ticker.upper(),
            "count": len(rows),
            "news": [
                {
                    "published_at": r.published_at.isoformat(),
                    "title": r.title,
                    "publisher": r.publisher,
                    "url": r.url,
                    "summary": r.summary,
                    "sentiment_label": r.sentiment_label,
                    "sentiment_score": r.sentiment_score,
                }
                for r in rows
            ],
        })

    @app.get("/db/stats")
    def db_stats():
        with SessionLocal() as session:
            n_prices = session.query(PriceRecord).count()
            n_news = session.query(NewsItem).count()
            n_enriched = session.query(NewsItem).filter(NewsItem.sentiment_label.isnot(None)).count()
            tickers = {t for (t,) in session.query(PriceRecord.ticker).distinct()}
        return jsonify({
            "prices_count": n_prices,
            "news_count": n_news,
            "news_enriched": n_enriched,
            "tickers": sorted(tickers),
        })

    # ---------- Nouveaux endpoints Lab 3 (sentiment) ----------

    @app.post("/sentiment")
    def sentiment():
        """Analyse le sentiment d'un texte unique. Body: {"text": "..."}."""
        payload = request.get_json(silent=True) or {}
        text = payload.get("text")
        if not text:
            return jsonify({"error": "Champ 'text' manquant", "code": 400}), 400
        try:
            result = analyze(text)
        except ValueError as e:
            return jsonify({"error": str(e), "code": 400}), 400
        except Exception:
            log.exception("Erreur dans /sentiment")
            return jsonify({"error": "Erreur interne", "code": 500}), 500
        return jsonify({
            "label": result.label,
            "score": result.score,
            "text_preview": result.text_preview,
        })

    @app.post("/sentiment/batch")
    def sentiment_batch():
        """Analyse plusieurs textes. Body: {"texts": ["...", ...]}."""
        payload = request.get_json(silent=True) or {}
        texts = payload.get("texts")
        if not isinstance(texts, list) or not texts:
            return jsonify({"error": "Champ 'texts' (liste non vide) requis", "code": 400}), 400
        if len(texts) > 100:
            return jsonify({"error": "Maximum 100 textes par requête", "code": 400}), 400
        try:
            results = analyze_batch(texts)
        except Exception:
            log.exception("Erreur dans /sentiment/batch")
            return jsonify({"error": "Erreur interne", "code": 500}), 500
        return jsonify({
            "count": len(results),
            "results": [
                {"label": r.label, "score": r.score, "text_preview": r.text_preview}
                for r in results
            ],
        })

    @app.get("/db/sentiment-summary/<ticker>")
    def sentiment_summary(ticker: str):
        """Résumé des sentiments stockés pour un ticker."""
        with SessionLocal() as session:
            rows = (
                session.query(NewsItem.sentiment_label, func.count(NewsItem.id))
                .filter(NewsItem.ticker == ticker.upper())
                .filter(NewsItem.sentiment_label.isnot(None))
                .group_by(NewsItem.sentiment_label)
                .all()
            )
        return jsonify({
            "ticker": ticker.upper(),
            "distribution": {label: count for label, count in rows},
        })

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
