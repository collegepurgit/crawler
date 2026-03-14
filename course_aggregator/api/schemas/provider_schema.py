"""Provider response schemas."""

from pydantic import BaseModel


class ProviderSchema(BaseModel):
    id: int
    name: str
    website: str | None = None
    logo_url: str | None = None
