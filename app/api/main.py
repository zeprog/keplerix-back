from fastapi import FastAPI, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.auth import create_access_token
from core.security import hash_password, verify_password
from core.redis import redis_client
from db.models.user import Users
from db.session import get_async_session
from domain.users.entities import UserCreate, UserLogin, UserLogout

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
    
  return app