# src/dags/etl_pipeline.py
"""
ETL Pipeline DAG — збір вакансій з усіх провайдерів.
Запускається кожні 6 годин.
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
    def run_provider(provider_name: str) -> dict:
        from src.etl.pipeline import run_etl_for_provider

        return asyncio.run(run_etl_for_provider(provider_name))

    @task
    def summarize(results: list[dict]) -> dict:
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

    results = run_provider.expand(provider_name=ACTIVE_PROVIDERS)
    summarize(results)


etl_vacancy_pipeline()
