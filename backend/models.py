from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    elevenlabs_key: Optional[str] = None

class UserProfile(UserBase):
    id: str
    created_at: datetime
    elevenlabs_key: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: Optional[str] = None

class TokenData(BaseModel):
    username: Optional[str] = None

class ActivityLog(BaseModel):
    text: str
    timestamp: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = "text"

class VoiceRequest(BaseModel):
    audio_data: str

class QueryRequest(BaseModel):
    query: str
    timeframe: Optional[str] = None

class LogQuery(BaseModel):
    query: str
    timeframe: Optional[str] = None
    category_filter: Optional[str] = None

class Conversation(BaseModel):
    id: str
    user_id: str
    type: str
    raw_conversation: Dict
    activities: List[Dict]
    summary: Dict
    timestamp: datetime

class Category(BaseModel):
    name: str
    count: int
    metadata: Dict = Field(default_factory=dict)

class VisualizationData(BaseModel):
    last_updated: datetime
    total_activities: int
    stats: Dict
    trends: Dict 