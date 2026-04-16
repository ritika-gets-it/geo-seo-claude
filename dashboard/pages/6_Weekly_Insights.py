"""
Page 6: Weekly Insights
Structured commentary panel with headline, observations, and recommendations.
"""

import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_weekly_ga4_summary, load_weekly_gsc_summary,
    load_weekly_ai_breakdown, format_duration, format_wow,
)
from config import WEEKS

st.set_page_config(page_title="Weekly Insights", page_icon="💡", layout="wide")
st.markdown("# 💡 Weekly Insights")
st.markdown("Structured weekly summary with auto-generated metrics and space for team commentary.")
st.markdown("---")

with st.spinner("Loading data..."):
    ga4_weekly = load_weekly_ga4_summary()
    gsc_weekly = load_weekly_gsc_summary()
    ai_breakdown = load_weekly_ai_breakdown()

if ga4_weekly.empty:
    st.error("No weekly data available.")
    st.stop()

week_labels = [w["label"] for w in WEEKS]
selected_week = st.selectbox("Select week", week_labels, index=len(week_labels) - 1)
week_idx = week_labels.index(selected_week)

current = ga4_weekly.iloc[week_idx] if week_idx < len(ga4_weekly) else None
prev = ga4_weekly.iloc[week_idx - 1] if week_idx > 0 and week_idx - 1 < len(ga4_weekly) else None

if current is None:
    st.info("No data for this week.")
    st.stop()

# ─── Auto-Generated Summary ───────────────────────────────

st.markdown(f"## Week of {selected_week}")

# Key Metrics
st.markdown("### Key Metrics")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Sessions", f"{int(current['sessions']):,}",
          delta=format_wow(current.get("sessions_wow")) if pd.notna(current.get("sessions_wow")) else None)
k2.metric("Users", f"{int(current['users']):,}",
          delta=format_wow(current.get("users_wow")) if pd.notna(current.get("users_wow")) else None)

gsc_row = gsc_weekly.iloc[week_idx] if not gsc_weekly.empty and week_idx < len(gsc_weekly) else None
if gsc_row is not None:
    k3.metric("GSC Clicks", f"{int(gsc_row['clicks']):,}",
              delta=format_wow(gsc_row.get("clicks_wow")) if pd.notna(gsc_row.get("clicks_wow")) else None)
    k4.metric("GSC Impressions", f"{int(gsc_row['impressions']):,}")

k5.metric("AI Sessions", f"{int(current['ai_sessions']):,}",
          delta=format_wow(current.get("ai_sessions_wow")) if pd.notna(current.get("ai_sessions_wow")) else None)

st.markdown("---")

# ─── Auto-Generated Observations ──────────────────────────

st.markdown("### Auto-Generated Observations")

observations = []

# Session trend
if pd.notna(current.get("sessions_wow")):
    wow = current["sessions_wow"]
    if wow > 10:
        observations.append(f"Sessions up {wow:.1f}% WoW — significant growth this week.")
    elif wow < -10:
        observations.append(f"Sessions down {abs(wow):.1f}% WoW — notable decline. Investigate cause.")
    else:
        observations.append(f"Sessions relatively stable ({wow:+.1f}% WoW).")

# Bounce rate
if current["bounce_rate"] > 70:
    observations.append(f"Bounce rate at {current['bounce_rate']}% — above healthy range. Check for campaign traffic or bot activity.")
elif current["bounce_rate"] < 60:
    observations.append(f"Bounce rate at {current['bounce_rate']}% — good engagement.")

# AI traffic
if current["ai_sessions"] > 0:
    observations.append(f"AI referral traffic: {int(current['ai_sessions']):,} sessions ({current['ai_share']}% of total).")
else:
    observations.append("No AI referral traffic detected this week.")

# GSC
if gsc_row is not None:
    if pd.notna(gsc_row.get("clicks_wow")) and gsc_row["clicks_wow"] < -20:
        observations.append(f"GSC clicks dropped {abs(gsc_row['clicks_wow']):.1f}% — search visibility declining.")
    if gsc_row["avg_position"] < 5:
        observations.append(f"Average search position is strong at {gsc_row['avg_position']} (top 5).")

# AI breakdown
if not ai_breakdown.empty and week_idx < len(ai_breakdown):
    ai_week = ai_breakdown.iloc[week_idx]
    ai_cols = [c for c in ai_breakdown.columns if c != "week" and ai_week.get(c, 0) > 0]
    if ai_cols:
        top_ai = max(ai_cols, key=lambda c: ai_week[c])
        observations.append(f"Top AI source: {top_ai} ({int(ai_week[top_ai])} sessions).")

for i, obs in enumerate(observations, 1):
    st.markdown(f"{i}. {obs}")

st.markdown("---")

# ─── Team Commentary (Manual) ─────────────────────────────

st.markdown("### Team Commentary")
st.markdown("*Add your observations and recommendations below:*")

headline = st.text_input("Headline (one-line summary of the week)",
                          placeholder="e.g., 'Steady organic growth; AI traffic emerging from ChatGPT'",
                          key=f"headline_{selected_week}")

observations_manual = st.text_area("Additional Observations",
                                    placeholder="Add numbered observations not captured above...",
                                    height=150, key=f"obs_{selected_week}")

team_question = st.text_input("Key Question for Team",
                               placeholder="e.g., 'Should we increase content cadence on newsroom?'",
                               key=f"question_{selected_week}")

recommendations = st.text_area("Recommendations",
                                placeholder="1. ...\n2. ...\n3. ...",
                                height=100, key=f"recs_{selected_week}")

st.info("Commentary is session-based and not saved between refreshes. "
        "For persistent storage, export insights to a shared document.")

st.markdown("---")

# ─── Week History ─────────────────────────────────────────

st.markdown("### All Weeks Summary")

summary = ga4_weekly[["week", "sessions", "users", "bounce_rate", "ai_sessions", "ai_share"]].copy()
summary = summary.rename(columns={
    "week": "Week", "sessions": "Sessions", "users": "Users",
    "bounce_rate": "Bounce %", "ai_sessions": "AI Sessions", "ai_share": "AI %",
})
st.dataframe(summary, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Auto-generated insights from GA4 and GSC data. Team commentary is manual input.")
