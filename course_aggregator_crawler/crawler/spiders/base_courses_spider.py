"""Reusable base spider for crawling course listing and detail pages."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import scrapy

from crawler.items import CourseItem


class BaseCoursesSpider(scrapy.Spider):
    """Base spider that handles seed URLs, pagination, dedupe, depth limits, and JS fallback."""

    source_name = "base"
    start_urls: list[str] = []
    max_depth = 2

    listing_card_selectors: tuple[str, ...] = (
        "article.course-card",
        "div[data-testid='course-card']",
        ".course-card",
    )
    pagination_selectors: tuple[str, ...] = (
        "a.next::attr(href)",
        "a[rel='next']::attr(href)",
        ".pagination a.next::attr(href)",
    )

    title_selectors: tuple[str, ...] = ("h1::text", "[data-testid='course-title']::text")
    provider_selectors: tuple[str, ...] = (".provider::text", "[data-testid='course-provider']::text")
    category_selectors: tuple[str, ...] = (".category::text", "[data-testid='course-category']::text")
    level_selectors: tuple[str, ...] = (".level::text", "[data-testid='course-level']::text")
    description_selectors: tuple[str, ...] = (
        ".description::text",
        "[data-testid='course-description']::text",
        "meta[name='description']::attr(content)",
    )

    course_url_patterns: tuple[re.Pattern[str], ...] = (
        re.compile(r"/course[s]?/", re.IGNORECASE),
        re.compile(r"/learn/", re.IGNORECASE),
        re.compile(r"/class(es)?/", re.IGNORECASE),
    )

    # Dynamic-page indicators
    dynamic_markers: tuple[str, ...] = (
        "__next",
        "_next/static",
        "data-reactroot",
        "reactdom",
        "id=\"root\"",
        "id='root'",
        "id=\"__next\"",
        "window.__next_data__",
        "webpack",
    )
    delayed_render_markers: tuple[str, ...] = ("loading", "spinner", "skeleton", "shimmer")

    def __init__(self, seed_urls: str | None = None, max_depth: int | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seed_urls = self._parse_seed_urls(seed_urls)
        self.max_depth = int(max_depth) if max_depth is not None else int(self.max_depth)
        self._seen_request_urls: set[str] = set()
        self._seen_course_urls: set[str] = set()
        self._js_retry_urls: set[str] = set()

    def start_requests(self):
        seeds = self.seed_urls or list(self.start_urls)
        for url in seeds:
            normalized_url = self._normalize_url(url)
            if normalized_url in self._seen_request_urls:
                continue
            self._seen_request_urls.add(normalized_url)
            yield self.make_request(normalized_url, depth=0)

    def make_request(self, url: str, depth: int, requires_js: bool = False, dont_filter: bool = False):
        meta = {"depth": depth}
        if requires_js:
            meta["requires_js"] = True
        return scrapy.Request(url=url, callback=self.parse, meta=meta, dont_filter=dont_filter)

    def parse(self, response: scrapy.http.Response):
        depth = int(response.meta.get("depth", 0))

        # Automatically escalate to Playwright when page looks JS-rendered.
        if self._should_switch_to_playwright(response):
            retry_url = self._normalize_url(response.url)
            self._js_retry_urls.add(retry_url)
            yield self.make_request(
                retry_url,
                depth=depth,
                requires_js=True,
                dont_filter=True,
            )
            return

        if self._is_course_detail_page(response):
            item = self.extract_course_item(response)
            if item:
                normalized_url = self._normalize_url(item["url"])
                if normalized_url not in self._seen_course_urls:
                    self._seen_course_urls.add(normalized_url)
                    yield item

        if depth >= self.max_depth:
            return

        for href in self._extract_pagination_links(response):
            next_url = self._normalize_url(response.urljoin(href))
            if next_url in self._seen_request_urls:
                continue
            self._seen_request_urls.add(next_url)
            yield self.make_request(next_url, depth=depth + 1)

        for href in self._extract_course_links(response):
            detail_url = self._normalize_url(response.urljoin(href))
            if detail_url in self._seen_request_urls:
                continue
            self._seen_request_urls.add(detail_url)
            yield self.make_request(detail_url, depth=depth + 1)

    def extract_course_item(self, response: scrapy.http.Response) -> CourseItem | None:
        title = self._first_text(response, self.title_selectors)
        description = self._first_text(response, self.description_selectors)

        if not title and not description:
            return None

        return CourseItem(
            source=self.source_name,
            url=self._normalize_url(response.url),
            title=title,
            provider=self._first_text(response, self.provider_selectors),
            category=self._first_text(response, self.category_selectors),
            level=self._first_text(response, self.level_selectors),
            description=description,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )

    def _extract_pagination_links(self, response: scrapy.http.Response) -> list[str]:
        links: list[str] = []
        for selector in self.pagination_selectors:
            links.extend(response.css(selector).getall())
        return [link for link in links if link]

    def _extract_course_links(self, response: scrapy.http.Response) -> list[str]:
        candidates: set[str] = set()

        for selector in self.listing_card_selectors:
            for node in response.css(selector):
                href = node.css("a::attr(href)").get()
                if href:
                    candidates.add(href)

        for anchor in response.css("a"):
            href = anchor.css("::attr(href)").get()
            anchor_text = " ".join(part.strip() for part in anchor.css("::text").getall() if part.strip())
            if href and self._looks_like_course_link(response.urljoin(href), anchor_text=anchor_text):
                candidates.add(href)

        return list(candidates)

    def _is_course_detail_page(self, response: scrapy.http.Response) -> bool:
        if any(response.css(selector).get() for selector in self.listing_card_selectors):
            return False

        current_url = response.url
        if any(pattern.search(current_url) for pattern in self.course_url_patterns):
            return True

        has_title = bool(self._first_text(response, self.title_selectors))
        has_description = bool(self._first_text(response, self.description_selectors))
        return has_title and has_description

    def _should_switch_to_playwright(self, response: scrapy.http.Response) -> bool:
        # Already Playwright-rendered or already retried once.
        if response.meta.get("playwright") is True:
            return False

        normalized_url = self._normalize_url(response.url)
        if normalized_url in self._js_retry_urls:
            return False

        text = response.text or ""
        html_lower = text.lower()

        # Indicator 1: mostly-empty HTML shell.
        body_text = " ".join(response.css("body *::text").getall()).strip()
        if not body_text and len(text.strip()) < 3000:
            return True

        # Indicator 2: heavy JS framework markers.
        if any(marker in html_lower for marker in self.dynamic_markers):
            # If content is not present, this is likely a JS app shell.
            if not self._extract_course_links(response) and not self._is_course_detail_page(response):
                return True

        # Indicator 3: delayed rendering placeholders.
        delayed_marker_found = any(marker in html_lower for marker in self.delayed_render_markers)
        if delayed_marker_found and not self._extract_course_links(response) and not self._is_course_detail_page(response):
            return True

        return False

    def _looks_like_course_link(self, url: str, anchor_text: str) -> bool:
        if not url:
            return False
        if any(pattern.search(url) for pattern in self.course_url_patterns):
            return True
        lowered_text = anchor_text.lower()
        return "course" in lowered_text or "learn" in lowered_text

    def _first_text(self, response: scrapy.http.Response, selectors: tuple[str, ...]) -> str:
        for selector in selectors:
            value = response.css(selector).get(default="")
            if value and value.strip():
                return value.strip()
        return ""

    def _parse_seed_urls(self, seed_urls: str | None) -> list[str]:
        if not seed_urls:
            return []
        return [part.strip() for part in seed_urls.split(",") if part.strip()]

    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        normalized_path = parsed.path or "/"
        return parsed._replace(fragment="", path=normalized_path).geturl()
