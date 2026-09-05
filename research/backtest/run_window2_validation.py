"""
Cross-window validation: re-run both BaselineMarketMaker (best real-
depth spread) and MeanReversionStrategy against the second, independent
12h order-book capture, to check whether window 1's mean-reversion
result holds or was luck.
"""
from core.strategy.baseline_market_maker import BaselineMarketMaker
from core.strategy.mean_reversion import MeanReversionStrategy
from research.backtest.run_orderbook_replay_evaluation import run_replay_evaluation

WINDOW2_CANDLES = "adausdt_candles_1m_orderbook_matched_window2_12h"
WINDOW2_SNAPSHOTS = "adausdt_orderbook_snapshots_window2_12h"
WINDOW2_DELTAS = "adausdt_orderbook_deltas_window2_12h"

print("=== Baseline (window2, real depth) ===")
run_replay_evaluation(
    lambda symbol: BaselineMarketMaker(symbol=symbol, base_half_spread=0.0005),
    run_name="phase9_replay_baseline_window2", strategy_name="BaselineMarketMaker",
    candle_dataset=WINDOW2_CANDLES, snapshot_dataset=WINDOW2_SNAPSHOTS, deltas_dataset=WINDOW2_DELTAS,
)

print("\n=== Mean Reversion (window2, real depth) ===")
run_replay_evaluation(
    lambda symbol: MeanReversionStrategy(symbol=symbol, lookback=20, entry_zscore=1.5,
                                           exit_zscore=0.3, max_hold_candles=60),
    run_name="phase9_replay_mean_reversion_window2", strategy_name="MeanReversionStrategy",
    candle_dataset=WINDOW2_CANDLES, snapshot_dataset=WINDOW2_SNAPSHOTS, deltas_dataset=WINDOW2_DELTAS,
)