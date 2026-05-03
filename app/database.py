"""Настройка базы данных и сессий SQLAlchemy."""

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Используем SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app/app.db")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Зависимость для получения сессии базы данных."""
    async with AsyncSessionLocal() as session:
        yield session