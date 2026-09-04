"""
Mean reversion strategy — designed specifically to work at the
1-minute decision cadence this system actually has, unlike market
making which needs sub-second requoting to compete (confirmed by
Phase 9's real order-book validation: every fill happened exactly 60s
after quoting, indicating adverse selection from stale quotes, not
genuine spread capture).

Holds positions for many candles rather than seconds, so a once-a-
minute decision isn't a structural handicap - it's simply how this
strategy is meant to operate. Uses the existing rolling_volatility and
simple_returns features already built (Phase 3).
"""
from core.features.feature_engine import rolling_volatility, simple_returns
from core.strategy.base import Signal


class MeanReversionStrategy:
    def __init__(
        self,
        symbol: str,
        lookback: int = 20,
        entry_zscore: float = 1.5,
        exit_zscore: float = 0.3,
        order_quantity: float = 100.0,
        max_hold_candles: int = 60,
    ):
        self.symbol = symbol
        self.lookback = lookback
        self.entry_zscore = entry_zscore
        self.exit_zscore = exit_zscore
        self.order_quantity = order_quantity
        self.max_hold_candles = max_hold_candles

        self.inventory = 0.0
        self._price_history: list[float] = []
        self._candles_since_entry = 0

    def record_fill(self, action: str, quantity: float) -> None:
        if action == "buy":
            self.inventory += quantity
        elif action == "sell":
            self.inventory -= quantity

    def decide(self, market_data: dict) -> Signal:
        price = market_data.get("price")
        if price is None:
            return Signal(action="hold", symbol=self.symbol, reason="no price")
        self._price_history.append(price)

        if len(self._price_history) < self.lookback + 1:
            return Signal(action="hold", symbol=self.symbol, reason="insufficient history")

        window = self._price_history[-self.lookback:]
        mean = sum(window) / len(window)
        returns = simple_returns(window)
        vol_series = rolling_volatility(returns, window=len(returns)) if returns else []
        std = vol_series[-1] if vol_series else 0.0

        if std == 0:
            return Signal(action="hold", symbol=self.symbol, reason="zero volatility, no signal")

        zscore = (price - mean) / (std * mean)  # normalize std (a return) into price terms

        # Flat -> look for an entry
        if self.inventory == 0:
            if zscore <= -self.entry_zscore:
                self._candles_since_entry = 0
                return Signal(action="buy", symbol=self.symbol, quantity=self.order_quantity,
                              price=price, reason=f"mean reversion entry: zscore={zscore:.2f}")
            if zscore >= self.entry_zscore:
                self._candles_since_entry = 0
                return Signal(action="sell", symbol=self.symbol, quantity=self.order_quantity,
                              price=price, reason=f"mean reversion entry: zscore={zscore:.2f}")
            return Signal(action="hold", symbol=self.symbol, reason=f"zscore={zscore:.2f}, no entry")

        # In a position -> look for an exit
        self._candles_since_entry += 1
        reverted = abs(zscore) <= self.exit_zscore
        timed_out = self._candles_since_entry >= self.max_hold_candles

        if reverted or timed_out:
            exit_action = "sell" if self.inventory > 0 else "buy"
            reason = "reverted to mean" if reverted else "max hold reached"
            return Signal(action=exit_action, symbol=self.symbol, quantity=abs(self.inventory),
                          price=price, reason=reason)

        return Signal(action="hold", symbol=self.symbol, reason="holding position")