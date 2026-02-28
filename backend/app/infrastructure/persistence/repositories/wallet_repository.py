"""SQLAlchemy Wallet & Transaction Repository"""
from typing import Optional, List, Tuple
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.wallet.aggregate import Wallet, Transaction
from domain.wallet.value_objects import Currency
from domain.wallet.repositories import IWalletRepository, ITransactionRepository
from app.infrastructure.persistence.models import WalletModel, TransactionModel


class SQLAlchemyWalletRepository(IWalletRepository):
    """SQLAlchemy implementation of WalletRepository"""

    def __init__(self, db: AsyncSession):
        self._db = db

    def _to_domain(self, model: WalletModel) -> Wallet:
        wallet = Wallet(
            id=model.id,
            user_id=model.user_id,
            currency=Currency(model.currency),
            balance=model.balance,
            locked_balance=model.locked_balance,
            version=model.version,
        )
        return wallet

    def _to_model(self, wallet: Wallet) -> WalletModel:
        return WalletModel(
            id=wallet.id,
            user_id=wallet.user_id,
            currency=wallet.currency.value,
            balance=wallet.balance,
            locked_balance=wallet.locked_balance,
            version=wallet.version,
        )

    async def save(self, wallet: Wallet) -> Wallet:
        existing = await self._db.get(WalletModel, wallet.id)
        
        if existing:
            existing.balance = wallet.balance
            existing.locked_balance = wallet.locked_balance
            existing.version = wallet.version
        else:
            model = self._to_model(wallet)
            self._db.add(model)
        
        await self._db.flush()
        return wallet

    async def get_by_user_id(self, user_id: UUID) -> Optional[Wallet]:
        query = select(WalletModel).where(WalletModel.user_id == user_id)
        result = await self._db.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_id(self, wallet_id: UUID) -> Optional[Wallet]:
        model = await self._db.get(WalletModel, wallet_id)
        if not model:
            return None
        return self._to_domain(model)


class SQLAlchemyTransactionRepository(ITransactionRepository):
    """SQLAlchemy implementation of TransactionRepository"""

    def __init__(self, db: AsyncSession):
        self._db = db

    def _to_domain(self, model: TransactionModel) -> Transaction:
        return Transaction(
            id=model.id,
            wallet_id=model.wallet_id,
            type=model.type,
            amount=model.amount,
            fee=model.fee,
            balance_before=model.balance_before,
            balance_after=model.balance_after,
            reference_id=model.reference_id,
            status=model.status,
            created_at=model.created_at,
        )

    def _to_model(self, tx: Transaction) -> TransactionModel:
        return TransactionModel(
            id=tx.id,
            wallet_id=tx.wallet_id,
            type=tx.type,
            amount=tx.amount,
            fee=tx.fee,
            balance_before=tx.balance_before,
            balance_after=tx.balance_after,
            reference_id=tx.reference_id,
            status=tx.status,
            created_at=tx.created_at,
        )

    async def save(self, transaction: Transaction) -> Transaction:
        model = self._to_model(transaction)
        self._db.add(model)
        await self._db.flush()
        return transaction

    async def get_by_id(self, tx_id: UUID) -> Optional[Transaction]:
        model = await self._db.get(TransactionModel, tx_id)
        if not model:
            return None
        return self._to_domain(model)

    async def find_by_wallet(
        self,
        wallet_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Transaction], int]:
        # Count
        count_query = select(func.count(TransactionModel.id)).where(
            TransactionModel.wallet_id == wallet_id
        )
        total = await self._db.scalar(count_query)

        # Data
        query = select(TransactionModel).where(
            TransactionModel.wallet_id == wallet_id
        ).order_by(TransactionModel.created_at.desc()).limit(limit).offset(offset)

        result = await self._db.execute(query)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models], total

    async def find_by_reference(self, reference_id: UUID) -> List[Transaction]:
        query = select(TransactionModel).where(
            TransactionModel.reference_id == reference_id
        ).order_by(TransactionModel.created_at.desc())

        result = await self._db.execute(query)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]
