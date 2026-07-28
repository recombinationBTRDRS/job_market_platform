# src/etl/pipeline.py
import asyncio
import logging

from src.db.session import AsyncSessionFactory
from src.etl.loaders.vacancy_loader import VacancyLoader
from src.etl.providers.registry import get_provider, get_rate_limit
from src.etl.transformers.deduplicator import (
    deduplicate_in_memory,
    filter_existing_vacancies,
)
from src.etl.transformers.normalizer import normalize_vacancies
from src.models.operational.provider import Provider
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


async def run_etl_for_provider(provider_name: str) -> dict:
    """Запустити повний ETL цикл для одного провайдера."""
    provider = get_provider(provider_name)
    if provider is None:
        return {
            "provider": provider_name,
            "status": "error",
            "error": "Provider not found",
        }

    rate_limit = get_rate_limit(provider_name)

    async with AsyncSessionFactory() as session:
        try:
            provider_repo = BaseRepository(model=Provider, session=session)
            all_providers = await provider_repo.get_all()
            db_provider = next(
                (p for p in all_providers if p.name == provider_name), None
            )

            if db_provider is None:
                db_provider = await provider_repo.create(
                    name=provider_name,
                    type=provider.provider_type,
                    is_active=True,
                )
                await session.commit()

            provider_id = db_provider.id

            if rate_limit > 0:
                await asyncio.sleep(rate_limit)

            logger.info("Extracting from %s", provider_name)
            raw_vacancies = await provider.fetch()
            logger.info(
                "Fetched %d vacancies from %s", len(raw_vacancies), provider_name
            )

            normalized = normalize_vacancies(raw_vacancies)
            unique_in_memory = deduplicate_in_memory(normalized)
            new_vacancies, duplicates = await filter_existing_vacancies(
                unique_in_memory, provider_id, session
            )

            loader = VacancyLoader(session=session, provider_id=provider_id)
            success, errors = await loader.load(new_vacancies)

            await session.commit()

            return {
                "provider": provider_name,
                "status": "success",
                "fetched": len(raw_vacancies),
                "normalized": len(normalized),
                "new": success,
                "duplicates": duplicates,
                "errors": errors,
            }

        except Exception as e:
            await session.rollback()
            logger.error("ETL failed for %s: %s", provider_name, e)
            return {
                "provider": provider_name,
                "status": "error",
                "error": str(e),
            }
