from datetime import datetime, timezone
from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, TIMESTAMP

metadata = MetaData()

users = Table(
  "users",
  metadata,
  Column("id", Integer, primary_key=True, index=True),
  Column("email", String, unique=True, index=True, nullable=False),
  Column("hashed_password", String, nullable=False),
  Column("is_active", Boolean, default=True),
  Column("is_superuser", Boolean, default=False),
  Column('created_at', TIMESTAMP, default=datetime.now(timezone.utc))
)