"""Candidate #18 -- h4_trend_following_market_structure_v1 -- DATA READINESS /
FETCH-APPROVAL CONTRACT (PURE, RESEARCH ONLY).

The C18 real-candle labels stage needs frozen local H4 BTCUSD OHLC data. A read-only
local discovery found that NO frozen H4 BTCUSD OHLC exists: the local crypto data is
DAILY (data/crypto_d1_spot, interval 1d), and the only intraday crypto present is a
handful of short 15m/1m NY-session windows under data/ny_fvg_choch -- not H4, not the
C18 window. So the labels stage CANNOT proceed yet.

The repo already has a SAFE public crypto OHLC fetch convention
(tools/fetch_binance_crypto_daily_frozen.py): public Binance klines only, NO API key,
NO signed/account/trade endpoints, deterministic, writes a SHA-frozen CSV, and is
AST/source safety-tested. BUT that convention is HARD-LOCKED to interval 1d -- it
cannot fetch H4 as-is, and there is NO committed approval for an H4 BTCUSD fetch. So
this contract does NOT fetch. It RECORDS exactly what is missing and DECLARES the
safety requirements + the human approval token a future H4 fetch must satisfy, and
STOPS before any network call.

It performs NO network access, NO fetch, NO credentials, NO XAUUSD, NO labels, NO
replay, NO optimization, NO paper/live/broker/order surface. It is chain-gated on the
committed C18 detector dry-run. Every capability flag is pinned False with a full
scope_locks set. Approving an H4 fetch needs an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.h4_trend_following_market_structure_v1_detector_spec_dry_run_contract as _d18  # noqa: E501

DR18_SCHEMA_VERSION = 1
DR18_MODE = "RESEARCH_ONLY"
DR18_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _d18.CANDIDATE_ID
CANDIDATE_FAMILY = _d18.CANDIDATE_FAMILY
CANDIDATE_NAME = _d18.CANDIDATE_NAME

REQUIRED_TIMEFRAME = "H4"
REQUIRED_SYMBOL = "BTCUSD"
REQUIRED_COLUMNS = ("date", "open", "high", "low", "close", "volume")
# a multi-year window so trend-following has structure + a forward-OOS tail
REQUIRED_MIN_HISTORY_DAYS = 1095          # ~3 years of H4 bars

# read-only local discovery result (no H4 OHLC found)
FROZEN_LOCAL_H4_BTCUSD_EXISTS = False
LOCAL_CRYPTO_DATA_FOUND = {
    "data/crypto_d1_spot/raw/BTC_1d.csv": "DAILY (1d) BTCUSD spot -- wrong timeframe",
    "data/crypto_d1_spot/raw/ETH_1d.csv": "DAILY (1d) ETHUSD spot -- wrong timeframe",
    "data/crypto_d1_spot/raw/SOL_1d.csv": "DAILY (1d) SOLUSD spot -- wrong timeframe",
    "data/ny_fvg_choch/staged/BTCUSD_15m_*.csv": "short 15m NY windows -- not H4",
}
MISSING_DATA = {
    "symbol": REQUIRED_SYMBOL, "timeframe": REQUIRED_TIMEFRAME,
    "columns": list(REQUIRED_COLUMNS),
    "min_history_days": REQUIRED_MIN_HISTORY_DAYS,
    "reason": "no frozen local H4 BTCUSD OHLC with SHA provenance exists",
}

# the existing SAFE public fetch convention (daily-only; cannot do H4 as-is)
EXISTING_SAFE_CONVENTION = {
    "tool": "tools/fetch_binance_crypto_daily_frozen.py",
    "public_market_data_only": True,
    "no_api_key": True,
    "no_signed_or_account_or_trade_endpoints": True,
    "deterministic": True,
    "sha_frozen_output": True,
    "ast_and_source_safety_tested": True,
    "interval_locked_to": "1d",
    "covers_h4": False,
    "reusable_for_h4_as_is": False,        # interval hard-locked to 1d
}

# the safety requirements any approved H4 fetch MUST satisfy (declared, not executed)
PROPOSED_FETCH_SAFETY_REQUIREMENTS = (
    "public market data only (Binance public klines); NO API key / NO credentials",
    "NO signed / account / order / trade / userdata endpoints",
    "interval restricted to 4h; symbol restricted to BTCUSDT (BTCUSD)",
    "deterministic + writes a SHA-frozen CSV with provenance (sha256, row_count)",
    "read-only: reads no env/secrets, places no orders, no broker/exchange SDK",
    "no XAUUSD / no gold; crypto H4 BTCUSD only",
    "executed by a one-off runner only on explicit human approval; stop before any "
    "network call until then",
)
PROPOSED_FETCH_APPROVAL_TOKEN = (
    "APPROVE_C18_H4_BTCUSD_PUBLIC_READONLY_FETCH")

NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_APPROVE_C18_H4_BTCUSD_PUBLIC_READONLY_FETCH_OR_REJECT")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "fetches_data", "uses_network", "calls_api",
    "uses_credentials", "reads_env_or_secrets", "connects_broker",
    "connects_exchange", "uses_xauusd", "runs_detector", "runs_labels",
    "runs_replay", "runs_backtest", "computes_pnl", "optimizes_parameters",
    "reparameterizes", "reads_real_data", "mutates_data", "stages_data",
    "auto_commits", "auto_pushes", "places_orders", "contains_order_logic",
    "paper_trading", "live_trading", "deploys_capital", "approves_fetch_itself",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def get_c18_data_readiness_label() -> str:
    return (
        "Candidate #18 h4_trend_following_market_structure_v1 data readiness / "
        "fetch-approval (READ-ONLY, RESEARCH ONLY, PURE). NO frozen local H4 BTCUSD "
        "OHLC exists (local crypto data is DAILY). This contract RECORDS the missing "
        "data and DECLARES the safety requirements + human approval token a future "
        "public, no-credential, deterministic, SHA-frozen H4 fetch must satisfy. It "
        "FETCHES NOTHING and stops before any network call. NOT a profitability "
        "claim.")


def get_c18_data_readiness_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c18_data_readiness(repo_root: Any = ".",
                             tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C18 data-readiness / fetch-approval record. Pure; no I/O;
    chain-gated on the frozen C18 detector dry-run. Fetches nothing."""
    dry = _d18.build_c18_detector_dry_run(repo_root, tracked_paths)
    dry_valid = _d18.validate_c18_detector_dry_run(dry)["valid"]

    blockers: list = []
    if not dry_valid:
        blockers.append("c18_detector_dry_run_invalid")
    if dry.get("verdict") != "C18_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c18_detector_dry_run_not_frozen")

    record: dict[str, Any] = {
        "schema_version": DR18_SCHEMA_VERSION, "mode": DR18_MODE, "lane": DR18_LANE,
        "label": get_c18_data_readiness_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_data_readiness_only": True,
        "blockers": blockers,
        "verdict": ("C18_DATA_READINESS_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C18_DATA_READINESS_BLOCKED"),
        # chain provenance
        "detector_dry_run_verdict": dry.get("verdict"),
        "detector_dry_run_valid": dry_valid,
        # read-only discovery result
        "frozen_local_h4_btcusd_exists": FROZEN_LOCAL_H4_BTCUSD_EXISTS,
        "labels_can_proceed_now": FROZEN_LOCAL_H4_BTCUSD_EXISTS,
        "local_crypto_data_found": dict(LOCAL_CRYPTO_DATA_FOUND),
        "missing_data": dict(MISSING_DATA),
        "required_timeframe": REQUIRED_TIMEFRAME, "required_symbol": REQUIRED_SYMBOL,
        # the existing safe convention + why it can't do H4 as-is
        "existing_safe_fetch_convention": dict(EXISTING_SAFE_CONVENTION),
        "approved_h4_fetch_convention_exists": False,
        "reuses_existing_convention_for_h4": False,
        # the proposed (declared, NOT executed) safe fetch + approval token
        "proposed_fetch_safety_requirements":
            list(PROPOSED_FETCH_SAFETY_REQUIREMENTS),
        "proposed_fetch_approval_token": PROPOSED_FETCH_APPROVAL_TOKEN,
        "no_fetch_performed_here": True,
        "no_network_call_here": True,
        "no_credentials_used": True,
        "stops_before_any_network_fetch": True,
        "fetch_requires_explicit_human_approval": True,
        # XAUUSD stays out of scope
        "xauusd_in_scope": False,
        "human_review_required": True,
        "current_loop_stage": "data_readiness",
        "next_required_action": NEXT_REQUIRED_ACTION,
        # downstream gates locked
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_write": True, "no_network": True, "no_fetch": True,
        "no_credentials": True, "no_env_or_secret_read": True, "no_api_call": True,
        "no_broker": True, "no_exchange": True, "no_xauusd": True, "no_labels": True,
        "no_replay": True, "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_reparameterization": True, "no_real_data_mutation": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_self_fetch_approval": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c18_data_readiness(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only,
    data-readiness-only, chain-gated on the frozen C18 detector dry-run, HONESTLY
    records that no frozen local H4 BTCUSD data exists (labels cannot proceed),
    declares the safety requirements + human approval token a future public,
    no-credential, deterministic, SHA-frozen H4 fetch must satisfy, performs NO
    fetch / network / credential use, keeps XAUUSD out of scope and downstream gates
    locked, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != DR18_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_data_readiness_only") is not True:
        failures.append("not_data_readiness_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C18_DATA_READINESS_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("detector_dry_run_valid") is not True:
        failures.append("detector_dry_run_not_valid")
    if record.get("detector_dry_run_verdict") != (
            "C18_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"):
        failures.append("detector_dry_run_not_frozen")

    # HONEST discovery: no H4 data -> labels cannot proceed
    if record.get("frozen_local_h4_btcusd_exists") is not False:
        failures.append("h4_data_existence_misreported")
    if record.get("labels_can_proceed_now") is not False:
        failures.append("labels_must_not_proceed_without_data")
    md = record.get("missing_data") or {}
    if md.get("symbol") != "BTCUSD" or md.get("timeframe") != "H4":
        failures.append("missing_data_spec_wrong")

    # the existing convention is acknowledged but NOT reusable for H4 as-is
    conv = record.get("existing_safe_fetch_convention") or {}
    if conv.get("interval_locked_to") != "1d":
        failures.append("convention_interval_misreported")
    if conv.get("covers_h4") is not False:
        failures.append("convention_must_not_cover_h4")
    if record.get("approved_h4_fetch_convention_exists") is not False:
        failures.append("must_not_claim_approved_h4_convention")
    if record.get("reuses_existing_convention_for_h4") is not False:
        failures.append("must_not_reuse_daily_convention_for_h4")

    # proposed fetch is DECLARED, safety-bounded, and NOT executed
    reqs = " || ".join(record.get("proposed_fetch_safety_requirements") or []).lower()
    for must in ("public market data only", "no api key", "no signed",
                 "deterministic", "sha-frozen", "no xauusd"):
        if must not in reqs:
            failures.append("fetch_requirement_missing_%s" % must.split()[0])
    if not record.get("proposed_fetch_approval_token"):
        failures.append("approval_token_missing")
    if record.get("no_fetch_performed_here") is not True:
        failures.append("fetch_must_not_be_performed")
    if record.get("no_network_call_here") is not True:
        failures.append("network_must_not_be_called")
    if record.get("no_credentials_used") is not True:
        failures.append("credentials_must_not_be_used")
    if record.get("stops_before_any_network_fetch") is not True:
        failures.append("must_stop_before_network")
    if record.get("fetch_requires_explicit_human_approval") is not True:
        failures.append("fetch_not_human_gated")
    if record.get("xauusd_in_scope") is not False:
        failures.append("xauusd_must_be_out_of_scope")
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_action_not_fetch_approval")

    # downstream gates locked
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_network", "no_fetch", "no_credentials",
                "no_api_call", "no_broker", "no_xauusd", "no_labels", "no_replay",
                "no_pnl", "no_optimization", "no_commit", "no_push",
                "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_self_fetch_approval", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
