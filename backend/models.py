from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(UserBase):
    id: str
    elevenlabs_key: Optional[str] = None
    created_at: str  # Store as ISO format string
    last_login: Optional[str] = None  # Store as ISO format string

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    elevenlabs_key: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str 