"""Selected Read-Only Spot Provider Client Adapter Contract (Block 151).

A PURE, stdlib-only, *read-only* CONTRACT layer. It DEFINES the injectable
provider_client interface that the Block 150 fetch runner requires, and the safety
rules any FUTURE concrete provider implementation must satisfy. It also provides pure
validators that judge a candidate adapter *descriptor* (metadata only) and a returned
*row schema* (a static example only) against those rules.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

THIS contract executes NOTHING. It does NOT call a provider, fetch data, import a CSV,
read or parse any file's contents, write any file, open a network, read or inspect any
credential, read a .env file, print / store / log any secret, run validation / QA /
baseline / backtest, touch any broker / exchange / trading / account / order /
portfolio endpoint, or unlock any gate. It only describes the required adapter
interface and validates supplied static metadata / schema descriptors.

CORE RULE: defining and validating an interface authorizes nothing and runs nothing.
A concrete provider is a SEPARATE, future, human-approved implementation OUTSIDE this
contract. real_data_qa stays BLOCKED, baseline stays BLOCKED, and paper / micro-live
stay LOCKED.

Public API:
  - ADAPTER_SCHEMA_VERSION / ADAPTER_LABEL / ADAPTER_STATUS / ADAPTER_MODE / ADAPTER_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - REQUIRED_ADAPTER_METHOD / ADAPTER_METHOD_SIGNATURE
  - ADAPTER_APPROVED_SYMBOLS / ADAPTER_APPROVED_TIMEFRAMES / ADAPTER_SYMBOL_ALIASES
  - ADAPTER_REQUIRED_RETURN_FIELDS / ADAPTER_REQUIRED_INSTRUMENT_TYPE
  - ADAPTER_PROVIDER_CONSTRAINTS / ADAPTER_REJECTION_RULES / ADAPTER_FORBIDDEN_RETURN_FIELDS
  - NEXT_RECOMMENDED_ACTION / DEFAULT_ADAPTER_DESCRIPTOR
  - validate_returned_row_schema(row, timeframe=None)
  - validate_provider_client_adapter_descriptor(descriptor)
  - build_crypto_d1_selected_read_only_spot_provider_client_adapter_contract(payload=None)
  - validate_crypto_d1_selected_read_only_spot_provider_client_adapter_contract(contract)
  - render_crypto_d1_selected_read_only_spot_provider_client_adapter_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    FETCH_APPROVED_SYMBOLS,
    FETCH_APPROVED_TIMEFRAMES,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

ADAPTER_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_selected_read_only_spot_provider_client_adapter_contract.v1"
)
ADAPTER_LABEL = (
    "Block 151 - Selected Read-Only Spot Provider Client Adapter Contract"
)
ADAPTER_STATUS = "PROVIDER_CLIENT_ADAPTER_CONTRACT_ONLY"
ADAPTER_MODE = "RESEARCH_ONLY"

ADAPTER_CORE_RULE = (
    "Defining and validating the injectable read-only provider adapter interface "
    "authorizes nothing and runs nothing. No provider is called, no API is called, no "
    "network is opened, no data is fetched, no CSV is imported, no file is read or "
    "written, no credential is read, and no .env is read. A concrete provider is a "
    "SEPARATE, future, human-approved implementation OUTSIDE this contract. "
    "real_data_qa stays BLOCKED, baseline stays BLOCKED, and paper / micro-live stay "
    "LOCKED."
)

# 1. The single required adapter method + its signature.
REQUIRED_ADAPTER_METHOD = "fetch_read_only_daily_spot_ohlcv"
ADAPTER_METHOD_SIGNATURE = "fetch_read_only_daily_spot_ohlcv(symbol, timeframe)"

# 2 + 3. Allowed symbols / timeframe.
ADAPTER_APPROVED_SYMBOLS: tuple[str, ...] = FETCH_APPROVED_SYMBOLS
ADAPTER_APPROVED_TIMEFRAMES: tuple[str, ...] = FETCH_APPROVED_TIMEFRAMES

ADAPTER_SYMBOL_ALIASES: dict[str, tuple[str, ...]] = {
    "BTCUSD": ("BTCUSD", "BTC/USD", "BTC-USD", "XBTUSD"),
    "ETHUSD": ("ETHUSD", "ETH/USD", "ETH-USD"),
    "SOLUSD": ("SOLUSD", "SOL/USD", "SOL-USD"),
}

# 4. Required return schema for every OHLCV row.
ADAPTER_REQUIRED_RETURN_FIELDS: tuple[str, ...] = (
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "source",
    "instrument_type",
)
ADAPTER_REQUIRED_INSTRUMENT_TYPE = "spot"

# 5. Required provider constraints.
ADAPTER_PROVIDER_CONSTRAINTS: tuple[str, ...] = (
    "Read-only historical spot market data only.",
    "No trading endpoint.",
    "No account endpoint.",
    "No portfolio endpoint.",
    "No order endpoint.",
    "No paper / live endpoint.",
    "No credential printing / logging / storing.",
    "No secret in returned data.",
)

# 6. Rejection rules.
ADAPTER_REJECTION_RULES: tuple[str, ...] = (
    "futures / perps",
    "exchange trading API requiring account auth",
    "wrong symbol",
    "wrong timeframe",
    "missing OHLCV fields",
    "unclear source / license",
    "data containing account / order / trade fields",
)

# Fields that, if present in a returned row, mean the data is NOT read-only OHLCV.
ADAPTER_FORBIDDEN_RETURN_FIELDS: tuple[str, ...] = (
    "order_id",
    "side",
    "account",
    "account_id",
    "position",
    "fill",
    "broker",
    "trade_id",
    "balance",
    "wallet",
    "api_key",
    "apikey",
    "secret",
    "password",
    "bearer",
    "access_token",
    "private_key",
)

# 7. The single next recommended action.
NEXT_RECOMMENDED_ACTION = (
    "HOLD_FOR_CONCRETE_PROVIDER_IMPLEMENTATION_OR_MANUAL_CSV"
)

# A compliant REFERENCE descriptor (metadata + a static schema EXAMPLE row, NOT real
# fetched data). Used as the default subject for the contract's own validation.
DEFAULT_ADAPTER_DESCRIPTOR: dict[str, Any] = {
    "name": "clear_license_readonly_spot_history_api_archetype",
    "method_name": REQUIRED_ADAPTER_METHOD,
    "instrument_type": "spot",
    "is_futures_or_perp": False,
    "requires_trading_endpoint": False,
    "requires_order_endpoint": False,
    "requires_account_endpoint": False,
    "requires_portfolio_endpoint": False,
    "requires_paper_live_endpoint": False,
    "requires_account_auth": False,
    "declared_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    "declared_timeframes": ["1d"],
    "return_fields": list(ADAPTER_REQUIRED_RETURN_FIELDS),
    "has_clear_license_metadata": True,
    "source": "REFERENCE_CLEAR_LICENSE_SPOT_HISTORICAL_SOURCE",
    "sample_row": {
        "date": "YYYY-MM-DD",
        "open": 0.0,
        "high": 0.0,
        "low": 0.0,
        "close": 0.0,
        "volume": 0.0,
        "source": "REFERENCE_SCHEMA_EXAMPLE_NOT_REAL_DATA",
        "instrument_type": "spot",
    },
}

# Top-level flags that, if truthy on an operator's input, mark it unsafe.
ADAPTER_FORBIDDEN_FLAGS: tuple[str, ...] = (
    "implement_real_provider",
    "call_provider_now",
    "fetch_data_now",
    "import_csv_now",
    "read_credentials",
    "read_dotenv",
    "print_secrets",
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_portfolio_control",
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
)

ADAPTER_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

ADAPTER_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "executes": False,
    "calls_provider": False,
    "implements_real_provider": False,
    "performs_data_fetch": False,
    "imports_csv": False,
    "reads_file_contents": False,
    "uses_network": False,
    "fetches_data": False,
    "checks_live_credentials": False,
    "reads_dotenv": False,
    "exposes_secret": False,
    "reads_data_files": False,
    "writes_data_files": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "runs_validation_pipeline": False,
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
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}

DEFAULT_ADAPTER_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 read-only spot provider client adapter contract input (static)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "descriptor": DEFAULT_ADAPTER_DESCRIPTOR,
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


def _normalize_symbol(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    raw = value.strip().upper().replace("/", "").replace("-", "")
    for canonical, aliases in ADAPTER_SYMBOL_ALIASES.items():
        if raw == canonical:
            return canonical
        for alias in aliases:
            if raw == alias.upper().replace("/", "").replace("-", ""):
                return canonical
    return None


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
# returned-row schema validation (pure; operates on a supplied static row)
# --------------------------------------------------------------------------- #
def validate_returned_row_schema(
    row: Any, timeframe: Any = None
) -> dict[str, Any]:
    """Validate a single static OHLCV row dict against the required schema and the
    read-only rejection rules. Operates on supplied data only; fetches nothing."""
    reasons: list[str] = []
    is_dict = isinstance(row, dict)
    if not is_dict:
        return {
            "row_schema_ok": False,
            "is_dict": False,
            "has_all_fields": False,
            "instrument_spot_ok": False,
            "no_forbidden_fields": False,
            "no_secret": True,
            "reasons": ["REJECT_ROW_NOT_A_MAPPING"],
        }

    keys = {str(k).lower() for k in row.keys()}
    missing = [f for f in ADAPTER_REQUIRED_RETURN_FIELDS if f not in row]
    has_all_fields = not missing
    if missing:
        reasons.append("REJECT_MISSING_RETURN_FIELDS:" + ",".join(missing))

    instrument_spot_ok = row.get("instrument_type") == ADAPTER_REQUIRED_INSTRUMENT_TYPE
    if not instrument_spot_ok:
        reasons.append("REJECT_WRONG_INSTRUMENT_TYPE")

    forbidden_hits = [f for f in ADAPTER_FORBIDDEN_RETURN_FIELDS if f in keys]
    no_forbidden_fields = not forbidden_hits
    if forbidden_hits:
        reasons.append("REJECT_NON_READ_ONLY_DATA_FIELDS:" + ",".join(forbidden_hits))

    no_secret = not _has_secret_value(row)
    if not no_secret:
        reasons.append("REJECT_SECRET_PRESENT")

    if timeframe is not None and timeframe not in ADAPTER_APPROVED_TIMEFRAMES:
        reasons.append("REJECT_WRONG_TIMEFRAME:" + str(timeframe))

    row_schema_ok = (
        has_all_fields
        and instrument_spot_ok
        and no_forbidden_fields
        and no_secret
        and not (timeframe is not None and timeframe not in ADAPTER_APPROVED_TIMEFRAMES)
    )
    return {
        "row_schema_ok": row_schema_ok,
        "is_dict": True,
        "has_all_fields": has_all_fields,
        "instrument_spot_ok": instrument_spot_ok,
        "no_forbidden_fields": no_forbidden_fields,
        "no_secret": no_secret,
        "reasons": reasons,
    }


# --------------------------------------------------------------------------- #
# adapter-descriptor validation (pure; operates on supplied metadata)
# --------------------------------------------------------------------------- #
def validate_provider_client_adapter_descriptor(
    descriptor: Any,
) -> dict[str, Any]:
    """Validate (read-only) a candidate adapter *descriptor* (metadata only) against
    the interface + safety rules. Returns boolean checks, rejection_reasons, and
    provider_client_contract_valid (True only if every criterion passes)."""
    d = descriptor if isinstance(descriptor, dict) else {}
    reasons: list[str] = []

    method_ok = d.get("method_name") == REQUIRED_ADAPTER_METHOD
    if not method_ok:
        reasons.append("REJECT_MISSING_REQUIRED_METHOD")

    is_futures = _is_truthy(d.get("is_futures_or_perp")) or str(
        d.get("instrument_type", "")
    ).lower() in {"futures", "future", "perp", "perps", "perpetual"}
    instrument_spot_ok = (
        d.get("instrument_type") == ADAPTER_REQUIRED_INSTRUMENT_TYPE
        and not is_futures
    )
    if is_futures:
        reasons.append("REJECT_FUTURES_OR_PERPS")
    elif not instrument_spot_ok:
        reasons.append("REJECT_WRONG_INSTRUMENT_TYPE")

    requires_account_auth = (
        _is_truthy(d.get("requires_account_auth"))
        or _is_truthy(d.get("requires_account_endpoint"))
        or _is_truthy(d.get("requires_trading_endpoint"))
    )
    no_trading_endpoint_ok = not _is_truthy(d.get("requires_trading_endpoint"))
    no_order_endpoint_ok = not _is_truthy(d.get("requires_order_endpoint"))
    no_account_endpoint_ok = not _is_truthy(d.get("requires_account_endpoint"))
    no_portfolio_endpoint_ok = not _is_truthy(d.get("requires_portfolio_endpoint"))
    no_paper_live_endpoint_ok = not _is_truthy(d.get("requires_paper_live_endpoint"))
    no_account_auth_ok = not requires_account_auth
    if not no_account_auth_ok or not no_trading_endpoint_ok:
        reasons.append("REJECT_TRADING_API_REQUIRING_ACCOUNT_AUTH")
    if not no_order_endpoint_ok:
        reasons.append("REJECT_ORDER_ENDPOINT")
    if not no_portfolio_endpoint_ok:
        reasons.append("REJECT_PORTFOLIO_ENDPOINT")
    if not no_paper_live_endpoint_ok:
        reasons.append("REJECT_PAPER_LIVE_ENDPOINT")

    declared_symbols = d.get("declared_symbols") or []
    if not isinstance(declared_symbols, (list, tuple)):
        declared_symbols = [declared_symbols]
    bad_symbols = [s for s in declared_symbols if _normalize_symbol(s) is None]
    symbols_ok = bool(declared_symbols) and not bad_symbols
    if bad_symbols:
        reasons.append("REJECT_WRONG_SYMBOL:" + ",".join(str(s) for s in bad_symbols))
    elif not declared_symbols:
        reasons.append("REJECT_WRONG_SYMBOL:none_declared")

    declared_timeframes = d.get("declared_timeframes") or []
    if not isinstance(declared_timeframes, (list, tuple)):
        declared_timeframes = [declared_timeframes]
    bad_timeframes = [
        t for t in declared_timeframes if t not in ADAPTER_APPROVED_TIMEFRAMES
    ]
    timeframe_ok = bool(declared_timeframes) and not bad_timeframes
    if bad_timeframes:
        reasons.append(
            "REJECT_WRONG_TIMEFRAME:" + ",".join(str(t) for t in bad_timeframes)
        )
    elif not declared_timeframes:
        reasons.append("REJECT_WRONG_TIMEFRAME:none_declared")

    return_fields = d.get("return_fields") or []
    if not isinstance(return_fields, (list, tuple)):
        return_fields = [return_fields]
    missing_fields = [f for f in ADAPTER_REQUIRED_RETURN_FIELDS if f not in return_fields]
    return_schema_ok = not missing_fields
    if missing_fields:
        reasons.append("REJECT_MISSING_RETURN_FIELDS:" + ",".join(missing_fields))

    license_ok = _is_truthy(d.get("has_clear_license_metadata")) and bool(
        str(d.get("source", "")).strip()
    )
    if not license_ok:
        reasons.append("REJECT_UNCLEAR_SOURCE_OR_LICENSE")

    sample_row = d.get("sample_row")
    if sample_row is None:
        sample_row_ok = True
        sample_row_verdict: dict[str, Any] = {"row_schema_ok": True, "skipped": True}
    else:
        sample_row_verdict = validate_returned_row_schema(sample_row)
        sample_row_ok = sample_row_verdict["row_schema_ok"]
        if not sample_row_ok:
            reasons.append("REJECT_SAMPLE_ROW_SCHEMA")

    no_secret_ok = not _has_secret_value(d)
    if not no_secret_ok:
        reasons.append("REJECT_SECRET_PRESENT")

    checks = {
        "method_ok": method_ok,
        "instrument_spot_ok": instrument_spot_ok,
        "no_trading_endpoint_ok": no_trading_endpoint_ok,
        "no_order_endpoint_ok": no_order_endpoint_ok,
        "no_account_endpoint_ok": no_account_endpoint_ok,
        "no_portfolio_endpoint_ok": no_portfolio_endpoint_ok,
        "no_paper_live_endpoint_ok": no_paper_live_endpoint_ok,
        "no_account_auth_ok": no_account_auth_ok,
        "symbols_ok": symbols_ok,
        "timeframe_ok": timeframe_ok,
        "return_schema_ok": return_schema_ok,
        "license_ok": license_ok,
        "sample_row_ok": sample_row_ok,
        "no_secret_ok": no_secret_ok,
    }
    verdict = dict(checks)
    verdict["sample_row_verdict"] = sample_row_verdict
    verdict["rejection_reasons"] = reasons
    verdict["provider_client_contract_valid"] = all(checks.values()) and not reasons
    return verdict


# --------------------------------------------------------------------------- #
# contract build
# --------------------------------------------------------------------------- #
def build_crypto_d1_selected_read_only_spot_provider_client_adapter_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the adapter interface contract. Validates the supplied
    (or default reference) descriptor; every capability flag is False and every gate
    lock is True regardless of input."""
    data = dict(DEFAULT_ADAPTER_INPUT) if payload is None else _as_payload(payload)

    mf_stage = data.get("mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE)
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_flag_hits = [
        f for f in ADAPTER_FORBIDDEN_FLAGS if _is_truthy(data.get(f))
    ]
    safe = mission_flow_aligned and not forbidden_flag_hits

    descriptor = data.get("descriptor", DEFAULT_ADAPTER_DESCRIPTOR)
    descriptor_verdict = validate_provider_client_adapter_descriptor(descriptor)
    provider_client_contract_valid = bool(
        descriptor_verdict["provider_client_contract_valid"]
    )

    adapter_interface = {
        "required_method": REQUIRED_ADAPTER_METHOD,
        "method_signature": ADAPTER_METHOD_SIGNATURE,
        "allowed_symbols": list(ADAPTER_APPROVED_SYMBOLS),
        "allowed_timeframes": list(ADAPTER_APPROVED_TIMEFRAMES),
        "symbol_aliases": {k: list(v) for k, v in ADAPTER_SYMBOL_ALIASES.items()},
        "required_return_fields": list(ADAPTER_REQUIRED_RETURN_FIELDS),
        "required_instrument_type": ADAPTER_REQUIRED_INSTRUMENT_TYPE,
        "provider_constraints": list(ADAPTER_PROVIDER_CONSTRAINTS),
        "rejection_rules": list(ADAPTER_REJECTION_RULES),
        "forbidden_return_fields": list(ADAPTER_FORBIDDEN_RETURN_FIELDS),
    }

    contract: dict[str, Any] = {
        "schema_version": ADAPTER_SCHEMA_VERSION,
        "label": ADAPTER_LABEL,
        "status": ADAPTER_STATUS,
        "mode": ADAPTER_MODE,
        "core_rule": ADAPTER_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": mission_flow_aligned,
        "safe": safe,
        "forbidden_flag_hits": list(forbidden_flag_hits),
        "adapter_interface": adapter_interface,
        # promoted top-level required outputs
        "required_adapter_method": REQUIRED_ADAPTER_METHOD,
        "allowed_symbols": list(ADAPTER_APPROVED_SYMBOLS),
        "allowed_timeframes": list(ADAPTER_APPROVED_TIMEFRAMES),
        "required_return_fields": list(ADAPTER_REQUIRED_RETURN_FIELDS),
        "required_instrument_type": ADAPTER_REQUIRED_INSTRUMENT_TYPE,
        "provider_constraints": list(ADAPTER_PROVIDER_CONSTRAINTS),
        "rejection_rules": list(ADAPTER_REJECTION_RULES),
        "descriptor_verdict": descriptor_verdict,
        "provider_client_contract_valid": provider_client_contract_valid,
        "next_recommended_action": NEXT_RECOMMENDED_ACTION,
        "contract_summary": (
            "Read-only PROVIDER CLIENT ADAPTER CONTRACT defining the injectable "
            "interface the Block 150 runner requires: a "
            "fetch_read_only_daily_spot_ohlcv(symbol, timeframe) method returning "
            "read-only daily spot OHLCV rows (date / open / high / low / close / "
            "volume / source / instrument_type=spot) for BTCUSD / ETHUSD / SOLUSD at "
            "1d only. It defines the provider constraints and rejection rules and "
            "validates supplied static descriptors. THIS contract defines and "
            "validates only -- it calls no provider, fetches nothing, reads / writes "
            "no file, and unlocks no gate."
        ),
        "operator_next_step": (
            "A human reviews this adapter contract and, as a SEPARATE action, either "
            "supplies a concrete read-only provider implementation that satisfies it "
            "or chooses the manual-CSV path. Reviewing this contract calls no "
            "provider, fetches no data, reads no file, writes nothing, and unlocks no "
            "gate; the recommended next action is "
            "HOLD_FOR_CONCRETE_PROVIDER_IMPLEMENTATION_OR_MANUAL_CSV."
        ),
        "human_operator_required_next_steps": [
            "A human reviews this read-only adapter interface contract.",
            "A human separately supplies a concrete read-only provider implementation "
            "that satisfies this contract, or chooses the manual-CSV import path.",
            "Only after that separate, human-approved provider exists could the Block "
            "150 runner be injected with it; this contract writes nothing and unlocks "
            "no gate.",
        ],
        "requires_human_provider_decision": True,
        "this_contract_calls_provider": False,
        "this_contract_implements_provider": False,
        "this_contract_fetches_data": False,
        "this_contract_reads_files": False,
        "this_contract_writes_files": False,
        "safety_posture": dict(ADAPTER_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "read_only": True,
        "research_only": True,
        "executes": False,
        "calls_provider": False,
        "implements_real_provider": False,
        "performs_data_fetch": False,
        "imports_csv": False,
        "reads_file_contents": False,
        "uses_network": False,
        "fetches_data": False,
        "checks_live_credentials": False,
        "reads_dotenv": False,
        "exposes_secret": False,
        "reads_data_files": False,
        "writes_data_files": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
        "runs_validation_pipeline": False,
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
# contract validation
# --------------------------------------------------------------------------- #
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "mode",
    "core_rule",
    "mission_flow_current_stage",
    "mission_flow_next_required_action",
    "adapter_interface",
    "required_adapter_method",
    "allowed_symbols",
    "allowed_timeframes",
    "required_return_fields",
    "required_instrument_type",
    "provider_constraints",
    "rejection_rules",
    "descriptor_verdict",
    "provider_client_contract_valid",
    "next_recommended_action",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "calls_provider",
    "implements_real_provider",
    "performs_data_fetch",
    "imports_csv",
    "reads_file_contents",
    "uses_network",
    "fetches_data",
    "checks_live_credentials",
    "reads_dotenv",
    "exposes_secret",
    "reads_data_files",
    "writes_data_files",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
    "runs_validation_pipeline",
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


def validate_crypto_d1_selected_read_only_spot_provider_client_adapter_contract(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built adapter interface contract."""
    c = contract if isinstance(contract, dict) else {}
    missing_fields = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == ADAPTER_SCHEMA_VERSION
    label_ok = c.get("label") == ADAPTER_LABEL
    status_ok = c.get("status") == ADAPTER_STATUS
    mode_ok = c.get("mode") == ADAPTER_MODE
    core_rule_ok = c.get("core_rule") == ADAPTER_CORE_RULE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    this_calls_false = c.get("this_contract_calls_provider") is False
    this_impl_false = c.get("this_contract_implements_provider") is False
    this_fetches_false = c.get("this_contract_fetches_data") is False
    this_reads_false = c.get("this_contract_reads_files") is False
    this_writes_false = c.get("this_contract_writes_files") is False
    human_decision_required = c.get("requires_human_provider_decision") is True
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == ADAPTER_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
    )
    next_action_ok = c.get("next_recommended_action") == NEXT_RECOMMENDED_ACTION

    method_ok = c.get("required_adapter_method") == REQUIRED_ADAPTER_METHOD
    symbols_ok = c.get("allowed_symbols") == list(ADAPTER_APPROVED_SYMBOLS)
    timeframes_ok = c.get("allowed_timeframes") == list(ADAPTER_APPROVED_TIMEFRAMES)
    return_fields_ok = c.get("required_return_fields") == list(
        ADAPTER_REQUIRED_RETURN_FIELDS
    )
    instrument_ok = c.get("required_instrument_type") == ADAPTER_REQUIRED_INSTRUMENT_TYPE
    constraints_ok = c.get("provider_constraints") == list(ADAPTER_PROVIDER_CONSTRAINTS)
    rejection_rules_ok = c.get("rejection_rules") == list(ADAPTER_REJECTION_RULES)

    interface = c.get("adapter_interface")
    interface_ok = isinstance(interface, dict) and (
        interface.get("required_method") == REQUIRED_ADAPTER_METHOD
        and interface.get("required_instrument_type") == ADAPTER_REQUIRED_INSTRUMENT_TYPE
        and interface.get("allowed_symbols") == list(ADAPTER_APPROVED_SYMBOLS)
        and interface.get("allowed_timeframes") == list(ADAPTER_APPROVED_TIMEFRAMES)
        and interface.get("required_return_fields")
        == list(ADAPTER_REQUIRED_RETURN_FIELDS)
    )

    dv = c.get("descriptor_verdict")
    descriptor_verdict_ok = isinstance(dv, dict) and (
        c.get("provider_client_contract_valid")
        == dv.get("provider_client_contract_valid")
    )

    no_secret_value_fields = not _has_secret_value(c)

    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "contract_summary", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(ADAPTER_FORBIDDEN_TRADE_TERMS))

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "status_ok": status_ok,
        "mode_ok": mode_ok,
        "core_rule_ok": core_rule_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "this_calls_false": this_calls_false,
        "this_impl_false": this_impl_false,
        "this_fetches_false": this_fetches_false,
        "this_reads_false": this_reads_false,
        "this_writes_false": this_writes_false,
        "human_decision_required": human_decision_required,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "next_action_ok": next_action_ok,
        "method_ok": method_ok,
        "symbols_ok": symbols_ok,
        "timeframes_ok": timeframes_ok,
        "return_fields_ok": return_fields_ok,
        "instrument_ok": instrument_ok,
        "constraints_ok": constraints_ok,
        "rejection_rules_ok": rejection_rules_ok,
        "interface_ok": interface_ok,
        "descriptor_verdict_ok": descriptor_verdict_ok,
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


def render_crypto_d1_selected_read_only_spot_provider_client_adapter_contract_markdown(
    contract: Any,
) -> str:
    """Render a built adapter contract as a deterministic markdown brief. Writes
    nothing."""
    c = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# Selected Read-Only Spot Provider Client Adapter Contract")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Required adapter method: " + str(c.get("required_adapter_method", ""))
    )
    lines.append(
        "- Required instrument type: " + str(c.get("required_instrument_type", ""))
    )
    lines.append(
        "- Provider client contract valid: "
        + str(c.get("provider_client_contract_valid", False))
    )
    lines.append(
        "- Next recommended action: " + str(c.get("next_recommended_action", ""))
    )
    lines.append(
        "- This contract calls provider: "
        + str(c.get("this_contract_calls_provider", False))
    )
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(lines, "Allowed Symbols", list(c.get("allowed_symbols") or []))
    _emit(lines, "Allowed Timeframe", list(c.get("allowed_timeframes") or []))
    _emit(lines, "Required Return Fields", list(c.get("required_return_fields") or []))
    _emit(lines, "Provider Constraints", list(c.get("provider_constraints") or []))
    _emit(lines, "Rejection Rules", list(c.get("rejection_rules") or []))
    _emit(
        lines,
        "Next Recommended Action",
        [str(c.get("next_recommended_action", ""))],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)
