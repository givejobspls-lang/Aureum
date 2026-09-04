"""
Capture real order-book data for ADA over a sustained window and
persist snapshots + deltas via the existing versioned research storage,
so paper_exchange.py can eventually use real depth instead of the
candle-close approximation.

bids/asks are serialized to strings before saving - save_dataset()'s
checksum step can't hash a column containing nested Python lists
(PriceLevel objects), which nothing had ever tried to save through
this path before - candle/trade data is all flat scalars.
"""
import asyncio
from datetime import datetime, timezone

import pandas as pd

from core.logging_config import configure_logging
from services.market_data.adapters.binance import BinanceAdapter
from services.market_data.models import OrderBookSnapshot, OrderBookDelta
from research.storage import save_dataset

CAPTURE_SECONDS = 3600  # 1 hour


async def main():
    configure_logging()
    adapter = BinanceAdapter(config={})
    snapshots = []
    deltas = []

    async def run_capture():
        async for event in adapter.stream_market_data(["ADAUSDT"]):
            if isinstance(event, OrderBookSnapshot):
                snapshots.append(event.model_dump())
                print(f"SNAPSHOT #{len(snapshots)} last_update_id={event.last_update_id}")
            elif isinstance(event, OrderBookDelta):
                deltas.append(event.model_dump())
                if len(deltas) % 50 == 0:
                    print(f"delta #{len(deltas)}")

    try:
        await asyncio.wait_for(run_capture(), timeout=CAPTURE_SECONDS)
    except asyncio.TimeoutError:
        pass

    print(f"\nCapture complete: {len(snapshots)} snapshots, {len(deltas)} deltas")

    if snapshots:
        df = pd.DataFrame(snapshots)
        df["bids"] = df["bids"].apply(lambda x: str(x))
        df["asks"] = df["asks"].apply(lambda x: str(x))
        save_dataset(
            "adausdt_orderbook_snapshots_1h",
            df,
            category="raw",
            source="samarth/capture_ada_orderbook",
            metadata={"captured_at": datetime.now(timezone.utc).isoformat(), "count": len(snapshots)},
        )

    if deltas:
        df = pd.DataFrame(deltas)
        df["bids"] = df["bids"].apply(lambda x: str(x))
        df["asks"] = df["asks"].apply(lambda x: str(x))
        save_dataset(
            "adausdt_orderbook_deltas_1h",
            df,
            category="raw",
            source="samarth/capture_ada_orderbook",
            metadata={"captured_at": datetime.now(timezone.utc).isoformat(), "count": len(deltas)},
        )

    print("Saved.")


asyncio.run(main())