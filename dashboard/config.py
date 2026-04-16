"""
Dashboard configuration for Animoca Brands AEO Performance Dashboard.
Centralizes property IDs, OKR targets, baseline data, key dates, and branding.
"""

from datetime import date

# ─── Data Sources ──────────────────────────────────────────

GA4_PROPERTY_ID = "520518732"
GSC_SITE_URL = "sc-domain:animocabrands.com"

# GA4 tracking start date
GA4_START_DATE = "2026-01-25"
# Default data range
DEFAULT_START_DATE = "2026-01-25"
DEFAULT_END_DATE = "2026-04-07"

# ─── Branding ──────────────────────────────────────────────

BRAND_NAME = "Animoca Brands"
DASHBOARD_TITLE = "AEO Performance Dashboard"
SITE_URL = "https://www.animocabrands.com"

COLORS = {
    "primary": "#1a1a2e",
    "secondary": "#16213e",
    "accent": "#0f3460",
    "highlight": "#e94560",
    "success": "#00b894",
    "warning": "#fdcb6e",
    "danger": "#d63031",
    "info": "#0984e3",
    "ai_purple": "#6c5ce7",
    "ai_gradient": ["#6c5ce7", "#0984e3", "#00b894", "#fdcb6e", "#e94560", "#fd79a8"],
}

# ─── AI Referrers ──────────────────────────────────────────

AI_REFERRERS = {
    "chatgpt.com": "ChatGPT",
    "chat.openai.com": "ChatGPT",
    "openai.com": "ChatGPT",
    "gemini.google.com": "Gemini",
    "claude.ai": "Claude",
    "perplexity.ai": "Perplexity",
    "copilot.microsoft.com": "Copilot",
    "meta.ai": "Meta AI",
}

# Patterns for matching (used in ga4_fetcher)
AI_SOURCE_PATTERNS = [
    "chatgpt", "chat.openai", "openai",
    "perplexity",
    "claude", "anthropic",
    "gemini", "bard", "google-ai",
    "copilot", "bing-chat",
    "meta.ai",
    "you.com", "phind", "kagi",
]

AI_SOURCE_LABELS = {
    "chatgpt": "ChatGPT",
    "chat.openai": "ChatGPT",
    "openai": "ChatGPT",
    "perplexity": "Perplexity",
    "claude": "Claude",
    "anthropic": "Claude",
    "gemini": "Gemini",
    "bard": "Gemini",
    "google-ai": "Gemini",
    "copilot": "Copilot",
    "bing-chat": "Copilot",
    "meta.ai": "Meta AI",
    "you.com": "You.com",
    "phind": "Phind",
    "kagi": "Kagi",
}

# ─── Q2 OKR Targets ───────────────────────────────────────

OKR_TARGETS = {
    "sessions_baseline_feb": 27859,
    "sessions_target_q2": 33430,  # +20%
    "sessions_target_pct": 20,
    "bounce_baseline_feb": 69.5,
    "bounce_target_q2": 62.6,  # -10%
    "bounce_target_pct": -10,
    "users_baseline_feb": 23935,
    "pageviews_baseline_feb": 39576,
    "gsc_clicks_baseline_feb": 6527,
    "ai_traffic_share_target": 2.0,  # 2% target
}

# ─── Organic Baseline (Feb 22-28) ─────────────────────────

ORGANIC_BASELINE = {
    "week": "Feb 22–28",
    "sessions": 4293,
    "users": 3766,
    "bounce_rate": 64.4,
    "engagement_rate": 35.6,
    "avg_duration_seconds": 127,  # 2:07
    "direct": 2156,
    "direct_pct": 50.0,
    "organic_search": 1695,
    "organic_search_pct": 40.0,
    "referral": 250,
    "organic_social": 97,
    "gsc_clicks": 1321,
    "gsc_impressions": 129593,
    "gsc_avg_position": 8.2,
    "gsc_ctr": 1.0,
}

# ─── Key Dates for Annotations ────────────────────────────

