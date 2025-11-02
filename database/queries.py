from sqlalchemy import select
from .models import User
from .session import AsyncSessionLocal

async def check_user(user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none() is not None