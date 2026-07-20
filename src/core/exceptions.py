# src/core/exceptions.py
from typing import Any


class AppError(Exception):
    """Базовий клас для всіх кастомних винятків."""

    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.detail = detail or self.__class__.detail
        self.status_code = status_code or self.__class__.status_code
        self.extra = extra or {}
        super().__init__(self.detail)


class NotFoundError(AppError):
    """Ресурс не знайдено."""

    status_code = 404
    detail = "Resource not found"


class DuplicateError(AppError):
    """Ресурс вже існує."""

    status_code = 409
    detail = "Resource already exists"


class ValidationError(AppError):
    """Помилка валідації даних."""

    status_code = 422
    detail = "Validation error"


class AuthenticationError(AppError):
    """Помилка автентифікації."""

    status_code = 401
    detail = "Authentication failed"


class AuthorizationError(AppError):
    """Недостатньо прав."""

    status_code = 403
    detail = "Permission denied"


class ETLError(AppError):
    """Помилка ETL pipeline."""

    status_code = 500
    detail = "ETL pipeline error"


class ProviderError(ETLError):
    """Помилка провайдера даних."""

    detail = "Data provider error"
