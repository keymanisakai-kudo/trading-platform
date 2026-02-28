"""Binance Market Adapter"""
from decimal import Decimal
from typing import List, Dict, Any, Optional
import httpx


class BinanceMarketAdapter:
    """Binance Market Data Adapter - 轻量适配器模式"""

    BASE_URL = "https://api.binance.com"

    def __init__(self, http_client: Optional[httpx.AsyncClient] = None):
        self._client = http_client

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()

    async def get_symbol_price(self, symbol: str) -> Decimal:
        """Get current price for symbol"""
        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/ticker/price",
            params={"symbol": symbol.upper()},
        )
        response.raise_for_status()
        data = response.json()
        return Decimal(data["price"])

    async def get_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get K-line/candlestick data"""
        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/klines",
            params={
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit,
            },
        )
        response.raise_for_status()
        return response.json()

    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """Get order book depth"""
        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/depth",
            params={"symbol": symbol.upper(), "limit": limit},
        )
        response.raise_for_status()
        return response.json()

    async def get_24h_ticker(self, symbol: str) -> Dict:
        """Get 24h price change stats"""
        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/ticker/24hr",
            params={"symbol": symbol.upper()},
        )
        response.raise_for_status()
        return response.json()

    async def get_all_prices(self) -> Dict[str, Decimal]:
        """Get all symbol prices"""
        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/ticker/price",
        )
        response.raise_for_status()
        data = response.json()
        return {item["symbol"]: Decimal(item["price"]) for item in data}

    async def get_ticker_price(self, symbol: str) -> Dict:
        """Get price with quote volume"""
        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/ticker/24hr",
            params={"symbol": symbol.upper()},
        )
        response.raise_for_status()
        return response.json()
