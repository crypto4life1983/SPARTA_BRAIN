"""CandidateState: per-candidate research-lifecycle state.

Tracked per candidate_id (e.g. "s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-..."):
    - canonical chain commits (in lifecycle order)
    - duplicate / parallel chain commits (acknowledged, not anchored)
    - current phase classification
    - latest sealed verdict
    - K9 pass/fail + observed closed_trades
    - DR-gate status snapshot
    - REC1_T1 / L1 carry-forward status
    - next recommended action (decision-engine output)
    - forbidden actions (hard-guard derived)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


# K9 / DR / L1 status enums kept as bare strings for JSON portability.
K9_PASS = "PASS"
K9_FAIL = "FAIL"
K9_UNKNOWN = "UNKNOWN"
K9_NOT_EVALUATED = "NOT_EVALUATED"

L1_FULL = "FULL_REC1_T1_BYTE_EQUIVALENT"
L1_PARTIAL = "PARTIAL_REC1_EQUIVALENT_VIA_C6_INHERITANCE_ONLY"
L1_MISSING = "MISSING_NO_REC1_OR_C6"

PHASE_PLAN = "PLAN"
PHASE_DRAFT = "DRAFT"
PHASE_SEAL = "SEAL"
PHASE_P1 = "P1"
PHASE_P2 = "P2"
PHASE_P3_BUILD = "P3_BUILD"
PHASE_P4_SMOKE = "P4_SMOKE"
PHASE_P6_IS = "P6_IS"
PHASE_P6_5_COST_STRESS = "P6_5_COST_STRESS"
PHASE_P7_DECISION = "P7_DECISION"
PHASE_P10_OOS = "P10_OOS"
PHASE_P11_LIFECYCLE = "P11_LIFECYCLE"
PHASE_SUPPLEMENT = "SUPPLEMENT"
PHASE_OBSERVATION = "OBSERVATION"
PHASE_DUPLICATE_CHAIN = "DUPLICATE_CHAIN"
PHASE_UNKNOWN = "UNKNOWN"


@dataclass
class CandidateState:
    """Per-candidate lifecycle state.

    A 'canonical_chain' lists commits in lifecycle order on the SEAL-A chain.
    A 'duplicate_chain' lists commits on the parallel SEAL-B chain that the
    operator has consistently chosen to acknowledge-but-not-anchor.
    """

    candidate_id: str
    canonical_chain: list[str] = field(default_factory=list)
    duplicate_chain: list[str] = field(default_factory=list)
    current_phase: str = PHASE_UNKNOWN
    latest_verdict: str | None = None
    closed_trades_observed: int | None = None
    k9_threshold: int = 100
    k9_status: str = K9_NOT_EVALUATED
    dr_gate_status: dict[str, Any] = field(default_factory=dict)
    rec1_t1_carry_status: str = L1_MISSING
    next_recommended_action: str | None = None
    forbidden_actions: list[str] = field(default_factory=list)
    last_updated_utc: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CandidateState":
        return cls(**d)

    def is_k9_passing(self) -> bool:
        return self.k9_status == K9_PASS

    def add_forbidden(self, action: str) -> None:
        if action not in self.forbidden_actions:
            self.forbidden_actions.append(action)


# Hard guards every candidate inherits.
HARD_GUARD_FORBIDDEN_ALWAYS = [
    "STAGE_LESSONS_MD",
    "MODIFY_LESSONS_MD",
    "MODIFY_LIVE_TRADING_CODE",
    "MODIFY_PAPER_TRADING_CODE",
    "MODIFY_BROKER_CODE",
    "RELAX_K9_THRESHOLD",
    "CLAIM_PROFITABILITY",
    "CLAIM_LIVE_READY",
    "CLAIM_OOS_CONFIRMED",
    "MODIFY_SEALED_ARTIFACT",
    "FETCH_DATABENTO_WITHOUT_LEVEL_3_APPROVAL",
    "RUN_P6_WITHOUT_LEVEL_3_APPROVAL",
    "RUN_P6_5_WITHOUT_LEVEL_3_APPROVAL",
    "RUN_P10_WITHOUT_LEVEL_3_APPROVAL",
]
