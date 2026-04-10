"""
Page 5: GEO/AEO Scores
Citability analysis, brand presence, AI crawler access, and AEO readiness.
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

from config import COLORS, BRAND_NAME, SITE_URL

st.set_page_config(page_title="GEO/AEO Scores", page_icon="🎯", layout="wide")
st.markdown("# 🎯 GEO/AEO Readiness Scores")
st.markdown("How well is animocabrands.com optimized for AI search engines?")
st.markdown("---")

# ─── AI Crawler Access ──────────────────────────────────────

st.markdown("### AI Crawler Access Status")
st.markdown("Are AI crawlers allowed to access your site?")

@st.cache_data(ttl=86400)
def check_crawler_access(url):
    """Check robots.txt for AI crawler access."""
    try:
        from fetch_page import check_robots_txt
        result = check_robots_txt(url)
        return result
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=86400)
def check_llms_txt(url):
    """Check if llms.txt exists."""
    try:
        import requests
        from urllib.parse import urlparse
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        domain = parsed.netloc or parsed.path
        llms_url = f"https://{domain}/llms.txt"
        resp = requests.get(llms_url, timeout=10)
        return {
            "exists": resp.status_code == 200,
            "url": llms_url,
            "status_code": resp.status_code,
            "content_preview": resp.text[:500] if resp.status_code == 200 else None,
        }
    except Exception as e:
        return {"exists": False, "error": str(e)}

crawlers = {
    "GPTBot (OpenAI/ChatGPT)": "GPTBot",
    "ClaudeBot (Anthropic)": "ClaudeBot",
    "PerplexityBot": "PerplexityBot",
    "Google-Extended (Gemini)": "Google-Extended",
    "Googlebot (Search)": "Googlebot",
    "Bingbot (Bing/Copilot)": "Bingbot",
}

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### robots.txt Crawler Status")

    # This would call the actual robots.txt check in production
    # For now, show the framework
    crawler_status = []
    for display_name, bot_name in crawlers.items():
        crawler_status.append({
            "Crawler": display_name,
            "Bot Name": bot_name,
            "Status": "Check with `/geo crawlers`",
        })

    st.dataframe(pd.DataFrame(crawler_status), use_container_width=True, hide_index=True)

    st.info("Run `/geo crawlers animocabrands.com` in Claude Code for a full robots.txt analysis.")

with col2:
    st.markdown("#### llms.txt Status")

    llms_result = check_llms_txt("animocabrands.com")

    if llms_result.get("exists"):
        st.success(f"llms.txt found at {llms_result['url']}")
        if llms_result.get("content_preview"):
            with st.expander("Preview llms.txt content"):
                st.code(llms_result["content_preview"])
    else:
        st.warning("No llms.txt file found. This file helps AI crawlers understand your site.")
        st.markdown("""
        **Create one with:** `/geo llmstxt animocabrands.com`

        llms.txt tells AI crawlers which pages to prioritize and how to categorize your content.
        """)

st.markdown("---")

# ─── Brand Presence on AI-Cited Platforms ──────────────────

st.markdown("### Brand Presence on AI-Cited Platforms")
st.markdown("AI engines cite sources they trust. Strong presence on these platforms increases citation probability.")

@st.cache_data(ttl=86400)
def scan_brand_presence():
    try:
        from brand_scanner import generate_brand_report
        return generate_brand_report(BRAND_NAME, "animocabrands.com")
    except Exception:
        return None

brand_data = scan_brand_presence()

if brand_data:
    platforms = brand_data.get("platforms", {})
    platform_rows = []
    for name, info in platforms.items():
        platform_rows.append({
            "Platform": name,
            "Found": "Yes" if info.get("found") else "No",
            "Correlation": info.get("correlation", "—"),
            "Details": info.get("details", "—"),
        })

    if platform_rows:
        pdf = pd.DataFrame(platform_rows)
        st.dataframe(pdf, use_container_width=True, hide_index=True)
else:
    # Show the framework even without live data
    platforms_info = pd.DataFrame([
        {"Platform": "YouTube", "AI Citation Correlation": "0.737 (Strongest)", "Priority": "Critical"},
        {"Platform": "Reddit", "AI Citation Correlation": "High", "Priority": "Critical"},
        {"Platform": "Wikipedia", "AI Citation Correlation": "High", "Priority": "High"},
        {"Platform": "LinkedIn", "AI Citation Correlation": "Medium-High", "Priority": "High"},
        {"Platform": "Quora", "AI Citation Correlation": "Medium", "Priority": "Medium"},
        {"Platform": "GitHub", "AI Citation Correlation": "Medium", "Priority": "Medium"},
        {"Platform": "Stack Overflow", "AI Citation Correlation": "Medium", "Priority": "Low"},
        {"Platform": "Crunchbase", "AI Citation Correlation": "Medium", "Priority": "Medium"},
        {"Platform": "G2", "AI Citation Correlation": "Medium", "Priority": "Low"},
        {"Platform": "Trustpilot", "AI Citation Correlation": "Medium", "Priority": "Medium"},
    ])

    st.dataframe(platforms_info, use_container_width=True, hide_index=True)
    st.info("Run `/geo brands animocabrands.com` in Claude Code for a full brand presence scan.")

st.markdown("---")

# ─── AEO Readiness Checklist ──────────────────────────────

st.markdown("### AEO Readiness Checklist")

checklist = [
    {"Item": "Structured Data (JSON-LD)", "Category": "Schema", "Impact": "High",
     "Description": "Organization, WebSite, Article schema on key pages"},
    {"Item": "AI Crawler Access", "Category": "Technical", "Impact": "Critical",
     "Description": "GPTBot, ClaudeBot, PerplexityBot allowed in robots.txt"},
    {"Item": "llms.txt File", "Category": "Technical", "Impact": "Medium",
     "Description": "Guide AI crawlers to your most important content"},
    {"Item": "Citation-Ready Content", "Category": "Content", "Impact": "High",
     "Description": "Concise, factual paragraphs (134-167 words) that AI can quote"},
    {"Item": "FAQ Sections", "Category": "Content", "Impact": "High",
     "Description": "Question-answer format that matches AI search patterns"},
    {"Item": "Author/Expertise Signals", "Category": "E-E-A-T", "Impact": "High",
     "Description": "Named authors, credentials, author schema markup"},
    {"Item": "Brand Mentions (YouTube)", "Category": "Authority", "Impact": "Critical",
     "Description": "YouTube has 0.737 correlation with AI citations — strongest signal"},
    {"Item": "Brand Mentions (Reddit)", "Category": "Authority", "Impact": "High",
     "Description": "Authentic discussions and recommendations on relevant subreddits"},
    {"Item": "Wikipedia Presence", "Category": "Authority", "Impact": "High",
     "Description": "Wikipedia/Wikidata entity = trusted source for AI engines"},
    {"Item": "Server-Side Rendering", "Category": "Technical", "Impact": "High",
     "Description": "AI crawlers don't execute JavaScript — SSR is required"},
    {"Item": "Fast Load Times", "Category": "Technical", "Impact": "Medium",
     "Description": "Core Web Vitals affect crawl priority for all bots"},
    {"Item": "Original Data & Statistics", "Category": "Content", "Impact": "High",
     "Description": "Unique research, case studies, proprietary data that AI engines prefer to cite"},
]

checklist_df = pd.DataFrame(checklist)

# Color-code by impact
def highlight_impact(val):
    colors = {"Critical": "background-color: #d63031; color: white",
              "High": "background-color: #fdcb6e",
              "Medium": "background-color: #dfe6e9"}
    return colors.get(val, "")

st.dataframe(
    checklist_df.style.applymap(highlight_impact, subset=["Impact"]),
    use_container_width=True, hide_index=True,
)

st.markdown("---")

# ─── GEO Score Gauge ──────────────────────────────────────

st.markdown("### Run a Full GEO Audit")
st.markdown("""
For a comprehensive GEO score (0-100) with detailed analysis across all categories, run:

```
/geo audit animocabrands.com
```

This performs a full audit across:
- AI Citability & Visibility (25%)
- Brand Authority Signals (20%)
- Content Quality & E-E-A-T (20%)
- Technical Foundations (15%)
- Structured Data (10%)
- Platform Optimization (10%)
""")

st.markdown("---")
st.caption(f"Brand: {BRAND_NAME} · Site: {SITE_URL}")
