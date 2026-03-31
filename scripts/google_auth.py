#!/usr/bin/env python3
"""
Google API Authentication for GSC and GA4 integration.
Supports both Service Account and OAuth2 authentication flows.
"""

import sys
import json
import os
from pathlib import Path

try:
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
except ImportError:
    print("ERROR: Google API packages not installed. Run:")
    print("  pip install google-api-python-client google-auth google-auth-oauthlib google-analytics-data")
    sys.exit(1)

# Default scopes for GSC and GA4
GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
GA4_SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
ALL_SCOPES = GSC_SCOPES + GA4_SCOPES

# Default paths for credentials
DEFAULT_CREDENTIALS_DIR = os.path.expanduser("~/.claude/google")
SERVICE_ACCOUNT_FILE = os.path.join(DEFAULT_CREDENTIALS_DIR, "service-account.json")
OAUTH_CLIENT_FILE = os.path.join(DEFAULT_CREDENTIALS_DIR, "client-secrets.json")
OAUTH_TOKEN_FILE = os.path.join(DEFAULT_CREDENTIALS_DIR, "token.json")


def get_credentials(scopes=None, auth_type="auto"):
    """
    Get Google API credentials.

    Args:
        scopes: List of OAuth scopes. Defaults to ALL_SCOPES.
        auth_type: "service_account", "oauth", or "auto" (try service account first).

    Returns:
        google.auth.credentials.Credentials object

    Raises:
        FileNotFoundError: If no credential files are found.
        ValueError: If auth_type is invalid.
    """
    if scopes is None:
        scopes = ALL_SCOPES

    if auth_type == "service_account":
        return _get_service_account_credentials(scopes)
    elif auth_type == "oauth":
        return _get_oauth_credentials(scopes)
    elif auth_type == "auto":
        # Try service account first, fall back to OAuth
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            return _get_service_account_credentials(scopes)
        elif os.path.exists(OAUTH_CLIENT_FILE) or os.path.exists(OAUTH_TOKEN_FILE):
            return _get_oauth_credentials(scopes)
        else:
            raise FileNotFoundError(
                "No Google credentials found. Please set up authentication:\n\n"
                "Option 1 — Service Account (recommended for automation):\n"
                f"  Place service account JSON at: {SERVICE_ACCOUNT_FILE}\n\n"
                "Option 2 — OAuth2 (for personal accounts):\n"
                f"  Place OAuth client secrets at: {OAUTH_CLIENT_FILE}\n\n"
                "See: https://console.cloud.google.com/apis/credentials"
            )
    else:
        raise ValueError(f"Invalid auth_type: {auth_type}. Use 'service_account', 'oauth', or 'auto'.")


def _get_service_account_credentials(scopes):
    """Authenticate using a service account JSON key file."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Service account file not found at: {SERVICE_ACCOUNT_FILE}\n"
            "Download it from Google Cloud Console > IAM & Admin > Service Accounts."
        )

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scopes
    )
    return credentials


def _get_oauth_credentials(scopes):
    """Authenticate using OAuth2 flow with token caching."""
    credentials = None

    # Check for existing token
    if os.path.exists(OAUTH_TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(OAUTH_TOKEN_FILE, scopes)

    # Refresh or run new auth flow
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    elif not credentials or not credentials.valid:
        if not os.path.exists(OAUTH_CLIENT_FILE):
            raise FileNotFoundError(
                f"OAuth client secrets not found at: {OAUTH_CLIENT_FILE}\n"
                "Download from Google Cloud Console > APIs & Services > Credentials > OAuth 2.0 Client IDs."
            )
        flow = InstalledAppFlow.from_client_secrets_file(OAUTH_CLIENT_FILE, scopes)
        credentials = flow.run_local_server(port=0)

    # Save token for future use
    os.makedirs(DEFAULT_CREDENTIALS_DIR, exist_ok=True)
    with open(OAUTH_TOKEN_FILE, "w") as token_file:
        token_file.write(credentials.to_json())

    return credentials


def check_setup():
    """Check if Google API credentials are configured and return status."""
    status = {
        "credentials_dir": DEFAULT_CREDENTIALS_DIR,
        "service_account_exists": os.path.exists(SERVICE_ACCOUNT_FILE),
        "oauth_client_exists": os.path.exists(OAUTH_CLIENT_FILE),
        "oauth_token_exists": os.path.exists(OAUTH_TOKEN_FILE),
        "ready": False,
    }
    status["ready"] = status["service_account_exists"] or status["oauth_token_exists"]
    return status


if __name__ == "__main__":
    """CLI: check auth setup status."""
    status = check_setup()
    print(json.dumps(status, indent=2))
