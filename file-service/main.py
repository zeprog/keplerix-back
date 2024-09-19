from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
  return app