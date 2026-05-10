"""
SQLite helpers for the movie / TV tracker.

This file only deals with reading and writing the database.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# Same folder as this script - keeps the project portable for a small assignment
DB_PATH = Path(__file__).resolve().parent / "media_tracker.db"

# These strings must match what the CREATE TABLE check allows
TYPES = ("Movie", "TV Show")
STATUSES = ("Plan to watch", "Watching", "Watched")


def _timestamp_now():
    """Return current UTC time as text for created_at / updated_at columns."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_connection():
    """
    Open one connection to the sqlite file.

    row_factory is set so we can access columns by name (row["title"] etc).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Make sure the table exists.

    Safe to call every time the app starts - it uses IF NOT EXISTS.
    """
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                media_type TEXT NOT NULL CHECK (media_type IN ('Movie', 'TV Show')),
                status TEXT NOT NULL CHECK (
                    status IN ('Plan to watch', 'Watching', 'Watched')
                ),
                year INTEGER,
                rating REAL,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_media_title ON media (title COLLATE NOCASE)"
        )


def fetch_all(search_text=None):
    """
    Load rows from the media table.

    If search_text is not empty, keep rows whose title OR notes contain it
    (case insensitive). Otherwise return everything.

    Returns a list of sqlite3.Row objects (each row behaves like a small dict).
    """
    sql = """
        SELECT id, title, media_type, status, year, rating, notes
        FROM media
    """
    params = []
    if search_text and str(search_text).strip():
        sql += " WHERE title LIKE ? COLLATE NOCASE OR notes LIKE ? COLLATE NOCASE"
        term = "%" + str(search_text).strip() + "%"
        params.extend([term, term])
    sql += " ORDER BY updated_at DESC, title COLLATE NOCASE ASC"

    with get_connection() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchall()


def insert_row(title, media_type, status, year, rating, notes):
    """
    Add a brand new entry.

    Returns the new primary key (id) sqlite assigned.
    """
    title = (title or "").strip()
    notes = (notes or "").strip()
    now = _timestamp_now()
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO media (
                title, media_type, status, year, rating, notes,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, media_type, status, year, rating, notes, now, now),
        )
        return int(cur.lastrowid)


def update_row(row_id, title, media_type, status, year, rating, notes):
    """Overwrite one row identified by row_id."""
    title = (title or "").strip()
    notes = (notes or "").strip()
    now = _timestamp_now()
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE media SET
                title = ?, media_type = ?, status = ?, year = ?, rating = ?,
                notes = ?, updated_at = ?
            WHERE id = ?
            """,
            (title, media_type, status, year, rating, notes, now, row_id),
        )


def delete_row(row_id):
    """Remove one row by id."""
    with get_connection() as conn:
        conn.execute("DELETE FROM media WHERE id = ?", (row_id,))


def fetch_notes(row_id):
    """Get only the notes field for one id (used when you click a row in the table)."""
    with get_connection() as conn:
        cur = conn.execute("SELECT notes FROM media WHERE id = ?", (row_id,))
        row = cur.fetchone()
    if row is None:
        return ""
    return row["notes"] or ""
