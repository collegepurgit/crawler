"""Udemy course spider."""

from crawler.spiders.base_spider import BaseCourseSpider


class UdemySpider(BaseCourseSpider):
    name = "udemy"
    platform = "udemy"
    allowed_domains = ["www.udemy.com", "udemy.com"]
    start_urls = ["https://www.udemy.com/courses/search/?q=python"]
    course_link_patterns = (r"/course/",)
