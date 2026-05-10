"""SQLite persistence for media entries."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import DB_PATH
from models import MEDIA_TYPES, STATUSES, MediaRow


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or DB_PATH

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_schema(self) -> None:
        with self.connect() as conn:
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
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_media_status ON media (status)"
            )

    def list_all(self, search: str | None = None) -> list[MediaRow]:
        sql = """
            SELECT id, title, media_type, status, year, rating, notes
            FROM media
        """
        params: list[str] = []
        if search and search.strip():
            sql += " WHERE title LIKE ? COLLATE NOCASE OR notes LIKE ? COLLATE NOCASE"
            term = f"%{search.strip()}%"
            params.extend([term, term])
        sql += " ORDER BY updated_at DESC, title COLLATE NOCASE ASC"
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_row_to_media(r) for r in rows]

    def insert(self, row: MediaRow) -> int:
        now = _utc_now_iso()
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO media (
                    title, media_type, status, year, rating, notes, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.title.strip(),
                    row.media_type,
                    row.status,
                    row.year,
                    row.rating,
                    row.notes.strip(),
                    now,
                    now,
                ),
            )
            return int(cur.lastrowid)

    def update(self, row_id: int, row: MediaRow) -> None:
        now = _utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE media SET
                    title = ?, media_type = ?, status = ?, year = ?, rating = ?,
                    notes = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    row.title.strip(),
                    row.media_type,
                    row.status,
                    row.year,
                    row.rating,
                    row.notes.strip(),
                    now,
                    row_id,
                ),
            )

    def delete(self, row_id: int) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM media WHERE id = ?", (row_id,))


def _row_to_media(row: sqlite3.Row) -> MediaRow:
    return MediaRow(
        id=row["id"],
        title=row["title"],
        media_type=row["media_type"],
        status=row["status"],
        year=row["year"],
        rating=row["rating"],
        notes=row["notes"] or "",
    )


def validate_media_row(
    title: str,
    media_type: str,
    status: str,
    year: Optional[int],
    rating: Optional[float],
) -> tuple[bool, str]:
    if not title or not title.strip():
        return False, "Title is required."
    if media_type not in MEDIA_TYPES:
        return False, "Pick Movie or TV Show."
    if status not in STATUSES:
        return False, "Pick a valid status."
    if year is not None and (year < 1888 or year > 2100):
        return False, "Year should be between 1888 and 2100."
    if rating is not None and (rating < 0 or rating > 10):
        return False, "Rating must be between 0 and 10."
    return True, ""
