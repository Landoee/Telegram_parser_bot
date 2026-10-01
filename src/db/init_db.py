from src.db.base import Base, engine
from src.db.models import User  # обязательно импортируем, чтобы Base знала о модели


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)