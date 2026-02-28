from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.wallet import Wallet, Transaction
from app.schemas.user import (
    WalletBalanceResponse,
    BalanceResponse,
    DepositAddressResponse,
    WithdrawRequest,
    TransactionResponse,
)
from app.api.v1.auth import get_current_user


router = APIRouter(prefix="/wallet", tags=["Wallet"])


# Mock deposit addresses (in production, generate via blockchain)
MOCK_ADDRESSES = {
    "USDT": {
        "TRC20": "TXxxxxTRC20Address",
        "ERC20": "0x....ERC20Address",
    },
    "BTC": {
        "BTC": "bc1qxxxxBitcoinAddress",
    },
}


@router.get("/balance", response_model=WalletBalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )
    wallets = result.scalars().all()
    
    balances = []
    total_usdt = 0.0
    
    for wallet in wallets:
        total = float(wallet.balance) + float(wallet.locked)
        balances.append(BalanceResponse(
            currency=wallet.currency,
            available=float(wallet.balance),
            locked=float(wallet.locked),
            total=total,
        ))
        
        # Simple USDT conversion (in production, use real prices)
        if wallet.currency == "USDT":
            total_usdt += total
    
    return WalletBalanceResponse(
        balances=balances,
        total_usdt_value=total_usdt
    )


@router.get("/deposit/address", response_model=DepositAddressResponse)
async def get_deposit_address(
    currency: str = "USDT",
    network: str = "TRC20",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
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
    
    return DepositAddressResponse(
        currency=currency,
        address=MOCK_ADDRESSES[currency][network],
        network=network,
    )


@router.post("/withdraw", response_model=TransactionResponse)
async def withdraw(
    request: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get user wallet
    result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == current_user.id,
            Wallet.currency == request.currency
        )
    )
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        # Create wallet if not exists
        wallet = Wallet(
            user_id=current_user.id,
            currency=request.currency,
            balance=0,
            locked=0
        )
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
    
    # Check balance
    available = float(wallet.balance)
    if available < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # Deduct balance
    wallet.balance = available - request.amount
    
    # Create transaction record
    # Note: In production, this would trigger blockchain withdrawal
    tx_fee = request.amount * 0.001  # 0.1% fee
    
    transaction = Transaction(
        user_id=current_user.id,
        wallet_id=wallet.id,
        type="withdraw",
        amount=request.amount,
        fee=tx_fee,
        status="pending",
        address=request.address,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return transaction


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    transactions = result.scalars().all()
    return transactions
