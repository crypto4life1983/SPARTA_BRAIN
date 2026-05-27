"""s12-d1 MNQ.c.0 single-instrument Donchian-15/8 runner harness package.

Inherits Phase 2 safety contracts (C1-C8) from:
  docs/phase2_safety_contract_template.md
  docs/phase2_safety_contract_template.json
Template source candidate (parked, not money-proven):
  s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
Template reuse notice: NKE strategy logic NOT inherited; only safety contracts.

s12-d1 specific adaptations:
  - C5 corporate-action/event-risk STRUCTURALLY_ABSENT (futures continuous-stitch)
  - C3 extended_hours / unsupported_order_type NOT_APPLICABLE
  - REC1 oos_k9_risk_disclosure carried binding

Anchors:
  tier_n_spec_seal     = 07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48 (commit 66bbbd1)
  plan_lock_seal       = eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340 (commit d8bd359)
  p2_phase2_plan_seal  = 689dd3d06c0e2518ab5f6105544cb3d38194027647de10940da976e427c8efa9 (commit 0b8d948)

Status (permanent):
  trading_status:        PAUSED
  live_status:           BLOCKED_AT_6_GATES
  frc_status:            NEVER_GRANTED
  research_label:        DIAGNOSTIC_ONLY_NOT_LIVE_GRADE
  lifecycle_state:       P3_BUILD_DRAFT (until P3 sealed BUILD reports are committed)
"""

__version__ = "s12_d1_v0_1_0"
