# src/main.py
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.routers.auth import router as auth_router
from src.api.v1.routers.companies import router as companies_router
from src.api.v1.routers.skills import router as skills_router
from src.api.v1.routers.vacancies import router as vacancies_router
from src.core.config import get_settings
from src.core.exceptions import AppError

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Job Market Analytics Platform API",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
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

    @app.get("/health", tags=["system"])
    async def health_check() -> dict:
        return {
            "status": "ok",
            "version": settings.app_version,
            "app": settings.app_name,
        }

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(vacancies_router, prefix="/api/v1")
    app.include_router(skills_router, prefix="/api/v1")
    app.include_router(companies_router, prefix="/api/v1")

    return app


app = create_app()
