"""
services/getlate.py — Publishing via Zernio
=============================================
Multi-platform social media publishing in one API call.
Students learn: this is the "output" stage — where content goes live.

API base: https://zernio.com/api/v1
Auth: Authorization: Bearer <key>
Posts endpoint: POST /posts
  Confirmed field names (from OpenAPI spec):
  - text: post text/caption (NOT "content")
  - profileId: Zernio profile ID string (top-level, NOT inside platforms)
  - socialAccountIds: flat array of account _id strings (NOT platforms objects)
  - publishNow: true  (for immediate publish)
  - scheduledAt: ISO datetime string (NOT "scheduledFor")
  - mediaItems: [{"url": "...", "type": "image|video"}] (NOT "media")

Profiles in Zernio are organizational containers. Publishing targets
individual account IDs. We resolve a profile's accounts by calling
GET /accounts and filtering by the profileId field on each account.
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

    Zernio's /accounts endpoint returns ALL accounts visible to the API key,
    including accounts from other users in the same workspace. The profileId
    field (confirmed field name) is the only safe way to scope to the correct
    brand profile.

    IMPORTANT: This function never falls back to all accounts on a failed
    filter. If the filter returns empty, it returns empty and lets the caller
    fail safely. Falling back to all accounts risks publishing to accounts
    belonging to other workspace members.

    Returns a list of account dicts with at minimum: _id, platform, profileId
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
        all_accounts = data if isinstance(data, list) else data.get("accounts", [])

        if not profile_id:
            # No profile specified — refuse to return all accounts to avoid
            # accidentally targeting other workspace members' accounts.
            emit("publish", "error",
                 "No profile_id specified — cannot safely resolve accounts. "
                 "Select a Brand Profile before publishing.")
            return []

        # Filter strictly by the confirmed profileId field name.
        # Do NOT fall back to all_accounts if this returns empty.
        filtered = [
            a for a in all_accounts
            if a.get("profileId") == profile_id
        ]

        if filtered:
            # Safety confirmation — logged to Railway so we can verify targeting
            account_labels = [
                f"{a.get('platform', '?')}:{a.get('username') or a.get('name') or a.get('_id', '?')}"
                for a in filtered
            ]
            print(f"[ZERNIO] Profile {profile_id} resolved to: {account_labels}")
            emit("publish", "progress",
                 f"Targeting {len(filtered)} account(s) for this profile: "
                 f"{', '.join(account_labels)}")
        else:
            # Filter returned nothing — fail loudly. Better to abort than to
            # publish to wrong accounts.
            print(f"[ZERNIO] WARNING: No accounts matched profileId={profile_id}. "
                  f"Total accounts visible: {len(all_accounts)}. Aborting.")
            emit("publish", "error",
                 f"No accounts found for profile {profile_id}. "
                 f"Check your Brand Profile ID in Settings.")

        return filtered

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

    # Build socialAccountIds — flat array of account _id strings,
    # filtered to the platforms we want to post to.
    # If no accounts resolved for a platform, skip it rather than guessing.
    social_account_ids = []
    for p in platforms:
        account_match = next(
            (a for a in accounts if a.get("platform", "").lower() == p.lower()),
            None
        )
        if account_match and account_match.get("_id"):
            social_account_ids.append(account_match["_id"])
        else:
            emit("publish", "progress",
                 f"No resolved account ID for platform '{p}' — skipping")

    if not social_account_ids:
        emit("publish", "error",
             "No valid account IDs resolved. Check your Brand Profile in Settings "
             "and ensure the profile has connected accounts on the target platform.")
        raise Exception("No valid socialAccountIds — publish aborted")

    try:
        # Build the post payload using confirmed Zernio field names
        payload = {
            "text": content_item.get("script", ""),          # NOT "content"
            "profileId": profile_id,                          # top-level profile ID
            "socialAccountIds": social_account_ids,           # flat array of _id strings
            "publishNow": True,                               # immediate publish
        }

        # Attach media using confirmed field name "mediaItems" (NOT "media")
        media_items = []
        if content_item.get("image_url"):
            media_items.append({"url": content_item["image_url"], "type": "image"})
        if content_item.get("video_url"):
            media_items.append({"url": content_item["video_url"], "type": "video"})
        if media_items:
            payload["mediaItems"] = media_items

        # If scheduled, use "scheduledAt" (NOT "scheduledFor") and drop publishNow
        if content_item.get("scheduled_at"):
            payload.pop("publishNow", None)
            payload["scheduledAt"] = content_item["scheduled_at"]
            payload["timezone"] = "America/Los_Angeles"

        response = requests.post(
            f"{ZERNIO_BASE_URL}/posts",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        # Zernio returns {"post": {"_id": "...", ...}}
        post = data.get("post", data)
        post_id = post.get("_id", post.get("id", "unknown"))

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
