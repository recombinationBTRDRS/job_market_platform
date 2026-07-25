# src/etl/providers/base.py
from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, Field


class NormalizedVacancy(BaseModel):
    """Єдина нормалізована модель вакансії для всіх провайдерів."""

    external_id: str
    title: str
    url: str
    company_name: str | None = None
    description: str | None = None
    skills: list[str] = Field(default_factory=list)
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    employment_type: str | None = None
    remote_type: str | None = None
    published_at: datetime | None = None
    raw_data: dict = Field(default_factory=dict)


class BaseProvider(ABC):
    """Базовий абстрактний клас для всіх провайдерів вакансій."""

    name: str = ""
    provider_type: str = ""

    @abstractmethod
    async def fetch(self) -> list[NormalizedVacancy]:
        """Отримати вакансії з джерела і повернути нормалізований список."""

    async def health_check(self) -> bool:
        """Перевірити доступність джерела. За замовчуванням True."""
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
