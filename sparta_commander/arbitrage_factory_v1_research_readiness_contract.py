"""SPARTA Arbitrage Factory V1 Research Readiness Contract (READ-ONLY, SPEC ONLY).

A PURE, stdlib-only, read-only module that OPENS a brand-new research lane -- the SPARTA
Arbitrage Factory V1 -- after the sealed Crypto-D1 Blocks 175->190 arc. It defines the
arbitrage research lane BEFORE any scanner, API client, data pull, or exchange connection
exists, so every later capability must be built against rules that predate it.

Scope of V1 research: crypto spot/perp funding, basis, spread, and cross-exchange
inefficiency RESEARCH. The lane produces ALERTS and PASS/WATCH/FAIL REPORTS only --
never orders. This contract is the readiness/spec layer: it registers the candidate
arbitrage families, the strict no-trade rules, the data/source requirements (without
fetching anything), the safety gates that must clear before any future scanner may even
be specified, and the roadmap of future blocks.

Hard boundary inherited from the SPARTA operating rules: no LLM or agent may receive
read/write exchange credentials or place orders unless a future top-level authorization
explicitly changes the architecture after full risk review. This lane is therefore
ALERT-ONLY BY CONSTRUCTION; "execution" is not a locked gate here -- it is absent.

It RUNS NOTHING and WRITES NOTHING: no data fetch, no API call, no exchange connection,
no credentials, no scanner run, no order logic, no paper/micro-live/live, no file write.
It does NOT touch the sealed Crypto-D1 lane and unlocks no gate anywhere.

Public API:
  - ARB_SCHEMA_VERSION / ARB_LABEL / ARB_MODE
  - VERDICT_READINESS_READY / NEXT_REQUIRED_ACTION
  - CANDIDATE_ARBITRAGE_FAMILIES / NO_TRADE_RULES / DATA_SOURCE_REQUIREMENTS
  - SAFETY_GATES_BEFORE_SCANNER / FUTURE_BLOCKS_ROADMAP
  - get_arbitrage_factory_v1_readiness_label()
  - candidate_arbitrage_families() / no_trade_rules() / data_source_requirements()
  - safety_gates_before_scanner() / future_blocks_roadmap()
  - build_arbitrage_factory_v1_readiness()
  - validate_arbitrage_factory_v1_readiness(spec)
  - render_arbitrage_factory_v1_readiness_markdown(spec)
"""

from __future__ import annotations

import copy
from typing import Any

ARB_SCHEMA_VERSION = "arbitrage_factory_v1_research_readiness_contract.v1"
ARB_LABEL = "SPARTA Arbitrage Factory V1 Research Readiness (READ-ONLY, SPEC ONLY)"
ARB_MODE = "RESEARCH_ONLY"

VERDICT_READINESS_READY = "ARBITRAGE_FACTORY_V1_READINESS_READY"

# After this readiness spec is recorded, the only next step is a SEPARATE explicit human
# approval of the scanner SPEC (a document, not a scanner). Nothing here authorizes any
# run, fetch, or connection.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_ARBITRAGE_SCANNER_SPEC"

