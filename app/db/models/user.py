from datetime import datetime, timezone
from sqlalchemy import Table, Column, Integer, String, Boolean, TIMESTAMP, func, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from db.base import Base, metadata
from db.models.project import Project

users = Table(
  "users",
  metadata,
  Column("id", Integer, primary_key=True, index=True, autoincrement=True),
  Column("email", String, unique=True, index=True, nullable=False),
  Column("username", String(length=256), primary_key=True),
  Column("hashed_password", String, nullable=False),
  Column('projects_count', Integer, default=0),
  Column("is_active", Boolean, default=True),
  Column("is_superuser", Boolean, default=False),
  Column("is_verified", Boolean, default=False),
  Column('created_at', TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
)

class Users(Base):
  __tablename__ = "users"
  
  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String(length=256), nullable=False)
  email = Column(String(length=320), unique=True, index=True, nullable=False)
  hashed_password = Column(String(length=1024), nullable=False)
  is_active = Column(Boolean, default=True)
  is_superuser = Column(Boolean, default=False)
  is_verified = Column(Boolean, default=False)
  created_at = Column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))

  projects = relationship("Project", back_populates="owner")

  async def get_projects_count(self, session: AsyncSession) -> int:
    result = await session.execute(
      select(func.count().label('count'))
      .select_from(Project)
      .where(Project.user_id == self.id)
    )
    count = result.scalar()
    return count