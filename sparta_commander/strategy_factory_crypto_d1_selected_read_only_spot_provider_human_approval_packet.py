"""Human Approval Packet for Selected Read-Only Spot Provider Run (Block 149).

A PURE, stdlib-only, *read-only* CONTRACT / PACKET layer. It DESCRIBES the exact
scope of a FUTURE, human-approved read-only acquisition run for the source the
Block 148 orchestrator already selected (the clear-license READ-ONLY spot historical
provider). It is the human-approval gate that sits between the automated selection
(Block 148) and any future run block.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

THIS packet executes NOTHING. It does NOT call a provider, fetch data, import a CSV,
read or parse any file's contents, write any file, open a network, read or inspect
any credential, read a .env file, print / store / log any secret, run validation /
QA / baseline / backtest, touch any broker / exchange / trading / account / order /
portfolio endpoint, or unlock any gate -- even when a caller passes
human_spot_provider_run_approved. It only emits a deterministic, static description
of the future run scope, the required human approval flag, the allowed
symbols / timeframe / paths, the provider-safety criteria, the required future
outputs, and the hard stops.

CORE RULE: describing a future run authorizes nothing and runs nothing. No provider
is called, no data is fetched, no file is read or written, no credential is read,
and no gate is unlocked. The actual read-only acquisition run is a SEPARATE, future,
human-approved action OUTSIDE this packet. real_data_qa stays BLOCKED, baseline
stays BLOCKED, and paper / micro-live stay LOCKED.

Public API:
  - PACKET_SCHEMA_VERSION / PACKET_LABEL / PACKET_STATUS / PACKET_MODE / PACKET_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - SELECTED_CANDIDATE_TYPE / DEFAULT_SELECTED_CANDIDATE_NAME
  - REQUIRED_RUN_APPROVAL_FLAG
  - PACKET_APPROVED_SYMBOLS / PACKET_APPROVED_TIMEFRAMES / PACKET_SYMBOL_ALIASES
  - PACKET_APPROVED_CACHE_PATH / PACKET_APPROVED_REPORT_DIR
  - PACKET_PROVIDER_CRITERIA / PACKET_REQUIRED_FUTURE_OUTPUTS / PACKET_HARD_STOPS
  - NEXT_RECOMMENDED_ACTION / PACKET_SAFETY_POSTURE / DEFAULT_PACKET_INPUT
  - build_crypto_d1_selected_read_only_spot_provider_human_approval_packet(payload=None)
  - validate_crypto_d1_selected_read_only_spot_provider_human_approval_packet(contract)
  - render_crypto_d1_selected_read_only_spot_provider_human_approval_packet_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    FETCH_APPROVED_SYMBOLS,
    FETCH_APPROVED_TIMEFRAMES,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

PACKET_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_selected_read_only_spot_provider_human_approval_packet.v1"
)
PACKET_LABEL = (
    "Block 149 - Human Approval Packet for Selected Read-Only Spot Provider Run"
)
PACKET_STATUS = "HUMAN_APPROVAL_PACKET_ONLY"
PACKET_MODE = "RESEARCH_ONLY"

PACKET_CORE_RULE = (
    "Describing a future read-only provider run authorizes nothing and runs nothing. "
    "No provider is called, no API is called, no network is opened, no data is "
    "fetched, no CSV is imported, no file content is read, no file is written, no "
    "credential is read, and no .env is read -- even when "
    "human_spot_provider_run_approved is passed. The actual read-only acquisition "
    "run is a SEPARATE, future, human-approved action OUTSIDE this packet. "
    "real_data_qa stays BLOCKED, baseline stays BLOCKED, and paper / micro-live "
    "stay LOCKED."
)

# The source the Block 148 orchestrator already selected.
SELECTED_CANDIDATE_TYPE = "CLEAR_LICENSE_READ_ONLY_SPOT_HISTORICAL_PROVIDER"
DEFAULT_SELECTED_CANDIDATE_NAME = "clear_license_readonly_spot_history_api_archetype"

# The explicit human approval flag a FUTURE run block must require.
REQUIRED_RUN_APPROVAL_FLAG = "human_spot_provider_run_approved"

PACKET_APPROVED_SYMBOLS: tuple[str, ...] = FETCH_APPROVED_SYMBOLS
PACKET_APPROVED_TIMEFRAMES: tuple[str, ...] = FETCH_APPROVED_TIMEFRAMES

# Acceptable written forms for each approved symbol (normalized by removing the
# slash / dash and upper-casing -- e.g. "BTC/USD" -> "BTCUSD").
PACKET_SYMBOL_ALIASES: dict[str, tuple[str, ...]] = {
    "BTCUSD": ("BTCUSD", "BTC/USD", "BTC-USD", "XBTUSD"),
    "ETHUSD": ("ETHUSD", "ETH/USD", "ETH-USD"),
    "SOLUSD": ("SOLUSD", "SOL/USD", "SOL-USD"),
}

# Approved FUTURE-only paths (recorded only; NOTHING is written / read / created).
PACKET_APPROVED_CACHE_PATH = "data/crypto_d1_spot_cache/"
PACKET_APPROVED_REPORT_DIR = "reports/research_os/data_qa/"

# 8. Provider-safety criteria the FUTURE run's provider must satisfy.
PACKET_PROVIDER_CRITERIA: tuple[str, ...] = (
    "Read-only historical spot market data.",
    "Clear license / source metadata.",
    "No trading endpoint required.",
    "No broker / exchange account control.",
    "No order endpoint.",
    "No portfolio endpoint.",
    "No paper / live endpoint.",
    "No credential printing / logging / storing.",
)

# 9. Required FUTURE run outputs (produced only in a separate, future approved step).
PACKET_REQUIRED_FUTURE_OUTPUTS: tuple[str, ...] = (
    "Local cached OHLCV data files only, under the approved cache path "
    "(data/crypto_d1_spot_cache/).",
    "Manifest / gap report only, under the approved report path "
    "(reports/research_os/data_qa/).",
)

# 10. Hard stops.
PACKET_HARD_STOPS: tuple[str, ...] = (
    "wrong symbol (not BTCUSD / ETHUSD / SOLUSD).",
    "wrong timeframe (not 1d).",
    "wrong instrument type (not spot).",
    "unclear source / license.",
    "trading / account / order / portfolio endpoint.",
    "credential / secret exposure.",
    "any write outside the approved paths.",
    "any QA / backtest / paper / live attempt.",
    "any runtime / dashboard write.",
    "any gate unlock attempt.",
)

# The single next recommended action this packet emits.
NEXT_RECOMMENDED_ACTION = "HOLD_FOR_EXPLICIT_HUMAN_PROVIDER_RUN_APPROVAL"

# Top-level flags that, if truthy on an operator's input, mark it unsafe.
PACKET_FORBIDDEN_FLAGS: tuple[str, ...] = (
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
    "unlocks_downstream_gate",
    "print_credentials",
    "expose_secret",
    "inspect_dotenv",
    "call_provider_now",
    "fetch_data_now",
    "run_provider_now",
    "import_csv_now",
    "read_file_contents_now",
    "write_cache_now",
    "write_report_now",
    "run_qa_now",
    "run_backtest_now",
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "place_order",
    "go_live",
)

# Execution / promotion verbs the authored NARRATIVE must never contain as whole
# words.
PACKET_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Read-only safety posture. Posture facts are True; every capability flag is False.
PACKET_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "human_run_approval_required": True,
    "executes": False,
    "calls_provider": False,
    "performs_data_fetch": False,
    "performs_data_import": False,
    "imports_csv": False,
    "reads_file_contents": False,
    "calls_provider_api": False,
    "connects_provider": False,
    "uses_network": False,
    "fetches_data": False,
    "checks_live_credentials": False,
    "reads_dotenv": False,
    "exposes_secret": False,
    "reads_data_files": False,
    "writes_data_files": False,
    "writes_cache": False,
    "writes_report": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "runs_validation": False,
    "runs_qa": False,
    "runs_backtest": False,
    "runs_simulation": False,
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

# Deterministic static input. No real data, no secret, no run.
DEFAULT_PACKET_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 selected read-only spot provider approval packet input (static)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "human_spot_provider_run_approved": False,
    "selected_candidate_name": DEFAULT_SELECTED_CANDIDATE_NAME,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
}


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _as_payload(payload: Any) -> dict[str, Any]:
    return dict(payload) if isinstance(payload, dict) else {}


def _is_truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _clean_name(value: Any) -> str:
    """Return a sanitized candidate name: printable, no secret-bearing content. A
    name is metadata only; a non-string or empty value falls back to the default."""
    if not isinstance(value, str) or not value.strip():
        return DEFAULT_SELECTED_CANDIDATE_NAME
    return value.strip()


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


_SECRET_VALUE_TOKENS: tuple[str, ...] = (
    "api_key",
    "apikey",
    "secret",
    "password",
    "private_key",
    "bearer",
    "access_token",
)


def _has_secret_value(obj: Any) -> bool:
    """True if any dict key looks like a secret AND carries a non-empty string
    value. A secret VALUE is always a string; booleans / counts are flags."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_l = str(key).lower()
            looks_secret = any(tok in key_l for tok in _SECRET_VALUE_TOKENS)
            if looks_secret and isinstance(value, str) and value.strip():
                return True
            if _has_secret_value(value):
                return True
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            if _has_secret_value(item):
                return True
    return False


