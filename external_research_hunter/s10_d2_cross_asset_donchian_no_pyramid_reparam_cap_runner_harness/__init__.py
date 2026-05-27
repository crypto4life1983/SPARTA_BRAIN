"""s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl runner harness.

PHASE 3 BUILD-only scaffolding (s8-D1, single delta from s7-D1: max_units_per_market=1). DIAGNOSTIC_ONLY_NOT_LIVE_GRADE.
Trading PAUSED. Live BLOCKED_AT_6_GATES. FRC never granted. No profitability claim.

Inherits Phase 2 safety contracts (C1-C8) from:
  docs/phase2_safety_contract_template.md  (sha 1812f485...8981)
  docs/phase2_safety_contract_template.json (sha 695a9fb6...4a32)
Template source candidate (parked, not money-proven):
  s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
Template reuse notice: NKE strategy logic NOT inherited; only safety contracts.
"""

__all__ = ["main", "execution_guard"]
