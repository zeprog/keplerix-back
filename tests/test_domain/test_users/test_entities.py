import pytest
from pydantic import ValidationError
from domain.users.entities import *

def test_user_create_valid_data():
  user = UserCreate(username="testuser", email="test@example.com", password="securepassword")
  assert user.username == "testuser"
  assert user.email == "test@example.com"
  assert user.password == "securepassword"

def test_user_create_missing_username():
  user = UserCreate(email="test@example.com", password="securepassword")
  assert user.username is None
  assert user.email == "test@example.com"
  assert user.password == "securepassword"

def test_user_login_valid_data():
  login = UserLogin(email="test@example.com", password="securepassword")
  assert login.email == "test@example.com"
  assert login.password == "securepassword"

def test_user_logout_valid_data():
  logout = UserLogout(email="test@example.com")
  assert logout.email == "test@example.com"

def test_forgot_password_and_verify_acc_request_valid_data():
  request = ForgotPasswordAndVerifyAccRequest(email="test@example.com")
  assert request.email == "test@example.com"

def test_reset_password_request_valid_data():
  request = ResetPasswordRequest(email="test@example.com", token="some-token", new_password="newpassword")
  assert request.email == "test@example.com"
  assert request.token == "some-token"
  assert request.new_password == "newpassword"

def test_verify_acc_request_valid_data():
  request = VerifyAccRequest(email="test@example.com", token="some-token")
  assert request.email == "test@example.com"
  assert request.token == "some-token"

def test_user_info_valid_data():
  info = UserInfo(email="test@example.com", username="testuser", is_active=True, is_superuser=False, is_verified=True)
  assert info.email == "test@example.com"
  assert info.username == "testuser"
  assert info.is_active is True
  assert info.is_superuser is False
  assert info.is_verified is True

def test_user_info_for_update_valid_data():
  update = UserInfoForUpdate(email="test@example.com", username="newusername")
  assert update.email == "test@example.com"
  assert update.username == "newusername"

def test_user_info_for_update_missing_data():
  update = UserInfoForUpdate()
  assert update.email is None
  assert update.username is None

def test_user_create_invalid_email():
  with pytest.raises(ValidationError):
    UserCreate(username="testuser", email="invalid-email", password="securepassword")

def test_user_create_missing_email():
  with pytest.raises(ValidationError):
    UserCreate(username="testuser", password="securepassword")