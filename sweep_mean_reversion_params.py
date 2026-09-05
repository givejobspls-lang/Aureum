"""Sweep entry/exit thresholds across BOTH windows - a parameter that
only works on one window is overfit, same discipline as Phase 5."""
from core.strategy.mean_reversion import MeanReversionStrategy
from research.backtest.run_orderbook_replay_evaluation import run_replay_evaluation

WINDOWS = {
    "window1_8h": dict(
        candle_dataset="adausdt_candles_1m_orderbook_matched_8h",
        snapshot_dataset="adausdt_orderbook_snapshots_8h",
        deltas_dataset="adausdt_orderbook_deltas_8h",
    ),
    "window2_12h": dict(
        candle_dataset="adausdt_candles_1m_orderbook_matched_window2_12h",
        snapshot_dataset="adausdt_orderbook_snapshots_window2_12h",
        deltas_dataset="adausdt_orderbook_deltas_window2_12h",
    ),
}

for entry_z in (1.5, 2.0, 2.5, 3.0):
    for window_name, datasets in WINDOWS.items():
        print(f"\n--- entry_zscore={entry_z}, {window_name} ---")
        run_replay_evaluation(
            lambda symbol, e=entry_z: MeanReversionStrategy(
                symbol=symbol, lookback=20, entry_zscore=e, exit_zscore=0.3, max_hold_candles=60
            ),
            run_name=f"phase9_mr_sweep_{entry_z}_{window_name}",
            strategy_name="MeanReversionStrategy",
            **datasets,
        )