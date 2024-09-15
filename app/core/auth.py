import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict
from core.config import settings
from core.redis import redis_client

async def create_access_token(email: str, data: Dict[str, str], expires_delta: timedelta = timedelta(minutes=15)) -> str:
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + expires_delta
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

  await redis_client.set(email, encoded_jwt, ex=expires_delta)
  
  return encoded_jwt

def verify_access_token(email: str) -> Dict[str, str]:
  token = redis_client.get(email)
  if token:
    try:
      payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
      return payload
    except jwt.PyJWTError:
      return {}
  return {}