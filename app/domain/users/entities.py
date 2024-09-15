from pydantic import BaseModel

class UserCreate(BaseModel):
  username: str
  email: str
  password: str

class UserLogin(BaseModel):
  email: str
  password: str

class UserLogout(BaseModel):
  email: str