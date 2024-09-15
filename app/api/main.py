import json
from datetime import timedelta
from fastapi import BackgroundTasks, FastAPI, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.auth import create_access_token, verify_access_token
from core.security import hash_password, verify_password
from core.redis import redis_client
from db import session
from db.models.user import Users
from db.session import get_async_session
from domain.users.entities import ForgotPasswordRequest, ResetPasswordRequest, UserCreate, UserLogin, UserLogout

async def send_reset_password_email(email: str, token: str):
    print('RESET TOKEN', token)

def create_app() -> FastAPI:
  app = FastAPI(title='Keplerix', docs_url='/api/docs', description='Web application for collaborative interface design')

  @app.post("/register", tags=['Auth'])
  async def register(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    hashed_password = hash_password(user.password)
    new_user = Users(username=user.username, email=user.email, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    return {"message": "User created"}

  @app.post("/login", tags=['Auth'])
  async def login(user: UserLogin, response: Response, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Users).where(Users.email == user.email))
    db_user = result.scalars().first()
    if db_user is None or not verify_password(user.password, db_user.hashed_password):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = await create_access_token(db_user.email, data={"sub": db_user.email})
    response.set_cookie(key="keplerix_token", value=access_token, httponly=True, secure=True, samesite="lax")
    
    return {"message": "Login successful"}
  
  @app.post("/logout", tags=['Auth'])
  async def logout(request: Request, response: Response, user: UserLogout):
    token_cookie_data = request.cookies.get("keplerix_token")
    
    if not token_cookie_data:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token missing in cookies")
      
    redis_key = f"{user.email}"
    token_redis_data = await redis_client.get(redis_key)
    
    if token_redis_data and token_redis_data == token_cookie_data:
      await redis_client.delete(redis_key)
      response.delete_cookie(key="keplerix_token")
      return {"message": "Logout successful"}
    else:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    
  @app.post('/forgot-password', tags=["Auth"])
  async def forgot_password(user_data: ForgotPasswordRequest, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Users).where(Users.email == user_data.email))
    db_user = result.scalars().first()
    
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    reset_token = await create_access_token(db_user.email, data={"sub": db_user.email}, expires_delta=timedelta(hours=1))
    await redis_client.set(f"reset_password:{db_user.email}", json.dumps({"token": reset_token}), ex=3600)
    background_tasks.add_task(send_reset_password_email, user_data.email, reset_token)
    
    return {"message": "Password reset token has been sent to your email."}
    
  @app.post("/reset-password", tags=["Auth"])
  async def reset_password(request: ResetPasswordRequest, session: AsyncSession = Depends(get_async_session)):
    redis_key = f"reset_password:{request.email}"
    stored_token_json = await redis_client.get(redis_key)

    if not stored_token_json:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    stored_token_data = json.loads(stored_token_json)
    stored_token = stored_token_data.get("token")

    if not stored_token or stored_token != request.token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    token_payload = await verify_access_token(request.email)

    if "sub" not in token_payload or token_payload["sub"] != request.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token structure")

    result = await session.execute(select(Users).where(Users.email == request.email))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_user.hashed_password = hash_password(request.new_password)
    await session.commit()
    await redis_client.delete(redis_key)

    return {"message": "Password has been reset successfully."}
    
  return app