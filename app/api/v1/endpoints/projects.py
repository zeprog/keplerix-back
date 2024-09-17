from datetime import datetime, timezone
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.redis import redis_client
from core.config import settings
from db.models.user import Users
from db.models.project import Project as DBProject
from db.session import get_async_session
from domain.projects.entities import ProjectCreate, ProjectResponse

router = APIRouter()

@router.get('/projects', response_model=list[ProjectResponse], tags=['Projects'])
async def get_projects(request: Request, session: AsyncSession = Depends(get_async_session)):
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

    # Fetch user details
    result = await session.execute(select(Users).where(Users.email == email))
    db_user = result.scalars().first()

    if not db_user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Fetch projects associated with the user
    result = await session.execute(select(DBProject).where(DBProject.user_id == db_user.id))
    projects = result.scalars().all()

    return [{
      "link": project.link,
      "owner": {
        "id": project.owner.id,
        "email": project.owner.email,
        "username": project.owner.username
      },
      "changed_at": project.changed_at.isoformat(),
      "created_at": project.created_at.isoformat(),
    } for project in projects]

  except jwt.PyJWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

@router.post('/add_project', response_model=list[ProjectResponse], tags=['Projects'])
async def create_project(request: Request, session: AsyncSession = Depends(get_async_session)):
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

    # Fetch user details
    result = await session.execute(select(Users).where(Users.email == email))
    db_user = result.scalars().first()

    if not db_user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Create a new project, with link and timestamps handled automatically
    new_project = DBProject(
      user_id=db_user.id
    )

    session.add(new_project)
    await session.commit()

    return {"message": "Project created successfully", "project_id": new_project.id}

  except jwt.PyJWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")