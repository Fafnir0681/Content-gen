"""
models.py — PostgreSQL Database Layer
======================================
Uses psycopg2 with a RealDictCursor so rows are returned as dicts.
DATABASE_URL is injected automatically by Railway when a PostgreSQL
service is attached to the project.
"""

import os
import json
from contextlib import contextmanager
from datetime import datetime

import psycopg2
import psycopg2.extras

# ---------------------------------------------------------------------------
# Database URL — injected by Railway PostgreSQL service
# Railway may inject postgres:// (legacy); psycopg2 requires postgresql://
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


# ---------------------------------------------------------------------------
# _Cursor — thin adapter so psycopg2 cursor matches sqlite3's chainable API
# sqlite3: conn.execute("SELECT ...").fetchone()
# psycopg2: cursor.execute() returns None, so we return self to keep chaining
# ---------------------------------------------------------------------------
class _Cursor:
    def __init__(self, cur):
        self._cur = cur

    def execute(self, sql, params=None):
        if params is not None:
            self._cur.execute(sql, params)
        else:
            self._cur.execute(sql)
        return self

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    @property
    def lastrowid(self):
        row = self._cur.fetchone()
        return row["id"] if row else None

    def close(self):
        self._cur.close()


# ---------------------------------------------------------------------------
# Context manager: get a database connection
# Usage:  with get_db() as db:
#             db.execute("SELECT ...")
# ---------------------------------------------------------------------------
@contextmanager
def get_db():
    """
    Yields a _Cursor wrapping a psycopg2 RealDictCursor.
    Auto-commits on success, rolls back on error, always closes.
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield _Cursor(cur)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ---------------------------------------------------------------------------
# init_db() — Create all tables if they don't exist
# Called once on app startup
# ---------------------------------------------------------------------------
def init_db():
    """Create all tables. Safe to call multiple times (IF NOT EXISTS)."""
    with get_db() as db:
        # -- content_items: stores each piece of content through the pipeline --
        db.execute("""
            CREATE TABLE IF NOT EXISTS content_items (
                id SERIAL PRIMARY KEY,
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
                include_video BOOLEAN DEFAULT FALSE,
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
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
                content_id INTEGER REFERENCES content_items(id) ON DELETE CASCADE,
                scheduled_datetime TIMESTAMP NOT NULL,
                platform TEXT NOT NULL,
                profile_id TEXT,
                status TEXT DEFAULT 'pending',
                published_at TIMESTAMP,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # -- zernio_profiles: saved Zernio profile IDs for brand targeting --
        db.execute("""
            CREATE TABLE IF NOT EXISTS zernio_profiles (
                id SERIAL PRIMARY KEY,
                label TEXT NOT NULL,
                profile_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migrate: add profile_id to existing schedule_slots tables that predate this column
        db.execute("""
            ALTER TABLE schedule_slots ADD COLUMN IF NOT EXISTS profile_id TEXT
        """)

        # Seed default profiles on first run
        count = db.execute("SELECT COUNT(*) as c FROM zernio_profiles").fetchone()["c"]
        if count == 0:
            db.execute(
                "INSERT INTO zernio_profiles (label, profile_id) VALUES (%s, %s)",
                ("Ironside", "6a1cff243917c8c2b74a2f26")
            )
            db.execute(
                "INSERT INTO zernio_profiles (label, profile_id) VALUES (%s, %s)",
                ("AssemblR", "6a1d0d3387faa42d5a3fe4f1")
            )


# ===========================================================================
# CONTENT ITEMS — CRUD helpers
# ===========================================================================

def create_content_item(input_text, input_type="idea", platform="instagram", include_video=False):
    """
    Insert a new content item and return its ID.
    input_type is auto-detected: if input_text starts with 'http', it's a URL.
    """
    if input_text.strip().lower().startswith("http"):
        input_type = "url"

    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO content_items (input_text, input_type, platform, include_video)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (input_text, input_type, platform, include_video)
        )
        return cursor.lastrowid


def get_content_item(item_id):
    """Fetch a single content item by ID. Returns dict or None."""
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM content_items WHERE id = %s", (item_id,)
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
                "SELECT * FROM content_items WHERE status = %s ORDER BY created_at DESC LIMIT %s",
                (status, limit)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM content_items ORDER BY created_at DESC LIMIT %s",
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

    fields["updated_at"] = datetime.now().isoformat()

    set_clause = ", ".join(f"{k} = %s" for k in fields.keys())
    values = list(fields.values()) + [item_id]

    with get_db() as db:
        db.execute(
            f"UPDATE content_items SET {set_clause} WHERE id = %s",
            values
        )


def delete_content_item(item_id):
    """Delete a content item and its associated logs (CASCADE)."""
    with get_db() as db:
        db.execute("DELETE FROM content_items WHERE id = %s", (item_id,))


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
               VALUES (%s, %s, %s, %s, %s)""",
            (content_id, stage, status, message, detail or "{}")
        )


def get_pipeline_logs(content_id):
    """Get all pipeline logs for a content item, oldest first."""
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM pipeline_logs WHERE content_id = %s ORDER BY created_at ASC",
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
            "SELECT value FROM settings WHERE key = %s", (key,)
        ).fetchone()
        return row["value"] if row else default


