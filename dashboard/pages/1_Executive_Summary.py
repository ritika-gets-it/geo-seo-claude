"""
Page 1: Executive Summary
KPI cards with WoW changes, Q2 target gauges, baseline comparison.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_weekly_ga4_summary, load_weekly_gsc_summary,
    format_duration, format_wow,
)
from config import COLORS, OKR_TARGETS, ORGANIC_BASELINE

st.set_page_config(page_title="Executive Summary", page_icon="📊", layout="wide")
st.markdown("# 📊 Executive Summary")
st.markdown("Key metrics at a glance with week-over-week trends and Q2 target progress.")
st.markdown("---")

with st.spinner("Loading weekly data..."):
    ga4_weekly = load_weekly_ga4_summary()
    gsc_weekly = load_weekly_gsc_summary()

if ga4_weekly.empty:
    st.error("No GA4 weekly data available.")
    st.stop()

latest = ga4_weekly.iloc[-1]
prev = ga4_weekly.iloc[-2] if len(ga4_weekly) > 1 else None

latest_gsc = gsc_weekly.iloc[-1] if not gsc_weekly.empty else None
prev_gsc = gsc_weekly.iloc[-2] if not gsc_weekly.empty and len(gsc_weekly) > 1 else None

# ─── KPI Cards ─────────────────────────────────────────────

st.markdown(f"### Current Week: {latest['week']}")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Sessions", f"{int(latest['sessions']):,}",
          delta=f"{latest.get('sessions_wow', 0):.1f}% WoW" if pd.notna(latest.get('sessions_wow')) else None)
k2.metric("Users", f"{int(latest['users']):,}",
          delta=f"{latest.get('users_wow', 0):.1f}% WoW" if pd.notna(latest.get('users_wow')) else None)
k3.metric("Pageviews", f"{int(latest['pageviews']):,}",
          delta=f"{latest.get('pageviews_wow', 0):.1f}% WoW" if pd.notna(latest.get('pageviews_wow')) else None)
k4.metric("Bounce Rate", f"{latest['bounce_rate']}%",
          delta=f"{latest.get('bounce_rate_wow', 0):.1f}% WoW" if pd.notna(latest.get('bounce_rate_wow')) else None,
          delta_color="inverse")
k5.metric("Avg Duration", format_duration(latest['avg_duration']))

st.markdown("---")

s1, s2, s3, s4 = st.columns(4)
if latest_gsc is not None:
    s1.metric("GSC Clicks", f"{int(latest_gsc['clicks']):,}",
              delta=f"{latest_gsc.get('clicks_wow', 0):.1f}% WoW" if pd.notna(latest_gsc.get('clicks_wow')) else None)
    s2.metric("GSC Impressions", f"{int(latest_gsc['impressions']):,}",
              delta=f"{latest_gsc.get('impressions_wow', 0):.1f}% WoW" if pd.notna(latest_gsc.get('impressions_wow')) else None)
    s3.metric("GSC CTR", f"{latest_gsc['ctr']}%",
              delta=f"{latest_gsc.get('ctr_wow', 0):.1f}% WoW" if pd.notna(latest_gsc.get('ctr_wow')) else None)
    s4.metric("GSC Avg Position", f"{latest_gsc['avg_position']}",
              delta=f"{latest_gsc.get('avg_position_wow', 0):.1f}% WoW" if pd.notna(latest_gsc.get('avg_position_wow')) else None,
              delta_color="inverse")

st.markdown("---")

a1, a2, a3 = st.columns(3)
a1.metric("AI Sessions", f"{int(latest['ai_sessions']):,}",
          delta=f"{latest.get('ai_sessions_wow', 0):.1f}% WoW" if pd.notna(latest.get('ai_sessions_wow')) else None)
a2.metric("AI % of Total", f"{latest['ai_share']}%",
          delta=f"{latest.get('ai_share_wow', 0):.1f}% WoW" if pd.notna(latest.get('ai_share_wow')) else None)
a3.metric("AI Users", f"{int(latest['ai_users']):,}")

st.markdown("---")

# ─── Q2 OKR Progress ──────────────────────────────────────

st.markdown("### Q2 OKR Progress")

# Calculate monthly totals for latest month
monthly_sessions = int(ga4_weekly.tail(4)["sessions"].sum())
monthly_bounce = round(ga4_weekly.tail(4)["bounce_rate"].mean(), 1)

col1, col2, col3 = st.columns(3)

with col1:
    target = OKR_TARGETS["sessions_target_q2"]
    progress = round(monthly_sessions / target * 100)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=monthly_sessions,
        delta={"reference": OKR_TARGETS["sessions_baseline_feb"], "relative": True, "valueformat": ".1%"},
        title={"text": "Monthly Sessions"},
        gauge={"axis": {"range": [0, target * 1.2]},
               "bar": {"color": COLORS["info"]},
               "steps": [{"range": [0, OKR_TARGETS["sessions_baseline_feb"]], "color": "#f8d7da"},
                         {"range": [OKR_TARGETS["sessions_baseline_feb"], target], "color": "#fff3cd"},
                         {"range": [target, target * 1.2], "color": "#d4edda"}],
               "threshold": {"line": {"color": "red", "width": 2}, "value": target}},
        number={"valueformat": ","},
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Target: {target:,} (+20% vs Feb) | Current: {monthly_sessions:,}")

with col2:
    target_b = OKR_TARGETS["bounce_target_q2"]
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=monthly_bounce,
        delta={"reference": OKR_TARGETS["bounce_baseline_feb"], "valueformat": ".1f"},
        title={"text": "Monthly Bounce Rate"},
        gauge={"axis": {"range": [40, 80]},
               "bar": {"color": COLORS["success"] if monthly_bounce <= target_b else COLORS["warning"]},
               "steps": [{"range": [40, target_b], "color": "#d4edda"},
                         {"range": [target_b, OKR_TARGETS["bounce_baseline_feb"]], "color": "#fff3cd"},
                         {"range": [OKR_TARGETS["bounce_baseline_feb"], 80], "color": "#f8d7da"}],
               "threshold": {"line": {"color": "green", "width": 2}, "value": target_b}},
        number={"suffix": "%"},
    ))
    fig2.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=0))
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(f"Target: {target_b}% (-10% vs Feb {OKR_TARGETS['bounce_baseline_feb']}%) | Current: {monthly_bounce}%")

with col3:
    ai_target = OKR_TARGETS["ai_traffic_share_target"]
    current_ai = latest["ai_share"]
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=current_ai,
        title={"text": "AI Traffic Share"},
        gauge={"axis": {"range": [0, 5]},
               "bar": {"color": COLORS["ai_purple"]},
               "threshold": {"line": {"color": "green", "width": 2}, "value": ai_target}},
        number={"suffix": "%"},
    ))
    fig3.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=0))
    st.plotly_chart(fig3, use_container_width=True)
    st.caption(f"Target: {ai_target}% | Current: {current_ai}%")

st.markdown("---")

# ─── Weekly Trend Table ───────────────────────────────────

st.markdown("### Weekly Summary Table")

display = ga4_weekly[["week", "sessions", "users", "pageviews", "bounce_rate",
                       "engagement_rate", "avg_duration", "ai_sessions", "ai_share"]].copy()
display["avg_duration"] = display["avg_duration"].apply(format_duration)

if not gsc_weekly.empty:
    display = display.merge(gsc_weekly[["week", "clicks", "impressions", "ctr", "avg_position"]],
                            on="week", how="left")

display = display.rename(columns={
    "week": "Week", "sessions": "Sessions", "users": "Users", "pageviews": "PVs",
    "bounce_rate": "Bounce %", "engagement_rate": "Engage %", "avg_duration": "Avg Dur",
    "ai_sessions": "AI Sessions", "ai_share": "AI %",
    "clicks": "GSC Clicks", "impressions": "GSC Impr", "ctr": "GSC CTR", "avg_position": "GSC Pos",
})

st.dataframe(display, use_container_width=True, hide_index=True)

# ─── Baseline Comparison ─────────────────────────────────

st.markdown("### vs Organic Baseline (Feb 22–28)")

baseline = ORGANIC_BASELINE
b_col1, b_col2, b_col3, b_col4 = st.columns(4)

sess_change = round((int(latest["sessions"]) - baseline["sessions"]) / baseline["sessions"] * 100, 1)
user_change = round((int(latest["users"]) - baseline["users"]) / baseline["users"] * 100, 1)
bounce_change = round(latest["bounce_rate"] - baseline["bounce_rate"], 1)

b_col1.metric("Sessions", f"{int(latest['sessions']):,}",
              delta=f"{sess_change}% vs baseline ({baseline['sessions']:,})")
b_col2.metric("Users", f"{int(latest['users']):,}",
              delta=f"{user_change}% vs baseline ({baseline['users']:,})")
b_col3.metric("Bounce Rate", f"{latest['bounce_rate']}%",
              delta=f"{bounce_change:+.1f}pp vs baseline ({baseline['bounce_rate']}%)",
              delta_color="inverse")
b_col4.metric("Avg Duration", format_duration(latest["avg_duration"]),
              help=f"Baseline: {format_duration(baseline['avg_duration_seconds'])}")

st.markdown("---")
st.caption("Data: Google Analytics 4 + Google Search Console | Week: Sun–Sat | Timezone: HKT")
