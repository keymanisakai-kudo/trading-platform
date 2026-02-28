"""Binance Trading Adapter"""
from decimal import Decimal
from typing import Dict, Optional
import httpx
import hashlib
import time


class BinanceTradingAdapter:
    """Binance Trading Adapter - 需要 API Key"""

    BASE_URL = "https://api.binance.com"

    def __init__(
        self,
        api_key: str,
        secret_key: str,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.api_key = api_key
        self.secret_key = secret_key
        self._client = http_client

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    def _sign(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hashlib.hmac.new(
            self.secret_key.encode(),
            query_string.encode(),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Optional[Decimal] = None,
    ) -> Dict:
        """Place an order on Binance"""
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": str(quantity),
            "timestamp": self._timestamp(),
        }

        if price:
            params["price"] = str(price)
            params["timeInForce"] = "GTC"

        params["signature"] = self._sign(params)

        response = await self.client.post(
            f"{self.BASE_URL}/api/v3/order",
            params=params,
            headers={"X-MBX-APIKEY": self.api_key},
        )
        response.raise_for_status()
        return response.json()

    async def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an order"""
        params = {
            "symbol": symbol.upper(),
            "orderId": order_id,
            "timestamp": self._timestamp(),
        }
        params["signature"] = self._sign(params)

        response = await self.client.delete(
            f"{self.BASE_URL}/api/v3/order",
            params=params,
            headers={"X-MBX-APIKEY": self.api_key},
        )
        response.raise_for_status()
        return response.json()

    async def get_order(self, symbol: str, order_id: int) -> Dict:
        """Get order status"""
        params = {
            "symbol": symbol.upper(),
            "orderId": order_id,
            "timestamp": self._timestamp(),
        }
        params["signature"] = self._sign(params)

        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/order",
            params=params,
            headers={"X-MBX-APIKEY": self.api_key},
        )
        response.raise_for_status()
        return response.json()

    async def get_open_orders(self, symbol: Optional[str] = None) -> Dict:
        """Get all open orders"""
        params = {"timestamp": self._timestamp()}
        if symbol:
            params["symbol"] = symbol.upper()
        params["signature"] = self._sign(params)

        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/openOrders",
            params=params,
            headers={"X-MBX-APIKEY": self.api_key},
        )
        response.raise_for_status()
        return response.json()

    async def get_account(self) -> Dict:
        """Get account information"""
        params = {"timestamp": self._timestamp()}
        params["signature"] = self._sign(params)

        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/account",
            params=params,
            headers={"X-MBX-APIKEY": self.api_key},
        )
        response.raise_for_status()
        return response.json()
