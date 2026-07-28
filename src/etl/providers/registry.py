# src/etl/providers/registry.py
import logging

from src.core.config import get_settings
from src.etl.providers.base import BaseProvider
from src.etl.providers.mock import MockProvider
from src.etl.providers.rss import RSSProvider

logger = logging.getLogger(__name__)

settings = get_settings()


def build_provider_registry() -> dict[str, BaseProvider]:
    """Побудувати реєстр активних провайдерів."""
    return {
        "mock": MockProvider(),
        "dou_ua": RSSProvider(
            feed_url="https://dou.ua/calendar/feed/",
            source_name="dou.ua",
        ),
        "work_ua": RSSProvider(
            feed_url="https://www.work.ua/rss/jobs/it/",
            source_name="work.ua",
        ),
        "robota_ua": RSSProvider(
            feed_url="https://robota.ua/rss",
            source_name="robota.ua",
        ),
        "djinni_co": RSSProvider(
            feed_url="https://djinni.co/jobs/feed/?primary_keyword=Python",
            source_name="djinni.co",
        ),
    }


RATE_LIMITS: dict[str, float] = {
    "mock": 0.0,
    "dou_ua": 5.0,
    "work_ua": 3.0,
    "robota_ua": 3.0,
    "djinni_co": 2.0,
}

ROBOTS_TXT_NOTES: dict[str, str] = {
    "mock": "Internal mock — no restrictions",
    "dou_ua": "RSS allowed. User-agent:* has no RSS disallow. Rate limit 5s.",
    "work_ua": "RSS allowed. Minimal restrictions. Rate limit 3s.",
    "robota_ua": "RSS allowed. Minimal restrictions. Rate limit 3s.",
    "djinni_co": "RSS allowed. Most liberal robots.txt. Rate limit 2s.",
}


def get_provider(name: str) -> BaseProvider | None:
    """Отримати провайдер по імені."""
    registry = build_provider_registry()
    provider = registry.get(name)
    if provider is None:
        logger.warning("Provider '%s' not found in registry", name)
    return provider


def get_rate_limit(provider_name: str) -> float:
    """Отримати rate limit для провайдера в секундах."""
    return RATE_LIMITS.get(provider_name, 3.0)


def list_providers() -> list[str]:
    """Отримати список всіх доступних провайдерів."""
    return list(build_provider_registry().keys())
