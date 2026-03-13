"""Scheduler module for automated recurring provider crawls."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import schedule
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from utils.logging_utils import setup_logging

PROVIDERS = ("coursera", "udemy", "edx")
LOGGER = logging.getLogger(__name__)


class CrawlScheduler:
    """Run provider spiders sequentially on a fixed interval."""

    def __init__(self, project_root: Path, interval_hours: int = 24) -> None:
        self.project_root = project_root
        self.interval_hours = interval_hours
        self.last_crawl_file = self.project_root / "logs" / "last_crawl.json"
        self.is_running = False

        setup_logging(str(self.project_root / "logs" / "scheduler.log"))

    def start(self) -> None:
        LOGGER.info("scheduler starts | interval_hours=%s providers=%s", self.interval_hours, PROVIDERS)

        # Run once immediately, then every N hours.
        self.run_all_providers()
        schedule.every(self.interval_hours).hours.do(self.run_all_providers)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def run_all_providers(self) -> None:
        if self.is_running:
            LOGGER.warning("skip scheduled run | reason=overlap_prevented")
            return

        self.is_running = True
        started_at = datetime.now(timezone.utc)
        run_results: dict[str, dict] = {}
        try:
            LOGGER.info("scheduled crawl run started | started_at=%s", started_at.isoformat())
            for provider in PROVIDERS:
                run_results[provider] = self._run_provider(provider)

            finished_at = datetime.now(timezone.utc)
            self._write_last_crawl(started_at, finished_at, run_results)
            LOGGER.info(
                "scheduled crawl run completed | finished_at=%s providers=%s",
                finished_at.isoformat(),
                list(run_results.keys()),
            )
        except Exception:
            LOGGER.exception("scheduled crawl run failed")
        finally:
            self.is_running = False

    def _run_provider(self, provider: str) -> dict:
        LOGGER.info("provider crawl start | provider=%s", provider)

        settings = get_project_settings()
        settings.set("PROJECT_ROOT", str(self.project_root), priority="cmdline")

        process = CrawlerProcess(settings)
        crawler = process.create_crawler(provider)
        process.crawl(crawler)
        process.start()

        stats = crawler.stats.get_stats()
        LOGGER.info("provider crawl completed | provider=%s item_scraped=%s", provider, stats.get("item_scraped_count", 0))
        return stats

    def _write_last_crawl(self, started_at: datetime, finished_at: datetime, run_results: dict[str, dict]) -> None:
        payload = {
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "providers": run_results,
        }
        self.last_crawl_file.parent.mkdir(parents=True, exist_ok=True)
        self.last_crawl_file.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
