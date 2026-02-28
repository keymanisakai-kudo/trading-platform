from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.order import Order, Trade
from app.models.wallet import Wallet
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    TradeResponse,
    OrderCancelResponse,
)
from app.api.v1.auth import get_current_user
from datetime import datetime


router = APIRouter(prefix="/orders", tags=["Orders"])


# Mock Binance order execution (in production, use real Binance API)
async def execute_order(order: Order, db: AsyncSession) -> bool:
    """Execute order via Binance API (mock)"""
    # In production, this would call Binance API
    # For now, simulate order execution
    order.status = "filled"
    order.filled_amount = order.amount
    order.updated_at = datetime.utcnow()
    
    # Update wallet balance
    result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == order.user_id,
            Wallet.currency == order.symbol.replace("USDT", "")
        )
    )
    wallet = result.scalar_one_or_none()
    
    if wallet:
        if order.side == "buy":
            # Add bought amount
            wallet.balance = float(wallet.balance) + float(order.amount)
        else:
            # Deduct sold amount
            wallet.balance = float(wallet.balance) - float(order.amount)
    
    # Create trade record
    trade = Trade(
        order_id=order.id,
        user_id=order.user_id,
        symbol=order.symbol,
        side=order.side,
        price=float(order.price) if order.price else 0,
        amount=order.amount,
        fee=order.amount * 0.001,
    )
    db.add(trade)
    
    return True


@router.get("/", response_model=OrderListResponse)
async def list_orders(
    symbol: str = None,
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Order).where(Order.user_id == current_user.id)
    
    if symbol:
        query = query.where(Order.symbol == symbol)
    if status:
        query = query.where(Order.status == status)
    
    # Get total count
    result = await db.execute(query)
    total = len(result.scalars().all())
    
    # Get paginated results
    result = await db.execute(
        query.order_by(Order.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    orders = result.scalars().all()
    
    return OrderListResponse(
        orders=[OrderResponse.model_validate(o) for o in orders],
        total=total
    )


@router.post("/limit", response_model=OrderResponse)
async def place_limit_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if order_data.order_type != "limit" or not order_data.price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order type for this endpoint"
        )
    
    # Get user wallet for the currency
    currency = order_data.symbol.replace("USDT", "")
    result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == current_user.id,
            Wallet.currency == currency
        )
    )
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No wallet found for {currency}"
        )
    
    # Check balance for sell orders
    if order_data.side == "sell":
        available = float(wallet.balance)
        if available < order_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        # Lock the amount
        wallet.locked = float(wallet.locked) + order_data.amount
    
    # Create order
    order = Order(
        user_id=current_user.id,
        symbol=order_data.symbol,
        side=order_data.side,
        order_type=order_data.order_type,
        price=order_data.price,
        amount=order_data.amount,
        status="open",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # Execute immediately for market orders (simulated)
    if order_data.order_type == "market":
        await execute_order(order, db)
        await db.commit()
    
    return order


@router.post("/market", response_model=OrderResponse)
async def place_market_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Similar to limit order but executes immediately
    order_data.order_type = "market"
    order_data.price = None  # Market price
    
    return await place_limit_order(order_data, current_user, db)


@router.delete("/{order_id}", response_model=OrderCancelResponse)
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from uuid import UUID
    
    try:
        order_uuid = UUID(order_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID"
        )
    
    result = await db.execute(
        select(Order).where(
            Order.id == order_uuid,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status not in ["open", "pending", "partially_filled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status {order.status}"
        )
    
    # Cancel the order
    order.status = "cancelled"
    order.updated_at = datetime.utcnow()
    
    # Release locked funds
    if order.side == "sell":
        currency = order.symbol.replace("USDT", "")
        result = await db.execute(
            select(Wallet).where(
                Wallet.user_id == current_user.id,
                Wallet.currency == currency
            )
        )
        wallet = result.scalar_one_or_none()
        if wallet:
            wallet.locked = float(wallet.locked) - float(order.amount - order.filled_amount)
            wallet.balance = float(wallet.balance) + float(order.amount - order.filled_amount)
    
    await db.commit()
    
    return OrderCancelResponse(
        id=order.id,
        status="cancelled",
        message="Order cancelled successfully"
    )


@router.get("/{order_id}/trades", response_model=list[TradeResponse])
async def get_order_trades(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from uuid import UUID
    
    try:
        order_uuid = UUID(order_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID"
        )
    
    result = await db.execute(
        select(Trade).where(
            Trade.order_id == order_uuid,
            Trade.user_id == current_user.id
        )
    )
    trades = result.scalars().all()
    
    return trades
