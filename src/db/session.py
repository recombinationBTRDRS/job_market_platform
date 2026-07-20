# src/db/session.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    str(settings.database_url),
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — одна сесія на один запит."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