def set_setting(key, value):
    """Set a setting value (insert or update)."""
    with get_db() as db:
        db.execute(
            """INSERT INTO settings (key, value) VALUES (%s, %s)
               ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value""",
            (key, value)
        )


# ===========================================================================
# SCHEDULE SLOTS — calendar entries for publishing
# ===========================================================================

def create_schedule_slot(content_id, scheduled_datetime, platform, profile_id=None):
    """Create a schedule slot for publishing. Returns the slot ID."""
    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO schedule_slots (content_id, scheduled_datetime, platform, profile_id)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (content_id, scheduled_datetime, platform, profile_id)
        )
        return cursor.lastrowid


def get_default_profile():
    """Return the first profile, or None if no profiles exist."""
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM zernio_profiles ORDER BY id ASC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


# ===========================================================================
# ZERNIO PROFILES — saved brand profiles for publishing targeting
# ===========================================================================

def list_profiles():
    """Return all Zernio profiles, ordered by creation (oldest first)."""
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM zernio_profiles ORDER BY id ASC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_profile(profile_db_id):
    """Fetch a single profile by its database ID. Returns dict or None."""
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM zernio_profiles WHERE id = %s", (profile_db_id,)
        ).fetchone()
        return dict(row) if row else None


def create_profile(label, profile_id):
    """Insert a new Zernio profile. Returns the new row ID."""
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO zernio_profiles (label, profile_id) VALUES (%s, %s) RETURNING id",
            (label.strip(), profile_id.strip())
        )
        return cursor.lastrowid


def update_profile(profile_db_id, label, profile_id):
    """Update an existing profile's label and Zernio profile ID."""
    with get_db() as db:
        db.execute(
            "UPDATE zernio_profiles SET label = %s, profile_id = %s WHERE id = %s",
            (label.strip(), profile_id.strip(), profile_db_id)
        )


def delete_profile(profile_db_id):
    """Delete a profile by its database ID."""
    with get_db() as db:
        db.execute("DELETE FROM zernio_profiles WHERE id = %s", (profile_db_id,))


# ===========================================================================
# SCHEDULE SLOTS — list helpers
# ===========================================================================

def list_schedule_slots(month=None, year=None):
    """
    List schedule slots, optionally filtered by month/year.
    Joins with content_items to include the content title/text.
    """
    with get_db() as db:
        if month and year:
            rows = db.execute(
                """SELECT s.*, c.input_text, c.article_title,
                          c.platform as content_platform, c.status as content_status
                   FROM schedule_slots s
                   LEFT JOIN content_items c ON s.content_id = c.id
                   WHERE EXTRACT(MONTH FROM s.scheduled_datetime) = %s
                     AND EXTRACT(YEAR  FROM s.scheduled_datetime) = %s
                   ORDER BY s.scheduled_datetime ASC""",
                (month, year)
            ).fetchall()
        else:
            rows = db.execute(
                """SELECT s.*, c.input_text, c.article_title,
                          c.platform as content_platform, c.status as content_status
                   FROM schedule_slots s
                   LEFT JOIN content_items c ON s.content_id = c.id
                   ORDER BY s.scheduled_datetime ASC"""
            ).fetchall()
        return [dict(r) for r in rows]
