from typing import List, Optional

from pydantic import BaseModel, EmailStr


# -------------------------
# Authentication Schemas
# -------------------------

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# -------------------------
# Home Planner
# -------------------------

class HomeBudgetInput(BaseModel):
    total_budget: float
    num_lights: int = 0
    num_fans: int = 0
    num_furniture: int = 0
    num_dining_tables: int = 0
    preferences: Optional[str] = None


# -------------------------
# Party Planner
# -------------------------

class PartyBudgetInput(BaseModel):
    total_budget: float
    party_type: str
    num_guests: int
    preferences: Optional[str] = None


# -------------------------
# Jewelry Planner
# -------------------------

class JewelryBudgetInput(BaseModel):
    total_budget: float
    occasion: str
    preferences: Optional[str] = None


# -------------------------
# Recommendation Response
# -------------------------

class RecommendationItem(BaseModel):
    name: str
    description: str
    estimated_price: Optional[float] = None
    platform: Optional[str] = None
    link: Optional[str] = None


class RecommendationResponse(BaseModel):
    category: str
    budget: float
    summary: str
    recommendations: List[RecommendationItem] = []