"""
Page 3: Search & Content
GSC queries/pages + GA4 top pages + bounce flags. Tabs for each view.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_weekly_gsc_summary, load_gsc_top_queries, load_gsc_top_pages,
    load_ga4_top_pages, gsc_rows_to_df, ga4_rows_to_df, format_duration,
)
from config import COLORS, WEEKS, TRACKED_BRANDED_QUERIES, KEY_GSC_PAGES, KEY_GA4_PAGES, DEFAULT_START_DATE, DEFAULT_END_DATE

st.set_page_config(page_title="Search & Content", page_icon="🔍", layout="wide")
st.markdown("# 🔍 Search & Content")
st.markdown("GSC search performance + GA4 page performance in one view.")
st.markdown("---")

granularity = st.radio("View", ["Daily", "Weekly"], horizontal=True, key="search_gran")

with st.spinner("Loading GSC data..."):
    gsc_weekly = load_weekly_gsc_summary()

tab_search, tab_queries, tab_gsc_pages, tab_ga4_pages = st.tabs([
    "Search Trends", "Top Queries", "GSC Top Pages", "GA4 Top Pages"
])

# ─── Tab 1: Search Trends ────────────────────────────────

with tab_search:
    st.markdown("### Search Performance Trend")

    if granularity == "Daily":
        from data_loader import load_gsc_daily_trend
        daily_gsc = load_gsc_daily_trend(DEFAULT_START_DATE, DEFAULT_END_DATE)
        daily_df = gsc_rows_to_df(daily_gsc)
        if not daily_df.empty and "date" in daily_df.columns:
            daily_df["date"] = pd.to_datetime(daily_df["date"])
            daily_df = daily_df.sort_values("date")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=daily_df["date"], y=daily_df["clicks"],
                                 name="Clicks", marker_color=COLORS["info"]))
            fig.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["impressions"],
                                     name="Impressions", yaxis="y2", mode="lines",
                                     line=dict(color=COLORS["accent"], dash="dot")))
            fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0),
                              legend=dict(orientation="h", y=-0.15),
                              yaxis=dict(title="Clicks"),
                              yaxis2=dict(title="Impressions", overlaying="y", side="right"))
            st.plotly_chart(fig, use_container_width=True)
    else:
        if not gsc_weekly.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=gsc_weekly["week"], y=gsc_weekly["clicks"],
                                 name="Clicks", marker_color=COLORS["info"]))
            fig.add_trace(go.Scatter(x=gsc_weekly["week"], y=gsc_weekly["impressions"],
                                     name="Impressions", yaxis="y2", mode="lines+markers",
                                     line=dict(color=COLORS["accent"], dash="dot")))
            fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0),
                              legend=dict(orientation="h", y=-0.15),
                              yaxis=dict(title="Clicks"),
                              yaxis2=dict(title="Impressions", overlaying="y", side="right"))
            st.plotly_chart(fig, use_container_width=True)

            # CTR + Position
            col1, col2 = st.columns(2)
            with col1:
                fig2 = px.line(gsc_weekly, x="week", y="ctr", markers=True,
                               color_discrete_sequence=[COLORS["success"]])
                fig2.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), title="CTR %")
                st.plotly_chart(fig2, use_container_width=True)
            with col2:
                fig3 = px.line(gsc_weekly, x="week", y="avg_position", markers=True,
                               color_discrete_sequence=[COLORS["highlight"]])
                fig3.update_yaxes(autorange="reversed")
                fig3.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), title="Avg Position (lower=better)")
                st.plotly_chart(fig3, use_container_width=True)

            st.dataframe(gsc_weekly[["week", "clicks", "impressions", "ctr", "avg_position"]].rename(columns={
                "week": "Week", "clicks": "Clicks", "impressions": "Impressions",
                "ctr": "CTR %", "avg_position": "Avg Pos",
            }), use_container_width=True, hide_index=True)

# ─── Tab 2: Top Queries ──────────────────────────────────

with tab_queries:
    st.markdown("### Top Search Queries")
    week_labels = [w["label"] for w in WEEKS]
    selected = st.selectbox("Select week", week_labels, index=len(week_labels) - 1, key="q_w")
    week_info = WEEKS[week_labels.index(selected)]

    queries_data = load_gsc_top_queries(week_info["start"], week_info["end"], limit=50)
    queries_df = gsc_rows_to_df(queries_data)

    if not queries_df.empty:
        queries_df["branded"] = queries_df["query"].str.lower().apply(
            lambda q: any(bq in q for bq in TRACKED_BRANDED_QUERIES))

        sub1, sub2, sub3 = st.tabs(["All", "Branded", "Non-Branded"])
        with sub1:
            st.dataframe(queries_df.drop(columns=["branded"]).style.format({
                "clicks": "{:,.0f}", "impressions": "{:,.0f}", "ctr": "{:.1f}%", "position": "{:.1f}",
            }), use_container_width=True, hide_index=True)
        with sub2:
            b = queries_df[queries_df["branded"]]
            st.dataframe(b.drop(columns=["branded"]).style.format({
                "clicks": "{:,.0f}", "impressions": "{:,.0f}", "ctr": "{:.1f}%", "position": "{:.1f}",
            }) if not b.empty else pd.DataFrame(), use_container_width=True, hide_index=True)
        with sub3:
            nb = queries_df[~queries_df["branded"]]
            st.dataframe(nb.drop(columns=["branded"]).style.format({
                "clicks": "{:,.0f}", "impressions": "{:,.0f}", "ctr": "{:.1f}%", "position": "{:.1f}",
            }) if not nb.empty else pd.DataFrame(), use_container_width=True, hide_index=True)

# ─── Tab 3: GSC Top Pages ────────────────────────────────

with tab_gsc_pages:
    st.markdown("### GSC Top Pages")
    selected_p = st.selectbox("Select week", week_labels, index=len(week_labels) - 1, key="p_w")
    week_info_p = WEEKS[week_labels.index(selected_p)]

    pages_data = load_gsc_top_pages(week_info_p["start"], week_info_p["end"], limit=25)
    pages_df = gsc_rows_to_df(pages_data)

    if not pages_df.empty:
        pages_df["short"] = pages_df["page"].str.replace("https://www.animocabrands.com", "").str.replace("https://animocabrands.com", "")
        pages_df["category"] = pages_df["short"].map(KEY_GSC_PAGES).fillna("—")
        st.dataframe(pages_df[["short", "category", "clicks", "impressions", "ctr", "position"]].rename(columns={
            "short": "Page", "category": "Category", "clicks": "Clicks",
            "impressions": "Impressions", "ctr": "CTR %", "position": "Position",
        }).style.format({
            "Clicks": "{:,.0f}", "Impressions": "{:,.0f}", "CTR %": "{:.1f}%", "Position": "{:.1f}",
        }), use_container_width=True, hide_index=True)

# ─── Tab 4: GA4 Top Pages ────────────────────────────────

with tab_ga4_pages:
    st.markdown("### GA4 Top Pages (by Sessions)")
    selected_g = st.selectbox("Select week", week_labels, index=len(week_labels) - 1, key="g_w")
    week_info_g = WEEKS[week_labels.index(selected_g)]

    ga4_pages = load_ga4_top_pages(week_info_g["start"], week_info_g["end"], limit=30)
    ga4_df = ga4_rows_to_df(ga4_pages)

    if not ga4_df.empty:
        if "bounceRate" in ga4_df.columns:
            ga4_df["bounce_pct"] = (ga4_df["bounceRate"] * 100).round(1)
            ga4_df["problem"] = ga4_df["bounceRate"] > 0.90

        if "averageSessionDuration" in ga4_df.columns:
            ga4_df["duration"] = ga4_df["averageSessionDuration"].apply(format_duration)

        display_cols = []
        rename = {}
        for col, label in [("pagePath", "Page"), ("sessions", "Sessions"),
                           ("screenPageViews", "PVs"), ("bounce_pct", "Bounce %"),
                           ("duration", "Avg Duration")]:
            if col in ga4_df.columns:
                display_cols.append(col)
                rename[col] = label

        st.dataframe(ga4_df[display_cols].rename(columns=rename),
                     use_container_width=True, hide_index=True)

        # Problem pages
        if "problem" in ga4_df.columns:
            problems = ga4_df[ga4_df["problem"]]
            if not problems.empty:
                st.markdown("#### Problem Pages (>90% Bounce)")
                st.warning(f"**{len(problems)} pages** have >90% bounce rate — check for UX, redirect, or content issues.")
                st.dataframe(problems[display_cols].rename(columns=rename),
                             use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Data: Google Search Console + Google Analytics 4")
