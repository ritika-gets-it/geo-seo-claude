"""
Animoca Brands — AEO Performance Dashboard
Main entry point. Run with: streamlit run dashboard/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="AEO Dashboard — Animoca Brands",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1a1a2e; }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 { color: #ffffff; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Animoca Brands")
    st.markdown("# AEO Dashboard")
    st.markdown("---")
    st.markdown("""
    **Pages**
    1. Executive Summary
    2. Traffic & Channels
    3. Search & Content
    4. AI & AEO Tracking
    5. Insights, OKR & Social
    """)
    st.markdown("---")
    st.markdown("*Data: Jan 25 – Apr 7, 2026*")
    st.markdown("*Refreshes every 24 hours*")
    if st.button("🔄 Force Refresh"):
        st.cache_data.clear()
        st.rerun()

st.markdown("# AEO Performance Dashboard")
st.markdown("**Animoca Brands** — animocabrands.com")
st.markdown("---")
st.markdown("Select a page from the sidebar to get started.")
st.markdown("---")
st.caption("Data: Google Search Console + Google Analytics 4 | Period: Jan 25 – Apr 7, 2026")
