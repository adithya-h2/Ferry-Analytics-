# Toronto Island Ferry Analytics

Real-Time Ferry Ticket Sales & Redemption Analytics for Toronto Island Park (15-minute intervals, 2015–2025).

This project builds a data pipeline (ingestion → cleaning → feature engineering → EDA) and a Streamlit dashboard for operational scheduling insights.

## Setup

From the repository root:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r ferry_analytics/requirements.txt
```

## Data location

Place the raw dataset at:

- `ferry_analytics/data/raw/Toronto Island Ferry Tickets.csv`

(This repo scaffolding copies it from `Data/Toronto Island Ferry Tickets.csv` if it exists.)

## Run the pipeline (in order)

From the repository root:

```bash
python ferry_analytics/notebooks/01_data_ingestion.py
python ferry_analytics/notebooks/02_data_cleaning.py
python ferry_analytics/notebooks/03_feature_engineering.py
python ferry_analytics/notebooks/04_eda_analysis.py
```

### Outputs

- Cleaned dataset: `ferry_analytics/data/processed/ferry_cleaned.csv`
- Featured dataset: `ferry_analytics/data/processed/ferry_featured.csv`
- EDA figures: `ferry_analytics/reports/figures/`

## Run the dashboard

From the repository root:

```bash
streamlit run ferry_analytics/dashboard/app.py
```

Then use the sidebar to filter by date range, year, season, and time of day.

