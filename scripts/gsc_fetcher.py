#!/usr/bin/env python3
"""
Google Search Console data fetcher for GEO analysis.
Retrieves search performance data: queries, clicks, impressions, CTR, position.
"""

import sys
import json
from datetime import datetime, timedelta

try:
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Google API client not installed. Run:")
    print("  pip install google-api-python-client google-auth google-auth-oauthlib")
    sys.exit(1)

from google_auth import get_credentials, GSC_SCOPES


def get_gsc_service():
    """Build and return the GSC API service."""
    credentials = get_credentials(scopes=GSC_SCOPES)
    return build("searchconsole", "v1", credentials=credentials)


def list_sites():
    """List all verified sites in GSC."""
    service = get_gsc_service()
    site_list = service.sites().list().execute()
    return site_list.get("siteEntry", [])


def get_search_performance(
    site_url,
    start_date=None,
    end_date=None,
    dimensions=None,
    row_limit=25,
    search_type="web",
):
    """
    Fetch search performance data from GSC.

    Args:
        site_url: Property URL (e.g., "https://example.com/" or "sc-domain:example.com")
        start_date: Start date string (YYYY-MM-DD). Defaults to 28 days ago.
        end_date: End date string (YYYY-MM-DD). Defaults to 3 days ago.
        dimensions: List of dimensions (query, page, country, device, date).
        row_limit: Max rows to return (default 25, max 25000).
        search_type: "web", "image", "video", or "news".

    Returns:
        dict with keys: rows, totals, date_range
    """
    service = get_gsc_service()

    if not end_date:
        end_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")
    if dimensions is None:
        dimensions = ["query"]

    request_body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": min(row_limit, 25000),
        "type": search_type,
    }

    response = service.searchanalytics().query(
        siteUrl=site_url, body=request_body
    ).execute()

    rows = response.get("rows", [])
    result = {
        "date_range": {"start": start_date, "end": end_date},
        "search_type": search_type,
        "dimensions": dimensions,
        "total_rows": len(rows),
        "rows": [],
    }

    for row in rows:
        result["rows"].append({
            "keys": row.get("keys", []),
            "clicks": row.get("clicks", 0),
            "impressions": row.get("impressions", 0),
            "ctr": round(row.get("ctr", 0) * 100, 2),
            "position": round(row.get("position", 0), 1),
        })

    return result


def get_top_queries(site_url, limit=25, start_date=None, end_date=None):
    """Get top search queries by clicks."""
    return get_search_performance(
        site_url,
        dimensions=["query"],
        row_limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


def get_top_pages(site_url, limit=25, start_date=None, end_date=None):
    """Get top pages by clicks."""
    return get_search_performance(
        site_url,
        dimensions=["page"],
        row_limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


def get_performance_by_date(site_url, start_date=None, end_date=None):
    """Get daily performance trends."""
    return get_search_performance(
        site_url,
        dimensions=["date"],
        row_limit=1000,
        start_date=start_date,
        end_date=end_date,
    )


def get_query_page_pairs(site_url, limit=50, start_date=None, end_date=None):
    """Get query-page combinations for content optimization insights."""
    return get_search_performance(
        site_url,
        dimensions=["query", "page"],
        row_limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


def get_device_breakdown(site_url, start_date=None, end_date=None):
    """Get performance by device type (DESKTOP, MOBILE, TABLET)."""
    return get_search_performance(
        site_url,
        dimensions=["device"],
        row_limit=10,
        start_date=start_date,
        end_date=end_date,
    )


def get_country_breakdown(site_url, limit=25, start_date=None, end_date=None):
    """Get performance by country."""
    return get_search_performance(
        site_url,
        dimensions=["country"],
        row_limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


def get_gsc_summary(site_url, start_date=None, end_date=None):
    """
    Get a comprehensive GSC summary combining multiple data views.
    Returns a single dict with all key metrics.
    """
    summary = {
        "site_url": site_url,
        "top_queries": get_top_queries(site_url, limit=20, start_date=start_date, end_date=end_date),
        "top_pages": get_top_pages(site_url, limit=15, start_date=start_date, end_date=end_date),
        "device_breakdown": get_device_breakdown(site_url, start_date=start_date, end_date=end_date),
        "country_breakdown": get_country_breakdown(site_url, limit=10, start_date=start_date, end_date=end_date),
        "daily_trend": get_performance_by_date(site_url, start_date=start_date, end_date=end_date),
    }

    # Calculate aggregate totals from daily data
    daily_rows = summary["daily_trend"].get("rows", [])
    if daily_rows:
        summary["totals"] = {
            "total_clicks": sum(r["clicks"] for r in daily_rows),
            "total_impressions": sum(r["impressions"] for r in daily_rows),
            "avg_ctr": round(
                sum(r["ctr"] for r in daily_rows) / len(daily_rows), 2
            ),
            "avg_position": round(
                sum(r["position"] for r in daily_rows) / len(daily_rows), 1
            ),
        }

    return summary


if __name__ == "__main__":
    """CLI: Fetch GSC data for a site."""
    if len(sys.argv) < 2:
        print("Usage: python3 gsc_fetcher.py <site_url> [command]")
        print("  Commands: sites, queries, pages, summary, trend, devices, countries")
        print("  Example: python3 gsc_fetcher.py https://example.com/ queries")
        sys.exit(1)

    site_url = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "summary"

    if command == "sites":
        data = list_sites()
    elif command == "queries":
        data = get_top_queries(site_url)
    elif command == "pages":
        data = get_top_pages(site_url)
    elif command == "trend":
        data = get_performance_by_date(site_url)
    elif command == "devices":
        data = get_device_breakdown(site_url)
    elif command == "countries":
        data = get_country_breakdown(site_url)
    else:
        data = get_gsc_summary(site_url)

    print(json.dumps(data, indent=2))
