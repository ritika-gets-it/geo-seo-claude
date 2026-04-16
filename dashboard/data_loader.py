"""
Centralized data loading with Streamlit caching and weekly aggregation.
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

from config import GA4_PROPERTY_ID, GSC_SITE_URL, CACHE_TTL, WEEKS, AI_SOURCE_LABELS


# ═══════════════════════════════════════════════════════════
# GSC Data
# ═══════════════════════════════════════════════════════════

@st.cache_data(ttl=CACHE_TTL)
def load_gsc_top_queries(start_date, end_date, limit=25):
    from gsc_fetcher import get_top_queries
    return get_top_queries(GSC_SITE_URL, limit=limit, start_date=start_date, end_date=end_date)

@st.cache_data(ttl=CACHE_TTL)
def load_gsc_top_pages(start_date, end_date, limit=25):
    from gsc_fetcher import get_top_pages
    return get_top_pages(GSC_SITE_URL, limit=limit, start_date=start_date, end_date=end_date)

@st.cache_data(ttl=CACHE_TTL)
def load_gsc_daily_trend(start_date, end_date):
    from gsc_fetcher import get_performance_by_date
    return get_performance_by_date(GSC_SITE_URL, start_date=start_date, end_date=end_date)

@st.cache_data(ttl=CACHE_TTL)
def load_gsc_devices(start_date, end_date):
    from gsc_fetcher import get_device_breakdown
    return get_device_breakdown(GSC_SITE_URL, start_date=start_date, end_date=end_date)

@st.cache_data(ttl=CACHE_TTL)
def load_gsc_countries(start_date, end_date, limit=25):
    from gsc_fetcher import get_country_breakdown
    return get_country_breakdown(GSC_SITE_URL, limit=limit, start_date=start_date, end_date=end_date)


# ═══════════════════════════════════════════════════════════
# GA4 Data
# ═══════════════════════════════════════════════════════════

@st.cache_data(ttl=CACHE_TTL)
def load_ga4_traffic_overview(start_date, end_date):
    from ga4_fetcher import get_traffic_overview
    return get_traffic_overview(GA4_PROPERTY_ID, start_date=start_date, end_date=end_date)

@st.cache_data(ttl=CACHE_TTL)
def load_ga4_top_pages(start_date, end_date, limit=25):
    from ga4_fetcher import get_top_pages
    return get_top_pages(GA4_PROPERTY_ID, limit=limit, start_date=start_date, end_date=end_date)

@st.cache_data(ttl=CACHE_TTL)
def load_ga4_traffic_sources(start_date, end_date, limit=50):
    from ga4_fetcher import get_traffic_sources
    return get_traffic_sources(GA4_PROPERTY_ID, limit=limit, start_date=start_date, end_date=end_date)

@st.cache_data(ttl=CACHE_TTL)
def load_ga4_ai_traffic(start_date, end_date):
    from ga4_fetcher import get_ai_referral_traffic
    return get_ai_referral_traffic(GA4_PROPERTY_ID, start_date=start_date, end_date=end_date)

@st.cache_data(ttl=CACHE_TTL)
def load_ga4_landing_pages(start_date, end_date, limit=25):
    from ga4_fetcher import get_landing_pages
    return get_landing_pages(GA4_PROPERTY_ID, limit=limit, start_date=start_date, end_date=end_date)

@st.cache_data(ttl=CACHE_TTL)
def load_ga4_devices(start_date, end_date):
    from ga4_fetcher import get_device_breakdown
    return get_device_breakdown(GA4_PROPERTY_ID, start_date=start_date, end_date=end_date)

@st.cache_data(ttl=CACHE_TTL)
def load_ga4_geo(start_date, end_date, limit=25):
    from ga4_fetcher import get_geo_breakdown
    return get_geo_breakdown(GA4_PROPERTY_ID, limit=limit, start_date=start_date, end_date=end_date)

@st.cache_data(ttl=CACHE_TTL)
def load_ga4_engagement(start_date, end_date):
    from ga4_fetcher import get_engagement_metrics
    return get_engagement_metrics(GA4_PROPERTY_ID, start_date=start_date, end_date=end_date)


# ═══════════════════════════════════════════════════════════
# DataFrame Helpers
# ═══════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════
# Weekly Aggregation
# ═══════════════════════════════════════════════════════════

@st.cache_data(ttl=CACHE_TTL)
def load_weekly_ga4_summary():
    """Load GA4 data for each defined week and aggregate."""
    weekly_data = []
    for week in WEEKS:
        overview = load_ga4_traffic_overview(week["start"], week["end"])
        ai = load_ga4_ai_traffic(week["start"], week["end"])
        df = ga4_rows_to_df(overview)

        if df.empty:
            continue

        sessions = int(df["sessions"].sum())
        ai_sessions = ai.get("total_ai_sessions", 0)

        weekly_data.append({
            "week": week["label"],
            "start": week["start"],
            "end": week["end"],
            "sessions": sessions,
            "users": int(df["totalUsers"].sum()),
            "pageviews": int(df["screenPageViews"].sum()),
            "bounce_rate": round(df["bounceRate"].mean() * 100, 1),
            "engagement_rate": round((1 - df["bounceRate"].mean()) * 100, 1),
            "avg_duration": round(df["averageSessionDuration"].mean(), 0),
            "ai_sessions": ai_sessions,
            "ai_users": ai.get("total_ai_users", 0),
            "ai_share": round(ai_sessions / sessions * 100, 2) if sessions > 0 else 0,
        })

    df = pd.DataFrame(weekly_data)
    if not df.empty:
        # Calculate WoW changes
        for col in ["sessions", "users", "pageviews", "bounce_rate", "ai_sessions", "ai_share"]:
            df[f"{col}_wow"] = df[col].pct_change() * 100

    return df


@st.cache_data(ttl=CACHE_TTL)
def load_weekly_gsc_summary():
    """Load GSC data for each defined week and aggregate."""
    weekly_data = []
    for week in WEEKS:
        trend = load_gsc_daily_trend(week["start"], week["end"])
        df = gsc_rows_to_df(trend)

        if df.empty:
            continue

        weekly_data.append({
            "week": week["label"],
            "start": week["start"],
            "end": week["end"],
            "clicks": int(df["clicks"].sum()),
            "impressions": int(df["impressions"].sum()),
            "ctr": round(df["clicks"].sum() / df["impressions"].sum() * 100, 1) if df["impressions"].sum() > 0 else 0,
            "avg_position": round(df["position"].mean(), 1),
        })

    df = pd.DataFrame(weekly_data)
    if not df.empty:
        for col in ["clicks", "impressions", "ctr", "avg_position"]:
            df[f"{col}_wow"] = df[col].pct_change() * 100
    return df


@st.cache_data(ttl=CACHE_TTL)
def load_weekly_ai_breakdown():
    """Load AI referrer breakdown per week."""
    weekly_data = []
    for week in WEEKS:
        ai = load_ga4_ai_traffic(week["start"], week["end"])
        sources = ai.get("ai_referral_sources", [])
        ai_df = ga4_rows_to_df({"rows": sources})

        if ai_df.empty:
            weekly_data.append({"week": week["label"]})
            continue

        row = {"week": week["label"]}
        if "sessionSource" in ai_df.columns:
            for _, r in ai_df.iterrows():
                source = r["sessionSource"]
                label = next((v for k, v in AI_SOURCE_LABELS.items() if k in source.lower()), source)
                row[label] = row.get(label, 0) + int(r.get("sessions", 0))
        weekly_data.append(row)

    return pd.DataFrame(weekly_data).fillna(0)


@st.cache_data(ttl=CACHE_TTL)
def load_weekly_channel_breakdown():
    """Load channel breakdown per week."""
    from ga4_fetcher import _run_report

    weekly_data = []
    for week in WEEKS:
        data = _run_report(
            GA4_PROPERTY_ID,
            dimensions=["sessionDefaultChannelGroup"],
            metrics=["sessions", "bounceRate"],
            start_date=week["start"],
            end_date=week["end"],
            limit=20,
            order_by_metric="sessions",
        )
        df = ga4_rows_to_df(data)
        if df.empty:
            continue

        row = {"week": week["label"]}
        for _, r in df.iterrows():
            channel = r.get("sessionDefaultChannelGroup", "Other")
            row[channel] = int(r.get("sessions", 0))
        weekly_data.append(row)

    return pd.DataFrame(weekly_data).fillna(0)


@st.cache_data(ttl=CACHE_TTL)
def load_weekly_device_breakdown():
    """Load device breakdown per week."""
    weekly_data = []
    for week in WEEKS:
        data = load_ga4_devices(week["start"], week["end"])
        df = ga4_rows_to_df(data)
        if df.empty:
            continue
        row = {"week": week["label"]}
        for _, r in df.iterrows():
            device = r.get("deviceCategory", "Other")
            row[device] = int(r.get("sessions", 0))
        weekly_data.append(row)

    return pd.DataFrame(weekly_data).fillna(0)


@st.cache_data(ttl=CACHE_TTL)
def load_weekly_geo_breakdown():
    """Load geo breakdown per week."""
    weekly_data = []
    for week in WEEKS:
        data = load_ga4_geo(week["start"], week["end"], limit=15)
        df = ga4_rows_to_df(data)
        if df.empty:
            continue
        row = {"week": week["label"]}
        for _, r in df.iterrows():
            country = r.get("country", "Other")
            row[country] = int(r.get("sessions", 0))
        weekly_data.append(row)

    return pd.DataFrame(weekly_data).fillna(0)


# ═══════════════════════════════════════════════════════════
# Formatting Helpers
# ═══════════════════════════════════════════════════════════

def format_duration(seconds):
    """Format seconds as mm:ss."""
    if pd.isna(seconds) or seconds == 0:
        return "0:00"
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


def wow_delta(current, previous):
    """Calculate WoW % change."""
    if previous == 0:
        return None
    return round((current - previous) / previous * 100, 1)


def format_wow(value):
    """Format WoW change with arrow."""
    if value is None or pd.isna(value):
        return "—"
    arrow = "↑" if value > 0 else "↓" if value < 0 else "→"
    return f"{arrow} {abs(value):.1f}%"
