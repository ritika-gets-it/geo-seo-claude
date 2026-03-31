#!/usr/bin/env python3
"""
Google Analytics 4 data fetcher for GEO analysis.
Retrieves traffic, engagement, and conversion data via the GA4 Data API.
"""

import sys
import json
from datetime import datetime, timedelta

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest,
        Dimension,
        Metric,
        DateRange,
        OrderBy,
    )
except ImportError:
    print("ERROR: GA4 Data API package not installed. Run:")
    print("  pip install google-analytics-data google-auth")
    sys.exit(1)

from google_auth import get_credentials, GA4_SCOPES


def get_ga4_client():
    """Build and return the GA4 Data API client."""
    credentials = get_credentials(scopes=GA4_SCOPES)
    return BetaAnalyticsDataClient(credentials=credentials)


def _run_report(property_id, dimensions, metrics, start_date=None, end_date=None, limit=25, order_by_metric=None):
    """
    Run a GA4 report and return structured results.

    Args:
        property_id: GA4 property ID (numeric, e.g., "123456789")
        dimensions: List of dimension names (e.g., ["pagePath", "sessionSource"])
        metrics: List of metric names (e.g., ["sessions", "screenPageViews"])
        start_date: Start date (YYYY-MM-DD). Defaults to 28 days ago.
        end_date: End date (YYYY-MM-DD). Defaults to yesterday.
        limit: Max rows (default 25).
        order_by_metric: Metric name to sort by descending.

    Returns:
        dict with rows and metadata.
    """
    client = get_ga4_client()

    if not end_date:
        end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )

    if order_by_metric:
        request.order_bys = [
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_by_metric), desc=True)
        ]

    response = client.run_report(request)

    result = {
        "date_range": {"start": start_date, "end": end_date},
        "dimensions": dimensions,
        "metrics": metrics,
        "total_rows": response.row_count,
        "rows": [],
    }

    for row in response.rows:
        entry = {
            "dimensions": {
                dimensions[i]: val.value for i, val in enumerate(row.dimension_values)
            },
            "metrics": {
                metrics[i]: _parse_metric_value(val.value) for i, val in enumerate(row.metric_values)
            },
        }
        result["rows"].append(entry)

    # Include totals if available
    if response.totals:
        for total_row in response.totals:
            result["totals"] = {
                metrics[i]: _parse_metric_value(val.value)
                for i, val in enumerate(total_row.metric_values)
            }

    return result


def _parse_metric_value(value):
    """Parse a GA4 metric value string into int or float."""
    try:
        if "." in value:
            return round(float(value), 2)
        return int(value)
    except (ValueError, TypeError):
        return value


def get_traffic_overview(property_id, start_date=None, end_date=None):
    """Get overall traffic metrics."""
    return _run_report(
        property_id,
        dimensions=["date"],
        metrics=["sessions", "totalUsers", "screenPageViews", "bounceRate", "averageSessionDuration"],
        start_date=start_date,
        end_date=end_date,
        limit=90,
    )


def get_top_pages(property_id, limit=25, start_date=None, end_date=None):
    """Get top pages by page views."""
    return _run_report(
        property_id,
        dimensions=["pagePath", "pageTitle"],
        metrics=["screenPageViews", "sessions", "bounceRate", "averageSessionDuration"],
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        order_by_metric="screenPageViews",
    )


def get_traffic_sources(property_id, limit=25, start_date=None, end_date=None):
    """Get traffic by source/medium."""
    return _run_report(
        property_id,
        dimensions=["sessionSource", "sessionMedium"],
        metrics=["sessions", "totalUsers", "bounceRate", "averageSessionDuration"],
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        order_by_metric="sessions",
    )


