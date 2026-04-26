from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from repopilot.config import settings


class Base(DeclarativeBase):
    pass


def _get_engine():
    return create_async_engine(
        f"sqlite+aiosqlite:///{settings.repopilot_db_path}",
        echo=False,
        future=True,
    )


engine = _get_engine()
AsyncSessionLocal = async_sessionmaker(
    engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
