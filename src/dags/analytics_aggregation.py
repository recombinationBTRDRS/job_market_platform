# src/dags/analytics_aggregation.py
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
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
    "email_on_failure": False,
}


@dag(
    dag_id="analytics_aggregation",
    description="Агрегація даних з операційної схеми в аналітичну",
    schedule="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["analytics", "aggregation"],
)
def analytics_aggregation():
    @task
    def aggregate_fact_vacancies(data_interval_end: datetime | None = None) -> int:
        from src.etl.aggregators import aggregate_fact_vacancies as _agg

        target_date = (data_interval_end or datetime.utcnow()).date()
        return asyncio.run(_agg(target_date))

    @task
    def aggregate_skills_daily(data_interval_end: datetime | None = None) -> int:
        from src.etl.aggregators import aggregate_skills_daily as _agg

        target_date = (data_interval_end or datetime.utcnow()).date()
        return asyncio.run(_agg(target_date))

    @task
    def aggregate_salary_by_skill() -> int:
        from src.etl.aggregators import aggregate_salary_by_skill as _agg

        return asyncio.run(_agg())

    @task
    def summarize(facts: int, skills: int, salaries: int) -> dict:
        logger.info(
            "Analytics aggregation complete: facts=%d, skills=%d, salaries=%d",
            facts,
            skills,
            salaries,
        )
        return {
            "fact_vacancies": facts,
            "skills_daily": skills,
            "salary_by_skill": salaries,
        }

    facts = aggregate_fact_vacancies()
    skills = aggregate_skills_daily()
    salaries = aggregate_salary_by_skill()
    summarize(facts, skills, salaries)


analytics_aggregation()
