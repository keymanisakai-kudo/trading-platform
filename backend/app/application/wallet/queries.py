"""Application Layer - Wallet Queries"""
from dataclasses import dataclass
from uuid import UUID
from typing import List

from domain.wallet.repositories import IWalletRepository, ITransactionRepository


@dataclass
class ListTransactionsQuery:
    """查询交易流水"""
    user_id: UUID
    limit: int = 50
    offset: int = 0


@dataclass
class ListTransactionsResult:
    """流水结果"""
    transactions: List[dict]
    total: int
    message: str


class ListTransactionsHandler:
    def __init__(
        self,
        wallet_repository: IWalletRepository,
        transaction_repository: ITransactionRepository,
    ):
        self.wallet_repository = wallet_repository
        self.transaction_repository = transaction_repository

    async def handle(self, query: ListTransactionsQuery) -> ListTransactionsResult:
        # Get wallet
        wallet = await self.wallet_repository.get_by_user_id(query.user_id)
        
        if not wallet:
            return ListTransactionsResult(
                transactions=[],
                total=0,
                message="Wallet not found",
            )
        
        # Get transactions
        txs, total = await self.transaction_repository.find_by_wallet(
            wallet_id=wallet.id,
            limit=query.limit,
            offset=query.offset,
        )
        
        # Convert to dict
        tx_dicts = []
        for tx in txs:
            tx_dicts.append({
                "id": str(tx.id),
                "type": tx.type,
                "amount": float(tx.amount),
                "fee": float(tx.fee),
                "balance_before": float(tx.balance_before),
                "balance_after": float(tx.balance_after),
                "status": tx.status,
                "created_at": tx.created_at.isoformat(),
            })
        
        return ListTransactionsResult(
            transactions=tx_dicts,
            total=total,
            message="Success",
        )
