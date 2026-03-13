"""Pipelines for persistence and post-processing."""

from __future__ import annotations

import logging
from itemadapter import ItemAdapter

from database.sqlite_store import SQLiteStore

logger = logging.getLogger(__name__)


class SQLitePipeline:
    """Persist scraped items into SQLite."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.store: SQLiteStore | None = None

    @classmethod
    def from_crawler(cls, crawler):
        db_path = crawler.settings.get("SQLITE_DB_PATH")
        return cls(db_path=db_path)

    def open_spider(self, spider) -> None:
        self.store = SQLiteStore(self.db_path)
        self.store.open()
        self.store.init_schema()
        logger.info("SQLite pipeline initialized: %s", self.db_path)

    def close_spider(self, spider) -> None:
        if self.store:
            self.store.close()
            logger.info("SQLite connection closed")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if self.store:
            self.store.insert_course(dict(adapter))
        return item
