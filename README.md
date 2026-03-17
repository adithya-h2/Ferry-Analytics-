# Toronto Island Ferry Analytics Dashboard

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat&logo=python&logoColor=white)](https://python.org)

A **Streamlit dashboard** for analyzing **15-minute ferry ticket Sales vs Redemption patterns** (2015–2025) to support data-driven scheduling decisions.

---

## 🚀 Live Demo

**[Try it live on Streamlit Cloud →](https://dodg4eirn2tkyeedte4dhh.streamlit.app/)**

---

## ✨ Features

- **Interactive Filters**
  - Date range selector
  - Year filter
  - Season filter
  - Time of day filter

- **Key Performance Indicators (KPIs)**
  - Total tickets sold
  - Total tickets redeemed
  - Net passenger movement
  - Peak hour identification

- **Visualizations**
  - Time series chart (Sales vs Redemptions)
  - Hourly average bar chart
  - Hour × Day-of-Week heatmap

- **Deployment-Safe Data Loading**
  - Uses `data/processed/ferry_featured.csv` when available
  - Falls back to sample data with a friendly message (prevents crashes on Streamlit Cloud)

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|--------|
| **Python** | Core programming language |
| **pandas** | Data manipulation & analysis |
| **numpy** | Numerical computations |
| **matplotlib** | Static plotting |
| **seaborn** | Statistical visualizations |
| **plotly** | Interactive charts |
| **streamlit** | Web dashboard framework |

---

## 📁 Project Structure

```
Ferry-Analytics-
├── dashboard/
│   ├── app.py                 # Streamlit entrypoint (Main file path)
│   ├── components/
│   │   ├── filters.py         # Interactive filter widgets
│   │   ├── kpi_cards.py       # KPI metric display
│   │   └── charts.py          # Visualization components
│   └── utils/
│       └── data_loader.py     # Cached loader + sample fallback
├── data/
│   └── processed/
│       └── ferry_featured.csv # Featured dataset (optional, recommended)
├── dashboard/                 # Dashboard folder
├── prepare_deploy.py          # Dataset size reducer for deployment
├── requirements.txt           # Python dependencies
├── runtime.txt                # Python runtime version
└── README.md                  # This file
```

---

## 💻 Run Locally

```bash
# Clone the repository
git clone https://github.com/adithya-h2/Ferry-Analytics-.git
cd Ferry-Analytics-

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard/app.py
```

---

## 📄 Data

### Recommended Dataset for Deployment

Keep a size-safe featured dataset at:
```
data/processed/ferry_featured.csv
```

### How Data Loading Works

- **If `ferry_featured.csv` exists**: The app loads the full dataset for analysis.
- **If missing**: The app loads **sample data** and displays a friendly message explaining what’s expected. This ensures the app never crashes on Streamlit Cloud.

### Data Source

The dataset contains 15-minute interval ferry ticket data including:
- Ticket sales counts
- Ticket redemption counts
- Timestamps for temporal analysis

---

## ☁️ Deployment (Streamlit Cloud)

1. **Repository**: Connect your GitHub repo
2. **Branch**: `main`
3. **Main file path**: `dashboard/app.py`
4. **Python version** (Recommended): Choose **Python 3.11** or **3.12** in Advanced settings
5. **Deploy!**

### Optional: Reduce Dataset Size

If your dataset is too large for Streamlit Cloud, use:
```bash
python prepare_deploy.py
```

---

## 🤖 AI Usage

This project was accelerated with **AI assistance** to:

1. **Scaffold** the pipeline + dashboard structure
2. **Generate** reusable Streamlit components
3. **Implement** a deployment-safe data loader
4. **Troubleshoot** Streamlit Cloud build/import issues quickly

---

## 📊 Insights & Results

*Coming soon — analysis of peak hours, seasonal trends, and scheduling recommendations based on the ferry data.*

---

## 🧑‍💻 Author

**Adithya N C**  
[GitHub](https://github.com/adithya-h2)

---

*Built with ❤️ and Streamlit*
