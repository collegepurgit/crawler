"""Data model definitions for relational persistence layer."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InstructorRecord:
    name: str
    profile_url: str = ""


@dataclass(slots=True)
class CourseRecord:
    title: str
    slug: str
    provider_name: str
    provider_website: str
    provider_logo_url: str
    rating: float | None
    description: str
    image_url: str
    course_url: str
    categories: list[str] = field(default_factory=list)
    instructors: list[InstructorRecord] = field(default_factory=list)
