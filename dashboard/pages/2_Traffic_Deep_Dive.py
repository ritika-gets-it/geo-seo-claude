"""
Page 2: Traffic Deep Dive
Weekly time series, channel breakdown, device and geo analysis.
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
    load_ga4_traffic_overview, ga4_rows_to_df,
)
from config import COLORS, CHANNEL_COLORS, KEY_EVENTS, DEFAULT_START_DATE, DEFAULT_END_DATE

st.set_page_config(page_title="Traffic Deep Dive", page_icon="📈", layout="wide")
st.markdown("# 📈 Traffic Deep Dive")
st.markdown("Weekly traffic trends, channel mix, device split, and geography.")
st.markdown("---")

with st.spinner("Loading weekly data..."):
    ga4_weekly = load_weekly_ga4_summary()
    channels = load_weekly_channel_breakdown()
    devices = load_weekly_device_breakdown()
    geo = load_weekly_geo_breakdown()
    daily_data = load_ga4_traffic_overview(DEFAULT_START_DATE, DEFAULT_END_DATE)

# ─── Weekly Sessions Trend ────────────────────────────────

st.markdown("### Weekly Sessions & Users")

if not ga4_weekly.empty:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ga4_weekly["week"], y=ga4_weekly["sessions"],
                         name="Sessions", marker_color=COLORS["info"]))
    fig.add_trace(go.Scatter(x=ga4_weekly["week"], y=ga4_weekly["users"],
                             name="Users", mode="lines+markers",
                             line=dict(color=COLORS["success"], width=2)))
    # Add event annotations
    for event in KEY_EVENTS:
        for _, row in ga4_weekly.iterrows():
            if row["start"] <= event["date"] <= row["end"]:
                fig.add_annotation(x=row["week"], y=row["sessions"],
                                   text=event["event"][:30], showarrow=True,
                                   arrowhead=2, font=dict(size=9))
                break
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0),
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─── Channel Breakdown ────────────────────────────────────

st.markdown("### Channel Breakdown (Weekly)")

if not channels.empty:
    ch_cols = [c for c in channels.columns if c != "week"]
    fig2 = go.Figure()
    for ch in ch_cols:
        color = CHANNEL_COLORS.get(ch, "#95a5a6")
        fig2.add_trace(go.Bar(x=channels["week"], y=channels[ch], name=ch,
                              marker_color=color))
    fig2.update_layout(barmode="stack", height=450,
                       margin=dict(l=0, r=0, t=30, b=0),
                       legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig2, use_container_width=True)

    # Channel share table
    st.markdown("#### Channel Share Table")
    share_df = channels.copy()
    total = share_df[ch_cols].sum(axis=1)
    for col in ch_cols:
        share_df[f"{col} %"] = (share_df[col] / total * 100).round(1)
    st.dataframe(share_df, use_container_width=True, hide_index=True)

    # Direct traffic quality flag
    if "Direct" in channels.columns:
        latest_direct_pct = round(channels.iloc[-1].get("Direct", 0) / total.iloc[-1] * 100, 1) if total.iloc[-1] > 0 else 0
        if latest_direct_pct > 50:
            st.warning(f"**Direct traffic is {latest_direct_pct}% of total** — monitor for quality. "
                       "High direct traffic with high bounce rates may indicate bot activity.")

st.markdown("---")

# ─── Device Breakdown ─────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Device Breakdown")
    if not devices.empty:
        dev_cols = [c for c in devices.columns if c != "week"]
        latest_devices = devices.iloc[-1]
        dev_data = pd.DataFrame({"Device": dev_cols, "Sessions": [int(latest_devices[c]) for c in dev_cols]})
        dev_data["Share"] = (dev_data["Sessions"] / dev_data["Sessions"].sum() * 100).round(1)
        fig_d = px.pie(dev_data, values="Sessions", names="Device",
                       color_discrete_sequence=[COLORS["info"], COLORS["success"], COLORS["warning"]])
        fig_d.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_d, use_container_width=True)
        st.dataframe(dev_data, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### Top Countries")
    if not geo.empty:
        geo_cols = [c for c in geo.columns if c != "week"]
        latest_geo = geo.iloc[-1]
        geo_data = pd.DataFrame({"Country": geo_cols, "Sessions": [int(latest_geo[c]) for c in geo_cols]})
        geo_data = geo_data.sort_values("Sessions", ascending=False).head(12)
        fig_g = px.bar(geo_data.sort_values("Sessions", ascending=True), x="Sessions", y="Country",
                       orientation="h", color_discrete_sequence=[COLORS["accent"]])
        fig_g.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_g, use_container_width=True)

st.markdown("---")

# ─── Daily Sessions ──────────────────────────────────────

st.markdown("### Daily Sessions (Full Period)")

daily_df = ga4_rows_to_df(daily_data)
if not daily_df.empty and "date" in daily_df.columns:
    daily_df["date"] = pd.to_datetime(daily_df["date"], format="%Y%m%d")
    daily_df = daily_df.sort_values("date")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["sessions"],
                              mode="lines", name="Sessions",
                              line=dict(color=COLORS["info"], width=1.5),
                              fill="tozeroy", fillcolor="rgba(9,132,227,0.1)"))
    # Annotate key events
    for event in KEY_EVENTS:
        fig3.add_vline(x=event["date"], line_dash="dot", line_color="grey", opacity=0.5)
        fig3.add_annotation(x=event["date"], y=daily_df["sessions"].max() * 0.9,
                           text=event["event"][:25], showarrow=False,
                           font=dict(size=8), textangle=-45)
    fig3.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.caption("Data: Google Analytics 4 | Week: Sun–Sat")
