"""Scrapy settings for course aggregator crawler."""

from pathlib import Path

from crawler.middlewares.playwright_headers import playwright_context_kwargs

BOT_NAME = "course_aggregator_crawler"

SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"

ROBOTSTXT_OBEY = True

# Concurrency controls (general + Playwright specific)
CONCURRENT_REQUESTS = 12
CONCURRENT_REQUESTS_PER_DOMAIN = 6
DOWNLOAD_DELAY = 0.35
RANDOMIZE_DOWNLOAD_DELAY = True
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_TARGET_CONCURRENCY = 3.0

LOG_LEVEL = "INFO"
LOG_FILE = str(Path(__file__).resolve().parents[1] / "logs" / "crawler.log")

FEEDS = {
    str(Path(__file__).resolve().parents[1] / "output" / "courses.jsonl"): {
        "format": "jsonlines",
        "encoding": "utf8",
        "overwrite": True,
    }
}

ITEM_PIPELINES = {
    "crawler.pipelines.SQLitePipeline": 300,
}

SQLITE_DB_PATH = str(Path(__file__).resolve().parents[1] / "database" / "courses.db")

# Retry middleware for transient failures.
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# Rotating user-agents for request variance.
USER_AGENT_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

# Any URL containing one of these substrings will automatically use Playwright.
PLAYWRIGHT_JS_URL_PATTERNS = ["/app", "/learn", "?spa=1", "#/"]
PLAYWRIGHT_WAIT_MS = 1200

DOWNLOADER_MIDDLEWARES = {
    "crawler.middlewares.request_middlewares.RandomUserAgentMiddleware": 350,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,
    "crawler.middlewares.request_middlewares.AutoPlaywrightMiddleware": 560,
}

# Playwright configuration for dynamic JS pages.
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30_000
PLAYWRIGHT_MAX_CONTEXTS = 4
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4
PLAYWRIGHT_CONTEXTS = {"default": playwright_context_kwargs()}
