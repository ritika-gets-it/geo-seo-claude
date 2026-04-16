"""
Page 3: Search Performance (GSC)
Weekly GSC data: queries, pages, CTR, position trends.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_weekly_gsc_summary, load_gsc_top_queries, load_gsc_top_pages,
    gsc_rows_to_df,
)
from config import COLORS, WEEKS, TRACKED_BRANDED_QUERIES, KEY_GSC_PAGES

st.set_page_config(page_title="Search Performance", page_icon="🔍", layout="wide")
st.markdown("# 🔍 Search Performance (GSC)")
st.markdown("Google Search Console — clicks, impressions, CTR, position trends.")
st.markdown("---")

with st.spinner("Loading GSC data..."):
    gsc_weekly = load_weekly_gsc_summary()

# ─── Weekly Trend ─────────────────────────────────────────

st.markdown("### Weekly Search Performance")

if not gsc_weekly.empty:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=gsc_weekly["week"], y=gsc_weekly["clicks"],
                         name="Clicks", marker_color=COLORS["info"]))
    fig.add_trace(go.Scatter(x=gsc_weekly["week"], y=gsc_weekly["impressions"],
                             name="Impressions", yaxis="y2",
                             mode="lines+markers", line=dict(color=COLORS["accent"], dash="dot")))
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0),
                      legend=dict(orientation="h", y=-0.15),
                      yaxis=dict(title="Clicks"), yaxis2=dict(title="Impressions", overlaying="y", side="right"))
    st.plotly_chart(fig, use_container_width=True)

    # CTR and Position trend
    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.line(gsc_weekly, x="week", y="ctr", markers=True,
                       labels={"ctr": "CTR %"}, color_discrete_sequence=[COLORS["success"]])
        fig2.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), title="CTR Trend")
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        fig3 = px.line(gsc_weekly, x="week", y="avg_position", markers=True,
                       labels={"avg_position": "Avg Position"}, color_discrete_sequence=[COLORS["highlight"]])
        fig3.update_yaxes(autorange="reversed")
        fig3.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), title="Avg Position (lower = better)")
        st.plotly_chart(fig3, use_container_width=True)

    # Weekly table
    st.markdown("#### Weekly Summary")
    st.dataframe(gsc_weekly[["week", "clicks", "impressions", "ctr", "avg_position"]].rename(columns={
        "week": "Week", "clicks": "Clicks", "impressions": "Impressions",
        "ctr": "CTR %", "avg_position": "Avg Pos",
    }), use_container_width=True, hide_index=True)

st.markdown("---")

# ─── Top Queries (Week Selector) ──────────────────────────

st.markdown("### Top Queries by Week")

week_labels = [w["label"] for w in WEEKS]
selected_week = st.selectbox("Select week", week_labels, index=len(week_labels) - 1, key="q_week")
week_info = WEEKS[week_labels.index(selected_week)]

with st.spinner("Loading queries..."):
    queries_data = load_gsc_top_queries(week_info["start"], week_info["end"], limit=50)

queries_df = gsc_rows_to_df(queries_data)
if not queries_df.empty:
    # Flag branded queries
    queries_df["branded"] = queries_df["query"].str.lower().apply(
        lambda q: any(bq in q for bq in TRACKED_BRANDED_QUERIES)
    )

    tab1, tab2, tab3 = st.tabs(["All Queries", "Branded Queries", "Non-Branded"])

    with tab1:
        st.dataframe(queries_df.style.format({
            "clicks": "{:,.0f}", "impressions": "{:,.0f}", "ctr": "{:.1f}%", "position": "{:.1f}",
        }), use_container_width=True, hide_index=True)

    with tab2:
        branded = queries_df[queries_df["branded"]]
        if not branded.empty:
            st.dataframe(branded.drop(columns=["branded"]).style.format({
                "clicks": "{:,.0f}", "impressions": "{:,.0f}", "ctr": "{:.1f}%", "position": "{:.1f}",
            }), use_container_width=True, hide_index=True)
        else:
            st.info("No branded queries found this week.")

    with tab3:
        non_branded = queries_df[~queries_df["branded"]]
        if not non_branded.empty:
            st.dataframe(non_branded.drop(columns=["branded"]).style.format({
                "clicks": "{:,.0f}", "impressions": "{:,.0f}", "ctr": "{:.1f}%", "position": "{:.1f}",
            }), use_container_width=True, hide_index=True)

st.markdown("---")

# ─── Top Pages (Week Selector) ────────────────────────────

st.markdown("### Top Pages by Week")

selected_week_p = st.selectbox("Select week", week_labels, index=len(week_labels) - 1, key="p_week")
week_info_p = WEEKS[week_labels.index(selected_week_p)]

with st.spinner("Loading pages..."):
    pages_data = load_gsc_top_pages(week_info_p["start"], week_info_p["end"], limit=25)

pages_df = gsc_rows_to_df(pages_data)
if not pages_df.empty:
    pages_df["page_short"] = pages_df["page"].str.replace("https://www.animocabrands.com", "").str.replace("https://animocabrands.com", "")
    pages_df["category"] = pages_df["page_short"].map(KEY_GSC_PAGES).fillna("—")

    st.dataframe(pages_df[["page_short", "category", "clicks", "impressions", "ctr", "position"]].rename(columns={
        "page_short": "Page", "category": "Category",
        "clicks": "Clicks", "impressions": "Impressions", "ctr": "CTR %", "position": "Position",
    }).style.format({
        "Clicks": "{:,.0f}", "Impressions": "{:,.0f}", "CTR %": "{:.1f}%", "Position": "{:.1f}",
    }), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Data: Google Search Console")
