"""Crypto-D1 Read-Only Real Data QA Boundary Plan Contract (Block 139).

A PURE, stdlib-only, *read-only* paper contract. It produces -- on paper only --
a deterministic PLAN for a future, human-approved, READ-ONLY data / API boundary
step. It is the document a human reviews to decide whether to later allow
read-only market-data access (local datasets and Databento historical/market data
only). It is a plan, not an action.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

It executes NOTHING. It does NOT fetch data, inspect or read any dataset, call
Databento, check or read any live credential, print or store any secret, write a
manifest, write any runtime / dashboard output, open a file, open a network,
spawn a subprocess, read an environment variable, mint an id, or record a
timestamp. It only reasons over a static, caller-supplied summary.

What this plan describes is ALLOWED LATER, only with explicit human approval, and
only as READ-ONLY data access:
  - read-only market-data inventory
  - read-only missing-data acquisition
  - Databento historical / market data access (read-only)
  - local dataset inspection
  - manifest / gap report

What stays FORBIDDEN, always (this plan never enables any of these):
  - exchange trading API, broker API, order placement
  - paper / live trading, account control, portfolio control
  - Telegram trade command, TradingView execution webhook
  - strategy promotion, automation that trades
  - credentials printed in logs or reports

CORE RULE: this contract NEVER unlocks Real Data QA and NEVER crosses any
real-world boundary. Producing the plan authorizes nothing. real_data_qa stays
BLOCKED, baseline stays BLOCKED, and the paper / micro-live gates stay LOCKED.

Public API:
  - PLAN_SCHEMA_VERSION / PLAN_LABEL / PLAN_STATUS / PLAN_MODE / PLAN_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - PLAN_ALLOWED_LATER_CAPABILITIES / PLAN_STILL_FORBIDDEN_CAPABILITIES
  - PLAN_DEFAULT_NEEDED_SYMBOLS / PLAN_DEFAULT_NEEDED_TIMEFRAMES
  - PLAN_DEFAULT_DATA_STORE_PATH
  - PLAN_ALLOWED_LATER_CHANGE_PATHS / PLAN_SCOPED_TESTS
  - PLAN_HARD_STOP_CONDITIONS / PLAN_FORBIDDEN_TRADE_TERMS
  - PLAN_AUTHORIZATION_FLAGS / PLAN_GATE_LOCK_FLAGS
  - PLAN_GATE_UNLOCK_REQUEST_FLAGS / PLAN_SAFETY_POSTURE
  - DEFAULT_PLAN_INPUT
  - assess_read_only_data_qa_boundary_plan(payload)
  - build_crypto_d1_read_only_data_qa_boundary_plan_contract(payload=None)
  - validate_crypto_d1_read_only_data_qa_boundary_plan_contract(contract)
  - render_crypto_d1_read_only_data_qa_boundary_plan_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

PLAN_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_read_only_data_qa_boundary_plan_contract.v1"
)
PLAN_LABEL = (
    "Block 139 - Crypto-D1 Read-Only Real Data QA Boundary Plan Contract"
)
PLAN_STATUS = "READ_ONLY_DATA_QA_PLAN_ONLY"
PLAN_MODE = "RESEARCH_ONLY"

PLAN_CORE_RULE = (
    "This contract NEVER unlocks Real Data QA and NEVER crosses any real-world "
    "boundary. It only produces a deterministic plan for a future, human-approved, "
    "READ-ONLY data / API step. Producing the plan authorizes nothing: no data is "
    "fetched, no dataset is read, no Databento call is made, no credential is "
    "checked, no secret is shown, and no manifest / runtime / dashboard output is "
    "written. real_data_qa stays BLOCKED, baseline stays BLOCKED, and the paper / "
    "micro-live gates stay LOCKED."
)

# Current mission-flow truth this contract is anchored to. The companion test
# cross-checks these against the live status module so they cannot drift.
MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# Capabilities this plan describes as ALLOWED LATER -- read-only data only, and
# only with explicit human approval. The plan never enables them itself.
PLAN_ALLOWED_LATER_CAPABILITIES: tuple[str, ...] = (
    "read_only_market_data_inventory",
    "read_only_missing_data_acquisition",
    "databento_historical_market_data_read_only",
    "local_dataset_inspection",
    "manifest_gap_report",
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
)

# Default Crypto-D1 coverage need: daily-timeframe crypto majors.
PLAN_DEFAULT_NEEDED_SYMBOLS: tuple[str, ...] = ("BTCUSD", "ETHUSD", "SOLUSD")
PLAN_DEFAULT_NEEDED_TIMEFRAMES: tuple[str, ...] = ("1d",)

# Where read-only data WOULD be stored in a later approved step (named only; this
# contract writes nothing here).
PLAN_DEFAULT_DATA_STORE_PATH = "data/databento_cache/"

# The ONLY paths a later, human-approved, read-only data step would be allowed to
# change. Named here as plan scope; this contract changes none of them.
PLAN_ALLOWED_LATER_CHANGE_PATHS: tuple[str, ...] = (
    "data/databento_cache/ (read-only fetch destination; later approved step only)",
    "reports/research_os/data_qa/ (manifest / gap report; later approved step only)",
)

# Tests that WOULD run for a later approved read-only data step.
PLAN_SCOPED_TESTS: tuple[str, ...] = (
    "tests/test_strategy_factory_crypto_d1_read_only_data_qa_boundary_plan_contract.py",
    "tests/test_sparta_commander_2_safety.py",
)

# Hard-stop conditions: if ANY would be true, the later step must STOP.
PLAN_HARD_STOP_CONDITIONS: tuple[str, ...] = (
    "Any real credential value would be read, printed, or written -> STOP.",
    "Any exchange / broker / account / portfolio API would be touched -> STOP.",
    "Any paper / live trading or strategy promotion would occur -> STOP.",
    "Any automation that places a market instruction would run -> STOP.",
    "Any data fetch, dataset read, or Databento call would occur in THIS plan "
    "step -> STOP.",
    "Any runtime / dashboard output would be written -> STOP.",
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

# Top-level flags that, if truthy, force a refusing BLOCK plan.
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
)

# Gate-lock flags that MUST be True (blocked / locked). If present and not True,
# the input tried to unlock a gate -> BLOCK.
PLAN_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock / fetch-now request flags that, if truthy, force a BLOCK.
PLAN_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "fetch_data_now",
    "inspect_datasets_now",
    "call_databento_now",
    "check_live_credentials_now",
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
    "fetches_data": False,
    "inspects_datasets": False,
    "calls_databento": False,
    "checks_live_credentials": False,
    "exposes_secret": False,
    "writes_manifest": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
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


# A deterministic, illustrative paper input. Datasets cover BTCUSD/1d, MNQ/1d, and
# MGC/1d, so the default plan reports ETHUSD/1d and SOLUSD/1d as missing. Nothing
# here is real data; static example only. databento_config_declared is a static
# operator assertion of presence -- NO credential is read or shown.
DEFAULT_PLAN_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 read-only data QA boundary plan input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
    "needed_symbols": list(PLAN_DEFAULT_NEEDED_SYMBOLS),
    "needed_timeframes": list(PLAN_DEFAULT_NEEDED_TIMEFRAMES),
    "declared_local_datasets": [
        {
            "name": "databento_cache",
            "path": "data/databento_cache/",
            "symbols": ["BTCUSD"],
            "timeframes": ["1d"],
        },
        {
            "name": "databento_long_history",
            "path": "data/s10_d1_mnq_mgc_databento_long_history/",
            "symbols": ["MNQ", "MGC"],
            "timeframes": ["1d"],
        },
    ],
    "data_store_path": PLAN_DEFAULT_DATA_STORE_PATH,
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


def _pair(symbol: str, timeframe: str) -> str:
    return symbol + "@" + timeframe


def _needed_pairs(payload: dict[str, Any]) -> list[str]:
    symbols = _as_str_list(payload.get("needed_symbols")) or list(
        PLAN_DEFAULT_NEEDED_SYMBOLS
    )
    timeframes = _as_str_list(payload.get("needed_timeframes")) or list(
        PLAN_DEFAULT_NEEDED_TIMEFRAMES
    )
    seen: set[str] = set()
    pairs: list[str] = []
    for sym in symbols:
        for tf in timeframes:
            p = _pair(sym, tf)
            if p not in seen:
                seen.add(p)
                pairs.append(p)
    return pairs


def _declared_datasets(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("declared_local_datasets")
    if not isinstance(raw, (list, tuple)):
        return []
    return [dict(d) for d in raw if isinstance(d, dict)]


def _present_pairs(datasets: list[dict[str, Any]]) -> set[str]:
    present: set[str] = set()
    for ds in datasets:
        syms = _as_str_list(ds.get("symbols"))
        tfs = _as_str_list(ds.get("timeframes"))
        for sym in syms:
            for tf in tfs:
                present.add(_pair(sym, tf))
    return present


# --------------------------------------------------------------------------- #
# assessment
# --------------------------------------------------------------------------- #
def assess_read_only_data_qa_boundary_plan(payload: Any) -> dict[str, Any]:
    """Assess (read-only) the static plan inputs and derive the coverage gap and
    safety verdict. Returns a fresh dict every call. Authorizes and unlocks
    nothing; reads no dataset, makes no API call, exposes no secret."""
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

    # forbidden-flag detection
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

    needed = _needed_pairs(data)
    datasets = _declared_datasets(data)
    present = _present_pairs(datasets)
    missing = [p for p in needed if p not in present]
    covered = [p for p in needed if p in present]

    safe = mission_flow_aligned and not forbidden_hits

    # databento config presence is a STATIC operator assertion; never verified,
    # never reads a secret, never shows a value.
    databento_declared = _is_truthy(data.get("databento_config_declared"))

    return {
        "mode": PLAN_MODE,
        "safe": safe,
        "mission_flow_current_stage": str(mf_stage),
        "mission_flow_next_required_action": str(mf_action),
        "mission_flow_aligned": mission_flow_aligned,
        "forbidden_flag_hits": forbidden_hits,
        "needed_pairs": needed,
        "covered_pairs": covered,
        "missing_pairs": missing,
        "databento_config_present_declared": databento_declared,
        "databento_secret_exposed": False,
        "real_data_qa_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "fetches_data": False,
        "inspects_datasets": False,
        "calls_databento": False,
        "checks_live_credentials": False,
        "unlocks_real_data_qa": False,
        "authorizes_nothing": True,
    }


# --------------------------------------------------------------------------- #
# plan build
# --------------------------------------------------------------------------- #
def _read_only_api_calls(missing: list[str]) -> list[str]:
    """Describe the read-only data retrievals a later approved step WOULD need.
    Pure string formatting; makes no call. No execution / trade verbs."""
    calls: list[str] = []
    for pair in missing:
        sym, _, tf = pair.partition("@")
        calls.append(
            "Databento historical market-data retrieval (read-only GET) for "
            + sym
            + " "
            + tf
        )
    return calls


def _dataset_inventory_plan(datasets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Name which local datasets WOULD be inventoried later. Reads nothing; only
    echoes the caller-declared descriptors."""
    plan: list[dict[str, Any]] = []
    for ds in datasets:
        plan.append(
            {
                "name": _norm(ds.get("name")),
                "path": _norm(ds.get("path")),
                "symbols": _as_str_list(ds.get("symbols")),
                "timeframes": _as_str_list(ds.get("timeframes")),
                "action": "inventory_read_only (later approved step only)",
            }
        )
    return plan


