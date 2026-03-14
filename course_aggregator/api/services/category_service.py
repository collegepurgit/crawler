"""Category service queries."""

from __future__ import annotations

from api.services.db import get_connection


class CategoryService:
    @staticmethod
    def list_categories(limit: int = 100, offset: int = 0) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT id, name, slug FROM categories ORDER BY name LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
