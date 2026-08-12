from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from autotrade_lab.models import Fill, Instrument, Order


class Broker(ABC):
    @abstractmethod
    def instruments(self) -> Sequence[Instrument]: ...

    @abstractmethod
    def cash(self, currency: str) -> float: ...

    @abstractmethod
    def submit(self, order: Order) -> str: ...

    @abstractmethod
    def cancel(self, order_id: str) -> None: ...

    @abstractmethod
    def fills(self, order_id: str) -> Sequence[Fill]: ...
