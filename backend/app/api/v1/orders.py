"""Orders API - DDD Style"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from decimal import Decimal
from typing import Optional

from app.api.v1.deps import (
    get_current_user,
    get_order_repo,
    get_wallet_repo,
    get_db,
)
from app.infrastructure.persistence.repositories import (
    SQLAlchemyOrderRepository,
    SQLAlchemyWalletRepository,
)
from app.application.orders.commands import (
    PlaceOrderCommand,
    PlaceOrderHandler,
    CancelOrderCommand,
    CancelOrderHandler,
)
from app.application.orders.queries import (
    GetOrderQuery,
    GetOrderHandler,
    ListOrdersQuery,
    ListOrdersHandler,
)
from app.domain.user.aggregate import User


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/")
async def list_orders(
    symbol: Optional[str] = Query(None, description="Filter by symbol (e.g., BTCUSDT)"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """List user's orders"""
    order_repo = SQLAlchemyOrderRepository(db)
    handler = ListOrdersHandler(order_repo)
    
    query = ListOrdersQuery(
        user_id=current_user.id,
        symbol=symbol,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    
    result = await handler.handle(query)
    
    return {
        "orders": result.orders,
        "total": result.total,
    }


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Get order details"""
    try:
        order_uuid = UUID(order_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    
    order_repo = SQLAlchemyOrderRepository(db)
    handler = GetOrderHandler(order_repo)
    
    query = GetOrderQuery(
        order_id=order_uuid,
        user_id=current_user.id,
    )
    
    result = await handler.handle(query)
    
    if not result.order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.message
        )
    
    return result.order


@router.post("/")
async def place_order(
    symbol: str = Query(..., description="Trading symbol (e.g., BTCUSDT)"),
    side: str = Query(..., description="buy or sell"),
    order_type: str = Query(..., description="market or limit"),
    quantity: float = Query(..., gt=0, description="Order quantity"),
    price: Optional[float] = Query(None, gt=0, description="Limit price (required for limit orders)"),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Place a new order"""
    order_repo = SQLAlchemyOrderRepository(db)
    wallet_repo = SQLAlchemyWalletRepository(db)
    
    handler = PlaceOrderHandler(order_repo, wallet_repo)
    
    command = PlaceOrderCommand(
        user_id=current_user.id,
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=Decimal(str(quantity)),
        price=Decimal(str(price)) if price else None,
    )
    
    result = await handler.handle(command)
    
    if result.status in ["rejected", "failed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    await db.commit()
    
    return {
        "order_id": str(result.order_id),
        "status": result.status,
        "message": result.message,
    }


@router.delete("/{order_id}")
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Cancel an order"""
    try:
        order_uuid = UUID(order_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    
    order_repo = SQLAlchemyOrderRepository(db)
    handler = CancelOrderHandler(order_repo)
    
    command = CancelOrderCommand(
        order_id=order_uuid,
        user_id=current_user.id,
    )
    
    result = await handler.handle(command)
    
    if result.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.message
        )
    
    if result.status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    await db.commit()
    
    return {
        "order_id": str(result.order_id),
        "status": result.status,
        "message": result.message,
    }
