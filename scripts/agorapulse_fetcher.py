#!/usr/bin/env python3
"""
Agorapulse API fetcher for social media metrics.
Pulls audience, content, and community management data.
"""

import sys
import json
import os
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("ERROR: requests package not installed.")
    sys.exit(1)

BASE_URL = "https://api.agorapulse.com"
ORG_ID = "180837"
WORKSPACE_ID = "80838"

# All connected profiles
PROFILES = {
    "tiktok_brands": {"uid": "tiktok_13490", "name": "Animoca Brands", "platform": "TikTok"},
    "tiktok_minds": {"uid": "tiktok_25210", "name": "Animoca Minds", "platform": "TikTok"},
    "instagram_brands": {"uid": "instagram_265097", "name": "Animoca Brands", "platform": "Instagram"},
    "instagram_minds": {"uid": "instagram_379234", "name": "Animoca Minds", "platform": "Instagram"},
    "linkedin_brands": {"uid": "linkedin_87218", "name": "Animoca Brands", "platform": "LinkedIn"},
    "linkedin_minds": {"uid": "linkedin_162584", "name": "Animoca Minds", "platform": "LinkedIn"},
    "twitter_brands": {"uid": "twitter_143715", "name": "Animoca Brands", "platform": "X (Twitter)"},
    "twitter_minds": {"uid": "twitter_182708", "name": "Animoca Minds", "platform": "X (Twitter)"},
    "facebook_brands": {"uid": "facebook_536683", "name": "Animoca Brands", "platform": "Facebook"},
    "youtube_brands": {"uid": "youtube_32100", "name": "Animoca Brands", "platform": "YouTube"},
    "youtube_minds": {"uid": "youtube_54304", "name": "Animoca Minds", "platform": "YouTube"},
}


def _get_api_key():
    """Read API key from Streamlit secrets or local file."""
    try:
        import streamlit as st
        key = st.secrets.get("AGORAPULSE_API_KEY")
        if key:
            return str(key).strip()
    except Exception:
        pass

    key_paths = [
        os.path.expanduser("~/.claude/google/agorapulse.txt"),
        os.path.join(os.path.dirname(__file__), "agorapulse.txt"),
    ]
    for path in key_paths:
        if os.path.exists(path):
            with open(path) as f:
                return f.read().strip()
    raise FileNotFoundError(
        "Agorapulse API key not found. Set AGORAPULSE_API_KEY in Streamlit secrets "
        "or save the key to ~/.claude/google/agorapulse.txt"
    )


def _to_unix_seconds(value):
    """Convert YYYY-MM-DD (or datetime) to Unix seconds Agorapulse expects."""
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        s = str(value)
        if "T" in s:
            dt = datetime.strptime(s.split("T")[0], "%Y-%m-%d")
        else:
            dt = datetime.strptime(s, "%Y-%m-%d")
    return int(dt.timestamp())


def _api_request(endpoint, params=None):
    """Make an authenticated API request."""
    api_key = _get_api_key()
    headers = {"X-API-KEY": api_key, "Accept": "application/json"}
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    if not resp.ok:
        body = resp.text[:500] if resp.text else "(empty body)"
        sent_params = params if params else {}
        raise requests.HTTPError(
            f"{resp.status_code} {resp.reason} for {url} "
            f"(params sent: {sent_params}) — body: {body}"
        )
    return resp.json()


def get_audience_report(profile_uid, since, until):
    """Get audience insights (followers, demographics) for a profile."""
    endpoint = (
        f"/v1.0/report/organizations/{ORG_ID}/workspaces/{WORKSPACE_ID}"
        f"/profiles/{profile_uid}/insights/audience"
    )
    return _api_request(endpoint, {"since": _to_unix_seconds(since), "until": _to_unix_seconds(until)})


def get_content_report(profile_uid, since, until):
    """Get content performance (posts, engagement, reach) for a profile."""
    endpoint = (
        f"/v1.0/report/organizations/{ORG_ID}/workspaces/{WORKSPACE_ID}"
        f"/profiles/{profile_uid}/insights/content"
    )
    return _api_request(endpoint, {"since": _to_unix_seconds(since), "until": _to_unix_seconds(until)})


def get_community_report(profile_uid, since, until):
    """Get community management metrics (replies, messages) for a profile."""
    endpoint = (
        f"/v1.0/report/organizations/{ORG_ID}/workspaces/{WORKSPACE_ID}"
        f"/profiles/{profile_uid}/insights/community-management"
    )
    return _api_request(endpoint, {"since": _to_unix_seconds(since), "until": _to_unix_seconds(until)})


def get_all_profiles_summary(since=None, until=None):
    """Get audience and content data for all profiles."""
    if not since:
        since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not until:
        until = datetime.now().strftime("%Y-%m-%d")

    results = []
    for key, profile in PROFILES.items():
        try:
            audience = get_audience_report(profile["uid"], since, until)
            content = get_content_report(profile["uid"], since, until)

            results.append({
                "key": key,
                "profile_uid": profile["uid"],
                "name": profile["name"],
                "platform": profile["platform"],
                "audience": audience,
                "content": content,
            })
        except Exception as e:
            msg = str(e)
            entry = {
                "key": key,
                "profile_uid": profile["uid"],
                "name": profile["name"],
                "platform": profile["platform"],
            }
            if '"subCode":1104' in msg or "not handled by open APIs" in msg:
                entry["unsupported"] = True
                entry["note"] = "Not exposed by Agorapulse open API"
            else:
                entry["error"] = msg
            results.append(entry)

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 agorapulse_fetcher.py <command> [profile_key]")
        print("  Commands: profiles, audience, content, community, summary")
        print("  Profile keys:", ", ".join(PROFILES.keys()))
        sys.exit(1)

    command = sys.argv[1]

    if command == "profiles":
        for key, p in PROFILES.items():
            print(f"  {key}: {p['name']} ({p['platform']}) — {p['uid']}")

    elif command == "summary":
        since = sys.argv[2] if len(sys.argv) > 2 else None
        until = sys.argv[3] if len(sys.argv) > 3 else None
        data = get_all_profiles_summary(since, until)
        print(json.dumps(data, indent=2, default=str))

    elif command in ("audience", "content", "community"):
        profile_key = sys.argv[2] if len(sys.argv) > 2 else "linkedin_brands"
        since = sys.argv[3] if len(sys.argv) > 3 else (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        until = sys.argv[4] if len(sys.argv) > 4 else datetime.now().strftime("%Y-%m-%d")

        profile = PROFILES.get(profile_key)
        if not profile:
            print(f"Unknown profile: {profile_key}")
            sys.exit(1)

        if command == "audience":
            data = get_audience_report(profile["uid"], since, until)
        elif command == "content":
            data = get_content_report(profile["uid"], since, until)
        else:
            data = get_community_report(profile["uid"], since, until)

        print(json.dumps(data, indent=2, default=str))
