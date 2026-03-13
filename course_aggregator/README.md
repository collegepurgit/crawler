# course_aggregator

Production-ready Python 3.11 crawler for online course marketplaces (Coursera, Udemy, edX) using:

- Scrapy
- Playwright via `scrapy-playwright`
- SQLite

## Features

- Crawls both static HTML and JavaScript-rendered pages (React / Next.js / SPA).
- Automatic dynamic-page detection in base spider:
  - empty/near-empty HTML shell
  - React/Next.js framework markers
  - delayed rendering placeholders (loading/spinner/skeleton)
- Automatically retries dynamic pages with Playwright rendering when content is missing, heavy JS frameworks are detected, or content appears delayed.
- Pagination traversal, course-link auto-discovery, duplicate URL prevention, and crawl-depth limits.
- Dedicated extraction paths for listing pages and detail pages; both are converted to `CourseItem`.
- Category and instructor names are normalized and deduplicated before persistence.
- Automatic internal link discovery follows URLs containing: `course`, `learn`, `training`, `class`, `program`; external domains are ignored.
- Spider maintains an in-memory URL queue with duplicate prevention for crawl scheduling.
- Persists normalized course records in SQLite and JSONL.
- Rotating log files are written under `logs/` and include: crawler start, page crawled, course extracted, database insert, and errors.
- Persistence pipeline performs relational writes in order: provider -> course (dedup by `course_url`) -> categories -> instructors -> join-table relations.

## Project structure

```text
course_aggregator/
  crawler/
    spiders/
    items.py
    pipelines.py
    middlewares.py
    settings.py
  database/
    models.py
    database.py
  utils/
  logs/
  output/
  scrapy.cfg
  requirements.txt
  main.py
  README.md
```

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Run

```bash
cd course_aggregator
scrapy crawl coursera
scrapy crawl udemy
scrapy crawl edx

# optional seed URLs and depth limit
scrapy crawl coursera -a seed_urls="https://www.coursera.org/search?query=ml" -a max_depth=2
```

Or via entrypoint:

```bash
python main.py --provider coursera
python main.py --provider udemy
python main.py --provider edx
```

## Output

- SQLite DB: `database/courses.db`
- JSONL: `output/courses.jsonl`
- Logs: `logs/crawler.log`

## Notes

- Scrape responsibly and comply with robots.txt and website terms.
- Selectors may need updates if target site markup changes.


## Database schema

SQLite schema includes normalized relational tables:

- `providers(id, name, website, logo_url)`
- `courses(id, title, slug, provider_id, rating, description, image_url, course_url, created_at, updated_at)`
- `categories(id, name, slug)`
- `course_categories(course_id, category_id)`
- `instructors(id, name, profile_url)`
- `course_instructors(course_id, instructor_id)`

Constraints and indexes:

- unique `courses.course_url` prevents duplicate course records
- many-to-many mapping for categories and instructors
- indexes on `courses.slug`, `courses.provider_id`, `courses.rating`
