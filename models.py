# models.py
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)  # Unique user identifier (e.g., "suvodutta" for superuser)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth accounts
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Fields for email verification and password reset
    email_verification_token = Column(String, nullable=True)
    password_reset_token = Column(String, nullable=True)
    token_expiration = Column(DateTime, nullable=True)
