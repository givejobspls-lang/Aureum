"""
Real order-book replay evaluation - Phase 9 prep. Runs Baseline and
Baseline+AI against REAL captured ADA order-book depth instead of the
candle-close approximation, using the exact matched 8h window.
"""
from datetime import datetime, timezone

from core.ai_reasoning.regime_classifier import classify_regime, Regime
from core.backtest.orderbook_replay_fill_model import build_replay_index, get_book_state_at
from core.backtest.paper_exchange import match_limit_order
from core.portfolio.portfolio import Portfolio, Fill as PortfolioFill
from core.strategy.baseline_market_maker import BaselineMarketMaker
from core.strategy.baseline_plus_ai import BaselinePlusAI
from research.storage import load_dataset, save_dataset
from services.market_data.models import Candle

CANDLE_DATASET = "adausdt_candles_1m_orderbook_matched_8h"
SNAPSHOT_DATASET = "adausdt_orderbook_snapshots_8h"
DELTAS_DATASET = "adausdt_orderbook_deltas_8h"
STARTING_CASH = 10_000.0
MAKER_FEE_RATE = 0.001


def run_replay_evaluation(strategy_factory, run_name: str, strategy_name: str) -> dict:
    candles_df = load_dataset("raw", CANDLE_DATASET)
    candles = [Candle(**row) for row in candles_df.to_dict(orient="records")]
    candles.sort(key=lambda c: c.close_time)
    print(f"Loaded {len(candles)} candles from {CANDLE_DATASET!r}")

    symbol = candles[0].symbol

    snapshot_df = load_dataset("raw", SNAPSHOT_DATASET)
    deltas_df = load_dataset("raw", DELTAS_DATASET)
    checkpoints = build_replay_index(snapshot_df, deltas_df, symbol=symbol)
    print(f"Built {len(checkpoints)} order-book replay checkpoints")
    strategy = strategy_factory(symbol)
    portfolio = Portfolio(starting_cash=STARTING_CASH)
    last_price = None
    fills_attempted = 0
    fills_no_book_state = 0

    for candle in candles:
        market_data = {
            "symbol": candle.symbol, "timestamp": candle.close_time,
            "event_type": candle.event_type, "price": candle.close,
            "open": candle.open, "high": candle.high, "low": candle.low,
            "volume": candle.volume,
        }
        last_price = candle.close

        result = strategy.decide(market_data)
        signals = result if isinstance(result, list) else [result]
        occurred_at = datetime.fromtimestamp(candle.close_time / 1000, tz=timezone.utc)

        # No-look-ahead: only the order-book state as of THIS candle's
        # close_time is visible - never a later delta.
        book_state = get_book_state_at(checkpoints, candle.close_time)
        if book_state is None:
            continue  # no order book existed yet at this point in history

        for signal in signals:
            if signal.action == "hold" or signal.price is None or signal.quantity is None:
                continue
            fills_attempted += 1

            fill_result = match_limit_order(
                book_state, side=signal.action,
                quantity=signal.quantity, limit_price=signal.price,
            )
            if fill_result is None:
                continue

            fill_price, fill_quantity = fill_result
            fee = fill_price * fill_quantity * MAKER_FEE_RATE
            portfolio.process_fill(PortfolioFill(
                symbol=signal.symbol, side=signal.action, quantity=fill_quantity,
                price=fill_price, fee=fee, timestamp=occurred_at,
            ))
            strategy.record_fill(action=signal.action, quantity=fill_quantity)

        portfolio.record_equity_snapshot(occurred_at, {symbol: candle.close})

    print(f"Processed {len(candles)} candles, {len(portfolio.trade_log)} fills "
          f"({fills_attempted} attempted)")

    current_prices = {symbol: last_price} if last_price is not None else None
    summary = portfolio.summary(current_prices)
    print(f"Summary: {summary}")

    from research.backtest.results import save_backtest_run
    versions = save_backtest_run(
        portfolio, run_name, current_prices=current_prices,
        strategy_name=strategy_name,
        extra_metadata={"phase": 9, "fill_model": "real_orderbook_replay", "window": "matched_8h"},
    )
    print(f"Saved run as {run_name!r}, versions: {versions}")
    return versions


def main():
    print("=== Baseline (real order-book fills) ===")
    run_replay_evaluation(
        lambda symbol: BaselineMarketMaker(symbol=symbol, base_half_spread=0.001),
        run_name="phase9_replay_baseline_8h", strategy_name="BaselineMarketMaker",
    )
    print("\n=== Baseline+AI (real order-book fills) ===")
    run_replay_evaluation(
        lambda symbol: BaselinePlusAI(symbol=symbol, base_half_spread=0.001),
        run_name="phase9_replay_ai_8h", strategy_name="BaselinePlusAI",
    )


if __name__ == "__main__":
    main()