"""
Page 1: Executive Summary
KPI cards with WoW changes, Q2 OKR gauges, baseline comparison.
Daily/Weekly/Monthly toggle.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_weekly_ga4_summary, load_weekly_gsc_summary,
    load_ga4_traffic_overview, load_gsc_daily_trend,
    ga4_rows_to_df, gsc_rows_to_df, format_duration,
)
from config import COLORS, OKR_TARGETS, ORGANIC_BASELINE, DEFAULT_START_DATE, DEFAULT_END_DATE

st.set_page_config(page_title="Executive Summary", page_icon="📊", layout="wide")
st.markdown("# 📊 Executive Summary")
st.markdown("KPIs, OKR progress, and baseline comparison.")
st.markdown("---")

# Granularity toggle
granularity = st.radio("View", ["Daily", "Weekly"], horizontal=True, key="exec_gran")

with st.spinner("Loading data..."):
    ga4_weekly = load_weekly_ga4_summary()
    gsc_weekly = load_weekly_gsc_summary()

if ga4_weekly.empty:
    st.error("No data available.")
    st.stop()

latest = ga4_weekly.iloc[-1]
prev = ga4_weekly.iloc[-2] if len(ga4_weekly) > 1 else None

latest_gsc = gsc_weekly.iloc[-1] if not gsc_weekly.empty else None

# ─── KPI Cards ─────────────────────────────────────────────

st.markdown(f"### Latest Week: {latest['week']}")

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

s1, s2, s3, s4 = st.columns(4)
if latest_gsc is not None:
    s1.metric("GSC Clicks", f"{int(latest_gsc['clicks']):,}",
              delta=f"{latest_gsc.get('clicks_wow', 0):.1f}% WoW" if pd.notna(latest_gsc.get('clicks_wow')) else None)
    s2.metric("GSC Impressions", f"{int(latest_gsc['impressions']):,}")
    s3.metric("GSC CTR", f"{latest_gsc['ctr']}%")
    s4.metric("GSC Avg Position", f"{latest_gsc['avg_position']}")

a1, a2 = st.columns(2)
a1.metric("AI Sessions", f"{int(latest['ai_sessions']):,}",
          delta=f"{latest.get('ai_sessions_wow', 0):.1f}% WoW" if pd.notna(latest.get('ai_sessions_wow')) else None)
a2.metric("AI % of Total", f"{latest['ai_share']}%")

st.markdown("---")

# ─── Trend Chart ──────────────────────────────────────────

if granularity == "Daily":
    st.markdown("### Daily Traffic Trend (Full Period)")
    daily = load_ga4_traffic_overview(DEFAULT_START_DATE, DEFAULT_END_DATE)
    daily_df = ga4_rows_to_df(daily)
    if not daily_df.empty and "date" in daily_df.columns:
        daily_df["date"] = pd.to_datetime(daily_df["date"], format="%Y%m%d")
        daily_df = daily_df.sort_values("date")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["sessions"],
                                 mode="lines", name="Sessions",
                                 line=dict(color=COLORS["info"], width=1.5),
                                 fill="tozeroy", fillcolor="rgba(9,132,227,0.1)"))
        fig.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["totalUsers"],
                                 mode="lines", name="Users",
                                 line=dict(color=COLORS["success"], width=1.5)))
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0),
                          legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown("### Weekly Sessions & Users")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ga4_weekly["week"], y=ga4_weekly["sessions"],
                         name="Sessions", marker_color=COLORS["info"]))
    fig.add_trace(go.Scatter(x=ga4_weekly["week"], y=ga4_weekly["users"],
                             name="Users", mode="lines+markers",
                             line=dict(color=COLORS["success"], width=2)))
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0),
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─── Q2 OKR Progress ──────────────────────────────────────

st.markdown("### Q2 OKR Progress")

monthly_sessions = int(ga4_weekly.tail(4)["sessions"].sum())
monthly_bounce = round(ga4_weekly.tail(4)["bounce_rate"].mean(), 1)
current_ai = latest["ai_share"]

col1, col2, col3 = st.columns(3)

with col1:
    target = OKR_TARGETS["sessions_target_q2"]
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=monthly_sessions,
        delta={"reference": OKR_TARGETS["sessions_baseline_feb"], "relative": True, "valueformat": ".1%"},
        title={"text": "Monthly Sessions"},
        gauge={"axis": {"range": [0, target * 1.2]}, "bar": {"color": COLORS["info"]},
               "threshold": {"line": {"color": "red", "width": 2}, "value": target}},
        number={"valueformat": ","},
    ))
    fig1.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=0))
    st.plotly_chart(fig1, use_container_width=True)
    st.caption(f"Target: {target:,} (+20% vs Feb)")

with col2:
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number", value=monthly_bounce,
        title={"text": "Bounce Rate"},
        gauge={"axis": {"range": [40, 80]},
               "bar": {"color": COLORS["success"] if monthly_bounce <= OKR_TARGETS["bounce_target_q2"] else COLORS["warning"]},
               "threshold": {"line": {"color": "green", "width": 2}, "value": OKR_TARGETS["bounce_target_q2"]}},
        number={"suffix": "%"},
    ))
    fig2.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=0))
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(f"Target: {OKR_TARGETS['bounce_target_q2']}% (-10% vs Feb)")

with col3:
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number", value=current_ai,
        title={"text": "AI Traffic Share"},
        gauge={"axis": {"range": [0, 5]}, "bar": {"color": COLORS["ai_purple"]},
               "threshold": {"line": {"color": "green", "width": 2}, "value": OKR_TARGETS["ai_traffic_share_target"]}},
        number={"suffix": "%"},
    ))
    fig3.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=0))
    st.plotly_chart(fig3, use_container_width=True)
    st.caption(f"Target: {OKR_TARGETS['ai_traffic_share_target']}%")

st.markdown("---")

# ─── Baseline Comparison ─────────────────────────────────

st.markdown("### vs Organic Baseline (Feb 22–28)")

baseline = ORGANIC_BASELINE
b1, b2, b3, b4 = st.columns(4)

sess_chg = round((latest["sessions"] - baseline["sessions"]) / baseline["sessions"] * 100, 1)
user_chg = round((latest["users"] - baseline["users"]) / baseline["users"] * 100, 1)
bounce_chg = round(latest["bounce_rate"] - baseline["bounce_rate"], 1)

b1.metric("Sessions", f"{int(latest['sessions']):,}", delta=f"{sess_chg}% vs baseline")
b2.metric("Users", f"{int(latest['users']):,}", delta=f"{user_chg}% vs baseline")
b3.metric("Bounce Rate", f"{latest['bounce_rate']}%",
          delta=f"{bounce_chg:+.1f}pp vs baseline", delta_color="inverse")
b4.metric("Avg Duration", format_duration(latest["avg_duration"]),
          help=f"Baseline: {format_duration(baseline['avg_duration_seconds'])}")

# ─── Weekly Table ─────────────────────────────────────────

st.markdown("---")
st.markdown("### Weekly Summary")

display = ga4_weekly[["week", "sessions", "users", "pageviews", "bounce_rate",
                       "engagement_rate", "avg_duration", "ai_sessions", "ai_share"]].copy()
display["avg_duration"] = display["avg_duration"].apply(format_duration)
if not gsc_weekly.empty:
    display = display.merge(gsc_weekly[["week", "clicks", "impressions", "ctr", "avg_position"]],
                            on="week", how="left")
display = display.rename(columns={
    "week": "Week", "sessions": "Sessions", "users": "Users", "pageviews": "PVs",
    "bounce_rate": "Bounce %", "engagement_rate": "Engage %", "avg_duration": "Avg Dur",
    "ai_sessions": "AI Sess", "ai_share": "AI %",
    "clicks": "Clicks", "impressions": "Impr", "ctr": "CTR %", "avg_position": "Pos",
})
st.dataframe(display, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Data: GA4 + GSC | Week: Sun–Sat | Timezone: HKT")
