"""Provider service queries."""

from __future__ import annotations

from api.services.db import get_connection


class ProviderService:
    @staticmethod
    def list_providers(limit: int = 100, offset: int = 0) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT id, name, website, logo_url FROM providers ORDER BY name LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
