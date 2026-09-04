"""
Real order-book replay fill model — Phase 9 prep.

Unlike candle_fill_model.py's candle-close approximation, this replays
the ACTUAL captured order book state and matches orders against real
depth via paper_exchange.py's match_market_order/match_limit_order.

NO LOOK-AHEAD: for a decision made at candle close time T, only order
book deltas with event_time <= T are ever visible. This mirrors the
same discipline enforced everywhere else in this project (Phase 3's
feature audit, Phase 7's regime classifier, etc.) - a delta arriving
after T must never influence a fill decision made at T.

"""
import ast
from dataclasses import dataclass

from services.market_data.order_book import OrderBook
from core.backtest.paper_exchange import match_market_order, match_limit_order
from core.ai_reasoning.historical_retrieval import _normalize  # not used here, placeholder guard
from services.market_data.models import OrderBookDelta, OrderBookSnapshot, PriceLevel


class ReplayOrderBook:
    """
    Rebuilds order book state deterministically from a snapshot +
    ordered deltas, and exposes the state as of any requested
    timestamp - never a state that includes a delta AFTER that
    timestamp.
    """

    def __init__(self, snapshot_row: dict):
        self._bids: dict[float, float] = {
            lvl["price"]: lvl["quantity"] for lvl in ast.literal_eval(snapshot_row["bids"])
        }
        self._asks: dict[float, float] = {
            lvl["price"]: lvl["quantity"] for lvl in ast.literal_eval(snapshot_row["asks"])
        }
        self.last_update_id = snapshot_row["last_update_id"]
        self.last_event_time = snapshot_row["snapshot_time"]

    def apply(self, delta_row: dict) -> None:
        for lvl in ast.literal_eval(delta_row["bids"]):
            self._apply_level(self._bids, lvl)
        for lvl in ast.literal_eval(delta_row["asks"]):
            self._apply_level(self._asks, lvl)
        self.last_update_id = delta_row["final_update_id"]
        self.last_event_time = delta_row["event_time"]

    @staticmethod
    def _apply_level(side: dict, level: dict) -> None:
        if level["quantity"] == 0:
            side.pop(level["price"], None)
        else:
            side[level["price"]] = level["quantity"]

    def best_bid(self) -> float | None:
        return max(self._bids) if self._bids else None

    def best_ask(self) -> float | None:
        return min(self._asks) if self._asks else None

    def bids_sorted(self) -> list[PriceLevel]:
        """Highest price first - matches how a real book is walked for a sell order."""
        return [PriceLevel(price=p, quantity=q) for p, q in sorted(self._bids.items(), reverse=True)]

    def asks_sorted(self) -> list[PriceLevel]:
        """Lowest price first - matches how a real book is walked for a buy order."""
        return [PriceLevel(price=p, quantity=q) for p, q in sorted(self._asks.items())]


def build_replay_index(snapshot_df, deltas_df, symbol: str) -> list[tuple[int, OrderBook]]:
    book = ReplayOrderBook(snapshot_df.iloc[0].to_dict())
    checkpoints = [(book.last_event_time, _snapshot_state(book, symbol))]

    deltas_sorted = deltas_df.sort_values("final_update_id")
    for _, row in deltas_sorted.iterrows():
        book.apply(row.to_dict())
        checkpoints.append((book.last_event_time, _snapshot_state(book, symbol)))

    return checkpoints

def _snapshot_state(book: ReplayOrderBook, symbol: str) -> OrderBook:
    """
    Materializes the current replay state as a REAL OrderBook instance
    - match_limit_order() specifically requires this type (book.asks/
    book.bids as dicts, book.symbol), not a plain dict. Reuses the
    tested live OrderBook class rather than duplicating its shape.
    """
    ob = OrderBook(symbol=symbol)
    ob.bids = dict(book._bids)
    ob.asks = dict(book._asks)
    return ob

def get_book_state_at(checkpoints: list[tuple[int, dict]], target_time_ms: int) -> dict | None:
    """
    Returns the book state from the LATEST checkpoint at or before
    target_time_ms - the no-look-ahead guarantee. Returns None if
    target_time_ms is before the first checkpoint (order book didn't
    exist yet at that point).
    """
    result = None
    for event_time, state in checkpoints:
        if event_time > target_time_ms:
            break
        result = state
    return result