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

\## Update: Window 2 Validation (12h, independent capture)



| | Window 1 (8h) | Window 2 (12h) |

|---|---|---|

| Return | +0.27% | -0.87% |

| Win rate | 45.5% | 40.9% |



\*\*Result did not replicate.\*\* Window 1's positive result does not hold

in an independent second window - mean reversion lost money in window

2, worse than the baseline lost in the same window.



\## Revised, honest conclusion



Neither BaselineMarketMaker nor MeanReversionStrategy has demonstrated

reliable profitability against real ADA order-book depth across two

independent windows. This is exactly the outcome the two-window check

exists to catch - a single-window "promising" result that doesn't

replicate is a false positive, not a real finding.

