from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from config import postgres_url
from services.session import cleanup_loop


session_engine = create_async_engine(postgres_url, echo=False)
session_maker = async_sessionmaker(session_engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    async with session_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]