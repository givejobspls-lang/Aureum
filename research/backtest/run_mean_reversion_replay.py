"""
Runs MeanReversionStrategy against the same real ADA order-book replay
data used to validate the market maker - genuine depth-based fills,
not the candle-close approximation.
"""
from core.strategy.mean_reversion import MeanReversionStrategy
from research.backtest.run_orderbook_replay_evaluation import run_replay_evaluation


def main():
    print("=== Mean Reversion (real order-book fills) ===")
    run_replay_evaluation(
        lambda symbol: MeanReversionStrategy(symbol=symbol, lookback=20, entry_zscore=1.5,
                                               exit_zscore=0.3, max_hold_candles=60),
        run_name="phase9_replay_mean_reversion_8h",
        strategy_name="MeanReversionStrategy",
    )


if __name__ == "__main__":
    main()