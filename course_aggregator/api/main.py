"""FastAPI app exposing course_aggregator data."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.categories import router as categories_router
from api.routes.courses import router as courses_router
from api.routes.providers import router as providers_router

app = FastAPI(title="Course Aggregator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(courses_router)
app.include_router(categories_router)
app.include_router(providers_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
