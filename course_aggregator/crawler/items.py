"""Scrapy items for extracted course aggregation data."""

import scrapy


class ProviderItem(scrapy.Item):
    name = scrapy.Field()
    website = scrapy.Field()
    logo_url = scrapy.Field()


class CategoryItem(scrapy.Item):
    name = scrapy.Field()
    slug = scrapy.Field()


class InstructorItem(scrapy.Item):
    name = scrapy.Field()
    profile_url = scrapy.Field()


class CourseItem(scrapy.Item):
    # Required fields
    course_title = scrapy.Field()
    title = scrapy.Field()
    provider = scrapy.Field()  # provider name
    rating = scrapy.Field()
    image_url = scrapy.Field()
    course_url = scrapy.Field()
    description = scrapy.Field()
    categories = scrapy.Field()  # list[str] or list[CategoryItem-compatible dicts]
    instructors = scrapy.Field()  # list[str] or list[InstructorItem-compatible dicts]

    # Optional normalized/compatibility fields used by pipeline/storage.
    slug = scrapy.Field()
    provider_name = scrapy.Field()
    provider_website = scrapy.Field()
    provider_logo_url = scrapy.Field()

    # Backward-compatible aliases.
    platform = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
