"""S12-D1 MNQ.c.0 Single-Instrument Donchian-15/8 runner harness.

P3 BUILD (no execution). Implements the locked F1 mechanic per the
sealed Tier-N spec at commit 9ce4d66 + P1 plan-lock at bd7245e + P2
phase-2 plan at 2b27acc2.

This package authors code only; it does NOT run the strategy on IS or
OOS data at BUILD time. Future P6 IS / P10 OOS / P10.5 cost-stress
phases (each requiring separate fresh operator authorization) will
invoke the in-sample / out-of-sample drivers.

Hard invariants (carried byte-equivalent from SEAL):
- candidate_record_id: s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history
- Universe: {MNQ.c.0} only (no widening, no substitution)
- Donchian periods: N=15 entry / M=8 exit (LOCKED at PLAN; no retreat to 55/20)
- Mechanic family: F1 bi-directional, no pyramid, ATR(20) stop
- START_CASH_USD: 100000.0 (DA4=B revised at SEAL)
- Per-trade risk: 1.0% of portfolio equity
- max_units_per_market: 1 (no-pyramid invariant)
- WARMUP_DAYS: 220
- RTH window: 09:30-16:00 ET America/New_York
- Cost tiers: S0/S1/S2/S3/S4 (5-tier, scalars 0.0/1.0/1.5/2.0/3.0)
- Commission per round-trip: $0.74; Fees: $0.36; Slippage e/s/x: 1/1/1 ticks
- K9 threshold: 100 closed trades (IS + OOS both)
- K4 max-drawdown threshold: 50% of START_CASH ($50,000 abs)
- OOS K9 sub-threshold disposition: DR1 INCONCLUSIVE_HOLD (per C1.D)

Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.
"""

__all__ = []
