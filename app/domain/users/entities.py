from typing import Optional
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
  username: Optional[str] = None
  email: EmailStr  
  password: str

class UserLogin(BaseModel):
  email: EmailStr  
  password: str

class UserLogout(BaseModel):
  email: EmailStr  

class ForgotPasswordAndVerifyAccRequest(BaseModel):
  email: EmailStr

class ResetPasswordRequest(BaseModel):
  email: EmailStr  
  token: str
  new_password: str

class VerifyAccRequest(BaseModel):
  email: EmailStr  
  token: str

class UserInfo(BaseModel):
  email: EmailStr  
  username: str
  is_active: bool
  is_superuser: bool
  is_verified: bool
  projects_count: int

class UserInfoForUpdate(BaseModel):
  email: Optional[EmailStr] = None
  username: Optional[str] = None