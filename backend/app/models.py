from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class UserRole(str, enum.Enum):
    owner = "owner"
    tenant = "tenant"
    admin = "admin"

class InterestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    listings = relationship("Listing", back_populates="owner")
    tenant_profile = relationship("TenantProfile", back_populates="user", uselist=False)

class TenantProfile(Base):
    __tablename__ = "tenant_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    preferred_location = Column(String, nullable=False)
    budget_min = Column(Float, nullable=False)
    budget_max = Column(Float, nullable=False)
    move_in_date = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tenant_profile")

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(String, nullable=False)
    rent = Column(Float, nullable=False)
    available_from = Column(DateTime, nullable=False)
    room_type = Column(String, nullable=False)
    furnishing_status = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    is_filled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="listings")

class CompatibilityScore(Base):
    __tablename__ = "compatibility_scores"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    score = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)
    source = Column(String, default="rule_based")  # "llm" or "rule_based"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InterestRequest(Base):
    __tablename__ = "interest_requests"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    status = Column(Enum(InterestStatus), default=InterestStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    interest_request_id = Column(Integer, ForeignKey("interest_requests.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())