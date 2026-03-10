import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Samsung Global Sales Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #0a0e1a; color: #e8eaf0; }
section[data-testid="stSidebar"] { background: #0d1120 !important; border-right: 1px solid #1e2540; }

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #111827 0%, #1a2035 100%);
    border: 1px solid #1e2a45;
    border-radius: 14px;
    padding: 18px 20px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
[data-testid="metric-container"] label {
    color: #6b7fa3 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e8eaf0 !important;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.6rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.75rem !important; }

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #c8d0e8;
    letter-spacing: 0.04em;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 2px solid #1e2a45;
}
.tab-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
}
.sidebar-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    color: #5b9ef7;
    margin-bottom: 4px;
}
.sidebar-sub { font-size: 0.72rem; color: #4a5568; margin-bottom: 20px; }

hr { border-color: #1e2540; }
.stPlotlyChart { border-radius: 12px; overflow: hidden; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #1e2a45; border-radius: 10px; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #0d1120;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #1e2540;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #6b7fa3;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    padding: 8px 20px;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: #1e2a45 !important;
    color: #5b9ef7 !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: transparent !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Theme constants ───────────────────────────────────────────────────────────
CHART_BG   = "#0f1422"
PAPER_BG   = "#0f1422"
FONT_COLOR = "#c8d0e8"
GRID_COLOR = "#1a2035"
ACCENT     = "#5b9ef7"
PALETTE    = ["#5b9ef7", "#f77b5b", "#5bf7c0", "#f7d85b", "#c85bf7",
              "#f75b8e", "#5bf75b", "#f7a05b", "#5b7ff7", "#f75b5b"]

def chart_layout(fig, title="", height=340):
    fig.update_layout(
        title=dict(text=title, font=dict(family="Syne", size=14, color=FONT_COLOR), x=0.02),
        paper_bgcolor=PAPER_BG, plot_bgcolor=CHART_BG,
        font=dict(family="DM Sans", color=FONT_COLOR, size=11),
        height=height, margin=dict(l=16, r=16, t=44, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        coloraxis_colorbar=dict(tickfont=dict(color=FONT_COLOR), title=dict(font=dict(color=FONT_COLOR))),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR))
    fig.update_yaxes(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR))
    return fig

def st_title(text):
    st.markdown(f'<p class="section-title">{text}</p>', unsafe_allow_html=True)

# ── Load & cache data ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("samsung_global_sales_dataset.csv")
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df["customer_rating"]    = df["customer_rating"].fillna(df["customer_rating"].median())
    df["previous_device_os"] = df["previous_device_os"].fillna("Unknown")
    df["storage"]            = df.groupby("product_name")["storage"].transform(
        lambda x: x.fillna(x.mode()[0] if not x.mode().empty else "128GB"))
    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-header">📱 Samsung Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-sub">Global Product Sales · 2021–2024</p>', unsafe_allow_html=True)
    st.markdown("#### 🔍 Filters")

    sel_years    = st.multiselect("Year",             sorted(df["year"].unique()),             default=sorted(df["year"].unique()))
    sel_regions  = st.multiselect("Region",           sorted(df["region"].unique()),           default=sorted(df["region"].unique()))
    sel_cats     = st.multiselect("Category",         sorted(df["category"].unique()),         default=sorted(df["category"].unique()))
    sel_channels = st.multiselect("Sales Channel",    sorted(df["sales_channel"].unique()),    default=sorted(df["sales_channel"].unique()))
    sel_segments = st.multiselect("Customer Segment", sorted(df["customer_segment"].unique()), default=sorted(df["customer_segment"].unique()))

    st.markdown("---")
    price_min, price_max = float(df["unit_price_usd"].min()), float(df["unit_price_usd"].max())
    sel_price = st.slider("Unit Price Range (USD)", price_min, price_max, (price_min, price_max), step=10.0)

    st.markdown("---")
    is_5g_opt = st.radio("5G Filter", ["All", "5G Only", "Non-5G"])

# ── Apply filters ─────────────────────────────────────────────────────────────
mask = (
    df["year"].isin(sel_years) &
    df["region"].isin(sel_regions) &
    df["category"].isin(sel_cats) &
    df["sales_channel"].isin(sel_channels) &
    df["customer_segment"].isin(sel_segments) &
    df["unit_price_usd"].between(*sel_price)
)
if is_5g_opt == "5G Only":  mask &= df["is_5g"] == "Yes"
elif is_5g_opt == "Non-5G": mask &= df["is_5g"] == "No"
fdf = df[mask]

if fdf.empty:
    st.warning("⚠️ No data matches the current filters.")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:10px 0 12px 0'>
  <span style='font-family:Syne;font-size:2rem;font-weight:800;color:#e8eaf0'>Samsung Global Sales</span>
  <span style='font-family:DM Sans;font-size:1rem;color:#4a5a7a;margin-left:14px'>Executive Dashboard</span>
</div>
""", unsafe_allow_html=True)

# ── Global KPIs (always visible above tabs) ───────────────────────────────────
total_rev   = fdf["revenue_usd"].sum()
total_units = fdf["units_sold"].sum()
avg_price   = fdf["unit_price_usd"].mean()
avg_rating  = fdf["customer_rating"].mean()
return_rate = (fdf["return_status"] == "Returned").mean() * 100
pct_5g      = (fdf["is_5g"] == "Yes").mean() * 100

k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("💰 Total Revenue",  f"${total_rev/1e6:.1f}M")
k2.metric("📦 Units Sold",     f"{total_units:,.0f}")
k3.metric("🏷️ Avg Unit Price", f"${avg_price:,.0f}")
k4.metric("⭐ Avg Rating",      f"{avg_rating:.2f} / 5")
k5.metric("↩️ Return Rate",    f"{return_rate:.1f}%")
k6.metric("📶 5G Share",       f"{pct_5g:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Products & Customers",
    "Forecast",
    "Data",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    # Revenue trend | Category revenue
    c1, c2 = st.columns([3, 2])
    with c1:
        st_title("Revenue Trend Over Time")
        trend = fdf.set_index("sale_date").resample("ME")["revenue_usd"].sum().reset_index()
        trend["rev_M"] = trend["revenue_usd"] / 1e6
        fig = px.area(trend, x="sale_date", y="rev_M",
                      labels={"sale_date": "", "rev_M": "Revenue (USD M)"},
                      color_discrete_sequence=[ACCENT])
        fig.update_traces(line_width=2, fillcolor="rgba(91,158,247,0.12)")
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    with c2:
        st_title("Revenue by Category")
        cat_rev = fdf.groupby("category")["revenue_usd"].sum().reset_index().sort_values("revenue_usd")
        fig = px.bar(cat_rev, x="revenue_usd", y="category", orientation="h",
                     labels={"revenue_usd": "Revenue (USD)", "category": ""},
                     color="revenue_usd", color_continuous_scale="Blues")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    # World map | Top 10 countries
    c3, c4 = st.columns([3, 2])
    with c3:
        st_title("Global Sales Volume by Country")
        map_data = fdf["country"].value_counts().reset_index()
        map_data.columns = ["country", "sales_count"]
        fig = px.choropleth(map_data, locations="country", locationmode="country names",
                            color="sales_count", hover_name="country",
                            color_continuous_scale="Blues")
        fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=CHART_BG,
                          height=360, margin=dict(l=0, r=0, t=10, b=0),
                          geo=dict(bgcolor=CHART_BG, showframe=False,
                                   lakecolor=CHART_BG, landcolor="#1a2035",
                                   showcoastlines=True, coastlinecolor="#2a3555"))
        fig.update_coloraxes(colorbar=dict(tickfont=dict(color=FONT_COLOR),
                                           title=dict(font=dict(color=FONT_COLOR))))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st_title("Top 10 Countries by Revenue")
        top_c = fdf.groupby("country")["revenue_usd"].sum().nlargest(10).reset_index().sort_values("revenue_usd")
        fig = px.bar(top_c, x="revenue_usd", y="country", orientation="h",
                     labels={"revenue_usd": "Revenue (USD)", "country": ""},
                     color="revenue_usd", color_continuous_scale="Blues")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_layout(fig, height=360), use_container_width=True)

    # Region & year | Quarterly heatmap
    c5, c6 = st.columns(2)
    with c5:
        st_title("Revenue by Region & Year")
        reg_yr = fdf.groupby(["region", "year"])["revenue_usd"].sum().reset_index()
        fig = px.bar(reg_yr, x="region", y="revenue_usd", color="year",
                     labels={"revenue_usd": "Revenue (USD)", "region": ""},
                     color_discrete_sequence=PALETTE, barmode="group")
        fig.update_xaxes(tickangle=20)
        st.plotly_chart(chart_layout(fig, height=320), use_container_width=True)

    with c6:
        st_title("Quarterly Revenue Heatmap")
        q_pivot = fdf.groupby(["year", "quarter"])["revenue_usd"].sum().reset_index() \
                     .pivot(index="quarter", columns="year", values="revenue_usd").fillna(0)
        fig = px.imshow(q_pivot / 1e6, text_auto=".1f",
                        labels=dict(color="Rev (USD M)"),
                        color_continuous_scale="Blues", aspect="auto")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_layout(fig, height=320), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — PRODUCTS & CUSTOMERS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    # Top products | Price vs Revenue | Rating
    c1, c2, c3 = st.columns(3)
    with c1:
        st_title("Top 10 Products by Revenue")
        top_prod = fdf.groupby("product_name")["revenue_usd"].sum().nlargest(10).reset_index().sort_values("revenue_usd")
        fig = px.bar(top_prod, x="revenue_usd", y="product_name", orientation="h",
                     labels={"revenue_usd": "Revenue (USD)", "product_name": ""},
                     color="revenue_usd", color_continuous_scale="Blues")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_layout(fig, height=320), use_container_width=True)

    with c2:
        st_title("Unit Price vs Revenue")
        sample = fdf.sample(min(2000, len(fdf)), random_state=42)
        fig = px.scatter(sample, x="unit_price_usd", y="revenue_usd", color="category",
                         opacity=0.55, labels={"unit_price_usd": "Unit Price (USD)", "revenue_usd": "Revenue (USD)"},
                         color_discrete_sequence=PALETTE)
        fig.update_traces(marker=dict(size=4))
        fig.update_layout(legend=dict(font=dict(size=9)))
        st.plotly_chart(chart_layout(fig, height=320), use_container_width=True)

    with c3:
        st_title("Customer Rating Distribution")
        fig = px.histogram(fdf, x="customer_rating", nbins=30, color_discrete_sequence=[ACCENT])
        fig.update_traces(opacity=0.85)
        fig.update_layout(bargap=0.05)
        st.plotly_chart(chart_layout(fig, height=320), use_container_width=True)

    # Sales channel | Segment | Payment
    c4, c5, c6 = st.columns(3)
    with c4:
        st_title("Revenue by Sales Channel")
        fig = px.pie(fdf.groupby("sales_channel")["revenue_usd"].sum().reset_index(),
                     names="sales_channel", values="revenue_usd",
                     color_discrete_sequence=PALETTE, hole=0.45)
        fig.update_traces(textposition="outside", textfont_size=10)
        st.plotly_chart(chart_layout(fig, height=300), use_container_width=True)

    with c5:
        st_title("Revenue by Customer Segment")
        fig = px.pie(fdf.groupby("customer_segment")["revenue_usd"].sum().reset_index(),
                     names="customer_segment", values="revenue_usd",
                     color_discrete_sequence=PALETTE[2:], hole=0.45)
        fig.update_traces(textposition="outside", textfont_size=10)
        st.plotly_chart(chart_layout(fig, height=300), use_container_width=True)

    with c6:
        st_title("Revenue by Payment Method")
        fig = px.pie(fdf.groupby("payment_method")["revenue_usd"].sum().reset_index(),
                     names="payment_method", values="revenue_usd",
                     color_discrete_sequence=PALETTE[4:], hole=0.45)
        fig.update_traces(textposition="outside", textfont_size=10)
        st.plotly_chart(chart_layout(fig, height=300), use_container_width=True)

    # 5G | Age group | Galaxy Z | Return status | OS
    c7, c8, c9 = st.columns(3)
    with c7:
        st_title("5G Adoption by Year")
        g5 = fdf.groupby(["year", "is_5g"])["units_sold"].sum().reset_index()
        fig = px.bar(g5, x="year", y="units_sold", color="is_5g",
                     labels={"units_sold": "Units Sold", "year": "", "is_5g": "5G"},
                     color_discrete_map={"Yes": ACCENT, "No": "#2a3555"}, barmode="stack")
        st.plotly_chart(chart_layout(fig, height=300), use_container_width=True)

    with c8:
        st_title("Customer Age Group × Category")
        age_cat = fdf.groupby(["customer_age_group", "category"])["units_sold"].sum().reset_index()
        fig = px.bar(age_cat, x="customer_age_group", y="units_sold", color="category",
                     labels={"units_sold": "Units Sold", "customer_age_group": ""},
                     category_orders={"customer_age_group": sorted(fdf["customer_age_group"].unique())},
                     color_discrete_sequence=PALETTE)
        fig.update_layout(legend=dict(font=dict(size=9)))
        st.plotly_chart(chart_layout(fig, height=300), use_container_width=True)

    with c9:
        st_title("Discount % vs Avg Revenue")
        disc = fdf.groupby("discount_pct")["revenue_usd"].mean().reset_index()
        fig = px.line(disc, x="discount_pct", y="revenue_usd",
                      labels={"discount_pct": "Discount (%)", "revenue_usd": "Avg Revenue (USD)"},
                      color_discrete_sequence=[ACCENT], markers=True)
        st.plotly_chart(chart_layout(fig, height=300), use_container_width=True)

    c10, c11, c12 = st.columns(3)
    with c10:
        st_title("Galaxy Z — Units by Model & Year")
        df_z = fdf[fdf["category"] == "Galaxy Z"]
        if not df_z.empty:
            z_data = df_z.groupby(["product_name", "year"])["units_sold"].sum().reset_index()
            fig = px.bar(z_data, x="year", y="units_sold", color="product_name",
                         labels={"units_sold": "Units Sold", "year": ""},
                         color_discrete_sequence=PALETTE, barmode="group")
            fig.update_layout(legend=dict(font=dict(size=8)))
        else:
            fig = go.Figure()
            fig.add_annotation(text="No Galaxy Z data in selection",
                               xref="paper", yref="paper", x=0.5, y=0.5,
                               showarrow=False, font=dict(color=FONT_COLOR))
        st.plotly_chart(chart_layout(fig, height=300), use_container_width=True)

    with c11:
        st_title("Return Status by Category")
        ret = fdf.groupby(["category", "return_status"])["sale_id"].count().reset_index()
        ret.columns = ["category", "return_status", "count"]
        fig = px.bar(ret, x="category", y="count", color="return_status", 
                     labels={"count": "Transactions", "category": ""},
                     color_discrete_map={"Not Returned": ACCENT, "Returned": "#f7aa1b"},
                     barmode="stack")
        fig.update_xaxes(tickangle=45, tickfont=dict(size=10), automargin=True)
        st.plotly_chart(chart_layout(fig, height=300), use_container_width=True)

    with c12:
        st_title("Previous Device OS of Buyers")
        os_counts = fdf["previous_device_os"].value_counts().reset_index()
        os_counts.columns = ["os", "count"]
        os_counts = os_counts[os_counts["os"] != "Unknown"]
        fig = px.bar(os_counts, x="count", y="os", orientation="h",
                     labels={"count": "Count", "os": ""},
                     color="count", color_continuous_scale="Blues")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_layout(fig, height=300), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — FORECAST
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div style='padding:4px 0 16px 0'>
      <span style='font-family:Syne;font-size:1.15rem;font-weight:700;color:#c8d0e8'>
        Prophet Time-Series Forecast
      </span>
      <span style='font-size:0.78rem;color:#4a5a7a;margin-left:12px'>
        Trained on 2021–2024 · Predicting 2025–2026 · 95% confidence interval
      </span>
    </div>
    """, unsafe_allow_html=True)

    try:
        from prophet import Prophet

        with st.spinner("Training forecast models..."):
            monthly = (fdf.set_index("sale_date").resample("ME")["revenue_usd"]
                          .sum().reset_index().rename(columns={"sale_date": "ds", "revenue_usd": "y"}))
            monthly2 = (fdf.set_index("sale_date").resample("ME")["units_sold"]
                           .sum().reset_index().rename(columns={"sale_date": "ds", "units_sold": "y"}))

            m1 = Prophet(yearly_seasonality=True, weekly_seasonality=False,
                         daily_seasonality=False, interval_width=0.95)
            m1.fit(monthly)
            forecast1 = m1.predict(m1.make_future_dataframe(periods=24, freq="ME"))

            m2 = Prophet(yearly_seasonality=True, weekly_seasonality=False,
                         daily_seasonality=False, interval_width=0.95)
            m2.fit(monthly2)
            forecast2 = m2.predict(m2.make_future_dataframe(periods=24, freq="ME"))

        def forecast_chart(actual_df, forecast_df, ylabel):
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=pd.concat([forecast_df["ds"], forecast_df["ds"][::-1]]),
                y=pd.concat([forecast_df["yhat_upper"], forecast_df["yhat_lower"][::-1]]),
                fill="toself", fillcolor="rgba(247,123,91,0.15)",
                line=dict(color="rgba(0,0,0,0)"), name="95% CI", hoverinfo="skip"
            ))
            fig.add_trace(go.Scatter(
                x=forecast_df["ds"], y=forecast_df["yhat"], mode="lines",
                line=dict(color="#f77b5b", width=2, dash="dash"), name="Forecast"
            ))
            fig.add_trace(go.Scatter(
                x=actual_df["ds"], y=actual_df["y"], mode="lines",
                line=dict(color=ACCENT, width=2), name="Actual"
            ))
            fig.add_vline(x=str(actual_df["ds"].iloc[-1]),
                          line_width=1, line_dash="dot", line_color="gray")
            fig.update_layout(yaxis_title=ylabel,
                              legend=dict(orientation="h", y=1.08, font=dict(size=10)))
            return chart_layout(fig, height=380)

        fc1, fc2 = st.columns(2)
        with fc1:
            st_title("Revenue Forecast (USD)")
            st.plotly_chart(forecast_chart(monthly, forecast1, "Revenue (USD)"),
                            use_container_width=True)
        with fc2:
            st_title("Units Sold Forecast")
            st.plotly_chart(forecast_chart(monthly2, forecast2, "Units Sold"),
                            use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st_title("Predicted Yearly Totals")

        forecast1["year"] = forecast1["ds"].dt.year
        forecast2["year"] = forecast2["ds"].dt.year
        rev_pred   = forecast1[forecast1["year"].isin([2025, 2026])].groupby("year")["yhat"].sum()
        units_pred = forecast2[forecast2["year"].isin([2025, 2026])].groupby("year")["yhat"].sum()

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("💰 Revenue 2025", f"${rev_pred.get(2025, 0)/1e6:.1f}M")
        s2.metric("💰 Revenue 2026", f"${rev_pred.get(2026, 0)/1e6:.1f}M")
        s3.metric("📦 Units 2025",   f"{units_pred.get(2025, 0):,.0f}")
        s4.metric("📦 Units 2026",   f"{units_pred.get(2026, 0):,.0f}")

    except ImportError:
        st.warning("⚠️ Prophet not installed. Run `pip install prophet` to enable forecasting.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — DATA
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("""
    <div style='padding:4px 0 16px 0'>
      <span style='font-family:Syne;font-size:1.15rem;font-weight:700;color:#c8d0e8'>
        Raw Filtered Data
      </span>
      <span style='font-size:0.78rem;color:#4a5a7a;margin-left:12px'>
        Showing all records matching current sidebar filters
      </span>
    </div>
    """, unsafe_allow_html=True)

    cols_to_show = ["sale_date", "country", "region", "category", "product_name",
                    "units_sold", "unit_price_usd", "discount_pct", "revenue_usd",
                    "sales_channel", "customer_segment", "customer_rating", "return_status", "is_5g"]
    st.dataframe(
        fdf[cols_to_show].sort_values("sale_date", ascending=False).reset_index(drop=True),
        use_container_width=True, height=520
    )
    st.markdown(f"<p style='color:#4a5a7a;font-size:0.75rem'>{len(fdf):,} records · {len(fdf.columns)} columns</p>",
                unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:24px 0 8px 0;color:#2a3555;font-size:0.72rem;'>
Samsung Global Sales · Synthetic Dataset · EDA Dashboard
</div>
""", unsafe_allow_html=True)
