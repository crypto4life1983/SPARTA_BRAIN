"""Crypto-D1 Real Data QA Plan-Only Contract (Block 171).

A PURE, stdlib-only, *read-only* PAPER contract. It is the concrete realization of
the operator's PREPARE_REAL_DATA_QA_PLAN_ONLY decision taken at the parked
mission-flow boundary

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

It defines -- ON PAPER ONLY -- the exact scope of a FUTURE, separately
human-controlled, read-only Real Data QA step: the QA checks, the selected
read-only spot provider boundaries, the dataset manifest requirements, the allowed
symbols / timeframe / instrument type, the rejection conditions, the abort rules,
and the safety gates that must stay shut. It is a plan, not an action.

THIS contract executes NOTHING. It does NOT fetch, acquire, download, inspect,
read, or transform any data, runs no QA, no baseline, no backtest, no simulation,
touches no broker / exchange / order / account / paper / live surface, activates
no automation, performs no auto-push, opens no network, reads no .env, inspects no
credential, shows no secret, reads or writes no file, writes no manifest, spawns
no subprocess, reads no environment variable, mints no id, and records no
timestamp. It only assembles a static, deterministic plan and emits it for human
review.

CORE RULE: assembling or reading this plan authorizes nothing and crosses no
real-world boundary. It NEVER unlocks Real Data QA. real_data_qa stays BLOCKED,
baseline stays BLOCKED, and paper / micro-live stay LOCKED. The QA step this plan
describes is a SEPARATE, future, explicitly human-controlled act; writing the plan
performs none of it.

Public API:
  - PLAN_SCHEMA_VERSION / PLAN_LABEL / PLAN_STATUS / PLAN_MODE / PLAN_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - QA_SCOPE_CHECKS
  - PROVIDER_BOUNDARIES
  - DATASET_MANIFEST_REQUIREMENTS
  - ALLOWED_SYMBOLS / ALLOWED_TIMEFRAME / ALLOWED_INSTRUMENT_TYPE
  - REJECTION_CONDITIONS
  - ABORT_RULES
  - SAFETY_GATES
  - PLAN_FORBIDDEN_FLAGS / PLAN_FORBIDDEN_TRADE_TERMS
  - PLAN_SAFETY_POSTURE / DEFAULT_PLAN_INPUT
  - build_real_data_qa_plan_only_contract(payload=None)
  - validate_real_data_qa_plan_only_contract(contract)
  - render_real_data_qa_plan_only_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

# Single source of truth for the parked boundary constants: re-exported from the
# Block 136 human-approval-packet CONTRACT (a pure, stdlib-only sibling). The
# companion test additionally cross-checks these against the live mission-flow
# status module so neither can silently drift.
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract import (  # noqa: E501
    RDQ_APPROVAL_MISSION_FLOW_CURRENT_STAGE as MISSION_FLOW_CURRENT_STAGE,
    RDQ_APPROVAL_MISSION_FLOW_NEXT_REQUIRED_ACTION as MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

PLAN_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_real_data_qa_plan_only_contract.v1"
)
PLAN_LABEL = "Block 171 - Crypto-D1 Real Data QA Plan-Only Contract"
PLAN_STATUS = "READ_ONLY_REAL_DATA_QA_PLAN_ONLY"
PLAN_MODE = "RESEARCH_ONLY"

PLAN_CORE_RULE = (
    "This contract is a plan-only document for a FUTURE, separately "
    "human-controlled, read-only Real Data QA step. Assembling or reading it "
    "authorizes nothing and crosses no real-world boundary: no data is fetched or "
    "inspected, no QA / baseline / backtest / simulation is run, no broker / "
    "exchange / order surface is touched, no automation or auto-push fires, no "
    "network is opened, no credential or .env is read, no secret is shown, and no "
    "manifest or artifact is written. It NEVER unlocks Real Data QA. real_data_qa "
    "stays BLOCKED, baseline stays BLOCKED, and paper / micro-live stay LOCKED."
)

# The read-only QA checks the FUTURE step would perform. Each is a description of
# a check; this contract performs none of them. (id, description).
QA_SCOPE_CHECKS: tuple[tuple[str, str], ...] = (
    (
        "schema_conformance",
        "Confirm each row exposes exactly the required OHLCV schema and types; "
        "read-only inspection only.",
    ),
    (
        "null_check",
        "Confirm no required field is null / missing across the dataset.",
    ),
    (
        "duplicate_check",
        "Confirm there are no duplicate (symbol, date) rows.",
    ),
    (
        "timestamp_monotonicity",
        "Confirm dates are strictly increasing per symbol with no reordering.",
    ),
    (
        "gap_detection",
        "Confirm there are no unexplained daily gaps in the date sequence.",
    ),
    (
        "range_sanity",
        "Confirm open/high/low/close are positive and low <= open/close <= high; "
        "volume is non-negative.",
    ),
    (
        "row_count_minimums",
        "Confirm each symbol meets a minimum row count for the approved range.",
    ),
    (
        "symbol_coverage",
        "Confirm every approved symbol is present and no unapproved symbol is.",
    ),
    (
        "ohlcv_field_presence",
        "Confirm date/open/high/low/close/volume/source/instrument_type are all "
        "present.",
    ),
    (
        "instrument_type_spot_only",
        "Confirm instrument_type is 'spot' for every row; reject anything else.",
    ),
)

# Boundaries on the selected read-only spot provider (carried from the Block 151 /
# 168 adapter rules). These are constraints on a FUTURE step, asserted here only.
PROVIDER_BOUNDARIES: tuple[str, ...] = (
    "Exactly one selected read-only spot provider; no second/live provider.",
    "Read-only daily spot OHLCV method only (fetch_read_only_daily_spot_ohlcv).",
    "Spot instrument type only; reject futures, perps, and dated contracts.",
    "No account-authenticated, order, trade, balance, or position endpoint.",
    "Clear, stated data source and license; reject unclear or unlicensed data.",
    "No credential required for read-only access; none is held or read here.",
    "No network call, endpoint hit, or URL fetch performed by this plan.",
)

# What a future dataset manifest MUST contain before any QA step. Listing a
# requirement neither writes a manifest nor satisfies it. (field, description).
DATASET_MANIFEST_REQUIREMENTS: tuple[tuple[str, str], ...] = (
    ("provider_name", "The single selected read-only spot provider name."),
    ("source_license", "The stated data source and its license / terms."),
    ("symbols", "The explicit list of approved symbols (must match allowlist)."),
    ("timeframe", "The timeframe; must be the approved daily timeframe."),
    ("instrument_type", "Must be 'spot'."),
    ("date_range_start", "Inclusive start date of the approved range."),
    ("date_range_end", "Inclusive end date of the approved range."),
    ("files", "Per-file path, row count, and checksum for integrity."),
    ("required_fields", "The required OHLCV field list each file must expose."),
    ("read_only_attestation", "An attestation that access is read-only only."),
)

# The approved data scope for a FUTURE QA step. These are data identifiers, not
# trading instructions; nothing here is bought, sold, or traded.
ALLOWED_SYMBOLS: tuple[str, ...] = ("BTC-USD", "ETH-USD")
ALLOWED_TIMEFRAME = "1d"
ALLOWED_INSTRUMENT_TYPE = "spot"

# Conditions that REJECT a dataset at QA time. Stating a condition rejects
# nothing now; it defines what a future step would refuse. (id, description).
REJECTION_CONDITIONS: tuple[tuple[str, str], ...] = (
    (
        "wrong_instrument_type",
        "Any row whose instrument_type is not 'spot' (e.g. futures / perp).",
    ),
    (
        "missing_required_field",
        "Any missing required OHLCV field in any row.",
    ),
    (
        "non_daily_timeframe",
        "Any timeframe other than the approved daily timeframe.",
    ),
    (
        "unapproved_symbol",
        "Any symbol not on the approved allowlist.",
    ),
    (
        "unclear_source_or_license",
        "Any dataset whose source or license is unclear or unstated.",
    ),
    (
        "credentialed_provider",
        "Any provider that requires account authentication or credentials.",
    ),
    (
        "schema_mismatch",
        "Any schema / type mismatch against the required OHLCV schema.",
    ),
    (
        "non_monotonic_timestamps",
        "Any non-increasing or reordered dates within a symbol.",
    ),
    (
        "duplicate_rows",
        "Any duplicate (symbol, date) rows.",
    ),
    (
        "out_of_range_values",
        "Any non-positive price, inverted high/low, or negative volume.",
    ),
)

# Conditions that ABORT the entire QA step immediately (harder than a per-dataset
# rejection). Any of these means the boundary would be crossed -- never allowed.
ABORT_RULES: tuple[tuple[str, str], ...] = (
    (
        "network_or_endpoint_attempted",
        "Any network call, endpoint hit, or URL fetch is attempted -> ABORT.",
    ),
    (
        "credential_required_or_read",
        "Any credential / .env / secret is required or read -> ABORT.",
    ),
    (
        "write_outside_read_only",
        "Any write to runtime / dashboard / storage / data is attempted -> ABORT.",
    ),
    (
        "execution_or_trade_surface_touched",
        "Any broker / exchange / order / trade / account surface is touched -> ABORT.",
    ),
    (
        "gate_unlock_requested",
        "Any unlock of real_data_qa / baseline / paper / micro-live is requested "
        "-> ABORT.",
    ),
    (
        "boundary_crossing_required",
        "Any step that would cross the human-controlled real data QA boundary "
        "-> ABORT.",
    ),
)

# The gates that stay shut, always. (gate, state).
SAFETY_GATES: tuple[tuple[str, str], ...] = (
    ("real_data_qa", "BLOCKED"),
    ("baseline_backtest", "BLOCKED"),
    ("paper_trading_gate", "LOCKED"),
    ("micro_live_gate", "LOCKED"),
    ("real_strategy_intake", "BLOCKED"),
)

# Top-level flags that, if truthy on an operator's input, mark it unsafe. Any of
# these means the caller tried to bend this plan into an authorization.
PLAN_FORBIDDEN_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "authorizes_qa_baseline",
    "authorizes_data_fetch",
    "unlocks_downstream_gate",
    "print_credentials",
    "expose_secret",
    "inspect_dotenv",
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
    "run_qa_now",
    "run_baseline_now",
    "run_backtest_now",
    "run_simulation_now",
    "fetch_data_now",
    "inspect_dataset_now",
    "access_credentials",
    "write_manifest_now",
    "activate_automation",
    "enable_auto_push",
    "write_runtime_artifact",
    "write_dashboard_artifact",
    "write_storage_artifact",
    "contact_broker",
    "contact_exchange",
    "place_order",
    "go_live",
)

# Execution / promotion verbs the authored narrative must never contain as whole
# words.
PLAN_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Read-only safety posture. Posture facts are True; every capability / execution
# flag is False.
PLAN_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "plan_only": True,
    "human_decision_required": True,
    "parked_at_boundary": True,
    "executes": False,
    "performs_data_fetch": False,
    "inspects_dataset": False,
    "reads_data_files": False,
    "writes_data_files": False,
    "writes_manifest": False,
    "uses_network": False,
    "reads_dotenv": False,
    "exposes_secret": False,
    "accesses_credentials": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "writes_storage_outputs": False,
    "runs_qa": False,
    "runs_baseline": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "contacts_broker": False,
    "contacts_exchange": False,
    "activates_automation": False,
    "performs_auto_push": False,
    "generates_trade_signal": False,
    "generates_order": False,
    "authorizes_trading": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_order_placement": False,
    "authorizes_account_control": False,
    "authorizes_portfolio_control": False,
    "authorizes_strategy_promotion": False,
    "authorizes_automation_trading": False,
    "authorizes_data_fetch": False,
    "authorizes_qa_baseline": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}

# Deterministic static input. No real data, no secret, no authorization flag.
DEFAULT_PLAN_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 real data QA plan-only contract input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
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
    value. A secret VALUE is always a string; booleans and counts are flags."""
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
# plan build
# --------------------------------------------------------------------------- #
def _pairs_to_records(
    pairs: tuple[tuple[str, str], ...], key_a: str, key_b: str
) -> list[dict[str, Any]]:
    return [{key_a: a, key_b: b} for a, b in pairs]