# --- 1: candidate arbitrage families (fixed, research-only) ------------------
CANDIDATE_ARBITRAGE_FAMILIES: list[dict[str, Any]] = [
    {
        "family_id": "ARB_F1_spot_perp_funding_basis",
        "description": (
            "Spot vs perpetual funding/basis: measure the funding rate and the "
            "spot-perp basis on the same venue and quantify the theoretical "
            "delta-neutral carry, fee-adjusted."
        ),
        "research_question": (
            "After fees, slippage, and funding variability, does a persistent "
            "positive net carry exist, and how often does it invert?"
        ),
        "data_needs": ["spot daily closes", "perp funding history", "perp mark prices"],
    },
    {
        "family_id": "ARB_F2_cross_exchange_basis_monitoring",
        "description": (
            "Cross-exchange basis: monitor the same instrument's price across "
            "venues and characterize the spread distribution and persistence."
        ),
        "research_question": (
            "Are cross-venue spreads ever wider than round-trip costs for longer "
            "than transfer/settlement latency?"
        ),
        "data_needs": ["multi-venue price snapshots", "withdrawal/transfer fee tables"],
    },
    {
        "family_id": "ARB_F3_btc_eth_sol_pair_spread_alerts",
        "description": (
            "BTC/ETH/SOL pair-spread alerts: track relative-value ratios between "
            "the three majors and flag statistical extremes -- ALERTS only."
        ),
        "research_question": (
            "Do ratio extremes mean-revert reliably enough to be worth a "
            "human-reviewed alert, after the Crypto-D1 overfit lessons?"
        ),
        "data_needs": ["BTC/ETH/SOL daily closes (already-staged manual CSVs qualify)"],
    },
    {
        "family_id": "ARB_F4_fee_adjusted_net_edge_scanner",
        "description": (
            "Fee-adjusted net edge scanner: a future read-only scanner that "
            "reduces every raw opportunity to NET edge after maker/taker fees, "
            "funding, slippage, and transfer costs."
        ),
        "research_question": (
            "What fraction of raw 'opportunities' survive honest full-cost "
            "accounting?"
        ),
        "data_needs": ["venue fee schedules", "the approved fee/slippage model block"],
    },
    {
        "family_id": "ARB_F5_liquidity_spread_slippage_filters",
        "description": (
            "Liquidity/spread/slippage filters: minimum book depth, maximum "
            "quoted spread, and slippage ceilings that gate every family above."
        ),
        "research_question": (
            "What filter thresholds eliminate opportunities that only exist on "
            "paper-thin books?"
        ),
        "data_needs": ["order book depth snapshots", "quoted spread history"],
    },
    {
        "family_id": "ARB_F6_pass_watch_fail_report_framework",
        "description": (
            "PASS/WATCH/FAIL report framework: every family's output reduces to "
            "a three-state verdict per opportunity class, with evidence attached "
            "-- the lane's only product."
        ),
        "research_question": (
            "Can each verdict be made reproducible from staged inputs alone, "
            "with no live dependency?"
        ),
        "data_needs": ["outputs of ARB_F1..ARB_F5 once their blocks exist"],
    },
]

# --- 2: strict no-trade rules (the lane's constitution) ----------------------
NO_TRADE_RULES: list[str] = [
    "this_lane_produces_alerts_and_reports_only_never_orders",
    "no_order_logic_may_ever_be_added_to_any_arbitrage_factory_module",
    "no_exchange_credentials_read_or_write_may_ever_be_held_by_this_lane",
    "no_execution_gate_exists_to_unlock_execution_is_absent_by_construction",
    "any_future_execution_idea_requires_a_top_level_architecture_authorization_"
    "after_full_risk_review_outside_this_lane",
    "crypto_d1_lessons_apply_in_sample_edges_must_survive_preregistered_"
    "out_of_sample_bars_before_any_verdict_upgrade",
]

# --- 3: data/source requirements (defined, never fetched here) ---------------
DATA_SOURCE_REQUIREMENTS: dict[str, Any] = {
    "fetched_by_this_contract": False,
    "allowed_source_classes": [
        "manually_staged_csv_files_placed_by_the_operator",
        "future_separately_approved_read_only_public_market_data_contract",
    ],
    "forbidden": [
        "any_authenticated_or_private_endpoint",
        "any_credentialed_api_key",
        "any_websocket_or_streaming_connection_without_its_own_approved_data_contract",
        "any_fetch_performed_by_a_contract_module",
    ],
    "note": (
        "Until a dedicated data contract block is human-approved, the only data this "
        "lane may reference is what the operator manually stages on disk."
    ),
}

# --- 4: safety gates that must clear BEFORE any scanner exists ---------------
SAFETY_GATES_BEFORE_SCANNER: list[dict[str, Any]] = [
    {"gate_id": "G1_scanner_spec_approved",
     "requirement": "a read-only scanner SPEC contract is built, tested, and human-approved"},
    {"gate_id": "G2_data_contract_approved",
     "requirement": "a data contract defines exactly which read-only sources are allowed, "
                    "with staging rules and no credentials"},
    {"gate_id": "G3_fee_slippage_model_approved",
     "requirement": "a fee/slippage model block exists so every edge is net-of-costs "
                    "before it is ever reported"},
    {"gate_id": "G4_report_schema_approved",
     "requirement": "the PASS/WATCH/FAIL report schema is frozen before the first scan"},
    {"gate_id": "G5_commander_safety_review",
     "requirement": "the commander safety suite passes with the scanner module present, "
                    "with an allowlist entry only if the repo pattern requires one"},
    {"gate_id": "G6_explicit_human_run_approval",
     "requirement": "every scan run is individually human-approved; no scheduler, no "
                    "automation, no background loop"},
]

