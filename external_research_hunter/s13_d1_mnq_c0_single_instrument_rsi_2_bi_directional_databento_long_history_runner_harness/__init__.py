"""s13-d1 MNQ.c.0 single-instrument RSI(2) bi-directional runner harness package.

Inherits Phase 2 safety contracts (C1-C8) from:
  docs/phase2_safety_contract_template.md
Template source candidate (parked, not money-proven):
  s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
Template reuse: NKE strategy logic NOT inherited; only safety contracts.

s13-d1 specific adaptations:
  - C5 corporate-action/event-risk STRUCTURALLY_ABSENT (futures)
  - C3 extended_hours / unsupported_order_type NOT_APPLICABLE
  - DR3 ELEVATED (RSI s9 lineage); mitigated via DA3=B (per_trade_risk=0.5%)
  - DR10 ELEVATED (high-frequency); mitigated via DA4=C (START_CASH=$200k)
  - REC1-equivalent + DA3=B + DA4=C + K9-reachability carried binding in C6

Anchors:
  tier_n_spec_seal     = 2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775 (commit 262491c)
  plan_lock_seal       = 1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c (commit 005cb8a)
  p2_phase2_plan_seal  = b181ce834f5eacd2fb9f6766d6ce9404a86ecfe3d2787c7e4899d3e47ba57ec6 (commit beecd87)
"""

__version__ = "s13_d1_v0_1_0"
