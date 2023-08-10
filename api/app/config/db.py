import os
from typing import AsyncGenerator, List

from sqlmodel import Field, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine

from sqlalchemy.orm import sessionmaker
from app.models.models import PetType, Roles


DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost:5432/foo"
# DATABASE_URL = os.environ.get("DATABASE_URL")

engine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    session = await get_session()
    
    items = [Roles(role_name="admin"), Roles(role_name="pet-owner"), Roles(role_name="pet-walker")]
    pet_types = [
                    PetType(type="Dog"),
                    PetType(type="Cat"),
                    # PetType(type="Bird"), PetType(type="Rabbit")
                ]
    try:
        session.add_all(items)
        await session.commit()
    except Exception as e:
        await session.rollback()
        
    try:
        session.add_all(pet_types)
        await session.commit()
    except Exception as e:
        await session.rollback()


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        return session
        