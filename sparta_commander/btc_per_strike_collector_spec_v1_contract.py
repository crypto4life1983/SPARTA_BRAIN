"""BTC-only Deribit PER-STRIKE forward-collector SPEC v1 -- PURE, RESEARCH ONLY, SPEC ONLY.

A committable, anti-tamper SPEC for the VRP Phase-2 BTC per-strike forward collector. It is
DESIGN ONLY: it encodes the Phase-1 grounding, the v1-vs-v2 collector relationship, the required
v2 fields, the storage/safety rules, the human gates, and the tail-risk caveats. It implements
NO collector, runs NOTHING, makes NO external API call, fetches NO data, buys NO data, runs NO
replay/backtest/optimization, does NO paper/live, promotes NO candidate, changes NO scheduled
task, and commits NO data. Every future action is explicitly human-gated; every capability flag
is pinned False.
"""
from __future__ import annotations

from typing import Any

SPEC_SCHEMA_VERSION = 1
SPEC_MODE = "RESEARCH_ONLY"
RECORD_ID = "BTC_DERIBIT_PER_STRIKE_FORWARD_COLLECTOR_SPEC_V1"
VERDICT = "BTC_PER_STRIKE_COLLECTOR_SPEC_FROZEN_DESIGN_ONLY"

CURRENCY = "BTC"   # BTC-only

# --- (1) Phase-1 grounding (verified, commit 6daac546) ----------------------
PHASE1_EVIDENCE_COMMIT = "6daac546f95f7f78022823e7616b70febcaa1953"
PHASE1_GROUNDING = {
    "btc_avg_spread_30d": 8.8, "btc_hit_rate_30d": 0.727,
    "btc_ex_2021_avg": 7.2, "btc_2024_2026_avg": 5.4,
    "eth_avg_spread_30d": 4.7, "eth_2024_2026_avg": 0.5, "eth_positive_but_fading": True,
    "combined_avg_spread_30d": 6.8, "combined_hit_rate_30d": 0.688,
    "btc_worst_day_spread": -45.2, "eth_worst_day_spread": -111.6,
    "yen_carry_2024_08_near_break_even": True,
    "is_index_level_proxy_not_tradeable": True,
}

# --- (2) existing collector relationship ------------------------------------
EXISTING_V1_TOOL = "tools/fetch_deribit_btc_option_chain_snapshot_once.py"
V1_RELATIONSHIP = {
    "v1_captures": ["instrument_name", "strike", "option_type", "expiration_timestamp",
                    "mark_iv", "mark_price", "underlying_index_price", "open_interest", "volume"],
    "v1_lacks_bid_ask": True,
    "v1_lacks_greeks": True,
    "v2_is_strict_superset": True,
    "v2_supersedes_v1_only_after_separate_human_approval": True,
    "v2_is_not_a_code_wrapper_of_v1": True,
    "this_spec_changes_no_scheduled_task": True,
}

# --- (3) required v2 per-strike fields ---------------------------------------
REQUIRED_V2_FIELDS = (
    "instrument_name", "timestamp", "expiration_timestamp", "tenor_days", "strike",
    "option_type", "bid", "ask", "mark_price", "mark_iv",
    "delta", "gamma", "vega", "theta",                       # "if available"
    "open_interest", "volume", "underlying_index_price", "atm_proximity", "tenor_30d_tag",
)
GREEKS_REQUIRED = ("delta", "gamma", "vega", "theta")
NEW_FIELDS_VS_V1 = ("bid", "ask", "delta", "gamma", "vega", "theta", "tenor_days",
                    "atm_proximity", "tenor_30d_tag")

# allowed PUBLIC endpoints only (no /private/, no auth/account/order/trade)
ALLOWED_PUBLIC_ENDPOINTS = (
    "https://www.deribit.com/api/v2/public/get_instruments",
    "https://www.deribit.com/api/v2/public/get_book_summary_by_currency",
    "https://www.deribit.com/api/v2/public/ticker",
)
FORBIDDEN_ENDPOINT_FRAGMENTS = ("/private/", "account", "order", "trade", "buy", "sell",
                                "subaccount", "withdraw", "apikey", "signature")

# --- (4) storage + safety ---------------------------------------------------
STORAGE = {
    "data_root": "data/deribit_options_chain_universe/",
    "v2_snapshots_dir": "data/deribit_options_chain_universe/snapshots_v2/",
    "snapshot_naming": "snapshots_v2/<YYYY-MM-DD>/btc_per_strike_<YYYY-MM-DD>.csv",
    "immutable_one_snapshot_per_utc_date": True,
    "duplicate_snapshot_behavior": "NO_OVERWRITE__REPORT_DUPLICATE_SNAPSHOT",
    "manifest_required": True,
    "quality_report_required": True,
    "no_forward_fill": True,
    "no_clip_no_smooth": True,
    "data_is_gitignored_local_only": True,
    "no_data_file_tracked_by_git": True,
}

