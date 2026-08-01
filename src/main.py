# src/main.py
import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.routers.analytics import router as analytics_router
from src.api.v1.routers.auth import router as auth_router
from src.api.v1.routers.companies import router as companies_router
from src.api.v1.routers.parse_runs import router as parse_runs_router
from src.api.v1.routers.providers import router as providers_router
from src.api.v1.routers.skills import router as skills_router
from src.api.v1.routers.vacancies import router as vacancies_router
from src.core.config import get_settings
from src.core.exceptions import AppError

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    yield
    logger.info("Shutting down %s", settings.app_name)


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

    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],
        )

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        start_time = time.monotonic()
        response = await call_next(request)
        process_time = time.monotonic() - start_time
        logger.info(
            "%s %s %d %.3fs",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )
        response.headers["X-Process-Time"] = str(process_time)
        return response

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
    app.include_router(providers_router, prefix="/api/v1")
    app.include_router(parse_runs_router, prefix="/api/v1")
    app.include_router(analytics_router, prefix="/api/v1")

    return app


app = create_app()
