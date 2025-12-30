import asyncio
from sqlmodel import SQLModel
from src.core.database import async_engine
from src.models.user import User
from src.models.task import Task

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_tables())