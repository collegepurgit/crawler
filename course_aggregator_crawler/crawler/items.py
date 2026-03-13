"""Scrapy items for course records."""

import scrapy


class CourseItem(scrapy.Item):
    source = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    provider = scrapy.Field()
    category = scrapy.Field()
    level = scrapy.Field()
    description = scrapy.Field()
    scraped_at = scrapy.Field()
