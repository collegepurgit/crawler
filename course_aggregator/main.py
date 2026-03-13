"""CLI runner for manual and scheduled crawler execution."""

from __future__ import annotations

import argparse
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from utils.scheduler import CrawlScheduler


PROJECT_ROOT = Path(__file__).resolve().parent
PROVIDERS = ("coursera", "udemy", "edx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run course aggregator spiders")

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--provider",
        choices=PROVIDERS,
        help="Run one provider spider manually (coursera|udemy|edx)",
    )
    mode_group.add_argument(
        "--schedule",
        action="store_true",
        help="Run scheduler mode (sequential spiders every 24 hours)",
    )

    parser.add_argument(
        "--seed-urls",
        default="",
        help="Optional comma-separated seed URLs override (manual mode only)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Optional crawl depth override (manual mode only)",
    )
    return parser


def run_provider(provider: str, seed_urls: str = "", max_depth: int | None = None) -> dict:
    settings = get_project_settings()
    settings.set("PROJECT_ROOT", str(PROJECT_ROOT), priority="cmdline")

    process = CrawlerProcess(settings)
    crawler = process.create_crawler(provider)

    crawl_kwargs: dict[str, str | int] = {}
    if seed_urls:
        crawl_kwargs["seed_urls"] = seed_urls
    if max_depth is not None:
        crawl_kwargs["max_depth"] = max_depth

    process.crawl(crawler, **crawl_kwargs)
    process.start()
    return crawler.stats.get_stats()


def main() -> None:
    args = build_parser().parse_args()

    if args.schedule:
        scheduler = CrawlScheduler(project_root=PROJECT_ROOT, interval_hours=24)
        scheduler.start()
        return

    stats = run_provider(provider=args.provider, seed_urls=args.seed_urls, max_depth=args.max_depth)

    print("\n=== Crawl Statistics ===")
    print(f"provider: {args.provider}")
    for key in sorted(stats):
        print(f"{key}: {stats[key]}")


if __name__ == "__main__":
    main()
