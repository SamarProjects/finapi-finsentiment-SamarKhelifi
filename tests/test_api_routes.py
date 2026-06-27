from unittest.mock import patch

from finapi.sentiment import SentimentResult


def test_db_stats_returns_200(client):
    response = client.get("/db/stats")
    assert response.status_code == 200


def test_db_prices_returns_200(client):
    response = client.get("/db/prices/AAPL")
    assert response.status_code == 200


def test_db_news_returns_200(client):
    response = client.get("/db/news/AAPL")
    assert response.status_code == 200


def test_sentiment_summary_returns_200(client):
    response = client.get("/db/sentiment-summary/AAPL")
    assert response.status_code == 200


@patch("finapi.app.analyze")
def test_sentiment_endpoint_returns_result(mock_analyze, client):
    mock_analyze.return_value = SentimentResult(
        label="positive",
        score=0.95,
        text_preview="Apple beats expectations",
    )

    response = client.post("/sentiment", json={"text": "Apple beats expectations"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["label"] == "positive"
    assert data["score"] == 0.95


def test_sentiment_endpoint_missing_text_returns_400(client):
    response = client.post("/sentiment", json={})
    assert response.status_code == 400


@patch("finapi.app.analyze")
def test_sentiment_batch_endpoint_returns_results(mock_analyze, client):
    mock_analyze.side_effect = [
        SentimentResult(
            label="positive",
            score=0.95,
            text_preview="Apple beats expectations",
        ),
        SentimentResult(
            label="negative",
            score=0.80,
            text_preview="Stock falls after bad news",
        ),
    ]

    response = client.post(
        "/sentiment/batch",
        json={"texts": ["Apple beats expectations", "Stock falls after bad news"]},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["results"]) == 2


def test_sentiment_batch_missing_texts_returns_400(client):
    response = client.post("/sentiment/batch", json={})
    assert response.status_code == 400
    