KEY_EVENTS = [
    {"date": "2026-02-08", "event": "Email campaign start", "type": "campaign"},
    {"date": "2026-02-15", "event": "Email campaign peak (3,360 email sessions)", "type": "campaign"},
    {"date": "2026-03-15", "event": "Animoca Minds launch", "type": "product"},
    {"date": "2026-03-16", "event": "Ava Labs partnership announced", "type": "partnership"},
    {"date": "2026-03-22", "event": "Singapore campaign spike", "type": "campaign"},
    {"date": "2026-03-26", "event": "Traffic spike (1,457 sessions)", "type": "spike"},
]

# ─── Branded Queries to Always Track ──────────────────────

TRACKED_BRANDED_QUERIES = [
    "animoca brands", "animoca", "animoca minds", "animoca brands careers",
    "animoca brands limited", "animoca brand", "anchorpoint", "animocabrands",
    "animoca brands hong kong", "anchorpoint financial limited",
    "animoca brands portfolio", "animoca research", "animoca brands ipo",
    "anchorpoint stablecoin", "animoca labs", "animoca brands jobs",
    "animoca brands news", "animoca brands games", "animocaminds",
    "animoca minds ai", "animoca capital", "animoca brands stock",
]

# ─── Key Pages to Track ───────────────────────────────────

KEY_GSC_PAGES = {
    "/": "Homepage",
    "/leadership": "Team page",
    "/newsroom": "News hub",
    "/animoca-minds-launch": "Product launch",
    "/anchorpoint-stablecoin": "Product page",
    "/contact": "Contact page",
    "/currenc-group-term-sheet": "IR/deals",
    "/investors-relations": "Investor relations",
    "/our-portfolio": "Portfolio",
    "/ava-labs-partnership": "Partnership",
    "/sandbox-mobile-playtest": "Game content",
}

KEY_GA4_PAGES = [
    "/", "/newsroom", "/who-we-are", "/leadership", "/investment-overview",
    "/our-projects/consumer-business", "/our-portfolio", "/investment-portfolio",
    "/investors-relations", "/ava-labs-partnership", "/institutional-business",
    "/contact", "/digital-asset-services", "/animoca-minds-launch", "/careers",
]

# ─── Week Definitions (Sun-Sat) ───────────────────────────

WEEKS = [
    {"label": "Jan 25–31", "start": "2026-01-25", "end": "2026-01-31"},
    {"label": "Feb 1–7", "start": "2026-02-01", "end": "2026-02-07"},
    {"label": "Feb 8–14", "start": "2026-02-08", "end": "2026-02-14"},
    {"label": "Feb 15–21", "start": "2026-02-15", "end": "2026-02-21"},
    {"label": "Feb 22–28", "start": "2026-02-22", "end": "2026-02-28"},
    {"label": "Mar 1–7", "start": "2026-03-01", "end": "2026-03-07"},
    {"label": "Mar 8–14", "start": "2026-03-08", "end": "2026-03-14"},
    {"label": "Mar 15–21", "start": "2026-03-15", "end": "2026-03-21"},
    {"label": "Mar 22–28", "start": "2026-03-22", "end": "2026-03-28"},
    {"label": "Apr 1–7", "start": "2026-04-01", "end": "2026-04-07"},
]

# ─── Channel Definitions ──────────────────────────────────

CHANNEL_ORDER = [
    "Direct", "Organic Search", "Referral", "Organic Social",
    "Organic Video", "Email", "Unassigned",
]

CHANNEL_COLORS = {
    "Direct": "#636e72",
    "Organic Search": "#00b894",
    "Referral": "#0984e3",
    "Organic Social": "#6c5ce7",
    "Organic Video": "#e94560",
    "Email": "#fdcb6e",
    "Unassigned": "#dfe6e9",
}

# ─── Social Platforms ─────────────────────────────────────

SOCIAL_PLATFORMS = [
    "LinkedIn", "Instagram", "Facebook", "TikTok",
    "YouTube (Brands)", "YouTube (Minds)",
]

# Cache TTL
CACHE_TTL = 86400
DEFAULT_DAYS_BACK = 28
