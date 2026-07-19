# src/models/operational/provider.py
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.operational.parse_run import ParseRun
    from src.models.operational.vacancy import Vacancy


class Provider(Base, TimestampMixin):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    vacancies: Mapped[list["Vacancy"]] = relationship(
        back_populates="provider",
        lazy="select",
    )
    parse_runs: Mapped[list["ParseRun"]] = relationship(
        back_populates="provider",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Provider id={self.id} name={self.name} type={self.type}>"
