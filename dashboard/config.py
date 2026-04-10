"""
Dashboard configuration for Animoca Brands AEO Performance Dashboard.
Centralizes all property IDs, site URLs, branding, and settings.
"""

# Google Analytics 4
GA4_PROPERTY_ID = "520518732"

# Google Search Console
GSC_SITE_URL = "sc-domain:animocabrands.com"

# Branding
BRAND_NAME = "Animoca Brands"
DASHBOARD_TITLE = "AEO Performance Dashboard"
SITE_URL = "https://www.animocabrands.com"

# Color palette (matching existing PDF report branding)
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
    "ai_gradient": ["#6c5ce7", "#0984e3", "#00b894", "#fdcb6e", "#e94560"],
}

# AI referral source display names
AI_SOURCE_LABELS = {
    "chatgpt": "ChatGPT",
    "chat.openai": "ChatGPT",
    "openai": "OpenAI",
    "perplexity": "Perplexity",
    "claude": "Claude",
    "anthropic": "Anthropic",
    "gemini": "Gemini",
    "bard": "Bard",
    "google-ai": "Google AI",
    "copilot": "Copilot",
    "bing-chat": "Bing Chat",
    "you.com": "You.com",
    "phind": "Phind",
    "kagi": "Kagi",
}

# Cache TTL in seconds (24 hours)
CACHE_TTL = 86400

# Default date range (days back from today)
DEFAULT_DAYS_BACK = 28
