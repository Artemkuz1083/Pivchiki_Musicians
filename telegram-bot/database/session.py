import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{os.getenv('DB_USER', 'postgres')}:"
    f"{os.getenv('DB_PASSWORD', 'parol123')}@"
    f"{os.getenv('DB_HOST', 'db')}:5432/"
    f"{os.getenv('DB_NAME', 'music_app')}"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        from .models import Base
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        from database.test_seed import seed_initial_data
        await seed_initial_data(session)