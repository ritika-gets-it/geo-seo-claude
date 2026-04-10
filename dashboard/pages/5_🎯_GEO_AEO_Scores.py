"""
Page 5: GEO/AEO Scores
Live crawler access checks, structured data detection, brand presence, and actionable insights.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from config import COLORS, BRAND_NAME, SITE_URL


def _schema_description(schema_type):
    """Return human-readable description for common schema types."""
    descriptions = {
        "Organization": "Company identity — name, logo, social profiles. Helps AI cite us correctly.",
        "WebSite": "Site-level info — helps AI understand our site's purpose and scope.",
        "WebPage": "Individual page metadata — helps AI categorize content.",
        "Article": "Blog/news content with author and publication info — boosts citation credibility.",
        "FAQPage": "Question-answer pairs — AI engines pull these directly into answers.",
        "BreadcrumbList": "Site navigation hierarchy — helps AI understand content relationships.",
        "Product": "Product details — useful for commerce-related AI queries.",
        "LocalBusiness": "Physical location info — critical for local AI search results.",
        "Person": "Author/team info — strengthens E-E-A-T signals for AI.",
        "SoftwareApplication": "App/tool details — helps AI recommend our products.",
        "HowTo": "Step-by-step instructions — AI loves to cite these directly.",
        "VideoObject": "Video content metadata — YouTube correlation with AI citations is 0.737.",
    }
    return descriptions.get(schema_type, f"Tells AI this content is a {schema_type}.")


st.set_page_config(page_title="GEO/AEO Scores", page_icon="🎯", layout="wide")
st.markdown("# 🎯 GEO/AEO Readiness")
st.markdown("Is animocabrands.com set up for AI search engines to find, crawl, and cite our content?")
st.markdown("---")

# ─── Live Checks ──────────────────────────────────────────

@st.cache_data(ttl=86400)
def check_robots_for_ai_crawlers(domain):
    """Fetch robots.txt and check AI crawler access."""
    import requests
    results = {}
    crawlers = {
        "GPTBot": {"owner": "OpenAI (ChatGPT)", "critical": True},
        "ClaudeBot": {"owner": "Anthropic (Claude)", "critical": True},
        "PerplexityBot": {"owner": "Perplexity AI", "critical": True},
        "Google-Extended": {"owner": "Google (Gemini/AI Overviews)", "critical": True},
        "Googlebot": {"owner": "Google Search", "critical": True},
        "Bingbot": {"owner": "Microsoft (Bing/Copilot)", "critical": False},
        "Bytespider": {"owner": "ByteDance (TikTok)", "critical": False},
    }
    try:
        resp = requests.get(f"https://{domain}/robots.txt", timeout=10)
        if resp.status_code == 200:
            robots_text = resp.text.lower()
            for bot, info in crawlers.items():
                bot_lower = bot.lower()
                # Check if explicitly disallowed
                blocked = False
                in_section = False
                for line in robots_text.split("\n"):
                    line = line.strip()
                    if line.startswith("user-agent:"):
                        agent = line.split(":", 1)[1].strip()
                        in_section = agent == "*" or bot_lower in agent
                    elif in_section and line.startswith("disallow:"):
                        path = line.split(":", 1)[1].strip()
                        if path == "/" or path == "/*":
                            blocked = True
                            break

                results[bot] = {
                    "owner": info["owner"],
                    "critical": info["critical"],
                    "status": "Blocked" if blocked else "Allowed",
                    "impact": "AI cannot crawl or cite our content" if blocked else "AI can access our content",
                }
            return {"success": True, "crawlers": results, "robots_url": f"https://{domain}/robots.txt"}
        else:
            return {"success": False, "error": f"robots.txt returned status {resp.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@st.cache_data(ttl=86400)
def check_llms_txt(domain):
    """Check if llms.txt exists and what it contains."""
    import requests
    try:
        resp = requests.get(f"https://{domain}/llms.txt", timeout=10)
        if resp.status_code == 200:
            content = resp.text
            lines = [l for l in content.split("\n") if l.strip()]
            return {
                "exists": True,
                "url": f"https://{domain}/llms.txt",
                "lines": len(lines),
                "preview": content[:1000],
            }
        return {"exists": False, "status": resp.status_code}
    except Exception as e:
        return {"exists": False, "error": str(e)}


@st.cache_data(ttl=86400)
def check_structured_data(domain):
    """Check homepage for JSON-LD structured data."""
    import requests
    from bs4 import BeautifulSoup
    try:
        resp = requests.get(f"https://{domain}", timeout=15, headers={
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
                else:
                    schemas.append(data.get("@type", "Unknown"))
            except (json.JSONDecodeError, TypeError):
                pass
        return {
            "found": len(schemas) > 0,
            "count": len(schemas),
            "types": schemas,
        }
    except Exception as e:
        return {"found": False, "error": str(e)}


@st.cache_data(ttl=86400)
def check_page_basics(domain):
    """Check basic SEO elements on homepage."""
    import requests
    from bs4 import BeautifulSoup
    try:
        resp = requests.get(f"https://{domain}", timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.find("title")
        desc = soup.find("meta", attrs={"name": "description"})
        canonical = soup.find("link", attrs={"rel": "canonical"})
        h1s = soup.find_all("h1")
        og_title = soup.find("meta", attrs={"property": "og:title"})
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        return {
            "title": title.text.strip() if title else None,
            "description": desc["content"] if desc and desc.get("content") else None,
            "canonical": canonical["href"] if canonical and canonical.get("href") else None,
            "h1_count": len(h1s),
            "h1_text": h1s[0].text.strip() if h1s else None,
            "has_og": bool(og_title),
            "has_og_desc": bool(og_desc),
            "ssr": len(soup.find_all("div")) > 10,
        }
    except Exception as e:
        return {"error": str(e)}


domain = "animocabrands.com"

# Run all checks
with st.spinner("Running live AEO checks on animocabrands.com..."):
    robots_result = check_robots_for_ai_crawlers(domain)
    llms_result = check_llms_txt(domain)
    schema_result = check_structured_data(domain)
    page_result = check_page_basics(domain)

# ─── Overall Score ─────────────────────────────────────────

# Calculate a quick AEO readiness score
score = 0
max_score = 0
score_details = []

# Crawler access (30 points)
if robots_result.get("success"):
    crawlers = robots_result.get("crawlers", {})
    critical_crawlers = {k: v for k, v in crawlers.items() if v.get("critical")}
    allowed = sum(1 for v in critical_crawlers.values() if v["status"] == "Allowed")
    total_critical = len(critical_crawlers)
    crawler_score = round(allowed / total_critical * 30) if total_critical > 0 else 0
    score += crawler_score
    max_score += 30
    score_details.append(f"Crawler access: {crawler_score}/30 ({allowed}/{total_critical} critical crawlers allowed)")

# llms.txt (10 points)
if llms_result.get("exists"):
    score += 10
    score_details.append("llms.txt: 10/10 (found)")
else:
    score_details.append("llms.txt: 0/10 (not found)")
max_score += 10

# Structured data (20 points)
if schema_result.get("found"):
    schema_score = min(20, schema_result["count"] * 5)
    score += schema_score
    score_details.append(f"Structured data: {schema_score}/20 ({schema_result['count']} schemas found)")
else:
    score_details.append("Structured data: 0/20 (none found)")
max_score += 20

# Page basics (20 points)
if not page_result.get("error"):
    basics_score = 0
    if page_result.get("title"): basics_score += 5
    if page_result.get("description"): basics_score += 5
    if page_result.get("has_og"): basics_score += 5
    if page_result.get("ssr"): basics_score += 5
    score += basics_score
    score_details.append(f"Page fundamentals: {basics_score}/20")
max_score += 20

total_pct = round(score / max_score * 100) if max_score > 0 else 0

# Score gauge
st.markdown("### AEO Readiness Score")

col_score, col_details = st.columns([1, 2])

with col_score:
    color = COLORS["success"] if total_pct >= 70 else COLORS["warning"] if total_pct >= 40 else COLORS["danger"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total_pct,
        title={"text": "AEO Readiness"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 40], "color": "#ffcccc"},
                {"range": [40, 70], "color": "#fff3cd"},
                {"range": [70, 100], "color": "#d4edda"},
            ],
        },
        number={"suffix": "%"},
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_details:
    if total_pct >= 70:
        st.success(f"**Score: {total_pct}%** — Strong AEO readiness. Focus on content optimization and brand presence to maximize AI citations.")
    elif total_pct >= 40:
        st.warning(f"**Score: {total_pct}%** — Moderate readiness. Key gaps need attention before AI engines will reliably cite us.")
    else:
        st.error(f"**Score: {total_pct}%** — Significant gaps. AI engines likely cannot access or properly understand our content.")

    st.markdown("**Score Breakdown:**")
    for detail in score_details:
        st.markdown(f"- {detail}")

st.markdown("---")

# ─── AI Crawler Access (with real data) ───────────────────

st.markdown("### AI Crawler Access")
st.markdown("Can AI engines crawl our site? If blocked in robots.txt, they can't cite us.")

if robots_result.get("success"):
    crawlers = robots_result["crawlers"]
    crawler_rows = []
    for bot, info in crawlers.items():
        status_emoji = "Allowed" if info["status"] == "Allowed" else "BLOCKED"
        crawler_rows.append({
            "Crawler": bot,
            "Platform": info["owner"],
            "Access": status_emoji,
            "Critical": "Yes" if info["critical"] else "No",
            "What This Means": info["impact"],
        })

    cdf = pd.DataFrame(crawler_rows)

    def style_access(val):
        if val == "Allowed":
            return "background-color: #d4edda; color: #155724"
        elif val == "BLOCKED":
            return "background-color: #f8d7da; color: #721c24"
        return ""

    st.dataframe(
        cdf.style.applymap(style_access, subset=["Access"]),
        use_container_width=True, hide_index=True,
    )

    blocked = [bot for bot, info in crawlers.items() if info["status"] == "Blocked" and info["critical"]]
    if blocked:
        st.error(
            f"**Action Required:** {', '.join(blocked)} {'is' if len(blocked) == 1 else 'are'} blocked. "
            f"Update robots.txt to allow these crawlers, otherwise "
            f"{'this AI platform' if len(blocked) == 1 else 'these AI platforms'} cannot index or cite our content."
        )
    else:
        st.success("All critical AI crawlers are allowed — our content is accessible to AI engines.")
else:
    st.error(f"Could not check robots.txt: {robots_result.get('error', 'Unknown error')}")

st.markdown("---")

# ─── llms.txt Status ──────────────────────────────────────

st.markdown("### llms.txt File")
st.markdown("A guide for AI crawlers — tells them what our site is about and which pages matter most.")

if llms_result.get("exists"):
    st.success(f"**Found** at `{llms_result['url']}` — {llms_result['lines']} lines")
    st.markdown("**Why this helps:** AI crawlers use llms.txt to understand site structure and prioritize pages, similar to how sitemap.xml helps Google.")
    with st.expander("View llms.txt content"):
        st.code(llms_result["preview"])
else:
    st.warning(
        "**Not found.** Creating an llms.txt file gives AI crawlers explicit guidance about our site.\n\n"
        "**Impact:** Without it, AI crawlers guess which pages matter. With it, we control the narrative.\n\n"
        "**How to create:** Run `/geo llmstxt animocabrands.com` in Claude Code to auto-generate one."
    )

st.markdown("---")

# ─── Structured Data ──────────────────────────────────────

st.markdown("### Structured Data (Schema Markup)")
st.markdown("JSON-LD structured data helps AI engines understand *what* our content is about — not just the text, but the meaning.")

if schema_result.get("found"):
    st.success(f"**{schema_result['count']} schema type(s) found** on the homepage.")

    schema_df = pd.DataFrame([{"Schema Type": t, "What It Tells AI": _schema_description(t)} for t in schema_result["types"]])
    st.dataframe(schema_df, use_container_width=True, hide_index=True)

    # Check for missing important schemas
    found_types = [t.lower() for t in schema_result["types"]]
    recommended = {
        "Organization": "Who we are as a company — name, logo, social profiles, founding info",
        "WebSite": "Site-level info with search action — helps AI understand site scope",
        "FAQPage": "Question-answer content that AI engines love to cite directly",
        "Article": "Blog/news content with author, date, publisher info",
        "BreadcrumbList": "Site hierarchy — helps AI understand content relationships",
    }
    missing = {k: v for k, v in recommended.items() if k.lower() not in found_types}

    if missing:
        st.markdown("**Recommended schemas to add:**")
        for schema, desc in missing.items():
            st.markdown(f"- **{schema}** — {desc}")
else:
    st.error(
        "**No structured data found on the homepage.** This is a significant gap.\n\n"
        "Without schema markup, AI engines rely purely on text parsing to understand our content. "
        "Adding JSON-LD structured data makes our content machine-readable and dramatically increases "
        "the chance of being cited.\n\n"
        "**Priority schemas to add:**\n"
        "- **Organization** — Company identity\n"
        "- **WebSite** — Site scope and search\n"
        "- **FAQPage** — Q&A content for direct citations\n\n"
        "Run `/geo schema animocabrands.com` to generate these automatically."
    )

st.markdown("---")

# ─── Page Fundamentals ────────────────────────────────────

st.markdown("### Homepage Fundamentals")

if not page_result.get("error"):
    checks = [
        {"Check": "Page Title", "Status": "Found" if page_result.get("title") else "Missing",
         "Value": page_result.get("title", "—")[:80],
         "Why It Matters": "First thing AI sees — used in citations and summaries"},
        {"Check": "Meta Description", "Status": "Found" if page_result.get("description") else "Missing",
         "Value": (page_result.get("description", "—") or "—")[:100],
         "Why It Matters": "AI uses this as a summary when deciding to cite"},
        {"Check": "H1 Tag", "Status": "Found" if page_result.get("h1_text") else "Missing",
         "Value": (page_result.get("h1_text", "—") or "—")[:80],
         "Why It Matters": "Primary heading — AI weights this heavily for topic understanding"},
        {"Check": "Open Graph Tags", "Status": "Found" if page_result.get("has_og") else "Missing",
         "Value": "Present" if page_result.get("has_og") else "Missing",
         "Why It Matters": "Used by social platforms and some AI engines for content previews"},
        {"Check": "Server-Side Rendering", "Status": "Likely Yes" if page_result.get("ssr") else "Possibly No",
         "Value": "Content visible in HTML" if page_result.get("ssr") else "May require JavaScript",
         "Why It Matters": "AI crawlers don't execute JavaScript — SSR is critical"},
    ]

    checks_df = pd.DataFrame(checks)

    def style_status(val):
        if val in ["Found", "Likely Yes"]:
            return "background-color: #d4edda; color: #155724"
        elif val in ["Missing", "Possibly No"]:
            return "background-color: #f8d7da; color: #721c24"
        return ""

    st.dataframe(
        checks_df.style.applymap(style_status, subset=["Status"]),
        use_container_width=True, hide_index=True,
    )

    missing_items = [c for c in checks if c["Status"] in ["Missing", "Possibly No"]]
    if missing_items:
        st.warning(f"**{len(missing_items)} issue(s) found** — fixing these improves how AI engines understand and cite our content.")
    else:
        st.success("All homepage fundamentals are in place.")
else:
    st.error(f"Could not analyze homepage: {page_result.get('error')}")

st.markdown("---")

# ─── Priority Actions ─────────────────────────────────────

st.markdown("### Top Priority Actions")

priorities = []

if robots_result.get("success"):
    blocked_crawlers = [bot for bot, info in robots_result.get("crawlers", {}).items()
                       if info["status"] == "Blocked" and info["critical"]]
    if blocked_crawlers:
        priorities.append(("CRITICAL", f"Unblock {', '.join(blocked_crawlers)} in robots.txt — AI engines cannot see our site"))

if not schema_result.get("found"):
    priorities.append(("HIGH", "Add JSON-LD structured data to homepage — Organization, WebSite, FAQPage schemas"))

if not llms_result.get("exists"):
    priorities.append(("MEDIUM", "Create llms.txt file to guide AI crawlers"))

if page_result.get("error") or not page_result.get("description"):
    priorities.append(("HIGH", "Add/fix meta description on homepage"))

if not page_result.get("ssr"):
    priorities.append(("HIGH", "Ensure server-side rendering — AI crawlers can't execute JavaScript"))

if not priorities:
    st.success("No critical issues found. Focus on content quality and brand presence for maximum AI visibility.")
else:
    for level, action in priorities:
        if level == "CRITICAL":
            st.error(f"**{level}:** {action}")
        elif level == "HIGH":
            st.warning(f"**{level}:** {action}")
        else:
            st.info(f"**{level}:** {action}")

st.markdown("---")
st.caption(f"Live checks on {domain} · Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M')} · Refreshes daily")
