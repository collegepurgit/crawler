"""Course service queries."""

from __future__ import annotations

from api.services.db import get_connection


class CourseService:
    @staticmethod
    def list_courses(limit: int = 100, offset: int = 0) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT
                    c.id,
                    c.title,
                    c.slug,
                    c.provider_id,
                    p.name AS provider_name,
                    c.rating,
                    c.description,
                    c.image_url,
                    c.course_url,
                    c.created_at,
                    c.updated_at
                FROM courses c
                JOIN providers p ON p.id = c.provider_id
                ORDER BY c.updated_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
