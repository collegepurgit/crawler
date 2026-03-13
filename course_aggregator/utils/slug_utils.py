"""Slug generation helpers for course titles."""

from __future__ import annotations

import re
import unicodedata


def slugify_title(title: str) -> str:
    """Convert a course title into an SEO-friendly slug."""
    normalized = unicodedata.normalize("NFKD", title or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.strip().lower()).strip("-")
    return slug or "course"
