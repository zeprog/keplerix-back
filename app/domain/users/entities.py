from typing import Optional
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
  username: Optional[str] = None
  email: str
  password: str

class UserLogin(BaseModel):
  email: str
  password: str

class UserLogout(BaseModel):
  email: str

class ForgotPasswordAndVerifyAccRequest(BaseModel):
  email: EmailStr

class ResetPasswordRequest(BaseModel):
  email: str
  token: str
  new_password: str

class VerifyAccRequest(BaseModel):
  email: str
  token: str

class UserInfo(BaseModel):
  email: str
  username: str
  is_active: bool
  is_superuser: bool
  is_verified: bool

class UserInfoForUpdate(BaseModel):
  email: Optional[str] = None
  username: Optional[str] = None