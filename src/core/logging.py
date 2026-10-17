# src/core/logging.py
import logging
import sys
from collections.abc import Callable
from typing import Any

import structlog


def setup_logging(debug: bool = False) -> None:
    """Налаштувати structlog для production або dev режиму."""

    shared_processors: list[Callable[..., Any]] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    processors: list[Callable[..., Any]]
    if debug:
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        processors = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if debug else logging.INFO
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if debug else logging.INFO,
    )

    for noisy_logger in [
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "httpx",
        "httpcore",
        "uvicorn.access",
    ]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
