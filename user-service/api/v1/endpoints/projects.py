from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.dependencies import format_project_response, get_projects_by_user, get_user_by_email, verify_token
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