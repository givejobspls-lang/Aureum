\# Phase 9 — Mean Reversion: First Real-Depth Result



\*\*Data:\*\* Same 8h real ADA order-book replay (4,750 deltas, zero gaps) used for market-maker validation.



\## Result

\- 23 fills, 45.45% win rate, +0.27% return (vs market maker's best real-depth result: -0.19% at 20% win rate)

\- Positive on both realized and unrealized PnL



\## Honest caveat

Single 8-hour window. This is a genuinely promising first signal, not

a validated conclusion - the same statistical caution from Phase 8

applies here. Do not report this as "mean reversion is profitable"

without testing across multiple independent windows, same discipline

that caught the original spread-tuning issue in Phase 5.



\## Why this direction makes sense structurally

Confirmed via the market-maker's real-depth failure: fills happened

exactly 60s after quoting (adverse selection from a stale, once-per-

minute quote). Mean reversion holds positions for many candles, so

the same 60s decision cadence isn't a structural handicap here - it's

the intended operating speed.

