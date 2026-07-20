# src/models/operational/parse_run.py
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.operational.provider import Provider


class ParseRun(Base, TimestampMixin):
    __tablename__ = "parse_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="running")
    vacancies_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vacancies_new: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vacancies_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    provider: Mapped["Provider"] = relationship(back_populates="parse_runs")

    def __repr__(self) -> str:
        return f"<ParseRun id={self.id} status={self.status}>"
