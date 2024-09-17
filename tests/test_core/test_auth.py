import pytest
import jwt
from core.auth import create_access_token, create_refresh_token, generate_reset_password_token, verify_access_token
from core.redis import redis_client
from core.config import settings
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

@pytest.fixture(scope="module")
def mock_redis_client():
  mock_client = AsyncMock()
  redis_client.set = mock_client.set
  redis_client.get = mock_client.get
  return mock_client

@pytest.fixture
def test_settings():
  settings.SECRET_KEY = "test_secret"
  settings.ALGORITHM = "HS256"
  return settings

@pytest.fixture
async def clear_redis(mock_redis_client):
  await mock_redis_client.flushdb()

@pytest.mark.asyncio
async def test_create_access_token(mock_redis_client, test_settings):
  email = "test@example.com"
  data = {"some": "data"}
  token = await create_access_token(email, data=data)
  mock_redis_client.set.assert_called_once()
  expire_time = datetime.now(timezone.utc) + timedelta(minutes=60)
  mock_redis_client.set.assert_called_with(email, token, ex=timedelta(minutes=60))
  decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
  assert decoded["some"] == "data"
  assert decoded["exp"] > datetime.now(timezone.utc).timestamp()

@pytest.mark.asyncio
async def test_create_refresh_token(clear_redis, mock_redis_client, test_settings):
  email = "test@example.com"
  token = await create_refresh_token(email=email)
  expected_key = f"refresh_token:{email}"
  expected_token = token
  expected_expiration = timedelta(days=90)
  print("Actual calls:", mock_redis_client.set.call_args_list)
  call_found = False
  for call in mock_redis_client.set.call_args_list:
    call_key, call_token = call[0]
    call_expiration = call[1]['ex']

    if (call_key == expected_key and call_token == expected_token and abs((call_expiration - expected_expiration).total_seconds()) < 1):
      call_found = True
      break

  assert call_found, f"Expected call with ({expected_key}, {expected_token}, {expected_expiration}) not found. Actual calls: {mock_redis_client.set.call_args_list}"

@pytest.mark.asyncio
async def test_verify_access_token(mock_redis_client, test_settings):
  email = "test@example.com"
  valid_token = await create_access_token(email, data={})
  mock_redis_client.get.return_value = valid_token
  
  payload = await verify_access_token(email=email)
  assert payload is not None
  assert payload.get("exp") is not None
  mock_redis_client.get.return_value = "invalid_token"
  payload = await verify_access_token(email=email)
  assert payload == {}

@pytest.mark.asyncio
async def test_generate_reset_password_token(mock_redis_client, test_settings):
  email = "test@example.com"
  reset_token = await generate_reset_password_token(email=email)
  redis_key = f"reset_password:{email}"
  mock_redis_client.set.assert_any_call(redis_key, reset_token, ex=3600)