"""Spider for static HTML course listing/detail pages."""

from __future__ import annotations

from crawler.spiders.base_courses_spider import BaseCoursesSpider


class StaticCoursesSpider(BaseCoursesSpider):
    name = "static_courses"
    source_name = "static"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/courses"]
    max_depth = 2
