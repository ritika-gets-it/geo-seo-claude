"""
Page 4: AI & AEO Tracking
AI referrer breakdown by platform, AI share trend, AEO scorecard.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_weekly_ga4_summary, load_weekly_ai_breakdown,
    load_ga4_ai_traffic, ga4_rows_to_df,
)
from config import COLORS, AI_REFERRERS, OKR_TARGETS, WEEKS

st.set_page_config(page_title="AI & AEO Tracking", page_icon="🤖", layout="wide")
st.markdown("# 🤖 AI & AEO Tracking")
st.markdown("AI referral traffic by platform, weekly trends, and AEO scorecard.")
st.markdown("---")

with st.spinner("Loading AI traffic data..."):
    ga4_weekly = load_weekly_ga4_summary()
    ai_breakdown = load_weekly_ai_breakdown()

# ─── AI Traffic Trend ──────────────────────────────────────

st.markdown("### AI Traffic Share Trend")

if not ga4_weekly.empty:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ga4_weekly["week"], y=ga4_weekly["ai_sessions"],
                         name="AI Sessions", marker_color=COLORS["ai_purple"]))
    fig.add_trace(go.Scatter(x=ga4_weekly["week"], y=ga4_weekly["ai_share"],
                             name="AI % of Total", yaxis="y2",
                             mode="lines+markers", line=dict(color=COLORS["highlight"], width=2)))
    fig.add_hline(y=OKR_TARGETS["ai_traffic_share_target"], line_dash="dash",
                  line_color="green", yref="y2",
                  annotation_text=f"Target: {OKR_TARGETS['ai_traffic_share_target']}%")
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0),
                      legend=dict(orientation="h", y=-0.15),
                      yaxis=dict(title="AI Sessions"),
                      yaxis2=dict(title="AI % of Total", overlaying="y", side="right"))
    st.plotly_chart(fig, use_container_width=True)

    latest = ga4_weekly.iloc[-1]
    st.markdown(
        f"**Current AI traffic share: {latest['ai_share']}%** | "
        f"Target: {OKR_TARGETS['ai_traffic_share_target']}% | "
        f"AI sessions this week: {int(latest['ai_sessions']):,}"
    )

st.markdown("---")

# ─── AI Breakdown by Platform ─────────────────────────────

st.markdown("### AI Referrer Breakdown (Weekly)")

if not ai_breakdown.empty:
    ai_cols = [c for c in ai_breakdown.columns if c != "week"]
    ai_cols = [c for c in ai_cols if ai_breakdown[c].sum() > 0]

    if ai_cols:
        fig2 = go.Figure()
        colors = COLORS["ai_gradient"]
        for i, col in enumerate(ai_cols):
            fig2.add_trace(go.Bar(x=ai_breakdown["week"], y=ai_breakdown[col],
                                  name=col, marker_color=colors[i % len(colors)]))
        fig2.update_layout(barmode="stack", height=400,
                           margin=dict(l=0, r=0, t=30, b=0),
                           legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig2, use_container_width=True)

        # Per-platform table
        st.markdown("#### Weekly Sessions by AI Platform")
        display = ai_breakdown[["week"] + ai_cols].rename(columns={"week": "Week"})
        display["Total AI"] = display[ai_cols].sum(axis=1).astype(int)
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.info("**Note:** ChatGPT appears as both `chatgpt.com / referral` and `chatgpt.com / (not set)` — both are counted.")
    else:
        st.info("No AI referral sessions detected in any week yet.")

st.markdown("---")

# ─── AEO Scorecard ─────────────────────────────────────────

st.markdown("### AEO Scorecard")
st.markdown("Monthly scorecard tracking AI optimization effectiveness.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### AI Brand Voice Score")
    st.markdown("*Average score across 6 brand queries tested on Perplexity (0-10 scale)*")
    voice_score = st.number_input("Current score", min_value=0.0, max_value=10.0,
                                   value=0.0, step=0.5, key="voice_score",
                                   help="Enter manually from Perplexity brand query review")
    target_voice = 7.0
    if voice_score > 0:
        color = COLORS["success"] if voice_score >= target_voice else COLORS["warning"]
        st.progress(voice_score / 10)
        st.markdown(f"**{voice_score}/10** (target: {target_voice}/10)")

with col2:
    st.markdown("#### Ecosystem Understanding")
    st.markdown("*How many of Animoca's 6 business pillars appear in AI responses*")
    pillars = st.number_input("Pillars mentioned", min_value=0, max_value=6,
                               value=0, step=1, key="pillars",
                               help="Count from Perplexity/ChatGPT query responses")
    if pillars > 0:
        st.progress(pillars / 6)
        st.markdown(f"**{pillars}/6** pillars recognized")

with col3:
    st.markdown("#### AI Traffic Share")
    current_ai = ga4_weekly.iloc[-1]["ai_share"] if not ga4_weekly.empty else 0
    st.metric("Current", f"{current_ai}%", help="Auto-calculated from GA4")
    st.progress(min(current_ai / OKR_TARGETS["ai_traffic_share_target"], 1.0))
    st.markdown(f"Target: {OKR_TARGETS['ai_traffic_share_target']}%")

st.markdown("---")

# ─── Perplexity Brand Query Scoring ──────────────────────

st.markdown("### Perplexity Brand Query Scoring")
st.markdown("*Manual review: Score AI responses for brand accuracy (0-10)*")

queries_to_score = [
    "What is Animoca Brands?",
    "What does Animoca Brands do?",
    "Who are the founders of Animoca Brands?",
    "What is Animoca Brands' portfolio?",
    "Is Animoca Brands publicly traded?",
    "What is Animoca Minds?",
]

scoring_data = []
for q in queries_to_score:
    scoring_data.append({"Query": q, "Response snippet": "", "Score (0-10)": 0})

st.markdown("*Edit the table below to log your scoring:*")
st.dataframe(pd.DataFrame(scoring_data), use_container_width=True, hide_index=True)

st.info("To score: Search each query on Perplexity, review the response, "
        "rate 0-10 on brand accuracy, completeness, and tone.")

st.markdown("---")
st.caption("Data: Google Analytics 4 | Manual inputs: AEO scorecard, Perplexity scoring")
