# src/schemas/analytics.py
from pydantic import BaseModel


class TopSkill(BaseModel):
    id: int
    name: str
    normalized_name: str
    vacancy_count: int


class SalaryStats(BaseModel):
    skill_name: str
    avg_salary_min: float | None = None
    avg_salary_max: float | None = None
    sample_count: int


class MarketOverview(BaseModel):
    total_vacancies: int
    active_vacancies: int
    total_companies: int
    total_skills: int
    last_updated: str
