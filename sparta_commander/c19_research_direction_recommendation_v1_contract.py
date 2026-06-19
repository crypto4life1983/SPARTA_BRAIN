"""SPARTA C19 Research-Direction Recommendation v1 (PURE, READ-ONLY, RESEARCH ONLY).

Planning-mode output produced with the guarded automation stack (Orchestrator v2 +
Commit Guard + Runner + Executor) in DRY-RUN / planning only. It RECOMMENDS the next
research direction for a future Candidate #19 -- one preferred family and two backups
-- distilled from the lessons of the C1-C18 rejected families, but it DOES NOT assign
or open C19, creates no candidate, fetches no data, builds no detector / spec / labels
/ replay, optimizes nothing, and writes no trading code.

Central thesis (the C17 + C18 lesson): both C17 (vol-targeted / risk-parity
allocation) and C18 (H4 trend-following) cleared the structural labels gate and even
CUT DRAWDOWN, yet died on the SAME rock at fee-honest replay -- a long-biased
construction could not beat BTC/SOL buy-and-hold on a RISK-ADJUSTED basis, and lower
drawdown alone is not an edge. The cleanest escape is to stop trying to out-risk-
adjust buy-and-hold with long-biased exposure and instead pursue a MARKET-NEUTRAL
edge that has NO buy-and-hold beta to lose to (judged net-positive vs random / null),
while fixing the exact out-of-sample neutrality failure that rejected C16.

The H4 friend-style concept is considered but NOT reused: C18 rejected the OBJECTIVE
BTC H4 approximation; revisiting it would need a genuinely different instrument /
timeframe / edge AND separate approval, and is NOT recommended for C19.

Every capability flag is pinned False with a full scope_locks set. Turning ANY
direction below into Candidate #19 requires the separate explicit human token
HUMAN_APPROVED_C19_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep
import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane

C19R_VERSION = "v1"
C19R_MODE = "RESEARCH_ONLY"
C19R_LANE = "crypto_d1_auto_research"

REJECTED_FAMILIES_C1_TO_C18 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C18)
REJECTED_LEDGER_COUNT = len(REJECTED_FAMILIES_C1_TO_C18)            # 23

# The recommendation does NOT open C19. This separate, explicit human token is the
# ONLY thing that may turn the preferred direction into a candidate proposal.
HUMAN_TOKEN_TO_OPEN_C19 = (
    "HUMAN_APPROVED_C19_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL")
# Until then the lane's own next action stands (no candidate is open / started).
NEXT_REQUIRED_ACTION = (
    "AWAIT_HUMAN_DECISION_ON_C19_RESEARCH_DIRECTION__NO_C19_ASSIGNED")

# --- what the C1-C18 corpus teaches (the failure rocks to avoid) ------------
LESSONS_C1_TO_C18 = (
    "BUY-AND-HOLD CARRY TRAP: long-biased directional edges reduce to crypto beta "
    "and lose to simply holding (C10, C14, C15, and the raw-return side of C18)",
    "RISK-ADJUSTED FAILURE vs BUY-AND-HOLD: even well-constructed long-biased risk "
    "management cut drawdown but did NOT beat buy-and-hold on Sharpe/Calmar (C17, "
    "C18) -- lower drawdown ALONE is not an edge",
    "FORWARD-OOS COLLAPSE: in-sample looked fine, the 2026 forward-OOS edge did not "
    "hold (C11, C14, C17, C18)",
    "COST EROSION: net-negative after 37 bps, worse on multiple legs / high turnover "
    "(C12, C16)",
    "STRUCTURAL RARITY: too few valid events to clear the >=100 / >=20-per-asset "
    "labels gate (C13, C16)",
    "UNVALIDATED NEUTRALITY: a level-OLS hedge that is NOT return-beta-neutral out "
    "of sample (C16, net beta 2.82 >> 0.10)",
)

TRAITS_TO_AVOID = (
    "any dependence on net long / directional crypto beta (it will lose to "
    "buy-and-hold, the C17/C18 rock)",
    "judging success on raw return or on lower-drawdown-alone instead of beating "
    "the baseline RISK-ADJUSTED",
    "rare events that cannot clear the >=100 / >=20-per-asset structural gate",
    "thin edges eroded by fees/slippage or multi-leg / high-turnover cost",
    "in-sample-only fit with no forward-OOS survival",
    "neutrality / hedge assumptions that are not validated out-of-sample (C16)",
    "reusing any C1-C18 mechanism, including the H4 friend-style approximation (C18)",
)

TRAITS_TO_PREFER = (
    "MARKET-NEUTRAL by construction (no buy-and-hold beta to lose to) -- judged "
    "net-positive vs random / null, not vs holding BTC",
    "neutrality VALIDATED out-of-sample BEFORE any trading logic (fixes the exact "
    "C16 failure)",
    "a continuous / frequent signal with ample sample across bull / bear / chop",
    "low turnover so the 37 bps round-trip cost cannot dominate",
    "feasible on the ALREADY-CACHED BTC/ETH/SOL D1 spot data -- no new data fetch",
    "forward-OOS survival designed in as a gate from the start",
)

# --- the ranked directions (preferred + 2 backups); NONE is a rejected family
PREFERRED_DIRECTION_KEY = "oos_validated_beta_neutral_cross_sectional_relative_value"

NEXT_RESEARCH_DIRECTIONS = (
    {
        "key": "oos_validated_beta_neutral_cross_sectional_relative_value",
        "rank": 1,
        "role": "preferred",
        "name": "OOS-validated beta-neutral cross-sectional relative value "
                "(BTC/ETH/SOL, returns-space)",
        "mechanism": ("a continuous dollar- AND return-beta-neutral long-short "
                      "relative-value spread among BTC/ETH/SOL built in RETURN space, "
                      "where the beta-neutrality is VALIDATED out-of-sample as gate "
                      "zero before any trading logic, then the residual spread is "
                      "traded on mean-reversion of the neutral residual"),
        "market_neutral": True,
        "evaluation_axis": "net_positive_market_neutral_vs_random_and_null",
        "sample_size_outlook": "ample (continuous daily residual; not event-rare)",
        "feasible_on_cached_data": True,
        "data_required": "already-cached BTC/ETH/SOL D1 spot OHLCV (no new fetch)",
        "avoids": ("buy-and-hold carry trap (market-neutral, no beta to lose to)",
                   "risk-adjusted-vs-buy-and-hold failure (judged vs random/null)",
                   "structural rarity (continuous daily residual)",
                   "C16 neutrality failure (neutrality validated OOS first)"),
        "distinct_from_rejected": (
            "C16 (cointegration pairs) assumed neutrality from a level-OLS hedge on "
            "PRICE LEVELS that failed OOS (net beta 2.82) and had too few "
            "cointegration windows (43); this is a RETURNS-space, beta-neutral, "
            "CONTINUOUS residual whose neutrality is an OOS-validated GATE, not an "
            "assumption. C11 (relative-strength rotation) was a long-biased "
            "directional rotation; this is dollar+beta neutral with no net long "
            "exposure. It is materially different in construction (returns vs "
            "levels), sample profile (continuous vs intermittent), and the built-in "
            "OOS-neutrality gate."),
    },
    {
        "key": "dollar_neutral_rebalancing_diversification_premium",
        "rank": 2,
        "role": "backup",
        "name": "Dollar-neutral rebalancing / diversification premium (BTC/ETH/SOL)",
        "mechanism": ("harvest the rebalancing / diversification return of a "
                      "dollar-neutral, beta-neutral BTC/ETH/SOL combination via "
                      "disciplined low-turnover rebalancing of the neutral legs -- a "
                      "portfolio-MECHANICS edge, not a directional or RV timing "
                      "signal"),
        "market_neutral": True,
        "evaluation_axis": "net_positive_market_neutral_vs_buy_and_hold_neutral_null",
        "sample_size_outlook": "ample (continuous rebalancing)",
        "feasible_on_cached_data": True,
        "data_required": "already-cached BTC/ETH/SOL D1 spot OHLCV (no new fetch)",
        "avoids": ("buy-and-hold carry trap (dollar+beta neutral)",
                   "cost erosion (explicitly low-turnover)",
                   "timing-signal fragility (mechanics, not a forecast)"),
        "distinct_from_rejected": (
            "C17 (vol-targeted / risk-parity allocation) was a LONG-ONLY allocation "
            "judged vs buy-and-hold; this is a DOLLAR-NEUTRAL long-short whose return "
            "comes from rebalancing mechanics, not net market exposure. No C1-C18 "
            "family harvested rebalancing premium from a neutral basket."),
    },
    {
        "key": "orthogonal_residual_alpha_ensemble_meta_study",
        "rank": 3,
        "role": "backup",
        "name": "Orthogonal residual-alpha ensemble meta-study (research-only, never "
                "traded)",
        "mechanism": ("a purely DESCRIPTIVE study of whether the rejected C1-C18 "
                      "signals carry any orthogonal residual alpha when combined "
                      "market-neutrally -- informs whether any ensemble is worth "
                      "proposing at all; it is never promoted to trading"),
        "market_neutral": True,
        "evaluation_axis": "descriptive_only_no_promotion",
        "sample_size_outlook": "n/a (descriptive meta-study over the cached corpus)",
        "feasible_on_cached_data": True,
        "data_required": "already-committed C1-C18 labels / replay artifacts + cached "
                         "BTC/ETH/SOL D1 (no new fetch)",
        "avoids": ("premature candidate creation (study first)",
                   "buy-and-hold carry trap (market-neutral, descriptive)"),
        "distinct_from_rejected": (
            "studies the C1-C18 corpus rather than proposing a single new directional "
            "mechanism; it is descriptive and never traded, so it cannot repeat any "
            "rejected family's failure mode."),
    },
)

# --- the data that WOULD be required (none requires a new fetch) ------------
DATA_REQUIRED = {
    "preferred": "already-cached BTC/ETH/SOL D1 spot OHLCV (the C16/C17 cache) -- "
                 "NO new data fetch",
    "backups": "same cached BTC/ETH/SOL D1 (+ the already-committed C1-C18 labels / "
               "replay artifacts for the meta-study) -- NO new data fetch",
    "no_new_fetch_required": True,
    "no_xauusd_or_new_instrument_class": True,
}

# --- the gates that WOULD be needed (the frozen lifecycle, unchanged) -------
GATES_REQUIRED = (
    {"gate": "human_open_c19", "what": "explicit human token "
     "HUMAN_APPROVED_C19_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL "
     "(this recommendation does NOT open C19)"},
    {"gate": "family_proposal", "what": "pure proposal contract for the chosen "
     "family (declared, anti-loop checked vs the 23-family ledger)"},
    {"gate": "candidate_spec", "what": "exact neutral-construction / entry / exit / "
     "turnover / invalidation rules (declared, pure)"},
    {"gate": "detector_spec_dry_run", "what": "detector spec + synthetic dry-run "
     "(no real data)"},
    {"gate": "real_candle_labels_review", "what": "label on cached real candles; "
     "MUST clear the >=100 / >=20-per-asset structural sample-size gate AND the "
     "OOS-neutrality validation gate before replay"},
    {"gate": "fee_honest_replay_review", "what": "mark-to-market replay net of 37 "
     "bps; for a market-neutral edge MUST be net-positive vs random / null AND "
     "survive the 2026 forward-OOS window"},
    {"gate": "rejection_or_promote_decision", "what": "explicit human verdict; "
     "keep-on-record either way"},
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "assigns_c19", "creates_candidate",
    "creates_candidate_id", "opens_candidate", "runs_detector", "runs_labels",
    "runs_replay", "computes_pnl", "optimizes_parameters", "relabels",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data", "auto_commits",
    "auto_pushes", "reuses_rejected_family", "reuses_h4_friend_concept",
    "adds_new_instrument_class", "modifies_scheduler", "sends_notifications",
    "calls_api", "uses_network", "uses_credentials", "connects_broker",
    "connects_exchange", "uses_real_money", "places_orders", "contains_order_logic",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def _preferred() -> dict[str, Any]:
    for d in NEXT_RESEARCH_DIRECTIONS:
        if d["key"] == PREFERRED_DIRECTION_KEY:
            return dict(d)
    return {}


def _backups() -> list:
    return [dict(d) for d in NEXT_RESEARCH_DIRECTIONS if d["role"] == "backup"]


def get_c19_recommendation_label() -> str:
    return (
        "C19 research-direction recommendation v1 (READ-ONLY, RESEARCH ONLY, PLANNING "
        "MODE). Recommends one preferred + two backup MARKET-NEUTRAL families "
        "distilled from the C1-C18 (23) rejected-family lessons, WITHOUT assigning or "
        "opening C19. The H4 friend-style concept is not reused (C18 rejected the "
        "objective BTC H4 approximation). Real-data-QA / replay BLOCKED; paper / "
        "micro-live / live LOCKED. Opening C19 needs a separate explicit human token. "
        "Executes nothing; not a profitability claim.")


def build_c19_research_direction_recommendation() -> dict[str, Any]:
    """Assemble the frozen C19 research-direction recommendation. Pure; composes the
    rejected-ledger lessons + lane status (read-only). Executes nothing; assigns no
    C19; creates no candidate."""
    lane = _lane.get_lane_status()
    directions = [dict(d) for d in NEXT_RESEARCH_DIRECTIONS]
    none_is_rejected = all(d["key"] not in REJECTED_FAMILIES_C1_TO_C18
                           for d in directions)

    record: dict[str, Any] = {
        "version": C19R_VERSION, "mode": C19R_MODE, "lane": C19R_LANE,
        "is_recommendation_only": True,
        "label": get_c19_recommendation_label(),
        # explicitly does NOT open / assign C19
        "assigns_c19": False,
        "c19_assigned": False,
        "creates_candidate": False,
        "candidate_id": None,
        "is_active_candidate": False,
        # current lane state reviewed (read-only)
        "lane_active_candidate": lane.get("active_candidate"),
        "lane_open_candidate_gate": lane.get("open_candidate_gate"),
        "rejected_ledger_count": lane.get("rejected_ledger_count"),
        "uses_c1_to_c18_ledger": REJECTED_LEDGER_COUNT == 23,
        "last_rejected_candidate": lane.get("last_rejected_candidate"),
        "c18_rejected_at_replay": (
            lane.get("last_rejected_candidate") == "C18"
            and (lane.get("last_rejected_candidate_detail") or {}).get("verdict")
            == "C18_REJECTED_AT_FEE_HONEST_REPLAY"),
        # lessons + traits
        "lessons_c1_to_c18": list(LESSONS_C1_TO_C18),
        "traits_to_avoid": list(TRAITS_TO_AVOID),
        "traits_to_prefer": list(TRAITS_TO_PREFER),
        # the recommendation
        "next_research_directions": directions,
        "preferred_direction": _preferred(),
        "preferred_direction_key": PREFERRED_DIRECTION_KEY,
        "backup_directions": _backups(),
        "why_preferred_is_materially_different": (
            "every C1-C18 rejected family was LONG-BIASED or a directional / "
            "mean-reversion / pairs TIMING signal; C17 and C18 in particular cut "
            "drawdown but still could not beat buy-and-hold RISK-ADJUSTED, and the "
            "forward-OOS edge collapsed. The preferred direction is MARKET-NEUTRAL by "
            "construction -- it carries NO buy-and-hold beta, so it is judged "
            "net-positive vs random / null rather than against holding BTC, which is "
            "the exact rock C17/C18 died on. It also fixes C16's specific failure by "
            "VALIDATING return-beta-neutrality out-of-sample as gate zero (vs C16's "
            "unvalidated level-OLS hedge), is continuous (ample sample, unlike "
            "C13/C16), and is feasible on the cached BTC/ETH/SOL D1 data with no new "
            "fetch. The same downstream gates still apply -- it must clear the "
            "structural sample gate, be net-positive market-neutral, and survive "
            "forward-OOS."),
        "directions_are_distinct_from_rejected_ledger": none_is_rejected,
        # H4 friend-style concept handled explicitly
        "h4_friend_concept_considered": True,
        "h4_friend_concept_reused": False,
        "h4_friend_concept_note": (
            "Considered and NOT reused: C18 rejected the OBJECTIVE BTC H4 "
            "trend-following approximation at fee-honest replay. Revisiting the "
            "friend-style concept would require a genuinely different instrument / "
            "timeframe / edge AND separate human approval; it is NOT recommended for "
            "C19. (This does not reject the observed trader's exact private system.)"),
        # data + gates
        "data_required": dict(DATA_REQUIRED),
        "gates_required": [dict(g) for g in GATES_REQUIRED],
        # human gate -- nothing becomes C19 without this
        "requires_human_approval_before_c19": True,
        "human_token_to_open_c19": HUMAN_TOKEN_TO_OPEN_C19,
        "next_required_action": NEXT_REQUIRED_ACTION,
        # posture / locks (from the lane)
        "overnight_automation_research_only": lane.get(
            "overnight_automation_research_only"),
        "real_data_qa_state": lane.get("real_data_qa_state"),
        "replay_state": lane.get("replay_state"),
        "paper_trading_state": lane.get("paper_trading_state"),
        "live_trading_state": lane.get("live_trading_state"),
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_write": True, "no_assign_c19": True,
        "no_open_candidate": True, "no_create_candidate": True, "no_candidate_id": True,
        "no_detector": True, "no_labels": True, "no_replay": True, "no_pnl": True,
        "no_optimization": True, "no_relabel": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_new_instrument_class": True, "no_xauusd": True,
        "no_reuse_rejected_family": True, "no_reuse_h4_friend_concept": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def get_c19_recommendation_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def validate_c19_research_direction_recommendation(
        record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only,
    recommendation-only, assigns/opens NO C19 and creates no candidate, reviews the
    live lane (no active candidate, ledger 23, C18 rejected), recommends exactly one
    preferred + two backup MARKET-NEUTRAL directions that are NONE of the 23 rejected
    families, explicitly does not reuse the H4 friend concept, declares the data
    (no new fetch) and the full downstream gate chain, requires the separate human
    token to open C19, and pins every capability flag False with the scope locks."""
    failures: list = []
    if record.get("mode") != C19R_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_recommendation_only") is not True:
        failures.append("not_recommendation_only")

    # must NOT assign / open C19 or create a candidate
    for k in ("assigns_c19", "c19_assigned", "creates_candidate",
              "is_active_candidate"):
        if record.get(k) is not False:
            failures.append("must_be_false_%s" % k)
    if record.get("candidate_id") is not None:
        failures.append("candidate_id_must_be_none")

    # reviewed live lane state
    if record.get("lane_active_candidate") is not None:
        failures.append("lane_should_have_no_active_candidate")
    if record.get("rejected_ledger_count") != 23:
        failures.append("ledger_not_23")
    if record.get("uses_c1_to_c18_ledger") is not True:
        failures.append("not_using_c1_to_c18_ledger")
    if record.get("c18_rejected_at_replay") is not True:
        failures.append("c18_not_rejected_at_replay")

    # exactly one preferred + two backups; all market-neutral; none is rejected
    dirs = record.get("next_research_directions") or []
    if len(dirs) != 3:
        failures.append("expected_three_directions")
    preferred = [d for d in dirs if d.get("role") == "preferred"]
    backups = [d for d in dirs if d.get("role") == "backup"]
    if len(preferred) != 1:
        failures.append("expected_one_preferred")
    if len(backups) != 2:
        failures.append("expected_two_backups")
    if record.get("preferred_direction_key") != PREFERRED_DIRECTION_KEY:
        failures.append("preferred_key_tampered")
    for d in dirs:
        if d.get("market_neutral") is not True:
            failures.append("direction_not_market_neutral__%s" % d.get("key"))
        if d.get("key") in REJECTED_FAMILIES_C1_TO_C18:
            failures.append("direction_is_a_rejected_family__%s" % d.get("key"))
        if not d.get("distinct_from_rejected"):
            failures.append("direction_missing_distinctness__%s" % d.get("key"))
    if record.get("directions_are_distinct_from_rejected_ledger") is not True:
        failures.append("directions_not_distinct_from_ledger")
    if not record.get("why_preferred_is_materially_different"):
        failures.append("missing_material_difference_rationale")

    # H4 friend concept considered but not reused
    if record.get("h4_friend_concept_considered") is not True:
        failures.append("h4_concept_not_considered")
    if record.get("h4_friend_concept_reused") is not False:
        failures.append("h4_concept_must_not_be_reused")

    # data (no new fetch) + full gate chain
    dr = record.get("data_required") or {}
    if dr.get("no_new_fetch_required") is not True:
        failures.append("data_requires_new_fetch")
    if dr.get("no_xauusd_or_new_instrument_class") is not True:
        failures.append("data_adds_new_instrument_class")
    gate_names = [g.get("gate") for g in (record.get("gates_required") or [])]
    for required in ("human_open_c19", "family_proposal", "candidate_spec",
                     "detector_spec_dry_run", "real_candle_labels_review",
                     "fee_honest_replay_review", "rejection_or_promote_decision"):
        if required not in gate_names:
            failures.append("gate_missing__%s" % required)

    # the separate human token to open C19
    if record.get("requires_human_approval_before_c19") is not True:
        failures.append("missing_human_approval_requirement")
    if record.get("human_token_to_open_c19") != HUMAN_TOKEN_TO_OPEN_C19:
        failures.append("human_token_tampered")
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_action_must_not_open_c19")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_assign_c19", "no_open_candidate",
                "no_create_candidate", "no_detector", "no_labels", "no_replay",
                "no_optimization", "no_data_fetch", "no_new_instrument_class",
                "no_xauusd", "no_reuse_rejected_family", "no_reuse_h4_friend_concept",
                "no_commit", "no_push", "no_paper_trading", "no_live_trading",
                "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
