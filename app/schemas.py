from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    custom_alias: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    last_clicked: Optional[datetime]

    model_config = {
        "from_attributes": True
    }

class LinkStats(BaseModel):
    original_url: HttpUrl
    short_code: str
    custom_alias: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    last_clicked: Optional[datetime]

    class Config:
        orm_mode = True

class LinkUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None
    expires_at: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
