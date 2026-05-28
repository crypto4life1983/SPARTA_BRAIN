"""s14-d1-cross-sector cash-equity AAPL/JPM/XOM RSI(3) bi-directional runner harness package.

Inherits Phase 2 safety contracts (C1-C8) from:
  docs/phase2_safety_contract_template.md
Template reuse: only safety contracts; no foreign strategy logic inherited.

s14-d1-cross-sector specific adaptations:
  - C5 corporate-action handling: split_only (DA17). AAPL 2020-08-31 4:1 applied+verified;
    JPM/XOM no splits in window. Dividends NOT adjusted. NOT structurally-absent (futures); splits
    are documented + applied.
  - C3 extended_hours fill / unsupported_order_type NOT_APPLICABLE (daily bars).
  - C4 US equity RTH session boundary (NYSE/NASDAQ 09:30-16:00 ET).
  - Multi-name portfolio: max_positions_per_name=1, max_total_positions=3, per-name independent
    signals, no inter-name coordination, no pyramid (DA20).
  - A7 effective_independent_bets + K10 avg_pairwise_correlation LOAD-BEARING (cross-sector thesis).
  - REC1-equivalent + DA3=B (0.5%) + DA4=B ($100k) + K9-reachability carried binding in C6.

Anchors:
  tier_n_spec_seal     = 862c00a5ffcc470580b6defe9c31ce89c4a43114ad418b4b6b4dfb991500569c (commit 53cb804)
  plan_lock_seal       = fa6c2c52fb0befd5ec2345d3d74f4fd4ad4577ec4f4857193c288171692bcd00 (commit 02b77d8)
  p2_phase2_plan_seal  = 89717a4a60ff6b704c5922683d0a46e34e59e4032a5d38eba8b1bf841f819d67 (commit 27dbddc)

P3 BUILD scope: module structure + CONFIG + Algo class + RSI(3) bi-directional signal primitives.
NO backtest, NO fetch, NO broker calls. Strategy execution requires separate operator
authorization (P4 smoke / P6 IS / P10 OOS) and remains BLOCKED at 6 gates regardless of verdict.
"""

__version__ = "s14_d1_cross_sector_v0_1_0"
