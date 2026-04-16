"""
Page 4: AI & AEO Tracking
AI referrer breakdown, AI share trend, AEO scorecard, Perplexity scoring.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_weekly_ga4_summary, load_weekly_ai_breakdown,
    ga4_rows_to_df,
)
from config import COLORS, OKR_TARGETS

st.set_page_config(page_title="AI & AEO", page_icon="🤖", layout="wide")
st.markdown("# 🤖 AI & AEO Tracking")
st.markdown("AI referral traffic, AEO scorecard, and brand voice monitoring.")
st.markdown("---")

with st.spinner("Loading AI data..."):
    ga4_weekly = load_weekly_ga4_summary()
    ai_breakdown = load_weekly_ai_breakdown()

if ga4_weekly.empty:
    st.error("No data available.")
    st.stop()

latest = ga4_weekly.iloc[-1]

# ─── KPIs ──────────────────────────────────────────────────

k1, k2, k3, k4 = st.columns(4)
k1.metric("AI Sessions (Latest)", f"{int(latest['ai_sessions']):,}")
k2.metric("AI Share", f"{latest['ai_share']}%", help=f"Target: {OKR_TARGETS['ai_traffic_share_target']}%")
k3.metric("AI Users", f"{int(latest['ai_users']):,}")
k4.metric("Total Sessions", f"{int(latest['sessions']):,}")

st.markdown("---")

# ─── AI Share Trend ───────────────────────────────────────

st.markdown("### AI Traffic Share Trend")

fig = go.Figure()
fig.add_trace(go.Bar(x=ga4_weekly["week"], y=ga4_weekly["ai_sessions"],
                     name="AI Sessions", marker_color=COLORS["ai_purple"]))
fig.add_trace(go.Scatter(x=ga4_weekly["week"], y=ga4_weekly["ai_share"],
                         name="AI %", yaxis="y2", mode="lines+markers",
                         line=dict(color=COLORS["highlight"], width=2)))
fig.add_hline(y=OKR_TARGETS["ai_traffic_share_target"], line_dash="dash",
              line_color="green", yref="y2",
              annotation_text=f"Target: {OKR_TARGETS['ai_traffic_share_target']}%")
fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0),
                  legend=dict(orientation="h", y=-0.15),
                  yaxis=dict(title="AI Sessions"),
                  yaxis2=dict(title="AI %", overlaying="y", side="right"))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─── Platform Breakdown ──────────────────────────────────

st.markdown("### AI Referrer Breakdown")

if not ai_breakdown.empty:
    ai_cols = [c for c in ai_breakdown.columns if c != "week" and ai_breakdown[c].sum() > 0]
    if ai_cols:
        fig2 = go.Figure()
        colors = COLORS["ai_gradient"]
        for i, col in enumerate(ai_cols):
            fig2.add_trace(go.Bar(x=ai_breakdown["week"], y=ai_breakdown[col],
                                  name=col, marker_color=colors[i % len(colors)]))
        fig2.update_layout(barmode="stack", height=400, margin=dict(l=0, r=0, t=30, b=0),
                           legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### Sessions by Platform")
        display = ai_breakdown[["week"] + ai_cols].rename(columns={"week": "Week"})
        display["Total"] = display[ai_cols].sum(axis=1).astype(int)
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.info("**Note:** ChatGPT appears as both `chatgpt.com / referral` and "
                "`chatgpt.com / (not set)` — both are counted.")
    else:
        st.info("No AI referral sessions detected yet.")

st.markdown("---")

# ─── AEO Scorecard ────────────────────────────────────────

st.markdown("### AEO Scorecard (Monthly)")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### AI Brand Voice Score")
    st.markdown("*Avg of 6 queries on Perplexity (0-10)*")
    voice = st.number_input("Score", 0.0, 10.0, 0.0, 0.5, key="voice")
    if voice > 0:
        st.progress(voice / 10)
        color = "green" if voice >= 7 else "orange" if voice >= 4 else "red"
        st.markdown(f"**{voice}/10** {'(on target)' if voice >= 7 else '(below target of 7)'}")

with col2:
    st.markdown("#### Ecosystem Understanding")
    st.markdown("*6 pillars in AI responses*")
    pillars = st.number_input("Pillars", 0, 6, 0, 1, key="pillars")
    if pillars > 0:
        st.progress(pillars / 6)
        st.markdown(f"**{pillars}/6** pillars recognized")

with col3:
    st.markdown("#### AI Traffic Share")
    st.metric("Current", f"{latest['ai_share']}%")
    st.progress(min(latest["ai_share"] / OKR_TARGETS["ai_traffic_share_target"], 1.0))
    st.caption(f"Target: {OKR_TARGETS['ai_traffic_share_target']}%")

st.markdown("---")

# ─── Perplexity Scoring ──────────────────────────────────

st.markdown("### Perplexity Brand Query Scoring")
st.markdown("*Search each query on Perplexity and score the response 0-10.*")

queries = [
    "What is Animoca Brands?",
    "What does Animoca Brands do?",
    "Who are the founders of Animoca Brands?",
    "What is Animoca Brands' portfolio?",
    "Is Animoca Brands publicly traded?",
    "What is Animoca Minds?",
]

st.dataframe(pd.DataFrame([
    {"Query": q, "Response Snippet": "", "Score (0-10)": 0} for q in queries
]), use_container_width=True, hide_index=True)

st.info("Score criteria: brand accuracy, completeness, tone, prominence in response.")

st.markdown("---")
st.caption("Data: GA4 | Manual: AEO scorecard, Perplexity scoring")
