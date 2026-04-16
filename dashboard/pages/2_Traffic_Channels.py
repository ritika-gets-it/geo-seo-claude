"""
Page 2: Traffic & Channels
Weekly/daily trends, channel breakdown, device split, geography.
Email-heavy week detection and flagging.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_weekly_ga4_summary, load_weekly_channel_breakdown,
    load_weekly_device_breakdown, load_weekly_geo_breakdown,
    load_ga4_traffic_overview, load_ga4_traffic_sources,
    ga4_rows_to_df,
)
from config import COLORS, CHANNEL_COLORS, KEY_EVENTS, DEFAULT_START_DATE, DEFAULT_END_DATE

st.set_page_config(page_title="Traffic & Channels", page_icon="📈", layout="wide")
st.markdown("# 📈 Traffic & Channels")
st.markdown("Traffic trends, channel mix, devices, and geography.")
st.markdown("---")

granularity = st.radio("View", ["Daily", "Weekly"], horizontal=True, key="traffic_gran")
exclude_email = st.checkbox("Exclude email-heavy weeks from trend", value=False,
                            help="Flags weeks where Email channel > 5% of sessions")

with st.spinner("Loading data..."):
    ga4_weekly = load_weekly_ga4_summary()
    channels = load_weekly_channel_breakdown()
    devices = load_weekly_device_breakdown()
    geo = load_weekly_geo_breakdown()

# ─── Email Detection ──────────────────────────────────────

email_weeks = []
if not channels.empty and "Email" in channels.columns:
    total_per_week = channels.drop(columns=["week"]).sum(axis=1)
    email_pct = (channels["Email"] / total_per_week * 100).round(1)
    email_weeks = channels[email_pct > 5]["week"].tolist()

    if email_weeks:
        st.warning(f"**Email-heavy weeks detected:** {', '.join(email_weeks)} — "
                   f"these had >5% email traffic which inflates sessions and bounce rate.")

# Filter if requested
plot_weekly = ga4_weekly.copy()
plot_channels = channels.copy()
if exclude_email and email_weeks:
    plot_weekly = plot_weekly[~plot_weekly["week"].isin(email_weeks)]
    plot_channels = plot_channels[~plot_channels["week"].isin(email_weeks)]

# ─── Traffic Trend ────────────────────────────────────────

if granularity == "Daily":
    st.markdown("### Daily Sessions (Full Period)")
    daily = load_ga4_traffic_overview(DEFAULT_START_DATE, DEFAULT_END_DATE)
    daily_df = ga4_rows_to_df(daily)
    if not daily_df.empty and "date" in daily_df.columns:
        daily_df["date"] = pd.to_datetime(daily_df["date"], format="%Y%m%d")
        daily_df = daily_df.sort_values("date")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["sessions"],
                                 mode="lines+markers", name="Sessions",
                                 line=dict(color=COLORS["info"], width=1.5), marker=dict(size=3),
                                 fill="tozeroy", fillcolor="rgba(9,132,227,0.08)"))
        for event in KEY_EVENTS:
            fig.add_vline(x=event["date"], line_dash="dot", line_color="grey", opacity=0.5)
            fig.add_annotation(x=event["date"], y=daily_df["sessions"].max() * 0.95,
                               text=event["event"][:25], showarrow=False,
                               font=dict(size=8), textangle=-45)
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown("### Weekly Sessions")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=plot_weekly["week"], y=plot_weekly["sessions"],
                         name="Sessions", marker_color=COLORS["info"]))
    for event in KEY_EVENTS:
        for _, row in plot_weekly.iterrows():
            if row["start"] <= event["date"] <= row["end"]:
                fig.add_annotation(x=row["week"], y=row["sessions"],
                                   text=event["event"][:30], showarrow=True,
                                   arrowhead=2, font=dict(size=9))
                break
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─── Channel Breakdown ────────────────────────────────────

st.markdown("### Channel Breakdown")

if not plot_channels.empty:
    ch_cols = [c for c in plot_channels.columns if c != "week"]
    fig2 = go.Figure()
    for ch in ch_cols:
        color = CHANNEL_COLORS.get(ch, "#95a5a6")
        fig2.add_trace(go.Bar(x=plot_channels["week"], y=plot_channels[ch],
                              name=ch, marker_color=color))
    fig2.update_layout(barmode="stack", height=450, margin=dict(l=0, r=0, t=30, b=0),
                       legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig2, use_container_width=True)

    # Share table
    with st.expander("Channel detail table"):
        share = plot_channels.copy()
        total = share[ch_cols].sum(axis=1)
        for col in ch_cols:
            share[f"{col} %"] = (share[col] / total * 100).round(1)
        st.dataframe(share, use_container_width=True, hide_index=True)

    # Direct traffic flag
    if "Direct" in plot_channels.columns:
        latest_total = plot_channels[ch_cols].iloc[-1].sum()
        latest_direct_pct = round(plot_channels.iloc[-1].get("Direct", 0) / latest_total * 100, 1) if latest_total > 0 else 0
        if latest_direct_pct > 50:
            st.warning(f"**Direct traffic is {latest_direct_pct}% of total.** "
                       "High direct with high bounce may indicate bot activity.")

st.markdown("---")

# ─── Device & Geography ──────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Devices (Latest Week)")
    if not devices.empty:
        dev_cols = [c for c in devices.columns if c != "week"]
        latest_dev = devices.iloc[-1]
        dev_data = pd.DataFrame({"Device": dev_cols, "Sessions": [int(latest_dev[c]) for c in dev_cols]})
        dev_data["Share %"] = (dev_data["Sessions"] / dev_data["Sessions"].sum() * 100).round(1)
        fig_d = px.pie(dev_data, values="Sessions", names="Device",
                       color_discrete_sequence=[COLORS["info"], COLORS["success"], COLORS["warning"]])
        fig_d.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_d, use_container_width=True)
        st.dataframe(dev_data, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### Top Countries (Latest Week)")
    if not geo.empty:
        geo_cols = [c for c in geo.columns if c != "week"]
        latest_geo = geo.iloc[-1]
        geo_data = pd.DataFrame({"Country": geo_cols, "Sessions": [int(latest_geo[c]) for c in geo_cols]})
        geo_data = geo_data[geo_data["Sessions"] > 0].sort_values("Sessions", ascending=False).head(12)
        fig_g = px.bar(geo_data.sort_values("Sessions", ascending=True), x="Sessions", y="Country",
                       orientation="h", color_discrete_sequence=[COLORS["accent"]])
        fig_g.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_g, use_container_width=True)

# ─── Source / Medium Detail ───────────────────────────────

st.markdown("---")
st.markdown("### Traffic Source / Medium Detail (Full Period)")

with st.spinner("Loading sources..."):
    sources = load_ga4_traffic_sources(DEFAULT_START_DATE, DEFAULT_END_DATE, limit=30)

sources_df = ga4_rows_to_df(sources)
if not sources_df.empty:
    display = sources_df.copy()
    if "sessionMedium" in display.columns:
        display["Source / Medium"] = display["sessionSource"] + " / " + display["sessionMedium"]
        cols = ["Source / Medium", "sessions", "totalUsers", "bounceRate", "averageSessionDuration"]
        cols = [c for c in cols if c in display.columns]
        display = display[cols].rename(columns={
            "sessions": "Sessions", "totalUsers": "Users",
            "bounceRate": "Bounce Rate", "averageSessionDuration": "Avg Duration",
        })
        if "Bounce Rate" in display.columns:
            display["Bounce Rate"] = (display["Bounce Rate"] * 100).round(1).astype(str) + "%"
    st.dataframe(display, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Data: Google Analytics 4 | Week: Sun–Sat")