# --- 5: roadmap of future blocks (sequence is binding) ------------------------
FUTURE_BLOCKS_ROADMAP: list[dict[str, Any]] = [
    {"seq": 1, "block": "arbitrage_scanner_spec_contract",
     "purpose": "specify (not build) the read-only scanner: inputs, families covered, "
                "outputs, refusal conditions"},
    {"seq": 2, "block": "arbitrage_data_contract",
     "purpose": "define allowed read-only sources, staging layout, and QA rules; "
                "still fetches nothing"},
    {"seq": 3, "block": "arbitrage_fee_slippage_model_contract",
     "purpose": "frozen cost model: maker/taker fees, funding, slippage, transfer costs"},
    {"seq": 4, "block": "arbitrage_report_schema_contract",
     "purpose": "freeze the PASS/WATCH/FAIL report schema and evidence fields"},
    {"seq": 5, "block": "arbitrage_scanner_review_contract",
     "purpose": "read-only review layer over scanner reports; always "
                "human-review-required"},
    {"seq": 6, "block": "arbitrage_mission_flow_registration",
     "purpose": "register the lane's own mission-flow track without touching the "
                "sealed Crypto-D1 lane"},
]


def get_arbitrage_factory_v1_readiness_label() -> str:
    """Human label for the recognized Arbitrage Factory V1 readiness contract."""
    return ARB_LABEL


def candidate_arbitrage_families() -> list[dict[str, Any]]:
    """Return fresh deep copies of the fixed candidate families. Pure."""
    return [copy.deepcopy(f) for f in CANDIDATE_ARBITRAGE_FAMILIES]


def no_trade_rules() -> list[str]:
    """Return a fresh copy of the strict no-trade rules. Pure."""
    return list(NO_TRADE_RULES)


def data_source_requirements() -> dict[str, Any]:
    """Return a fresh deep copy of the data/source requirements. Pure; fetches nothing."""
    return copy.deepcopy(DATA_SOURCE_REQUIREMENTS)


def safety_gates_before_scanner() -> list[dict[str, Any]]:
    """Return fresh copies of the pre-scanner safety gates. Pure."""
    return [dict(g) for g in SAFETY_GATES_BEFORE_SCANNER]


def future_blocks_roadmap() -> list[dict[str, Any]]:
    """Return fresh copies of the binding future-block roadmap. Pure."""
    return [dict(b) for b in FUTURE_BLOCKS_ROADMAP]


