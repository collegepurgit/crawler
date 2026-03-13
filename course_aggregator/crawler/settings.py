"""Scrapy settings for course aggregator."""

from pathlib import Path

BOT_NAME = "course_aggregator"
SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"

ROBOTSTXT_OBEY = True

# Concurrency control (anti-blocking)
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# Randomized delay: with RANDOMIZE_DOWNLOAD_DELAY=True this becomes ~1-3s.
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

DEPTH_LIMIT = 3

# Retry system
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 429]

# User-agent rotation pool (Chrome, Firefox, Safari, Edge)
USER_AGENT_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
]

# Optional proxy rotation. Keep empty to disable.
PROXY_LIST = []

DOWNLOADER_MIDDLEWARES = {
    "crawler.middlewares.UserAgentRotationMiddleware": 350,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,
    "crawler.middlewares.AutoPlaywrightMiddleware": 560,
    "crawler.middlewares.ProxyRotationMiddleware": 740,
    "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 750,
}

ITEM_PIPELINES = {"crawler.pipelines.SQLitePipeline": 300}
EXTENSIONS = {
    "crawler.extensions.CrawlLoggingExtension": 500,
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = str(LOG_DIR / "crawler.log")
LOG_LEVEL = "INFO"

FEEDS = {
    str(PROJECT_ROOT / "output" / "courses.jsonl"): {
        "format": "jsonlines",
        "encoding": "utf-8",
        "overwrite": True,
    }
}

# Rotating file logging in /logs.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE,
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "standard",
            "encoding": "utf-8",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["console", "rotating_file"],
        "level": "INFO",
    },
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 45_000
PLAYWRIGHT_MAX_CONTEXTS = 4
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4
PLAYWRIGHT_URL_PATTERNS = ["/learn", "/course", "/class", "?query="]
PLAYWRIGHT_WAIT_MS = 1200
