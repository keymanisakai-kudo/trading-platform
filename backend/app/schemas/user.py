from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)


# Wallet Schemas
class BalanceResponse(BaseModel):
    currency: str
    available: float
    locked: float
    total: float
    
    class Config:
        from_attributes = True


class WalletBalanceResponse(BaseModel):
    balances: list[BalanceResponse]
    total_usdt_value: float


class DepositAddressResponse(BaseModel):
    currency: str
    address: str
    network: str


class WithdrawRequest(BaseModel):
    currency: str = "USDT"
    address: str
    amount: float = Field(..., gt=0)
    network: str = "TRC20"


class TransactionResponse(BaseModel):
    id: uuid.UUID
    type: str
    amount: float
    fee: float
    status: str
    tx_hash: Optional[str]
    address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
