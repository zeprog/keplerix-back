from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.users import router as users_router
from api.v1.endpoints.projects import router as projects_router

def create_app() -> FastAPI:
  app = FastAPI(title='Keplerix', docs_url='/api/docs', description='Web application for collaborative interface design')
  origins = [
    "http://localhost:3000",
  ]
  app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )
  app.include_router(auth_router, prefix="/auth")
  app.include_router(users_router, prefix="/user")
  app.include_router(projects_router, prefix="/project")
  
  return app