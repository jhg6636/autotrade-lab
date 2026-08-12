from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AssetClass(str, Enum):
    KR_EQUITY = "kr_equity"
    KR_ETF = "kr_etf"
    CRYPTO_SPOT = "crypto_spot"
    CRYPTO_PERP = "crypto_perp"


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


@dataclass(frozen=True, slots=True)
class Instrument:
    symbol: str
    asset_class: AssetClass
    venue: str
    currency: str


@dataclass(frozen=True, slots=True)
class Order:
    instrument: Instrument
    side: Side
    quantity: float
    order_type: OrderType = OrderType.MARKET
    limit_price: float | None = None
    reduce_only: bool = False
    client_order_id: str | None = None


@dataclass(frozen=True, slots=True)
class Fill:
    order_id: str
    timestamp: datetime
    price: float
    quantity: float
    fee: float
