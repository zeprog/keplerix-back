from fastapi import FastAPI
from fastapi_users import FastAPIUsers, fastapi_users
from core.auth import auth_backend
from core.manager import get_user_manager
from db.models.user import Users
from domain.users.entities import UserCreate, UserRead

def create_app() -> FastAPI:
    """Создание и настройка экземпляра приложения FastAPI."""
    
    app = FastAPI(
        title='Keplerix',
        docs_url='/api/docs',
        description='Web application for collaborative interface design',
        # lifespan=lifespan
    )

    fastapi_users = FastAPIUsers[Users, int](
        get_user_manager,
        [auth_backend],
    )

    app.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/auth",
        tags=["auth"],
    )

    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    
    return app