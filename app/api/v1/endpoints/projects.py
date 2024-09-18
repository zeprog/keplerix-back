import jwt
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.redis import redis_client
from core.config import settings
from db.models.user import Users
from db.models.project import Project as DBProject
from db.session import get_async_session
from domain.projects.entities import ProjectResponse, ProjectsDelete

router = APIRouter()

@router.get('/project', response_model=ProjectResponse, tags=['Projects'])
async def get_project(
  project_link: str,
  request: Request,
  session: AsyncSession = Depends(get_async_session)
):
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

        result = await session.execute(select(DBProject).where(DBProject.link == project_link, DBProject.user_id == db_user.id))
        project = result.scalars().first()

        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        return {
            "link": project.link,
            "owner": {
                "id": db_user.id,
                "email": db_user.email,
                "username": db_user.username
            },
            "changed_at": project.changed_at.isoformat(),
            "created_at": project.created_at.isoformat(),
        }

    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

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

    result = await session.execute(select(Users).where(Users.email == email))
    db_user = result.scalars().first()

    if not db_user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

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
  
@router.post('/add_project', response_model=ProjectResponse, tags=['Projects'])
async def create_project(
    request: Request, 
    session: AsyncSession = Depends(get_async_session)
):
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

        new_project_link = f"{uuid4()}"
        new_project = DBProject(
            user_id=db_user.id,
            link=new_project_link
        )

        session.add(new_project)
        await session.commit()
        await session.refresh(new_project)

        return {
            "link": new_project.link,
            "owner": {
                "id": db_user.id,
                "email": db_user.email,
                "username": db_user.username
            },
            "changed_at": new_project.changed_at.isoformat(),
            "created_at": new_project.created_at.isoformat(),
        }

    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
  
@router.delete('/delete_all_projects', tags=['Projects'])
async def delete_all_projects(request: Request, session: AsyncSession = Depends(get_async_session)):
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

    # Fetch and delete all projects associated with the user
    result = await session.execute(select(DBProject).where(DBProject.user_id == db_user.id))
    projects = result.scalars().all()

    if not projects:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found for the user")

    for project in projects:
      await session.delete(project)
    
    await session.commit()

    return {"message": "All projects deleted successfully"}

  except jwt.PyJWTError:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
  
@router.delete('/delete_project/{project_link}', tags=['Projects'])
async def delete_project(project_link: str, request: Request, session: AsyncSession = Depends(get_async_session)):
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

    # Fetch the project to delete
    result = await session.execute(select(DBProject).where(DBProject.link == project_link, DBProject.user_id == db_user.id))
    project = result.scalars().first()

    if not project:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or not owned by user")

    # Delete the project
    await session.delete(project)
    await session.commit()

    return {"message": "Project deleted successfully"}

  except jwt.PyJWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

@router.delete('/delete_projects', tags=['Projects'])
async def delete_projects(project_links: ProjectsDelete, request: Request, session: AsyncSession = Depends(get_async_session)):
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

    # Fetch the projects to delete
    result = await session.execute(
      select(DBProject).where(DBProject.link.in_(project_links.links), DBProject.user_id == db_user.id)
    )
    projects = result.scalars().all()

    if not projects:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found to delete or not owned by user")

    # Delete the projects
    for project in projects:
      await session.delete(project)
    
    await session.commit()

    return {"message": "Selected projects deleted successfully"}

  except jwt.PyJWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")