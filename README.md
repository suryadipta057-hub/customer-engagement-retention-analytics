# Customer Engagement & Product Utilization Analytics for Retention Strategy

Interactive Streamlit dashboard analyzing 10,000 European retail bank customer records to evaluate
retention through the lens of **engagement** and **product utilization** — not just demographics.

> Prepared for Unified Mentor — Applied Analytics Program (The European Central Bank).

## 🔗 Live App
_Add your deployed Streamlit Community Cloud link here after deployment, e.g._
`https://your-app-name.streamlit.app`

## 📊 What's inside

- **Engagement vs Churn Overview** — churn by activity status, engagement profile, and geography
- **Product Utilization Impact Analysis** — churn by product count, single vs multi-product, credit card ownership
- **High-Value Disengaged Customer Detector** — configurable filters to surface "silent churn" risk (high-balance, inactive customers), with CSV export
- **Retention Strength Scoring Panel** — a composite Relationship Strength Index (RSI: activity + product depth + card ownership) plotted against churn

Sidebar filters: geography, gender, engagement profile, product count, balance range, salary range, and activity status — all filters apply across every module.

## 🗂 Repository structure

```
bank-retention-dashboard/
├── app.py                  # Streamlit dashboard
├── requirements.txt
├── data/
│   └── European_Bank.csv   # dataset (N = 10,000)
├── docs/
│   └── Research_Paper.pdf  # full EDA research paper
└── README.md
```

## 🚀 Run locally

```bash
git clone https://github.com/<your-username>/bank-retention-dashboard.git
cd bank-retention-dashboard
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy (Streamlit Community Cloud — free)

1. Push this repo to GitHub (see commands below).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app**, pick this repo/branch, set main file to `app.py`, click **Deploy**.
4. Copy the generated `*.streamlit.app` link back into this README.

## 📈 Key findings (from the research paper)

- Single-product customers churn at **27.7%** vs **12.8%** for multi-product customers.
- Inactive members churn at **26.9%** vs **14.3%** for active members.
- **1,247** high-balance, inactive customers ("silent churn" segment) churn at **30.5%**.
- The Relationship Strength Index shows churn falling from **34.5%** (weakest tier) to **9.1%** (strongest tier).

Full methodology, figures, and recommendations are in [`docs/Research_Paper.pdf`](docs/Research_Paper.pdf).

## 🛠 Built with

Python · pandas · Plotly · Streamlit

## 📄 Dataset

`data/European_Bank.csv` — 10,000 rows, 14 fields, no missing values. Column definitions are documented in the research paper (Section 4).
