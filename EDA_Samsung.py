import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('samsung_global_sales_dataset.csv')

# 1. Page Config (Sets the "Business" vibe)
st.set_page_config(page_title="Samsung Global Sales Intelligence", layout="wide")

st.title("📱 Samsung Global Sales Strategy Dashboard")
st.markdown("### Real-time EDA & Market Performance")

# 2. Sidebar Filters (The Interactivity)
st.sidebar.header("Filter Your Data")
selected_region = st.sidebar.multiselect("Select Region", df['region'].unique(), default=df['region'].unique())
selected_cat = st.sidebar.multiselect("Select Category", df['category'].unique(), default=df['category'].unique())

# Filter the dataframe based on selection
filtered_df = df[(df['region'].isin(selected_region)) & (df['category'].isin(selected_cat))]

# 3. Key Metrics (KPIs)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Revenue", f"${filtered_df['revenue_usd'].sum():,.0f}")
with col2:
    st.metric("Units Sold", f"{filtered_df['units_sold'].sum():,.0f}")
with col3:
    st.metric("Avg Discount", f"{filtered_df['discount_pct'].mean():.1f}%")
with col4:
    st.metric("Avg Rating", f"{filtered_df['customer_rating'].mean():.2f} ⭐")

st.divider()

# 4. Interactive Visuals
row1_col1, row1_col2 = st.columns([2, 1]) # Make the first column wider

with row1_col1:
    st.subheader("🌍 Global Sales Distribution")
    fig_map = px.choropleth(filtered_df, locations="country", locationmode='country names',
                            color="revenue_usd", hover_name="country",
                            color_continuous_scale="Viridis", template="plotly_dark")
    st.plotly_chart(fig_map, use_container_width=True)

with row1_col2:
    st.subheader("📦 Top Products by Revenue")
    top_p = filtered_df.groupby('product_name')['revenue_usd'].sum().nlargest(10).reset_index()
    fig_bar = px.bar(top_p, x='revenue_usd', y='product_name', orientation='h', color='revenue_usd')
    st.plotly_chart(fig_bar, use_container_width=True)

# 5. Business Insight Section
st.subheader("💡 Strategic Insights: Price vs. Sales Volume")
fig_scatter = px.scatter(filtered_df, x="unit_price_usd", y="units_sold", 
                         color="category", size="revenue_usd", hover_data=['product_name'],
                         log_x=True, template="plotly_white")
st.plotly_chart(fig_scatter, use_container_width=True)