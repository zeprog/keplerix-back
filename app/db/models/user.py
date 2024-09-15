from datetime import datetime, timezone
from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase

metadata = MetaData()

aware_datetime = datetime(2024, 9, 14, 15, 48, 25, tzinfo=timezone.utc)
naive_datetime = aware_datetime.replace(tzinfo=None)

users = Table(
  "users",
  metadata,
  Column("id", Integer, primary_key=True, index=True, autoincrement=True),
  Column("email", String, unique=True, index=True, nullable=False),
  Column("username", String(length=256), primary_key=True),
  Column("hashed_password", String, nullable=False),
  Column("is_active", Boolean, default=True),
  Column("is_superuser", Boolean, default=False),
  Column("is_verified", Boolean, default=False),
  Column('created_at', TIMESTAMP, default=lambda: naive_datetime)
)

class Base(DeclarativeBase):
  pass

class Users(Base):
  __tablename__ = "users"
  
  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String(length=256), nullable=False)
  email = Column(String(length=320), unique=True, index=True, nullable=False)
  hashed_password = Column(String(length=1024), nullable=False)
  is_active = Column(Boolean, default=True)
  is_superuser = Column(Boolean, default=False)
  is_verified = Column(Boolean, default=False)
  created_at = Column(TIMESTAMP, default=lambda: naive_datetime)