# --- (5) human gates (each separate; NONE authorized by this spec) -----------
HUMAN_GATES = (
    {"step": "build_collector",
     "token": "HUMAN_APPROVED_BUILD_BTC_DERIBIT_PER_STRIKE_FORWARD_COLLECTOR_AND_TESTS_ONLY",
     "authorized_now": False},
    {"step": "run_or_schedule_collector",
     "token": "HUMAN_APPROVED_RUN_OR_SCHEDULE_BTC_PER_STRIKE_COLLECTOR_ONLY",
     "authorized_now": False},
    {"step": "retire_v1_00_20_task",
     "token": "HUMAN_APPROVED_RETIRE_V1_DERIBIT_00_20_SNAPSHOT_TASK_ONLY",
     "authorized_now": False},
    {"step": "paid_historical_data",
     "token": "HUMAN_DECISION_PROCURE_PAID_BTC_PER_STRIKE_HISTORY_TARDIS_ONLY",
     "authorized_now": False},
    {"step": "phase2_replay_backtest",
     "token": "HUMAN_APPROVED_RUN_BTC_DELTA_HEDGED_VRP_BACKTEST_FROM_FROZEN_PER_STRIKE_ONLY",
     "authorized_now": False},
    {"step": "paper_trading", "token": "SEPARATE_EXPLICIT_GATE", "authorized_now": False},
    {"step": "live_trading", "token": "SEPARATE_EXPLICIT_GATE", "authorized_now": False},
)

# --- (6) tail-risk caveats --------------------------------------------------
TAIL_RISK_CAVEATS = (
    "index-level VRP (Phase-1 DVOL vs realized) is NOT tradeable P&L",
    "bid/ask AND greeks are REQUIRED before tradability can even be tested",
    "short-vol tail risk is the CENTRAL danger (worst day BTC -45.2 / ETH -111.6; 2024-08 near "
    "break-even)",
    "NAKED short-vol is FORBIDDEN",
    "any future strategy MUST be delta-hedged, size-capped, and crash-stress-gated",
)

_CAPABILITY_FLAGS_FALSE = (
    "implements_collector", "runs_collector", "schedules_collector", "changes_scheduled_task",
    "retires_v1_task", "makes_external_api_call", "fetches_data", "buys_data", "writes_data",
    "writes_files", "runs_replay", "runs_backtest", "optimizes_parameters", "paper_trading",
    "live_trading", "sells_options", "authorizes_naked_short_vol", "promotes_any_candidate",
    "activates_any_candidate", "commits_data", "uses_private_endpoints", "uses_credentials",
    "advances_c22", "reactivates_c23_c24", "modifies_official_ledger", "modifies_lifecycle",
    "authorizes_any_future_step", "crosses_into_forbidden_gate",
)


def get_spec_label() -> str:
    return (
        "BTC-only Deribit per-strike forward-collector SPEC v1 (READ-ONLY, RESEARCH ONLY, SPEC "
        "ONLY). Grounded in verified Phase-1 VRP evidence (commit 6daac546: BTC avg +8.8 / hit "
        "72.7%% / ex-2021 +7.2 / 2024-2026 +5.4; ETH positive-but-fading; combined +6.8 / 68.8%%; "
        "worst BTC -45.2 / ETH -111.6). v2 is a STRICT SUPERSET of the existing v1 00:20 "
        "collector (adds bid/ask + greeks), superseding it ONLY after separate human approval. "
        "Implements/runs NOTHING; every future step is human-gated; naked short-vol is "
        "FORBIDDEN. NOT a tradability or profitability claim.")


