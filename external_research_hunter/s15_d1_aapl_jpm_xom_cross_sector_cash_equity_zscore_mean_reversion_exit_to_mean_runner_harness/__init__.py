"""s15-d1-cross-sector cash-equity AAPL/JPM/XOM z-score mean-reversion EXIT-TO-MEAN runner harness.

Inherits Phase 2 safety contracts (C1-C8) from docs/phase2_safety_contract_template.md.
Only safety contracts inherited; no foreign strategy logic.

s15-d1 specific design (the first-principles exit/stop edge fix after s14-d1-cross-sector FAIL_SAFETY):
  - NON-RSI z-score / Bollinger-band mean-reversion (lookback L=20, entry band k=2.0 sigma)
  - EXIT-TO-MEAN: close on re-cross of the rolling mean (SMA_L midline) = the reversion target
  - vol-scaled catastrophe stop: entry -/+ 3.5*sigma_L (NOT a fixed 2N ATR); disaster brake only
  - time-stop max-hold 10 bars fallback; vol-normalized sizing shares=floor(risk$/(3.5*sigma_L))
  - C5 split_only (AAPL 2020-08-31 4:1 applied+verified; JPM/XOM none); C3 extended-hours NA daily;
    C4 US equity RTH; portfolio max_total=3 / per_name=1, no pyramid, no inter-name coordination
  - REC1-equivalent + DA3=B (0.5%) + DA4=B ($100k) carried binding in C6

Anchors:
  tier_n_spec_seal     = 1a89df0f07c4360cb1969f02889cd6fa973b93e81b21f0b3e27c6adc3ff0903d (commit 597a49b)
  plan_lock_seal       = d1355589e0c43f9a19ae575fabb87458b7e86d33184de8b33f082cf3c9d383a3 (commit c8d6dd5)
  p2_phase2_plan_seal  = 6579f5cab302f5bf46c57184a196645755e1149941b614239cb8e9ad29488a40 (commit 5b36ac8)

P3 BUILD scope: module structure + CONFIG + Algo class + z-score exit-to-mean signal primitives.
NO backtest, NO fetch, NO broker calls. Strategy execution requires separate operator authorization
(P4 smoke / P6 IS / P10 OOS) and remains BLOCKED at 6 gates regardless of any future verdict.
"""

__version__ = "s15_d1_cross_sector_zscore_exit_to_mean_v0_1_0"
