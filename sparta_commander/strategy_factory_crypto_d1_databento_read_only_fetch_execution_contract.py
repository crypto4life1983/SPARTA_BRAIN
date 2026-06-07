"""Crypto-D1 Databento Read-Only Fetch Execution Contract (Block 142).

A PURE, stdlib-only, *read-only* CONTRACT / SPEC layer. It defines and guards the
execution boundary for a future, human-approved, READ-ONLY Databento historical
market-data fetch of the three missing Crypto-D1 daily pairs (BTCUSD@1d,
ETHUSD@1d, SOLUSD@1d) that Block 140 confirmed absent and Block 141 planned. It is
the document and gate a future RUNNER would consult before fetching.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

THIS contract executes NOTHING. It does NOT call Databento, open a network, fetch
or download data, inspect or read any credential, read a .env file, print / store
/ log any secret, read or write any data file, write a manifest / gap report, run
QA, run a backtest, open a file, spawn a subprocess, read an environment variable,
mint an id, or record a timestamp. It only reasons over a static, caller-supplied
summary and emits a deterministic permission DECISION for a future runner.

FETCH PERMISSION MODEL (the new boundary this block defines):
  - Fetch is DISABLED by default.
  - A future, separate RUNNER would be permitted to perform a READ-ONLY Databento
    historical fetch ONLY when an explicit human-run approval flag
    (`human_run_approved`) is supplied AND every pre-fetch check passes AND the
    request stays inside the approved scope (symbols / timeframe / provider /
    destination). Even then, THIS contract still performs no fetch; it only
    reports `fetch_permitted_for_future_runner = True`.
  - Granting fetch permission NEVER unlocks Real Data QA, baseline, or paper /
    live. Acquiring read-only market data is not QA and not trading.

APPROVED FUTURE FETCH SCOPE (and nothing else):
  - Provider : Databento HISTORICAL market data only (no exchange / broker /
    account / trading endpoint).
  - Symbols  : BTCUSD, ETHUSD, SOLUSD only.
  - Timeframe: 1d only.
  - Destination: data/databento_cache/crypto_d1/ only.
  - Optional later report dir: reports/research_os/data_qa/ only.

STRICTLY FORBIDDEN, always (this contract never enables any of these):
  exchange trading API, broker API, account / portfolio access, order placement,
  paper / live trading, Telegram trade command, TradingView execution webhook,
  strategy promotion, baseline / backtest / QA execution, runtime / dashboard
  writes, secret printing, credential logging, .env content printing, writing
  outside the approved data / report paths, any gate unlock.

CORE RULE: this contract NEVER unlocks Real Data QA and NEVER crosses any
real-world boundary by itself. Building / evaluating it authorizes nothing.
real_data_qa stays BLOCKED, baseline stays BLOCKED, paper / micro-live stay LOCKED.

Public API:
  - FETCH_SCHEMA_VERSION / FETCH_LABEL / FETCH_STATUS / FETCH_MODE / FETCH_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - FETCH_APPROVED_PAIRS / FETCH_APPROVED_SYMBOLS / FETCH_APPROVED_TIMEFRAMES
  - FETCH_APPROVED_PROVIDER / FETCH_PROVIDER_DETAIL
  - FETCH_APPROVED_DESTINATION / FETCH_APPROVED_REPORT_DIR
  - FETCH_MANIFEST_REPORT_PATH / FETCH_GAP_REPORT_PATH
  - FETCH_HUMAN_RUN_APPROVAL_FLAG
  - FETCH_CREDENTIAL_SAFETY_RULES / FETCH_PRE_FETCH_CHECKS / FETCH_POST_FETCH_CHECKS
  - FETCH_HARD_STOP_CONDITIONS / FETCH_STILL_FORBIDDEN_CAPABILITIES
  - FETCH_FORBIDDEN_TRADE_TERMS
  - FETCH_AUTHORIZATION_FLAGS / FETCH_GATE_LOCK_FLAGS / FETCH_GATE_UNLOCK_REQUEST_FLAGS
  - FETCH_SAFETY_POSTURE / DEFAULT_FETCH_INPUT
  - assess_databento_read_only_fetch_execution(payload)
  - build_crypto_d1_databento_read_only_fetch_execution_contract(payload=None)
  - validate_crypto_d1_databento_read_only_fetch_execution_contract(contract)
  - render_crypto_d1_databento_read_only_fetch_execution_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

FETCH_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract.v1"
)
FETCH_LABEL = (
    "Block 142 - Crypto-D1 Databento Read-Only Fetch Execution Contract"
)
FETCH_STATUS = "READ_ONLY_DATABENTO_FETCH_CONTRACT"
FETCH_MODE = "RESEARCH_ONLY"

FETCH_CORE_RULE = (
    "This contract NEVER unlocks Real Data QA and NEVER crosses any real-world "
    "boundary by itself. It only defines and guards the execution boundary for a "
    "future, human-approved, READ-ONLY Databento historical market-data fetch. "
    "Building or evaluating the contract authorizes nothing: no Databento call is "
    "made, no network is opened, no data is fetched or downloaded, no credential "
    "is inspected, no .env is read, no secret is shown, and no manifest / gap "
    "report is written. Fetch is disabled by default and permitted for a future "
    "runner only with an explicit human-run approval; even then real_data_qa "
    "stays BLOCKED, baseline stays BLOCKED, and paper / micro-live stay LOCKED."
)

# Mission-flow truth this contract is anchored to. The companion test cross-checks
# these against the live status module so they cannot drift.
MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# 1. Approved symbols / timeframes -> the three missing Crypto-D1 daily pairs.
FETCH_APPROVED_PAIRS: tuple[str, ...] = (
    "BTCUSD@1d",
    "ETHUSD@1d",
    "SOLUSD@1d",
)
FETCH_APPROVED_SYMBOLS: tuple[str, ...] = ("BTCUSD", "ETHUSD", "SOLUSD")
FETCH_APPROVED_TIMEFRAMES: tuple[str, ...] = ("1d",)

# 2. Approved provider -> Databento HISTORICAL market data only.
FETCH_APPROVED_PROVIDER = "databento_historical_market_data_read_only"
FETCH_PROVIDER_DETAIL = (
    "Databento historical market-data API: read-only retrieval of historical "
    "daily OHLCV bars for the approved crypto pairs. No exchange endpoint, no "
    "broker endpoint, no trading endpoint, no account endpoint -- historical "
    "market-data retrieval only."
)

# 3. Approved destination path (the ONLY local folder a future fetch may write).
FETCH_APPROVED_DESTINATION = "data/databento_cache/crypto_d1/"

# 4. Approved report dir for a later manifest / gap report.
FETCH_APPROVED_REPORT_DIR = "reports/research_os/data_qa/"
FETCH_MANIFEST_REPORT_PATH = (
    "reports/research_os/data_qa/crypto_d1_databento_manifest.json"
)
FETCH_GAP_REPORT_PATH = (
    "reports/research_os/data_qa/crypto_d1_databento_gap_report.md"
)

# The only paths a future, human-approved, read-only fetch step may change.
FETCH_ALLOWED_LATER_CHANGE_PATHS: tuple[str, ...] = (
    "data/databento_cache/crypto_d1/ (read-only fetch destination; later approved run only)",
    "reports/research_os/data_qa/ (post-fetch manifest / gap report; later approved run only)",
)

# 5. Credential safety rules.
FETCH_HUMAN_RUN_APPROVAL_FLAG = "human_run_approved"
FETCH_CREDENTIAL_SAFETY_RULES: tuple[str, ...] = (
    "A future runner may CHECK PRESENCE of Databento config only, and only after "
    "explicit human-run approval -- presence is a boolean, never a value.",
    "Never print a credential value.",
    "Never store a credential value in the contract, manifest, report, log, or "
    "Git history.",
    "Never log a secret.",
    "Never read or print .env file content.",
    "If any real secret value would be read, printed, or written -> STOP.",
)

# 7. Pre-fetch checks a future runner MUST pass before any read-only fetch.
FETCH_PRE_FETCH_CHECKS: tuple[str, ...] = (
    "Mission flow is at the human-controlled boundary.",
    "Explicit human-run approval flag is present.",
    "Requested symbols are a subset of BTCUSD / ETHUSD / SOLUSD.",
    "Requested timeframe is 1d only.",
    "Requested provider is Databento historical market data (read-only) only.",
    "Requested destination is exactly data/databento_cache/crypto_d1/.",
    "No forbidden authorization / unlock / trading flag is set.",
    "All gates remain locked (real_data_qa / baseline / paper / micro-live).",
    "Databento config presence may be checked as a boolean only; no secret read.",
)

# 8. Post-fetch checks a future runner MUST verify AFTER any read-only fetch.
FETCH_POST_FETCH_CHECKS: tuple[str, ...] = (
    "Files were written only under data/databento_cache/crypto_d1/.",
    "Each written file holds only daily OHLCV bars for an approved pair.",
    "No file holds, and no log shows, any credential or secret value.",
    "A manifest was written only under reports/research_os/data_qa/ recording "
    "pair, row count, and date range.",
    "A gap report under reports/research_os/data_qa/ records any missing date "
    "ranges.",
    "No exchange / broker / account / trading endpoint was touched.",
    "real_data_qa, baseline_backtest, paper, and micro-live remain BLOCKED / "
    "LOCKED -- the fetch unlocked no gate.",
    "No runtime or dashboard output was written.",
)

# 9. Hard-stop conditions: if ANY would be true, the future runner must STOP.
FETCH_HARD_STOP_CONDITIONS: tuple[str, ...] = (
    "Explicit human-run approval is absent -> STOP (fetch disabled by default).",
    "Any real credential value would be read, printed, or written -> STOP.",
    "Any .env file content would be read or printed -> STOP.",
    "Any exchange / broker / account / portfolio / trading endpoint would be "
    "touched -> STOP.",
    "Any non-Databento or non-historical-market-data endpoint would be called "
    "-> STOP.",
    "Any symbol outside BTCUSD / ETHUSD / SOLUSD or timeframe other than 1d "
    "would be requested -> STOP.",
    "Any write outside data/databento_cache/crypto_d1/ or "
    "reports/research_os/data_qa/ would occur -> STOP.",
    "Any paper / live trading, strategy promotion, or QA / baseline / backtest "
    "would run -> STOP.",
    "real_data_qa, baseline_backtest, paper, or micro-live would be unlocked "
    "-> STOP.",
    "Mission flow is no longer at the human-controlled boundary -> STOP.",
)

# Capabilities that stay FORBIDDEN, always. Listed as a signature of what remains
# blocked; the contract never enables any of them.
FETCH_STILL_FORBIDDEN_CAPABILITIES: tuple[str, ...] = (
    "exchange_trading_api",
    "broker_api",
    "account_access",
    "portfolio_access",
    "order_placement",
    "paper_trading",
    "live_trading",
    "telegram_trade_command",
    "tradingview_execution_webhook",
    "strategy_promotion",
    "baseline_backtest_qa_execution",
    "runtime_dashboard_writes",
    "secret_printing",
    "credential_logging",
    "dotenv_content_printing",
    "writing_outside_approved_paths",
    "gate_unlock",
)

# Execution / promotion verbs the authored NARRATIVE must never contain as whole
# words. (The forbidden-capability list above intentionally names some signature
# literals and is excluded from the narrative scan.)
FETCH_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Top-level flags that, if truthy, force a refusing (unsafe) verdict.
FETCH_AUTHORIZATION_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "authorizes_qa_baseline",
    "unlocks_downstream_gate",
    "print_credentials",
    "expose_secret",
    "inspect_dotenv",
)

# Gate-lock flags that MUST be True (blocked / locked). If present and not True,
# the input tried to unlock a gate -> unsafe.
FETCH_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock / out-of-band request flags that, if truthy, force unsafe.
FETCH_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "run_qa_now",
    "run_baseline_now",
    "run_backtest_now",
    "check_live_credentials_now",
    "read_dotenv_now",
    "place_order",
    "go_live",
)

# Read-only safety posture. The posture facts are True; every capability /
# authorization / unlock flag is False.
FETCH_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "human_approval_required": True,
    "fetch_disabled_by_default": True,
    "executes": False,
    "performs_fetch": False,
    "calls_databento": False,
    "uses_network": False,
    "fetches_data": False,
    "downloads_data": False,
    "checks_live_credentials": False,
    "reads_dotenv": False,
    "exposes_secret": False,
    "reads_data_files": False,
    "writes_data_files": False,
    "writes_manifest": False,
    "writes_reports": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "runs_qa": False,
    "runs_backtest": False,
    "authorizes_trading": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_order_placement": False,
    "authorizes_account_control": False,
    "authorizes_portfolio_control": False,
    "authorizes_strategy_promotion": False,
    "authorizes_automation_trading": False,
    "authorizes_qa_baseline": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}

# A deterministic, illustrative static input. Nothing here is real data. There is
# deliberately NO human_run_approved flag, so the default contract reports fetch
# DISABLED for a future runner.
DEFAULT_FETCH_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 Databento read-only fetch contract input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
    "requested_symbols": list(FETCH_APPROVED_SYMBOLS),
    "requested_timeframes": list(FETCH_APPROVED_TIMEFRAMES),
    "requested_provider": FETCH_APPROVED_PROVIDER,
    "requested_destination": FETCH_APPROVED_DESTINATION,
    "requested_report_dir": FETCH_APPROVED_REPORT_DIR,
    # Operator's STATIC presence assertion only. Not verified; no secret read.
    "databento_config_declared": False,
    # NOTE: no "human_run_approved" -> fetch stays disabled by default.
}


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _norm(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _is_truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _as_payload(payload: Any) -> dict[str, Any]:
    return dict(payload) if isinstance(payload, dict) else {}


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    out: list[str] = []
    for item in value:
        text = _norm(item)
        if text:
            out.append(text)
    return out


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _tokenize(text: str) -> list[str]:
    token: list[str] = []
    out: list[str] = []
    for ch in str(text).lower():
        if ch.isalnum() or ch == "_":
            token.append(ch)
        else:
            if token:
                out.append("".join(token))
                token = []
    if token:
        out.append("".join(token))
    return out


def _requested_symbols(payload: dict[str, Any]) -> list[str]:
    syms = _as_str_list(payload.get("requested_symbols")) or list(
        FETCH_APPROVED_SYMBOLS
    )
    return _dedupe(syms)


def _requested_timeframes(payload: dict[str, Any]) -> list[str]:
    tfs = _as_str_list(payload.get("requested_timeframes")) or list(
        FETCH_APPROVED_TIMEFRAMES
    )
    return _dedupe(tfs)


# --------------------------------------------------------------------------- #
# assessment + permission decision
# --------------------------------------------------------------------------- #
def assess_databento_read_only_fetch_execution(payload: Any) -> dict[str, Any]:
    """Assess (read-only) the static fetch inputs and derive the safety verdict
    and the fetch-permission decision for a FUTURE runner. Returns a fresh dict
    every call. Performs no fetch, calls no Databento, opens no network, reads no
    credential, exposes no secret, and unlocks nothing."""
    data = _as_payload(payload)

    mf_stage = data.get("mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE)
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    hits: list[str] = []
    for flag in FETCH_AUTHORIZATION_FLAGS:
        if _is_truthy(data.get(flag)):
            hits.append(flag)
    for flag in FETCH_GATE_UNLOCK_REQUEST_FLAGS:
        if _is_truthy(data.get(flag)):
            hits.append(flag)
    for flag in FETCH_GATE_LOCK_FLAGS:
        if flag in data and not _is_truthy(data.get(flag)):
            hits.append("unlocked:" + flag)
    forbidden_hits = _dedupe(hits)

    # scope checks
    req_syms = _requested_symbols(data)
    req_tfs = _requested_timeframes(data)
    req_provider = _norm(data.get("requested_provider")) or FETCH_APPROVED_PROVIDER
    req_dest = _norm(data.get("requested_destination")) or FETCH_APPROVED_DESTINATION
    req_report = _norm(data.get("requested_report_dir")) or FETCH_APPROVED_REPORT_DIR

    symbols_approved = bool(req_syms) and all(
        s in FETCH_APPROVED_SYMBOLS for s in req_syms
    )
    timeframes_approved = bool(req_tfs) and all(
        t in FETCH_APPROVED_TIMEFRAMES for t in req_tfs
    )
    provider_approved = req_provider == FETCH_APPROVED_PROVIDER
    destination_approved = req_dest == FETCH_APPROVED_DESTINATION
    report_path_approved = req_report == FETCH_APPROVED_REPORT_DIR
    scope_approved = (
        symbols_approved
        and timeframes_approved
        and provider_approved
        and destination_approved
        and report_path_approved
    )

    human_run_approved = _is_truthy(data.get(FETCH_HUMAN_RUN_APPROVAL_FLAG))
    gates_locked = not any(h.startswith("unlocked:") for h in forbidden_hits)

    safe = mission_flow_aligned and not forbidden_hits

    # Fetch permission for a FUTURE runner. THIS contract still performs no fetch.
    fetch_permitted_for_future_runner = (
        safe and human_run_approved and scope_approved
    )
    if not human_run_approved:
        reason = (
            "Fetch disabled by default: no explicit human-run approval flag "
            "supplied. A future runner is not permitted to fetch."
        )
    elif not safe:
        reason = (
            "Fetch refused: a forbidden authorization / unlock flag is set or the "
            "mission flow has left the human boundary."
        )
    elif not scope_approved:
        reason = (
            "Fetch refused: requested scope (symbols / timeframe / provider / "
            "destination / report path) is outside the approved boundary."
        )
    else:
        reason = (
            "Fetch permitted for a future runner ONLY: human-run approval is "
            "present, scope is approved, and all gates remain locked. THIS "
            "contract still performs no fetch and unlocks no gate."
        )

    return {
        "mode": FETCH_MODE,
        "safe": safe,
        "mission_flow_current_stage": str(mf_stage),
        "mission_flow_next_required_action": str(mf_action),
        "mission_flow_aligned": mission_flow_aligned,
        "forbidden_flag_hits": forbidden_hits,
        "requested_symbols": req_syms,
        "requested_timeframes": req_tfs,
        "requested_provider": req_provider,
        "requested_destination": req_dest,
        "requested_report_dir": req_report,
        "symbols_approved": symbols_approved,
        "timeframes_approved": timeframes_approved,
        "provider_approved": provider_approved,
        "destination_approved": destination_approved,
        "report_path_approved": report_path_approved,
        "scope_approved": scope_approved,
        "human_run_approved": human_run_approved,
        "gates_locked": gates_locked,
        "fetch_permitted_for_future_runner": fetch_permitted_for_future_runner,
        "fetch_permitted_reason": reason,
        "databento_config_present_declared": _is_truthy(
            data.get("databento_config_declared")
        ),
        "databento_secret_exposed": False,
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "executes": False,
        "performs_fetch": False,
        "calls_databento": False,
        "uses_network": False,
        "fetches_data": False,
        "checks_live_credentials": False,
        "reads_dotenv": False,
        "unlocks_real_data_qa": False,
        "authorizes_nothing": True,
    }


# --------------------------------------------------------------------------- #
# contract build
# --------------------------------------------------------------------------- #
def _operator_next_step(assessment: dict[str, Any]) -> str:
    if not assessment["safe"]:
        return (
            "Reject this fetch request. A forbidden authorization / unlock flag "
            "was set, or the mission flow has left the human boundary. Resolve the "
            "safety failure in research only; acquire no data, call no Databento, "
            "open no network, read no credential, read no .env file."
        )
    if not assessment["human_run_approved"]:
        return (
            "Hold at the human-controlled boundary. Fetch is disabled by default. "
            "A SEPARATE, explicit human-run approval is required before any "
            "read-only Databento historical retrieval may begin. This contract "
            "acquires no data and unlocks no gate."
        )
    if not assessment["scope_approved"]:
        return (
            "Reject this fetch request. The requested scope is outside the "
            "approved boundary (symbols / timeframe / provider / destination / "
            "report path). Acquire no data."
        )
    return (
        "A future runner MAY perform the read-only Databento historical fetch "
        "within the approved scope, under human-run approval, and must pass every "
        "pre-fetch and post-fetch check. This contract still performs no fetch and "
        "unlocks no gate; real_data_qa stays BLOCKED, baseline stays BLOCKED, and "
        "paper / micro-live stay LOCKED."
    )


def build_crypto_d1_databento_read_only_fetch_execution_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only Databento fetch execution contract.
    All capability flags are False and all gate locks are True regardless of
    input. `fetch_permitted_for_future_runner` is the ONLY field that may be True,
    and only when human-run approval is supplied, scope is approved, and the input
    is safe; even then THIS contract performs no fetch."""
    data = dict(DEFAULT_FETCH_INPUT) if payload is None else _as_payload(payload)
    a = assess_databento_read_only_fetch_execution(data)

    pre_fetch_check_results = {
        "mission_flow_aligned": a["mission_flow_aligned"],
        "human_run_approved": a["human_run_approved"],
        "symbols_approved": a["symbols_approved"],
        "timeframes_approved": a["timeframes_approved"],
        "provider_approved": a["provider_approved"],
        "destination_approved": a["destination_approved"],
        "report_path_approved": a["report_path_approved"],
        "no_forbidden_flags": not a["forbidden_flag_hits"],
        "gates_locked": a["gates_locked"],
        "credentials_not_exposed": True,
    }

    spec = {
        # 1. approved symbols / timeframes
        "approved_pairs": list(FETCH_APPROVED_PAIRS),
        "approved_symbols": list(FETCH_APPROVED_SYMBOLS),
        "approved_timeframes": list(FETCH_APPROVED_TIMEFRAMES),
        # 2. approved provider
        "approved_provider": FETCH_APPROVED_PROVIDER,
        "provider_detail": FETCH_PROVIDER_DETAIL,
        # 3. approved destination path
        "approved_destination": FETCH_APPROVED_DESTINATION,
        # 4. approved report path for a later manifest / gap report
        "approved_report_dir": FETCH_APPROVED_REPORT_DIR,
        "manifest_report_path": FETCH_MANIFEST_REPORT_PATH,
        "gap_report_path": FETCH_GAP_REPORT_PATH,
        "allowed_later_change_paths": list(FETCH_ALLOWED_LATER_CHANGE_PATHS),
        # 5. credential safety rules
        "credential_safety_rules": list(FETCH_CREDENTIAL_SAFETY_RULES),
        "databento_config_present_declared": a[
            "databento_config_present_declared"
        ],
        "databento_secret_exposed": False,
        "databento_config_note": (
            "Presence is a static operator assertion only. This contract does not "
            "read, verify, print, store, or log any credential value, and never "
            "reads .env file content."
        ),
        # 6. fetch permission model
        "fetch_permission_model": {
            "enabled_by_default": False,
            "requires_explicit_human_run_approval": True,
            "human_run_approval_flag": FETCH_HUMAN_RUN_APPROVAL_FLAG,
            "human_run_approved": a["human_run_approved"],
            "scope_approved": a["scope_approved"],
            "fetch_permitted_for_future_runner": a[
                "fetch_permitted_for_future_runner"
            ],
            "fetch_permitted_reason": a["fetch_permitted_reason"],
            "this_contract_performs_fetch": False,
        },
        # 7. pre-fetch checks
        "pre_fetch_checks": list(FETCH_PRE_FETCH_CHECKS),
        "pre_fetch_check_results": pre_fetch_check_results,
        # 8. post-fetch checks
        "post_fetch_checks": list(FETCH_POST_FETCH_CHECKS),
        # 9. hard-stop rules
        "hard_stop_conditions": list(FETCH_HARD_STOP_CONDITIONS),
        # 10. no-unlock confirmation
        "no_unlock_confirmation": {
            "unlocks_real_data_qa": False,
            "unlocks_baseline_backtest": False,
            "unlocks_paper_trading": False,
            "unlocks_micro_live": False,
            "real_data_qa_state": "BLOCKED",
            "baseline_backtest_state": "BLOCKED",
            "paper_live_state": "LOCKED",
        },
    }

    contract: dict[str, Any] = {
        "schema_version": FETCH_SCHEMA_VERSION,
        "label": FETCH_LABEL,
        "status": FETCH_STATUS,
        "mode": FETCH_MODE,
        "core_rule": FETCH_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": a["mission_flow_aligned"],
        "safe": a["safe"],
        "forbidden_flag_hits": list(a["forbidden_flag_hits"]),
        "still_forbidden_capabilities": list(FETCH_STILL_FORBIDDEN_CAPABILITIES),
        "fetch_contract": spec,
        "fetch_permitted_for_future_runner": a[
            "fetch_permitted_for_future_runner"
        ],
        "fetch_permitted_reason": a["fetch_permitted_reason"],
        "requires_explicit_human_run_approval": True,
        "fetch_summary": (
            "Read-only Databento fetch execution contract: a future runner may, "
            "under explicit human-run approval and within the approved scope, "
            "perform a read-only Databento historical retrieval of the missing "
            "Crypto-D1 daily bars (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d) into "
            "data/databento_cache/crypto_d1/ and write a manifest / gap report "
            "under reports/research_os/data_qa/. THIS contract performs no fetch, "
            "calls no Databento, opens no network, and unlocks nothing."
        ),
        "operator_next_step": _operator_next_step(a),
        "human_operator_required_next_steps": [
            "A human reviews this read-only Databento fetch execution contract.",
            "A human separately decides whether to grant explicit human-run "
            "approval for a future read-only Databento historical retrieval.",
            "Only with that separate approval, and only within the approved "
            "scope, may a future runner perform the read-only retrieval; it still "
            "unlocks no gate.",
        ],
        "safety_posture": dict(FETCH_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "human_approval_required": True,
        "read_only": True,
        "research_only": True,
        "fetch_disabled_by_default": True,
        "executes": False,
        "performs_fetch": False,
        "calls_databento": False,
        "uses_network": False,
        "fetches_data": False,
        "downloads_data": False,
        "checks_live_credentials": False,
        "reads_dotenv": False,
        "exposes_secret": False,
        "reads_data_files": False,
        "writes_data_files": False,
        "writes_manifest": False,
        "writes_reports": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
        "runs_qa": False,
        "runs_backtest": False,
        "authorizes_trading": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "authorizes_broker_exchange": False,
        "authorizes_order_placement": False,
        "authorizes_account_control": False,
        "authorizes_portfolio_control": False,
        "authorizes_strategy_promotion": False,
        "authorizes_automation_trading": False,
        "authorizes_qa_baseline": False,
        "authorizes_nothing": True,
        "unlocks_real_data_qa": False,
        "unlocks_baseline_backtest": False,
        "unlocks_paper_trading": False,
        "unlocks_micro_live": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return contract


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "mode",
    "core_rule",
    "mission_flow_current_stage",
    "mission_flow_next_required_action",
    "fetch_contract",
    "still_forbidden_capabilities",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_REQUIRED_SPEC_KEYS: tuple[str, ...] = (
    "approved_pairs",
    "approved_symbols",
    "approved_timeframes",
    "approved_provider",
    "provider_detail",
    "approved_destination",
    "approved_report_dir",
    "credential_safety_rules",
    "fetch_permission_model",
    "pre_fetch_checks",
    "pre_fetch_check_results",
    "post_fetch_checks",
    "hard_stop_conditions",
    "no_unlock_confirmation",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "performs_fetch",
    "calls_databento",
    "uses_network",
    "fetches_data",
    "downloads_data",
    "checks_live_credentials",
    "reads_dotenv",
    "exposes_secret",
    "reads_data_files",
    "writes_data_files",
    "writes_manifest",
    "writes_reports",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
    "runs_qa",
    "runs_backtest",
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_portfolio_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "authorizes_qa_baseline",
    "unlocks_real_data_qa",
    "unlocks_baseline_backtest",
    "unlocks_paper_trading",
    "unlocks_micro_live",
)

_ALL_GATE_LOCKS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

_SECRET_VALUE_TOKENS: tuple[str, ...] = (
    "api_key",
    "apikey",
    "secret",
    "password",
    "private_key",
    "bearer",
    "access_token",
)


def validate_crypto_d1_databento_read_only_fetch_execution_contract(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built fetch contract. Returns a verdict dict of
    boolean checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing_fields = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == FETCH_SCHEMA_VERSION
    label_ok = c.get("label") == FETCH_LABEL
    status_ok = c.get("status") == FETCH_STATUS
    mode_ok = c.get("mode") == FETCH_MODE
    core_rule_ok = c.get("core_rule") == FETCH_CORE_RULE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    performs_fetch_false = c.get("performs_fetch") is False
    human_required = c.get("human_approval_required") is True
    human_run_required = c.get("requires_explicit_human_run_approval") is True
    fetch_disabled_default = c.get("fetch_disabled_by_default") is True
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == FETCH_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
    )

    spec = c.get("fetch_contract")
    spec_is_dict = isinstance(spec, dict)
    spec_keys_ok = spec_is_dict and all(k in spec for k in _REQUIRED_SPEC_KEYS)

    provider_ok = spec_is_dict and spec.get("approved_provider") == FETCH_APPROVED_PROVIDER
    pairs_ok = spec_is_dict and spec.get("approved_pairs") == list(
        FETCH_APPROVED_PAIRS
    )
    destination_ok = spec_is_dict and spec.get("approved_destination") == (
        FETCH_APPROVED_DESTINATION
    )
    report_dir_ok = spec_is_dict and spec.get("approved_report_dir") == (
        FETCH_APPROVED_REPORT_DIR
    )

    # fetch permission model: disabled by default, requires explicit human-run
    # approval, and this contract never performs the fetch itself.
    fpm = spec.get("fetch_permission_model") if spec_is_dict else None
    permission_model_ok = isinstance(fpm, dict) and (
        fpm.get("enabled_by_default") is False
        and fpm.get("requires_explicit_human_run_approval") is True
        and fpm.get("human_run_approval_flag") == FETCH_HUMAN_RUN_APPROVAL_FLAG
        and fpm.get("this_contract_performs_fetch") is False
    )

    # no-unlock confirmation block.
    nuc = spec.get("no_unlock_confirmation") if spec_is_dict else None
    no_unlock_ok = isinstance(nuc, dict) and (
        nuc.get("unlocks_real_data_qa") is False
        and nuc.get("unlocks_baseline_backtest") is False
        and nuc.get("unlocks_paper_trading") is False
        and nuc.get("unlocks_micro_live") is False
        and nuc.get("real_data_qa_state") == "BLOCKED"
        and nuc.get("baseline_backtest_state") == "BLOCKED"
    )

    credential_safe = spec_is_dict and (
        spec.get("databento_secret_exposed") is False
    )

    no_secret_value_fields = not _has_secret_value(c)

    forbidden_list_intact = set(
        c.get("still_forbidden_capabilities") or ()
    ) == set(FETCH_STILL_FORBIDDEN_CAPABILITIES)

    # if a fetch is permitted for a future runner, gates MUST still be locked.
    permit_consistent = (
        (c.get("fetch_permitted_for_future_runner") is not True)
        or (gates_locked and states_blocked_locked and flags_false)
    )

    # authored narrative must carry no execution / trade verbs as whole words.
    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "fetch_summary", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(FETCH_FORBIDDEN_TRADE_TERMS))

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "status_ok": status_ok,
        "mode_ok": mode_ok,
        "core_rule_ok": core_rule_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "performs_fetch_false": performs_fetch_false,
        "human_required": human_required,
        "human_run_required": human_run_required,
        "fetch_disabled_default": fetch_disabled_default,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "spec_keys_ok": spec_keys_ok,
        "provider_ok": provider_ok,
        "pairs_ok": pairs_ok,
        "destination_ok": destination_ok,
        "report_dir_ok": report_dir_ok,
        "permission_model_ok": permission_model_ok,
        "no_unlock_ok": no_unlock_ok,
        "credential_safe": credential_safe,
        "no_secret_value_fields": no_secret_value_fields,
        "forbidden_list_intact": forbidden_list_intact,
        "permit_consistent": permit_consistent,
        "no_trade_language": no_trade_language,
    }
    verdict = dict(checks)
    verdict["missing_fields"] = missing_fields
    verdict["valid"] = (not missing_fields) and all(checks.values())
    return verdict


