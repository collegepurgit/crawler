"""Spider for JavaScript-rendered course listing/detail pages."""

from __future__ import annotations

from crawler.spiders.base_courses_spider import BaseCoursesSpider


class DynamicCoursesSpider(BaseCoursesSpider):
    name = "dynamic_courses"
    source_name = "dynamic"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/app/courses"]
    max_depth = 2

    def make_request(self, url: str, depth: int, requires_js: bool = False, dont_filter: bool = False):
        return super().make_request(url=url, depth=depth, requires_js=True, dont_filter=dont_filter)
