"""Category normalization helpers for cross-provider consistency."""

from __future__ import annotations

import re


CATEGORY_CANONICAL_MAP = {
    # Artificial Intelligence bucket
    "ai": "Artificial Intelligence",
    "a.i.": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "machine learning": "Artificial Intelligence",
    "ml": "Artificial Intelligence",
    "deep learning": "Artificial Intelligence",
    "neural networks": "Artificial Intelligence",
}


def normalize_category_name(name: str) -> str:
    """Map provider-specific category labels to a canonical category name."""
    cleaned = re.sub(r"\s+", " ", (name or "").strip())
    if not cleaned:
        return ""

    key = cleaned.lower()
    if key in CATEGORY_CANONICAL_MAP:
        return CATEGORY_CANONICAL_MAP[key]

    # Fallback: title-case normalized text for consistent storage.
    return cleaned.title()


def normalize_category_list(categories: list[str]) -> list[str]:
    """Normalize category names and dedupe while preserving order."""
    normalized = [normalize_category_name(category) for category in categories]
    normalized = [value for value in normalized if value]
    return list(dict.fromkeys(normalized))
