"""
Page 3: AI Referral Traffic
Tracks traffic from AI search engines with bounce analysis and actionable insights.
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
    load_ga4_top_pages,
    ga4_rows_to_df,
)
from config import COLORS, AI_SOURCE_LABELS

st.set_page_config(page_title="AI Referral Traffic", page_icon="🤖", layout="wide")
st.markdown("# 🤖 AI Referral Traffic")
st.markdown("Are AI platforms sending us traffic? This is the scorecard for our AEO work.")
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
    sources = load_ga4_traffic_sources(start_str, end_str, limit=100)
    pages = load_ga4_top_pages(start_str, end_str, limit=50)

overview_df = ga4_rows_to_df(overview)
sources_df = ga4_rows_to_df(sources)
total_sessions = int(overview_df["sessions"].sum()) if not overview_df.empty else 0
ai_sessions = ai_data.get("total_ai_sessions", 0)
ai_users = ai_data.get("total_ai_users", 0)
ai_share = round((ai_sessions / total_sessions * 100), 2) if total_sessions > 0 else 0

# ─── Plain English Summary ─────────────────────────────────

st.markdown("### The Bottom Line")

if ai_sessions > 0:
    st.markdown(
        f"AI platforms sent **{ai_sessions:,} visitors** to animocabrands.com this period, "
        f"making up **{ai_share}%** of total traffic. "
        f"{'This is above the industry average (<1%) — our AEO work is paying off.' if ai_share > 1 else 'This is in line with industry averages — as AEO efforts mature, expect this to grow.'}"
    )
else:
    st.markdown(
        "**No AI referral traffic detected yet.** This is our starting point — the baseline we measure from. "
        "As schema markup, content optimization, and brand presence work takes hold over the next weeks, "
        "we expect AI platforms to begin sending traffic. This page will track that growth."
    )

st.markdown("---")

# ─── KPIs ──────────────────────────────────────────────────

k1, k2, k3, k4 = st.columns(4)
k1.metric("AI Sessions", f"{ai_sessions:,}", help="Visits from ChatGPT, Perplexity, Claude, Gemini, Copilot")
k2.metric("AI Users", f"{ai_users:,}", help="Unique visitors from AI platforms")
k3.metric("AI Share of Traffic", f"{ai_share}%", help="AI sessions as % of all sessions")
k4.metric("Total Sessions", f"{total_sessions:,}", help="All visits for comparison")

st.markdown("---")

# ─── AI Sources Breakdown ──────────────────────────────────

st.markdown("### Which AI Platforms Send Us Traffic")

ai_sources = ai_data.get("ai_referral_sources", [])

if ai_sources:
    ai_df = ga4_rows_to_df({"rows": ai_sources})

    if not ai_df.empty and "sessionSource" in ai_df.columns:
        # Clean up source names
        ai_df["platform"] = ai_df["sessionSource"].apply(
            lambda s: next((v for k, v in AI_SOURCE_LABELS.items() if k in s.lower()), s)
        )

        # Aggregate
        ai_agg = ai_df.groupby("platform").agg({
            "sessions": "sum",
            "totalUsers": "sum",
            "screenPageViews": "sum",
            "bounceRate": "mean",
        }).reset_index().sort_values("sessions", ascending=False)

        top_platform = ai_agg.iloc[0]["platform"]
        top_sessions = int(ai_agg.iloc[0]["sessions"])

        st.markdown(
            f"**Insight:** **{top_platform}** is our top AI traffic source with {top_sessions:,} sessions. "
            f"This tells us {top_platform} is citing or linking to our content in its answers."
        )

        col1, col2 = st.columns([1, 1])

        with col1:
            fig = px.bar(
                ai_agg.sort_values("sessions", ascending=True),
                x="sessions", y="platform",
                orientation="h",
                color="sessions",
                color_continuous_scale=["#6c5ce7", "#0984e3", "#00b894"],
                labels={"platform": "AI Platform", "sessions": "Sessions"},
            )
            fig.update_layout(
                height=max(250, len(ai_agg) * 55),
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False, coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.pie(
                ai_agg, values="sessions", names="platform",
                color_discrete_sequence=COLORS["ai_gradient"],
            )
            fig2.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig2, use_container_width=True)

        # Detailed table
        st.dataframe(
            ai_agg.rename(columns={
                "platform": "AI Platform",
                "sessions": "Sessions",
                "totalUsers": "Users",
                "screenPageViews": "Page Views",
                "bounceRate": "Bounce Rate",
            }).style.format({
                "Sessions": "{:,.0f}", "Users": "{:,.0f}",
                "Page Views": "{:,.0f}", "Bounce Rate": "{:.1%}",
            }),
            use_container_width=True, hide_index=True,
        )

        # ─── Bounce Analysis (Issue 5) ─────────────────────

        st.markdown("---")
        st.markdown("### Why Are AI Visitors Bouncing?")

        avg_ai_bounce = ai_agg["bounceRate"].mean()
        avg_overall_bounce = overview_df["bounceRate"].mean() if not overview_df.empty else 0

        if avg_ai_bounce > 0:
            st.markdown(
                f"AI referral bounce rate: **{avg_ai_bounce:.0%}** vs overall site: **{avg_overall_bounce:.0%}**"
            )

            if avg_ai_bounce > avg_overall_bounce:
                st.warning(
                    f"**AI visitors bounce more than average.** This is common and here's why:\n\n"
                    f"1. **AI already gave them the answer** — The AI engine summarized our content, "
                    f"so when users click through they've already read the key points and leave quickly\n"
                    f"2. **Content mismatch** — The page they land on doesn't match what the AI told them to expect\n"
                    f"3. **No clear next step** — The landing page doesn't offer a compelling reason to explore further\n\n"
                    f"**How to fix this:**\n"
                    f"- Add **related content links** and clear CTAs on pages that get AI traffic\n"
                    f"- Include **exclusive content** (tools, calculators, detailed reports) that AI can't summarize\n"
                    f"- Ensure **page load speed** is fast — AI visitors have very low patience\n"
                    f"- Add **interactive elements** (videos, charts, demos) that provide value beyond text"
                )
            elif avg_ai_bounce < avg_overall_bounce:
                st.success(
                    f"**AI visitors bounce less than average** — this is a great sign. "
                    f"It means AI is sending us *qualified* traffic: people who are genuinely interested "
                    f"in our content and explore further after arriving."
                )
            else:
                st.info("AI visitor bounce rate is similar to overall — no unusual patterns.")

            # Per-platform bounce analysis
            if len(ai_agg) > 1:
                high_bounce = ai_agg[ai_agg["bounceRate"] > 0.7]
                low_bounce = ai_agg[ai_agg["bounceRate"] <= 0.5]

                if not high_bounce.empty:
                    platforms = ", ".join(high_bounce["platform"].tolist())
                    st.markdown(f"**High bounce platforms ({'>'}70%):** {platforms} — these visitors may need better landing page experiences.")
                if not low_bounce.empty:
                    platforms = ", ".join(low_bounce["platform"].tolist())
                    st.markdown(f"**Low bounce platforms ({'<'}50%):** {platforms} — these send the most engaged visitors.")

        # ─── Pages per session analysis ────────────────────

        avg_ai_pages = ai_agg["screenPageViews"].sum() / ai_agg["sessions"].sum() if ai_agg["sessions"].sum() > 0 else 0
        overall_pages = overview_df["screenPageViews"].sum() / overview_df["sessions"].sum() if not overview_df.empty and overview_df["sessions"].sum() > 0 else 0

        if avg_ai_pages > 0:
            st.markdown(
                f"\n**Pages per session:** AI visitors view **{avg_ai_pages:.1f} pages** vs "
                f"overall average of **{overall_pages:.1f} pages**. "
                f"{'AI visitors explore less — consider improving internal linking on AI landing pages.' if avg_ai_pages < overall_pages else 'AI visitors are highly engaged, viewing more pages than average.'}"
            )

else:
    st.info("No AI referral traffic detected yet. See recommendations below.")

st.markdown("---")

# ─── AI vs Other Channels ─────────────────────────────────

st.markdown("### How AI Compares to Other Traffic Channels")

if not sources_df.empty and "sessionSource" in sources_df.columns:
    # Build channel summary
    channels = {"AI Referrals": ai_sessions}

    if "sessionMedium" in sources_df.columns:
        organic = sources_df[sources_df["sessionMedium"].str.lower() == "organic"]["sessions"].sum()
        social = sources_df[sources_df["sessionMedium"].str.lower().isin(["social", "referral"])]["sessions"].sum()
    else:
        organic = sources_df[sources_df["sessionSource"].str.lower() == "google"]["sessions"].sum()
        social = 0

    direct = sources_df[sources_df["sessionSource"].str.lower() == "(direct)"]["sessions"].sum()

    channels["Organic Search"] = int(organic)
    channels["Direct"] = int(direct)
    channels["Social/Referral"] = int(social)
    channels["Other"] = max(0, total_sessions - ai_sessions - int(organic) - int(direct) - int(social))

    channel_df = pd.DataFrame([
        {"Channel": k, "Sessions": v, "Share": f"{round(v/total_sessions*100, 1)}%" if total_sessions > 0 else "0%"}
        for k, v in channels.items()
    ]).sort_values("Sessions", ascending=False)

    col1, col2 = st.columns([1, 1])

    with col1:
        fig3 = px.bar(
            channel_df, x="Channel", y="Sessions",
            color="Channel",
            color_discrete_map={
                "AI Referrals": COLORS["ai_purple"],
                "Organic Search": COLORS["success"],
                "Direct": COLORS["info"],
                "Social/Referral": COLORS["warning"],
                "Other": "#dfe6e9",
            },
        )
        fig3.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown("**Channel Breakdown**")
        st.dataframe(channel_df, use_container_width=True, hide_index=True)

        if ai_sessions > 0:
            st.markdown(
                f"AI traffic is currently **{ai_share}%** of total. "
                f"Industry data shows AI-referred traffic growing **+527% YoY**. "
                f"Even a small percentage now represents significant future growth potential."
            )

st.markdown("---")

# ─── What To Do Next ──────────────────────────────────────

st.markdown("### Recommended Actions")

if ai_sessions > 0:
    st.success("**AI traffic is flowing. Here's how to grow it:**")
    actions = [
        "**Identify winning content** — Check which pages attract AI referrals and create more content in that format",
        "**Reduce AI bounce rate** — Add unique value (tools, data, visuals) that AI summaries can't replace",
        "**Monitor weekly** — Track AI traffic share growth as a key AEO KPI",
        "**Expand citation signals** — Strengthen brand presence on YouTube, Reddit, Wikipedia",
        "**Optimize for more AI platforms** — If traffic is only from one platform, target others with structured data",
    ]
else:
    st.info("**Building toward AI traffic. Priority actions:**")
    actions = [
        "**Allow AI crawlers** — Ensure robots.txt permits GPTBot, ClaudeBot, PerplexityBot",
        "**Create llms.txt** — Guide AI crawlers to your most important content",
        "**Add structured data** — JSON-LD schema markup on all key pages (Organization, Article, FAQ)",
        "**Build citation-ready content** — Concise, factual paragraphs (134-167 words) with statistics and named sources",
        "**Grow brand mentions** — Get discussed on YouTube (0.737 correlation), Reddit, and Wikipedia",
        "**Create FAQ content** — Question-answer format that matches how people use AI search",
        "**Check back in 2-4 weeks** — AEO is a medium-term play; results build over time",
    ]

for action in actions:
    st.markdown(f"- {action}")

st.markdown("---")
st.caption(f"Data range: {start_str} to {end_str} · Source: Google Analytics 4 · AI sources tracked: ChatGPT, Perplexity, Claude, Gemini, Copilot, Phind, Kagi, You.com")