def get_ai_referral_traffic(property_id, start_date=None, end_date=None):
    """
    Identify AI-referred traffic (ChatGPT, Perplexity, Claude, etc.).
    This is critical for GEO analysis — tracks actual AI search referrals.
    """
    all_sources = _run_report(
        property_id,
        dimensions=["sessionSource"],
        metrics=["sessions", "totalUsers", "screenPageViews", "bounceRate"],
        start_date=start_date,
        end_date=end_date,
        limit=500,
        order_by_metric="sessions",
    )

    # Known AI referral source patterns
    ai_source_patterns = [
        "chatgpt", "chat.openai", "openai",
        "perplexity",
        "claude", "anthropic",
        "gemini", "bard", "google-ai",
        "copilot", "bing-chat",
        "you.com", "phind",
        "kagi",
    ]

    ai_rows = []
    for row in all_sources.get("rows", []):
        source = row["dimensions"].get("sessionSource", "").lower()
        if any(pattern in source for pattern in ai_source_patterns):
            ai_rows.append(row)

    return {
        "date_range": all_sources["date_range"],
        "ai_referral_sources": ai_rows,
        "total_ai_sessions": sum(r["metrics"].get("sessions", 0) for r in ai_rows),
        "total_ai_users": sum(r["metrics"].get("totalUsers", 0) for r in ai_rows),
    }


def get_landing_pages(property_id, limit=25, start_date=None, end_date=None):
    """Get top landing pages (entry points)."""
    return _run_report(
        property_id,
        dimensions=["landingPagePlusQueryString"],
        metrics=["sessions", "totalUsers", "bounceRate", "averageSessionDuration", "conversions"],
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        order_by_metric="sessions",
    )


def get_device_breakdown(property_id, start_date=None, end_date=None):
    """Get traffic by device category."""
    return _run_report(
        property_id,
        dimensions=["deviceCategory"],
        metrics=["sessions", "totalUsers", "screenPageViews", "bounceRate"],
        start_date=start_date,
        end_date=end_date,
        limit=10,
        order_by_metric="sessions",
    )


def get_geo_breakdown(property_id, limit=25, start_date=None, end_date=None):
    """Get traffic by country."""
    return _run_report(
        property_id,
        dimensions=["country"],
        metrics=["sessions", "totalUsers", "screenPageViews"],
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        order_by_metric="sessions",
    )


def get_engagement_metrics(property_id, start_date=None, end_date=None):
    """Get engagement metrics (events, conversions)."""
    return _run_report(
        property_id,
        dimensions=["eventName"],
        metrics=["eventCount", "totalUsers"],
        start_date=start_date,
        end_date=end_date,
        limit=50,
        order_by_metric="eventCount",
    )


def get_ga4_summary(property_id, start_date=None, end_date=None):
    """
    Get a comprehensive GA4 summary combining multiple data views.
    Returns a single dict with all key metrics for GEO analysis.
    """
    summary = {
        "property_id": property_id,
        "traffic_overview": get_traffic_overview(property_id, start_date=start_date, end_date=end_date),
        "top_pages": get_top_pages(property_id, limit=15, start_date=start_date, end_date=end_date),
        "traffic_sources": get_traffic_sources(property_id, limit=15, start_date=start_date, end_date=end_date),
        "ai_referrals": get_ai_referral_traffic(property_id, start_date=start_date, end_date=end_date),
        "landing_pages": get_landing_pages(property_id, limit=10, start_date=start_date, end_date=end_date),
        "device_breakdown": get_device_breakdown(property_id, start_date=start_date, end_date=end_date),
    }

    return summary


if __name__ == "__main__":
    """CLI: Fetch GA4 data for a property."""
    if len(sys.argv) < 2:
        print("Usage: python3 ga4_fetcher.py <property_id> [command]")
        print("  Commands: overview, pages, sources, ai-traffic, landing, devices, geo, events, summary")
        print("  Example: python3 ga4_fetcher.py 123456789 ai-traffic")
        sys.exit(1)

    property_id = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "summary"

    if command == "overview":
        data = get_traffic_overview(property_id)
    elif command == "pages":
        data = get_top_pages(property_id)
    elif command == "sources":
        data = get_traffic_sources(property_id)
    elif command == "ai-traffic":
        data = get_ai_referral_traffic(property_id)
    elif command == "landing":
        data = get_landing_pages(property_id)
    elif command == "devices":
        data = get_device_breakdown(property_id)
    elif command == "geo":
        data = get_geo_breakdown(property_id)
    elif command == "events":
        data = get_engagement_metrics(property_id)
    else:
        data = get_ga4_summary(property_id)

    print(json.dumps(data, indent=2, default=str))
