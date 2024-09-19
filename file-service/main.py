from fastapi import FastAPI

def create_app() -> FastAPI:
  app = FastAPI(title='Keplerix', docs_url='/api/docs', description='Web application for collaborative interface design')
  
  return app