def _has_secret_value(obj: Any) -> bool:
    """True if any dict key looks like a secret AND carries a non-empty value.
    A declared-presence boolean or an explicit *_exposed=False flag is fine."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_l = str(key).lower()
            looks_secret = any(tok in key_l for tok in _SECRET_VALUE_TOKENS)
            if looks_secret and value not in (None, "", False, [], {}):
                return True
            if _has_secret_value(value):
                return True
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            if _has_secret_value(item):
                return True
    return False


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def _emit(lines: list[str], heading: str, rows: list[str]) -> None:
    lines.append("")
    lines.append("## " + heading)
    if not rows:
        lines.append("- (none)")
        return
    for row in rows:
        lines.append("- " + row)


def render_crypto_d1_databento_read_only_fetch_execution_contract_markdown(
    contract: Any,
) -> str:
    """Render a built fetch contract as a deterministic markdown brief. Pure
    string formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    spec = c.get("fetch_contract") or {}
    fpm = spec.get("fetch_permission_model") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Databento Read-Only Fetch Execution Contract")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Fetch permitted (future runner): "
        + str(c.get("fetch_permitted_for_future_runner", False))
    )
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(lines, "1. Approved Pairs", list(spec.get("approved_pairs") or []))
    _emit(
        lines,
        "2. Approved Provider",
        [str(spec.get("approved_provider", "")), str(spec.get("provider_detail", ""))],
    )
    _emit(
        lines,
        "3. Approved Destination",
        [str(spec.get("approved_destination", ""))],
    )
    _emit(
        lines,
        "4. Approved Report Path",
        [
            "report dir: " + str(spec.get("approved_report_dir", "")),
            "manifest: " + str(spec.get("manifest_report_path", "")),
            "gap report: " + str(spec.get("gap_report_path", "")),
        ],
    )
    _emit(
        lines,
        "5. Credential Safety Rules",
        list(spec.get("credential_safety_rules") or []),
    )
    _emit(
        lines,
        "6. Fetch Permission Model",
        [
            "enabled_by_default: " + str(fpm.get("enabled_by_default", False)),
            "requires_explicit_human_run_approval: "
            + str(fpm.get("requires_explicit_human_run_approval", True)),
            "human_run_approval_flag: " + str(fpm.get("human_run_approval_flag", "")),
            "fetch_permitted_for_future_runner: "
            + str(fpm.get("fetch_permitted_for_future_runner", False)),
            "this_contract_performs_fetch: "
            + str(fpm.get("this_contract_performs_fetch", False)),
            "reason: " + str(fpm.get("fetch_permitted_reason", "")),
        ],
    )
    _emit(lines, "7. Pre-Fetch Checks", list(spec.get("pre_fetch_checks") or []))
    _emit(lines, "8. Post-Fetch Checks", list(spec.get("post_fetch_checks") or []))
    _emit(
        lines,
        "9. Hard-Stop Conditions",
        list(spec.get("hard_stop_conditions") or []),
    )
    _emit(
        lines,
        "10. No-Unlock Confirmation",
        [
            str(k) + ": " + str(v)
            for k, v in (spec.get("no_unlock_confirmation") or {}).items()
        ],
    )
    _emit(
        lines,
        "Still Forbidden (always)",
        list(c.get("still_forbidden_capabilities") or []),
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)
