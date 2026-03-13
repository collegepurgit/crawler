"""SQLite helper used by Scrapy pipeline."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None

    def open(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def create_tables(self) -> None:
        assert self.conn is not None
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                website TEXT,
                logo_url TEXT
            );

            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT NOT NULL,
                provider_id INTEGER NOT NULL,
                rating REAL,
                description TEXT,
                image_url TEXT,
                course_url TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE RESTRICT
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                slug TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS course_categories (
                course_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                PRIMARY KEY (course_id, category_id),
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS instructors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                profile_url TEXT,
                UNIQUE(name, profile_url)
            );

            CREATE TABLE IF NOT EXISTS course_instructors (
                course_id INTEGER NOT NULL,
                instructor_id INTEGER NOT NULL,
                PRIMARY KEY (course_id, instructor_id),
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_courses_slug ON courses(slug);
            CREATE INDEX IF NOT EXISTS idx_courses_provider_id ON courses(provider_id);
            CREATE INDEX IF NOT EXISTS idx_courses_rating ON courses(rating);
            CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);
            """
        )
        self.conn.commit()

    def get_or_create_provider(self, name: str, website: str = "", logo_url: str = "") -> int:
        """Insert provider when missing and return provider id."""
        assert self.conn is not None
        provider_name = (name or "Unknown Provider").strip()
        self.conn.execute(
            """
            INSERT INTO providers (name, website, logo_url)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                website = excluded.website,
                logo_url = excluded.logo_url
            """,
            (provider_name, website.strip(), logo_url.strip()),
        )
        return self.conn.execute(
            "SELECT id FROM providers WHERE name = ?",
            (provider_name,),
        ).fetchone()[0]

    def upsert_course(
        self,
        *,
        title: str,
        slug: str,
        provider_id: int,
        rating: float | None,
        description: str,
        image_url: str,
        course_url: str,
    ) -> int:
        """Insert or update course by unique course_url and return course id."""
        assert self.conn is not None
        self.conn.execute(
            """
            INSERT INTO courses (
                title, slug, provider_id, rating, description, image_url, course_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(course_url) DO UPDATE SET
                title = excluded.title,
                slug = excluded.slug,
                provider_id = excluded.provider_id,
                rating = excluded.rating,
                description = excluded.description,
                image_url = excluded.image_url,
                updated_at = CURRENT_TIMESTAMP
            """,
            (title, slug, provider_id, rating, description, image_url, course_url),
        )
        return self.conn.execute(
            "SELECT id FROM courses WHERE course_url = ?",
            (course_url,),
        ).fetchone()[0]

    def get_or_create_category(self, name: str) -> int:
        """Insert category if missing and return category id."""
        assert self.conn is not None
        cleaned = (name or "").strip()
        if not cleaned:
            raise ValueError("Category name cannot be empty")

        self.conn.execute(
            """
            INSERT INTO categories (name, slug)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET slug = excluded.slug
            """,
            (cleaned, self._slugify(cleaned)),
        )
        return self.conn.execute(
            "SELECT id FROM categories WHERE name = ?",
            (cleaned,),
        ).fetchone()[0]

    def get_or_create_instructor(self, name: str, profile_url: str = "") -> int:
        """Insert instructor if missing and return instructor id."""
        assert self.conn is not None
        cleaned_name = (name or "").strip()
        cleaned_profile = (profile_url or "").strip()
        if not cleaned_name:
            raise ValueError("Instructor name cannot be empty")

        self.conn.execute(
            """
            INSERT INTO instructors (name, profile_url)
            VALUES (?, ?)
            ON CONFLICT(name, profile_url) DO NOTHING
            """,
            (cleaned_name, cleaned_profile),
        )
        return self.conn.execute(
            "SELECT id FROM instructors WHERE name = ? AND profile_url = ?",
            (cleaned_name, cleaned_profile),
        ).fetchone()[0]

    def replace_course_categories(self, course_id: int, category_ids: list[int]) -> None:
        """Replace category relations for a course."""
        assert self.conn is not None
        self.conn.execute("DELETE FROM course_categories WHERE course_id = ?", (course_id,))
        for category_id in set(category_ids):
            self.conn.execute(
                "INSERT OR IGNORE INTO course_categories (course_id, category_id) VALUES (?, ?)",
                (course_id, category_id),
            )

    def replace_course_instructors(self, course_id: int, instructor_ids: list[int]) -> None:
        """Replace instructor relations for a course."""
        assert self.conn is not None
        self.conn.execute("DELETE FROM course_instructors WHERE course_id = ?", (course_id,))
        for instructor_id in set(instructor_ids):
            self.conn.execute(
                "INSERT OR IGNORE INTO course_instructors (course_id, instructor_id) VALUES (?, ?)",
                (course_id, instructor_id),
            )

    def commit(self) -> None:
        assert self.conn is not None
        self.conn.commit()

    def _slugify(self, value: str) -> str:
        text = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
        return text or "unknown"
