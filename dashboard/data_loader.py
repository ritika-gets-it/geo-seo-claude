"""
Centralized data loading with Streamlit caching.
All data fetching goes through here to ensure 24-hour cache TTL.
"""

import sys
import os
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd

# Add scripts directory to path
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from config import GA4_PROPERTY_ID, GSC_SITE_URL, CACHE_TTL, DEFAULT_DAYS_BACK


def _default_dates(days_back=None):
    if days_back is None:
        days_back = DEFAULT_DAYS_BACK
    end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    return start, end


# ─── GSC Data ───────────────────────────────────────────────


@st.cache_data(ttl=CACHE_TTL)
def load_gsc_top_queries(start_date=None, end_date=None, limit=25):
    from gsc_fetcher import get_top_queries
    if not start_date:
        start_date, end_date = _default_dates()
    return get_top_queries(GSC_SITE_URL, limit=limit, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=CACHE_TTL)
def load_gsc_top_pages(start_date=None, end_date=None, limit=25):
    from gsc_fetcher import get_top_pages
    if not start_date:
        start_date, end_date = _default_dates()
    return get_top_pages(GSC_SITE_URL, limit=limit, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=CACHE_TTL)
def load_gsc_daily_trend(start_date=None, end_date=None):
    from gsc_fetcher import get_performance_by_date
    if not start_date:
        start_date, end_date = _default_dates()
    return get_performance_by_date(GSC_SITE_URL, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=CACHE_TTL)
def load_gsc_devices(start_date=None, end_date=None):
    from gsc_fetcher import get_device_breakdown
    if not start_date:
        start_date, end_date = _default_dates()
    return get_device_breakdown(GSC_SITE_URL, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=CACHE_TTL)
def load_gsc_countries(start_date=None, end_date=None, limit=25):
    from gsc_fetcher import get_country_breakdown
    if not start_date:
        start_date, end_date = _default_dates()
    return get_country_breakdown(GSC_SITE_URL, limit=limit, start_date=start_date, end_date=end_date)


# ─── GA4 Data ───────────────────────────────────────────────


@st.cache_data(ttl=CACHE_TTL)
def load_ga4_traffic_overview(start_date=None, end_date=None):
    from ga4_fetcher import get_traffic_overview
    if not start_date:
        start_date, end_date = _default_dates()
    return get_traffic_overview(GA4_PROPERTY_ID, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=CACHE_TTL)
def load_ga4_top_pages(start_date=None, end_date=None, limit=25):
    from ga4_fetcher import get_top_pages
    if not start_date:
        start_date, end_date = _default_dates()
    return get_top_pages(GA4_PROPERTY_ID, limit=limit, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=CACHE_TTL)
def load_ga4_traffic_sources(start_date=None, end_date=None, limit=25):
    from ga4_fetcher import get_traffic_sources
    if not start_date:
        start_date, end_date = _default_dates()
    return get_traffic_sources(GA4_PROPERTY_ID, limit=limit, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=CACHE_TTL)
def load_ga4_ai_traffic(start_date=None, end_date=None):
    from ga4_fetcher import get_ai_referral_traffic
    if not start_date:
        start_date, end_date = _default_dates()
    return get_ai_referral_traffic(GA4_PROPERTY_ID, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=CACHE_TTL)
def load_ga4_landing_pages(start_date=None, end_date=None, limit=25):
    from ga4_fetcher import get_landing_pages
    if not start_date:
        start_date, end_date = _default_dates()
    return get_landing_pages(GA4_PROPERTY_ID, limit=limit, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=CACHE_TTL)
def load_ga4_devices(start_date=None, end_date=None):
    from ga4_fetcher import get_device_breakdown
    if not start_date:
        start_date, end_date = _default_dates()
    return get_device_breakdown(GA4_PROPERTY_ID, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=CACHE_TTL)
def load_ga4_geo(start_date=None, end_date=None, limit=25):
    from ga4_fetcher import get_geo_breakdown
    if not start_date:
        start_date, end_date = _default_dates()
    return get_geo_breakdown(GA4_PROPERTY_ID, limit=limit, start_date=start_date, end_date=end_date)


@st.cache_data(ttl=CACHE_TTL)
def load_ga4_engagement(start_date=None, end_date=None):
    from ga4_fetcher import get_engagement_metrics
    if not start_date:
        start_date, end_date = _default_dates()
    return get_engagement_metrics(GA4_PROPERTY_ID, start_date=start_date, end_date=end_date)


# ─── DataFrame Helpers ──────────────────────────────────────


def gsc_rows_to_df(data):
    """Convert GSC response rows to a pandas DataFrame."""
    rows = data.get("rows", [])
    if not rows:
        return pd.DataFrame()
    records = []
    for row in rows:
        record = {}
        keys = row.get("keys", [])
        dims = data.get("dimensions", ["query"])
        for i, dim in enumerate(dims):
            record[dim] = keys[i] if i < len(keys) else ""
        record["clicks"] = row.get("clicks", 0)
        record["impressions"] = row.get("impressions", 0)
        record["ctr"] = row.get("ctr", 0)
        record["position"] = row.get("position", 0)
        records.append(record)
    return pd.DataFrame(records)


def ga4_rows_to_df(data):
    """Convert GA4 response rows to a pandas DataFrame."""
    rows = data.get("rows", [])
    if not rows:
        return pd.DataFrame()
    records = []
    for row in rows:
        record = {}
        record.update(row.get("dimensions", {}))
        record.update(row.get("metrics", {}))
        records.append(record)
    return pd.DataFrame(records)
