import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict
from core.config import settings
from core.redis import redis_client

async def create_access_token(email: str, data: Dict[str, str], expires_delta: timedelta = timedelta(minutes=60)) -> str:
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + expires_delta
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

  await redis_client.set(email, encoded_jwt, ex=expires_delta)
  
  return encoded_jwt

async def create_refresh_token(email: str, expires_delta: timedelta = timedelta(days=90)) -> str:
  to_encode = {"sub": email}
  expire = datetime.now(timezone.utc) + expires_delta
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
  
  await redis_client.set(f"refresh_token:{email}", encoded_jwt, ex=expires_delta)
  
  return encoded_jwt

async def verify_access_token(email: str) -> Dict[str, str]:
  token = await redis_client.get(email)
  if token:
    try:
      payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
      return payload
    except jwt.PyJWTError:
      return {}
  return {}

async def generate_reset_password_token(email: str) -> str:
  reset_token_data = {"sub": email}
  reset_token = create_access_token(email, data=reset_token_data, expires_delta=timedelta(hours=1))
  redis_key = f"reset_password:{email}"
  await redis_client.set(redis_key, reset_token, ex=3600)

  return reset_token