def _operator_next_step(assessment: dict[str, Any]) -> str:
    if not assessment["safe"]:
        return (
            "Reject this plan. A forbidden authorization / unlock / fetch-now flag "
            "was set, or the mission flow has left the human boundary. Resolve the "
            "safety failure in research only; acquire no data, read no dataset, "
            "call no Databento, check no credential."
        )
    return (
        "Hold at the human-controlled boundary. This plan is ready for a SEPARATE "
        "human approval review. Approval of THIS plan would authorize only a "
        "future, read-only data step; it would still acquire no data here and "
        "unlock no gate. A separate, explicitly human-approved step is required "
        "before any read-only inventory or retrieval may begin."
    )


def build_crypto_d1_read_only_data_qa_boundary_plan_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only data QA boundary plan contract. All
    capability flags are False and all gate locks are True regardless of input."""
    data = (
        dict(DEFAULT_PLAN_INPUT) if payload is None else _as_payload(payload)
    )
    assessment = assess_read_only_data_qa_boundary_plan(data)
    datasets = _declared_datasets(data)
    data_store = _norm(data.get("data_store_path")) or PLAN_DEFAULT_DATA_STORE_PATH

    plan = {
        # 1. which local datasets should be inventoried
        "datasets_to_inventory": _dataset_inventory_plan(datasets),
        # 2. which symbols / timeframes are needed
        "needed_symbols": _as_str_list(data.get("needed_symbols"))
        or list(PLAN_DEFAULT_NEEDED_SYMBOLS),
        "needed_timeframes": _as_str_list(data.get("needed_timeframes"))
        or list(PLAN_DEFAULT_NEEDED_TIMEFRAMES),
        "needed_pairs": list(assessment["needed_pairs"]),
        # 3. which data may be missing
        "missing_pairs": list(assessment["missing_pairs"]),
        "covered_pairs": list(assessment["covered_pairs"]),
        # 4. databento credentials/config presence WITHOUT exposing secrets
        "databento_config_present_declared": assessment[
            "databento_config_present_declared"
        ],
        "databento_secret_exposed": False,
        "databento_config_note": (
            "Presence is a static operator assertion only. This contract does not "
            "read, verify, print, or store any credential value."
        ),
        # 5. which read-only data API calls would be needed later
        "read_only_api_calls_needed_later": _read_only_api_calls(
            list(assessment["missing_pairs"])
        ),
        # 6. where data would be stored
        "data_store_path": data_store,
        # 7. which files would be allowed to change in a later approved step
        "allowed_later_change_paths": list(PLAN_ALLOWED_LATER_CHANGE_PATHS),
        # 8. which tests would run
        "scoped_tests": list(PLAN_SCOPED_TESTS),
        # 9. hard-stop conditions
        "hard_stop_conditions": list(PLAN_HARD_STOP_CONDITIONS),
        # 10. confirmation no trading / broker / exec / paper-live / account
        "no_trading_confirmation": {
            "no_trading": True,
            "no_exchange_or_broker_execution": True,
            "no_order_placement": True,
            "no_paper_or_live_trading": True,
            "no_account_or_portfolio_control": True,
            "no_strategy_promotion": True,
            "no_trading_automation": True,
            "no_credentials_in_logs_or_reports": True,
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
        "allowed_later_capabilities": list(PLAN_ALLOWED_LATER_CAPABILITIES),
        "still_forbidden_capabilities": list(PLAN_STILL_FORBIDDEN_CAPABILITIES),
        "plan": plan,
        "plan_summary": (
            "Read-only data QA boundary plan: inventory declared local datasets, "
            "identify the needed Crypto-D1 coverage, list the missing pairs, note "
            "declared Databento config presence (no secret shown), and describe "
            "the read-only retrievals a future approved step WOULD perform. This "
            "plan acquires nothing and unlocks nothing."
        ),
        "operator_next_step": _operator_next_step(assessment),
        "human_operator_required_next_steps": [
            "A human reviews this read-only plan.",
            "A human separately decides whether to approve a future read-only "
            "data step.",
            "A separate, future, explicitly human-approved step is required "
            "before any read-only inventory, retrieval, or dataset inspection "
            "may begin.",
        ],
        "safety_posture": dict(PLAN_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "requires_separate_future_human_approved_step": True,
        "human_approval_required": True,
        "read_only": True,
        "executes": False,
        "research_only": True,
        "fetches_data": False,
        "inspects_datasets": False,
        "calls_databento": False,
        "checks_live_credentials": False,
        "exposes_secret": False,
        "writes_manifest": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
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
    "allowed_later_capabilities",
    "still_forbidden_capabilities",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "paper_live_state",
)

_REQUIRED_PLAN_KEYS: tuple[str, ...] = (
    "datasets_to_inventory",
    "needed_symbols",
    "needed_timeframes",
    "needed_pairs",
    "missing_pairs",
    "covered_pairs",
    "databento_config_present_declared",
    "databento_secret_exposed",
    "read_only_api_calls_needed_later",
    "data_store_path",
    "allowed_later_change_paths",
    "scoped_tests",
    "hard_stop_conditions",
    "no_trading_confirmation",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "fetches_data",
    "inspects_datasets",
    "calls_databento",
    "checks_live_credentials",
    "exposes_secret",
    "writes_manifest",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
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


def validate_crypto_d1_read_only_data_qa_boundary_plan_contract(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built plan contract. Returns a verdict dict of
    boolean checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

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
        and c.get("paper_live_state") == "LOCKED"
    )

    plan = c.get("plan")
    plan_is_dict = isinstance(plan, dict)
    plan_keys_ok = plan_is_dict and all(
        k in plan for k in _REQUIRED_PLAN_KEYS
    )

    # secret never exposed: the declared flag is a bool, the value flag is False,
    # and no key anywhere carries a populated secret-looking field.
    declared_value = plan.get("databento_config_present_declared") if plan_is_dict else None
    databento_presence_is_bool = isinstance(declared_value, bool)
    secret_not_exposed = (
        c.get("exposes_secret") is False
        and (plan.get("databento_secret_exposed") is False if plan_is_dict else False)
    )
    no_secret_value_fields = not _has_secret_value(c)

    # the still-forbidden list must NOT have leaked into allowed-later.
    allowed_later = set(c.get("allowed_later_capabilities") or ())
    still_forbidden = set(c.get("still_forbidden_capabilities") or ())
    no_forbidden_in_allowed = not (allowed_later & still_forbidden)
    forbidden_list_intact = still_forbidden == set(
        PLAN_STILL_FORBIDDEN_CAPABILITIES
    )

    # plan acquires nothing in THIS step.
    acquires_nothing = (
        c.get("fetches_data") is False
        and c.get("inspects_datasets") is False
        and c.get("calls_databento") is False
        and c.get("checks_live_credentials") is False
        and c.get("writes_manifest") is False
    )

    # the trading confirmation block must affirm all eight no-execution facts.
    confirmation = plan.get("no_trading_confirmation") if plan_is_dict else None
    no_trading_confirmed = isinstance(confirmation, dict) and all(
        confirmation.get(k) is True
        for k in (
            "no_trading",
            "no_exchange_or_broker_execution",
            "no_order_placement",
            "no_paper_or_live_trading",
            "no_account_or_portfolio_control",
            "no_strategy_promotion",
            "no_trading_automation",
            "no_credentials_in_logs_or_reports",
        )
    )

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
        "databento_presence_is_bool": databento_presence_is_bool,
        "secret_not_exposed": secret_not_exposed,
        "no_secret_value_fields": no_secret_value_fields,
        "no_forbidden_in_allowed": no_forbidden_in_allowed,
        "forbidden_list_intact": forbidden_list_intact,
        "acquires_nothing": acquires_nothing,
        "no_trading_confirmed": no_trading_confirmed,
        "no_trade_language": no_trade_language,
    }
    verdict = dict(checks)
    verdict["missing_fields"] = missing
    verdict["valid"] = (not missing) and all(checks.values())
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


def render_crypto_d1_read_only_data_qa_boundary_plan_contract_markdown(
    contract: Any,
) -> str:
    """Render a built plan contract as a deterministic markdown brief. Pure string
    formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    plan = c.get("plan") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Read-Only Real Data QA Boundary Plan")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Mission flow stage: " + str(c.get("mission_flow_current_stage", ""))
    )
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))
    lines.append(
        "- Databento config present (declared): "
        + str(plan.get("databento_config_present_declared", False))
        + " (no secret shown)"
    )

    _emit(
        lines,
        "1. Datasets To Inventory (later, read-only)",
        [
            str(d.get("name")) + " @ " + str(d.get("path"))
            for d in (plan.get("datasets_to_inventory") or [])
        ],
    )
    _emit(
        lines,
        "2. Needed Symbols / Timeframes",
        [
            "symbols: " + ", ".join(plan.get("needed_symbols") or []),
            "timeframes: " + ", ".join(plan.get("needed_timeframes") or []),
        ],
    )
    _emit(lines, "3. Possibly Missing Pairs", list(plan.get("missing_pairs") or []))
    _emit(
        lines,
        "4. Databento Config Presence (no secret)",
        [str(plan.get("databento_config_note", ""))],
    )
    _emit(
        lines,
        "5. Read-Only API Calls Needed Later",
        list(plan.get("read_only_api_calls_needed_later") or []),
    )
    _emit(lines, "6. Data Store Path", [str(plan.get("data_store_path", ""))])
    _emit(
        lines,
        "7. Files Allowed To Change In A Later Approved Step",
        list(plan.get("allowed_later_change_paths") or []),
    )
    _emit(lines, "8. Tests That Would Run", list(plan.get("scoped_tests") or []))
    _emit(
        lines,
        "9. Hard-Stop Conditions",
        list(plan.get("hard_stop_conditions") or []),
    )
    _emit(
        lines,
        "10. No-Execution Confirmation",
        [
            str(k) + ": " + str(v)
            for k, v in (plan.get("no_trading_confirmation") or {}).items()
        ],
    )
    _emit(lines, "Still Forbidden (always)", list(c.get("still_forbidden_capabilities") or []))
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)
