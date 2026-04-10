"""
Page 4: Traffic Sources & Landing Pages
All traffic sources, landing pages, geography, and device breakdown.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_ga4_traffic_sources,
    load_ga4_landing_pages,
    load_ga4_top_pages,
    load_ga4_devices,
    load_ga4_geo,
    ga4_rows_to_df,
)
from config import COLORS

st.set_page_config(page_title="Traffic Sources", page_icon="🌐", layout="wide")
st.markdown("# 🌐 Traffic Sources & Landing Pages")
st.markdown("Where visitors come from and where they land.")
st.markdown("---")

# Date range
col_d1, col_d2, _ = st.columns([1, 1, 2])
with col_d1:
    start_date = st.date_input("Start date", datetime.now() - timedelta(days=28), key="ts_start")
with col_d2:
    end_date = st.date_input("End date", datetime.now() - timedelta(days=1), key="ts_end")

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

# Load data
with st.spinner("Loading traffic data..."):
    sources_data = load_ga4_traffic_sources(start_str, end_str)
    landing_data = load_ga4_landing_pages(start_str, end_str)
    pages_data = load_ga4_top_pages(start_str, end_str)
    devices_data = load_ga4_devices(start_str, end_str)
    geo_data = load_ga4_geo(start_str, end_str)

# ─── Traffic Sources ────────────────────────────────────────

st.markdown("### Traffic Sources")

sources_df = ga4_rows_to_df(sources_data)

if not sources_df.empty:
    col1, col2 = st.columns([1, 1])

    with col1:
        top10 = sources_df.head(10).copy()
        top10["source_medium"] = top10["sessionSource"] + " / " + top10.get("sessionMedium", "")
        fig = px.bar(
            top10.sort_values("sessions", ascending=True),
            x="sessions", y="source_medium",
            orientation="h",
            color_discrete_sequence=[COLORS["info"]],
            labels={"source_medium": "Source / Medium", "sessions": "Sessions"},
        )
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.pie(
            sources_df.head(8), values="sessions", names="sessionSource",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig2.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Full Source Table")
    display_df = sources_df.copy()
    if "sessionMedium" in display_df.columns:
        display_df = display_df.rename(columns={
            "sessionSource": "Source",
            "sessionMedium": "Medium",
            "sessions": "Sessions",
            "totalUsers": "Users",
            "bounceRate": "Bounce Rate",
            "averageSessionDuration": "Avg Duration (s)",
        })
    st.dataframe(
        display_df.style.format({
            "Sessions": "{:,.0f}",
            "Users": "{:,.0f}",
            "Bounce Rate": "{:.1%}",
            "Avg Duration (s)": "{:.0f}",
        }) if "Sessions" in display_df.columns else display_df,
        use_container_width=True, hide_index=True,
    )

st.markdown("---")

# ─── Landing Pages ──────────────────────────────────────────

st.markdown("### Top Landing Pages")

landing_df = ga4_rows_to_df(landing_data)

if not landing_df.empty:
    st.dataframe(
        landing_df.rename(columns={
            "landingPagePlusQueryString": "Landing Page",
            "sessions": "Sessions",
            "totalUsers": "Users",
            "bounceRate": "Bounce Rate",
            "averageSessionDuration": "Avg Duration (s)",
            "conversions": "Conversions",
        }).style.format({
            "Sessions": "{:,.0f}",
            "Users": "{:,.0f}",
            "Bounce Rate": "{:.1%}",
            "Avg Duration (s)": "{:.0f}",
            "Conversions": "{:,.0f}",
        }),
        use_container_width=True, hide_index=True,
    )

st.markdown("---")

# ─── Top Pages by Views ────────────────────────────────────

st.markdown("### Top Pages by Page Views")

pages_df = ga4_rows_to_df(pages_data)

if not pages_df.empty:
    top_pages = pages_df.head(15)
    fig3 = px.bar(
        top_pages.sort_values("screenPageViews", ascending=True).tail(15),
        x="screenPageViews", y="pagePath",
        orientation="h",
        color_discrete_sequence=[COLORS["accent"]],
        labels={"pagePath": "Page", "screenPageViews": "Page Views"},
    )
    fig3.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ─── Device & Geography ────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Device Breakdown")
    devices_df = ga4_rows_to_df(devices_data)
    if not devices_df.empty:
        fig_d = px.pie(
            devices_df, values="sessions", names="deviceCategory",
            color_discrete_sequence=[COLORS["info"], COLORS["success"], COLORS["warning"]],
        )
        fig_d.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_d, use_container_width=True)

with col2:
    st.markdown("### Top Countries")
    geo_df = ga4_rows_to_df(geo_data)
    if not geo_df.empty:
        fig_g = px.bar(
            geo_df.head(10).sort_values("sessions", ascending=True),
            x="sessions", y="country",
            orientation="h",
            color_discrete_sequence=[COLORS["success"]],
        )
        fig_g.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_g, use_container_width=True)

st.markdown("---")
st.caption(f"Data range: {start_str} to {end_str} · Source: Google Analytics 4")
