from __future__ import annotations

from dataclasses import dataclass

from .models import Order


class RiskRejected(RuntimeError):
    pass


@dataclass(slots=True)
class RiskLimits:
    max_order_notional: float = 100_000
    max_gross_exposure: float = 500_000
    max_daily_loss: float = 20_000


class RiskEngine:
    def __init__(self, limits: RiskLimits):
        self.limits = limits

    def validate(
        self, order: Order, reference_price: float, gross_exposure: float, daily_pnl: float
    ) -> None:
        notional = abs(order.quantity * reference_price)
        if notional > self.limits.max_order_notional:
            raise RiskRejected("order notional exceeds limit")
        if gross_exposure + notional > self.limits.max_gross_exposure:
            raise RiskRejected("gross exposure exceeds limit")
        if daily_pnl <= -self.limits.max_daily_loss:
            raise RiskRejected("daily loss kill switch is active")
