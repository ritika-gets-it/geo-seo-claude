"""
Page 3: AI Referral Traffic
The AEO-specific page — tracks traffic from ChatGPT, Perplexity, Claude, Gemini, etc.
This is the core page that proves AEO ROI.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_ga4_ai_traffic,
    load_ga4_traffic_overview,
    load_ga4_landing_pages,
    load_ga4_traffic_sources,
    ga4_rows_to_df,
)
from config import COLORS, AI_SOURCE_LABELS

st.set_page_config(page_title="AI Referral Traffic", page_icon="🤖", layout="wide")
st.markdown("# 🤖 AI Referral Traffic")
st.markdown("Track traffic from AI search engines — the key metric for AEO success.")
st.markdown("---")

# Date range
col_d1, col_d2, _ = st.columns([1, 1, 2])
with col_d1:
    start_date = st.date_input("Start date", datetime.now() - timedelta(days=28), key="ai_start")
with col_d2:
    end_date = st.date_input("End date", datetime.now() - timedelta(days=1), key="ai_end")

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

# Load data
with st.spinner("Analyzing AI referral traffic..."):
    ai_data = load_ga4_ai_traffic(start_str, end_str)
    overview = load_ga4_traffic_overview(start_str, end_str)
    sources = load_ga4_traffic_sources(start_str, end_str)
    landing = load_ga4_landing_pages(start_str, end_str)

overview_df = ga4_rows_to_df(overview)
total_sessions = int(overview_df["sessions"].sum()) if not overview_df.empty else 0
ai_sessions = ai_data.get("total_ai_sessions", 0)
ai_users = ai_data.get("total_ai_users", 0)
ai_share = round((ai_sessions / total_sessions * 100), 2) if total_sessions > 0 else 0

# ─── AI KPIs ────────────────────────────────────────────────

st.markdown("### AI Traffic Overview")

k1, k2, k3, k4 = st.columns(4)
k1.metric(
    "AI Sessions",
    f"{ai_sessions:,}",
    help="Total sessions from AI referral sources",
)
k2.metric(
    "AI Users",
    f"{ai_users:,}",
    help="Unique users from AI referral sources",
)
k3.metric(
    "AI Traffic Share",
    f"{ai_share}%",
    help="AI sessions as percentage of total sessions",
)
k4.metric(
    "Total Sessions",
    f"{total_sessions:,}",
    help="All sessions for comparison",
)

st.markdown("---")

# ─── AI Sources Breakdown ──────────────────────────────────

st.markdown("### AI Traffic by Source")

ai_sources = ai_data.get("ai_referral_sources", [])

if ai_sources:
    ai_df = ga4_rows_to_df({"rows": ai_sources})

    if not ai_df.empty and "sessionSource" in ai_df.columns:
        # Clean up source names
        ai_df["source_label"] = ai_df["sessionSource"].apply(
            lambda s: next((v for k, v in AI_SOURCE_LABELS.items() if k in s.lower()), s)
        )

        # Aggregate by label
        ai_agg = ai_df.groupby("source_label").agg({
            "sessions": "sum",
            "totalUsers": "sum",
            "screenPageViews": "sum",
            "bounceRate": "mean",
        }).reset_index().sort_values("sessions", ascending=False)

        col1, col2 = st.columns([1, 1])

        with col1:
            fig = px.bar(
                ai_agg.sort_values("sessions", ascending=True),
                x="sessions", y="source_label",
                orientation="h",
                color="sessions",
                color_continuous_scale=["#6c5ce7", "#0984e3", "#00b894"],
                labels={"source_label": "AI Platform", "sessions": "Sessions"},
            )
            fig.update_layout(
                height=max(250, len(ai_agg) * 50),
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.pie(
                ai_agg, values="sessions", names="source_label",
                color_discrete_sequence=COLORS["ai_gradient"],
            )
            fig2.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig2, use_container_width=True)

        # Detailed table
        st.markdown("#### Detailed AI Source Metrics")
        st.dataframe(
            ai_agg.rename(columns={
                "source_label": "AI Platform",
                "sessions": "Sessions",
                "totalUsers": "Users",
                "screenPageViews": "Page Views",
                "bounceRate": "Bounce Rate",
            }).style.format({
                "Sessions": "{:,.0f}",
                "Users": "{:,.0f}",
                "Page Views": "{:,.0f}",
                "Bounce Rate": "{:.1%}",
            }),
            use_container_width=True, hide_index=True,
        )
else:
    st.warning("""
    **No AI referral traffic detected yet.**

    This is normal if AEO work is just starting. AI referral traffic typically appears as:
    - ChatGPT citations drive traffic from `chatgpt.com`
    - Perplexity answers link to `perplexity.ai`
    - Google AI Overviews appear as organic (harder to separate)

    **What to do:**
    1. Continue optimizing content for AI citability
    2. Build brand mentions on AI-cited platforms (Reddit, YouTube, Wikipedia)
    3. Ensure AI crawlers (GPTBot, ClaudeBot) are not blocked
    4. Check back in 2-4 weeks
    """)

st.markdown("---")

# ─── AI vs Organic Comparison ──────────────────────────────

st.markdown("### AI vs Organic Traffic Quality")

sources_df = ga4_rows_to_df(sources)

if not sources_df.empty and "sessionSource" in sources_df.columns:
    # Categorize sources
    ai_patterns = ["chatgpt", "openai", "perplexity", "claude", "anthropic", "gemini", "bard", "copilot", "bing-chat", "you.com", "phind", "kagi"]

    organic_sessions = sources_df[
        (sources_df["sessionMedium"].str.lower() == "organic") |
        (sources_df["sessionSource"].str.lower() == "google")
    ]["sessions"].sum() if "sessionMedium" in sources_df.columns else 0

    direct_sessions = sources_df[
        sources_df["sessionSource"].str.lower() == "(direct)"
    ]["sessions"].sum() if "sessionSource" in sources_df.columns else 0

    social_sessions = sources_df[
        sources_df["sessionMedium"].str.lower().isin(["social", "referral"])
    ]["sessions"].sum() if "sessionMedium" in sources_df.columns else 0

    comparison_data = pd.DataFrame([
        {"Source Type": "AI Referrals", "Sessions": ai_sessions, "Color": COLORS["ai_purple"]},
        {"Source Type": "Organic Search", "Sessions": int(organic_sessions), "Color": COLORS["success"]},
        {"Source Type": "Direct", "Sessions": int(direct_sessions), "Color": COLORS["info"]},
        {"Source Type": "Social/Referral", "Sessions": int(social_sessions), "Color": COLORS["warning"]},
    ])

    fig3 = px.bar(
        comparison_data, x="Source Type", y="Sessions",
        color="Source Type",
        color_discrete_map={
            "AI Referrals": COLORS["ai_purple"],
            "Organic Search": COLORS["success"],
            "Direct": COLORS["info"],
            "Social/Referral": COLORS["warning"],
        },
    )
    fig3.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
    )
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ─── AEO Recommendations ──────────────────────────────────

st.markdown("### AEO Action Items")

if ai_sessions > 0:
    st.success(f"""
    **AI traffic is flowing!** {ai_sessions:,} sessions from AI sources.
    - Monitor which pages attract the most AI referrals
    - Double down on content formats that AI engines cite
    - Track growth week-over-week to measure AEO ROI
    """)
else:
    st.info("""
    **Getting started with AEO:**
    - Ensure `/robots.txt` allows GPTBot, ClaudeBot, PerplexityBot
    - Create an `/llms.txt` file for AI crawler guidance
    - Add structured data (JSON-LD) to key pages
    - Build brand mentions on Reddit, YouTube, Wikipedia
    - Create "citation-ready" content blocks (concise, factual, self-contained)
    """)

st.markdown("---")
st.caption(f"Data range: {start_str} to {end_str} · Source: Google Analytics 4")
