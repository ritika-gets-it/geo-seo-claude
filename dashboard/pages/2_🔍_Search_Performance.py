"""
Page 2: Search Performance (GSC)
Queries, top pages, CTR analysis, device/country breakdowns.
With insights and AEO-specific analysis.
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
    load_gsc_top_queries,
    load_gsc_top_pages,
    load_gsc_daily_trend,
    load_gsc_devices,
    load_gsc_countries,
    gsc_rows_to_df,
)
from config import COLORS

st.set_page_config(page_title="Search Performance", page_icon="🔍", layout="wide")
st.markdown("# 🔍 Search Performance")
st.markdown("How animocabrands.com performs in Google Search — and where the AEO opportunities are.")
st.markdown("---")

# Date range
col_d1, col_d2, _ = st.columns([1, 1, 2])
with col_d1:
    start_date = st.date_input("Start date", datetime.now() - timedelta(days=28), key="gsc_start")
with col_d2:
    end_date = st.date_input("End date", datetime.now() - timedelta(days=3), key="gsc_end")

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

# Load data (fetch more queries to find question patterns)
with st.spinner("Loading GSC data..."):
    queries_data = load_gsc_top_queries(start_str, end_str, limit=100)
    pages_data = load_gsc_top_pages(start_str, end_str)
    trend_data = load_gsc_daily_trend(start_str, end_str)
    device_data = load_gsc_devices(start_str, end_str)
    country_data = load_gsc_countries(start_str, end_str)

# ─── Summary KPIs with Insight ─────────────────────────────

trend_df = gsc_rows_to_df(trend_data)
if not trend_df.empty:
    total_clicks = int(trend_df["clicks"].sum())
    total_impressions = int(trend_df["impressions"].sum())
    avg_ctr = round(trend_df["ctr"].mean(), 1)
    avg_position = round(trend_df["position"].mean(), 1)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Clicks", f"{total_clicks:,}", help="People who clicked through to our site from Google")
    k2.metric("Total Impressions", f"{total_impressions:,}", help="Times our pages appeared in search results")
    k3.metric("Avg CTR", f"{avg_ctr}%", help="Click-through rate — % of impressions that became clicks")
    k4.metric("Avg Position", f"{avg_position}", help="1 = top of page 1, 10 = bottom of page 1, 11+ = page 2+")

    # Plain English insight
    overall_ctr = round(total_clicks / total_impressions * 100, 1) if total_impressions > 0 else 0
    st.markdown(
        f"**What this means:** We showed up in Google **{total_impressions:,} times** and got **{total_clicks:,} clicks** "
        f"(1 in every {round(total_impressions/total_clicks) if total_clicks > 0 else '∞'} people who saw us clicked through). "
        f"{'Our average position is strong (top 3) — we are highly visible.' if avg_position <= 3 else ''}"
        f"{'We rank on page 1 on average — improving to top 3 would significantly increase traffic.' if 3 < avg_position <= 10 else ''}"
        f"{'We are mostly on page 2+ — a key growth opportunity.' if avg_position > 10 else ''}"
    )

st.markdown("---")

# ─── Daily Trend ────────────────────────────────────────────

st.markdown("### Daily Search Performance")

if not trend_df.empty and "date" in trend_df.columns:
    trend_df["date"] = pd.to_datetime(trend_df["date"])
    trend_df = trend_df.sort_values("date")

    peak_day = trend_df.loc[trend_df["clicks"].idxmax()]
    st.markdown(
        f"**Insight:** Peak search day was **{peak_day['date'].strftime('%b %d')}** "
        f"with {int(peak_day['clicks']):,} clicks. "
        f"Look for patterns — do spikes correlate with content publishes, PR, or social activity?"
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=trend_df["date"], y=trend_df["clicks"],
        name="Clicks", marker_color=COLORS["info"],
    ))
    fig.add_trace(go.Scatter(
        x=trend_df["date"], y=trend_df["impressions"],
        mode="lines", name="Impressions",
        line=dict(color=COLORS["accent"], width=1.5, dash="dot"),
        yaxis="y2",
    ))
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", y=-0.15),
        yaxis=dict(title="Clicks"),
        yaxis2=dict(title="Impressions", overlaying="y", side="right"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─── Top Queries ────────────────────────────────────────────

st.markdown("### Top Search Queries")

queries_df = gsc_rows_to_df(queries_data)
if not queries_df.empty:
    # Categorize queries
    QUESTION_WORDS = ["how", "what", "why", "when", "where", "who", "which", "is ", "are ", "can ", "does ", "do ", "should", "will "]
    COMPARISON_WORDS = ["best", "top", "vs", "versus", "compare", "alternative", "review"]
    INTENT_WORDS = QUESTION_WORDS + COMPARISON_WORDS

    def classify_query(q):
        q_lower = q.lower().strip()
        if any(q_lower.startswith(w) for w in QUESTION_WORDS):
            return "Question"
        if any(w in q_lower for w in COMPARISON_WORDS):
            return "Comparison/Review"
        if any(w in q_lower for w in QUESTION_WORDS):
            return "Contains Question"
        return "Navigational/Other"

    queries_df["query_type"] = queries_df["query"].apply(classify_query)

    # Branded vs non-branded
    queries_df["branded"] = queries_df["query"].str.lower().str.contains("animoca|animaca", na=False)

    # Show insight
    question_queries = queries_df[queries_df["query_type"].isin(["Question", "Comparison/Review", "Contains Question"])]
    branded_count = queries_df["branded"].sum()

    st.markdown(
        f"**Insight:** Out of {len(queries_df)} top queries, **{branded_count} are branded** (people searching for 'Animoca') "
        f"and **{len(question_queries)} are question/comparison queries** that AI engines prioritize for citations. "
        f"{'Creating more FAQ and comparison content could capture AI search traffic.' if len(question_queries) < 5 else 'Good question query coverage — these are prime candidates for AI citations.'}"
    )

    tab1, tab2, tab3 = st.tabs(["All Queries", "AI-Priority Queries", "Non-Branded (Discovery)"])

    with tab1:
        st.dataframe(
            queries_df.drop(columns=["query_type", "branded"]).style.format({
                "clicks": "{:,.0f}", "impressions": "{:,.0f}",
                "ctr": "{:.1f}%", "position": "{:.1f}",
            }),
            use_container_width=True, hide_index=True,
        )

    with tab2:
        st.markdown("""
        **Why these matter for AEO:** AI search engines (ChatGPT, Perplexity, Gemini) primarily answer
        questions and comparisons. If people are asking these questions in Google, they're also asking
        AI engines. Ranking well here + having citation-ready content = AI visibility.
        """)

        if not question_queries.empty:
            st.dataframe(
                question_queries.drop(columns=["query_type", "branded"]).style.format({
                    "clicks": "{:,.0f}", "impressions": "{:,.0f}",
                    "ctr": "{:.1f}%", "position": "{:.1f}",
                }),
                use_container_width=True, hide_index=True,
            )
        else:
            st.warning(
                "**No question/comparison queries found in the top 100 queries.** "
                "This means people aren't finding us through informational searches — they only search for our brand name directly. "
                "\n\n**Recommended action:** Create content that answers questions your audience asks:\n"
                "- 'What is Animoca Brands?' (company explainer)\n"
                "- 'Best Web3 gaming companies' (comparison/list)\n"
                "- 'Animoca Brands vs [competitor]' (comparison)\n"
                "- 'How does blockchain gaming work?' (educational)\n"
                "- 'Top metaverse investments' (thought leadership)\n\n"
                "This type of content is exactly what AI engines cite in their answers."
            )

    with tab3:
        non_branded = queries_df[~queries_df["branded"]]
        if not non_branded.empty:
            st.markdown("**These are discovery queries** — people finding us through topics, not brand name. Growing these means reaching new audiences.")
            st.dataframe(
                non_branded.drop(columns=["query_type", "branded"]).style.format({
                    "clicks": "{:,.0f}", "impressions": "{:,.0f}",
                    "ctr": "{:.1f}%", "position": "{:.1f}",
                }),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("All top queries are branded. Non-branded content strategy is a key growth lever.")

st.markdown("---")

# ─── Top Pages ──────────────────────────────────────────────

st.markdown("### Top Pages by Clicks")

pages_df = gsc_rows_to_df(pages_data)
if not pages_df.empty:
    pages_df["impressions_rank"] = pages_df["impressions"].rank(ascending=False)
    pages_df["ctr_rank"] = pages_df["ctr"].rank(ascending=True)

    st.dataframe(
        pages_df.drop(columns=["impressions_rank", "ctr_rank"]).style.format({
            "clicks": "{:,.0f}", "impressions": "{:,.0f}",
            "ctr": "{:.1f}%", "position": "{:.1f}",
        }),
        use_container_width=True, hide_index=True,
    )

    # AEO Opportunities — with clear explanation
    median_impressions = pages_df["impressions"].median()
    median_ctr = pages_df["ctr"].median()
    opps = pages_df[
        (pages_df["impressions"] > median_impressions) &
        (pages_df["ctr"] < median_ctr)
    ].copy()

    st.markdown("#### Pages Losing Clicks to AI Overviews")

    if not opps.empty:
        st.markdown(
            f"**What this means:** These pages show up in Google a lot (above-average impressions) "
            f"but people rarely click through (below-average CTR of {median_ctr:.1f}%). "
            f"This pattern often means **Google AI Overviews are answering the query directly**, "
            f"so users get the answer without visiting our site.\n\n"
            f"**What to do:** Optimize these pages to be the *source* AI engines cite. "
            f"Add structured data, create concise citation-ready paragraphs, and ensure "
            f"our content adds unique value beyond what an AI summary provides."
        )
        st.dataframe(
            opps.drop(columns=["impressions_rank", "ctr_rank"]).style.format({
                "clicks": "{:,.0f}", "impressions": "{:,.0f}",
                "ctr": "{:.1f}%", "position": "{:.1f}",
            }),
            use_container_width=True, hide_index=True,
        )
    else:
        st.success("No pages with the high-impression/low-CTR pattern detected — search listings are performing well.")

st.markdown("---")

# ─── Device & Country ──────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Device Breakdown")
    device_df = gsc_rows_to_df(device_data)
    if not device_df.empty:
        total_device_clicks = device_df["clicks"].sum()
        device_df["share"] = (device_df["clicks"] / total_device_clicks * 100).round(1)
        top_device = device_df.loc[device_df["clicks"].idxmax(), "device"]
        st.markdown(f"**Insight:** Most searches come from **{top_device}** devices.")

        fig_d = px.pie(
            device_df, values="clicks", names="device",
            color_discrete_sequence=[COLORS["info"], COLORS["success"], COLORS["warning"]],
        )
        fig_d.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_d, use_container_width=True)

with col2:
    st.markdown("### Top Countries")
    country_df = gsc_rows_to_df(country_data)
    if not country_df.empty:
        top_country = country_df.loc[country_df["clicks"].idxmax(), "country"]
        st.markdown(f"**Insight:** Top market by search traffic is **{top_country}**.")

        fig_c = px.bar(
            country_df.head(10).sort_values("clicks", ascending=True),
            x="clicks", y="country",
            orientation="h",
            color_discrete_sequence=[COLORS["accent"]],
        )
        fig_c.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_c, use_container_width=True)

st.markdown("---")
st.caption(f"Data range: {start_str} to {end_str} · Source: Google Search Console")
