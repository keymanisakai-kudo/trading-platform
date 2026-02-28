from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class OrderCreate(BaseModel):
    symbol: str = Field(..., example="BTCUSDT")
    side: str = Field(..., pattern="^(buy|sell)$")
    order_type: str = Field(..., pattern="^(limit|market)$")
    amount: float = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)


class OrderResponse(BaseModel):
    id: uuid.UUID
    symbol: str
    side: str
    order_type: str
    price: Optional[float]
    amount: float
    filled_amount: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int


class TradeResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    symbol: str
    side: str
    price: float
    amount: float
    fee: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderCancelResponse(BaseModel):
    id: uuid.UUID
    status: str
    message: str