def build_arbitrage_factory_v1_readiness() -> dict[str, Any]:
    """Assemble the full read-only readiness spec. PURE: no disk read, no fetch, no
    connection, no scanner, no order logic. Opens the lane; authorizes nothing."""
    return {
        "schema_version": ARB_SCHEMA_VERSION,
        "label": ARB_LABEL,
        "mode": ARB_MODE,
        "verdict": VERDICT_READINESS_READY,
        "lane": "arbitrage_factory_v1",
        "candidate_arbitrage_families": candidate_arbitrage_families(),
        "no_trade_rules": no_trade_rules(),
        "data_source_requirements": data_source_requirements(),
        "safety_gates_before_scanner": safety_gates_before_scanner(),
        "future_blocks_roadmap": future_blocks_roadmap(),
        # Lane constitution, stated structurally:
        "alerts_and_reports_only": True,
        "execution_capability_exists": False,
        "scanner_exists": False,
        "modifies_crypto_d1_lane": False,
        "blockers": [],
        "risk_notes": [
            "lane_opened_before_any_scanner_api_or_data_pull_exists",
            "every_future_capability_must_clear_the_preregistered_safety_gates",
            "crypto_d1_overfit_lessons_carried_as_lane_constraints",
            "scanner_spec_is_a_document_not_a_scanner",
        ],
        # Capability posture (this spec runs / fetches / connects / authorizes nothing):
        "executes": False,
        "writes_files": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "fetches_data": False,
        "calls_api": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "contains_order_logic": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        # Gate posture (the global trading gates are UNTOUCHED and stay locked):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def validate_arbitrage_factory_v1_readiness(spec: Any) -> dict[str, Any]:
    """Validate (read-only) a readiness spec's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec

    if s.get("verdict") != VERDICT_READINESS_READY:
        errors.append("bad_verdict")
    if s.get("schema_version") != ARB_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if s.get("lane") != "arbitrage_factory_v1":
        errors.append("bad_lane")

    fams = s.get("candidate_arbitrage_families")
    if not isinstance(fams, list) or len(fams) != 6:
        errors.append("families_not_six")
        fams = []
    seen: set[str] = set()
    for f in fams:
        if not isinstance(f, dict):
            errors.append("family_not_a_dict")
            continue
        for key in ("family_id", "description", "research_question", "data_needs"):
            if key not in f:
                errors.append("family_missing_field:" + key)
        fid = f.get("family_id")
        if fid in seen:
            errors.append("duplicate_family_id:" + str(fid))
        if isinstance(fid, str):
            seen.add(fid)

    rules = s.get("no_trade_rules")
    if not isinstance(rules, list) or len(rules) < 5:
        errors.append("no_trade_rules_incomplete")
    elif not any("never_orders" in r for r in rules):
        errors.append("never_orders_rule_missing")

    src = s.get("data_source_requirements") or {}
    if src.get("fetched_by_this_contract") is not False:
        errors.append("contract_claims_to_fetch")
    if not (src.get("forbidden") or []):
        errors.append("no_forbidden_sources_listed")

    gates = s.get("safety_gates_before_scanner")
    if not isinstance(gates, list) or len(gates) < 6:
        errors.append("safety_gates_incomplete")

    roadmap = s.get("future_blocks_roadmap")
    if not isinstance(roadmap, list) or len(roadmap) < 6:
        errors.append("roadmap_incomplete")

    # Lane constitution invariants.
    if s.get("alerts_and_reports_only") is not True:
        errors.append("lane_not_alerts_only")
    if s.get("execution_capability_exists") is not False:
        errors.append("execution_capability_claimed")
    if s.get("scanner_exists") is not False:
        errors.append("scanner_claimed_to_exist")
    if s.get("modifies_crypto_d1_lane") is not False:
        errors.append("crypto_d1_lane_touched")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if s.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "fetches_data",
        "calls_api",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "contains_order_logic",
        "authorizes_paper_execution",
        "authorizes_micro_live",
        "authorizes_live_trading",
        "promotes_gate",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_arbitrage_factory_v1_readiness_markdown(spec: Any) -> str:
    """Render a readiness spec as deterministic markdown. Pure string work."""
    s = spec if isinstance(spec, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Arbitrage Factory V1 Research Readiness (SPEC ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(s.get("verdict", "")))
    lines.append("- Lane: " + str(s.get("lane", "")))
    lines.append("- Alerts and reports only: " + str(s.get("alerts_and_reports_only", "")))
    lines.append("- Execution capability exists: "
                 + str(s.get("execution_capability_exists", "")))
    lines.append("- Scanner exists: " + str(s.get("scanner_exists", "")))
    lines.append("- Modifies Crypto-D1 lane: " + str(s.get("modifies_crypto_d1_lane", "")))
    lines.append("- Next required action: " + str(s.get("next_required_action", "")))
    lines.append("")
    lines.append("## Candidate arbitrage families (research only)")
    for f in s.get("candidate_arbitrage_families") or []:
        lines.append("### " + str(f.get("family_id")))
        lines.append("- " + str(f.get("description")))
        lines.append("- Question: " + str(f.get("research_question")))
        lines.append("- Data needs: " + ", ".join(f.get("data_needs") or []))
    lines.append("")
    lines.append("## No-trade rules (the lane's constitution)")
    for r in s.get("no_trade_rules") or []:
        lines.append("- " + str(r))
    lines.append("")
    lines.append("## Data/source requirements (defined, never fetched here)")
    src = s.get("data_source_requirements") or {}
    lines.append("- Fetched by this contract: " + str(src.get("fetched_by_this_contract")))
    for a in src.get("allowed_source_classes") or []:
        lines.append("  - allowed: " + str(a))
    for fbd in src.get("forbidden") or []:
        lines.append("  - forbidden: " + str(fbd))
    lines.append("")
    lines.append("## Safety gates before any scanner")
    for g in s.get("safety_gates_before_scanner") or []:
        lines.append("- " + str(g.get("gate_id")) + ": " + str(g.get("requirement")))
    lines.append("")
    lines.append("## Future blocks roadmap (binding sequence)")
    for b in s.get("future_blocks_roadmap") or []:
        lines.append("- " + str(b.get("seq")) + ". " + str(b.get("block"))
                     + " -- " + str(b.get("purpose")))
    lines.append("")
    lines.append("## Risk notes")
    for note in s.get("risk_notes") or ["(none)"]:
        lines.append("- " + str(note))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- execution: absent by construction (alerts and reports only)")
    return "\n".join(lines)
