from fastapi import FastAPI
from api.v1.endpoints.auth import router as auth_router

def create_app() -> FastAPI:
  app = FastAPI(title='Keplerix', docs_url='/api/docs', description='Web application for collaborative interface design')

  app.include_router(auth_router, prefix="/auth")
  
  return app