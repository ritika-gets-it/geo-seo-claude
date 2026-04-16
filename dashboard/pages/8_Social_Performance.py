"""
Page 8: Social Performance
Platform-level social media tracking. Placeholder for Agorapulse integration.
"""

import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SOCIAL_PLATFORMS, COLORS

st.set_page_config(page_title="Social Performance", page_icon="📱", layout="wide")
st.markdown("# 📱 Social Performance")
st.markdown("Monthly social media tracking across 6 platforms.")
st.markdown("---")

# ─── Monthly Social Table ────────────────────────────────

st.markdown("### Monthly Social Media Metrics")
st.markdown("*Data to be populated from Agorapulse or manual entry.*")

months = ["Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026"]
selected_month = st.selectbox("Month", months, index=len(months) - 1)

social_data = []
for platform in SOCIAL_PLATFORMS:
    social_data.append({
        "Platform": platform,
        "Followers": "—",
        "Net New": "—",
        "Reach": "—",
        "Engagement %": "—",
        "Posts": "—",
    })

st.dataframe(pd.DataFrame(social_data), use_container_width=True, hide_index=True)

st.markdown("---")

# ─── Agorapulse Integration ──────────────────────────────

st.markdown("### Agorapulse Integration")

st.info("""
**To connect Agorapulse and auto-populate social data:**

1. Log into [Agorapulse](https://app.agorapulse.com)
2. Go to **Settings > API** (or ask your account admin)
3. Generate an API key
4. Share the API key and we'll connect it to this dashboard

**What Agorapulse can provide:**
- Follower counts and growth per platform
- Post reach and impressions
- Engagement rate
- Publishing schedule and post count
- Best performing content

Currently this page uses manual entry. Once Agorapulse API credentials are provided,
data will auto-populate daily.
""")

st.markdown("---")

# ─── Manual Entry Section ────────────────────────────────

st.markdown("### Quick Entry (Manual)")
st.markdown("*Enter latest social stats if Agorapulse isn't connected yet:*")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**LinkedIn**")
    li_followers = st.number_input("Followers", min_value=0, value=0, key="li_f")
    li_engagement = st.number_input("Engagement %", min_value=0.0, value=0.0, step=0.1, key="li_e")

    st.markdown("**Instagram**")
    ig_followers = st.number_input("Followers", min_value=0, value=0, key="ig_f")
    ig_engagement = st.number_input("Engagement %", min_value=0.0, value=0.0, step=0.1, key="ig_e")

    st.markdown("**Facebook**")
    fb_followers = st.number_input("Followers", min_value=0, value=0, key="fb_f")
    fb_engagement = st.number_input("Engagement %", min_value=0.0, value=0.0, step=0.1, key="fb_e")

with col2:
    st.markdown("**TikTok**")
    tt_followers = st.number_input("Followers", min_value=0, value=0, key="tt_f")
    tt_engagement = st.number_input("Engagement %", min_value=0.0, value=0.0, step=0.1, key="tt_e")

    st.markdown("**YouTube (Brands)**")
    yt_followers = st.number_input("Subscribers", min_value=0, value=0, key="yt_f")
    yt_engagement = st.number_input("Engagement %", min_value=0.0, value=0.0, step=0.1, key="yt_e")

    st.markdown("**YouTube (Minds)**")
    ytm_followers = st.number_input("Subscribers", min_value=0, value=0, key="ytm_f")
    ytm_engagement = st.number_input("Engagement %", min_value=0.0, value=0.0, step=0.1, key="ytm_e")

st.info("Manual entries are session-based. For persistent tracking, connect Agorapulse or export to a spreadsheet.")

st.markdown("---")
st.caption("Social data: Manual entry / Agorapulse (when connected)")
