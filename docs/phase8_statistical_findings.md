# Phase 8 - Real Statistical Findings

**Owner:** Hansika
**Data:** Baseline vs Baseline+AI, 3 pinned windows, real trade-level PnL (2026-09-02)

---

## Bug Fixed Before This Analysis

The initial comparison script bootstrapped over candle-level equity returns, which was dominated by structural zeros (equity is flat between trades with only 2-34 fills across 1,440-2,880 candles). Fixed to bootstrap over trade-level realized PnL, filtering to CLOSING trades only - opening trades always carry realized_pnl=0.0 by construction (nothing to realize yet), not a genuine zero-PnL outcome. Verified this filter exactly matches each run's own num_closing_trades summary field before relying on it.

---

## Results by Window

### recent_24h
- Baseline: 2 closing trades, PnLs [0.189, -0.040]
- AI variant: 1 closing trade, PnL [-0.040]
- **Cannot compare** - AI variant has only 1 observation, below the minimum of 2 needed for bootstrap resampling to be meaningful.

### prior_24h
- Baseline: 8 closing trades
- AI variant: 1 closing trade, PnL [-0.091]
- **Cannot compare** - same reason as above.

### prior_48h
- Baseline: 17 closing trades, mean PnL -0.0106 [95% CI: -0.0417, 0.0259]
- AI variant: 9 closing trades, mean PnL -0.0090 [95% CI: -0.0390, 0.0288]
- Difference CI: [-0.0465, 0.0520] - **includes zero**
- **Inconclusive.** The AI variant's point estimate is slightly better (-0.0090 vs -0.0106), matching the directional pattern Samarth described, but the confidence interval is wide relative to the difference and cannot rule out the baseline being equal or better.

---

## Honest Overall Conclusion

**No window supports a confident claim that Baseline+AI outperforms the baseline.** Two of three windows have too few AI-variant trades (1 each) to run a statistical comparison at all - this is itself informative: the AI variant's volatility-avoidance behavior means it trades far less often, which is consistent with its design (reduce/pause quoting during HIGH_VOLATILITY), but it also means we have very little data to evaluate it on in the two shorter windows.

The one window with enough data on both sides (prior_48h) shows a directionally favorable but statistically inconclusive result for the AI variant.

**This matches exactly what docs/phase8_statistical_rigor.md predicted in advance: an inconclusive result given this sample size is the expected, correct outcome - not a sign the analysis failed.**

---

## Fee-Rate Correction — Resolved

MAKER_FEE_RATE was corrected from 0.0005 to 0.001 (Gauri, PR #68) and this
analysis was re-run against the corrected rate. Real effect observed:
win rates dropped and losses roughly doubled in the more active windows
(prior_24h, prior_48h) — confirming the fee gap mattered, as suspected.

**The statistical conclusion did NOT change**: prior_48h remains the
only window with enough data for comparison, and remains inconclusive
(95% CI for the difference: [-0.04653, 0.05191], includes zero). The
fee correction changed point estimates but not the final verdict —
worth noting as reassurance that the original finding wasn't an
artifact of the fee bug.

**These findings are now final, not provisional.**

---
---

## Independent Verification (Hansika, 2026-09-03)

Regenerated all 6 datasets fresh from the pinned windows and re-ran
`research/run_phase8_comparison.py` independently, without relying on
Samarth's stated numbers. Result matched exactly: prior_48h difference
CI = [-0.04653, 0.05191], identical to the value reported above.
recent_24h and prior_24h correctly still cannot be compared (AI
variant had only 1 closing trade in each, unchanged by the fee fix).

This confirms the fee-corrected findings are genuine and reproducible,
not a copy-paste or a single unverified run.

## Recommendation

- Do not report Baseline+AI as "better than baseline" based on this data - the evidence does not support that claim.
- The most useful next step is likely NOT more statistical squeezing of this same small sample, but either (a) running across more/longer windows to get enough AI-variant trades for a real comparison, or (b) fixing the fee-rate issue first, since it affects the interpretation of any number here.
- Two of three windows had too few AI trades to evaluate at all - worth discussing with Samarth whether the volatility-avoidance threshold is appropriately calibrated, or too conservative for these particular windows.

## Reproduction

```
python -m research.download_sensitivity_windows
python -c "from research.backtest.run_comparison_evaluation import run_comparison_across_windows; run_comparison_across_windows()"
python -m research.run_phase8_comparison
```