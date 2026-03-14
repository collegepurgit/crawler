"""Category API routes."""

from fastapi import APIRouter, HTTPException

from api.services.category_service import CategoryService
from api.services.db_service import get_courses_by_category

router = APIRouter(tags=["categories"])


@router.get("/categories")
def list_categories() -> dict[str, list[dict]]:
    categories = CategoryService.list_categories(limit=1000, offset=0)
    return {
        "categories": [
            {
                "name": category["name"],
                "slug": category["slug"],
            }
            for category in categories
        ]
    }


@router.get("/category/{slug}")
def get_category_courses(slug: str) -> dict[str, list[dict]]:
    courses = get_courses_by_category(category_slug=slug, limit=1000, offset=0)
    if not courses:
        known_categories = CategoryService.list_categories(limit=1000, offset=0)
        if slug not in {category["slug"] for category in known_categories}:
            raise HTTPException(status_code=404, detail="Category not found")
    return {"courses": courses}