def build_real_data_qa_plan_only_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only Real Data QA plan-only contract.
    Every capability / execution flag is False and every gate lock is True
    regardless of input. The plan authorizes nothing and unlocks nothing."""
    data = dict(DEFAULT_PLAN_INPUT) if payload is None else _as_payload(payload)

    mf_stage = data.get("mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE)
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_flag_hits = [
        f for f in PLAN_FORBIDDEN_FLAGS if _is_truthy(data.get(f))
    ]
    safe = mission_flow_aligned and not forbidden_flag_hits

    qa_plan = {
        "parked_stage": MISSION_FLOW_CURRENT_STAGE,
        "parked_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "qa_scope_checks": _pairs_to_records(QA_SCOPE_CHECKS, "id", "description"),
        "provider_boundaries": list(PROVIDER_BOUNDARIES),
        "dataset_manifest_requirements": _pairs_to_records(
            DATASET_MANIFEST_REQUIREMENTS, "field", "description"
        ),
        "allowed_symbols": list(ALLOWED_SYMBOLS),
        "allowed_timeframe": ALLOWED_TIMEFRAME,
        "allowed_instrument_type": ALLOWED_INSTRUMENT_TYPE,
        "rejection_conditions": _pairs_to_records(
            REJECTION_CONDITIONS, "id", "description"
        ),
        "abort_rules": _pairs_to_records(ABORT_RULES, "id", "description"),
        "safety_gates": _pairs_to_records(SAFETY_GATES, "gate", "state"),
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
        "mission_flow_aligned": mission_flow_aligned,
        "safe": safe,
        "forbidden_flag_hits": list(forbidden_flag_hits),
        "qa_plan": qa_plan,
        "plan_summary": (
            "Real Data QA plan-only contract: the Crypto-D1 chain is parked at "
            "the human-controlled real data QA boundary. This plan defines the QA "
            "scope, the selected read-only spot provider boundaries, the dataset "
            "manifest requirements, the approved symbols / daily timeframe / spot "
            "instrument type, the rejection conditions, the abort rules, and the "
            "safety gates for a FUTURE, separately human-controlled, read-only QA "
            "step. It fetches nothing, inspects nothing, runs nothing, writes "
            "nothing, and unlocks nothing."
        ),
        "operator_next_step": (
            "A human reviews this plan and, as a SEPARATE act, decides whether to "
            "approve a future read-only QA step against it. Reading this plan "
            "acquires no data, runs nothing, writes no manifest, and unlocks no "
            "gate; real_data_qa stays BLOCKED until a separate, future, explicitly "
            "human-controlled step is supplied."
        ),
        "human_operator_required_next_steps": [
            "A human reviews this read-only QA plan-only contract.",
            "A human separately decides whether to approve a future read-only QA "
            "step bounded exactly by this plan.",
            "A separate, future, explicitly human-controlled review is required "
            "before any QA step is run; this plan supplies none of it.",
        ],
        "requires_separate_future_human_controlled_step": True,
        "human_decision_required": True,
        "this_plan_authorizes_boundary_crossing": False,
        "this_plan_unlocks_real_data_qa": False,
        "safety_posture": dict(PLAN_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "real_strategy_intake_state": "BLOCKED",
        "human_approval_required": True,
        "read_only": True,
        "research_only": True,
        "executes": False,
        "performs_data_fetch": False,
        "inspects_dataset": False,
        "reads_data_files": False,
        "writes_data_files": False,
        "writes_manifest": False,
        "uses_network": False,
        "reads_dotenv": False,
        "exposes_secret": False,
        "accesses_credentials": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
        "writes_storage_outputs": False,
        "runs_qa": False,
        "runs_baseline": False,
        "runs_backtest": False,
        "runs_simulation": False,
        "contacts_broker": False,
        "contacts_exchange": False,
        "activates_automation": False,
        "performs_auto_push": False,
        "generates_trade_signal": False,
        "generates_order": False,
        "authorizes_trading": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "authorizes_broker_exchange": False,
        "authorizes_order_placement": False,
        "authorizes_account_control": False,
        "authorizes_portfolio_control": False,
        "authorizes_strategy_promotion": False,
        "authorizes_automation_trading": False,
        "authorizes_data_fetch": False,
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
    "qa_plan",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_REQUIRED_PLAN_KEYS: tuple[str, ...] = (
    "parked_stage",
    "parked_next_required_action",
    "qa_scope_checks",
    "provider_boundaries",
    "dataset_manifest_requirements",
    "allowed_symbols",
    "allowed_timeframe",
    "allowed_instrument_type",
    "rejection_conditions",
    "abort_rules",
    "safety_gates",
    "no_unlock_confirmation",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "performs_data_fetch",
    "inspects_dataset",
    "reads_data_files",
    "writes_data_files",
    "writes_manifest",
    "uses_network",
    "reads_dotenv",
    "exposes_secret",
    "accesses_credentials",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
    "writes_storage_outputs",
    "runs_qa",
    "runs_baseline",
    "runs_backtest",
    "runs_simulation",
    "contacts_broker",
    "contacts_exchange",
    "activates_automation",
    "performs_auto_push",
    "generates_trade_signal",
    "generates_order",
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_portfolio_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "authorizes_data_fetch",
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


def validate_real_data_qa_plan_only_contract(contract: Any) -> dict[str, Any]:
    """Validate (read-only) a built plan-only contract. Returns a verdict dict of
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
    human_decision_required = c.get("human_decision_required") is True
    future_step_required = (
        c.get("requires_separate_future_human_controlled_step") is True
    )
    no_boundary_crossing = c.get("this_plan_authorizes_boundary_crossing") is False
    no_unlock_self = c.get("this_plan_unlocks_real_data_qa") is False
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
        and c.get("real_strategy_intake_state") == "BLOCKED"
    )

    p = c.get("qa_plan")
    p_is_dict = isinstance(p, dict)
    plan_keys_ok = p_is_dict and all(k in p for k in _REQUIRED_PLAN_KEYS)
    parked_refs_ok = p_is_dict and (
        p.get("parked_stage") == MISSION_FLOW_CURRENT_STAGE
        and p.get("parked_next_required_action") == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    qa_scope_ok = p_is_dict and (
        isinstance(p.get("qa_scope_checks"), list)
        and len(p.get("qa_scope_checks") or []) == len(QA_SCOPE_CHECKS)
        and all(
            isinstance(i, dict) and {"id", "description"} <= set(i)
            for i in (p.get("qa_scope_checks") or [])
        )
    )
    provider_boundaries_ok = p_is_dict and bool(p.get("provider_boundaries"))
    manifest_ok = p_is_dict and (
        isinstance(p.get("dataset_manifest_requirements"), list)
        and len(p.get("dataset_manifest_requirements") or [])
        == len(DATASET_MANIFEST_REQUIREMENTS)
        and all(
            isinstance(i, dict) and {"field", "description"} <= set(i)
            for i in (p.get("dataset_manifest_requirements") or [])
        )
    )
    scope_data_ok = p_is_dict and (
        p.get("allowed_symbols") == list(ALLOWED_SYMBOLS)
        and p.get("allowed_timeframe") == ALLOWED_TIMEFRAME
        and p.get("allowed_instrument_type") == ALLOWED_INSTRUMENT_TYPE
    )
    rejection_ok = p_is_dict and (
        isinstance(p.get("rejection_conditions"), list)
        and len(p.get("rejection_conditions") or []) == len(REJECTION_CONDITIONS)
        and all(
            isinstance(i, dict) and {"id", "description"} <= set(i)
            for i in (p.get("rejection_conditions") or [])
        )
    )
    abort_ok = p_is_dict and (
        isinstance(p.get("abort_rules"), list)
        and len(p.get("abort_rules") or []) == len(ABORT_RULES)
        and all(
            isinstance(i, dict) and {"id", "description"} <= set(i)
            for i in (p.get("abort_rules") or [])
        )
    )
    safety_gates_ok = p_is_dict and (
        isinstance(p.get("safety_gates"), list)
        and len(p.get("safety_gates") or []) == len(SAFETY_GATES)
        and all(
            isinstance(i, dict)
            and {"gate", "state"} <= set(i)
            and i.get("state") in {"BLOCKED", "LOCKED"}
            for i in (p.get("safety_gates") or [])
        )
    )

    nuc = p.get("no_unlock_confirmation") if p_is_dict else None
    no_unlock_ok = isinstance(nuc, dict) and (
        nuc.get("unlocks_real_data_qa") is False
        and nuc.get("unlocks_baseline_backtest") is False
        and nuc.get("unlocks_paper_trading") is False
        and nuc.get("unlocks_micro_live") is False
        and nuc.get("real_data_qa_state") == "BLOCKED"
        and nuc.get("baseline_backtest_state") == "BLOCKED"
        and nuc.get("paper_live_state") == "LOCKED"
    )

    no_secret_value_fields = not _has_secret_value(c)

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
        "human_decision_required": human_decision_required,
        "future_step_required": future_step_required,
        "no_boundary_crossing": no_boundary_crossing,
        "no_unlock_self": no_unlock_self,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "plan_keys_ok": plan_keys_ok,
        "parked_refs_ok": parked_refs_ok,
        "qa_scope_ok": qa_scope_ok,
        "provider_boundaries_ok": provider_boundaries_ok,
        "manifest_ok": manifest_ok,
        "scope_data_ok": scope_data_ok,
        "rejection_ok": rejection_ok,
        "abort_ok": abort_ok,
        "safety_gates_ok": safety_gates_ok,
        "no_unlock_ok": no_unlock_ok,
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


def render_real_data_qa_plan_only_contract_markdown(contract: Any) -> str:
    """Render a built plan-only contract as a deterministic markdown brief. Pure
    string formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    p = c.get("qa_plan") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Real Data QA Plan-Only Contract")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Authorizes boundary crossing: "
        + str(c.get("this_plan_authorizes_boundary_crossing", False))
    )
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))
    lines.append(
        "- Allowed scope: "
        + ", ".join(str(s) for s in (p.get("allowed_symbols") or []))
        + " @ "
        + str(p.get("allowed_timeframe", ""))
        + " ("
        + str(p.get("allowed_instrument_type", ""))
        + ")"
    )

    _emit(
        lines,
        "QA Scope Checks",
        [
            str(i.get("id")) + ": " + str(i.get("description"))
            for i in (p.get("qa_scope_checks") or [])
        ],
    )
    _emit(lines, "Provider Boundaries", list(p.get("provider_boundaries") or []))
    _emit(
        lines,
        "Dataset Manifest Requirements",
        [
            str(i.get("field")) + ": " + str(i.get("description"))
            for i in (p.get("dataset_manifest_requirements") or [])
        ],
    )
    _emit(
        lines,
        "Rejection Conditions",
        [
            str(i.get("id")) + ": " + str(i.get("description"))
            for i in (p.get("rejection_conditions") or [])
        ],
    )
    _emit(
        lines,
        "Abort Rules",
        [
            str(i.get("id")) + ": " + str(i.get("description"))
            for i in (p.get("abort_rules") or [])
        ],
    )
    _emit(
        lines,
        "Safety Gates",
        [
            str(i.get("gate")) + ": " + str(i.get("state"))
            for i in (p.get("safety_gates") or [])
        ],
    )
    _emit(
        lines,
        "No-Unlock Confirmation",
        [
            str(k) + ": " + str(v)
            for k, v in (p.get("no_unlock_confirmation") or {}).items()
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)
