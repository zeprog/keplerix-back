from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from core.config import settings
from db.models.user import Users

DATABASE_URL = settings.DATABASE_URL_ASYNC

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session():
  async with async_session_maker() as session:
    yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
  return session