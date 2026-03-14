# course_aggregator

Production-ready Python 3.11 crawler for online course marketplaces (Coursera, Udemy, edX) using:

- Scrapy
- Playwright via `scrapy-playwright`
- SQLite

## Features

- This repository keeps `course_aggregator/` as the single maintained project (legacy duplicate scaffold removed).
- Crawls both static HTML and JavaScript-rendered pages (React / Next.js / SPA).
- Anti-blocking protections include randomized 1-3s delays, UA rotation (Chrome/Firefox/Safari/Edge), reduced concurrency, retry policy, AutoThrottle, and optional proxy rotation.
- Automatic dynamic-page detection in base spider:
  - empty/near-empty HTML shell
  - React/Next.js framework markers
  - delayed rendering placeholders (loading/spinner/skeleton)
- Automatically retries dynamic pages with Playwright rendering when content is missing, heavy JS frameworks are detected, or content appears delayed.
- Pagination traversal, course-link auto-discovery, duplicate URL prevention, and crawl-depth limits.
- Dedicated extraction paths for listing pages and detail pages; both are converted to `CourseItem`.
- Category and instructor names are normalized and deduplicated before persistence.
- Category names are normalized via `utils/category_normalizer.py` (e.g., AI/Machine Learning -> Artificial Intelligence) before category persistence.
- Automatic internal link discovery follows URLs containing: `course`, `learn`, `training`, `class`, `program`; external domains are ignored.
- Spider maintains an in-memory URL queue with duplicate prevention for crawl scheduling.
- Default Scrapy depth setting is `DEPTH_LIMIT = 3` (overridable per run with `--max-depth`).
- Persists normalized course records in SQLite and JSONL.
- Rotating log files are written under `logs/` and include: crawler start, page crawled, course extracted, database insert, and errors.
- Scheduler mode runs providers sequentially every 24 hours, tracks last crawl time in `logs/last_crawl.json`, logs results, and prevents overlapping runs.
- Persistence pipeline performs relational writes in order: provider -> course (dedup by `course_url`) -> categories -> instructors -> join-table relations.
- SEO-friendly slugs are generated from course titles via `utils/slug_utils.py` and made unique before storing in `courses.slug`.

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

# scheduled mode (runs coursera -> udemy -> edx every 24h)
python main.py --schedule
```


## API (FastAPI)

A backend API is available under `api/`, connected to `database/courses.db` with CORS enabled for frontend access.

Run API server:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints:

- `GET /health`
- `GET /courses?limit=100&offset=0`
- `GET /categories`
- `GET /providers`

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
