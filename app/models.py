from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, Text, JSON
from datetime import datetime, timezone
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    last_password_reset = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(Text, nullable=False)
    user_id = Column(Integer, nullable=True)
    event_metadata = Column(JSON, nullable=True, name="metadata")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
