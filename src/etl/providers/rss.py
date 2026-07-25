# src/etl/providers/rss.py
import hashlib
import logging
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from src.etl.providers.base import BaseProvider, NormalizedVacancy

logger = logging.getLogger(__name__)

SKILL_KEYWORDS = [
    "python",
    "fastapi",
    "django",
    "flask",
    "sqlalchemy",
    "postgresql",
    "mysql",
    "redis",
    "mongodb",
    "elasticsearch",
    "docker",
    "kubernetes",
    "airflow",
    "spark",
    "kafka",
    "aws",
    "gcp",
    "azure",
    "terraform",
    "ansible",
    "javascript",
    "typescript",
    "react",
    "vue",
    "nodejs",
    "git",
    "linux",
    "nginx",
    "celery",
    "pytest",
    "asyncio",
    "pydantic",
    "alembic",
    "graphql",
    "rest",
]


def extract_skills(text: str) -> list[str]:
    """Витягти скіли з тексту по ключових словах."""
    text_lower = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text_lower):
            found.append(skill.capitalize())
    return list(dict.fromkeys(found))


def parse_salary(text: str) -> tuple[int | None, int | None, str | None]:
    """Спроба витягти зарплату з тексту."""
    usd_pattern = r"\$\s*(\d+(?:,\d{3})*(?:k)?)\s*[-–]\s*\$?\s*(\d+(?:,\d{3})*(?:k)?)"
    match = re.search(usd_pattern, text, re.IGNORECASE)
    if match:

        def parse_num(s: str) -> int:
            s = s.replace(",", "")
            if s.lower().endswith("k"):
                return int(s[:-1]) * 1000
            return int(s)

        return parse_num(match.group(1)), parse_num(match.group(2)), "USD"
    return None, None, None


def parse_published_at(entry: feedparser.FeedParserDict) -> datetime | None:
    """Парсити дату публікації з RSS entry."""
    if hasattr(entry, "published") and entry.published:
        try:
            return parsedate_to_datetime(entry.published)
        except Exception:
            pass
    return datetime.now(UTC)


class RSSProvider(BaseProvider):
    """Провайдер для парсингу вакансій з RSS feeds."""

    name = "rss"
    provider_type = "rss"

    def __init__(self, feed_url: str, source_name: str = "rss") -> None:
        self.feed_url = feed_url
        self.source_name = source_name

    def _generate_external_id(self, entry: feedparser.FeedParserDict) -> str:
        """Генерувати унікальний ID для вакансії."""
        source = entry.get("id") or entry.get("link") or entry.get("title", "")
        return hashlib.md5(source.encode()).hexdigest()

    def _extract_company(self, entry: feedparser.FeedParserDict) -> str | None:
        """Витягти назву компанії з entry."""
        if hasattr(entry, "author"):
            return entry.author
        if hasattr(entry, "source") and hasattr(entry.source, "title"):
            return entry.source.title
        return self.source_name

    def _parse_entry(
        self, entry: feedparser.FeedParserDict
    ) -> NormalizedVacancy | None:
        """Конвертувати RSS entry в NormalizedVacancy."""
        try:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            if not title or not link:
                return None

            description = ""
            if hasattr(entry, "summary"):
                description = re.sub(r"<[^>]+>", "", entry.summary).strip()
            elif hasattr(entry, "content") and entry.content:
                description = re.sub(r"<[^>]+>", "", entry.content[0].value).strip()

            full_text = f"{title} {description}"
            skills = extract_skills(full_text)
            salary_min, salary_max, currency = parse_salary(full_text)

            remote_type = None
            text_lower = full_text.lower()
            if "remote" in text_lower:
                remote_type = "remote"
            elif "hybrid" in text_lower:
                remote_type = "hybrid"
            elif "office" in text_lower or "onsite" in text_lower:
                remote_type = "office"

            return NormalizedVacancy(
                external_id=self._generate_external_id(entry),
                title=title,
                url=link,
                company_name=self._extract_company(entry),
                description=description[:5000] if description else None,
                skills=skills,
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency=currency,
                remote_type=remote_type,
                published_at=parse_published_at(entry),
                raw_data={"source": self.source_name},
            )
        except Exception as e:
            logger.warning("Failed to parse RSS entry: %s", e)
            return None

    async def fetch(self) -> list[NormalizedVacancy]:
        """Отримати вакансії з RSS feed."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.feed_url)
                response.raise_for_status()
                feed = feedparser.parse(response.text)
        except Exception as e:
            logger.error("Failed to fetch RSS feed %s: %s", self.feed_url, e)
            return []

        vacancies = []
        for entry in feed.entries:
            vacancy = self._parse_entry(entry)
            if vacancy is not None:
                vacancies.append(vacancy)

        logger.info(
            "RSSProvider fetched %d vacancies from %s",
            len(vacancies),
            self.feed_url,
        )
        return vacancies

    async def health_check(self) -> bool:
        """Перевірити доступність RSS feed."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.head(self.feed_url)
                return response.status_code < 400
        except Exception:
            return False
