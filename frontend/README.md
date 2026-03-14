# Course Aggregator Frontend

Modern Next.js + Tailwind CSS frontend for the Course Aggregation platform.

## Tech Stack

- Next.js (JavaScript)
- Tailwind CSS
- Server-side rendering (SSR) with `getServerSideProps`

## API Backend

This frontend connects to the FastAPI backend at:

- `http://localhost:8000`

You can override this with:

- `NEXT_PUBLIC_API_BASE_URL`

## Run locally

```bash
npm install
npm run dev
```

Open: `http://localhost:3000`

## Build for production

```bash
npm run build
npm run start
```


## Programmatic SEO pages

Dynamic SEO landing pages are generated through a dynamic route and support pagination:

- `/best-[category]-courses`
- `/free-[category]-courses`
- `/beginner-[category]-courses`

Examples:

- `/best-ai-courses`
- `/best-python-courses`
- `/free-data-science-courses`

Each SEO page includes:

- H1 heading
- Intro paragraph
- Course listing (top rated first)
- FAQ section

Generate SEO keyword combinations from DB categories:

```bash
npm run seo:generate
```


## Sitemap

A dynamic XML sitemap system is available at:

- `/sitemap.xml` (sitemap index)
- `/sitemaps/static.xml` (homepage, index pages, category/provider pages, SEO keyword pages)
- `/sitemaps/courses-1.xml`, `/sitemaps/courses-2.xml`, ... (chunked course pages)

It is generated server-side from live API/database-backed records and SEO config, so new courses/categories/providers are reflected automatically. Course URLs are chunked to support thousands of pages.


SEO metadata fields generated per SEO page:

- page title
- meta description
- canonical URL
- OpenGraph title/description/url
