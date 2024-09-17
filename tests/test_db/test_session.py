import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from db.session import get_async_session, get_user_db
from core.config import settings

DATABASE_URL = settings.DATABASE_URL_ASYNC

@pytest.fixture
async def test_session() -> AsyncSession:
  engine = create_async_engine(DATABASE_URL, echo=True)
  async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
  async with async_session_maker() as session:
    yield session

@pytest.mark.asyncio
async def test_get_user_db():
  async for session in get_async_session():
    user_db = await get_user_db(session=session)
    assert isinstance(user_db, AsyncSession)
    assert user_db == session