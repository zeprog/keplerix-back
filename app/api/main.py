from fastapi import FastAPI

def create_app() -> FastAPI:
    """Создание и настройка экземпляра приложения FastAPI."""
    
    app = FastAPI(
        title='Keplerix',
        docs_url='/api/docs',
        description='Web application for collaborative interface design',
        # lifespan=lifespan
    )
    
    return app