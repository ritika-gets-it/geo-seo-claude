"""
Page 5: AEO Impact Analysis
Measures how AEO work (schema, structured data, content optimization) is
affecting search performance and AI visibility. Cross-references schema
presence with actual GSC/GA4 data to show measurable impact.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from data_loader import (
    load_gsc_top_pages,
    load_gsc_top_queries,
    load_ga4_ai_traffic,
    load_ga4_top_pages,
    load_ga4_traffic_overview,
    gsc_rows_to_df,
    ga4_rows_to_df,
)
from config import COLORS, BRAND_NAME, SITE_URL


def _schema_description(schema_type):
    """Return human-readable description for common schema types."""
    descriptions = {
        "Organization": "Company identity — helps AI cite us correctly",
        "WebSite": "Site scope — helps AI understand what we do",
        "WebPage": "Page metadata — helps AI categorize content",
        "Article": "News/blog with author info — boosts citation credibility",
        "FAQPage": "Q&A pairs — AI pulls these directly into answers",
        "BreadcrumbList": "Site hierarchy — helps AI understand structure",
        "Product": "Product details — for commerce AI queries",
        "LocalBusiness": "Location info — for local AI results",
        "Person": "Author/team — strengthens E-E-A-T signals",
        "SoftwareApplication": "App details — helps AI recommend products",
        "HowTo": "Step-by-step — AI loves to cite these",
        "VideoObject": "Video metadata — YouTube has 0.737 AI citation correlation",
    }
    return descriptions.get(schema_type, f"{schema_type} markup")


st.set_page_config(page_title="AEO Impact", page_icon="🎯", layout="wide")
st.markdown("# 🎯 AEO Impact Analysis")
st.markdown("Is our schema markup and content optimization actually improving performance?")
st.markdown("---")

# Date range
col_d1, col_d2, _ = st.columns([1, 1, 2])
with col_d1:
    start_date = st.date_input("Start date", datetime.now() - timedelta(days=28), key="aeo_start")
with col_d2:
    end_date = st.date_input("End date", datetime.now() - timedelta(days=1), key="aeo_end")

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")
domain = "animocabrands.com"


# ─── Scan Pages for Schema ────────────────────────────────

@st.cache_data(ttl=86400)
def scan_pages_for_schema(domain, page_urls):
    """Check which pages have JSON-LD structured data."""
    import requests
    from bs4 import BeautifulSoup

    results = {}
    for url in page_urls:
        if not url.startswith("http"):
            url = f"https://{domain}{url}"
        try:
            resp = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            soup = BeautifulSoup(resp.text, "html.parser")
            scripts = soup.find_all("script", {"type": "application/ld+json"})
            schemas = []
            for s in scripts:
                try:
                    data = json.loads(s.string)
                    if isinstance(data, list):
                        for item in data:
                            schemas.append(item.get("@type", "Unknown"))
                    elif isinstance(data, dict):
                        if "@graph" in data:
                            for item in data["@graph"]:
                                schemas.append(item.get("@type", "Unknown"))
                        else:
                            schemas.append(data.get("@type", "Unknown"))
                except (json.JSONDecodeError, TypeError):
                    pass

            # Count content signals
            h1s = soup.find_all("h1")
            faqs = soup.find_all(["details", "summary"])
            tables = soup.find_all("table")
            lists = soup.find_all(["ul", "ol"])
            word_count = len(soup.get_text().split())

            results[url] = {
                "has_schema": len(schemas) > 0,
                "schema_count": len(schemas),
                "schema_types": schemas,
                "has_faq_markup": "FAQPage" in schemas,
                "has_article_markup": "Article" in schemas or "NewsArticle" in schemas,
                "has_org_markup": "Organization" in schemas,
                "word_count": word_count,
                "has_tables": len(tables) > 0,
                "has_lists": len(lists) > 0,
                "content_signals": len(tables) + len(lists) + len(faqs),
            }
        except Exception:
            results[url] = {"has_schema": False, "schema_count": 0, "schema_types": [], "error": True}

    return results


# ─── Load Performance Data ────────────────────────────────

with st.spinner("Loading performance data and scanning pages for schema..."):
    gsc_pages = load_gsc_top_pages(start_str, end_str, limit=25)
    gsc_queries = load_gsc_top_queries(start_str, end_str, limit=50)
    ai_traffic = load_ga4_ai_traffic(start_str, end_str)
    ga4_pages = load_ga4_top_pages(start_str, end_str, limit=25)
    ga4_overview = load_ga4_traffic_overview(start_str, end_str)

pages_df = gsc_rows_to_df(gsc_pages)
queries_df = gsc_rows_to_df(gsc_queries)
ga4_pages_df = ga4_rows_to_df(ga4_pages)
overview_df = ga4_rows_to_df(ga4_overview)

# Get page URLs to scan
page_urls = []
if not pages_df.empty and "page" in pages_df.columns:
    page_urls = pages_df["page"].tolist()[:15]  # Scan top 15 pages

# Scan for schema
schema_data = {}
if page_urls:
    with st.spinner("Scanning top pages for schema markup..."):
        schema_data = scan_pages_for_schema(domain, page_urls)

# ─── Schema Impact Summary ────────────────────────────────

st.markdown("### How Schema Markup Affects Performance")

if schema_data and not pages_df.empty:
    # Merge schema data with performance data
    pages_df["has_schema"] = pages_df["page"].apply(
        lambda p: schema_data.get(p, {}).get("has_schema", False)
    )
    pages_df["schema_count"] = pages_df["page"].apply(
        lambda p: schema_data.get(p, {}).get("schema_count", 0)
    )
    pages_df["schema_types"] = pages_df["page"].apply(
        lambda p: ", ".join(schema_data.get(p, {}).get("schema_types", []))
    )

    with_schema = pages_df[pages_df["has_schema"]]
    without_schema = pages_df[~pages_df["has_schema"]]

    schema_count = len(with_schema)
    no_schema_count = len(without_schema)

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Pages with Schema", f"{schema_count}/{len(pages_df)}", help="Out of top performing pages")
    k2.metric("Pages without Schema", f"{no_schema_count}", help="Opportunity to add structured data")

    avg_ctr_schema = round(with_schema["ctr"].mean(), 1) if not with_schema.empty else 0
    avg_ctr_no_schema = round(without_schema["ctr"].mean(), 1) if not without_schema.empty else 0
    k3.metric("Avg CTR (with schema)", f"{avg_ctr_schema}%", help="Click-through rate for pages with structured data")
    k4.metric("Avg CTR (without schema)", f"{avg_ctr_no_schema}%", help="Click-through rate for pages without structured data")

    # Insight
    if avg_ctr_schema > 0 and avg_ctr_no_schema > 0:
        diff = round(avg_ctr_schema - avg_ctr_no_schema, 1)
        if diff > 0:
            st.success(
                f"**Pages with schema markup have {diff} percentage points higher CTR** "
                f"({avg_ctr_schema}% vs {avg_ctr_no_schema}%). Schema is helping our search listings "
                f"stand out and earn more clicks."
            )
        elif diff < 0:
            st.info(
                f"Pages without schema currently have higher CTR ({avg_ctr_no_schema}% vs {avg_ctr_schema}%). "
                f"This may be because schema pages target more competitive queries. "
                f"Look at position differences — schema pages may rank for harder terms."
            )
        else:
            st.info("CTR is similar with and without schema. Monitor as more pages get markup.")
    elif schema_count == 0:
        st.warning("**None of the top pages have schema markup.** Adding structured data is the highest-impact AEO action to take.")
    elif no_schema_count == 0:
        st.success("**All top pages have schema markup.** Focus on enriching schema types (add FAQPage, Article) for even more impact.")

    # Comparison chart
    if not with_schema.empty and not without_schema.empty:
        comparison = pd.DataFrame([
            {
                "Group": "With Schema",
                "Avg Clicks": round(with_schema["clicks"].mean(), 1),
                "Avg Impressions": round(with_schema["impressions"].mean(), 1),
                "Avg CTR": avg_ctr_schema,
                "Avg Position": round(with_schema["position"].mean(), 1),
            },
            {
                "Group": "Without Schema",
                "Avg Clicks": round(without_schema["clicks"].mean(), 1),
                "Avg Impressions": round(without_schema["impressions"].mean(), 1),
                "Avg CTR": avg_ctr_no_schema,
                "Avg Position": round(without_schema["position"].mean(), 1),
            },
        ])

        st.markdown("#### Side-by-Side Comparison")

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                comparison.melt(id_vars="Group", value_vars=["Avg Clicks", "Avg CTR", "Avg Position"]),
                x="variable", y="value", color="Group", barmode="group",
                color_discrete_map={"With Schema": COLORS["success"], "Without Schema": COLORS["danger"]},
                labels={"variable": "", "value": ""},
            )
            fig.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.dataframe(comparison.style.format({
                "Avg Clicks": "{:.0f}",
                "Avg Impressions": "{:.0f}",
                "Avg CTR": "{:.1f}%",
                "Avg Position": "{:.1f}",
            }), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ─── Page-by-Page Breakdown ────────────────────────────

    st.markdown("### Page-by-Page Schema & Performance")
    st.markdown("Which pages have schema, what type, and how they're performing in search.")

    display_df = pages_df[["page", "has_schema", "schema_types", "clicks", "impressions", "ctr", "position"]].copy()
    display_df["page"] = display_df["page"].apply(lambda p: p.replace(f"https://www.{domain}", "").replace(f"https://{domain}", "") or "/")

    display_df = display_df.rename(columns={
        "page": "Page",
        "has_schema": "Has Schema",
        "schema_types": "Schema Types",
        "clicks": "Clicks",
        "impressions": "Impressions",
        "ctr": "CTR %",
        "position": "Position",
    })

    def style_schema(val):
        if val is True:
            return "background-color: #d4edda; color: #155724"
        elif val is False:
            return "background-color: #f8d7da; color: #721c24"
        return ""

    st.dataframe(
        display_df.style.applymap(style_schema, subset=["Has Schema"]).format({
            "Clicks": "{:,.0f}", "Impressions": "{:,.0f}",
            "CTR %": "{:.1f}%", "Position": "{:.1f}",
        }),
        use_container_width=True, hide_index=True,
    )

    # Highlight pages that need schema
    if not without_schema.empty:
        st.markdown("#### Priority Pages to Add Schema")
        st.markdown("These are your top-performing pages that don't have schema yet — adding structured data could boost their CTR.")
        high_value_no_schema = without_schema.nlargest(5, "impressions")[["page", "clicks", "impressions", "ctr", "position"]]
        high_value_no_schema["page"] = high_value_no_schema["page"].apply(
            lambda p: p.replace(f"https://www.{domain}", "").replace(f"https://{domain}", "") or "/"
        )
        st.dataframe(
            high_value_no_schema.rename(columns={"page": "Page", "clicks": "Clicks", "impressions": "Impressions", "ctr": "CTR %", "position": "Position"}).style.format({
                "Clicks": "{:,.0f}", "Impressions": "{:,.0f}",
                "CTR %": "{:.1f}%", "Position": "{:.1f}",
            }),
            use_container_width=True, hide_index=True,
        )

st.markdown("---")

# ─── AI Citation Readiness ────────────────────────────────

st.markdown("### Content Readiness for AI Citations")
st.markdown("AI engines prefer content that is concise, factual, and well-structured. Here's how our top pages score.")

if schema_data:
    citation_rows = []
    for url, data in schema_data.items():
        if data.get("error"):
            continue
        short_url = url.replace(f"https://www.{domain}", "").replace(f"https://{domain}", "") or "/"

        # Score content readiness
        readiness_score = 0
        reasons = []

        if data.get("has_schema"):
            readiness_score += 30
            reasons.append("Has schema markup")
        else:
            reasons.append("No schema markup")

        if data.get("has_faq_markup"):
            readiness_score += 20
            reasons.append("Has FAQ schema (AI favorite)")

        word_count = data.get("word_count", 0)
        if 500 < word_count < 5000:
            readiness_score += 20
            reasons.append(f"Good content length ({word_count:,} words)")
        elif word_count >= 5000:
            readiness_score += 10
            reasons.append(f"Long content ({word_count:,} words) — may need summary sections")
        else:
            reasons.append(f"Thin content ({word_count:,} words)")

        if data.get("has_tables") or data.get("has_lists"):
            readiness_score += 15
            reasons.append("Has structured content (tables/lists)")

        if data.get("content_signals", 0) >= 3:
            readiness_score += 15
            reasons.append("Rich content formatting")

        citation_rows.append({
            "Page": short_url,
            "Citation Score": readiness_score,
            "Schema": "Yes" if data.get("has_schema") else "No",
            "Word Count": word_count,
            "Structured Content": "Yes" if data.get("has_tables") or data.get("has_lists") else "No",
            "Key Factors": " · ".join(reasons[:3]),
        })

    if citation_rows:
        citation_df = pd.DataFrame(citation_rows).sort_values("Citation Score", ascending=False)

        avg_score = round(citation_df["Citation Score"].mean())
        top_page = citation_df.iloc[0]["Page"]
        bottom_page = citation_df.iloc[-1]["Page"]

        st.markdown(
            f"**Insight:** Average citation readiness is **{avg_score}/100**. "
            f"Best page: **{top_page}** ({citation_df.iloc[0]['Citation Score']}/100). "
            f"Most improvement needed: **{bottom_page}** ({citation_df.iloc[-1]['Citation Score']}/100)."
        )

        def color_score(val):
            if isinstance(val, (int, float)):
                if val >= 60:
                    return "background-color: #d4edda"
                elif val >= 30:
                    return "background-color: #fff3cd"
                else:
                    return "background-color: #f8d7da"
            return ""

        st.dataframe(
            citation_df.style.applymap(color_score, subset=["Citation Score"]).format({
                "Word Count": "{:,}",
            }),
            use_container_width=True, hide_index=True,
        )

st.markdown("---")

# ─── AI Traffic vs Schema Correlation ─────────────────────

st.markdown("### Are Schema Pages Getting AI Traffic?")

ai_sources = ai_traffic.get("ai_referral_sources", [])
ai_sessions = ai_traffic.get("total_ai_sessions", 0)

if ai_sessions > 0 and not ga4_pages_df.empty:
    st.markdown(
        f"We're receiving **{ai_sessions:,} AI referral sessions**. "
        f"Below are the top pages by traffic — pages with schema markup are highlighted."
    )

    ga4_pages_df["short_page"] = ga4_pages_df.get("pagePath", ga4_pages_df.columns[0]).apply(
        lambda p: p if p.startswith("/") else "/" + p
    )

    # Try to match GA4 pages with schema data
    ga4_pages_df["has_schema"] = ga4_pages_df["short_page"].apply(
        lambda p: any(
            p in url or url.endswith(p)
            for url in schema_data.keys()
            if schema_data[url].get("has_schema")
        ) if schema_data else False
    )

    top_ga4 = ga4_pages_df.head(15)
    st.dataframe(
        top_ga4[["short_page", "has_schema", "screenPageViews", "sessions", "bounceRate"]].rename(columns={
            "short_page": "Page",
            "has_schema": "Has Schema",
            "screenPageViews": "Page Views",
            "sessions": "Sessions",
            "bounceRate": "Bounce Rate",
        }).style.format({
            "Page Views": "{:,.0f}", "Sessions": "{:,.0f}", "Bounce Rate": "{:.1%}",
        }),
        use_container_width=True, hide_index=True,
    )
elif ai_sessions == 0:
    st.info(
        "No AI referral traffic yet to correlate with schema presence. "
        "Once AI traffic starts flowing, this section will show which pages AI engines are citing "
        "and whether schema markup makes a difference."
    )

st.markdown("---")

# ─── Recommendations ──────────────────────────────────────

st.markdown("### What to Do Next")

actions = []

if schema_data:
    no_schema_pages = [url for url, data in schema_data.items() if not data.get("has_schema") and not data.get("error")]
    with_schema_pages = [url for url, data in schema_data.items() if data.get("has_schema")]
    faq_pages = [url for url, data in schema_data.items() if data.get("has_faq_markup")]

    if no_schema_pages:
        actions.append(("HIGH", f"Add schema markup to {len(no_schema_pages)} top pages that don't have it yet"))

    if not faq_pages:
        actions.append(("HIGH", "Add FAQPage schema to at least one page — AI engines directly pull Q&A into answers"))

    if len(with_schema_pages) > 0 and ai_sessions == 0:
        actions.append(("MEDIUM", "Schema is in place but no AI traffic yet — focus on content quality and brand mentions to trigger citations"))

    if ai_sessions > 0:
        actions.append(("MONITOR", f"AI traffic is flowing ({ai_sessions:,} sessions) — track week-over-week growth"))

if not queries_df.empty:
    question_queries = queries_df[queries_df["query"].str.lower().str.contains(
        r"^(how|what|why|when|where|who|which|is |are |can |does )|best|top|vs|review", regex=True, na=False
    )]
    if len(question_queries) < 3:
        actions.append(("HIGH", "Create FAQ/how-to content — very few question queries are finding us in search"))

if not actions:
    st.success("AEO setup looks solid. Continue monitoring and optimizing content for AI citations.")
else:
    for level, action in actions:
        if level == "HIGH":
            st.warning(f"**{level}:** {action}")
        elif level == "MONITOR":
            st.success(f"**{level}:** {action}")
        else:
            st.info(f"**{level}:** {action}")

st.markdown("---")
st.caption(f"Data range: {start_str} to {end_str} · Schema scan of top 15 pages · Sources: GSC, GA4, live page analysis")
