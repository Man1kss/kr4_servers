"""Фикстуры для тестов pytest."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from faker import Faker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

# Создаем in-memory SQLite базу для тестов
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db() -> AsyncSession:
    """Переопределение зависимости для тестов."""
    async with TestAsyncSessionLocal() as session:
        yield session


# Переопределяем зависимость базы данных
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function")
async def async_client():
    """Асинхронный клиент для тестирования API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
def client():
    """Синхронный клиент для тестирования API (через TestClient)."""
    # Сбрасываем in-memory хранилище пользователей
    import app.main as main_module
    main_module.users_db.clear()
    main_module._id_counter = 1

    return TestClient(app)


@pytest.fixture(scope="function")
def faker():
    """Фикстура Faker для генерации тестовых данных."""
    return Faker("ru_RU")


@pytest_asyncio.fixture(scope="function")
async def setup_database():
    """Настройка тестовой базы данных."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function", autouse=True)
def reset_in_memory_db():
    """Сброс in-memory хранилища перед каждым тестом."""
    import app.main as main_module
    main_module.users_db.clear()
    main_module._id_counter = 1
    yield