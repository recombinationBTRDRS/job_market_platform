# src/schemas/vacancy.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VacancyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    provider_id: int
    company_id: int | None = None
    url: str
    title: str
    description: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    employment_type: str | None = None
    remote_type: str | None = None
    published_at: datetime | None = None
    is_active: bool
    created_at: datetime


class VacancyListRead(BaseModel):
    """Schema для списку вакансій з пагінацією."""

    items: list[VacancyRead]
    total: int
    page: int
    per_page: int
    pages: int


class VacancyFilterParams(BaseModel):
    """Query параметри для фільтрації вакансій."""

    skill_ids: list[int] | None = Field(default=None)
    remote_type: str | None = None
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    salary_currency: str | None = None
    company_id: int | None = None
    provider_id: int | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
