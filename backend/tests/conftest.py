import asyncio
import shutil
from pathlib import Path
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.db.database import Base, get_db
from app.main import create_application
from app.services.storage_service import StorageService

# Enable test auth bypass for Phase 1-9 analytical integration tests
settings.AUTH_TEST_BYPASS = True


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Session-wide async engine using DATABASE_TEST_URL."""
    engine = create_async_engine(settings.DATABASE_TEST_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def test_storage():
    """Isolated test storage directory for Phase 2 tests."""
    settings.STORAGE_PATH = settings.TEST_STORAGE_PATH
    storage_path = Path(settings.TEST_STORAGE_PATH).resolve()
    storage_path.mkdir(parents=True, exist_ok=True)
    yield storage_path
    if storage_path.exists():
        shutil.rmtree(storage_path, ignore_errors=True)


@pytest.fixture
def storage_service(test_storage) -> StorageService:
    return StorageService(base_storage_path=str(test_storage))


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provides an isolated database session per test function using PostgreSQL test DB."""
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:
        pytest.skip(f"PostgreSQL test database unavailable ({settings.DATABASE_TEST_URL}): {exc}")

    TestingSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestingSessionLocal() as session:
        yield session

    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except Exception:
        pass


@pytest_asyncio.fixture
async def async_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for FastAPI integration testing."""
    app = create_application()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
