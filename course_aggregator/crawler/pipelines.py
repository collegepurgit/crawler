"""Item pipelines for relational persistence."""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from database.database import Database
from database.models import InstructorRecord

logger = logging.getLogger(__name__)


class SQLitePipeline:
    """Persist crawled data into providers/courses/categories/instructors tables."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.db: Database | None = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(db_path=crawler.settings.get("SQLITE_DB_PATH"))

    def open_spider(self, spider):
        self.db = Database(self.db_path)
        self.db.open()
        self.db.create_tables()

    def close_spider(self, spider):
        if self.db:
            self.db.close()

    def process_item(self, item, spider):
        assert self.db is not None
        adapter = ItemAdapter(item)

        try:
            course_url = (adapter.get("course_url") or adapter.get("url") or "").strip()
            if not course_url:
                raise DropItem("Missing course_url; cannot persist course")

            title = (adapter.get("title") or adapter.get("course_title") or "Untitled course").strip()
            slug = (adapter.get("slug") or self._slugify(title) or self._slugify(course_url)).strip()

            # 1) Insert provider if missing.
            provider_name = (adapter.get("provider_name") or adapter.get("provider") or "Unknown Provider").strip()
            provider_website = (adapter.get("provider_website") or self._domain_to_site(course_url)).strip()
            provider_logo_url = (adapter.get("provider_logo_url") or "").strip()
            provider_id = self.db.get_or_create_provider(provider_name, provider_website, provider_logo_url)

            # 2) Insert/upsert course record by unique course_url.
            course_id = self.db.upsert_course(
                title=title,
                slug=slug,
                provider_id=provider_id,
                rating=self._to_float(adapter.get("rating")),
                description=(adapter.get("description") or "").strip(),
                image_url=(adapter.get("image_url") or "").strip(),
                course_url=course_url,
            )

            # 3) Insert categories if missing and 5) create course_categories relations.
            categories = self._normalize_list(adapter.get("categories") or adapter.get("category"))
            category_ids: list[int] = []
            for category_name in categories:
                category_ids.append(self.db.get_or_create_category(category_name))
            self.db.replace_course_categories(course_id, category_ids)

            # 4) Insert instructors if missing and 5) create course_instructors relations.
            instructors = self._normalize_instructors(adapter.get("instructors"))
            instructor_ids: list[int] = []
            for instructor in instructors:
                instructor_ids.append(self.db.get_or_create_instructor(instructor.name, instructor.profile_url))
            self.db.replace_course_instructors(course_id, instructor_ids)

            self.db.commit()
            logger.info("database insert | course_url=%s provider_id=%s course_id=%s", course_url, provider_id, course_id)
            return item
        except DropItem:
            raise
        except Exception:
            logger.exception("errors | pipeline failure for item url=%s", adapter.get("course_url") or adapter.get("url"))
            raise

    def _normalize_list(self, raw_value) -> list[str]:
        if not raw_value:
            return []
        if isinstance(raw_value, str):
            parts = [part.strip() for part in raw_value.split(",")]
            values = [part for part in parts if part]
        elif isinstance(raw_value, (list, tuple, set)):
            values = [str(part).strip() for part in raw_value if str(part).strip()]
        else:
            values = [str(raw_value).strip()]

        # Preserve order + remove duplicates.
        return list(dict.fromkeys(values))

    def _normalize_instructors(self, raw_value) -> list[InstructorRecord]:
        if not raw_value:
            return []

        result: list[InstructorRecord] = []
        if isinstance(raw_value, str):
            for name in [part.strip() for part in raw_value.split(",") if part.strip()]:
                result.append(InstructorRecord(name=name, profile_url=""))
        elif isinstance(raw_value, (list, tuple, set)):
            for instructor in raw_value:
                if isinstance(instructor, dict):
                    result.append(
                        InstructorRecord(
                            name=str(instructor.get("name", "")).strip(),
                            profile_url=str(instructor.get("profile_url", "")).strip(),
                        )
                    )
                else:
                    name = str(instructor).strip()
                    if name:
                        result.append(InstructorRecord(name=name, profile_url=""))

        unique: list[InstructorRecord] = []
        seen: set[tuple[str, str]] = set()
        for instructor in result:
            key = (instructor.name, instructor.profile_url)
            if instructor.name and key not in seen:
                seen.add(key)
                unique.append(instructor)
        return unique

    def _slugify(self, value: str) -> str:
        text = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "").lower()).strip("-")
        return text or "unknown"

    def _domain_to_site(self, url: str) -> str:
        if not url:
            return ""
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return ""
        return f"{parsed.scheme}://{parsed.netloc}"

    def _to_float(self, value) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(str(value).strip())
        except ValueError:
            return None
