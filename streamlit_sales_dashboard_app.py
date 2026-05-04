import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================
# TITLE
# =========================
st.title("📊 Interactive Sales Dashboard")
st.markdown("Visualisasi data jualan mengikut daerah, tarif dan produk")

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    file_path = "data/Sale By District Tariff.xlsx"

    if not Path(file_path).exists():
        st.error("Excel file tidak dijumpai. Pastikan fail berada dalam folder yang sama.")
        st.stop()

    df = pd.read_excel(file_path)

    # Clean column names
    df.columns = [str(col).strip() for col in df.columns]

    return df


df = load_data()

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🔎 Filters")

# Detect possible columns
possible_region_cols = [
    col for col in df.columns
    if any(keyword in col.lower() for keyword in ["district", "region", "daerah", "zone"])
]

possible_product_cols = [
    col for col in df.columns
    if any(keyword in col.lower() for keyword in ["tariff", "product", "kategori", "type"])
]

possible_sales_cols = [
    col for col in df.columns
    if any(keyword in col.lower() for keyword in ["sale", "revenue", "amount", "jualan"])
]

# Auto-select columns
region_col = possible_region_cols[0] if possible_region_cols else df.columns[0]
product_col = possible_product_cols[0] if possible_product_cols else df.columns[1]
sales_col = possible_sales_cols[0] if possible_sales_cols else df.select_dtypes(include='number').columns[0]

# Filters
regions = st.sidebar.multiselect(
    "Select Region",
    options=sorted(df[region_col].dropna().unique()),
    default=sorted(df[region_col].dropna().unique())
)

products = st.sidebar.multiselect(
    "Select Product/Tariff",
    options=sorted(df[product_col].dropna().unique()),
    default=sorted(df[product_col].dropna().unique())
)

# Filter dataframe
filtered_df = df[
    (df[region_col].isin(regions)) &
    (df[product_col].isin(products))
]

# =========================
# KPI SECTION
# =========================

st.subheader("📌 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

# Total sales
try:
    total_sales = pd.to_numeric(filtered_df[sales_col], errors='coerce').sum()
except:
    total_sales = 0

# Total regions
total_regions = filtered_df[region_col].nunique()

# Total products
total_products = filtered_df[product_col].nunique()

col1.metric("Total Sales", f"RM {total_sales:,.2f}")
col2.metric("Total Regions", total_regions)
col3.metric("Total Products", total_products)

st.divider()

# =========================
# CHARTS
# =========================

chart_col1, chart_col2 = st.columns(2)

# =========================
# SALES BY REGION
# =========================
with chart_col1:
    st.subheader("📍 Sales by Region")

    region_summary = (
        filtered_df
        .groupby(region_col)[sales_col]
        .sum(numeric_only=True)
        .reset_index()
        .sort_values(by=sales_col, ascending=False)
    )

    fig_region = px.bar(
        region_summary,
        x=region_col,
        y=sales_col,
        color=sales_col,
        text_auto=True,
        title="Sales Performance by Region"
    )

    fig_region.update_layout(
        xaxis_title="Region",
        yaxis_title="Sales",
        height=500
    )

    st.plotly_chart(fig_region, use_container_width=True)

# =========================
# SALES BY PRODUCT
# =========================
with chart_col2:
    st.subheader("🛒 Sales by Product/Tariff")

    product_summary = (
        filtered_df
        .groupby(product_col)[sales_col]
        .sum(numeric_only=True)
        .reset_index()
        .sort_values(by=sales_col, ascending=False)
    )

    fig_product = px.pie(
        product_summary,
        names=product_col,
        values=sales_col,
        hole=0.45,
        title="Contribution by Product/Tariff"
    )

    fig_product.update_layout(height=500)

    st.plotly_chart(fig_product, use_container_width=True)

# =========================
# TREND ANALYSIS
# =========================

st.subheader("📈 Sales Trend Analysis")

# Detect date/year/month column
possible_time_cols = [
    col for col in df.columns
    if any(keyword in col.lower() for keyword in ["date", "month", "year", "period"])
]

if possible_time_cols:
    time_col = possible_time_cols[0]

    trend_summary = (
        filtered_df
        .groupby(time_col)[sales_col]
        .sum(numeric_only=True)
        .reset_index()
    )

    fig_trend = px.line(
        trend_summary,
        x=time_col,
        y=sales_col,
        markers=True,
        title="Sales Trend"
    )

    fig_trend.update_layout(
        height=500,
        xaxis_title="Period",
        yaxis_title="Sales"
    )

    st.plotly_chart(fig_trend, use_container_width=True)

else:
    st.info("No date/month/year column detected for trend analysis.")

# =========================
# DATA TABLE
# =========================

st.subheader("📋 Filtered Data")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400
)

# =========================
# DOWNLOAD OPTION
# =========================

csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="⬇ Download Filtered Data",
    data=csv,
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)

# =========================
# FOOTER
# =========================

st.markdown("---")
st.caption("Interactive Sales Dashboard using Streamlit + Plotly")
