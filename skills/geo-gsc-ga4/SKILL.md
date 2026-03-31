---
name: geo-gsc-ga4
description: Connect Google Search Console and GA4 to pull real search performance data, AI referral traffic, and engagement metrics for GEO analysis
version: 1.0.0
author: geo-seo-claude
tags: [geo, gsc, ga4, google-search-console, google-analytics, search-performance, ai-traffic]
---

# GSC & GA4 Data Integration

## Purpose

Connect real Google Search Console and Google Analytics 4 data into GEO analysis. This replaces heuristic-only analysis with actual performance metrics — real clicks, impressions, CTR, search positions, traffic sources, and critically, **AI referral traffic** from ChatGPT, Perplexity, Claude, and other AI platforms.

## Prerequisites — One-Time Setup

Before using this skill, the user must configure Google API credentials:

### Option 1: Service Account (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select existing)
3. Enable these APIs:
   - **Google Search Console API** (`searchconsole.googleapis.com`)
   - **Google Analytics Data API** (`analyticsdata.googleapis.com`)
4. Create a Service Account (IAM & Admin > Service Accounts)
5. Download the JSON key file
6. Place it at: `~/.claude/google/service-account.json`
7. In GSC: Add the service account email as a **verified user** for your property
8. In GA4: Add the service account email as a **Viewer** under Admin > Property Access Management

### Option 2: OAuth2 (Personal Accounts)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the same APIs as above
3. Create OAuth 2.0 Client ID (APIs & Services > Credentials > Create Credentials)
4. Choose "Desktop app" as application type
5. Download the client secrets JSON
6. Place it at: `~/.claude/google/client-secrets.json`
7. On first run, a browser window will open for authorization

### Check Setup Status

Run: `python3 scripts/google_auth.py`

This outputs a JSON status showing which credential files are found.

---

## How to Use This Skill

### Commands

| Command | What It Does |
|---------|-------------|
| `/geo gsc <site_url>` | Pull GSC search performance summary |
| `/geo ga4 <property_id>` | Pull GA4 traffic and engagement summary |
| `/geo ai-traffic <property_id>` | Identify AI referral traffic (ChatGPT, Perplexity, etc.) |
| `/geo connect-status` | Check if Google API credentials are configured |

### GSC Site URL Format

- Domain property: `sc-domain:example.com`
- URL-prefix property: `https://example.com/`

### GA4 Property ID

- Find in GA4: Admin > Property Details > Property ID (numeric, e.g., `123456789`)

---

## Execution Steps

### `/geo gsc <site_url>` — Search Console Data

1. Check auth setup: `python3 scripts/google_auth.py`
2. If not configured, output the setup instructions above and stop
3. Fetch GSC summary: `python3 scripts/gsc_fetcher.py <site_url> summary`
4. Parse the JSON output
5. Present findings in this format:

```markdown
## Google Search Console — [site_url]
**Period:** [start_date] to [end_date]

### Performance Summary
| Metric | Value |
|--------|-------|
| Total Clicks | X |
| Total Impressions | X |
| Average CTR | X% |
| Average Position | X |

### Top 10 Queries by Clicks
| Query | Clicks | Impressions | CTR | Position |
|-------|--------|-------------|-----|----------|
| ... | ... | ... | ... | ... |

### Top 10 Pages by Clicks
| Page | Clicks | Impressions | CTR | Position |
|------|--------|-------------|-----|----------|
| ... | ... | ... | ... | ... |

### Device Breakdown
| Device | Sessions | % Share |
|--------|----------|---------|
| ... | ... | ... |

### GEO Insights
- [Analyze which queries could trigger AI citations]
- [Identify pages with high impressions but low CTR — AI overview candidates]
- [Flag branded vs non-branded query ratio]
```

### `/geo ga4 <property_id>` — Analytics Data

1. Check auth setup: `python3 scripts/google_auth.py`
2. If not configured, output the setup instructions above and stop
3. Fetch GA4 summary: `python3 scripts/ga4_fetcher.py <property_id> summary`
4. Parse the JSON output
5. Present findings in this format:

```markdown
## Google Analytics 4 — Property [property_id]
**Period:** [start_date] to [end_date]

### Traffic Overview
| Metric | Value |
|--------|-------|
| Total Sessions | X |
| Total Users | X |
| Page Views | X |
| Bounce Rate | X% |
| Avg Session Duration | Xs |

### Top Traffic Sources
| Source / Medium | Sessions | Users | Bounce Rate |
|----------------|----------|-------|-------------|
| ... | ... | ... | ... |

### AI Referral Traffic
| Source | Sessions | Users | Page Views | Bounce Rate |
|--------|----------|-------|------------|-------------|
| chatgpt.com | ... | ... | ... | ... |
| perplexity.ai | ... | ... | ... | ... |
| Total AI Traffic | **X** | **X** | | |

### Top Landing Pages
| Page | Sessions | Bounce Rate | Conversions |
|------|----------|-------------|-------------|
| ... | ... | ... | ... |

### GEO Insights
- [Compare AI vs organic traffic quality]
- [Identify which pages attract AI referrals]
- [Highlight engagement differences between AI and organic visitors]
```

### `/geo ai-traffic <property_id>` — AI Referral Deep Dive

1. Fetch AI referral data: `python3 scripts/ga4_fetcher.py <property_id> ai-traffic`
2. Present the AI-specific traffic analysis
3. Compare against total traffic to calculate AI traffic share
4. Provide GEO recommendations based on AI traffic patterns

### `/geo connect-status` — Setup Check

1. Run: `python3 scripts/google_auth.py`
2. Parse JSON output
3. Display clear status:

```markdown
## Google API Connection Status

| Component | Status |
|-----------|--------|
| Credentials Directory | ~/.claude/google/ |
| Service Account | ✅ Found / ❌ Not found |
| OAuth Client Secrets | ✅ Found / ❌ Not found |
| OAuth Token (cached) | ✅ Found / ❌ Not found |
| Ready to Use | ✅ Yes / ❌ No |
```

If not ready, display the full setup instructions.

---

## GEO-Specific Analysis

When presenting GSC/GA4 data, always include GEO-focused insights:

### From GSC Data
- **AI Overview Candidates**: Pages with position 1-5 and high impressions — likely appearing in AI overviews
- **Citation-Worthy Queries**: Question-format queries (how, what, why, best, vs) that AI engines prioritize
- **Content Gap Signals**: High-impression, low-CTR queries — users seeing but not clicking, possibly getting answers from AI overviews
- **Featured Snippet Queries**: Position 1 queries with unusually high CTR — already winning featured snippets

### From GA4 Data
- **AI Traffic Growth**: Compare AI referral sessions month-over-month
- **AI vs Organic Quality**: Compare bounce rate, session duration, pages/session between AI and organic traffic
- **AI Landing Pages**: Which pages attract AI referrals — these are being cited by AI engines
- **Conversion Impact**: How AI-referred traffic converts compared to organic

---

## Integration with Full Audit

When GSC/GA4 data is available, the `/geo audit` should incorporate real performance data:

1. **Citability Score Enhancement**: Cross-reference citability scores with actual AI referral data
2. **Content Priority**: Use GSC data to prioritize which pages to optimize for GEO
3. **ROI Tracking**: Show actual traffic impact of GEO optimizations over time
4. **Competitive Insights**: Use query data to identify GEO opportunities competitors are missing
