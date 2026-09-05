\# Phase 9 — Real Order-Book Validation Findings



\*\*Data:\*\* 8 hours of real captured ADA order-book depth (4,750 deltas, zero gaps), matched exactly against 482 real 1m candles from the same window.



\## Method

Replayed real order-book state and matched BaselineMarketMaker's quotes

against it via paper\_exchange.py's match\_limit\_order (genuine depth

walking), instead of candle\_fill\_model.py's high/low approximation used

in all prior phases.



\## Result — spread sweep



| half\_spread | fills | win\_rate | return |

|---|---|---|---|

| 0.001  | 0   | -      | 0%      |

| 0.0005 | 10  | 20.0%  | -0.19%  |

| 0.0003 | 55  | 7.4%   | -1.73%  |

| 0.0001 | 239 | 13.4%  | -6.58%  |

| 0.00005| 239 | 13.4%  | -6.58%  |



\## Conclusion



Every spread that produces any real fills against genuine order-book

depth loses money, and losses worsen as spread tightens (more trades,

more loss) rather than improving. The candle-close approximation used

throughout Phase 5-8 was materially more permissive with fills than

real market depth allows - none of the earlier "profitable" or

"inconclusive" results should be trusted as representative of real

market behavior.



\*\*Honest finding: this strategy design, as currently built, is not

demonstrated to be profitable against real ADA order-book depth in

this 8-hour window.\*\* This is a genuine negative result, not an

inconclusive one.



\## Caveats

\- Single 8-hour window - not the same statistical rigor as Phase 8's

&#x20; 3-window bootstrap comparison

\- Real order-book depth, but testnet liquidity may not reflect

&#x20; mainnet conditions

\- Only BaselineMarketMaker's spread was swept; BaselinePlusAI's

&#x20; behavior at these spreads not yet tested

