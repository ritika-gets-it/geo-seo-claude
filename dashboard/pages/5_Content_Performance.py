"""
Page 5: Content Performance (GA4 Pages)
Top pages by sessions with bounce rate and duration. Flags problem pages.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import load_ga4_top_pages, ga4_rows_to_df, format_duration
from config import COLORS, WEEKS, KEY_GA4_PAGES

st.set_page_config(page_title="Content Performance", page_icon="📄", layout="wide")
st.markdown("# 📄 Content Performance (GA4)")
st.markdown("Top pages by sessions with engagement metrics. Problem pages flagged.")
st.markdown("---")

week_labels = [w["label"] for w in WEEKS]
selected_week = st.selectbox("Select week", week_labels, index=len(week_labels) - 1)
week_info = WEEKS[week_labels.index(selected_week)]

with st.spinner("Loading page data..."):
    pages_data = load_ga4_top_pages(week_info["start"], week_info["end"], limit=30)

pages_df = ga4_rows_to_df(pages_data)

if pages_df.empty:
    st.info("No page data available for this week.")
    st.stop()

# Clean up
if "pagePath" in pages_df.columns:
    pages_df["page"] = pages_df["pagePath"]
elif "pageTitle" in pages_df.columns:
    pages_df["page"] = pages_df.get("pagePath", pages_df["pageTitle"])

pages_df["is_key_page"] = pages_df["page"].isin(KEY_GA4_PAGES)

# ─── Top Pages Table ──────────────────────────────────────

st.markdown(f"### Top Pages — {selected_week}")

display_cols = []
rename_map = {}

if "page" in pages_df.columns:
    display_cols.append("page")
    rename_map["page"] = "Page"
if "sessions" in pages_df.columns:
    display_cols.append("sessions")
    rename_map["sessions"] = "Sessions"
if "screenPageViews" in pages_df.columns:
    display_cols.append("screenPageViews")
    rename_map["screenPageViews"] = "Page Views"
if "bounceRate" in pages_df.columns:
    display_cols.append("bounceRate")
    rename_map["bounceRate"] = "Bounce Rate"
if "averageSessionDuration" in pages_df.columns:
    display_cols.append("averageSessionDuration")
    rename_map["averageSessionDuration"] = "Avg Duration"

display = pages_df[display_cols].rename(columns=rename_map)

if "Avg Duration" in display.columns:
    display["Avg Duration"] = display["Avg Duration"].apply(lambda x: format_duration(x) if pd.notna(x) else "—")

st.dataframe(display, use_container_width=True, hide_index=True)

# ─── Top Pages Chart ──────────────────────────────────────

st.markdown("### Top Pages by Sessions")

if "page" in pages_df.columns and "sessions" in pages_df.columns:
    chart_df = pages_df.nlargest(15, "sessions")
    fig = px.bar(chart_df.sort_values("sessions", ascending=True),
                 x="sessions", y="page", orientation="h",
                 color_discrete_sequence=[COLORS["info"]])
    fig.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0),
                      yaxis_title="", xaxis_title="Sessions")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─── Problem Pages ────────────────────────────────────────

st.markdown("### Problem Pages (High Bounce)")
st.markdown("Pages with >90% bounce rate — potential UX, redirect, or content issues.")

if "bounceRate" in pages_df.columns:
    problem_pages = pages_df[pages_df["bounceRate"] > 0.90].copy()
    if not problem_pages.empty:
        problem_pages["bounce_pct"] = (problem_pages["bounceRate"] * 100).round(1)
        problem_display = problem_pages[["page", "sessions", "bounce_pct"]].rename(columns={
            "page": "Page", "sessions": "Sessions", "bounce_pct": "Bounce Rate %",
        }).sort_values("Bounce Rate %", ascending=False)

        def highlight_bounce(val):
            if isinstance(val, (int, float)) and val > 95:
                return "background-color: #f8d7da; color: #721c24"
            elif isinstance(val, (int, float)) and val > 90:
                return "background-color: #fff3cd"
            return ""

        st.dataframe(problem_display.style.applymap(highlight_bounce, subset=["Bounce Rate %"]),
                     use_container_width=True, hide_index=True)

        st.warning(f"**{len(problem_pages)} pages** have >90% bounce rate. "
                   "Check for: broken redirects, thin content, slow load times, or mismatched search intent.")
    else:
        st.success("No pages with >90% bounce rate detected.")

st.markdown("---")

# ─── Key Pages Tracking ──────────────────────────────────

st.markdown("### Key Pages Performance")
st.markdown("Tracking specific strategic pages.")

key_pages = pages_df[pages_df["is_key_page"]].copy()
if not key_pages.empty:
    key_display = key_pages[display_cols].rename(columns=rename_map)
    if "Avg Duration" in key_display.columns:
        key_display["Avg Duration"] = pages_df.loc[key_pages.index, "averageSessionDuration"].apply(
            lambda x: format_duration(x) if pd.notna(x) else "—"
        )
    st.dataframe(key_display, use_container_width=True, hide_index=True)
else:
    st.info("Key pages not found in this week's top pages. They may have too few sessions to appear.")

st.markdown("---")
st.caption(f"Data: Google Analytics 4 | Week: {selected_week}")
