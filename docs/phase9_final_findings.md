\# Phase 9 — Final Real-Depth Findings



\## Method

Two independent real ADA order-book captures (8h/4750 deltas, 12h/4269

deltas, both zero sequence gaps), replayed with genuine depth-based

matching (paper\_exchange.py), not the candle-close approximation used

in Phases 5-8.



\## Market Making (BaselineMarketMaker)

Every tested spread (0.001 down to 0.00005) either produces zero fills

or loses money, worsening as spread tightens. Root cause identified:

fills consistently occur exactly 60 seconds after quoting - adverse

selection from a stale, once-per-minute quote against a continuously

moving real market. This is a structural/infrastructure limitation

(decision cadence, execution latency), not a parameter problem.



\## Mean Reversion

Full sweep, entry\_zscore in {1.5, 2.0, 2.5, 3.0}, both windows:



| entry\_zscore | Window 1 (8h) | Window 2 (12h) |

|---|---|---|

| 1.5 | +0.27% | -0.87% |

| 2.0 | -0.29% | -0.96% |

| 2.5 | -0.08% | -0.68% |

| 3.0 | -0.87% | -0.48% |



No parameter value is profitable across both windows. Diagnosed

directly: unlike market making, this is not a stale-quote/adverse-

selection problem (holding periods vary genuinely, from 1 to 40+

minutes) - it's a threshold-calibration problem, where "reversion"

entries sometimes fire during genuine trend continuation rather than

real mean reversion, and the sweep shows no threshold in this range

avoids that reliably.



\## Final Conclusion



Across two independent real order-book captures and two strategies

(one infrastructure-limited, one parameter-swept), Aureum has not

demonstrated a reliably profitable strategy against real ADA market

depth. This is an honest negative result, arrived at through the same

rigor applied throughout the project (real data validation, multi-

window testing, root-cause diagnosis rather than parameter searching

until a good number appears).



\## What this genuinely establishes

\- A complete, working research pipeline: live data -> backtesting ->

&#x20; risk management -> AI reasoning -> real order-book validation

\- A documented, diagnosed reason market making fails (execution speed)

\- A documented, diagnosed reason mean reversion (as implemented) fails

&#x20; (threshold calibration against genuine trend/reversion ambiguity)

\- Real evidence-based rejection of two plausible strategies, rather

&#x20; than false confidence from under-tested backtests

