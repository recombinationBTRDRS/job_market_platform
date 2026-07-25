# src/repositories/__init__.py
from src.repositories.base import BaseRepository
from src.repositories.company import CompanyRepository
from src.repositories.skill import SkillRepository
from src.repositories.vacancy import VacancyRepository

__all__ = [
    "BaseRepository",
    "VacancyRepository",
    "SkillRepository",
    "CompanyRepository",
]
