# course_aggregator_crawler

Production-ready Scrapy project that can crawl both:

1. **Static HTML course pages**
2. **Dynamic JavaScript (React / SPA) course pages** via Playwright

## Stack

- Python 3.11
- Scrapy
- scrapy-playwright + Playwright (Chromium)
- SQLite
- Python `logging` module

## Project structure

```text
course_aggregator_crawler/
    crawler/
        spiders/
        middlewares/
    database/
    utils/
    logs/
    output/
    scrapy.cfg
    requirements.txt
    README.md
```

## Quick start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Base spider (reusable)

`crawler/spiders/base_courses_spider.py` provides reusable crawling behavior:

- accepts seed URLs (`-a seed_urls="https://site/a,https://site/b"`)
- supports pagination detection/following
- auto-detects course links from listing cards and URL/text heuristics
- prevents duplicate crawling and duplicate course item emission
- limits crawl depth (`-a max_depth=2`)
- handles both listing pages and detail pages
- returns structured `CourseItem` objects

## Playwright integration (enabled)

This project is configured for async Scrapy + Playwright crawling:

- `TWISTED_REACTOR` uses `AsyncioSelectorReactor`
- `scrapy_playwright` download handlers are enabled for `http/https`
- Retry middleware is enabled with production-safe retry codes
- Concurrency controls are configured for both Scrapy and Playwright
- Random user-agent rotation is enabled via downloader middleware
- Automatic Playwright routing is enabled for JavaScript pages:
- Automatic dynamic-page detection in the base spider triggers Playwright when pages look JS-rendered (empty HTML shell, React/Next.js markers, or loading-placeholder responses)
  - any request with `meta={"requires_js": True}`
  - any request URL matching `PLAYWRIGHT_JS_URL_PATTERNS`

## Run spiders

From project root (`course_aggregator_crawler/`):

```bash
scrapy crawl static_courses
scrapy crawl dynamic_courses

# override defaults for any spider
scrapy crawl static_courses -a seed_urls="https://example.com/courses,https://example.com/learn" -a max_depth=3
```

## Output

- JSON Lines export: `output/courses.jsonl`
- SQLite database: `database/courses.db`
- Log file: `logs/crawler.log`

## Notes for adapting to real targets

- Tune selectors in `BaseCoursesSpider` or override them in child spiders.
- Replace `allowed_domains` and `start_urls` with target course websites.
- Tune user-agent pool, URL JS patterns, and concurrency in `crawler/settings.py`.
- Keep `ROBOTSTXT_OBEY = True` and respect each website's terms of service.
