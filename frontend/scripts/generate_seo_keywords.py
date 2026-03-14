"""Generate SEO keyword/page metadata from database categories and template config."""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "course_aggregator" / "database" / "courses.db"
TEMPLATES_PATH = ROOT / "frontend" / "config" / "seo-keyword-templates.json"
OUTPUT_PATH = ROOT / "frontend" / "config" / "seo-keywords.json"
SITE_URL = os.getenv("NEXT_PUBLIC_SITE_URL", "http://localhost:3000").rstrip("/")


@dataclass
class SeoKeywordEntry:
    slug: str
    url_path: str
    modifier: str
    category_slug: str
    category: str
    keyword: str
    title: str
    heading: str
    description: str
    canonical_url: str
    og_title: str
    og_description: str
    og_url: str
    source: str


def _load_categories() -> list[dict[str, str]]:
    if not DB_PATH.exists():
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT name, slug FROM categories ORDER BY name").fetchall()
        return [{"name": row["name"], "slug": row["slug"]} for row in rows]
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def _load_templates() -> list[dict[str, str]]:
    if not TEMPLATES_PATH.exists():
        return []

    payload = json.loads(TEMPLATES_PATH.read_text())
    return payload.get("templates", [])


def _build_entries(categories: list[dict[str, str]], templates: list[dict[str, str]]) -> list[SeoKeywordEntry]:
    entries: list[SeoKeywordEntry] = []
    seen_slugs: set[str] = set()

    for category in categories:
        for template in templates:
            slug = template["slug"].format(category_slug=category["slug"])
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            title = template["title"].format(category=category["name"])
            heading = template["heading"].format(category=category["name"])
            description = template["description"].format(category=category["name"])
            url_path = f"/{slug}"
            canonical_url = f"{SITE_URL}{url_path}"

            entries.append(
                SeoKeywordEntry(
                    slug=slug,
                    url_path=url_path,
                    modifier=template["modifier"],
                    category_slug=category["slug"],
                    category=category["name"],
                    keyword=template["keyword"].format(category=category["name"]),
                    title=title,
                    heading=heading,
                    description=description,
                    canonical_url=canonical_url,
                    og_title=title,
                    og_description=description,
                    og_url=canonical_url,
                    source=template["source"],
                )
            )

    return entries


def generate() -> dict:
    categories = _load_categories()
    templates = _load_templates()
    entries = _build_entries(categories, templates)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "database": str(DB_PATH.relative_to(ROOT)),
        "templates": str(TEMPLATES_PATH.relative_to(ROOT)),
        "site_url": SITE_URL,
        "count": len(entries),
        "entries": [asdict(entry) for entry in entries],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


if __name__ == "__main__":
    data = generate()
    print(f"Generated {data['count']} SEO pages -> {OUTPUT_PATH}")
