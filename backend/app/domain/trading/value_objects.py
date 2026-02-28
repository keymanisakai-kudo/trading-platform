"""Trading Domain Value Objects"""
from enum import Enum
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass(frozen=True)
class OrderId:
    value: str


@dataclass(frozen=True)
class Symbol:
    base: str  # BTC
    quote: str  # USDT

    def __str__(self) -> str:
        return f"{self.base}{self.quote}"

    @classmethod
    def from_string(cls, s: str) -> "Symbol":
        """Parse BTCUSDT -> Symbol('BTC', 'USDT')"""
        if s.endswith("USDT"):
            return cls(base=s[:-4], quote="USDT")
        # Handle other quote assets
        for quote in ["USDT", "BUSD", "BTC", "ETH"]:
            if s.endswith(quote) and len(s) > len(quote):
                return cls(base=s[:-len(quote)], quote=quote)
        raise ValueError(f"Invalid symbol: {s}")


@dataclass(frozen=True)
class Price:
    value: Decimal
    symbol: Symbol

    def __mul__(self, other: "Quantity") -> "Money":
        from domain.wallet.value_objects import Money
        return Money(self.value * other.value, self.symbol.quote)


@dataclass(frozen=True)
class Quantity:
    value: Decimal
    symbol: Symbol

    def __mul__(self, other: Price) -> "Money":
        from domain.wallet.value_objects import Money
        return Money(self.value * other.value, other.symbol.quote)
