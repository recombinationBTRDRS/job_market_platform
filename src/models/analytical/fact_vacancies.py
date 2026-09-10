# src/models/analytical/fact_vacancies.py
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class AnalyticsBase(DeclarativeBase):
    """Окрема Base для аналітичних моделей."""

    pass


class FactVacancy(AnalyticsBase):
    __tablename__ = "fact_vacancies"
    __table_args__ = {"schema": "analytics"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    vacancy_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    remote_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    collected_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<FactVacancy id={self.id} title={self.title}>"
