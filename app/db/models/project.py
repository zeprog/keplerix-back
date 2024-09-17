from datetime import datetime, timezone
import uuid
from sqlalchemy import ForeignKey, Table, Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from db.base import Base, metadata

now = datetime.now(timezone.utc)

def generate_unique_link():
    return str(uuid.uuid4()) 

projects = Table(
  "projects",
  metadata,
  Column("id", Integer, primary_key=True, index=True, autoincrement=True),
  Column("user_id", Integer, ForeignKey('users.id'), nullable=False),
  Column("link", String, unique=True, nullable=False, default=generate_unique_link),
  Column("changed_at", TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)),
  Column('created_at', TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
)

class Project(Base):
  __tablename__ = "projects"
  
  id = Column(Integer, primary_key=True, autoincrement=True)
  user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
  link = Column(String, unique=True, nullable=False, default=generate_unique_link)
  changed_at = Column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
  created_at = Column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))

  owner = relationship("Users", back_populates="projects")