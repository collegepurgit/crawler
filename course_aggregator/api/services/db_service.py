"""Database access helpers for FastAPI course queries."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "database" / "courses.db"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _filtered_courses_from_clause(
    category: str | None = None,
    provider: str | None = None,
) -> tuple[str, list[object]]:
    from_clause = """
        FROM courses c
        JOIN providers p ON p.id = c.provider_id
        LEFT JOIN course_categories cc ON cc.course_id = c.id
        LEFT JOIN categories cat ON cat.id = cc.category_id
        WHERE 1=1
    """
    params: list[object] = []

    if category:
        from_clause += " AND cat.slug = ?"
        params.append(category)
    if provider:
        from_clause += " AND p.name = ?"
        params.append(provider)

    return from_clause, params


def get_courses(
    limit: int = 100,
    offset: int = 0,
    category: str | None = None,
    provider: str | None = None,
) -> list[dict]:
    """Return paginated courses with optional category/provider filtering."""
    from_clause, params = _filtered_courses_from_clause(category=category, provider=provider)
    query = (
        """
        SELECT DISTINCT
            c.id,
            c.title,
            c.slug,
            p.name AS provider,
            c.rating
        """
        + from_clause
        + " ORDER BY c.updated_at DESC LIMIT ? OFFSET ?"
    )
    params.extend([limit, offset])

    with _get_connection() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]


def get_courses_total(
    category: str | None = None,
    provider: str | None = None,
) -> int:
    """Return total number of courses for optional filters."""
    from_clause, params = _filtered_courses_from_clause(category=category, provider=provider)
    query = "SELECT COUNT(DISTINCT c.id) AS total " + from_clause

    with _get_connection() as conn:
        row = conn.execute(query, tuple(params)).fetchone()
        return int(row["total"]) if row else 0


def get_course_by_slug(slug: str) -> dict | None:
    """Return full details for a single course by slug."""
    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                c.id,
                c.title,
                c.slug,
                c.description,
                p.name AS provider,
                c.rating,
                c.image_url,
                c.course_url
            FROM courses c
            JOIN providers p ON p.id = c.provider_id
            WHERE c.slug = ?
            LIMIT 1
            """,
            (slug,),
        ).fetchone()

        if not row:
            return None

        course = dict(row)

        categories = conn.execute(
            """
            SELECT cat.name
            FROM categories cat
            JOIN course_categories cc ON cc.category_id = cat.id
            WHERE cc.course_id = ?
            ORDER BY cat.name
            """,
            (course["id"],),
        ).fetchall()

        instructors = conn.execute(
            """
            SELECT i.name
            FROM instructors i
            JOIN course_instructors ci ON ci.instructor_id = i.id
            WHERE ci.course_id = ?
            ORDER BY i.name
            """,
            (course["id"],),
        ).fetchall()

        course["categories"] = [item["name"] for item in categories]
        course["instructors"] = [item["name"] for item in instructors]
        course.pop("id", None)
        return course


def get_courses_by_category(
    category_slug: str,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Return courses associated with a category slug."""
    return get_courses(limit=limit, offset=offset, category=category_slug)


def get_courses_by_provider(
    provider_name: str,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Return courses associated with the given provider name."""
    return get_courses(limit=limit, offset=offset, provider=provider_name)


def search_courses(q: str) -> list[dict]:
    """Search courses by title using SQL LIKE."""
    pattern = f"%{q.strip()}%"
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                c.title,
                c.slug,
                p.name AS provider,
                c.rating
            FROM courses c
            JOIN providers p ON p.id = c.provider_id
            WHERE c.title LIKE ?
            ORDER BY c.updated_at DESC
            """,
            (pattern,),
        ).fetchall()
        return [dict(row) for row in rows]
