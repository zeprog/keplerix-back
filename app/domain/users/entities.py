from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
  username: str
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