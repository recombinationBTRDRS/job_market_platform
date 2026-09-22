# src/models/analytical/aggregates.py
from datetime import date

from sqlalchemy import BigInteger, Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.analytical.fact_vacancies import AnalyticsBase


class AggSkillsDaily(AnalyticsBase):
    """Агрегат — кількість вакансій по скілу за день."""

    __tablename__ = "agg_skills_daily"
    __table_args__ = {"schema": "analytics"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    skill_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregation_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    vacancy_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<AggSkillsDaily skill={self.skill_name} date={self.aggregation_date}>"


class AggSalaryBySkill(AnalyticsBase):
    """Агрегат — зарплатна статистика по скілу."""

    __tablename__ = "agg_salary_by_skill"
    __table_args__ = {"schema": "analytics"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    skill_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avg_salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<AggSalaryBySkill skill={self.skill_name}>"
