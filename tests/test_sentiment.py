from unittest.mock import patch

import pytest

from finapi.sentiment import SentimentResult, analyze


@patch("finapi.sentiment.get_pipeline")
def test_analyze_positive(mock_pipe):
    mock_pipe.return_value = lambda text, **kwargs: [
        {"label": "positive", "score": 0.95}
    ]

    result = analyze("Apple beats expectations")

    assert isinstance(result, SentimentResult)
    assert result.label == "positive"
    assert result.score == 0.95


@patch("finapi.sentiment.get_pipeline")
def test_analyze_negative(mock_pipe):
    mock_pipe.return_value = lambda text, **kwargs: [
        {"label": "negative", "score": 0.87}
    ]

    result = analyze("Apple stock falls after bad earnings")

    assert result.label == "negative"
    assert result.score == 0.87


def test_analyze_empty_raises():
    with pytest.raises(ValueError):
        analyze("")



from unittest.mock import MagicMock

@patch("finapi.sentiment.get_pipeline")
def test_analyze_uses_token_truncation(mock_get_pipe):
    fake_pipe = MagicMock(return_value=[{"label": "neutral", "score": 0.5}])
    mock_get_pipe.return_value = fake_pipe

    long_text = "word " * 2000
    analyze(long_text)

    args, kwargs = fake_pipe.call_args
    assert args[0] == long_text              # full text sent, not cut by characters
    assert kwargs["truncation"] is True
    assert kwargs["max_length"] == 512