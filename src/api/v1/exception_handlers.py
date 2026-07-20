# src/api/v1/exception_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions import AppError


async def app_exception_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "detail": exc.detail,
                "extra": exc.extra,
            }
        },
    )
