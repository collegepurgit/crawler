"""Custom middleware package."""

from crawler.middlewares.request_middlewares import (  # noqa: F401
    AutoPlaywrightMiddleware,
    RandomUserAgentMiddleware,
)
