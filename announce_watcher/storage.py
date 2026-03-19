from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from announce_watcher.models import Notice


class SQLiteNoticeStore:
    def __init__(self, db_path: str | Path = "watcher.db") -> None:
        self.db_path = Path(db_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notices (
                    site_name TEXT NOT NULL,
                    notice_key TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    published_at TEXT,
                    first_seen_at TEXT NOT NULL,
                    PRIMARY KEY (site_name, notice_key)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS check_history (
                    site_name TEXT NOT NULL,
                    checked_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail TEXT
                )
                """
            )
            conn.commit()

    def has_notice(self, site_name: str, notice_key: str) -> bool:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT 1 FROM notices WHERE site_name = ? AND notice_key = ?",
                (site_name, notice_key),
            ).fetchone()
        return row is not None

    def has_any_notices(self, site_name: str) -> bool:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT 1 FROM notices WHERE site_name = ? LIMIT 1",
                (site_name,),
            ).fetchone()
        return row is not None

    def save_notice(self, notice: Notice) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO notices (
                    site_name, notice_key, title, url, published_at, first_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    notice.site_name,
                    notice.notice_key,
                    notice.title,
                    notice.url,
                    notice.published_at.isoformat() if notice.published_at else None,
                    notice.first_seen_at.isoformat(),
                ),
            )
            conn.commit()

    def record_check(self, site_name: str, status: str, detail: str = "") -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                "INSERT INTO check_history (site_name, checked_at, status, detail) VALUES (?, ?, ?, ?)",
                (site_name, datetime.utcnow().isoformat(), status, detail),
            )
            conn.commit()
