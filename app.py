
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Digital Marketing ROI Visualizer",
    layout="wide"
)

st.title("Digital Marketing Ad Campaign ROI & Engagement Visualizer")
st.write("Upload your campaign data to analyze advertising performance.")

uploaded_file = st.file_uploader(
    "Upload campaign CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    required_columns = [
        "Platform",
        "Campaign Type",
        "Impressions",
        "Clicks",
        "Engagement",
        "Conversions",
        "Ad Spend",
        "Revenue"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    numeric_columns = [
        "Impressions",
        "Clicks",
        "Engagement",
        "Conversions",
        "Ad Spend",
        "Revenue"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    df = df.dropna(subset=numeric_columns)

    def safe_divide(a, b):
        return np.divide(
            a, b,
            out=np.zeros_like(
                np.asarray(a, dtype=float)
            ),
            where=np.asarray(b) != 0
        )

    df["ROI (%)"] = (
        safe_divide(
            df["Revenue"] - df["Ad Spend"],
            df["Ad Spend"]
        ) * 100
    )

    df["CTR (%)"] = (
        safe_divide(
            df["Clicks"],
            df["Impressions"]
        ) * 100
    )

    df["Engagement Rate (%)"] = (
        safe_divide(
            df["Engagement"],
            df["Impressions"]
        ) * 100
    )

    df["Conversion Rate (%)"] = (
        safe_divide(
            df["Conversions"],
            df["Clicks"]
        ) * 100
    )

    df["CPC"] = safe_divide(
        df["Ad Spend"], df["Clicks"]
    )

    df["CPA"] = safe_divide(
        df["Ad Spend"], df["Conversions"]
    )

    df["ROAS"] = safe_divide(
        df["Revenue"], df["Ad Spend"]
    )

    st.sidebar.header("Campaign Filters")

    platforms = st.sidebar.multiselect(
        "Select Platform",
        df["Platform"].unique(),
        default=df["Platform"].unique()
    )

    campaign_types = st.sidebar.multiselect(
        "Select Campaign Type",
        df["Campaign Type"].unique(),
        default=df["Campaign Type"].unique()
    )

    filtered = df[
        df["Platform"].isin(platforms)
        & df["Campaign Type"].isin(campaign_types)
    ]

    if filtered.empty:
        st.warning("No campaigns match the selected filters.")
        st.stop()

    total_spend = filtered["Ad Spend"].sum()
    total_revenue = filtered["Revenue"].sum()

    roi = (
        (total_revenue - total_spend)
        / total_spend * 100
        if total_spend != 0 else 0
    )

    ctr = (
        filtered["Clicks"].sum()
        / filtered["Impressions"].sum() * 100
        if filtered["Impressions"].sum() != 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Ad Spend", f"${total_spend:,.2f}")
    col2.metric("Total Revenue", f"${total_revenue:,.2f}")
    col3.metric("ROI", f"{roi:.2f}%")
    col4.metric("CTR", f"{ctr:.2f}%")

    st.subheader("Advertising Spend vs Revenue")

    platform_data = (
        filtered.groupby("Platform")
        [["Ad Spend", "Revenue"]]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        platform_data,
        x="Platform",
        y=["Ad Spend", "Revenue"],
        barmode="group",
        title="Platform-wise Advertising Performance"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Campaign ROI Comparison")

    roi_data = (
        filtered.groupby("Platform")["ROI (%)"]
        .mean()
        .reset_index()
    )

    fig2 = px.bar(
        roi_data,
        x="Platform",
        y="ROI (%)",
        title="Average ROI by Platform"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Campaign Data")

    st.dataframe(filtered, use_container_width=True)

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Campaign Report",
        csv,
        file_name="campaign_analysis.csv",
        mime="text/csv"
    )

else:
    st.info("Upload a CSV file to begin analysis.")
