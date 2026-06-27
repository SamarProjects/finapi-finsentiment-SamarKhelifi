# finapi — Lab 4 : Dashboard Streamlit

Application complète : API Flask + base SQLite + FinBERT + **dashboard Streamlit interactif**.

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Démarrer le système complet (3 étapes)

```bash
# 1. Ingérer les données
python scripts/run_etl.py AAPL MSFT GOOGL TSLA

# 2. Calculer le sentiment des news
python scripts/enrich_sentiment.py

# 3a. Lancer l'API (terminal 1)
python -m finapi.app

# 3b. Lancer le dashboard (terminal 2)
streamlit run dashboard/app.py
```

Ouvrez ensuite http://localhost:8501

## Architecture

```
finapi/                   # Backend
├── finapi/
│   ├── app.py            # API Flask
│   ├── db.py, models.py  # SQLAlchemy
│   ├── prices.py         # yfinance
│   ├── sentiment.py      # FinBERT
│   └── etl/
├── dashboard/            # Frontend Streamlit
│   ├── app.py            # Page principale
│   ├── api_client.py     # Wrapper requests
│   └── charts.py         # Plotly
├── scripts/              # ETL & enrichissement
└── data/                 # SQLite
```

## Captures d'écran

Voir `docs/screenshots/`.
