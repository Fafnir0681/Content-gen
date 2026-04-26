"""
models.py — SQLite Database Layer
==================================
Uses raw sqlite3 (no ORM) so students can see exactly what's happening.
Every query is a plain SQL string — easy to read, easy to modify.
"""

import sqlite3
import os
import json
from contextlib import contextmanager
from datetime import datetime

# ---------------------------------------------------------------------------
# Database path — defaults to content.db in the project root
# ---------------------------------------------------------------------------
DATABASE_PATH = os.getenv("DATABASE_PATH", "content.db")


# ---------------------------------------------------------------------------
# Context manager: get a database connection with Row factory
# Usage:  with get_db() as db:
#             db.execute("SELECT ...")
# ---------------------------------------------------------------------------
@contextmanager
def get_db():
    """
    Yields a sqlite3 connection configured with Row factory.
    Auto-commits on success, rolls back on error, always closes.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row          # Access columns by name
    conn.execute("PRAGMA foreign_keys = ON")  # Enforce FK constraints
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# init_db() — Create all tables if they don't exist
# Called once on app startup
# ---------------------------------------------------------------------------
def init_db():
    """Create all 4 tables. Safe to call multiple times (IF NOT EXISTS)."""
    with get_db() as db:
        # -- content_items: stores each piece of content through the pipeline --
        db.execute("""
            CREATE TABLE IF NOT EXISTS content_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT NOT NULL,
                input_type TEXT DEFAULT 'idea',
                platform TEXT DEFAULT 'instagram',
                article_text TEXT,
                article_title TEXT,
                word_count INTEGER,
                script TEXT,
                captions TEXT,
                image_prompt TEXT,
                image_url TEXT,
                image_task_id TEXT,
                video_prompt TEXT,
                video_url TEXT,
                video_task_id TEXT,
                include_video BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'draft',
                cost_total REAL DEFAULT 0.0,
                scheduled_at TIMESTAMP,
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # -- pipeline_logs: every event that happens during processing --
        db.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER REFERENCES content_items(id) ON DELETE CASCADE,
                stage TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                detail TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # -- settings: key-value store for API keys, preferences, etc. --
        db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # -- schedule_slots: calendar entries for scheduled publishing --
        db.execute("""
            CREATE TABLE IF NOT EXISTS schedule_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER REFERENCES content_items(id) ON DELETE CASCADE,
                scheduled_datetime TIMESTAMP NOT NULL,
                platform TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                published_at TIMESTAMP,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


# ===========================================================================
# CONTENT ITEMS — CRUD helpers
# ===========================================================================

def create_content_item(input_text, input_type="idea", platform="instagram", include_video=False):
    """
    Insert a new content item and return its ID.
    input_type is auto-detected: if input_text starts with 'http', it's a URL.
    """
    # Auto-detect URL vs idea
    if input_text.strip().lower().startswith("http"):
        input_type = "url"

    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO content_items (input_text, input_type, platform, include_video)
               VALUES (?, ?, ?, ?)""",
            (input_text, input_type, platform, int(include_video))
        )
        return cursor.lastrowid


def get_content_item(item_id):
    """Fetch a single content item by ID. Returns dict or None."""
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM content_items WHERE id = ?", (item_id,)
        ).fetchone()
        return dict(row) if row else None


def list_content_items(limit=50, status=None):
    """
    List content items, newest first.
    Optionally filter by status (e.g., 'ready', 'published').
    """
    with get_db() as db:
        if status:
            rows = db.execute(
                "SELECT * FROM content_items WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM content_items ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


def update_content_item(item_id, **fields):
    """
    Update any columns on a content item.
    Usage: update_content_item(1, status='scripted', script='Hello world...')
    """
    if not fields:
        return

    # Always update the updated_at timestamp
    fields["updated_at"] = datetime.now().isoformat()

    set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
    values = list(fields.values()) + [item_id]

    with get_db() as db:
        db.execute(
            f"UPDATE content_items SET {set_clause} WHERE id = ?",
            values
        )


def delete_content_item(item_id):
    """Delete a content item and its associated logs (CASCADE)."""
    with get_db() as db:
        db.execute("DELETE FROM content_items WHERE id = ?", (item_id,))


# ===========================================================================
# PIPELINE LOGS — track every event during processing
# ===========================================================================

def add_pipeline_log(content_id, stage, status, message, detail=None):
    """
    Insert a pipeline log entry.
    detail should be a JSON string (or None).
    """
    with get_db() as db:
        db.execute(
            """INSERT INTO pipeline_logs (content_id, stage, status, message, detail)
               VALUES (?, ?, ?, ?, ?)""",
            (content_id, stage, status, message, detail or "{}")
        )


def get_pipeline_logs(content_id):
    """Get all pipeline logs for a content item, oldest first."""
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM pipeline_logs WHERE content_id = ? ORDER BY created_at ASC",
            (content_id,)
        ).fetchall()
        return [dict(r) for r in rows]


# ===========================================================================
# SETTINGS — key-value store for API keys and config
# ===========================================================================

def get_setting(key, default=None):
    """Get a setting value by key. Returns default if not found."""
    with get_db() as db:
        row = db.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default


def set_setting(key, value):
    """Set a setting value (insert or update)."""
    with get_db() as db:
        db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )


# ===========================================================================
# SCHEDULE SLOTS — calendar entries for publishing
# ===========================================================================

def create_schedule_slot(content_id, scheduled_datetime, platform):
    """Create a schedule slot for publishing. Returns the slot ID."""
    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO schedule_slots (content_id, scheduled_datetime, platform)
               VALUES (?, ?, ?)""",
            (content_id, scheduled_datetime, platform)
        )
        return cursor.lastrowid


def list_schedule_slots(month=None, year=None):
    """
    List schedule slots, optionally filtered by month/year.
    Joins with content_items to include the content title/text.
    """
    with get_db() as db:
        if month and year:
            rows = db.execute(
                """SELECT s.*, c.input_text, c.article_title, c.platform as content_platform, c.status as content_status
                   FROM schedule_slots s
                   LEFT JOIN content_items c ON s.content_id = c.id
                   WHERE strftime('%m', s.scheduled_datetime) = ?
                     AND strftime('%Y', s.scheduled_datetime) = ?
                   ORDER BY s.scheduled_datetime ASC""",
                (str(month).zfill(2), str(year))
            ).fetchall()
        else:
            rows = db.execute(
                """SELECT s.*, c.input_text, c.article_title, c.platform as content_platform, c.status as content_status
                   FROM schedule_slots s
                   LEFT JOIN content_items c ON s.content_id = c.id
                   ORDER BY s.scheduled_datetime ASC"""
            ).fetchall()
        return [dict(r) for r in rows]
