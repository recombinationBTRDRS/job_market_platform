# src/dags/etl_pipeline.py
"""
ETL Pipeline DAG — збір вакансій з усіх провайдерів.
Запускається кожні 6 годин.
Extract → Transform → Load
"""

from __future__ import annotations

import asyncio
import logging
import sys
from datetime import datetime, timedelta

from airflow.decorators import dag, task

sys.path.insert(0, "/opt/airflow/app")

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "job_market",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

ACTIVE_PROVIDERS = ["mock", "djinni_co", "work_ua", "robota_ua"]


async def _run_etl_for_provider(provider_name: str) -> dict:
    """Запустити ETL pipeline для одного провайдера."""
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

    provider = get_provider(provider_name)
    if provider is None:
        return {
            "provider": provider_name,
            "status": "error",
            "error": "Provider not found",
        }

    rate_limit = get_rate_limit(provider_name)
    if rate_limit > 0:
        await asyncio.sleep(rate_limit)

    async with AsyncSessionFactory() as session:
        provider_repo = BaseRepository(model=Provider, session=session)
        all_providers = await provider_repo.get_all()
        db_provider = next((p for p in all_providers if p.name == provider_name), None)

        if db_provider is None:
            db_provider = await provider_repo.create(
                name=provider_name,
                type=provider.provider_type,
                is_active=True,
            )
            await session.commit()

        provider_id = db_provider.id

        try:
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


@dag(
    dag_id="etl_vacancy_pipeline",
    description="ETL pipeline для збору вакансій з усіх провайдерів",
    schedule="0 */6 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["etl", "vacancies"],
)
def etl_vacancy_pipeline():
    @task
    def extract_mock() -> dict:
        return asyncio.run(_run_etl_for_provider("mock"))

    @task
    def extract_djinni() -> dict:
        return asyncio.run(_run_etl_for_provider("djinni_co"))

    @task
    def extract_work_ua() -> dict:
        return asyncio.run(_run_etl_for_provider("work_ua"))

    @task
    def extract_robota_ua() -> dict:
        return asyncio.run(_run_etl_for_provider("robota_ua"))

    @task
    def summarize(
        mock_result: dict,
        djinni_result: dict,
        work_result: dict,
        robota_result: dict,
    ) -> dict:
        results = [mock_result, djinni_result, work_result, robota_result]
        total_fetched = sum(r.get("fetched", 0) for r in results)
        total_new = sum(r.get("new", 0) for r in results)
        total_errors = sum(r.get("errors", 0) for r in results)

        logger.info(
            "ETL Summary: fetched=%d, new=%d, errors=%d",
            total_fetched,
            total_new,
            total_errors,
        )
        return {
            "total_fetched": total_fetched,
            "total_new": total_new,
            "total_errors": total_errors,
            "results": results,
        }

    mock = extract_mock()
    djinni = extract_djinni()
    work = extract_work_ua()
    robota = extract_robota_ua()

    summarize(mock, djinni, work, robota)


etl_vacancy_pipeline()
