# tests/conftest.py
import asyncio
import sys
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import get_settings
from src.db.base import Base
from src.main import create_app
from src.models.operational import (
    Company,
    Provider,
    Skill,
    User,
    Vacancy,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

settings = get_settings()

TEST_DATABASE_URL = str(settings.database_url).replace(
    f"/{settings.postgres_db}",
    "/test_job_market_db",
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.connect() as conn:
        await conn.begin_nested()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await conn.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    from src.api.v1.dependencies import get_db

    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_provider(db_session: AsyncSession) -> Provider:
    provider = Provider(name="test_provider", type="mock", is_active=True)
    db_session.add(provider)
    await db_session.flush()
    return provider


@pytest_asyncio.fixture
async def test_company(db_session: AsyncSession) -> Company:
    company = Company(name="Test Company")
    db_session.add(company)
    await db_session.flush()
    return company


@pytest_asyncio.fixture
async def test_skill(db_session: AsyncSession) -> Skill:
    skill = Skill(name="Python", normalized_name="python")
    db_session.add(skill)
    await db_session.flush()
    return skill


@pytest_asyncio.fixture
async def test_vacancy(
    db_session: AsyncSession,
    test_provider: Provider,
    test_company: Company,
) -> Vacancy:
    vacancy = Vacancy(
        external_id="test-001",
        provider_id=test_provider.id,
        company_id=test_company.id,
        url="https://test.com/jobs/001",
        title="Senior Python Developer",
        salary_min=3000,
        salary_max=5000,
        salary_currency="USD",
        remote_type="remote",
        is_active=True,
    )
    db_session.add(vacancy)
    await db_session.flush()
    return vacancy


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    from src.core.security import hash_password

    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    from src.core.security import hash_password

    user = User(
        email="admin@example.com",
        hashed_password=hash_password("adminpassword123"),
        full_name="Admin User",
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user
