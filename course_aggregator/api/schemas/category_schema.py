"""Category response schemas."""

from pydantic import BaseModel


class CategorySchema(BaseModel):
    id: int
    name: str
    slug: str