# --------------------------------------------------------------------------- #
# packet build
# --------------------------------------------------------------------------- #
def build_crypto_d1_selected_read_only_spot_provider_human_approval_packet(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the human approval packet. Every capability flag is
    False and every gate lock is True regardless of input -- including when
    human_spot_provider_run_approved is passed. The packet runs nothing; the next
    recommended action is always HOLD_FOR_EXPLICIT_HUMAN_PROVIDER_RUN_APPROVAL."""
    data = dict(DEFAULT_PACKET_INPUT) if payload is None else _as_payload(payload)

    mf_stage = data.get("mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE)
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_flag_hits = [
        f for f in PACKET_FORBIDDEN_FLAGS if _is_truthy(data.get(f))
    ]
    safe = mission_flow_aligned and not forbidden_flag_hits

    selected_candidate_name = _clean_name(data.get("selected_candidate_name"))
    run_approved_echo = _is_truthy(data.get(REQUIRED_RUN_APPROVAL_FLAG))

    approval_packet = {
        # 1 + 2: selected source
        "selected_candidate_type": SELECTED_CANDIDATE_TYPE,
        "selected_candidate_name": selected_candidate_name,
        # 3: required future approval flag
        "required_run_approval_flag": REQUIRED_RUN_APPROVAL_FLAG,
        "required_run_approval_value": True,
        "human_run_approval_required": True,
        "human_run_approved_echo": run_approved_echo,
        "run_executed": False,
        "run_performed_by_this_block": False,
        # 4 + 5: approved scope
        "approved_symbols": list(PACKET_APPROVED_SYMBOLS),
        "approved_timeframes": list(PACKET_APPROVED_TIMEFRAMES),
        "symbol_aliases": {k: list(v) for k, v in PACKET_SYMBOL_ALIASES.items()},
        # 6 + 7: approved future paths
        "approved_future_cache_path": PACKET_APPROVED_CACHE_PATH,
        "approved_future_report_dir": PACKET_APPROVED_REPORT_DIR,
        # 8: provider criteria
        "provider_criteria": list(PACKET_PROVIDER_CRITERIA),
        # 9: required future outputs
        "required_future_outputs": list(PACKET_REQUIRED_FUTURE_OUTPUTS),
        # 10: hard stops
        "hard_stops": list(PACKET_HARD_STOPS),
        "what_a_human_must_approve": (
            "A SEPARATE, future block performs the read-only acquisition run for the "
            "selected clear-license read-only spot historical provider ONLY after an "
            "explicit human_spot_provider_run_approved=True decision. This packet "
            "calls no provider, fetches nothing, reads / writes no file, and unlocks "
            "no gate."
        ),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
    }

    contract: dict[str, Any] = {
        "schema_version": PACKET_SCHEMA_VERSION,
        "label": PACKET_LABEL,
        "status": PACKET_STATUS,
        "mode": PACKET_MODE,
        "core_rule": PACKET_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": mission_flow_aligned,
        "safe": safe,
        "forbidden_flag_hits": list(forbidden_flag_hits),
        "approval_packet": approval_packet,
        # promoted top-level required outputs
        "selected_candidate_type": SELECTED_CANDIDATE_TYPE,
        "selected_candidate_name": selected_candidate_name,
        "required_run_approval_flag": REQUIRED_RUN_APPROVAL_FLAG,
        "approved_symbols": list(PACKET_APPROVED_SYMBOLS),
        "approved_timeframes": list(PACKET_APPROVED_TIMEFRAMES),
        "approved_future_cache_path": PACKET_APPROVED_CACHE_PATH,
        "approved_future_report_dir": PACKET_APPROVED_REPORT_DIR,
        "provider_criteria": list(PACKET_PROVIDER_CRITERIA),
        "required_future_outputs": list(PACKET_REQUIRED_FUTURE_OUTPUTS),
        "hard_stops": list(PACKET_HARD_STOPS),
        "next_recommended_action": NEXT_RECOMMENDED_ACTION,
        "packet_summary": (
            "Read-only HUMAN APPROVAL PACKET describing the exact scope of a FUTURE, "
            "human-approved read-only acquisition run for the selected clear-license "
            "spot historical provider (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d). It defines "
            "the required approval flag, the allowed symbols / timeframe / paths, the "
            "provider-safety criteria, the required future outputs, and the hard "
            "stops. THIS packet describes only -- it calls no provider, fetches "
            "nothing, reads / writes no file, and unlocks no gate."
        ),
        "operator_next_step": (
            "A human reviews this approval packet and, as a SEPARATE action, decides "
            "whether to authorize a future read-only acquisition run by setting "
            "human_spot_provider_run_approved=True for a separate run block. "
            "Reviewing this packet calls no provider, fetches no data, reads no file, "
            "writes nothing, and unlocks no gate; the recommended next action is "
            "HOLD_FOR_EXPLICIT_HUMAN_PROVIDER_RUN_APPROVAL."
        ),
        "human_operator_required_next_steps": [
            "A human reviews this read-only approval packet.",
            "A human separately sets human_spot_provider_run_approved=True to "
            "authorize a future read-only acquisition run OUTSIDE this packet.",
            "Only after that separate human-approved run + validation step could "
            "local cached spot data exist; this packet writes nothing and unlocks "
            "no gate.",
        ],
        "requires_human_run_approval": True,
        "this_packet_calls_provider": False,
        "this_packet_fetches_data": False,
        "this_packet_reads_files": False,
        "this_packet_writes_files": False,
        "this_packet_runs_acquisition": False,
        "human_run_approved_echo": run_approved_echo,
        "run_executed": False,
        "safety_posture": dict(PACKET_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "read_only": True,
        "research_only": True,
        "executes": False,
        "calls_provider": False,
        "performs_data_fetch": False,
        "performs_data_import": False,
        "imports_csv": False,
        "reads_file_contents": False,
        "calls_provider_api": False,
        "connects_provider": False,
        "uses_network": False,
        "fetches_data": False,
        "checks_live_credentials": False,
        "reads_dotenv": False,
        "exposes_secret": False,
        "reads_data_files": False,
        "writes_data_files": False,
        "writes_cache": False,
        "writes_report": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
        "runs_validation": False,
        "runs_qa": False,
        "runs_backtest": False,
        "runs_simulation": False,
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
    "approval_packet",
    "selected_candidate_type",
    "selected_candidate_name",
    "required_run_approval_flag",
    "approved_symbols",
    "approved_timeframes",
    "approved_future_cache_path",
    "approved_future_report_dir",
    "provider_criteria",
    "required_future_outputs",
    "hard_stops",
    "next_recommended_action",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_REQUIRED_PACKET_KEYS: tuple[str, ...] = (
    "selected_candidate_type",
    "selected_candidate_name",
    "required_run_approval_flag",
    "required_run_approval_value",
    "human_run_approval_required",
    "run_executed",
    "approved_symbols",
    "approved_timeframes",
    "approved_future_cache_path",
    "approved_future_report_dir",
    "provider_criteria",
    "required_future_outputs",
    "hard_stops",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "calls_provider",
    "performs_data_fetch",
    "performs_data_import",
    "imports_csv",
    "reads_file_contents",
    "calls_provider_api",
    "connects_provider",
    "uses_network",
    "fetches_data",
    "checks_live_credentials",
    "reads_dotenv",
    "exposes_secret",
    "reads_data_files",
    "writes_data_files",
    "writes_cache",
    "writes_report",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
    "runs_validation",
    "runs_qa",
    "runs_backtest",
    "runs_simulation",
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


def validate_crypto_d1_selected_read_only_spot_provider_human_approval_packet(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built human approval packet. Returns a verdict dict of
    boolean checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing_fields = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == PACKET_SCHEMA_VERSION
    label_ok = c.get("label") == PACKET_LABEL
    status_ok = c.get("status") == PACKET_STATUS
    mode_ok = c.get("mode") == PACKET_MODE
    core_rule_ok = c.get("core_rule") == PACKET_CORE_RULE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    calls_provider_false = c.get("calls_provider") is False
    fetches_false = c.get("fetches_data") is False
    this_calls_false = c.get("this_packet_calls_provider") is False
    this_fetches_false = c.get("this_packet_fetches_data") is False
    this_reads_false = c.get("this_packet_reads_files") is False
    this_writes_false = c.get("this_packet_writes_files") is False
    this_runs_false = c.get("this_packet_runs_acquisition") is False
    run_executed_false = c.get("run_executed") is False
    human_approval_required = c.get("requires_human_run_approval") is True
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == PACKET_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
    )
    next_action_ok = c.get("next_recommended_action") == NEXT_RECOMMENDED_ACTION

    selected_type_ok = c.get("selected_candidate_type") == SELECTED_CANDIDATE_TYPE
    approval_flag_ok = c.get("required_run_approval_flag") == REQUIRED_RUN_APPROVAL_FLAG
    symbols_ok = c.get("approved_symbols") == list(PACKET_APPROVED_SYMBOLS)
    timeframes_ok = c.get("approved_timeframes") == list(PACKET_APPROVED_TIMEFRAMES)
    cache_path_ok = c.get("approved_future_cache_path") == PACKET_APPROVED_CACHE_PATH
    report_dir_ok = c.get("approved_future_report_dir") == PACKET_APPROVED_REPORT_DIR
    provider_criteria_ok = c.get("provider_criteria") == list(PACKET_PROVIDER_CRITERIA)
    future_outputs_ok = c.get("required_future_outputs") == list(
        PACKET_REQUIRED_FUTURE_OUTPUTS
    )
    hard_stops_ok = c.get("hard_stops") == list(PACKET_HARD_STOPS)

    packet = c.get("approval_packet")
    packet_is_dict = isinstance(packet, dict)
    packet_keys_ok = packet_is_dict and all(
        k in packet for k in _REQUIRED_PACKET_KEYS
    )
    packet_locked_ok = packet_is_dict and (
        packet.get("required_run_approval_value") is True
        and packet.get("human_run_approval_required") is True
        and packet.get("run_executed") is False
        and packet.get("run_performed_by_this_block") is False
        and packet.get("real_data_qa_state") == "BLOCKED"
        and packet.get("baseline_backtest_state") == "BLOCKED"
        and packet.get("paper_live_state") == "LOCKED"
    )

    no_secret_value_fields = not _has_secret_value(c)

    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "packet_summary", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(PACKET_FORBIDDEN_TRADE_TERMS))

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "status_ok": status_ok,
        "mode_ok": mode_ok,
        "core_rule_ok": core_rule_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "calls_provider_false": calls_provider_false,
        "fetches_false": fetches_false,
        "this_calls_false": this_calls_false,
        "this_fetches_false": this_fetches_false,
        "this_reads_false": this_reads_false,
        "this_writes_false": this_writes_false,
        "this_runs_false": this_runs_false,
        "run_executed_false": run_executed_false,
        "human_approval_required": human_approval_required,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "next_action_ok": next_action_ok,
        "selected_type_ok": selected_type_ok,
        "approval_flag_ok": approval_flag_ok,
        "symbols_ok": symbols_ok,
        "timeframes_ok": timeframes_ok,
        "cache_path_ok": cache_path_ok,
        "report_dir_ok": report_dir_ok,
        "provider_criteria_ok": provider_criteria_ok,
        "future_outputs_ok": future_outputs_ok,
        "hard_stops_ok": hard_stops_ok,
        "packet_keys_ok": packet_keys_ok,
        "packet_locked_ok": packet_locked_ok,
        "no_secret_value_fields": no_secret_value_fields,
        "no_trade_language": no_trade_language,
    }
    verdict = dict(checks)
    verdict["missing_fields"] = missing_fields
    verdict["valid"] = (not missing_fields) and all(checks.values())
    return verdict


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


def render_crypto_d1_selected_read_only_spot_provider_human_approval_packet_markdown(
    contract: Any,
) -> str:
    """Render a built human approval packet as a deterministic markdown brief. Pure
    string formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append(
        "# Human Approval Packet for Selected Read-Only Spot Provider Run"
    )
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Selected candidate type: " + str(c.get("selected_candidate_type", ""))
    )
    lines.append(
        "- Selected candidate name: " + str(c.get("selected_candidate_name", ""))
    )
    lines.append(
        "- Required run approval flag: "
        + str(c.get("required_run_approval_flag", ""))
        + "=True"
    )
    lines.append(
        "- Next recommended action: " + str(c.get("next_recommended_action", ""))
    )
    lines.append(
        "- This packet calls provider: "
        + str(c.get("this_packet_calls_provider", False))
    )
    lines.append(
        "- This packet fetches data: "
        + str(c.get("this_packet_fetches_data", False))
    )
    lines.append("- Run executed: " + str(c.get("run_executed", False)))
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(lines, "Approved Symbols", list(c.get("approved_symbols") or []))
    _emit(lines, "Approved Timeframe", list(c.get("approved_timeframes") or []))
    _emit(
        lines,
        "Approved Future Paths (recorded only; nothing written)",
        [
            "approved_future_cache_path: "
            + str(c.get("approved_future_cache_path", "")),
            "approved_future_report_dir: "
            + str(c.get("approved_future_report_dir", "")),
        ],
    )
    _emit(lines, "Provider Criteria", list(c.get("provider_criteria") or []))
    _emit(
        lines,
        "Required Future Outputs",
        list(c.get("required_future_outputs") or []),
    )
    _emit(lines, "Hard Stops", list(c.get("hard_stops") or []))
    _emit(
        lines,
        "Next Recommended Action",
        [str(c.get("next_recommended_action", ""))],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)
