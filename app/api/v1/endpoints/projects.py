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

@router.get('/project', response_model=ProjectResponse, tags=['Projects'])
async def get_project(
  project_link: str, 
  request: Request, 
  session: AsyncSession = Depends(get_async_session)
):
  email = await verify_token(request)
  user = await get_user_by_email(session, email)
  result = await session.execute(select(DBProject).where(DBProject.link == project_link, DBProject.user_id == user.id))
  project = result.scalars().first()
  
  if not project:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
  
  return format_project_response(project, user)

@router.get('/projects', response_model=list[ProjectResponse], tags=['Projects'])
async def get_projects(request: Request, session: AsyncSession = Depends(get_async_session)):
  email = await verify_token(request)
  user = await get_user_by_email(session, email)
  projects = await get_projects_by_user(session, user.id)
  
  return [format_project_response(project, user) for project in projects]

@router.post('/add_project', response_model=ProjectResponse, tags=['Projects'])
async def create_project(request: Request, session: AsyncSession = Depends(get_async_session)):
  email = await verify_token(request)
  user = await get_user_by_email(session, email)
  
  new_project = DBProject(user_id=user.id, link=str(uuid4()))
  session.add(new_project)
  await session.commit()
  await session.refresh(new_project)
  
  return format_project_response(new_project, user)

@router.delete('/delete_all_projects', tags=['Projects'])
async def delete_all_projects(request: Request, session: AsyncSession = Depends(get_async_session)):
  email = await verify_token(request)
  user = await get_user_by_email(session, email)
  projects = await get_projects_by_user(session, user.id)
  
  if not projects:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found for the user")
  
  for project in projects:
    await session.delete(project)
  await session.commit()

  return {"message": "All projects deleted successfully"}

@router.delete('/delete_project/{project_link}', tags=['Projects'])
async def delete_project(project_link: str, request: Request, session: AsyncSession = Depends(get_async_session)):
  email = await verify_token(request)
  user = await get_user_by_email(session, email)
  
  result = await session.execute(select(DBProject).where(DBProject.link == project_link, DBProject.user_id == user.id))
  project = result.scalars().first()

  if not project:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or not owned by user")

  await session.delete(project)
  await session.commit()

  return {"message": "Project deleted successfully"}

@router.delete('/delete_projects', tags=['Projects'])
async def delete_projects(project_links: ProjectsDelete, request: Request, session: AsyncSession = Depends(get_async_session)):
  email = await verify_token(request)
  user = await get_user_by_email(session, email)
  
  result = await session.execute(select(DBProject).where(DBProject.link.in_(project_links.links), DBProject.user_id == user.id))
  projects = result.scalars().all()

  if not projects:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found to delete or not owned by user")

  for project in projects:
    await session.delete(project)
  await session.commit()

  return {"message": "Selected projects deleted successfully"}