"""Downloader middlewares for anti-blocking protections and dynamic-page routing."""

from __future__ import annotations

import random

from scrapy import Request
from scrapy_playwright.page import PageMethod


class UserAgentRotationMiddleware:
    """Rotate modern browser user-agents per request."""

    def __init__(self, user_agents: list[str]) -> None:
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist("USER_AGENT_POOL"))

    def process_request(self, request: Request, spider):
        if self.user_agents:
            request.headers[b"User-Agent"] = random.choice(self.user_agents).encode("utf-8")
        return None


class ProxyRotationMiddleware:
    """Apply optional rotating proxies when configured."""

    def __init__(self, proxies: list[str]) -> None:
        self.proxies = [proxy.strip() for proxy in proxies if proxy.strip()]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist("PROXY_LIST"))

    def process_request(self, request: Request, spider):
        if self.proxies:
            request.meta["proxy"] = random.choice(self.proxies)
        return None


class AutoPlaywrightMiddleware:
    """Route requests through Playwright when required by hints or URL patterns."""

    def __init__(self, patterns: list[str], wait_ms: int) -> None:
        self.patterns = [p.lower() for p in patterns]
        self.wait_ms = wait_ms

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            patterns=crawler.settings.getlist("PLAYWRIGHT_URL_PATTERNS"),
            wait_ms=crawler.settings.getint("PLAYWRIGHT_WAIT_MS", 1000),
        )

    def process_request(self, request: Request, spider):
        needs_js = bool(request.meta.get("requires_js")) or any(
            token in request.url.lower() for token in self.patterns
        )
        if needs_js and not request.meta.get("playwright"):
            request.meta["playwright"] = True
            request.meta.setdefault("playwright_context", "default")
            request.meta.setdefault("playwright_page_methods", [PageMethod("wait_for_timeout", self.wait_ms)])
        return None
