"""Application Layer - Wallet Commands"""
from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from typing import Optional

from domain.wallet.repositories import IWalletRepository, ITransactionRepository
from domain.wallet.value_objects import Currency


@dataclass
class GetBalanceQuery:
    """查询余额"""
    user_id: UUID


@dataclass
class GetBalanceResult:
    """余额结果"""
    wallet_id: Optional[str]
    currency: str
    balance: float
    locked_balance: float
    available_balance: float


class GetBalanceHandler:
    def __init__(self, wallet_repository: IWalletRepository):
        self.wallet_repository = wallet_repository

    async def handle(self, query: GetBalanceQuery) -> GetBalanceResult:
        wallet = await self.wallet_repository.get_by_user_id(query.user_id)
        
        if not wallet:
            return GetBalanceResult(
                wallet_id=None,
                currency="USDT",
                balance=0.0,
                locked_balance=0.0,
                available_balance=0.0,
            )
        
        return GetBalanceResult(
            wallet_id=str(wallet.id),
            currency=wallet.currency.value,
            balance=float(wallet.balance),
            locked_balance=float(wallet.locked_balance),
            available_balance=float(wallet.available_balance),
        )


@dataclass
class DepositCommand:
    """充值命令"""
    user_id: UUID
    amount: Decimal
    reference_id: Optional[UUID] = None


@dataclass
class DepositResult:
    """充值结果"""
    transaction_id: Optional[UUID]
    balance: float
    message: str


class DepositHandler:
    def __init__(self, wallet_repository: IWalletRepository):
        self.wallet_repository = wallet_repository

    async def handle(self, command: DepositCommand) -> DepositResult:
        # Get or create wallet
        wallet = await self.wallet_repository.get_by_user_id(command.user_id)
        
        if not wallet:
            from domain.wallet.aggregate import Wallet
            wallet = Wallet.create(user_id=command.user_id, currency=Currency.USDT)
        
        # Deposit
        try:
            tx = wallet.deposit(command.amount, command.reference_id)
        except Exception as e:
            return DepositResult(
                transaction_id=None,
                balance=float(wallet.balance),
                message=str(e),
            )
        
        # Save
        await self.wallet_repository.save(wallet)
        
        return DepositResult(
            transaction_id=tx.id,
            balance=float(wallet.balance),
            message="Deposit successful",
        )


@dataclass
class WithdrawCommand:
    """提现命令"""
    user_id: UUID
    amount: Decimal
    reference_id: Optional[UUID] = None


@dataclass
class WithdrawResult:
    """提现结果"""
    transaction_id: Optional[UUID]
    balance: float
    message: str


class WithdrawHandler:
    def __init__(self, wallet_repository: IWalletRepository):
        self.wallet_repository = wallet_repository

    async def handle(self, command: WithdrawCommand) -> WithdrawResult:
        wallet = await self.wallet_repository.get_by_user_id(command.user_id)
        
        if not wallet:
            return WithdrawResult(
                transaction_id=None,
                balance=0.0,
                message="Wallet not found",
            )
        
        # Withdraw
        try:
            tx = wallet.withdraw(command.amount, command.reference_id)
        except Exception as e:
            return WithdrawResult(
                transaction_id=None,
                balance=float(wallet.balance),
                message=str(e),
            )
        
        # Save
        await self.wallet_repository.save(wallet)
        
        return WithdrawResult(
            transaction_id=tx.id,
            balance=float(wallet.balance),
            message="Withdrawal submitted",
        )
