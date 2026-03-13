"""Course response schemas."""

from pydantic import BaseModel


class CourseSchema(BaseModel):
    id: int
    title: str
    slug: str
    provider_id: int
    provider_name: str
    rating: float | None = None
    description: str | None = None
    image_url: str | None = None
    course_url: str
    created_at: str
    updated_at: str
