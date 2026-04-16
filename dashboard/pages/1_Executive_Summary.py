"""
Page 1: Executive Summary
KPI cards with day-over-day or week-over-week changes.
Date range selector. Q2 OKR gauges.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_weekly_ga4_summary, load_weekly_gsc_summary,
    load_ga4_traffic_overview, load_gsc_daily_trend,
    load_ga4_ai_traffic,
    ga4_rows_to_df, gsc_rows_to_df, format_duration,
)
from config import COLORS, OKR_TARGETS, GA4_START_DATE

st.set_page_config(page_title="Executive Summary", page_icon="📊", layout="wide")
st.markdown("# 📊 Executive Summary")
st.markdown("---")

# ─── Date Range & Granularity ─────────────────────────────

col_g, col_s, col_e, _ = st.columns([1, 1, 1, 1])
with col_g:
    granularity = st.radio("View", ["Daily", "Weekly"], horizontal=True, key="exec_gran")
with col_s:
    start_date = st.date_input("From", datetime(2026, 1, 25), key="exec_start")
with col_e:
    end_date = st.date_input("To", datetime.now() - timedelta(days=1), key="exec_end")

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

st.markdown("---")

# ═══════════════════════════════════════════════════════════
# DAILY VIEW
# ═══════════════════════════════════════════════════════════

if granularity == "Daily":
    with st.spinner("Loading daily data..."):
        daily_ga4 = load_ga4_traffic_overview(start_str, end_str)
        daily_gsc = load_gsc_daily_trend(start_str, end_str)
        ai_data = load_ga4_ai_traffic(start_str, end_str)

    daily_df = ga4_rows_to_df(daily_ga4)
    gsc_df = gsc_rows_to_df(daily_gsc)

    if daily_df.empty:
        st.error("No data for selected date range.")
        st.stop()

    # Parse dates and sort
    if "date" in daily_df.columns:
        daily_df["date"] = pd.to_datetime(daily_df["date"], format="%Y%m%d")
        daily_df = daily_df.sort_values("date")

    # Latest day and previous day
    latest = daily_df.iloc[-1]
    prev = daily_df.iloc[-2] if len(daily_df) > 1 else None

    latest_date = latest["date"].strftime("%b %d, %Y") if "date" in daily_df.columns else "Latest"

    # Day-over-day deltas
    def dod_delta(metric):
        if prev is None:
            return None
        curr_val = latest[metric]
        prev_val = prev[metric]
        if prev_val == 0:
            return None
        return round((curr_val - prev_val) / prev_val * 100, 1)

    # ─── KPI Cards (Daily) ────────────────────────────────

    st.markdown(f"### {latest_date}")

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Sessions", f"{int(latest['sessions']):,}",
              delta=f"{dod_delta('sessions')}% DoD" if dod_delta('sessions') is not None else None)
    k2.metric("Users", f"{int(latest['totalUsers']):,}",
              delta=f"{dod_delta('totalUsers')}% DoD" if dod_delta('totalUsers') is not None else None)
    k3.metric("Page Views", f"{int(latest['screenPageViews']):,}",
              delta=f"{dod_delta('screenPageViews')}% DoD" if dod_delta('screenPageViews') is not None else None)
    k4.metric("Bounce Rate", f"{round(latest['bounceRate'] * 100, 1)}%",
              delta=f"{dod_delta('bounceRate')}% DoD" if dod_delta('bounceRate') is not None else None,
              delta_color="inverse")
    k5.metric("Avg Duration", format_duration(latest.get('averageSessionDuration', 0)))

    # Period totals
    st.markdown("---")
    st.markdown(f"### Period Totals ({start_date.strftime('%b %d')} – {end_date.strftime('%b %d')})")

    total_sessions = int(daily_df["sessions"].sum())
    total_users = int(daily_df["totalUsers"].sum())
    total_pvs = int(daily_df["screenPageViews"].sum())
    avg_bounce = round(daily_df["bounceRate"].mean() * 100, 1)
    avg_duration = round(daily_df["averageSessionDuration"].mean(), 0)
    ai_sessions = ai_data.get("total_ai_sessions", 0)
    ai_share = round(ai_sessions / total_sessions * 100, 2) if total_sessions > 0 else 0

    t1, t2, t3, t4, t5 = st.columns(5)
    t1.metric("Total Sessions", f"{total_sessions:,}")
    t2.metric("Total Users", f"{total_users:,}")
    t3.metric("Total Page Views", f"{total_pvs:,}")
    t4.metric("Avg Bounce Rate", f"{avg_bounce}%")
    t5.metric("Avg Duration", format_duration(avg_duration))

    # GSC totals
    if not gsc_df.empty:
        total_clicks = int(gsc_df["clicks"].sum())
        total_impressions = int(gsc_df["impressions"].sum())
        overall_ctr = round(total_clicks / total_impressions * 100, 1) if total_impressions > 0 else 0
        avg_pos = round(gsc_df["position"].mean(), 1)

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("GSC Clicks", f"{total_clicks:,}")
        s2.metric("GSC Impressions", f"{total_impressions:,}")
        s3.metric("GSC CTR", f"{overall_ctr}%")
        s4.metric("GSC Avg Position", f"{avg_pos}")

    # AI traffic
    a1, a2 = st.columns(2)
    a1.metric("AI Sessions", f"{ai_sessions:,}")
    a2.metric("AI % of Total", f"{ai_share}%")

    st.markdown("---")

    # ─── Daily Trend Chart ────────────────────────────────

    st.markdown("### Daily Trend")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["sessions"],
                             mode="lines+markers", name="Sessions",
                             line=dict(color=COLORS["info"], width=2), marker=dict(size=4),
                             fill="tozeroy", fillcolor="rgba(9,132,227,0.08)"))
    fig.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["totalUsers"],
                             mode="lines+markers", name="Users",
                             line=dict(color=COLORS["success"], width=1.5), marker=dict(size=3)))

    # Average line
    avg_sessions = daily_df["sessions"].mean()
    fig.add_hline(y=avg_sessions, line_dash="dash", line_color="grey",
                  annotation_text=f"Avg: {int(avg_sessions):,}")

    fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0),
                      legend=dict(orientation="h", y=-0.15),
                      xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    # ─── Daily Table ──────────────────────────────────────

    with st.expander("Daily data table"):
        table_df = daily_df[["date", "sessions", "totalUsers", "screenPageViews",
                             "bounceRate", "averageSessionDuration"]].copy()
        table_df["bounceRate"] = (table_df["bounceRate"] * 100).round(1)
        table_df["averageSessionDuration"] = table_df["averageSessionDuration"].apply(format_duration)
        table_df["date"] = table_df["date"].dt.strftime("%b %d")
        # Add DoD change
        table_df["Sessions DoD %"] = table_df["sessions"].pct_change().mul(100).round(1)
        table_df = table_df.rename(columns={
            "date": "Date", "sessions": "Sessions", "totalUsers": "Users",
            "screenPageViews": "PVs", "bounceRate": "Bounce %",
            "averageSessionDuration": "Avg Dur",
        })
        st.dataframe(table_df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════
# WEEKLY VIEW
# ═══════════════════════════════════════════════════════════

else:
    with st.spinner("Loading weekly data..."):
        ga4_weekly = load_weekly_ga4_summary()
        gsc_weekly = load_weekly_gsc_summary()

    if ga4_weekly.empty:
        st.error("No weekly data available.")
        st.stop()

    latest = ga4_weekly.iloc[-1]

    # ─── KPI Cards (Weekly) ───────────────────────────────

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

    st.markdown("---")

    latest_gsc = gsc_weekly.iloc[-1] if not gsc_weekly.empty else None
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

    # ─── Weekly Trend Chart ───────────────────────────────

    st.markdown("### Weekly Trend")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ga4_weekly["week"], y=ga4_weekly["sessions"],
                         name="Sessions", marker_color=COLORS["info"]))
    fig.add_trace(go.Scatter(x=ga4_weekly["week"], y=ga4_weekly["users"],
                             name="Users", mode="lines+markers",
                             line=dict(color=COLORS["success"], width=2)))
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0),
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)

    # ─── Weekly Table ─────────────────────────────────────

    with st.expander("Weekly data table"):
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

# ═══════════════════════════════════════════════════════════
# Q2 OKR Progress (shown in both views)
# ═══════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("### Q2 OKR Progress")

with st.spinner("Loading OKR data..."):
    ga4_w = load_weekly_ga4_summary()

if not ga4_w.empty:
    monthly_sessions = int(ga4_w.tail(4)["sessions"].sum())
    monthly_bounce = round(ga4_w.tail(4)["bounce_rate"].mean(), 1)
    current_ai = ga4_w.iloc[-1]["ai_share"]

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
st.caption("Data: GA4 + GSC | Week: Sun–Sat | Timezone: HKT")
