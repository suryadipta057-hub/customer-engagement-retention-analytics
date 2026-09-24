# Customer Engagement & Product Utilization Analytics for Retention Strategy

A Streamlit analytics dashboard that studies customer churn through **engagement, product utilization, financial commitment, and relationship strength**.

## Project objective

The project evaluates:
- Engagement vs. churn
- Product depth vs. churn
- High-balance but inactive customers
- Credit-card ownership and retention
- Relationship Strength Index (RSI)

## Dataset

The project uses the supplied European Bank customer dataset containing 10,000 customer records and 14 fields, including `IsActiveMember`, `NumOfProducts`, `Balance`, `EstimatedSalary`, and `Exited`.

## Dashboard modules

1. **Executive Overview** — KPIs, churn distribution, geography comparison
2. **Engagement Analysis** — activity and engagement profiles
3. **Product Utilization** — product count, single vs. multi-product, credit card
4. **At-Risk Customers** — high-balance + inactive customer detector
5. **Relationship Strength** — transparent 0–5 RSI and churn relationship

## Tech stack

- Python
- Pandas
- NumPy
- Plotly
- Streamlit

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Repository structure

```text
customer-engagement-retention-analytics/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── European_Bank.csv
├── src/
└── assets/
```

## Analytical note

The Relationship Strength Index is a project-specific, interpretable scoring framework:
- +2 active member
- +2 for 2 or more products
- +1 for credit-card ownership

The research paper notes that the dataset is cross-sectional and that the RSI weights are heuristic. Therefore, the dashboard presents relationships/associations rather than causal claims.

## Project report

See the accompanying research paper submitted with this project.

## Deployment

This repository is designed for deployment on Streamlit Community Cloud. After the GitHub repository is created, deploy `app.py` as the main file.

## Author

Prepared as part of the Unified Mentor Applied Analytics Program.
