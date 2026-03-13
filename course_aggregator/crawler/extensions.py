"""Crawler logging extensions based on Scrapy signals."""

from __future__ import annotations

import logging

from scrapy import signals

logger = logging.getLogger(__name__)


class CrawlLoggingExtension:
    """Emit high-level crawl lifecycle logs."""

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.response_received, signal=signals.response_received)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.spider_error, signal=signals.spider_error)
        return ext

    def spider_opened(self, spider):
        logger.info("crawler start | spider=%s", spider.name)

    def response_received(self, response, request, spider):
        logger.info("page crawled | spider=%s url=%s status=%s", spider.name, response.url, response.status)

    def item_scraped(self, item, response, spider):
        course_url = item.get("course_url") or item.get("url") or ""
        logger.info("course extracted | spider=%s course_url=%s", spider.name, course_url)

    def spider_error(self, failure, response, spider):
        logger.error(
            "errors | spider=%s url=%s error=%s",
            spider.name,
            response.url if response else "",
            failure.getErrorMessage(),
        )
