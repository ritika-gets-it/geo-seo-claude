"""
Page 1: Executive Overview
Top-level KPIs with contextual insights for senior management.
Every number tells a story — no raw data without meaning.
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
    load_ga4_traffic_overview,
    load_ga4_ai_traffic,
    load_ga4_traffic_sources,
    load_gsc_daily_trend,
    load_gsc_top_queries,
    ga4_rows_to_df,
    gsc_rows_to_df,
)
from config import COLORS, BRAND_NAME

st.set_page_config(page_title="Executive Overview", page_icon="📈", layout="wide")
st.markdown(f"# 📈 Executive Overview — {BRAND_NAME}")
st.markdown("What's happening with our website and AI visibility this period.")
st.markdown("---")

# Date range selector
col_d1, col_d2, col_d3 = st.columns([1, 1, 2])
with col_d1:
    start_date = st.date_input("Start date", datetime.now() - timedelta(days=28))
with col_d2:
    end_date = st.date_input("End date", datetime.now() - timedelta(days=1))

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")
num_days = (end_date - start_date).days or 1

# Load data
with st.spinner("Loading data from GA4 and GSC..."):
    ga4_overview = load_ga4_traffic_overview(start_str, end_str)
    ai_traffic = load_ga4_ai_traffic(start_str, end_str)
    gsc_trend = load_gsc_daily_trend(start_str, end_str)
    gsc_queries = load_gsc_top_queries(start_str, end_str, limit=50)

# ─── Compute All Metrics ───────────────────────────────────

ga4_df = ga4_rows_to_df(ga4_overview)
gsc_df = gsc_rows_to_df(gsc_trend)

total_sessions = int(ga4_df["sessions"].sum()) if not ga4_df.empty else 0
total_users = int(ga4_df["totalUsers"].sum()) if not ga4_df.empty else 0
total_pageviews = int(ga4_df["screenPageViews"].sum()) if not ga4_df.empty else 0
avg_bounce = round(ga4_df["bounceRate"].mean() * 100, 1) if not ga4_df.empty else 0
avg_duration = round(ga4_df["averageSessionDuration"].mean(), 0) if not ga4_df.empty else 0
pages_per_session = round(total_pageviews / total_sessions, 1) if total_sessions > 0 else 0
daily_avg_sessions = round(total_sessions / num_days) if num_days > 0 else 0

total_clicks = int(gsc_df["clicks"].sum()) if not gsc_df.empty else 0
total_impressions = int(gsc_df["impressions"].sum()) if not gsc_df.empty else 0
avg_ctr = round(gsc_df["ctr"].mean(), 1) if not gsc_df.empty else 0
avg_position = round(gsc_df["position"].mean(), 1) if not gsc_df.empty else 0
click_through_rate_overall = round(total_clicks / total_impressions * 100, 1) if total_impressions > 0 else 0

ai_sessions = ai_traffic.get("total_ai_sessions", 0)
ai_users = ai_traffic.get("total_ai_users", 0)
ai_share = round((ai_sessions / total_sessions * 100), 2) if total_sessions > 0 else 0

# Identify peak and low days
if not ga4_df.empty and "date" in ga4_df.columns:
    ga4_df["date"] = pd.to_datetime(ga4_df["date"], format="%Y%m%d")
    ga4_df = ga4_df.sort_values("date")
    peak_day = ga4_df.loc[ga4_df["sessions"].idxmax()]
    low_day = ga4_df.loc[ga4_df["sessions"].idxmin()]
    peak_date_str = peak_day["date"].strftime("%b %d")
    low_date_str = low_day["date"].strftime("%b %d")
    peak_sessions = int(peak_day["sessions"])
    low_sessions = int(low_day["sessions"])

# ─── Top-Line Summary (Plain English) ─────────────────────

st.markdown("### The Big Picture")

summary_parts = []
summary_parts.append(f"Over the last **{num_days} days**, animocabrands.com received **{total_sessions:,} visits** from **{total_users:,} unique visitors**, averaging **{daily_avg_sessions:,} sessions per day**.")

if not ga4_df.empty:
    summary_parts.append(f"Peak traffic was **{peak_date_str}** ({peak_sessions:,} sessions) and the quietest day was **{low_date_str}** ({low_sessions:,} sessions).")

if avg_bounce > 70:
    summary_parts.append(f"Bounce rate is **{avg_bounce}%** — on the high side. Most visitors leave after viewing one page, which means content may not be engaging enough or visitors are finding their answer immediately.")
elif avg_bounce > 50:
    summary_parts.append(f"Bounce rate is **{avg_bounce}%** — within normal range for a corporate site.")
else:
    summary_parts.append(f"Bounce rate is **{avg_bounce}%** — strong engagement. Visitors are exploring multiple pages.")

if total_impressions > 0:
    summary_parts.append(f"The site appeared in **{total_impressions:,} Google searches** and earned **{total_clicks:,} clicks** (overall CTR: **{click_through_rate_overall}%**). Average search position: **{avg_position}**.")

if ai_sessions > 0:
    summary_parts.append(f"**{ai_sessions:,} sessions ({ai_share}%)** came from AI platforms (ChatGPT, Perplexity, etc.) — this is the traffic our AEO work is driving.")
else:
    summary_parts.append("No measurable AI referral traffic yet — this is the baseline we're building from.")

st.markdown(" ".join(summary_parts))

st.markdown("---")

# ─── KPI Cards (with context) ─────────────────────────────

st.markdown("### Key Metrics")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Daily Avg Sessions", f"{daily_avg_sessions:,}", help="Average visits per day this period")
k2.metric("Pages Per Session", f"{pages_per_session}", help="How many pages each visitor views — higher = more engaged")
k3.metric("Bounce Rate", f"{avg_bounce}%", help="% of visitors who leave after one page — lower is better")
k4.metric("Avg Visit Duration", f"{avg_duration:.0f}s", help="How long visitors stay — longer = more valuable")

s1, s2, s3, s4 = st.columns(4)
s1.metric("Search Clicks", f"{total_clicks:,}", help="How many Google searchers clicked through to our site")
s2.metric("Search Impressions", f"{total_impressions:,}", help="How many times we appeared in Google search results")
s3.metric("Click-Through Rate", f"{click_through_rate_overall}%", help="% of people who saw us in search and clicked — higher = our titles/descriptions are compelling")
s4.metric("Avg Search Position", f"{avg_position}", help="Where we rank on average — 1-3 is page 1 top, 4-10 is page 1")

a1, a2, a3, a4 = st.columns(4)
a1.metric("AI Traffic Sessions", f"{ai_sessions:,}", help="Visits from ChatGPT, Perplexity, Claude, Gemini, Copilot")
a2.metric("AI Traffic Share", f"{ai_share}%", help="What % of our total traffic comes from AI platforms")
a3.metric("AI Users", f"{ai_users:,}", help="Unique visitors from AI platforms")
a4.metric("Total Users", f"{total_users:,}", help="All unique visitors for comparison")

st.markdown("---")

# ─── Traffic Trend (with insight) ──────────────────────────

st.markdown("### Daily Traffic Trend")

if not ga4_df.empty:
    # Insight above the chart
    weekday_avg = ga4_df.groupby(ga4_df["date"].dt.dayofweek)["sessions"].mean()
    best_weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][int(weekday_avg.idxmax())]
    worst_weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][int(weekday_avg.idxmin())]

    st.markdown(f"**Insight:** Traffic peaks on **{best_weekday}s** and dips on **{worst_weekday}s**. "
                f"The busiest day was **{peak_date_str}** with {peak_sessions:,} sessions — "
                f"worth investigating what drove that spike (PR, social post, news mention?).")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ga4_df["date"], y=ga4_df["sessions"],
        mode="lines+markers", name="Sessions",
        line=dict(color=COLORS["info"], width=2.5),
        marker=dict(size=5),
        fill="tozeroy", fillcolor="rgba(9,132,227,0.1)",
    ))
    fig.add_trace(go.Scatter(
        x=ga4_df["date"], y=ga4_df["totalUsers"],
        mode="lines+markers", name="Unique Users",
        line=dict(color=COLORS["success"], width=2),
        marker=dict(size=4),
    ))
    # Add average line
    fig.add_hline(y=daily_avg_sessions, line_dash="dash", line_color="grey",
                  annotation_text=f"Daily avg: {daily_avg_sessions:,}")
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", y=-0.15),
        xaxis_title="", yaxis_title="Visitors",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No traffic data available for the selected date range.")

st.markdown("---")

# ─── Search Performance (with insight) ────────────────────

st.markdown("### Search Visibility")

if not gsc_df.empty and "date" in gsc_df.columns:
    gsc_df["date"] = pd.to_datetime(gsc_df["date"])
    gsc_df = gsc_df.sort_values("date")

    # Insight
    if avg_position <= 3:
        pos_insight = f"Average position **{avg_position}** — we're ranking in the top 3 on average, which is strong."
    elif avg_position <= 10:
        pos_insight = f"Average position **{avg_position}** — we're on page 1 but not at the top. Improving to top 3 could significantly increase clicks."
    else:
        pos_insight = f"Average position **{avg_position}** — we're mostly on page 2+. Most clicks go to page 1 results, so this is our biggest growth opportunity."

    if click_through_rate_overall < 2:
        ctr_insight = "CTR is low — our search snippets (titles/descriptions) may need improvement, or AI overviews may be answering queries before users click."
    elif click_through_rate_overall < 5:
        ctr_insight = "CTR is moderate — there's room to improve titles and meta descriptions to attract more clicks."
    else:
        ctr_insight = "CTR is healthy — our search listings are compelling to users."

    st.markdown(f"**Insight:** {pos_insight} {ctr_insight}")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=gsc_df["date"], y=gsc_df["clicks"],
        name="Clicks", marker_color=COLORS["info"],
    ))
    fig2.add_trace(go.Scatter(
        x=gsc_df["date"], y=gsc_df["impressions"],
        mode="lines", name="Impressions",
        line=dict(color=COLORS["accent"], width=1.5, dash="dot"),
        yaxis="y2",
    ))
    fig2.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", y=-0.15),
        yaxis=dict(title="Clicks"),
        yaxis2=dict(title="Impressions", overlaying="y", side="right"),
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ─── AI Traffic Sources (with insight) ─────────────────────

st.markdown("### AI Traffic Breakdown")

ai_sources = ai_traffic.get("ai_referral_sources", [])
if ai_sources:
    ai_df = ga4_rows_to_df({"rows": ai_sources})
    if not ai_df.empty and "sessionSource" in ai_df.columns:
        top_ai_source = ai_df.loc[ai_df["sessions"].idxmax(), "sessionSource"]
        top_ai_sessions = int(ai_df["sessions"].max())

        st.markdown(
            f"**Insight:** The top AI source is **{top_ai_source}** with {top_ai_sessions:,} sessions. "
            f"AI platforms sent **{ai_share}% of total traffic** this period. "
            f"Industry benchmark: most sites see <1% AI traffic, so "
            f"{'we are ahead of the curve.' if ai_share > 1 else 'we are in line with the market — AEO work will move this number.'}"
        )

        ai_df = ai_df.sort_values("sessions", ascending=True)
        fig3 = px.bar(
            ai_df, x="sessions", y="sessionSource",
            orientation="h",
            color_discrete_sequence=[COLORS["ai_purple"]],
            labels={"sessionSource": "AI Platform", "sessions": "Sessions"},
        )
        fig3.update_layout(
            height=max(200, len(ai_df) * 50),
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)
else:
    st.markdown(
        "**Insight:** No AI referral traffic detected yet. This is our **baseline** — as AEO work "
        "(schema markup, content optimization, brand presence building) takes effect over the coming weeks, "
        "we expect to see sessions appearing from ChatGPT, Perplexity, and other AI platforms. "
        "This is the number we're working to grow."
    )

st.markdown("---")

# ─── Top Queries (with insight) ────────────────────────────

st.markdown("### What People Search to Find Us")

queries_df = gsc_rows_to_df(gsc_queries)
if not queries_df.empty:
    branded = queries_df[queries_df["query"].str.lower().str.contains("animoca|animaca", na=False)]
    non_branded = queries_df[~queries_df["query"].str.lower().str.contains("animoca|animaca", na=False)]
    branded_clicks = int(branded["clicks"].sum())
    non_branded_clicks = int(non_branded["clicks"].sum())
    branded_pct = round(branded_clicks / total_clicks * 100, 1) if total_clicks > 0 else 0

    st.markdown(
        f"**Insight:** **{branded_pct}% of search clicks** come from branded searches "
        f"(people searching for 'Animoca'). "
        f"{'This is very high — most visitors already know us. ' if branded_pct > 70 else ''}"
        f"Non-branded clicks ({non_branded_clicks:,}) represent people discovering us through topics — "
        f"{'growing this number means our content is reaching new audiences.' if non_branded_clicks > 0 else 'this is an opportunity to create topic-based content that attracts new visitors.'}"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top Branded Queries**")
        if not branded.empty:
            st.dataframe(
                branded.head(5).style.format({
                    "clicks": "{:,.0f}", "impressions": "{:,.0f}",
                    "ctr": "{:.1f}%", "position": "{:.1f}",
                }),
                use_container_width=True, hide_index=True,
            )
    with col2:
        st.markdown("**Top Non-Branded Queries** (discovery traffic)")
        if not non_branded.empty:
            st.dataframe(
                non_branded.head(5).style.format({
                    "clicks": "{:,.0f}", "impressions": "{:,.0f}",
                    "ctr": "{:.1f}%", "position": "{:.1f}",
                }),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No non-branded queries found — creating topic-focused content will help here.")

st.markdown("---")

# ─── Executive Summary Box ─────────────────────────────────

st.markdown("### Summary & Recommendations")

recs = []
if avg_bounce > 65:
    recs.append("**Reduce bounce rate** — Visitors are leaving quickly. Improve internal linking, add related content suggestions, and ensure page load is fast.")
if avg_position > 5:
    recs.append("**Improve search rankings** — Average position is beyond the top 5. Focus on strengthening content for high-impression queries.")
if click_through_rate_overall < 3:
    recs.append("**Improve search snippets** — Low CTR suggests our titles and meta descriptions aren't compelling enough, or AI overviews are capturing clicks.")
if branded_pct > 80:
    recs.append("**Diversify beyond branded traffic** — Over 80% of clicks are branded. Create topic-authority content to capture non-branded searches.")
if ai_share < 1:
    recs.append("**Accelerate AEO work** — AI traffic is below 1%. Prioritize schema markup, llms.txt, AI crawler access, and citation-ready content.")
if ai_share >= 1:
    recs.append(f"**AI traffic is growing ({ai_share}%)** — Double down on what's working. Identify which pages attract AI referrals and create more content like them.")

if recs:
    for rec in recs:
        st.markdown(f"- {rec}")
else:
    st.success("All key metrics look healthy. Continue current strategy and monitor trends.")

st.markdown("---")
st.caption(f"Data range: {start_str} to {end_str} · Sources: Google Analytics 4, Google Search Console · Auto-refreshes daily")
