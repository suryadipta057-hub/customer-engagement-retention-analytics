import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Customer Engagement & Retention Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def load_data():
    df = pd.read_csv("data/European_Bank.csv")
    # Standardize binary fields and create analytical features
    for col in ["HasCrCard", "IsActiveMember", "Exited"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce").fillna(0)
    df["EstimatedSalary"] = pd.to_numeric(df["EstimatedSalary"], errors="coerce").fillna(0)
    df["NumOfProducts"] = pd.to_numeric(df["NumOfProducts"], errors="coerce").fillna(0).astype(int)
    high_balance_cutoff = df["Balance"].quantile(0.75)
    df["BalanceTier"] = np.where(df["Balance"] >= high_balance_cutoff, "High Balance", "Standard Balance")
    df["EngagementProfile"] = np.select(
        [
            (df["IsActiveMember"] == 1) & (df["NumOfProducts"] >= 2),
            (df["IsActiveMember"] == 1) & (df["NumOfProducts"] == 1),
            (df["IsActiveMember"] == 0) & (df["Balance"] >= high_balance_cutoff),
        ],
        ["Active Engaged", "Active Low-Product", "Inactive High-Balance"],
        default="Inactive Disengaged",
    )
    # Relationship Strength Index: activity (+2), product depth (+2), credit card (+1)
    df["RSI"] = (
        (df["IsActiveMember"] == 1).astype(int) * 2
        + (df["NumOfProducts"] >= 2).astype(int) * 2
        + (df["HasCrCard"] == 1).astype(int)
    )
    df["RelationshipTier"] = pd.cut(
        df["RSI"],
        bins=[-1, 1, 3, 5],
        labels=["Weak", "Moderate", "Strong"],
    )
    return df, float(high_balance_cutoff)

df, high_balance_cutoff = load_data()

# ---------- Sidebar ----------
st.sidebar.title("🔎 Dashboard Filters")
geographies = st.sidebar.multiselect(
    "Geography",
    options=sorted(df["Geography"].dropna().unique()),
    default=sorted(df["Geography"].dropna().unique()),
)
activity = st.sidebar.multiselect(
    "Engagement",
    options=["Active", "Inactive"],
    default=["Active", "Inactive"],
)
min_products, max_products = int(df["NumOfProducts"].min()), int(df["NumOfProducts"].max())
product_range = st.sidebar.slider(
    "Number of products",
    min_value=min_products,
    max_value=max_products,
    value=(min_products, max_products),
)
min_balance, max_balance = float(df["Balance"].min()), float(df["Balance"].max())
balance_range = st.sidebar.slider(
    "Balance range (€)",
    min_value=float(min_balance),
    max_value=float(max_balance),
    value=(float(min_balance), float(max_balance)),
)

filtered = df[
    df["Geography"].isin(geographies)
    & df["IsActiveMember"].isin([1 if x == "Active" else 0 for x in activity])
    & df["NumOfProducts"].between(product_range[0], product_range[1])
    & df["Balance"].between(balance_range[0], balance_range[1])
].copy()

# ---------- Header ----------
st.title("📊 Customer Engagement & Product Utilization Analytics")
st.markdown(
    "**Retention Strategy Dashboard** · Behavioral and relationship-strength approach to customer churn"
)
st.caption("Dataset: European Bank Customer Records · 10,000 customer records · 2025 snapshot")

# ---------- KPI row ----------
total = len(filtered)
churned = int(filtered["Exited"].sum()) if total else 0
churn_rate = (churned / total * 100) if total else 0
active_rate = (filtered["IsActiveMember"].mean() * 100) if total else 0
avg_products = filtered["NumOfProducts"].mean() if total else 0
avg_balance = filtered["Balance"].mean() if total else 0
high_balance_inactive = filtered[(filtered["Balance"] >= high_balance_cutoff) & (filtered["IsActiveMember"] == 0)]
hb_inactive_rate = high_balance_inactive["Exited"].mean() * 100 if len(high_balance_inactive) else 0

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Customers", f"{total:,}")
c2.metric("Churn Rate", f"{churn_rate:.1f}%")
c3.metric("Active Members", f"{active_rate:.1f}%")
c4.metric("Avg Products", f"{avg_products:.2f}")
c5.metric("Avg Balance", f"€{avg_balance:,.0f}")
c6.metric("High-Balance + Inactive Churn", f"{hb_inactive_rate:.1f}%")

st.divider()

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Overview",
    "Engagement Analysis",
    "Product Utilization",
    "At-Risk Customers",
    "Relationship Strength",
])

