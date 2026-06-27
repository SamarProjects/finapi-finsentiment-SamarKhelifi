"""Modèles SQLAlchemy : prix et news (avec sentiment depuis Lab 3)."""

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
)

from finapi.db import Base


class PriceRecord(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(16), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    close = Column(Float, nullable=False)
    currency = Column(String(8), default="USD")

    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_ticker_date"),
    )

    def __repr__(self) -> str:
        return f"<Price {self.ticker} {self.date} {self.close}>"


class NewsItem(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(16), nullable=False, index=True)
    published_at = Column(DateTime, nullable=False, index=True)
    title = Column(String(512), nullable=False)
    publisher = Column(String(128))
    url = Column(String(1024), unique=True)
    summary = Column(String(2048))

    # === Lab 3 : enrichissement sentiment ===
    sentiment_label = Column(String(16), nullable=True, index=True)
    sentiment_score = Column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<News {self.ticker} {self.published_at} {self.sentiment_label}>"
