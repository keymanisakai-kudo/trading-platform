"""Wallet API - DDD Style"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from decimal import Decimal
from typing import Optional

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories import (
    SQLAlchemyWalletRepository,
    SQLAlchemyTransactionRepository,
)
from app.application.wallet.commands import (
    GetBalanceQuery,
    GetBalanceHandler,
    DepositCommand,
    DepositHandler,
    WithdrawCommand,
    WithdrawHandler,
)
from app.application.wallet.queries import (
    ListTransactionsQuery,
    ListTransactionsHandler,
)

# Dependency imports
from app.api.v1.auth import get_current_user
from app.models.user import User


router = APIRouter(prefix="/wallet", tags=["Wallet"])


# Mock deposit addresses
MOCK_ADDRESSES = {
    "USDT": {"TRC20": "TXxxxxTRC20Address", "ERC20": "0x....ERC20Address"},
    "BTC": {"BTC": "bc1qxxxxBitcoinAddress"},
}


@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Get user's wallet balance"""
    wallet_repo = SQLAlchemyWalletRepository(db)
    handler = GetBalanceHandler(wallet_repo)
    
    query = GetBalanceQuery(user_id=current_user.id)
    result = await handler.handle(query)
    
    return {
        "balances": [{
            "currency": result.currency,
            "available": result.available_balance,
            "locked": result.locked_balance,
            "total": result.balance,
        }],
        "total_usdt_value": result.balance,
    }


@router.get("/deposit/address")
async def get_deposit_address(
    currency: str = Query("USDT", description="Currency"),
    network: str = Query("TRC20", description="Network"),
):
    """Get deposit address (mock)"""
    if currency not in MOCK_ADDRESSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currency {currency} not supported"
        )
    
    if network not in MOCK_ADDRESSES.get(currency, {}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Network {network} not supported for {currency}"
        )
    
    return {
        "currency": currency,
        "address": MOCK_ADDRESSES[currency][network],
        "network": network,
    }


@router.post("/deposit")
async def deposit(
    amount: float = Query(..., gt=0, description="Deposit amount"),
    currency: str = Query("USDT", description="Currency"),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Deposit funds (mock - in production, this would be callback from payment gateway)"""
    wallet_repo = SQLAlchemyWalletRepository(db)
    handler = DepositHandler(wallet_repo)
    
    command = DepositCommand(
        user_id=current_user.id,
        amount=Decimal(str(amount)),
    )
    
    result = await handler.handle(command)
    await db.commit()
    
    return {
        "transaction_id": str(result.transaction_id) if result.transaction_id else None,
        "balance": result.balance,
        "message": result.message,
    }


@router.post("/withdraw")
async def withdraw(
    amount: float = Query(..., gt=0, description="Withdrawal amount"),
    address: str = Query(..., description="Withdrawal address"),
    currency: str = Query("USDT", description="Currency"),
    network: str = Query("TRC20", description="Network"),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Withdraw funds"""
    wallet_repo = SQLAlchemyWalletRepository(db)
    handler = WithdrawHandler(wallet_repo)
    
    command = WithdrawCommand(
        user_id=current_user.id,
        amount=Decimal(str(amount)),
    )
    
    result = await handler.handle(command)
    
    if "not found" in result.message.lower() or "insufficient" in result.message.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    await db.commit()
    
    return {
        "transaction_id": str(result.transaction_id) if result.transaction_id else None,
        "balance": result.balance,
        "message": result.message,
    }


@router.get("/transactions")
async def get_transactions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Get transaction history"""
    wallet_repo = SQLAlchemyWalletRepository(db)
    tx_repo = SQLAlchemyTransactionRepository(db)
    
    handler = ListTransactionsHandler(wallet_repo, tx_repo)
    
    query = ListTransactionsQuery(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    
    result = await handler.handle(query)
    
    return {
        "transactions": result.transactions,
        "total": result.total,
    }
