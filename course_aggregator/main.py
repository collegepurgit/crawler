"""CLI runner for starting course provider spiders and printing crawl statistics."""

from __future__ import annotations

import argparse
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


PROJECT_ROOT = Path(__file__).resolve().parent
PROVIDERS = ("coursera", "udemy", "edx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run course aggregator spiders")
    parser.add_argument(
        "--provider",
        required=True,
        choices=PROVIDERS,
        help="Provider spider to run (coursera|udemy|edx)",
    )
    parser.add_argument(
        "--seed-urls",
        default="",
        help="Optional comma-separated seed URLs override",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Optional crawl depth override",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    settings = get_project_settings()
    settings.set("PROJECT_ROOT", str(PROJECT_ROOT), priority="cmdline")

    process = CrawlerProcess(settings)
    crawler = process.create_crawler(args.provider)

    crawl_kwargs: dict[str, str | int] = {}
    if args.seed_urls:
        crawl_kwargs["seed_urls"] = args.seed_urls
    if args.max_depth is not None:
        crawl_kwargs["max_depth"] = args.max_depth

    process.crawl(crawler, **crawl_kwargs)
    process.start()

    crawler_stats = crawler.stats.get_stats()

    print("\n=== Crawl Statistics ===")
    print(f"provider: {args.provider}")
    for key in sorted(crawler_stats):
        print(f"{key}: {crawler_stats[key]}")


if __name__ == "__main__":
    main()
