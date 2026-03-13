"""Reusable base spider that crawls static and dynamic course pages."""

from __future__ import annotations

import re
from collections import deque
from urllib.parse import urlparse

import scrapy

from crawler.items import CourseItem


class BaseCourseSpider(scrapy.Spider):
    """Base spider with pagination, link discovery, depth limits, and JS fallback."""

    platform = "generic"
    start_urls: list[str] = []
    allowed_domains: list[str] = []
    max_depth = 2

    listing_selectors: tuple[str, ...] = (
        "article",
        "li.course-card",
        "div[data-testid='course-card']",
        ".course-listing-card",
        "[data-testid='course-card']",
    )
    pagination_selectors: tuple[str, ...] = (
        "a.next::attr(href)",
        "a[rel='next']::attr(href)",
        ".pagination a::attr(href)",
    )

    title_selectors: tuple[str, ...] = (
        "h1::text",
        "meta[property='og:title']::attr(content)",
        "[data-purpose='lead-title']::text",
        "[data-testid='course-title']::text",
    )
    description_selectors: tuple[str, ...] = (
        "meta[name='description']::attr(content)",
        "[data-testid='description']::text",
        ".course-description::text",
    )
    provider_selectors: tuple[str, ...] = (
        ".provider::text",
        "[data-testid='partner-name']::text",
        "[data-purpose='instructor-name-top']::text",
    )
    image_selectors: tuple[str, ...] = (
        "meta[property='og:image']::attr(content)",
        "img.course-image::attr(src)",
        "img::attr(src)",
    )

    dynamic_framework_markers = (
        "__next",
        "_next/static",
        "window.__next_data__",
        "window.__nuxt",
        "data-reactroot",
        "reactdom",
        "webpack",
        "chunk.js",
        "vite",
    )
    delayed_render_markers = (
        "loading",
        "spinner",
        "skeleton",
        "shimmer",
        "placeholder",
        "is-loading",
        "lazyload",
    )
    # Automatic link discovery rules.
    discover_link_keywords = ("course", "learn", "training", "class", "program")

    def __init__(self, seed_urls: str | None = None, max_depth: int | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seed_urls = [u.strip() for u in (seed_urls or "").split(",") if u.strip()]
        if max_depth is not None:
            self.max_depth = int(max_depth)
        self.seen_urls: set[str] = set()
        self.js_retries: set[str] = set()
        self.emitted_course_urls: set[str] = set()
        self.pending_urls: deque[tuple[str, int, bool, bool]] = deque()

    def start_requests(self):
        urls = self.seed_urls or list(self.start_urls)
        for url in urls:
            self._enqueue_url(url=self._normalize(url), depth=0)
        yield from self._drain_queue()

    def _request(self, url: str, depth: int, requires_js: bool = False, dont_filter: bool = False):
        meta = {"depth": depth}
        if requires_js:
            meta["requires_js"] = True
        return scrapy.Request(url=url, callback=self.parse, meta=meta, dont_filter=dont_filter)

    def _enqueue_url(self, url: str, depth: int, requires_js: bool = False, dont_filter: bool = False) -> None:
        normalized = self._normalize(url)
        if not normalized:
            return
        if not self._is_internal_url(normalized):
            return
        if normalized in self.seen_urls:
            return
        self.seen_urls.add(normalized)
        self.pending_urls.append((normalized, depth, requires_js, dont_filter))

    def _drain_queue(self):
        while self.pending_urls:
            url, depth, requires_js, dont_filter = self.pending_urls.popleft()
            yield self._request(url=url, depth=depth, requires_js=requires_js, dont_filter=dont_filter)

    def parse(self, response: scrapy.http.Response):
        depth = int(response.meta.get("depth", 0))

        if self._should_use_playwright(response):
            normalized = self._normalize(response.url)
            if normalized not in self.js_retries:
                self.js_retries.add(normalized)
                yield self._request(normalized, depth=depth, requires_js=True, dont_filter=True)
                return

        if self._is_listing_page(response):
            for item in self.parse_listing_page(response):
                if item["course_url"] not in self.emitted_course_urls:
                    self.emitted_course_urls.add(item["course_url"])
                    yield item
        else:
            item = self.parse_detail_page(response)
            if item and item["course_url"] not in self.emitted_course_urls:
                self.emitted_course_urls.add(item["course_url"])
                yield item

        if depth >= self.max_depth:
            return

        for next_link in self._extract_pagination_links(response):
            self._enqueue_url(url=response.urljoin(next_link), depth=depth + 1)

        for discovered_link in self._discover_links(response):
            self._enqueue_url(url=response.urljoin(discovered_link), depth=depth + 1)

        yield from self._drain_queue()

    def parse_listing_page(self, response: scrapy.http.Response):
        for selector in self.listing_selectors:
            cards = response.css(selector)
            if not cards:
                continue
            for card in cards:
                title = self._first_node(card, ("h2::text", "h3::text", "[data-testid='course-title']::text"))
                course_url = self._normalize(response.urljoin(card.css("a::attr(href)").get(default="")))
                if not course_url:
                    continue
                provider_name = self._normalize_name(
                    self._first_node(card, (".provider::text", "[data-testid='partner-name']::text")) or self.platform
                )
                item = CourseItem(
                    course_title=title,
                    title=title,
                    provider_name=provider_name,
                    provider=provider_name,
                    rating=self._normalize_rating(self._first_node(card, (".rating::text", "[data-testid='rating']::text"))),
                    course_url=course_url,
                    image_url=response.urljoin(
                        self._first_node(card, ("img::attr(src)", "img::attr(data-src)", "img::attr(srcset)"))
                    ),
                    description=self._normalize_text(
                        self._first_node(card, (".description::text", ".subtitle::text", "[data-testid='description']::text"))
                    ),
                    categories=self._normalize_name_list(self._node_all(card, (".category::text", ".topic::text"))),
                    instructors=self._normalize_name_list(
                        self._node_all(card, (".instructor::text", "[data-testid='instructor-name']::text"))
                    ),
                    url=course_url,
                )
                yield item
            break

    def parse_detail_page(self, response: scrapy.http.Response) -> CourseItem | None:
        title = self._normalize_text(self._first(response, self.title_selectors))
        description = self._normalize_text(self._first(response, self.description_selectors))
        if not title and not description:
            return None

        provider_name = self._normalize_name(self._first(response, self.provider_selectors) or self.platform)
        categories = self._normalize_name_list(self._extract_categories(response))
        instructors = self._normalize_name_list(self._extract_instructors(response))

        return CourseItem(
            course_title=title,
            title=title,
            provider_name=provider_name,
            provider=provider_name,
            rating=self._normalize_rating(self._safe_css(response, ".rating::text")),
            image_url=response.urljoin(self._first(response, self.image_selectors)),
            course_url=self._normalize(response.url),
            description=description,
            categories=categories,
            instructors=instructors,
            url=self._normalize(response.url),
        )

    def _is_listing_page(self, response: scrapy.http.Response) -> bool:
        return any(response.css(selector) for selector in self.listing_selectors)

    def _extract_pagination_links(self, response: scrapy.http.Response) -> list[str]:
        links: list[str] = []
        for selector in self.pagination_selectors:
            links.extend(response.css(selector).getall())
        return [link for link in links if link]

    def _discover_links(self, response: scrapy.http.Response) -> list[str]:
        out: set[str] = set()

        for selector in self.listing_selectors:
            for node in response.css(selector):
                href = node.css("a::attr(href)").get()
                if href:
                    out.add(href)

        for anchor in response.css("a"):
            href = anchor.css("::attr(href)").get()
            if not href:
                continue
            text = " ".join(t.strip() for t in anchor.css("::text").getall() if t.strip()).lower()
            full_url = response.urljoin(href).lower()
            if any(keyword in full_url for keyword in self.discover_link_keywords) or any(
                keyword in text for keyword in self.discover_link_keywords
            ):
                out.add(href)

        return list(out)

    def _should_use_playwright(self, response: scrapy.http.Response) -> bool:
        if response.meta.get("playwright") is True:
            return False

        normalized = self._normalize(response.url)
        if normalized in self.js_retries:
            return False

        html = (response.text or "").lower()
        text_tokens = [t.strip() for t in response.css("body *::text").getall() if t.strip()]
        visible_text_len = len(" ".join(text_tokens))

        has_links = bool(self._discover_links(response))
        has_course_content = bool(self.parse_detail_page(response))

        if visible_text_len < 80 and len(html.strip()) < 3000:
            return True

        framework_detected = any(marker in html for marker in self.dynamic_framework_markers)
        if framework_detected and not has_links and not has_course_content:
            return True

        delayed_detected = any(marker in html for marker in self.delayed_render_markers)
        script_count = len(response.css("script").getall())
        if delayed_detected and script_count >= 3 and not has_links and not has_course_content:
            return True

        return False

    def _extract_categories(self, response: scrapy.http.Response) -> list[str]:
        selectors = (
            ".category::text",
            "[data-testid='category']::text",
            "a[href*='topic']::text",
            "a[href*='subject']::text",
        )
        values: list[str] = []
        for selector in selectors:
            values.extend([v.strip() for v in response.css(selector).getall() if v.strip()])
        return values

    def _extract_instructors(self, response: scrapy.http.Response) -> list[str]:
        selectors = (
            ".instructor::text",
            "[data-purpose='instructor-name-top']::text",
            "[data-testid='instructor-name']::text",
        )
        values: list[str] = []
        for selector in selectors:
            values.extend([v.strip() for v in response.css(selector).getall() if v.strip()])
        return values

    def _first(self, response: scrapy.http.Response, selectors: tuple[str, ...]) -> str:
        for selector in selectors:
            value = response.css(selector).get(default="").strip()
            if value:
                return value
        return ""

    def _first_node(self, node: scrapy.Selector, selectors: tuple[str, ...]) -> str:
        for selector in selectors:
            value = node.css(selector).get(default="").strip()
            if value:
                return value
        return ""

    def _node_all(self, node: scrapy.Selector, selectors: tuple[str, ...]) -> list[str]:
        values: list[str] = []
        for selector in selectors:
            values.extend(node.css(selector).getall())
        return values

    def _safe_css(self, response: scrapy.http.Response, selector: str) -> str:
        return response.css(selector).get(default="").strip()

    def _normalize(self, url: str) -> str:
        if not url:
            return ""
        parsed = urlparse(url)
        return parsed._replace(fragment="").geturl()

    def _is_internal_url(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme and parsed.scheme not in {"http", "https"}:
            return False
        if not parsed.netloc:
            return True

        host = parsed.netloc.lower()
        if self.allowed_domains:
            allowed = [d.lower() for d in self.allowed_domains]
            return any(host == domain or host.endswith(f".{domain}") for domain in allowed)

        seed_hosts = [urlparse(seed).netloc.lower() for seed in (self.seed_urls or self.start_urls)]
        return not seed_hosts or any(host == domain or host.endswith(f".{domain}") for domain in seed_hosts)

    def _normalize_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", (value or "").strip())

    def _normalize_name(self, value: str) -> str:
        return self._normalize_text(value).title()

    def _normalize_name_list(self, values: list[str]) -> list[str]:
        normalized = [self._normalize_name(v) for v in values if self._normalize_text(v)]
        return list(dict.fromkeys(normalized))

    def _normalize_rating(self, value: str) -> str:
        text = self._normalize_text(value)
        match = re.search(r"\d+(?:\.\d+)?", text)
        return match.group(0) if match else ""
