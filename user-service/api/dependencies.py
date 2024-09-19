import jwt
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.redis import redis_client
from core.config import settings
from db.models.user import Users
from db.models.project import Project as DBProject

async def verify_token(request: Request):
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
    
    return email
  except jwt.PyJWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

async def get_user_by_email(session: AsyncSession, email: str):
  result = await session.execute(select(Users).where(Users.email == email))
  user = result.scalars().first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
  return user

async def get_projects_by_user(session: AsyncSession, user_id: int):
  result = await session.execute(select(DBProject).where(DBProject.user_id == user_id))
  return result.scalars().all()

def format_project_response(project, user):
  return {
    "link": project.link,
    "owner": {
      "id": user.id,
      "email": user.email,
      "username": user.username
    },
    "changed_at": project.changed_at.isoformat(),
    "created_at": project.created_at.isoformat(),
  }