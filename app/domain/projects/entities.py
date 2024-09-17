from datetime import datetime
from pydantic import BaseModel

class ProjectOwner(BaseModel):
  id: int
  email: str
  username: str

class ProjectResponse(BaseModel):
  link: str  
  changed_at: str
  created_at: str
  owner: ProjectOwner

class ProjectCreate(BaseModel):
  link: str
  changed_at: datetime
  created_at: datetime