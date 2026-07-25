# src/schemas/parse_run.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ParseRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_id: int
    started_at: datetime
    finished_at: datetime | None = None
    status: str
    vacancies_found: int
    vacancies_new: int
    vacancies_failed: int
    error_message: str | None = None
