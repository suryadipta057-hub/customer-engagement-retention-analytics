"""
Customer Engagement & Product Utilization Analytics for Retention Strategy
Streamlit dashboard — European Bank Customer Records (N = 10,000)
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Engagement & Retention Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#0B3D5C"
ACCENT = "#C0392B"
TEAL = "#1A8F8F"
GOLD = "#D4A017"
PALETTE = [PRIMARY, TEAL, GOLD, ACCENT]

# ----------------------------------------------------------------------------
# Data loading & feature engineering
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path="data/European_Bank.csv"):
    df = pd.read_csv(path)

    # Behavioral / engineered fields --------------------------------------
    balance_q4 = df["Balance"].quantile(0.75)
    df["HighBalance"] = df["Balance"] >= balance_q4

    def engagement_profile(row):
        if row["IsActiveMember"] == 1 and row["NumOfProducts"] >= 2:
            return "Active Engaged"
        if row["IsActiveMember"] == 1 and row["NumOfProducts"] == 1:
            return "Active Low-Product"
        if row["IsActiveMember"] == 0 and not row["HighBalance"]:
            return "Inactive Disengaged"
        return "Inactive High-Balance"

    df["EngagementProfile"] = df.apply(engagement_profile, axis=1)

    df["ProductTier"] = np.where(df["NumOfProducts"] >= 2, "Multi-Product", "Single-Product")

    # Relationship Strength Index (0-5): active +2, 2+ products +2, card +1
    df["RSI"] = (
        (df["IsActiveMember"] == 1) * 2
        + (df["NumOfProducts"] >= 2) * 2
        + (df["HasCrCard"] == 1) * 1
    )

    age_bins = [17, 30, 40, 50, 60, 100]
    age_labels = ["18-30", "31-40", "41-50", "51-60", "60+"]
    df["AgeGroup"] = pd.cut(df["Age"], bins=age_bins, labels=age_labels)

    return df, balance_q4


df, BALANCE_Q4 = load_data()

# ----------------------------------------------------------------------------
# Sidebar — global filters
# ----------------------------------------------------------------------------
st.sidebar.title("🏦 Filters")
st.sidebar.caption("Filters apply to every module below.")

geo_sel = st.sidebar.multiselect(
    "Geography", sorted(df["Geography"].unique()), default=sorted(df["Geography"].unique())
)
gender_sel = st.sidebar.multiselect(
    "Gender", sorted(df["Gender"].unique()), default=sorted(df["Gender"].unique())
)
engagement_sel = st.sidebar.multiselect(
    "Engagement profile",
    ["Active Engaged", "Active Low-Product", "Inactive Disengaged", "Inactive High-Balance"],
    default=["Active Engaged", "Active Low-Product", "Inactive Disengaged", "Inactive High-Balance"],
)
product_sel = st.sidebar.slider(
    "Number of products", int(df["NumOfProducts"].min()), int(df["NumOfProducts"].max()), (1, 4)
)
balance_sel = st.sidebar.slider(
    "Balance range (€)",
    0,
    int(df["Balance"].max()),
    (0, int(df["Balance"].max())),
    step=1000,
)
salary_sel = st.sidebar.slider(
    "Estimated salary range (€)",
    int(df["EstimatedSalary"].min()),
    int(df["EstimatedSalary"].max()),
    (int(df["EstimatedSalary"].min()), int(df["EstimatedSalary"].max())),
    step=1000,
)
active_only = st.sidebar.radio("Activity status", ["All", "Active only", "Inactive only"], index=0)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: European Bank Customer Records, N = 10,000 (France, Germany, Spain). "
    "High-balance = top quartile, ≥ €{:,.0f}.".format(BALANCE_Q4)
)

fdf = df[
    df["Geography"].isin(geo_sel)
    & df["Gender"].isin(gender_sel)
    & df["EngagementProfile"].isin(engagement_sel)
    & df["NumOfProducts"].between(product_sel[0], product_sel[1])
    & df["Balance"].between(balance_sel[0], balance_sel[1])
    & df["EstimatedSalary"].between(salary_sel[0], salary_sel[1])
]
if active_only == "Active only":
    fdf = fdf[fdf["IsActiveMember"] == 1]
elif active_only == "Inactive only":
    fdf = fdf[fdf["IsActiveMember"] == 0]

if fdf.empty:
    st.warning("No customers match the current filters. Widen a filter in the sidebar.")
    st.stop()

# ----------------------------------------------------------------------------
# Header + top-line KPIs
# ----------------------------------------------------------------------------
st.title("Customer Engagement & Product Utilization Analytics")
st.caption("Retention strategy dashboard · European Bank Customer Records · Unified Mentor — The European Central Bank")

churn_rate = fdf["Exited"].mean() * 100
n_customers = len(fdf)
n_churned = int(fdf["Exited"].sum())
avg_bal_churn = fdf.loc[fdf["Exited"] == 1, "Balance"].mean()
avg_bal_retain = fdf.loc[fdf["Exited"] == 0, "Balance"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Customers (filtered)", f"{n_customers:,}")
k2.metric("Churn rate", f"{churn_rate:.1f}%")
k3.metric("Churned customers", f"{n_churned:,}")
k4.metric("Avg. balance — churned", f"€{avg_bal_churn:,.0f}" if not np.isnan(avg_bal_churn) else "—")
k5.metric("Avg. balance — retained", f"€{avg_bal_retain:,.0f}" if not np.isnan(avg_bal_retain) else "—")

st.markdown("---")

# ----------------------------------------------------------------------------
# Tabs = Core Modules
# ----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Engagement vs Churn",
        "🧩 Product Utilization",
        "💎 High-Value Disengaged Detector",
        "🛡️ Retention Strength Scoring",
    ]
)

# ---- Tab 1: Engagement vs churn overview -----------------------------------
with tab1:
    st.subheader("Engagement vs Churn Overview")
    c1, c2 = st.columns([1.3, 1])

    with c1:
        prof_churn = (
            fdf.groupby("EngagementProfile")["Exited"]
            .mean()
            .mul(100)
            .reindex(["Active Engaged", "Active Low-Product", "Inactive Disengaged", "Inactive High-Balance"])
            .dropna()
        )
        fig = px.bar(
            prof_churn,
            x=prof_churn.index,
            y=prof_churn.values,
            color=prof_churn.index,
            color_discrete_sequence=PALETTE,
            labels={"x": "Engagement profile", "y": "Churn rate (%)"},
            title="Churn Rate by Engagement Profile",
            text=[f"{v:.1f}%" for v in prof_churn.values],
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, yaxis_range=[0, max(prof_churn.values) * 1.25])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        comp = fdf["EngagementProfile"].value_counts()
        fig2 = px.pie(
            comp, values=comp.values, names=comp.index, hole=0.45,
            color=comp.index, color_discrete_sequence=PALETTE,
            title="Customer Base Composition",
        )
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        act_churn = fdf.groupby("IsActiveMember")["Exited"].mean().mul(100)
        act_churn.index = act_churn.index.map({0: "Inactive", 1: "Active"})
        fig3 = px.bar(
            act_churn, x=act_churn.index, y=act_churn.values,
            color=act_churn.index, color_discrete_sequence=[ACCENT, PRIMARY],
            text=[f"{v:.1f}%" for v in act_churn.values],
            labels={"x": "Activity status", "y": "Churn rate (%)"},
            title="Activity Status vs Churn",
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        geo_churn = fdf.groupby("Geography")["Exited"].mean().mul(100).sort_values()
        fig4 = px.bar(
            geo_churn, x=geo_churn.values, y=geo_churn.index, orientation="h",
            color=geo_churn.index, color_discrete_sequence=PALETTE,
            text=[f"{v:.1f}%" for v in geo_churn.values],
            labels={"x": "Churn rate (%)", "y": ""},
            title="Churn Rate by Geography",
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.info(
        "**Reading this module:** Active Engaged customers (active + 2 or more products) show the lowest "
        "churn of any segment; Inactive High-Balance customers show the highest — the clearest evidence "
        "that engagement, not wealth, drives retention."
    )

# ---- Tab 2: Product utilization impact -------------------------------------
with tab2:
    st.subheader("Product Utilization Impact Analysis")
    c1, c2 = st.columns(2)

    with c1:
        prod_churn = fdf.groupby("NumOfProducts")["Exited"].mean().mul(100)
        prod_count = fdf.groupby("NumOfProducts")["Exited"].count()
        fig = go.Figure()
        fig.add_bar(x=prod_churn.index, y=prod_churn.values, name="Churn rate (%)", marker_color=PRIMARY,
                    text=[f"{v:.1f}%" for v in prod_churn.values], textposition="outside")
        fig.add_trace(go.Scatter(x=prod_count.index, y=prod_count.values, name="Customer count",
                                  yaxis="y2", mode="lines+markers", line=dict(color=GOLD, width=3)))
        fig.update_layout(
            title="Churn Rate by Number of Products (with Customer Volume)",
            xaxis_title="Number of products held",
            yaxis=dict(title="Churn rate (%)"),
            yaxis2=dict(title="Customer count", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.15),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        tier_churn = fdf.groupby("ProductTier")["Exited"].mean().mul(100)
        fig2 = px.bar(
            tier_churn, x=tier_churn.index, y=tier_churn.values,
            color=tier_churn.index, color_discrete_sequence=[TEAL, ACCENT],
            text=[f"{v:.1f}%" for v in tier_churn.values],
            labels={"x": "", "y": "Churn rate (%)"},
            title="Single-Product vs Multi-Product Retention",
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        card_churn = fdf.groupby("HasCrCard")["Exited"].mean().mul(100)
        card_churn.index = card_churn.index.map({0: "No credit card", 1: "Has credit card"})
        fig3 = px.bar(
            card_churn, x=card_churn.index, y=card_churn.values,
            color=card_churn.index, color_discrete_sequence=["#8C97A6", TEAL],
            text=[f"{v:.1f}%" for v in card_churn.values],
            labels={"x": "", "y": "Churn rate (%)"},
            title="Credit Card Ownership vs Churn",
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.markdown("#### Product Depth Index")
        pdi = fdf.groupby("ProductTier")["Exited"].mean().mul(100)
        try:
            st.metric("Multi-product churn", f"{pdi.get('Multi-Product', float('nan')):.1f}%")
            st.metric("Single-product churn", f"{pdi.get('Single-Product', float('nan')):.1f}%")
        except Exception:
            st.write("Not enough data in current filter.")
        st.caption(
            "Churn is minimized at exactly **two** products in the full dataset. A third or fourth product "
            "is associated with sharply elevated churn — likely forced cross-sell rather than loyalty."
        )

    st.info(
        "**Reading this module:** Product count is the strongest single predictor of churn. Credit card "
        "ownership alone shows almost no relationship with retention."
    )

# ---- Tab 3: High-value disengaged customer detector -------------------------
with tab3:
    st.subheader("High-Value Disengaged Customer Detector")
    st.caption("Identifies customers who look financially healthy but are behaviorally disengaged — the 'silent churn' risk pool.")

    c1, c2, c3 = st.columns(3)
    min_balance = c1.number_input("Minimum balance (€)", min_value=0, value=int(BALANCE_Q4), step=1000)
    min_salary = c2.number_input("Minimum estimated salary (€)", min_value=0, value=0, step=1000)
    require_inactive = c3.checkbox("Inactive members only", value=True)

    at_risk = fdf[fdf["Balance"] >= min_balance]
    at_risk = at_risk[at_risk["EstimatedSalary"] >= min_salary]
    if require_inactive:
        at_risk = at_risk[at_risk["IsActiveMember"] == 0]

    r1, r2, r3 = st.columns(3)
    r1.metric("At-risk segment size", f"{len(at_risk):,}")
    r2.metric("Churn rate in segment", f"{at_risk['Exited'].mean()*100:.1f}%" if len(at_risk) else "—")
    r3.metric("Already churned", f"{int(at_risk['Exited'].sum()):,}" if len(at_risk) else "—")

    c4, c5 = st.columns(2)
    with c4:
        quad = fdf.groupby(["HighBalance", "IsActiveMember"])["Exited"].mean().mul(100)
        labels = {
            (True, 0): "High-Balance + Inactive",
            (True, 1): "High-Balance + Active",
            (False, 0): "Low-Balance + Inactive",
            (False, 1): "Low-Balance + Active",
        }
        quad_df = pd.DataFrame(
            {"Segment": [labels[i] for i in quad.index], "Churn rate (%)": quad.values}
        ).sort_values("Churn rate (%)", ascending=False)
        fig = px.bar(
            quad_df, x="Segment", y="Churn rate (%)", color="Segment",
            color_discrete_sequence=PALETTE,
            text=[f"{v:.1f}%" for v in quad_df["Churn rate (%)"]],
            title="At-Risk Premium Customers: Balance × Engagement",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c5:
        fig2 = px.scatter(
            fdf, x="Balance", y="EstimatedSalary", color="EngagementProfile",
            symbol="Exited", opacity=0.55, color_discrete_sequence=PALETTE,
            labels={"Exited": "Churned"},
            title="Balance vs Salary by Engagement Profile",
        )
        fig2.add_vline(x=min_balance, line_dash="dash", line_color=ACCENT)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("##### Customer-level list (current filters)")
    show_cols = ["CustomerId", "Surname", "Geography", "Age", "Balance", "EstimatedSalary",
                 "NumOfProducts", "IsActiveMember", "RSI", "Exited"]
    st.dataframe(
        at_risk[show_cols].sort_values("Balance", ascending=False).reset_index(drop=True),
        use_container_width=True, height=320,
    )
    st.download_button(
        "⬇️ Download at-risk segment (CSV)",
        at_risk[show_cols].to_csv(index=False).encode("utf-8"),
        file_name="at_risk_premium_customers.csv",
        mime="text/csv",
    )

# ---- Tab 4: Retention strength scoring --------------------------------------
with tab4:
    st.subheader("Retention Strength Scoring Panel")
    st.caption("Relationship Strength Index (RSI) = Active member (+2) + 2 or more products (+2) + Credit card (+1), scale 0–5.")

    c1, c2 = st.columns([1.3, 1])
    with c1:
        rsi_churn = fdf.groupby("RSI")["Exited"].mean().mul(100)
        fig = px.line(
            rsi_churn, x=rsi_churn.index, y=rsi_churn.values, markers=True,
            labels={"x": "Relationship Strength Index (0 = weakest, 5 = strongest)", "y": "Churn rate (%)"},
            title="Relationship Strength Index vs Churn Rate",
        )
        fig.update_traces(line_color=PRIMARY, line_width=3, marker=dict(size=9, color=ACCENT))
        fig.update_layout(yaxis_range=[0, max(rsi_churn.values) * 1.2 if len(rsi_churn) else 10])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        rsi_count = fdf["RSI"].value_counts().sort_index()
        fig2 = px.bar(
            rsi_count, x=rsi_count.index, y=rsi_count.values,
            color_discrete_sequence=[TEAL],
            labels={"x": "RSI tier", "y": "Customer count"},
            title="Customers per RSI Tier",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("##### Age-group churn context")
    age_churn = fdf.groupby("AgeGroup", observed=True)["Exited"].mean().mul(100)
    fig3 = px.bar(
        age_churn, x=age_churn.index, y=age_churn.values,
        color_discrete_sequence=[PRIMARY],
        text=[f"{v:.1f}%" for v in age_churn.values],
        labels={"x": "Age group", "y": "Churn rate (%)"},
        title="Churn Rate by Age Group",
    )
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

    st.info(
        "**Reading this module:** Churn declines near-monotonically as RSI rises, confirming that combined "
        "behavioral signals (activity + product depth + card) outperform any single metric as a retention lever."
    )

st.markdown("---")
st.caption(
    "Customer Engagement & Product Utilization Analytics for Retention Strategy · "
    "Unified Mentor — The European Central Bank · Dataset N = 10,000, no missing values."
)
