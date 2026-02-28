"""Wallet Domain - Repository Interfaces"""
from typing import Protocol, Optional, List
from uuid import UUID

from domain.wallet.aggregate import Wallet, Transaction


class IWalletRepository(Protocol):
    """Wallet Repository Interface"""

    async def save(self, wallet: Wallet) -> Wallet:
        """Save or update wallet"""
        ...

    async def get_by_user_id(self, user_id: UUID) -> Optional[Wallet]:
        """Get wallet by user ID"""
        ...

    async def get_by_id(self, wallet_id: UUID) -> Optional[Wallet]:
        """Get wallet by ID"""
        ...


class ITransactionRepository(Protocol):
    """Transaction Repository Interface"""

    async def save(self, transaction: Transaction) -> Transaction:
        """Save or update transaction"""
        ...

    async def get_by_id(self, tx_id: UUID) -> Optional[Transaction]:
        """Get transaction by ID"""
        ...

    async def find_by_wallet(
        self,
        wallet_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Transaction], int]:
        """Find transactions by wallet"""
        ...

    async def find_by_reference(
        self,
        reference_id: UUID,
    ) -> List[Transaction]:
        """Find transactions by reference (e.g., order_id)"""
        ...
