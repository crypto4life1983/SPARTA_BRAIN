"""s16-d1 expanded-universe (12-name) cash-equity Donchian breakout TREND (trailing-stop) runner harness.

Inherits Phase 2 safety contracts (C1-C8) from docs/phase2_safety_contract_template.md.
Only safety contracts inherited; no foreign strategy logic.

s16-d1 design (NON-mean-reversion family fix after s14/s15 cross-sector mean-reversion terminals):
  - Donchian channel breakout, bi-directional: enter long when close > prior N_entry=20 high; short
    when close < prior 20 low.
  - TRAILING exit = opposite N_exit=10 Donchian channel (let winners run / cut losers).
  - Initial catastrophe stop = 2 x ATR(14) from entry (vol-scaled floor; whichever triggers first).
  - vol-normalized sizing shares=floor(0.005*equity/(2*ATR14)); 0.5% risk/name (DA3=B); $100k (DA4=B).
  - portfolio max_total_positions=6, max_positions_per_name=1, no pyramid, no inter-name coordination.
  - C5 split_only; 12-name universe; DR9 PASSED all 12 by REUSE (245ac0d); no fetch.

Anchors:
  tier_n_spec_seal     = 359aea43df85c153c8cbf2b7a84ddeaa78d6516fe43769e34b052b4f88c60df8 (commit 985c569)
  plan_lock_seal       = 957ca333d59a24e942a1c5f6c40375035942e2fcc53bc461c0ffbe5684d60f86 (commit f95e5e3)
  p2_phase2_plan_seal  = 3fa8634d3c5c4317ae27a498542cac7757a50029de766967d2a729cddcf73df5 (commit f826aea)

P3 BUILD scope: module structure + CONFIG + Algo class + Donchian breakout/trailing-exit primitives.
NO backtest, NO fetch, NO broker calls. Execution requires separate operator authorization
(P4 smoke / P6 IS / P10 OOS) and remains BLOCKED at 6 gates regardless of any verdict.
"""

__version__ = "s16_d1_expanded_donchian_trend_v0_1_0"
