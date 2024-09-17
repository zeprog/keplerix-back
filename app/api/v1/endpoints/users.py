import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.auth import verify_access_token
from core.redis import redis_client
from core.config import settings
from db.models.user import Users
from db.session import get_async_session
from domain.users.entities import UserInfo, UserInfoForUpdate

router = APIRouter()

@router.get('/info', response_model=UserInfo, tags=["User"])
async def get_account_info(request: Request, session: AsyncSession = Depends(get_async_session)):
  token_cookie_data = request.cookies.get("keplerix_token")

  if not token_cookie_data:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing in cookies")

  try:
    payload = jwt.decode(token_cookie_data, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    email = payload.get("sub")
    if not email:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    redis_key = f"{email}"
    token_redis_data = await redis_client.get(redis_key)

    if token_cookie_data != token_redis_data:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    result = await session.execute(select(Users).where(Users.email == email))
    db_user = result.scalars().first()

    if not db_user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    projects_count = await db_user.get_projects_count(session)

    return UserInfo(
      email=db_user.email,
      username=db_user.username,
      is_active=db_user.is_active,
      is_superuser=db_user.is_superuser,
      is_verified=db_user.is_verified,
      projects_count=projects_count
    )

  except jwt.PyJWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
  
@router.patch('/update_info', tags=['User'])
async def update_account_info(
  user_update: UserInfoForUpdate, 
  request: Request, 
  session: AsyncSession = Depends(get_async_session)
):
  token_cookie_data = request.cookies.get("keplerix_token")
  if not token_cookie_data:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

  try:
    payload = verify_access_token(token_cookie_data)
    email = payload.get("sub")
    redis_key = f"{email}"
    token_redis_data = await redis_client.get(redis_key)

    if token_cookie_data != token_redis_data:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
  except Exception:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

  result = await session.execute(select(Users).where(Users.email == email))
  db_user = result.scalars().first()

  if not db_user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

  if user_update.email is not None:
    db_user.email = user_update.email
  if user_update.username is not None:
    db_user.username = user_update.username

  await session.commit()

  return {"message": "User information updated successfully"}

@router.delete('/delete_user', tags=["User"])
async def delete_user(
  request: Request, 
  session: AsyncSession = Depends(get_async_session)
):
  token_cookie_data = request.cookies.get("keplerix_token")
  if not token_cookie_data:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

  try:
    payload = jwt.decode(token_cookie_data, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    email = payload.get("sub")
    if not email:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    redis_key = f"{email}"
    token_redis_data = await redis_client.get(redis_key)

    if token_cookie_data != token_redis_data:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
  except Exception:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

  result = await session.execute(select(Users).where(Users.email == email))
  db_user = result.scalars().first()

  if not db_user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

  await session.delete(db_user)
  await session.commit()

  await redis_client.delete(redis_key)

  return {"message": "User account deleted successfully"}