def build_spec() -> dict[str, Any]:
    """Assemble the frozen BTC per-strike collector spec. Pure; no I/O; spec only."""
    blockers: list = []
    if len(PHASE1_EVIDENCE_COMMIT) != 40:
        blockers.append("phase1_commit_not_sha")
    if CURRENCY != "BTC":
        blockers.append("not_btc_only")
    for g in GREEKS_REQUIRED + ("bid", "ask"):
        if g not in REQUIRED_V2_FIELDS:
            blockers.append("missing_required_field:%s" % g)
    for e in ALLOWED_PUBLIC_ENDPOINTS:
        if "/private/" in e or not e.startswith("https://www.deribit.com/api/v2/public/"):
            blockers.append("non_public_endpoint:%s" % e)

    record: dict[str, Any] = {
        "schema_version": SPEC_SCHEMA_VERSION, "mode": SPEC_MODE,
        "record_id": RECORD_ID, "label": get_spec_label(),
        "is_spec_only": True, "currency": CURRENCY, "blockers": blockers,
        "verdict": (VERDICT if not blockers else "BTC_PER_STRIKE_SPEC_BLOCKED"),
        # (1) grounding
        "phase1_evidence_commit": PHASE1_EVIDENCE_COMMIT,
        "phase1_grounding": dict(PHASE1_GROUNDING),
        # (2) relationship
        "existing_v1_tool": EXISTING_V1_TOOL,
        "v1_relationship": {k: (list(v) if isinstance(v, list) else v)
                            for k, v in V1_RELATIONSHIP.items()},
        # (3) fields
        "required_v2_fields": list(REQUIRED_V2_FIELDS),
        "greeks_required": list(GREEKS_REQUIRED),
        "new_fields_vs_v1": list(NEW_FIELDS_VS_V1),
        "v2_requires_bid_ask": ("bid" in REQUIRED_V2_FIELDS and "ask" in REQUIRED_V2_FIELDS),
        "v2_requires_greeks": all(g in REQUIRED_V2_FIELDS for g in GREEKS_REQUIRED),
        "allowed_public_endpoints": list(ALLOWED_PUBLIC_ENDPOINTS),
        "forbidden_endpoint_fragments": list(FORBIDDEN_ENDPOINT_FRAGMENTS),
        "uses_only_public_endpoints": True,
        # (4) storage/safety
        "storage": dict(STORAGE),
        # (5) gates
        "human_gates": [dict(g) for g in HUMAN_GATES],
        "all_future_actions_human_gated": all(not g["authorized_now"] for g in HUMAN_GATES),
        "v1_retirement_authorized_by_this_spec": False,
        # (6) caveats
        "tail_risk_caveats": list(TAIL_RISK_CAVEATS),
        "naked_short_vol_forbidden": True,
        "index_level_not_tradeable": True,
        "is_tradability_claim": False, "is_profitability_claim": False,
        # preservation
        "implements_no_collector": True, "runs_nothing": True, "fetches_nothing": True,
        "changes_no_scheduled_task": True, "commits_no_data": True,
        "advances_c22": False, "reactivates_c23_c24": False,
        "human_review_required": True,
        "next_required_action": HUMAN_GATES[0]["token"],
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_implement_collector": True, "no_run_collector": True, "no_schedule_change": True,
        "no_retire_v1": True, "no_external_api_call": True, "no_fetch": True, "no_buy_data": True,
        "no_write_data": True, "no_replay": True, "no_backtest": True, "no_optimization": True,
        "no_paper_trading": True, "no_live_trading": True, "no_naked_short_vol": True,
        "no_promote_candidate": True, "no_advance_c22": True, "no_reactivate_c23_c24": True,
        "no_commit_data": True, "no_private_endpoints": True, "no_credentials": True,
        "no_modify_ledger": True, "no_authorize_future_step": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, spec-only, BTC-only; uses ONLY
    public Deribit endpoints (no /private/); v2 requires bid/ask + all four greeks and is a
    strict superset of v1; storage is gitignored/immutable with no-overwrite duplicate handling;
    EVERY future step is human-gated (authorized_now False) and v1 retirement is NOT authorized
    here; naked short-vol is forbidden and index-level is flagged not-tradeable; nothing is
    implemented/run/fetched/committed; and every capability flag is False."""
    f: list = []
    if record.get("mode") != SPEC_MODE:
        f.append("mode_not_research_only")
    if record.get("is_spec_only") is not True:
        f.append("not_spec_only")
    if record.get("blockers"):
        f.append("has_blockers")
    if record.get("verdict") != VERDICT:
        f.append("verdict_wrong")
    if record.get("currency") != "BTC":
        f.append("not_btc_only")

    # grounding pinned
    g = record.get("phase1_grounding") or {}
    if record.get("phase1_evidence_commit") != PHASE1_EVIDENCE_COMMIT:
        f.append("phase1_commit_tampered")
    for k, v in (("btc_avg_spread_30d", 8.8), ("btc_hit_rate_30d", 0.727),
                 ("combined_avg_spread_30d", 6.8), ("btc_worst_day_spread", -45.2),
                 ("eth_worst_day_spread", -111.6)):
        if g.get(k) != v:
            f.append("grounding_tampered:%s" % k)
    if g.get("eth_positive_but_fading") is not True:
        f.append("eth_fading_flag_off")
    if g.get("is_index_level_proxy_not_tradeable") is not True:
        f.append("must_flag_index_level_not_tradeable")

    # public endpoints only
    for e in (record.get("allowed_public_endpoints") or []):
        if "/private/" in str(e) or not str(e).startswith(
                "https://www.deribit.com/api/v2/public/"):
            f.append("non_public_endpoint:%s" % e)
    if record.get("uses_only_public_endpoints") is not True:
        f.append("must_be_public_only")

    # v2 superset: bid/ask + greeks required; v1 lacks them
    if record.get("v2_requires_bid_ask") is not True:
        f.append("v2_must_require_bid_ask")
    if record.get("v2_requires_greeks") is not True:
        f.append("v2_must_require_greeks")
    rel = record.get("v1_relationship") or {}
    if rel.get("v1_lacks_bid_ask") is not True or rel.get("v1_lacks_greeks") is not True:
        f.append("v1_lacks_must_be_true")
    if rel.get("v2_is_strict_superset") is not True:
        f.append("v2_not_superset")
    if rel.get("v2_supersedes_v1_only_after_separate_human_approval") is not True:
        f.append("supersede_must_be_gated")

    # storage immutable/gitignored/no-overwrite
    st = record.get("storage") or {}
    if not str(st.get("v2_snapshots_dir", "")).startswith(
            "data/deribit_options_chain_universe/snapshots_v2"):
        f.append("v2_storage_path_wrong")
    if st.get("immutable_one_snapshot_per_utc_date") is not True:
        f.append("storage_not_immutable")
    if st.get("duplicate_snapshot_behavior") != "NO_OVERWRITE__REPORT_DUPLICATE_SNAPSHOT":
        f.append("duplicate_overwrite_allowed")
    if st.get("data_is_gitignored_local_only") is not True or st.get(
            "no_data_file_tracked_by_git") is not True:
        f.append("data_not_gitignored_local")
    if not st.get("manifest_required") or not st.get("quality_report_required"):
        f.append("manifest_or_quality_not_required")

    # all gates present, none authorized; v1 retirement not authorized here
    gates = record.get("human_gates") or []
    gate_steps = {x.get("step") for x in gates}
    for req in ("build_collector", "run_or_schedule_collector", "retire_v1_00_20_task",
                "paid_historical_data", "phase2_replay_backtest", "paper_trading",
                "live_trading"):
        if req not in gate_steps:
            f.append("gate_missing:%s" % req)
    if any(x.get("authorized_now") is not False for x in gates):
        f.append("a_gate_is_authorized_now")
    if record.get("all_future_actions_human_gated") is not True:
        f.append("future_actions_not_all_gated")
    if record.get("v1_retirement_authorized_by_this_spec") is not False:
        f.append("v1_retirement_must_not_be_authorized")

    # tail-risk caveats
    if len(record.get("tail_risk_caveats") or []) < 4:
        f.append("tail_caveats_incomplete")
    if record.get("naked_short_vol_forbidden") is not True:
        f.append("naked_short_vol_must_be_forbidden")
    if record.get("index_level_not_tradeable") is not True:
        f.append("index_level_not_flagged")
    if record.get("is_tradability_claim") is not False or record.get(
            "is_profitability_claim") is not False:
        f.append("must_not_claim_tradable_or_profitable")

    # implements/runs/fetches nothing
    for k in ("implements_no_collector", "runs_nothing", "fetches_nothing",
              "changes_no_scheduled_task", "commits_no_data"):
        if record.get(k) is not True:
            f.append("preservation_off_%s" % k)
    if record.get("advances_c22") is not False or record.get("reactivates_c23_c24") is not False:
        f.append("must_not_advance_or_reactivate")

    locks = record.get("scope_locks") or {}
    for key in ("no_implement_collector", "no_run_collector", "no_schedule_change",
                "no_retire_v1", "no_external_api_call", "no_fetch", "no_buy_data",
                "no_write_data", "no_replay", "no_backtest", "no_optimization",
                "no_paper_trading", "no_live_trading", "no_naked_short_vol",
                "no_promote_candidate", "no_advance_c22", "no_commit_data",
                "no_private_endpoints", "no_authorize_future_step"):
        if locks.get(key) is not True:
            f.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            f.append("capability_flag_true_%s" % flag)

    return {"valid": not f, "failures": f}
