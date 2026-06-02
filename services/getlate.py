"""
services/getlate.py — Publishing via Zernio
=============================================
Multi-platform social media publishing in one API call.
Students learn: this is the "output" stage — where content goes live.

API base: https://zernio.com/api/v1
Auth: Authorization: Bearer <key>
Posts endpoint: POST /posts
  - content: post text
  - platforms: [{"platform": "instagram", "accountId": "<id>"}]
  - publishNow: true  (for immediate publish)
  - scheduledFor: ISO datetime string  (for scheduled publish)
  - media: [{"url": "...", "type": "image"}]

Profiles in Zernio are organizational containers. Publishing targets
individual account IDs. We resolve a profile's accounts by calling
GET /accounts and filtering by the profile_id field on each account.
"""

import os
import requests

# ---------------------------------------------------------------------------
# API endpoint
# ---------------------------------------------------------------------------
ZERNIO_BASE_URL = "https://zernio.com/api/v1"


def _get_headers():
    """Build auth headers for Zernio API."""
    api_key = os.getenv("GETLATE_API_KEY")
    if not api_key:
        return None
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


# ---------------------------------------------------------------------------
# get_accounts_for_profile() — Resolve account IDs for a Zernio profile
# ---------------------------------------------------------------------------
def get_accounts_for_profile(profile_id, emit_event=None):
    """
    Fetch all connected Zernio accounts, then filter to those belonging
    to the given profile_id.

    Returns a list of account dicts with at minimum: _id, platform
    Falls back to all accounts if profile_id is None.
    """
    emit = emit_event or (lambda *a, **kw: None)
    headers = _get_headers()

    if not headers:
        return []

    try:
        response = requests.get(
            f"{ZERNIO_BASE_URL}/accounts",
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        # Zernio returns either a list or {"accounts": [...]}
        accounts = data if isinstance(data, list) else data.get("accounts", [])

        # TEMP DEBUG — remove once account field names are confirmed
        if accounts:
            print(f"[ZERNIO DEBUG] First account keys: {list(accounts[0].keys())}")
            print(f"[ZERNIO DEBUG] First account sample: { {k: v for k, v in accounts[0].items() if k != '_id'} }")
        else:
            print("[ZERNIO DEBUG] /accounts returned empty list")
        # END TEMP DEBUG

        if profile_id:
            # Filter to accounts that belong to this profile
            filtered = [
                a for a in accounts
                if a.get("profile") == profile_id
                or a.get("profileId") == profile_id
                or a.get("profile_id") == profile_id
                or a.get("group") == profile_id
            ]
            # If the filter returns nothing (API may not expose profile field),
            # fall back to all accounts so publishing isn't silently broken.
            return filtered if filtered else accounts

        return accounts

    except requests.exceptions.RequestException as e:
        emit("publish", "error", f"Failed to fetch Zernio accounts: {str(e)}")
        return []


# ---------------------------------------------------------------------------
# publish_post() — Send content to connected social accounts
# ---------------------------------------------------------------------------
def publish_post(content_item, platforms=None, profile_id=None, emit_event=None):
    """
    Publish a content item to social media via Zernio.

    Args:
        content_item: dict from the database (must have script, image_url, etc.)
        platforms: list of platform names to publish to (defaults to item's platform)
        profile_id: Zernio profile ID string — used to resolve target account IDs
        emit_event: Callback for SSE logging

    Returns:
        dict with: post_id, platforms_published, status
    """
    emit = emit_event or (lambda *a, **kw: None)
    headers = _get_headers()

    if not platforms:
        platforms = [content_item.get("platform", "instagram")]

    if not headers:
        emit("publish", "progress", "No Zernio API key — simulating publish")
        return {
            "post_id": "demo_post_id",
            "platforms_published": platforms,
            "status": "demo",
            "demo": True,
            "message": "Set your Zernio API key in Settings to publish for real."
        }

    emit("publish", "progress", f"Publishing to {', '.join(platforms)} via Zernio...")

    # Resolve account IDs for the selected profile
    if profile_id:
        emit("publish", "progress", f"Resolving accounts for profile {profile_id}...")
        accounts = get_accounts_for_profile(profile_id, emit_event=emit_event)
    else:
        accounts = []

    # Build platforms array — prefer resolved accountId, fall back to platform-only
    platforms_payload = []
    for p in platforms:
        account_match = next(
            (a for a in accounts if a.get("platform", "").lower() == p.lower()),
            None
        )
        if account_match and account_match.get("_id"):
            platforms_payload.append({
                "platform": p,
                "accountId": account_match["_id"]
            })
        else:
            platforms_payload.append({"platform": p})

    try:
        # Build the post payload
        payload = {
            "content": content_item.get("script", ""),
            "platforms": platforms_payload,
            "publishNow": True,
        }

        # Attach image if available
        if content_item.get("image_url"):
            payload["media"] = [{"url": content_item["image_url"], "type": "image"}]

        # Attach video if available (video takes precedence over image)
        if content_item.get("video_url"):
            payload["media"] = payload.get("media", [])
            payload["media"].append({"url": content_item["video_url"], "type": "video"})

        # If there's a scheduled time, use scheduledFor instead of publishNow
        if content_item.get("scheduled_at"):
            payload.pop("publishNow", None)
            payload["scheduledFor"] = content_item["scheduled_at"]
            payload["timezone"] = "America/Los_Angeles"

        response = requests.post(
            f"{ZERNIO_BASE_URL}/posts",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        post_id = data.get("id", data.get("post_id", "unknown"))

        emit("publish", "progress", f"Published! Post ID: {post_id}")

        return {
            "post_id": post_id,
            "platforms_published": platforms,
            "status": "published",
            "demo": False,
            "response": data
        }

    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        emit("publish", "error", f"Zernio error: {error_msg}")
        raise


# ---------------------------------------------------------------------------
# get_connected_accounts() — List all connected social accounts
# ---------------------------------------------------------------------------
def get_connected_accounts(emit_event=None):
    """
    Fetch the list of connected social media accounts from Zernio.

    Returns:
        list of account dicts with: _id, platform, username/name, status
    """
    emit = emit_event or (lambda *a, **kw: None)
    headers = _get_headers()

    if not headers:
        # Return demo accounts so the UI has something to show
        return [
            {"_id": "demo_1", "platform": "instagram", "username": "@demo_user", "status": "demo"},
            {"_id": "demo_2", "platform": "tiktok", "username": "@demo_user", "status": "demo"},
            {"_id": "demo_3", "platform": "linkedin", "username": "Demo User", "status": "demo"},
        ]

    try:
        response = requests.get(
            f"{ZERNIO_BASE_URL}/accounts",
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else data.get("accounts", [])

    except requests.exceptions.RequestException as e:
        emit("publish", "error", f"Failed to fetch connected accounts: {str(e)}")
        return []
