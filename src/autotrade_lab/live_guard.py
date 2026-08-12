from __future__ import annotations

import os


class LiveTradingDisabled(RuntimeError):
    pass


def require_live_confirmation() -> None:
    """Require two deliberate environment settings before any real broker can send an order."""
    environment = os.getenv("AUTOTRADE_ENV", "paper").lower()
    confirmation = os.getenv("AUTOTRADE_LIVE_CONFIRMATION", "false").lower()
    if environment != "live" or confirmation != "i-understand-real-money-is-at-risk":
        raise LiveTradingDisabled("live trading is disabled; use paper mode")
