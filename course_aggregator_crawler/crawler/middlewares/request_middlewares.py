"""Downloader middlewares for automatic Playwright routing and user-agent rotation."""

from __future__ import annotations

import random
from scrapy import Request
from scrapy_playwright.page import PageMethod


class RandomUserAgentMiddleware:
    """Assign a random user-agent header when missing."""

    def __init__(self, user_agents: list[str]) -> None:
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        user_agents = crawler.settings.getlist("USER_AGENT_POOL")
        if not user_agents:
            raise ValueError("USER_AGENT_POOL must contain at least one user-agent string")
        return cls(user_agents=user_agents)

    def process_request(self, request: Request, spider):
        if b"User-Agent" not in request.headers:
            request.headers[b"User-Agent"] = random.choice(self.user_agents).encode("utf-8")
        return None


class AutoPlaywrightMiddleware:
    """Enable Playwright automatically for JavaScript-heavy page patterns."""

    def __init__(self, js_patterns: list[str], wait_ms: int) -> None:
        self.js_patterns = [pattern.lower() for pattern in js_patterns]
        self.wait_ms = wait_ms

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            js_patterns=crawler.settings.getlist("PLAYWRIGHT_JS_URL_PATTERNS"),
            wait_ms=crawler.settings.getint("PLAYWRIGHT_WAIT_MS", 1200),
        )

    def process_request(self, request: Request, spider):
        if request.meta.get("playwright") is True:
            return None

        requires_js = request.meta.get("requires_js", False)
        if not requires_js and self._matches_js_pattern(request.url):
            requires_js = True

        if requires_js:
            request.meta["playwright"] = True
            request.meta.setdefault("playwright_context", "default")
            request.meta.setdefault(
                "playwright_page_methods",
                [PageMethod("wait_for_timeout", self.wait_ms)],
            )
        return None

    def _matches_js_pattern(self, url: str) -> bool:
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.js_patterns)
