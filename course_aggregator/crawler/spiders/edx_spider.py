"""edX course spider."""

from crawler.spiders.base_spider import BaseCourseSpider


class EdxSpider(BaseCourseSpider):
    name = "edx"
    platform = "edx"
    allowed_domains = ["www.edx.org", "edx.org"]
    start_urls = ["https://www.edx.org/search?q=computer+science"]
    course_link_patterns = (r"/learn/", r"/course/")
