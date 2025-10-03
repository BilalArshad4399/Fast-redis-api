from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models import TransactionType


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    api_key: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserPublic(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount (must be positive)")
    description: Optional[str] = None
    transaction_type: TransactionType


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
