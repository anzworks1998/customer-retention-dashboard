import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Customer Retention Dashboard", layout="wide")

# ------------------ LOAD DATA ------------------
df = pd.read_csv("final_data.csv")

# ------------------ STYLING ------------------
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        color: #1f4e79;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
    }
    .summary-box {
        background-color: #eef4fb;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
col1, col2, col3 = st.columns([1,2,1])

with col1:
    st.image("mentor_logo.png", width=120)

with col2:
    st.markdown("<div class='main-title'>Customer Engagement & Product Utilization Analytics for Retention Strategy</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Presented by <b>Geetanjali Sateesh</b><br>Mentored by <b>Saiprasad Kagne</b></div>", unsafe_allow_html=True)

with col3:
    st.image("ecb_logo.png", width=120)

st.markdown("---")

# ------------------ SIDEBAR ------------------
st.sidebar.header("🔎 Filters")

engagement_filter = st.sidebar.selectbox("Customer Activity", ["All", "Active", "Inactive"])
product_range = st.sidebar.slider("Number of Products", 1, 4, (1,4))
balance_range = st.sidebar.slider("Balance", 0, int(df['Balance'].max()), (0, int(df['Balance'].max())))
salary_range = st.sidebar.slider("Estimated Salary", 0, int(df['EstimatedSalary'].max()), (0, int(df['EstimatedSalary'].max())))

# ------------------ APPLY FILTERS ------------------
filtered_df = df.copy()

if engagement_filter == "Active":
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 1]
elif engagement_filter == "Inactive":
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 0]

filtered_df = filtered_df[
    (filtered_df['NumOfProducts'] >= product_range[0]) &
    (filtered_df['NumOfProducts'] <= product_range[1]) &
    (filtered_df['Balance'] >= balance_range[0]) &
    (filtered_df['Balance'] <= balance_range[1]) &
    (filtered_df['EstimatedSalary'] >= salary_range[0]) &
    (filtered_df['EstimatedSalary'] <= salary_range[1])
]

# ------------------ RELATIONSHIP STRENGTH ------------------
filtered_df['EngagementScore'] = filtered_df['IsActiveMember']

filtered_df['RelationshipStrength'] = (
    filtered_df['EngagementScore'] * 0.7 +
    (filtered_df['NumOfProducts'] / filtered_df['NumOfProducts'].max()) * 0.3
)

# ------------------ EXECUTIVE SUMMARY ------------------
st.markdown("## 🧾 Executive Summary")

if len(filtered_df) > 0:
    churn_rate = filtered_df['Exited'].mean()
    avg_products = filtered_df['NumOfProducts'].mean()
    inactive_pct = (filtered_df['IsActiveMember'] == 0).mean()
else:
    churn_rate, avg_products, inactive_pct = 0,0,0

st.markdown(f"""
<div class="summary-box">
<b>Key Insights:</b><br><br>
• Overall churn rate stands at <b>{churn_rate:.2f}</b>, indicating the proportion of customers leaving the bank.<br>
• Customers use an average of <b>{avg_products:.2f}</b> products, reflecting product adoption levels.<br>
• Approximately <b>{inactive_pct:.2f}</b> of customers are inactive, highlighting engagement gaps.<br><br>

<b>Business Interpretation:</b><br>
Higher engagement and increased product usage significantly reduce churn probability. Inactive customers, especially those with high balances, represent a key risk segment requiring targeted retention strategies.
</div>
""", unsafe_allow_html=True)

# ------------------ KPI SECTION ------------------
st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

active_df = filtered_df[filtered_df['IsActiveMember'] == 1]
inactive_df = filtered_df[filtered_df['IsActiveMember'] == 0]

if len(active_df) == 0 or len(inactive_df) == 0:
    engagement_retention_ratio = None
else:
    active_churn = active_df['Exited'].mean()
    inactive_churn = inactive_df['Exited'].mean()
    engagement_retention_ratio = inactive_churn / active_churn if active_churn != 0 else None

col1.metric("Engagement Retention Ratio", round(engagement_retention_ratio,2) if engagement_retention_ratio else "N/A")

product_depth_kpi = (filtered_df['NumOfProducts'] / filtered_df['NumOfProducts'].max()).mean() if len(filtered_df)>0 else None
col2.metric("Product Depth Index", round(product_depth_kpi,2) if product_depth_kpi else "N/A")

high_balance = filtered_df[filtered_df['Balance'] > filtered_df['Balance'].quantile(0.75)]
disengaged = high_balance[high_balance['IsActiveMember'] == 0]
high_balance_rate = (len(disengaged)/len(high_balance)) if len(high_balance)>0 else None
col3.metric("High-Balance Disengagement", f"{high_balance_rate*100:.1f}%" if high_balance_rate else "N/A")

cc = filtered_df.groupby('HasCrCard')['Exited'].mean()
if 0 in cc and 1 in cc and (1-cc[0]) != 0:
    cc_score = (1-cc[1])/(1-cc[0])
else:
    cc_score = None
col4.metric("Credit Card Stickiness", round(cc_score,2) if cc_score else "N/A")

rs = filtered_df['RelationshipStrength'].mean() if len(filtered_df)>0 else None
col5.metric("Relationship Strength", round(rs,2) if rs else "N/A")

st.markdown("---")

# ================== MODULE 1 ==================
st.markdown("## 👥 Engagement vs Churn Overview")
st.markdown("### 📌 Churn Distribution by Customer Activity")

fig1 = px.histogram(filtered_df, x="IsActiveMember", color="Exited", barmode="group")
st.plotly_chart(fig1, use_container_width=True)

st.info("Active customers show significantly lower churn compared to inactive customers.")

# ================== MODULE 2 ==================
st.markdown("## 📦 Product Utilization Impact Analysis")

st.markdown("### 📌 Churn Rate by Number of Products")
product_churn = filtered_df.groupby('NumOfProducts')['Exited'].mean().reset_index()
fig2 = px.line(product_churn, x='NumOfProducts', y='Exited', markers=True)
st.plotly_chart(fig2, use_container_width=True)

st.info("Churn decreases as product usage increases.")

st.markdown("### 📌 Single vs Multi-Product Customer Churn")
filtered_df['ProductCategory'] = filtered_df['NumOfProducts'].apply(lambda x: 'Single' if x==1 else 'Multi')
single_multi = filtered_df.groupby('ProductCategory')['Exited'].mean().reset_index()
fig3 = px.bar(single_multi, x='ProductCategory', y='Exited', text='Exited')
st.plotly_chart(fig3, use_container_width=True)

st.info("Single-product customers show higher churn risk.")

# ================== MODULE 3 ==================
st.markdown("## 🚨 High-Value Disengaged Customers")

at_risk = filtered_df[(filtered_df['Balance'] > filtered_df['Balance'].quantile(0.75)) & (filtered_df['IsActiveMember']==0)]

st.metric("Total At-Risk Customers", len(at_risk))
st.dataframe(at_risk.head(20))

# ================== MODULE 4 ==================
st.markdown("## 🧲 Retention Strength Analysis")

st.markdown("### 📌 Relationship Strength Distribution")

fig4 = px.histogram(filtered_df, x="RelationshipStrength", nbins=25)
st.plotly_chart(fig4, use_container_width=True)

st.info("Higher relationship strength reduces churn probability.")