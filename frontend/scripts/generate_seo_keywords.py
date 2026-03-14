"""Generate SEO keyword combinations from database categories."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "course_aggregator" / "database" / "courses.db"
OUTPUT_PATH = ROOT / "frontend" / "config" / "seo-keywords.json"

TEMPLATES = [
    {
        "modifier": "best",
        "keyword": "best {category} courses",
        "slug": "best-{category_slug}-courses",
        "title": "Best {category} Courses Online",
        "heading": "Best {category} Courses",
        "description": "Explore the best {category} courses from top online learning platforms.",
        "source": "category",
    },
    {
        "modifier": "free",
        "keyword": "free {category} courses",
        "slug": "free-{category_slug}-courses",
        "title": "Free {category} Courses Online",
        "heading": "Free {category} Courses",
        "description": "Discover free {category} courses you can start today.",
        "source": "search",
    },
    {
        "modifier": "beginner",
        "keyword": "beginner {category} courses",
        "slug": "beginner-{category_slug}-courses",
        "title": "Beginner {category} Courses Online",
        "heading": "Beginner {category} Courses",
        "description": "Start learning with beginner-friendly {category} courses for new learners.",
        "source": "search",
    },
    {
        "modifier": "advanced",
        "keyword": "advanced {category} courses",
        "slug": "advanced-{category_slug}-courses",
        "title": "Advanced {category} Courses Online",
        "heading": "Advanced {category} Courses",
        "description": "Level up your skills with advanced {category} courses and hands-on projects.",
        "source": "search",
    },
    {
        "modifier": "top_certifications",
        "keyword": "top {category} certifications",
        "slug": "top-{category_slug}-certifications",
        "title": "Top {category} Certifications Online",
        "heading": "Top {category} Certifications",
        "description": "Explore top {category} certifications and career-focused learning paths.",
        "source": "search",
    },
]


@dataclass
class SeoKeywordEntry:
    slug: str
    modifier: str
    category_slug: str
    category: str
    keyword: str
    title: str
    heading: str
    description: str
    source: str


def _load_categories() -> list[dict[str, str]]:
    if not DB_PATH.exists():
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT name, slug FROM categories ORDER BY name"
        ).fetchall()
        return [{"name": row["name"], "slug": row["slug"]} for row in rows]
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def _build_entries(categories: list[dict[str, str]]) -> list[SeoKeywordEntry]:
    entries: list[SeoKeywordEntry] = []
    for category in categories:
        for template in TEMPLATES:
            entries.append(
                SeoKeywordEntry(
                    slug=template["slug"].format(category_slug=category["slug"]),
                    modifier=template["modifier"],
                    category_slug=category["slug"],
                    category=category["name"],
                    keyword=template["keyword"].format(category=category["name"]),
                    title=template["title"].format(category=category["name"]),
                    heading=template["heading"].format(category=category["name"]),
                    description=template["description"].format(category=category["name"]),
                    source=template["source"],
                )
            )
    return entries


def generate() -> dict:
    categories = _load_categories()
    entries = _build_entries(categories)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "database": str(DB_PATH.relative_to(ROOT)),
        "count": len(entries),
        "entries": [asdict(entry) for entry in entries],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


if __name__ == "__main__":
    data = generate()
    print(f"Generated {data['count']} SEO keyword combinations -> {OUTPUT_PATH}")
