"""Provider API routes."""

from fastapi import APIRouter, HTTPException

from api.services.db_service import get_courses_by_provider
from api.services.provider_service import ProviderService

router = APIRouter(tags=["providers"])


@router.get("/providers")
def list_providers() -> dict[str, list[dict]]:
    providers = ProviderService.list_providers(limit=1000, offset=0)
    return {
        "providers": [
            {
                "name": provider["name"],
                "website": provider["website"],
            }
            for provider in providers
        ]
    }


@router.get("/provider/{name}")
def get_provider_courses(name: str) -> dict[str, list[dict]]:
    courses = get_courses_by_provider(provider_name=name, limit=1000, offset=0)
    if not courses:
        known_providers = ProviderService.list_providers(limit=1000, offset=0)
        if name not in {provider["name"] for provider in known_providers}:
            raise HTTPException(status_code=404, detail="Provider not found")
    return {"courses": courses}
