"""
Animoca Brands — AEO Performance Dashboard
Main entry point. Run with: streamlit run dashboard/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="AEO Performance Dashboard — Animoca Brands",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for branding
st.markdown("""
<style>
    /* Dark sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffffff;
    }
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    [data-testid="stMetricDelta"] > div {
        font-size: 0.9rem;
    }
    /* Card-like containers */
    .stContainer {
        border-radius: 8px;
    }
    /* Header */
    .dashboard-header {
        padding: 1rem 0;
        border-bottom: 2px solid #0f3460;
        margin-bottom: 1.5rem;
    }
    .dashboard-header h1 {
        color: #1a1a2e;
        margin: 0;
    }
    .dashboard-header p {
        color: #636e72;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Animoca Brands")
    st.markdown("# AEO Dashboard")
    st.markdown("---")
    st.markdown("""
    **Pages**
    - 📈 Executive Overview
    - 🔍 Search Performance
    - 🤖 AI Referral Traffic
    - 🌐 Traffic Sources
    - 🎯 GEO/AEO Scores
    """)
    st.markdown("---")
    st.markdown("*Data refreshes every 24 hours*")
    if st.button("🔄 Force Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# Main landing page
st.markdown("""
<div class="dashboard-header">
    <h1>AEO Performance Dashboard</h1>
    <p>Animoca Brands — AI Engine Optimization Performance Tracking</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
## Welcome

This dashboard tracks the impact of AEO (AI Engine Optimization) work on **animocabrands.com**.
Use the sidebar to navigate between pages, or select a page below.

### Quick Navigation

| Page | What It Shows |
|------|--------------|
| **📈 Executive Overview** | KPIs, traffic trends, AI traffic share |
| **🔍 Search Performance** | GSC queries, top pages, CTR, positions |
| **🤖 AI Referral Traffic** | Traffic from ChatGPT, Perplexity, Claude, Gemini |
| **🌐 Traffic Sources** | All traffic sources, landing pages, geography |
| **🎯 GEO/AEO Scores** | Citability scores, brand presence, crawler access |

### Why This Dashboard Exists

We're optimizing content for AI search engines. This dashboard answers:
- **Is AI traffic growing?** Track referrals from ChatGPT, Perplexity, Claude, Gemini
- **What content is AI citing?** See which pages attract AI referrals
- **Is AEO working?** Compare AI vs organic traffic quality
- **What should we optimize next?** Find high-impression, low-CTR opportunities
""")

st.markdown("---")
st.caption("Data sources: Google Search Console · Google Analytics 4 · Last refresh: auto (24h cache)")
