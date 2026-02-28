"""Integration Tests for Wallet API"""
import pytest
from decimal import Decimal
from uuid import uuid4
from unittest.mock import AsyncMock

from domain.wallet.aggregate import Wallet
from domain.wallet.value_objects import Currency


class TestGetBalanceHandler:
    """Test GetBalanceHandler"""

    @pytest.mark.asyncio
    async def test_get_balance_no_wallet(self):
        """Test getting balance when no wallet exists"""
        from application.wallet.commands import GetBalanceQuery, GetBalanceHandler

        mock_wallet_repo = AsyncMock()
        mock_wallet_repo.get_by_user_id = AsyncMock(return_value=None)

        handler = GetBalanceHandler(mock_wallet_repo)

        query = GetBalanceQuery(user_id=uuid4())

        result = await handler.handle(query)

        assert result.balance == 0.0
        assert result.currency == "USDT"

    @pytest.mark.asyncio
    async def test_get_balance_with_wallet(self):
        """Test getting balance with existing wallet"""
        from application.wallet.commands import GetBalanceQuery, GetBalanceHandler

        user_id = uuid4()
        wallet = Wallet(
            id=uuid4(),
            user_id=user_id,
            currency=Currency.USDT,
            balance=Decimal("1000.00"),
            locked_balance=Decimal("100.00"),
        )

        mock_wallet_repo = AsyncMock()
        mock_wallet_repo.get_by_user_id = AsyncMock(return_value=wallet)

        handler = GetBalanceHandler(mock_wallet_repo)

        query = GetBalanceQuery(user_id=user_id)

        result = await handler.handle(query)

        assert result.balance == 1000.0
        assert result.locked_balance == 100.0
        assert result.available_balance == 900.0


class TestDepositHandler:
    """Test DepositHandler"""

    @pytest.mark.asyncio
    async def test_deposit_creates_wallet(self):
        """Test deposit creates wallet if not exists"""
        from application.wallet.commands import DepositCommand, DepositHandler

        user_id = uuid4()

        mock_wallet_repo = AsyncMock()
        mock_wallet_repo.get_by_user_id = AsyncMock(return_value=None)
        mock_wallet_repo.save = AsyncMock()

        handler = DepositHandler(mock_wallet_repo)

        command = DepositCommand(
            user_id=user_id,
            amount=Decimal("1000.00"),
        )

        result = await handler.handle(command)

        assert result.balance == 1000.0
        assert result.transaction_id is not None
        assert "successful" in result.message.lower()

    @pytest.mark.asyncio
    async def test_deposit_existing_wallet(self):
        """Test deposit to existing wallet"""
        from application.wallet.commands import DepositCommand, DepositHandler

        user_id = uuid4()
        wallet = Wallet(
            id=uuid4(),
            user_id=user_id,
            currency=Currency.USDT,
            balance=Decimal("500.00"),
        )

        mock_wallet_repo = AsyncMock()
        mock_wallet_repo.get_by_user_id = AsyncMock(return_value=wallet)
        mock_wallet_repo.save = AsyncMock()

        handler = DepositHandler(mock_wallet_repo)

        command = DepositCommand(
            user_id=user_id,
            amount=Decimal("500.00"),
        )

        result = await handler.handle(command)

        assert result.balance == 1000.0

    @pytest.mark.asyncio
    async def test_deposit_invalid_amount(self):
        """Test deposit with invalid amount"""
        from application.wallet.commands import DepositCommand, DepositHandler

        user_id = uuid4()

        mock_wallet_repo = AsyncMock()
        mock_wallet_repo.get_by_user_id = AsyncMock(return_value=None)

        handler = DepositHandler(mock_wallet_repo)

        command = DepositCommand(
            user_id=user_id,
            amount=Decimal("-100.00"),  # Invalid
        )

        result = await handler.handle(command)

        assert "positive" in result.message.lower()


class TestWithdrawHandler:
    """Test WithdrawHandler"""

    @pytest.mark.asyncio
    async def test_withdraw_no_wallet(self):
        """Test withdraw when no wallet exists"""
        from application.wallet.commands import WithdrawCommand, WithdrawHandler

        user_id = uuid4()

        mock_wallet_repo = AsyncMock()
        mock_wallet_repo.get_by_user_id = AsyncMock(return_value=None)

        handler = WithdrawHandler(mock_wallet_repo)

        command = WithdrawCommand(
            user_id=user_id,
            amount=Decimal("100.00"),
        )

        result = await handler.handle(command)

        assert "not found" in result.message.lower()

    @pytest.mark.asyncio
    async def test_withdraw_insufficient_balance(self):
        """Test withdraw with insufficient balance"""
        from application.wallet.commands import WithdrawCommand, WithdrawHandler
        from domain.wallet.exceptions import InsufficientBalance

        user_id = uuid4()
        wallet = Wallet(
            id=uuid4(),
            user_id=user_id,
            currency=Currency.USDT,
            balance=Decimal("50.00"),
        )

        mock_wallet_repo = AsyncMock()
        mock_wallet_repo.get_by_user_id = AsyncMock(return_value=wallet)

        handler = WithdrawHandler(mock_wallet_repo)

        command = WithdrawCommand(
            user_id=user_id,
            amount=Decimal("100.00"),
        )

        # The handler catches the exception
        result = await handler.handle(command)

        assert "insufficient" in result.message.lower()


class TestListTransactionsHandler:
    """Test ListTransactionsHandler"""

    @pytest.mark.asyncio
    async def test_list_transactions_no_wallet(self):
        """Test listing transactions when no wallet"""
        from application.wallet.queries import ListTransactionsQuery, ListTransactionsHandler

        user_id = uuid4()

        mock_wallet_repo = AsyncMock()
        mock_wallet_repo.get_by_user_id = AsyncMock(return_value=None)

        mock_tx_repo = AsyncMock()

        handler = ListTransactionsHandler(mock_wallet_repo, mock_tx_repo)

        query = ListTransactionsQuery(user_id=user_id)

        result = await handler.handle(query)

        assert result.transactions == []
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_list_transactions_with_data(self):
        """Test listing transactions with data"""
        from application.wallet.queries import ListTransactionsQuery, ListTransactionsHandler
        from domain.wallet.aggregate import Transaction

        user_id = uuid4()
        wallet_id = uuid4()
        wallet = Wallet(
            id=wallet_id,
            user_id=user_id,
            currency=Currency.USDT,
            balance=Decimal("1000.00"),
        )

        transactions = [
            Transaction(
                id=uuid4(),
                wallet_id=wallet_id,
                type="deposit",
                amount=Decimal("1000.00"),
                balance_before=Decimal(0),
                balance_after=Decimal("1000.00"),
                status="completed",
            ),
            Transaction(
                id=uuid4(),
                wallet_id=wallet_id,
                type="withdrawal",
                amount=Decimal("100.00"),
                balance_before=Decimal("1000.00"),
                balance_after=Decimal("900.00"),
                status="completed",
            ),
        ]

        mock_wallet_repo = AsyncMock()
        mock_wallet_repo.get_by_user_id = AsyncMock(return_value=wallet)

        mock_tx_repo = AsyncMock()
        mock_tx_repo.find_by_wallet = AsyncMock(
            return_value=(transactions, 2)
        )

        handler = ListTransactionsHandler(mock_wallet_repo, mock_tx_repo)

        query = ListTransactionsQuery(user_id=user_id)

        result = await handler.handle(query)

        assert len(result.transactions) == 2
        assert result.total == 2
