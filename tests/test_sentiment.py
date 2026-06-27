from unittest.mock import patch

import pytest

from finapi.sentiment import SentimentResult, analyze


@patch("finapi.sentiment.get_pipeline")
def test_analyze_positive(mock_pipe):
    mock_pipe.return_value = lambda text: [
        {"label": "positive", "score": 0.95}
    ]

    result = analyze("Apple beats expectations")

    assert isinstance(result, SentimentResult)
    assert result.label == "positive"
    assert result.score == 0.95


@patch("finapi.sentiment.get_pipeline")
def test_analyze_negative(mock_pipe):
    mock_pipe.return_value = lambda text: [
        {"label": "negative", "score": 0.87}
    ]

    result = analyze("Apple stock falls after bad earnings")

    assert result.label == "negative"
    assert result.score == 0.87


def test_analyze_empty_raises():
    with pytest.raises(ValueError):
        analyze("")
        