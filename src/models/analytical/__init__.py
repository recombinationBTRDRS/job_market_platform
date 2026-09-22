# src/models/analytical/__init__.py
from src.models.analytical.aggregates import AggSalaryBySkill, AggSkillsDaily
from src.models.analytical.fact_vacancies import AnalyticsBase, FactVacancy

__all__ = [
    "AnalyticsBase",
    "FactVacancy",
    "AggSkillsDaily",
    "AggSalaryBySkill",
]
