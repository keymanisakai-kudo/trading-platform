"""Tests for Wallet Aggregate"""
import pytest
from decimal import Decimal
from uuid import uuid4

from domain.wallet.aggregate import Wallet, Transaction
from domain.wallet.value_objects import Currency
from domain.wallet.exceptions import InsufficientBalance, InvalidAmount


class TestWalletCreate:
    """Test Wallet creation"""

    def test_create_wallet(self, user_id):
        """Test creating a wallet"""
        wallet = Wallet.create(user_id=user_id, currency=Currency.USDT)

        assert wallet.user_id == user_id
        assert wallet.currency == Currency.USDT
        assert wallet.balance == Decimal(0)
        assert wallet.locked_balance == Decimal(0)

    def test_available_balance(self, sample_wallet):
        """Test available balance calculation"""
        assert sample_wallet.available_balance == Decimal(0)

        # Add some balance
        sample_wallet.deposit(Decimal("1000"))
        
        assert sample_wallet.balance == Decimal("1000")
        assert sample_wallet.available_balance == Decimal("1000")


class TestWalletDeposit:
    """Test deposit"""

    def test_deposit_success(self, sample_wallet):
        """Test successful deposit"""
        tx = sample_wallet.deposit(Decimal("1000"))

        assert sample_wallet.balance == Decimal("1000")
        assert tx.type == "deposit"
        assert tx.amount == Decimal("1000")
        assert tx.status == "completed"

    def test_deposit_zero_fails(self, sample_wallet):
        """Test that deposit zero fails"""
        with pytest.raises(InvalidAmount, match="must be positive"):
            sample_wallet.deposit(Decimal(0))

    def test_deposit_negative_fails(self, sample_wallet):
        """Test that deposit negative fails"""
        with pytest.raises(InvalidAmount, match="must be positive"):
            sample_wallet.deposit(Decimal("-100"))


class TestWalletWithdraw:
    """Test withdrawal"""

    def test_withdraw_success(self, sample_wallet):
        """Test successful withdrawal"""
        sample_wallet.deposit(Decimal("1000"))
        tx = sample_wallet.withdraw(Decimal("500"))

        assert sample_wallet.balance == Decimal("500")
        assert tx.type == "withdrawal"
        assert tx.amount == Decimal("500")

    def test_withdraw_insufficient_balance(self, sample_wallet):
        """Test withdrawal with insufficient balance"""
        sample_wallet.deposit(Decimal("100"))

        with pytest.raises(InsufficientBalance):
            sample_wallet.withdraw(Decimal("200"))

    def test_withdraw_more_than_available(self, sample_wallet):
        """Test withdrawal more than available (locked balance)"""
        sample_wallet.deposit(Decimal("1000"))
        sample_wallet.lock_for_order(Decimal("500"), uuid4())

        # Available is 500, trying to withdraw 600
        with pytest.raises(InsufficientBalance):
            sample_wallet.withdraw(Decimal("600"))


class TestWalletLock:
    """Test balance locking"""

    def test_lock_for_order(self, sample_wallet):
        """Test locking balance for order"""
        sample_wallet.deposit(Decimal("1000"))
        order_id = uuid4()
        
        sample_wallet.lock_for_order(Decimal("500"), order_id)

        assert sample_wallet.locked_balance == Decimal("500")
        assert sample_wallet.available_balance == Decimal("500")

    def test_lock_more_than_available_fails(self, sample_wallet):
        """Test locking more than available fails"""
        sample_wallet.deposit(Decimal("100"))

        with pytest.raises(InsufficientBalance):
            sample_wallet.lock_for_order(Decimal("200"), uuid4())

    def test_unlock(self, sample_wallet):
        """Test unlocking balance"""
        sample_wallet.deposit(Decimal("1000"))
        order_id = uuid4()
        
        sample_wallet.lock_for_order(Decimal("500"), order_id)
        sample_wallet.unlock(Decimal("300"), order_id)

        assert sample_wallet.locked_balance == Decimal("200")
        assert sample_wallet.available_balance == Decimal("800")


class TestWalletDeduct:
    """Test trade deduction"""

    def test_deduct_balance(self, sample_wallet):
        """Test deducting balance for trade"""
        sample_wallet.deposit(Decimal("1000"))
        order_id = uuid4()
        
        tx = sample_wallet.deduct(Decimal("500"), order_id)

        assert sample_wallet.balance == Decimal("500")
        assert tx.type == "trade_deduct"

    def test_deduct_insufficient_balance(self, sample_wallet):
        """Test deducting more than balance fails"""
        sample_wallet.deposit(Decimal("100"))

        with pytest.raises(InsufficientBalance):
            sample_wallet.deduct(Decimal("200"), uuid4())

    def test_add_proceeds(self, sample_wallet):
        """Test adding trade proceeds"""
        order_id = uuid4()
        
        tx = sample_wallet.add_proceeds(Decimal("500"), order_id)

        assert sample_wallet.balance == Decimal("500")
        assert tx.type == "trade_proceeds"


class TestDomainEvents:
    """Test Domain Events"""

    def test_deposit_emits_events(self, sample_wallet):
        """Test deposit emits events"""
        sample_wallet.deposit(Decimal("1000"))

        events = sample_wallet.pull_events()
        event_types = [e.__class__.__name__ for e in events]
        
        assert "DepositEvent" in event_types
        assert "BalanceChangedEvent" in event_types
