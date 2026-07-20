# src/db/base.py
from datetime import UTC, datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовий клас для всіх SQLAlchemy моделей."""

    pass


class TimestampMixin:
    """Mixin який додає created_at і updated_at до моделі."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
