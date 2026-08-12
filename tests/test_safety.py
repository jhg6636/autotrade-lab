from unittest.mock import Mock

import pytest

from autotrade_lab.brokers.kis import KisBroker
from autotrade_lab.live_guard import LiveTradingDisabled
from autotrade_lab.models import AssetClass, Instrument, Order, Side
from autotrade_lab.risk import RiskEngine, RiskLimits, RiskRejected

ORDER = Order(Instrument("005930", AssetClass.KR_EQUITY, "KRX", "KRW"), Side.BUY, 10)


def test_live_broker_fails_closed(monkeypatch):
    monkeypatch.delenv("AUTOTRADE_ENV", raising=False)
    with pytest.raises(LiveTradingDisabled):
        KisBroker(Mock(), paper=False).submit(ORDER)


def test_risk_engine_blocks_large_order():
    with pytest.raises(RiskRejected):
        RiskEngine(RiskLimits(max_order_notional=100)).validate(ORDER, 70_000, 0, 0)
