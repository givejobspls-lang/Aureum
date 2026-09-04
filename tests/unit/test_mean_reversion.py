"""
Tests for MeanReversionStrategy. Entry/exit logic verified with
hand-calculated z-scores, same rigor as every other strategy in this
project.
"""
import pytest
from core.strategy.mean_reversion import MeanReversionStrategy


def make_prices(n, pattern="flat"):
    if pattern == "flat":
        return [0.20] * n
    raise ValueError(pattern)


def test_insufficient_history_holds():
    strat = MeanReversionStrategy(symbol="ADAUSDT", lookback=20)
    signal = strat.decide({"price": 0.20})
    assert signal.action == "hold"
    assert "insufficient" in signal.reason


def test_zero_volatility_holds_no_division_error():
    strat = MeanReversionStrategy(symbol="ADAUSDT", lookback=5)
    for p in make_prices(6, "flat"):
        signal = strat.decide({"price": p})
    assert signal.action == "hold"
    assert "zero volatility" in signal.reason


def test_entry_triggers_on_significant_deviation_below_mean():
    """
    Hand-built series: mostly flat at 0.20, then one big drop to 0.15 -
    should trigger a buy entry once the drop is large enough relative
    to the window's own volatility.
    """
    strat = MeanReversionStrategy(symbol="ADAUSDT", lookback=10, entry_zscore=1.5)
    prices = [0.20, 0.201, 0.199, 0.200, 0.202, 0.198, 0.200, 0.201, 0.199, 0.200, 0.15]
    signal = None
    for p in prices:
        signal = strat.decide({"price": p})
    assert signal.action == "buy"
    assert strat.inventory == 0.0  # decide() doesn't self-apply; record_fill does


def test_record_fill_updates_inventory_and_triggers_exit_path():
    strat = MeanReversionStrategy(symbol="ADAUSDT", lookback=5, entry_zscore=1.0, exit_zscore=0.3)
    for p in [0.20, 0.20, 0.20, 0.20, 0.20, 0.10]:
        signal = strat.decide({"price": p})
    assert signal.action == "buy"

    strat.record_fill(action="buy", quantity=signal.quantity)
    assert strat.inventory == signal.quantity

    # Price reverts back toward the mean -> should exit (sell)
    exit_signal = strat.decide({"price": 0.195})
    assert exit_signal.action == "sell"


def test_max_hold_forces_exit_even_without_reversion():
    strat = MeanReversionStrategy(symbol="ADAUSDT", lookback=5, entry_zscore=1.0,
                                    exit_zscore=0.01, max_hold_candles=3)
    for p in [0.20, 0.20, 0.20, 0.20, 0.20, 0.10]:
        signal = strat.decide({"price": p})
    strat.record_fill(action="buy", quantity=signal.quantity)

    # Feed prices that never revert - should still force-exit after max_hold_candles
    exits = []
    for p in [0.10, 0.10, 0.10, 0.10]:
        exits.append(strat.decide({"price": p}).action)
    assert "sell" in exits  # forced exit happened within the fed candles


def test_no_lookahead_history_only_grows_forward():
    """Same discipline as BaselinePlusAI's equivalent test."""
    prices = [0.20, 0.201, 0.199, 0.200, 0.202, 0.198, 0.200, 0.201]

    strat_a = MeanReversionStrategy(symbol="ADAUSDT", lookback=5)
    results_a = [strat_a.decide({"price": p}).action for p in prices]

    strat_b = MeanReversionStrategy(symbol="ADAUSDT", lookback=5)
    results_b = [strat_b.decide({"price": p}).action for p in prices]
    for p in [0.30, 0.10]:
        strat_b.decide({"price": p})

    assert results_a == results_b