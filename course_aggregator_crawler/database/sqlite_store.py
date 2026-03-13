"""SQLite storage helper for scraped courses."""

from __future__ import annotations

import sqlite3
from typing import Any


class SQLiteStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None

    def open(self) -> None:
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def init_schema(self) -> None:
        assert self.conn is not None
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                title TEXT,
                provider TEXT,
                category TEXT,
                level TEXT,
                description TEXT,
                scraped_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def insert_course(self, item: dict[str, Any]) -> None:
        assert self.conn is not None
        self.conn.execute(
            """
            INSERT INTO courses (
                source, url, title, provider, category, level, description, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title = excluded.title,
                provider = excluded.provider,
                category = excluded.category,
                level = excluded.level,
                description = excluded.description,
                scraped_at = excluded.scraped_at
            """,
            (
                item.get("source"),
                item.get("url"),
                item.get("title"),
                item.get("provider"),
                item.get("category"),
                item.get("level"),
                item.get("description"),
                item.get("scraped_at"),
            ),
        )
        self.conn.commit()