with tab1:
    left, right = st.columns(2)
    with left:
        churn_counts = filtered["Exited"].value_counts().rename(index={0: "Retained", 1: "Churned"}).reset_index()
        churn_counts.columns = ["Status", "Customers"]
        fig = px.pie(churn_counts, names="Status", values="Customers", hole=0.55,
                     title="Overall Retention vs Churn")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        geo = filtered.groupby("Geography", as_index=False)["Exited"].mean()
        geo["Churn Rate"] = geo["Exited"] * 100
        fig = px.bar(geo, x="Geography", y="Churn Rate", text="Churn Rate",
                     title="Churn Rate by Geography")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Executive Takeaways")
    st.markdown(
        """
        - **Engagement:** active membership is evaluated alongside product depth to identify behavioral risk.
        - **Product depth:** single- vs multi-product customers are compared to understand relationship strength.
        - **Silent churn:** high-balance inactive customers are surfaced separately because balance alone can hide disengagement.
        - **Relationship strength:** the RSI combines activity, product depth, and credit-card ownership into an interpretable 0–5 score.
        """
    )

with tab2:
    profile = filtered.groupby("EngagementProfile", as_index=False).agg(
        Customers=("CustomerId", "count"),
        Churn_Rate=("Exited", "mean")
    )
    profile["Churn Rate"] = profile["Churn_Rate"] * 100
    profile = profile.sort_values("Churn Rate", ascending=False)
    fig = px.bar(profile, x="EngagementProfile", y="Churn Rate", text="Churn Rate",
                 title="Churn Rate by Engagement Profile")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    activity_df = filtered.groupby("IsActiveMember", as_index=False)["Exited"].mean()
    activity_df["Engagement"] = activity_df["IsActiveMember"].map({0: "Inactive", 1: "Active"})
    activity_df["Churn Rate"] = activity_df["Exited"] * 100
    fig = px.bar(activity_df, x="Engagement", y="Churn Rate", text="Churn Rate",
                 title="Active vs Inactive Churn")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    prod = filtered.groupby("NumOfProducts", as_index=False).agg(
        Customers=("CustomerId", "count"),
        Churn_Rate=("Exited", "mean")
    )
    prod["Churn Rate"] = prod["Churn_Rate"] * 100
    fig = px.bar(prod, x="NumOfProducts", y="Churn Rate", text="Churn Rate",
                 hover_data=["Customers"], title="Churn Rate by Number of Products")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    single = filtered.assign(ProductGroup=np.where(filtered["NumOfProducts"] == 1, "Single Product", "Multi-Product"))
    single_summary = single.groupby("ProductGroup", as_index=False)["Exited"].mean()
    single_summary["Churn Rate"] = single_summary["Exited"] * 100
    fig = px.bar(single_summary, x="ProductGroup", y="Churn Rate", text="Churn Rate",
                 title="Single-Product vs Multi-Product Churn")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    card = filtered.groupby("HasCrCard", as_index=False)["Exited"].mean()
    card["Card Ownership"] = card["HasCrCard"].map({0: "No Card", 1: "Cardholder"})
    card["Churn Rate"] = card["Exited"] * 100
    fig = px.bar(card, x="Card Ownership", y="Churn Rate", text="Churn Rate",
                 title="Credit Card Ownership vs Churn")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("High-Value Disengaged Customer Detector")
    at_risk = filtered[
        (filtered["Balance"] >= high_balance_cutoff) &
        (filtered["IsActiveMember"] == 0)
    ].copy()
    st.write(
        f"High-balance threshold (top quartile): **€{high_balance_cutoff:,.0f}** · "
        f"Matching customers: **{len(at_risk):,}**"
    )
    if len(at_risk):
        summary = at_risk["Exited"].mean() * 100
        st.metric("Churn rate in this segment", f"{summary:.1f}%")
        display_cols = [
            "CustomerId", "Surname", "Geography", "Age", "Tenure",
            "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember",
            "EstimatedSalary", "Exited", "RSI"
        ]
        st.dataframe(
            at_risk[display_cols].sort_values("Balance", ascending=False).head(100),
            use_container_width=True,
            hide_index=True,
        )
        st.caption("Showing up to 100 highest-balance records. Use the sidebar to narrow the population.")
    else:
        st.info("No customers match the selected high-balance + inactive criteria.")

with tab5:
    rsi = filtered.groupby(["RSI", "RelationshipTier"], as_index=False).agg(
        Customers=("CustomerId", "count"),
        Churn_Rate=("Exited", "mean")
    )
    rsi["Churn Rate"] = rsi["Churn_Rate"] * 100
    fig = px.line(rsi, x="RSI", y="Churn Rate", markers=True,
                  hover_data=["Customers", "RelationshipTier"],
                  title="Relationship Strength Index vs Churn")
    fig.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Relationship Strength Index")
    st.markdown(
        """
        **RSI scoring:** +2 for active membership, +2 for holding 2 or more products,
        and +1 for credit-card ownership. This produces a transparent 0–5 score.
        The score is an analytical framework for this project, not a bank-standard risk score.
        """
    )
    st.dataframe(
        rsi[["RSI", "RelationshipTier", "Customers", "Churn Rate"]]
        .sort_values("RSI"),
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.caption("For educational/analytical use. Findings are associations in a cross-sectional dataset and should not be interpreted as causal effects.")
