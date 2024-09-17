import pytest
from core.security import hash_password, verify_password

@pytest.mark.parametrize("password", [
  "simplepassword",
  "123456789",
  "PasswordWithSymbols!@#",
  "парольНаКириллице"
])
def test_hash_password(password):
  hashed_password = hash_password(password)
  assert hashed_password != password, "Хэшированный пароль не должен быть равен исходному паролю"
  assert hashed_password.startswith("$2b$"), "Хэш должен начинаться с префикса bcrypt"

@pytest.mark.parametrize("password", [
  "simplepassword",
  "123456789",
  "PasswordWithSymbols!@#",
  "парольНаКириллице"
])
def test_verify_password(password):
  hashed_password = hash_password(password)
  assert verify_password(password, hashed_password), "Пароль должен быть верифицирован"
  assert not verify_password("wrongpassword", hashed_password), "Верификация должна провалиться для неверного пароля"