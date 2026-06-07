"""Crypto-D1 Databento Missing Crypto Data Acquisition Plan Contract (Block 141).

A PURE, stdlib-only, *read-only* paper contract. It produces -- on paper only --
a deterministic PLAN for a future, human-approved, READ-ONLY Databento historical
market-data acquisition step that would obtain the missing Crypto-D1 daily bars
(BTCUSD@1d, ETHUSD@1d, SOLUSD@1d) the local inventory (Block 140) confirmed are
absent. It is the document a human reviews to decide whether to later allow a
read-only Databento fetch. It is a plan, not an action.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

It executes NOTHING. It does NOT call Databento, open a network, fetch or download
data, inspect or read any credential, read a .env file, print or store any secret,
read or write any data file, write a manifest / gap report, run QA, run a
backtest, open a file, spawn a subprocess, read an environment variable, mint an
id, or record a timestamp. It only reasons over a static, caller-supplied summary.

What this plan describes is ALLOWED LATER, only with explicit human approval, and
only as a READ-ONLY data acquisition:
  - Databento HISTORICAL market-data retrieval (read-only) of the missing daily
    crypto bars
  - storing the retrieved bars into an approved local data folder
  - producing a post-fetch manifest / gap report

What stays FORBIDDEN, always (this plan never enables any of these):
  - exchange trading API, broker API, order placement
  - paper / live trading, account control, portfolio control
  - Telegram trade command, TradingView execution webhook
  - strategy promotion, automation that trades
  - credentials printed in logs or reports, .env inspection, secret logging

CORE RULE: this contract NEVER unlocks Real Data QA and NEVER crosses any
real-world boundary. Producing the plan authorizes nothing. real_data_qa stays
BLOCKED, baseline stays BLOCKED, and the paper / micro-live gates stay LOCKED.

Public API:
  - PLAN_SCHEMA_VERSION / PLAN_LABEL / PLAN_STATUS / PLAN_MODE / PLAN_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - PLAN_DEFAULT_MISSING_PAIRS / PLAN_PROPOSED_PROVIDER / PLAN_PROVIDER_DETAIL
  - PLAN_DEFAULT_STORAGE_DESTINATION / PLAN_ALLOWED_STORAGE_DESTINATIONS
  - PLAN_ALLOWED_LATER_CHANGE_PATHS
  - PLAN_MANIFEST_REPORT_PATH / PLAN_GAP_REPORT_PATH
  - PLAN_STILL_FORBIDDEN_CAPABILITIES / PLAN_REQUIRED_TESTS
  - PLAN_HARD_STOP_CONDITIONS / PLAN_FORBIDDEN_TRADE_TERMS
  - PLAN_AUTHORIZATION_FLAGS / PLAN_GATE_LOCK_FLAGS
  - PLAN_GATE_UNLOCK_REQUEST_FLAGS / PLAN_SAFETY_POSTURE
  - DEFAULT_PLAN_INPUT
  - assess_databento_missing_crypto_data_acquisition_plan(payload)
  - build_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract(payload=None)
  - validate_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract(contract)
  - render_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

PLAN_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract.v1"
)
PLAN_LABEL = (
    "Block 141 - Crypto-D1 Databento Missing Crypto Data Acquisition Plan Contract"
)
PLAN_STATUS = "READ_ONLY_DATABENTO_PLAN_ONLY"
PLAN_MODE = "RESEARCH_ONLY"

PLAN_CORE_RULE = (
    "This contract NEVER unlocks Real Data QA and NEVER crosses any real-world "
    "boundary. It only produces a deterministic plan for a future, human-approved, "
    "READ-ONLY Databento historical market-data acquisition step. Producing the "
    "plan authorizes nothing: no Databento call is made, no network is opened, no "
    "data is fetched or downloaded, no credential is inspected, no .env is read, "
    "no secret is shown, and no manifest / gap report is written. real_data_qa "
    "stays BLOCKED, baseline stays BLOCKED, and the paper / micro-live gates stay "
    "LOCKED."
)

# Current mission-flow truth this contract is anchored to. The companion test
# cross-checks these against the live status module so they cannot drift.
MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# The missing Crypto-D1 pairs Block 140's local inventory confirmed are absent.
PLAN_DEFAULT_MISSING_PAIRS: tuple[str, ...] = (
    "BTCUSD@1d",
    "ETHUSD@1d",
    "SOLUSD@1d",
)

# Proposed read-only provider. Databento HISTORICAL market data only -- never an
# exchange, broker, or trading endpoint.
PLAN_PROPOSED_PROVIDER = "databento_historical_market_data_read_only"
PLAN_PROVIDER_DETAIL = (
    "Databento historical market-data API: read-only retrieval of historical "
    "daily OHLCV bars for the missing crypto pairs. No exchange endpoint, no "
    "broker endpoint, no trading endpoint, no account endpoint -- historical "
    "market data retrieval only."
)

# Proposed local storage destination for a later approved fetch. Named only; this
# contract writes nothing here.
PLAN_DEFAULT_STORAGE_DESTINATION = "data/databento_cache/"
PLAN_ALLOWED_STORAGE_DESTINATIONS: tuple[str, ...] = (
    "data/databento_cache/",
    "data/databento_cache/crypto_d1/",
)

# The ONLY paths a later, human-approved, read-only Databento fetch step would be
# allowed to change. Named here as plan scope; this contract changes none of them.
PLAN_ALLOWED_LATER_CHANGE_PATHS: tuple[str, ...] = (
    "data/databento_cache/ (read-only fetch destination; later approved step only)",
    "data/databento_cache/crypto_d1/ (read-only fetch destination; later approved step only)",
    "reports/research_os/data_qa/ (post-fetch manifest / gap report; later approved step only)",
)

# Required post-fetch manifest / gap report paths. NAMED here; NOT written now.
PLAN_MANIFEST_REPORT_PATH = (
    "reports/research_os/data_qa/crypto_d1_databento_manifest.json"
)
PLAN_GAP_REPORT_PATH = (
    "reports/research_os/data_qa/crypto_d1_databento_gap_report.md"
)

# Capabilities that stay FORBIDDEN, always. The plan never enables any of these;
# they are listed here as a signature of what remains blocked.
PLAN_STILL_FORBIDDEN_CAPABILITIES: tuple[str, ...] = (
    "exchange_trading_api",
    "broker_api",
    "order_placement",
    "paper_live_trading",
    "account_control",
    "portfolio_control",
    "telegram_trade_command",
    "tradingview_execution_webhook",
    "strategy_promotion",
    "automation_that_trades",
    "credentials_in_logs_or_reports",
    "dotenv_inspection",
    "secret_logging",
)

# Tests that WOULD run before and after a later approved read-only fetch step.
PLAN_REQUIRED_TESTS: tuple[str, ...] = (
    "tests/test_strategy_factory_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract.py",
    "tests/test_strategy_factory_crypto_d1_local_data_inventory_inspector.py",
    "tests/test_sparta_commander_2_safety.py",
)

# Hard-stop conditions: if ANY would be true, the later step must STOP.
PLAN_HARD_STOP_CONDITIONS: tuple[str, ...] = (
    "Any real credential value would be read, printed, or written -> STOP.",
    "Any .env file would be read or inspected -> STOP.",
    "Any exchange / broker / account / portfolio / trading endpoint would be "
    "touched -> STOP.",
    "Any paper / live trading or strategy promotion would occur -> STOP.",
    "Any non-Databento or non-historical-market-data endpoint would be called "
    "-> STOP.",
    "Any data fetch, download, or Databento call would occur in THIS plan "
    "step -> STOP.",
    "Any manifest / gap report / runtime / dashboard output would be written in "
    "THIS plan step -> STOP.",
    "real_data_qa, baseline_backtest, paper, or micro-live would be unlocked "
    "-> STOP.",
    "Mission flow is no longer at the human-controlled boundary -> STOP.",
)

# Execution / promotion verbs the plan's authored NARRATIVE must never contain as
# whole words. (The forbidden-capability list above intentionally names some of
# these as signature literals and is excluded from the narrative scan.)
PLAN_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Top-level flags that, if truthy, force a refusing (unsafe) plan verdict.
PLAN_AUTHORIZATION_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "unlocks_downstream_gate",
    "print_credentials",
    "expose_secret",
    "inspect_dotenv",
)

# Gate-lock flags that MUST be True (blocked / locked). If present and not True,
# the input tried to unlock a gate -> unsafe.
PLAN_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock / fetch-now request flags that, if truthy, force unsafe.
PLAN_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "fetch_data_now",
    "download_now",
    "call_databento_now",
    "check_live_credentials_now",
    "read_dotenv_now",
    "write_manifest_now",
    "place_order",
    "go_live",
)

# Read-only safety posture. The posture facts are True; every capability /
# authorization / unlock flag is False.
PLAN_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "human_approval_required": True,
    "executes": False,
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
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}


# A deterministic, illustrative paper input. Nothing here is real data; static
# example only. databento_config_declared is a static operator assertion of
# presence -- NO credential is read or shown.
DEFAULT_PLAN_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 Databento missing-data acquisition plan input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
    "missing_pairs": list(PLAN_DEFAULT_MISSING_PAIRS),
    "storage_destination": PLAN_DEFAULT_STORAGE_DESTINATION,
    # Operator's STATIC presence assertion only. Not verified; no secret read.
    "databento_config_declared": False,
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


def _missing_pairs(payload: dict[str, Any]) -> list[str]:
    pairs = _as_str_list(payload.get("missing_pairs")) or list(
        PLAN_DEFAULT_MISSING_PAIRS
    )
    seen: set[str] = set()
    out: list[str] = []
    for p in pairs:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


# --------------------------------------------------------------------------- #
# assessment
# --------------------------------------------------------------------------- #
def assess_databento_missing_crypto_data_acquisition_plan(
    payload: Any,
) -> dict[str, Any]:
    """Assess (read-only) the static plan inputs and derive the safety verdict.
    Returns a fresh dict every call. Authorizes and unlocks nothing; calls no
    Databento, opens no network, reads no credential, exposes no secret."""
    data = _as_payload(payload)

    mf_stage = data.get(
        "mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE
    )
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    hits: list[str] = []
    for flag in PLAN_AUTHORIZATION_FLAGS:
        if _is_truthy(data.get(flag)):
            hits.append(flag)
    for flag in PLAN_GATE_UNLOCK_REQUEST_FLAGS:
        if _is_truthy(data.get(flag)):
            hits.append(flag)
    for flag in PLAN_GATE_LOCK_FLAGS:
        if flag in data and not _is_truthy(data.get(flag)):
            hits.append("unlocked:" + flag)
    seen: set[str] = set()
    forbidden_hits: list[str] = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            forbidden_hits.append(h)

    missing = _missing_pairs(data)
    safe = mission_flow_aligned and not forbidden_hits

    databento_declared = _is_truthy(data.get("databento_config_declared"))

    return {
        "mode": PLAN_MODE,
        "safe": safe,
        "mission_flow_current_stage": str(mf_stage),
        "mission_flow_next_required_action": str(mf_action),
        "mission_flow_aligned": mission_flow_aligned,
        "forbidden_flag_hits": forbidden_hits,
        "missing_pairs": missing,
        "databento_config_present_declared": databento_declared,
        "databento_secret_exposed": False,
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "calls_databento": False,
        "uses_network": False,
        "fetches_data": False,
        "downloads_data": False,
        "checks_live_credentials": False,
        "reads_dotenv": False,
        "unlocks_real_data_qa": False,
        "authorizes_nothing": True,
    }


# --------------------------------------------------------------------------- #
# plan build
# --------------------------------------------------------------------------- #
def _retrieval_descriptions(missing: list[str]) -> list[str]:
    """Describe the read-only Databento retrievals a later approved step WOULD
    perform. Pure string formatting; makes no call. No execution / trade verbs."""
    calls: list[str] = []
    for pair in missing:
        sym, _, tf = pair.partition("@")
        calls.append(
            "Databento historical market-data retrieval (read-only GET) of daily "
            "OHLCV bars for " + sym + " " + tf
        )
    return calls


def _operator_next_step(assessment: dict[str, Any]) -> str:
    if not assessment["safe"]:
        return (
            "Reject this plan. A forbidden authorization / unlock / fetch-now flag "
            "was set, or the mission flow has left the human boundary. Resolve the "
            "safety failure in research only; acquire no data, call no Databento, "
            "open no network, read no credential, read no .env file."
        )
    return (
        "Hold at the human-controlled boundary. This plan is ready for a SEPARATE "
        "human approval review. Approval of THIS plan would authorize only a "
        "future, read-only Databento historical retrieval step; it would still "
        "acquire no data here and unlock no gate. A separate, explicitly "
        "human-approved step is required before any read-only retrieval may begin."
    )


def build_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only Databento acquisition plan contract.
    All capability flags are False and all gate locks are True regardless of
    input."""
    data = (
        dict(DEFAULT_PLAN_INPUT) if payload is None else _as_payload(payload)
    )
    assessment = assess_databento_missing_crypto_data_acquisition_plan(data)
    missing = list(assessment["missing_pairs"])
    storage = _norm(data.get("storage_destination")) or PLAN_DEFAULT_STORAGE_DESTINATION
    if storage not in PLAN_ALLOWED_STORAGE_DESTINATIONS:
        storage = PLAN_DEFAULT_STORAGE_DESTINATION

    symbols: list[str] = []
    timeframes: list[str] = []
    for pair in missing:
        sym, _, tf = pair.partition("@")
        if sym and sym not in symbols:
            symbols.append(sym)
        if tf and tf not in timeframes:
            timeframes.append(tf)

    plan = {
        # 1. missing symbols / timeframes
        "missing_pairs": missing,
        "missing_symbols": symbols,
        "missing_timeframes": timeframes,
        # 2. proposed read-only provider
        "proposed_provider": PLAN_PROPOSED_PROVIDER,
        "provider_detail": PLAN_PROVIDER_DETAIL,
        "read_only_retrieval_descriptions": _retrieval_descriptions(missing),
        # 3. no exchange / broker / trading API
        "no_exchange_broker_trading_api": {
            "uses_exchange_trading_api": False,
            "uses_broker_api": False,
            "uses_trading_endpoint": False,
            "uses_account_endpoint": False,
            "historical_market_data_only": True,
        },
        # 4. no credential printing / .env inspection / secret logging
        "no_credential_exposure": {
            "prints_credentials": False,
            "inspects_dotenv": False,
            "logs_secret": False,
            "stores_secret": False,
            "databento_secret_exposed": False,
        },
        "databento_config_present_declared": assessment[
            "databento_config_present_declared"
        ],
        "databento_config_note": (
            "Presence is a static operator assertion only. This contract does not "
            "read, verify, print, store, or log any credential value, and never "
            "reads a .env file."
        ),
        # 5. proposed storage destination
        "proposed_storage_destination": storage,
        "allowed_storage_destinations": list(PLAN_ALLOWED_STORAGE_DESTINATIONS),
        # 6. allowed future change paths for a later approved fetch step
        "allowed_future_change_paths": list(PLAN_ALLOWED_LATER_CHANGE_PATHS),
        # 7. required post-fetch manifest / gap report paths (named, NOT written)
        "post_fetch_manifest_path": PLAN_MANIFEST_REPORT_PATH,
        "post_fetch_gap_report_path": PLAN_GAP_REPORT_PATH,
        "manifest_written_now": False,
        "gap_report_written_now": False,
        # 8. hard-stop rules
        "hard_stop_conditions": list(PLAN_HARD_STOP_CONDITIONS),
        # 9. tests required before / after a later fetch step
        "required_tests": list(PLAN_REQUIRED_TESTS),
        # 10. confirmation this plan does not unlock real_data_qa / baseline
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
        "schema_version": PLAN_SCHEMA_VERSION,
        "label": PLAN_LABEL,
        "status": PLAN_STATUS,
        "mode": PLAN_MODE,
        "core_rule": PLAN_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": assessment["mission_flow_aligned"],
        "safe": assessment["safe"],
        "forbidden_flag_hits": list(assessment["forbidden_flag_hits"]),
        "still_forbidden_capabilities": list(PLAN_STILL_FORBIDDEN_CAPABILITIES),
        "plan": plan,
        "plan_summary": (
            "Read-only Databento acquisition plan: obtain the missing Crypto-D1 "
            "daily bars (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d) via Databento historical "
            "market-data retrieval only, store them in an approved local folder, "
            "and produce a post-fetch manifest / gap report. This plan acquires "
            "nothing, calls no Databento, opens no network, and unlocks nothing."
        ),
        "operator_next_step": _operator_next_step(assessment),
        "human_operator_required_next_steps": [
            "A human reviews this read-only Databento acquisition plan.",
            "A human separately decides whether to approve a future read-only "
            "Databento historical retrieval step.",
            "A separate, future, explicitly human-approved step is required "
            "before any read-only retrieval, download, or manifest write may "
            "begin.",
        ],
        "safety_posture": dict(PLAN_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "requires_separate_future_human_approved_step": True,
        "human_approval_required": True,
        "read_only": True,
        "executes": False,
        "research_only": True,
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
    "plan",
    "still_forbidden_capabilities",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_REQUIRED_PLAN_KEYS: tuple[str, ...] = (
    "missing_pairs",
    "missing_symbols",
    "missing_timeframes",
    "proposed_provider",
    "provider_detail",
    "no_exchange_broker_trading_api",
    "no_credential_exposure",
    "proposed_storage_destination",
    "allowed_future_change_paths",
    "post_fetch_manifest_path",
    "post_fetch_gap_report_path",
    "manifest_written_now",
    "gap_report_written_now",
    "hard_stop_conditions",
    "required_tests",
    "no_unlock_confirmation",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
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

# Field-name fragments that would suggest a raw secret value was stored.
_SECRET_VALUE_TOKENS: tuple[str, ...] = (
    "api_key",
    "apikey",
    "secret",
    "password",
    "private_key",
    "bearer",
    "access_token",
)


def validate_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built plan contract. Returns a verdict dict of
    boolean checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing_fields = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == PLAN_SCHEMA_VERSION
    label_ok = c.get("label") == PLAN_LABEL
    status_ok = c.get("status") == PLAN_STATUS
    mode_ok = c.get("mode") == PLAN_MODE
    core_rule_ok = c.get("core_rule") == PLAN_CORE_RULE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    human_required = c.get("human_approval_required") is True
    future_step_required = (
        c.get("requires_separate_future_human_approved_step") is True
    )
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == PLAN_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
    )

    plan = c.get("plan")
    plan_is_dict = isinstance(plan, dict)
    plan_keys_ok = plan_is_dict and all(
        k in plan for k in _REQUIRED_PLAN_KEYS
    )

    # provider must be Databento historical read-only.
    provider_ok = plan_is_dict and plan.get("proposed_provider") == PLAN_PROPOSED_PROVIDER

    # no exchange / broker / trading endpoint.
    nebt = plan.get("no_exchange_broker_trading_api") if plan_is_dict else None
    no_exchange_broker_ok = isinstance(nebt, dict) and (
        nebt.get("uses_exchange_trading_api") is False
        and nebt.get("uses_broker_api") is False
        and nebt.get("uses_trading_endpoint") is False
        and nebt.get("uses_account_endpoint") is False
        and nebt.get("historical_market_data_only") is True
    )

    # no credential exposure / .env inspection / secret logging.
    nce = plan.get("no_credential_exposure") if plan_is_dict else None
    no_credential_exposure_ok = isinstance(nce, dict) and (
        nce.get("prints_credentials") is False
        and nce.get("inspects_dotenv") is False
        and nce.get("logs_secret") is False
        and nce.get("stores_secret") is False
        and nce.get("databento_secret_exposed") is False
    )

    # manifest / gap report are named but NOT written now.
    not_written_now = plan_is_dict and (
        plan.get("manifest_written_now") is False
        and plan.get("gap_report_written_now") is False
    )

    # storage destination must be an approved local data folder.
    storage_ok = plan_is_dict and (
        plan.get("proposed_storage_destination") in PLAN_ALLOWED_STORAGE_DESTINATIONS
    )

    # no-unlock confirmation block.
    nuc = plan.get("no_unlock_confirmation") if plan_is_dict else None
    no_unlock_ok = isinstance(nuc, dict) and (
        nuc.get("unlocks_real_data_qa") is False
        and nuc.get("unlocks_baseline_backtest") is False
        and nuc.get("unlocks_paper_trading") is False
        and nuc.get("unlocks_micro_live") is False
        and nuc.get("real_data_qa_state") == "BLOCKED"
        and nuc.get("baseline_backtest_state") == "BLOCKED"
    )

    no_secret_value_fields = not _has_secret_value(c)

    forbidden_list_intact = set(
        c.get("still_forbidden_capabilities") or ()
    ) == set(PLAN_STILL_FORBIDDEN_CAPABILITIES)

    # authored narrative must carry no execution / trade verbs as whole words.
    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "plan_summary", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(PLAN_FORBIDDEN_TRADE_TERMS))

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "status_ok": status_ok,
        "mode_ok": mode_ok,
        "core_rule_ok": core_rule_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "human_required": human_required,
        "future_step_required": future_step_required,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "plan_keys_ok": plan_keys_ok,
        "provider_ok": provider_ok,
        "no_exchange_broker_ok": no_exchange_broker_ok,
        "no_credential_exposure_ok": no_credential_exposure_ok,
        "not_written_now": not_written_now,
        "storage_ok": storage_ok,
        "no_unlock_ok": no_unlock_ok,
        "no_secret_value_fields": no_secret_value_fields,
        "forbidden_list_intact": forbidden_list_intact,
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


def render_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract_markdown(
    contract: Any,
) -> str:
    """Render a built plan contract as a deterministic markdown brief. Pure string
    formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    plan = c.get("plan") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Databento Missing Crypto Data Acquisition Plan")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Mission flow stage: " + str(c.get("mission_flow_current_stage", ""))
    )
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(lines, "1. Missing Pairs", list(plan.get("missing_pairs") or []))
    _emit(
        lines,
        "2. Proposed Read-Only Provider",
        [str(plan.get("proposed_provider", "")), str(plan.get("provider_detail", ""))],
    )
    _emit(
        lines,
        "3. No Exchange / Broker / Trading API",
        [
            str(k) + ": " + str(v)
            for k, v in (plan.get("no_exchange_broker_trading_api") or {}).items()
        ],
    )
    _emit(
        lines,
        "4. No Credential Exposure",
        [
            str(k) + ": " + str(v)
            for k, v in (plan.get("no_credential_exposure") or {}).items()
        ],
    )
    _emit(
        lines,
        "5. Proposed Storage Destination",
        [str(plan.get("proposed_storage_destination", ""))],
    )
    _emit(
        lines,
        "6. Allowed Future Change Paths",
        list(plan.get("allowed_future_change_paths") or []),
    )
    _emit(
        lines,
        "7. Post-Fetch Manifest / Gap Report (named, NOT written now)",
        [
            "manifest: " + str(plan.get("post_fetch_manifest_path", "")),
            "gap report: " + str(plan.get("post_fetch_gap_report_path", "")),
            "manifest_written_now: " + str(plan.get("manifest_written_now", False)),
            "gap_report_written_now: " + str(plan.get("gap_report_written_now", False)),
        ],
    )
    _emit(
        lines,
        "8. Hard-Stop Conditions",
        list(plan.get("hard_stop_conditions") or []),
    )
    _emit(lines, "9. Required Tests (before / after later fetch)", list(plan.get("required_tests") or []))
    _emit(
        lines,
        "10. No-Unlock Confirmation",
        [
            str(k) + ": " + str(v)
            for k, v in (plan.get("no_unlock_confirmation") or {}).items()
        ],
    )
    _emit(lines, "Still Forbidden (always)", list(c.get("still_forbidden_capabilities") or []))
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)
