"""Toss Securities Open API adapter boundary (account access dependent)."""

from __future__ import annotations

from collections.abc import Sequence

from autotrade_lab.live_guard import require_live_confirmation
from autotrade_lab.models import Fill, Instrument, Order

from .base import Broker


class TossBroker(Broker):
    def __init__(self, transport, *, paper: bool = True):
        self.transport = transport
        self.paper = paper

    def instruments(self) -> Sequence[Instrument]:
        return self.transport.instruments()

    def cash(self, currency: str) -> float:
        return self.transport.cash(currency)

    def submit(self, order: Order) -> str:
        if not self.paper:
            require_live_confirmation()
        return self.transport.submit(order, paper=self.paper)

    def cancel(self, order_id: str) -> None:
        self.transport.cancel(order_id, paper=self.paper)

    def fills(self, order_id: str) -> Sequence[Fill]:
        return self.transport.fills(order_id, paper=self.paper)
