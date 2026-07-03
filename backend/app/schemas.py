from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum
from .models import UserRole

class PublicRole(str, Enum):
    owner = "owner"
    tenant = "tenant"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: PublicRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ListingCreate(BaseModel):
    location: str
    rent: float
    available_from: datetime
    room_type: str
    furnishing_status: str
    photo_url: Optional[str] = None

class ListingOut(BaseModel):
    id: int
    owner_id: int
    location: str
    rent: float
    available_from: datetime
    room_type: str
    furnishing_status: str
    photo_url: Optional[str]
    is_filled: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CompatibilityScoreOut(BaseModel):
    id: int
    tenant_id: int
    listing_id: int
    score: int
    explanation: str
    source: str
    created_at: datetime

    class Config:
        from_attributes = True

class TenantProfileCreate(BaseModel):
    preferred_location: str
    budget_min: float
    budget_max: float
    move_in_date: Optional[datetime] = None

class TenantProfileOut(BaseModel):
    id: int
    user_id: int
    preferred_location: str
    budget_min: float
    budget_max: float
    move_in_date: Optional[datetime]

    class Config:
        from_attributes = True