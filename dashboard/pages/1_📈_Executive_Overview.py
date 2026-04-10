"""
Page 1: Executive Overview
Top-level KPIs, traffic trends, and AI traffic share for senior management.
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
    load_ga4_traffic_overview,
    load_ga4_ai_traffic,
    load_ga4_traffic_sources,
    load_gsc_daily_trend,
    load_gsc_top_queries,
    ga4_rows_to_df,
    gsc_rows_to_df,
)
from config import COLORS, BRAND_NAME

st.set_page_config(page_title="Executive Overview", page_icon="📈", layout="wide")
st.markdown(f"# 📈 Executive Overview — {BRAND_NAME}")
st.markdown("Key performance indicators at a glance.")
st.markdown("---")

# Date range selector
col_d1, col_d2, col_d3 = st.columns([1, 1, 2])
with col_d1:
    start_date = st.date_input("Start date", datetime.now() - timedelta(days=28))
with col_d2:
    end_date = st.date_input("End date", datetime.now() - timedelta(days=1))

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

# Load data
with st.spinner("Loading data from GA4 and GSC..."):
    ga4_overview = load_ga4_traffic_overview(start_str, end_str)
    ai_traffic = load_ga4_ai_traffic(start_str, end_str)
    gsc_trend = load_gsc_daily_trend(start_str, end_str)
    gsc_queries = load_gsc_top_queries(start_str, end_str)

# ─── KPI Cards ──────────────────────────────────────────────

ga4_df = ga4_rows_to_df(ga4_overview)
gsc_df = gsc_rows_to_df(gsc_trend)

total_sessions = int(ga4_df["sessions"].sum()) if not ga4_df.empty else 0
total_users = int(ga4_df["totalUsers"].sum()) if not ga4_df.empty else 0
total_pageviews = int(ga4_df["screenPageViews"].sum()) if not ga4_df.empty else 0
avg_bounce = round(ga4_df["bounceRate"].mean() * 100, 1) if not ga4_df.empty else 0

total_clicks = int(gsc_df["clicks"].sum()) if not gsc_df.empty else 0
total_impressions = int(gsc_df["impressions"].sum()) if not gsc_df.empty else 0
avg_ctr = round(gsc_df["ctr"].mean(), 1) if not gsc_df.empty else 0
avg_position = round(gsc_df["position"].mean(), 1) if not gsc_df.empty else 0

ai_sessions = ai_traffic.get("total_ai_sessions", 0)
ai_share = round((ai_sessions / total_sessions * 100), 2) if total_sessions > 0 else 0

st.markdown("### Website Performance")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Sessions", f"{total_sessions:,}")
k2.metric("Total Users", f"{total_users:,}")
k3.metric("Page Views", f"{total_pageviews:,}")
k4.metric("Avg Bounce Rate", f"{avg_bounce}%")
k5.metric("Avg Session Duration", f"{round(ga4_df['averageSessionDuration'].mean(), 0):.0f}s" if not ga4_df.empty else "—")

st.markdown("### Search Performance")
s1, s2, s3, s4 = st.columns(4)
s1.metric("Search Clicks", f"{total_clicks:,}")
s2.metric("Search Impressions", f"{total_impressions:,}")
s3.metric("Avg CTR", f"{avg_ctr}%")
s4.metric("Avg Position", f"{avg_position}")

st.markdown("### AI Traffic")
a1, a2, a3 = st.columns(3)
a1.metric("AI Referral Sessions", f"{ai_sessions:,}", help="Traffic from ChatGPT, Perplexity, Claude, Gemini, etc.")
a2.metric("AI Traffic Share", f"{ai_share}%", help="Percentage of total sessions from AI sources")
a3.metric("AI Referral Users", f"{ai_traffic.get('total_ai_users', 0):,}")

st.markdown("---")

# ─── Traffic Trend Chart ────────────────────────────────────

st.markdown("### Daily Traffic Trend")

if not ga4_df.empty and "date" in ga4_df.columns:
    ga4_df["date"] = pd.to_datetime(ga4_df["date"], format="%Y%m%d")
    ga4_df = ga4_df.sort_values("date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ga4_df["date"], y=ga4_df["sessions"],
        mode="lines+markers",
        name="Sessions",
        line=dict(color=COLORS["info"], width=2),
        marker=dict(size=4),
    ))
    fig.add_trace(go.Scatter(
        x=ga4_df["date"], y=ga4_df["totalUsers"],
        mode="lines+markers",
        name="Users",
        line=dict(color=COLORS["success"], width=2),
        marker=dict(size=4),
    ))
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", y=-0.15),
        xaxis_title="",
        yaxis_title="Count",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No traffic data available for the selected date range.")

# ─── Search Clicks Trend ───────────────────────────────────

st.markdown("### Daily Search Clicks")

if not gsc_df.empty and "date" in gsc_df.columns:
    gsc_df["date"] = pd.to_datetime(gsc_df["date"])
    gsc_df = gsc_df.sort_values("date")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=gsc_df["date"], y=gsc_df["clicks"],
        name="Clicks",
        marker_color=COLORS["accent"],
    ))
    fig2.add_trace(go.Scatter(
        x=gsc_df["date"], y=gsc_df["ctr"],
        mode="lines+markers",
        name="CTR %",
        yaxis="y2",
        line=dict(color=COLORS["highlight"], width=2),
    ))
    fig2.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", y=-0.15),
        yaxis=dict(title="Clicks"),
        yaxis2=dict(title="CTR %", overlaying="y", side="right"),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ─── AI Traffic Sources Breakdown ───────────────────────────

st.markdown("### AI Traffic Sources")

ai_sources = ai_traffic.get("ai_referral_sources", [])
if ai_sources:
    ai_df = ga4_rows_to_df({"rows": ai_sources})
    if not ai_df.empty and "sessionSource" in ai_df.columns:
        ai_df = ai_df.sort_values("sessions", ascending=True)
        fig3 = px.bar(
            ai_df, x="sessions", y="sessionSource",
            orientation="h",
            color_discrete_sequence=[COLORS["ai_purple"]],
            labels={"sessionSource": "AI Source", "sessions": "Sessions"},
        )
        fig3.update_layout(
            height=max(200, len(ai_df) * 40),
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No AI referral traffic detected in this period. This will grow as AEO efforts take effect.")

# ─── Top Queries Preview ────────────────────────────────────

st.markdown("### Top Search Queries")
queries_df = gsc_rows_to_df(gsc_queries)
if not queries_df.empty:
    st.dataframe(
        queries_df.head(10).style.format({
            "clicks": "{:,.0f}",
            "impressions": "{:,.0f}",
            "ctr": "{:.1f}%",
            "position": "{:.1f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")
st.caption(f"Data range: {start_str} to {end_str} · Sources: Google Analytics 4, Google Search Console")
