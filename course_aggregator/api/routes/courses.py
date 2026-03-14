"""Course API routes."""

from fastapi import APIRouter, HTTPException, Query

from api.services.db_service import (
    get_course_by_slug,
    get_courses,
    get_courses_by_category,
    get_courses_by_provider,
    get_courses_total,
    search_courses,
)

router = APIRouter(tags=["courses"])


@router.get("/courses")
def list_courses(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    category: str | None = Query(default=None),
    provider: str | None = Query(default=None),
) -> dict[str, list[dict]]:
    if category and provider:
        courses = get_courses(limit=limit, offset=offset, category=category, provider=provider)
        total = get_courses_total(category=category, provider=provider)
    elif category:
        courses = get_courses_by_category(category_slug=category, limit=limit, offset=offset)
        total = get_courses_total(category=category)
    elif provider:
        courses = get_courses_by_provider(provider_name=provider, limit=limit, offset=offset)
        total = get_courses_total(provider=provider)
    else:
        courses = get_courses(limit=limit, offset=offset)
        total = get_courses_total()

    return {"total": total, "limit": limit, "offset": offset, "courses": courses}


@router.get("/course/{slug}")
def get_course(slug: str) -> dict:
    course = get_course_by_slug(slug)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/search")
def search(q: str = Query(..., min_length=1)) -> dict[str, list[dict]]:
    return {"courses": search_courses(q)}
