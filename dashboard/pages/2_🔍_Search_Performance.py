"""
Page 2: Search Performance (GSC)
Queries, top pages, CTR analysis, device/country breakdowns.
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
    load_gsc_top_queries,
    load_gsc_top_pages,
    load_gsc_daily_trend,
    load_gsc_devices,
    load_gsc_countries,
    gsc_rows_to_df,
)
from config import COLORS

st.set_page_config(page_title="Search Performance", page_icon="🔍", layout="wide")
st.markdown("# 🔍 Search Performance")
st.markdown("Google Search Console data — how animocabrands.com performs in search.")
st.markdown("---")

# Date range
col_d1, col_d2, _ = st.columns([1, 1, 2])
with col_d1:
    start_date = st.date_input("Start date", datetime.now() - timedelta(days=28), key="gsc_start")
with col_d2:
    end_date = st.date_input("End date", datetime.now() - timedelta(days=3), key="gsc_end")

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

# Load data
with st.spinner("Loading GSC data..."):
    queries_data = load_gsc_top_queries(start_str, end_str)
    pages_data = load_gsc_top_pages(start_str, end_str)
    trend_data = load_gsc_daily_trend(start_str, end_str)
    device_data = load_gsc_devices(start_str, end_str)
    country_data = load_gsc_countries(start_str, end_str)

# ─── Summary KPIs ───────────────────────────────────────────

trend_df = gsc_rows_to_df(trend_data)
if not trend_df.empty:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Clicks", f"{int(trend_df['clicks'].sum()):,}")
    k2.metric("Total Impressions", f"{int(trend_df['impressions'].sum()):,}")
    k3.metric("Avg CTR", f"{round(trend_df['ctr'].mean(), 1)}%")
    k4.metric("Avg Position", f"{round(trend_df['position'].mean(), 1)}")

st.markdown("---")

# ─── Daily Trend ────────────────────────────────────────────

st.markdown("### Daily Search Performance")

if not trend_df.empty and "date" in trend_df.columns:
    trend_df["date"] = pd.to_datetime(trend_df["date"])
    trend_df = trend_df.sort_values("date")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=trend_df["date"], y=trend_df["clicks"],
        name="Clicks", marker_color=COLORS["info"],
    ))
    fig.add_trace(go.Bar(
        x=trend_df["date"], y=trend_df["impressions"],
        name="Impressions", marker_color=COLORS["accent"],
        opacity=0.4,
    ))
    fig.update_layout(
        height=400, barmode="overlay",
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─── Top Queries ────────────────────────────────────────────

st.markdown("### Top Search Queries")

queries_df = gsc_rows_to_df(queries_data)
if not queries_df.empty:
    # AEO insight: flag question queries
    queries_df["type"] = queries_df["query"].apply(
        lambda q: "Question" if any(q.lower().startswith(w) for w in
            ["how", "what", "why", "when", "where", "who", "which", "is ", "can ", "does ", "best", "top", "vs"]) else "Other"
    )

    tab1, tab2 = st.tabs(["All Queries", "Question Queries (AI Priority)"])

    with tab1:
        st.dataframe(
            queries_df.drop(columns=["type"]).style.format({
                "clicks": "{:,.0f}", "impressions": "{:,.0f}",
                "ctr": "{:.1f}%", "position": "{:.1f}",
            }),
            use_container_width=True, hide_index=True,
        )

    with tab2:
        q_df = queries_df[queries_df["type"] == "Question"]
        if not q_df.empty:
            st.markdown("*These question-format queries are prioritized by AI search engines.*")
            st.dataframe(
                q_df.drop(columns=["type"]).style.format({
                    "clicks": "{:,.0f}", "impressions": "{:,.0f}",
                    "ctr": "{:.1f}%", "position": "{:.1f}",
                }),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No question-format queries found. Consider creating FAQ content to attract AI citations.")

st.markdown("---")

# ─── Top Pages ──────────────────────────────────────────────

st.markdown("### Top Pages by Clicks")

pages_df = gsc_rows_to_df(pages_data)
if not pages_df.empty:
    # Highlight high-impression, low-CTR pages (AI overview candidates)
    pages_df["opportunity"] = (pages_df["impressions"] > pages_df["impressions"].median()) & (pages_df["ctr"] < pages_df["ctr"].median())

    st.dataframe(
        pages_df.drop(columns=["opportunity"]).style.format({
            "clicks": "{:,.0f}", "impressions": "{:,.0f}",
            "ctr": "{:.1f}%", "position": "{:.1f}",
        }),
        use_container_width=True, hide_index=True,
    )

    # AEO opportunities
    opps = pages_df[pages_df["opportunity"]]
    if not opps.empty:
        st.markdown("#### AEO Opportunities")
        st.markdown("*These pages have high impressions but low CTR — users may be getting answers from AI overviews instead of clicking through. Optimize these for AI citations.*")
        st.dataframe(
            opps.drop(columns=["opportunity"]).style.format({
                "clicks": "{:,.0f}", "impressions": "{:,.0f}",
                "ctr": "{:.1f}%", "position": "{:.1f}",
            }),
            use_container_width=True, hide_index=True,
        )

st.markdown("---")

# ─── Device & Country ──────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Device Breakdown")
    device_df = gsc_rows_to_df(device_data)
    if not device_df.empty:
        fig_d = px.pie(
            device_df, values="clicks", names="device",
            color_discrete_sequence=[COLORS["info"], COLORS["success"], COLORS["warning"]],
        )
        fig_d.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_d, use_container_width=True)

with col2:
    st.markdown("### Top Countries")
    country_df = gsc_rows_to_df(country_data)
    if not country_df.empty:
        fig_c = px.bar(
            country_df.head(10), x="clicks", y="country",
            orientation="h",
            color_discrete_sequence=[COLORS["accent"]],
        )
        fig_c.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_c, use_container_width=True)

st.markdown("---")
st.caption(f"Data range: {start_str} to {end_str} · Source: Google Search Console")
