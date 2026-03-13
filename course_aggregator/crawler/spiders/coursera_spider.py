"""Coursera course spider."""

from crawler.spiders.base_spider import BaseCourseSpider


class CourseraSpider(BaseCourseSpider):
    name = "coursera"
    platform = "coursera"
    allowed_domains = ["www.coursera.org", "coursera.org"]
    start_urls = ["https://www.coursera.org/search?query=data"]
    course_link_patterns = (r"/learn/", r"/professional-certificates/", r"/specializations/")
