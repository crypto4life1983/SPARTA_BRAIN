"""Tests for the Selected Read-Only Spot Provider Client Adapter Contract (Block 151).

This module is a PURE, stdlib-only, *read-only* CONTRACT layer. It DEFINES the
injectable provider_client interface the Block 150 fetch runner requires, plus the
safety rules any FUTURE concrete provider must satisfy, and provides pure validators
for a candidate adapter *descriptor* (metadata only) and a returned *row schema* (a
static example only). It calls no provider, fetches nothing, imports no CSV, reads /
parses no file's contents, opens no network, reads no credential / .env, writes
nothing, runs no QA / baseline / backtest, and unlocks no gate.

These tests assert: schema / constants; mission-flow truth sync against the live status
module; the required adapter interface sections (method + signature, approved symbols
BTCUSD/ETHUSD/SOLUSD, timeframe 1d, return schema, instrument_type=spot, 8 provider
constraints, 7 rejection rules, forbidden return fields); the row-schema validator
(accept compliant, reject missing fields / wrong instrument / order-trade-account
fields / secret values / wrong timeframe); the descriptor validator (accept the
compliant reference, reject futures/perps, account-auth/trading/order/portfolio/paper-
live endpoints, wrong symbol, wrong timeframe, missing return fields, unclear license,
bad sample row, secrets); that the built contract carries every required section, that
every capability flag is False and every gate stays locked, next_recommended_action =
HOLD_FOR_CONCRETE_PROVIDER_IMPLEMENTATION_OR_MANUAL_CSV; forbidden-flag and
off-boundary mission-flow unsafe marking; secrets never carried; determinism / caller
isolation; validation tamper rejections; render; AST purity (only __future__ / typing /
sparta_commander roots, no os / json / csv / network / credential modules, no
os.environ access, NO open / write_* call); and the two additive commander_2_safety
allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_selected_read_only_spot_provider_client_adapter_contract import (  # noqa: E501
    ADAPTER_APPROVED_SYMBOLS,
    ADAPTER_APPROVED_TIMEFRAMES,
    ADAPTER_CORE_RULE,
    ADAPTER_FORBIDDEN_RETURN_FIELDS,
    ADAPTER_LABEL,
    ADAPTER_METHOD_SIGNATURE,
    ADAPTER_MODE,
    ADAPTER_PROVIDER_CONSTRAINTS,
    ADAPTER_REJECTION_RULES,
    ADAPTER_REQUIRED_INSTRUMENT_TYPE,
    ADAPTER_REQUIRED_RETURN_FIELDS,
    ADAPTER_SCHEMA_VERSION,
    ADAPTER_STATUS,
    ADAPTER_SYMBOL_ALIASES,
    DEFAULT_ADAPTER_DESCRIPTOR,
    NEXT_RECOMMENDED_ACTION,
    REQUIRED_ADAPTER_METHOD,
    build_crypto_d1_selected_read_only_spot_provider_client_adapter_contract,
    render_crypto_d1_selected_read_only_spot_provider_client_adapter_contract_markdown,
    validate_crypto_d1_selected_read_only_spot_provider_client_adapter_contract,
    validate_provider_client_adapter_descriptor,
    validate_returned_row_schema,
)
from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_selected_read_only_spot_provider_client_adapter_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_selected_read_only_spot_provider_client_adapter_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_selected_read_only_spot_provider_client_adapter_contract.py"
)

_BUILD = build_crypto_d1_selected_read_only_spot_provider_client_adapter_contract
_VALIDATE = validate_crypto_d1_selected_read_only_spot_provider_client_adapter_contract
_RENDER = (
    render_crypto_d1_selected_read_only_spot_provider_client_adapter_contract_markdown
)
_VALIDATE_DESCRIPTOR = validate_provider_client_adapter_descriptor
_VALIDATE_ROW = validate_returned_row_schema


def _good_row():
    return {
        "date": "2024-01-01",
        "open": 1.0,
        "high": 2.0,
        "low": 0.5,
        "close": 1.5,
        "volume": 100.0,
        "source": "REFERENCE_SCHEMA_EXAMPLE_NOT_REAL_DATA",
        "instrument_type": "spot",
    }


def _good_descriptor():
    import copy

    return copy.deepcopy(DEFAULT_ADAPTER_DESCRIPTOR)


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert ADAPTER_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_selected_read_only_spot_provider_client_adapter_contract.v1"
    )
    assert ADAPTER_LABEL == (
        "Block 151 - Selected Read-Only Spot Provider Client Adapter Contract"
    )
    assert ADAPTER_STATUS == "PROVIDER_CLIENT_ADAPTER_CONTRACT_ONLY"
    assert ADAPTER_MODE == "RESEARCH_ONLY"
    assert "authorizes nothing" in ADAPTER_CORE_RULE.lower()
    assert "blocked" in ADAPTER_CORE_RULE.lower()
    assert "locked" in ADAPTER_CORE_RULE.lower()


def test_required_method_and_signature():
    assert REQUIRED_ADAPTER_METHOD == "fetch_read_only_daily_spot_ohlcv"
    assert ADAPTER_METHOD_SIGNATURE == (
        "fetch_read_only_daily_spot_ohlcv(symbol, timeframe)"
    )


def test_approved_symbols_and_timeframes():
    assert ADAPTER_APPROVED_SYMBOLS == ("BTCUSD", "ETHUSD", "SOLUSD")
    assert ADAPTER_APPROVED_TIMEFRAMES == ("1d",)


def test_symbol_aliases_include_slash_and_dash_forms():
    assert "BTC/USD" in ADAPTER_SYMBOL_ALIASES["BTCUSD"]
    assert "ETH-USD" in ADAPTER_SYMBOL_ALIASES["ETHUSD"]
    assert "SOL/USD" in ADAPTER_SYMBOL_ALIASES["SOLUSD"]


def test_required_return_fields_and_instrument_type():
    assert ADAPTER_REQUIRED_RETURN_FIELDS == (
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "source",
        "instrument_type",
    )
    assert ADAPTER_REQUIRED_INSTRUMENT_TYPE == "spot"


def test_provider_constraints_and_rejection_rules_counts():
    assert len(ADAPTER_PROVIDER_CONSTRAINTS) == 8
    assert len(ADAPTER_REJECTION_RULES) == 7


def test_forbidden_return_fields_include_trade_and_secret_tokens():
    for field in ("order_id", "side", "account", "position", "trade_id", "balance"):
        assert field in ADAPTER_FORBIDDEN_RETURN_FIELDS
    for token in ("api_key", "secret", "access_token", "private_key"):
        assert token in ADAPTER_FORBIDDEN_RETURN_FIELDS


def test_next_recommended_action():
    assert NEXT_RECOMMENDED_ACTION == (
        "HOLD_FOR_CONCRETE_PROVIDER_IMPLEMENTATION_OR_MANUAL_CSV"
    )


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# Row-schema validator
# --------------------------------------------------------------------------- #
def test_row_validator_accepts_compliant_spot_row():
    verdict = _VALIDATE_ROW(_good_row(), timeframe="1d")
    assert verdict["row_schema_ok"] is True
    assert verdict["has_all_fields"] is True
    assert verdict["instrument_spot_ok"] is True
    assert verdict["no_forbidden_fields"] is True
    assert verdict["no_secret"] is True
    assert verdict["reasons"] == []


def test_row_validator_rejects_non_mapping():
    verdict = _VALIDATE_ROW(["not", "a", "dict"])
    assert verdict["row_schema_ok"] is False
    assert verdict["is_dict"] is False
    assert "REJECT_ROW_NOT_A_MAPPING" in verdict["reasons"]


def test_row_validator_rejects_missing_fields():
    row = _good_row()
    del row["volume"]
    verdict = _VALIDATE_ROW(row)
    assert verdict["row_schema_ok"] is False
    assert verdict["has_all_fields"] is False
    assert any(r.startswith("REJECT_MISSING_RETURN_FIELDS") for r in verdict["reasons"])


def test_row_validator_rejects_wrong_instrument_type():
    row = _good_row()
    row["instrument_type"] = "futures"
    verdict = _VALIDATE_ROW(row)
    assert verdict["row_schema_ok"] is False
    assert verdict["instrument_spot_ok"] is False
    assert "REJECT_WRONG_INSTRUMENT_TYPE" in verdict["reasons"]


def test_row_validator_rejects_order_account_trade_fields():
    row = _good_row()
    row["order_id"] = "abc"
    row["account"] = "x"
    verdict = _VALIDATE_ROW(row)
    assert verdict["row_schema_ok"] is False
    assert verdict["no_forbidden_fields"] is False
    assert any(
        r.startswith("REJECT_NON_READ_ONLY_DATA_FIELDS") for r in verdict["reasons"]
    )


def test_row_validator_rejects_secret_value():
    row = _good_row()
    row["api_key"] = "leaked-secret-value"
    verdict = _VALIDATE_ROW(row)
    assert verdict["row_schema_ok"] is False
    # api_key is both a forbidden return field and a secret-valued field.
    assert verdict["no_forbidden_fields"] is False or verdict["no_secret"] is False


def test_row_validator_rejects_wrong_timeframe():
    verdict = _VALIDATE_ROW(_good_row(), timeframe="1h")
    assert verdict["row_schema_ok"] is False
    assert any(r.startswith("REJECT_WRONG_TIMEFRAME") for r in verdict["reasons"])


# --------------------------------------------------------------------------- #
# Descriptor validator
# --------------------------------------------------------------------------- #
def test_descriptor_validator_accepts_compliant_reference():
    verdict = _VALIDATE_DESCRIPTOR(_good_descriptor())
    assert verdict["provider_client_contract_valid"] is True
    assert verdict["rejection_reasons"] == []
    for key in (
        "method_ok",
        "instrument_spot_ok",
        "no_trading_endpoint_ok",
        "no_order_endpoint_ok",
        "no_account_endpoint_ok",
        "no_portfolio_endpoint_ok",
        "no_paper_live_endpoint_ok",
        "no_account_auth_ok",
        "symbols_ok",
        "timeframe_ok",
        "return_schema_ok",
        "license_ok",
        "sample_row_ok",
        "no_secret_ok",
    ):
        assert verdict[key] is True, key


def test_descriptor_validator_rejects_missing_method():
    d = _good_descriptor()
    d["method_name"] = "something_else"
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert verdict["method_ok"] is False
    assert "REJECT_MISSING_REQUIRED_METHOD" in verdict["rejection_reasons"]


def test_descriptor_validator_rejects_futures_or_perps():
    d = _good_descriptor()
    d["is_futures_or_perp"] = True
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert "REJECT_FUTURES_OR_PERPS" in verdict["rejection_reasons"]


def test_descriptor_validator_rejects_account_auth_trading_endpoint():
    d = _good_descriptor()
    d["requires_account_auth"] = True
    d["requires_trading_endpoint"] = True
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert verdict["no_account_auth_ok"] is False
    assert "REJECT_TRADING_API_REQUIRING_ACCOUNT_AUTH" in verdict["rejection_reasons"]


def test_descriptor_validator_rejects_order_endpoint():
    d = _good_descriptor()
    d["requires_order_endpoint"] = True
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert verdict["no_order_endpoint_ok"] is False
    assert "REJECT_ORDER_ENDPOINT" in verdict["rejection_reasons"]


def test_descriptor_validator_rejects_portfolio_endpoint():
    d = _good_descriptor()
    d["requires_portfolio_endpoint"] = True
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert verdict["no_portfolio_endpoint_ok"] is False
    assert "REJECT_PORTFOLIO_ENDPOINT" in verdict["rejection_reasons"]


def test_descriptor_validator_rejects_paper_live_endpoint():
    d = _good_descriptor()
    d["requires_paper_live_endpoint"] = True
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert verdict["no_paper_live_endpoint_ok"] is False
    assert "REJECT_PAPER_LIVE_ENDPOINT" in verdict["rejection_reasons"]


def test_descriptor_validator_rejects_wrong_symbol():
    d = _good_descriptor()
    d["declared_symbols"] = ["BTCUSD", "DOGEUSD"]
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert verdict["symbols_ok"] is False
    assert any(r.startswith("REJECT_WRONG_SYMBOL") for r in verdict["rejection_reasons"])


def test_descriptor_validator_rejects_wrong_timeframe():
    d = _good_descriptor()
    d["declared_timeframes"] = ["1h"]
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert verdict["timeframe_ok"] is False
    assert any(
        r.startswith("REJECT_WRONG_TIMEFRAME") for r in verdict["rejection_reasons"]
    )


def test_descriptor_validator_rejects_missing_return_fields():
    d = _good_descriptor()
    d["return_fields"] = ["date", "open", "close"]
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert verdict["return_schema_ok"] is False
    assert any(
        r.startswith("REJECT_MISSING_RETURN_FIELDS")
        for r in verdict["rejection_reasons"]
    )


def test_descriptor_validator_rejects_unclear_license():
    d = _good_descriptor()
    d["has_clear_license_metadata"] = False
    d["source"] = ""
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert verdict["license_ok"] is False
    assert "REJECT_UNCLEAR_SOURCE_OR_LICENSE" in verdict["rejection_reasons"]


def test_descriptor_validator_rejects_bad_sample_row():
    d = _good_descriptor()
    d["sample_row"] = {"date": "x", "order_id": "1", "instrument_type": "spot"}
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert verdict["sample_row_ok"] is False
    assert "REJECT_SAMPLE_ROW_SCHEMA" in verdict["rejection_reasons"]


def test_descriptor_validator_rejects_secret_value():
    d = _good_descriptor()
    d["api_key"] = "should-never-be-here"
    verdict = _VALIDATE_DESCRIPTOR(d)
    assert verdict["provider_client_contract_valid"] is False
    assert verdict["no_secret_ok"] is False
    assert "REJECT_SECRET_PRESENT" in verdict["rejection_reasons"]


# --------------------------------------------------------------------------- #
# Build: happy path is valid and locked
# --------------------------------------------------------------------------- #
def test_default_contract_builds_and_validates():
    contract = _BUILD()
    assert contract["status"] == "PROVIDER_CLIENT_ADAPTER_CONTRACT_ONLY"
    assert contract["safe"] is True
    assert contract["this_contract_calls_provider"] is False
    assert contract["this_contract_implements_provider"] is False
    assert contract["this_contract_fetches_data"] is False
    assert contract["this_contract_reads_files"] is False
    assert contract["this_contract_writes_files"] is False
    assert contract["requires_human_provider_decision"] is True
    assert contract["provider_client_contract_valid"] is True
    assert contract["next_recommended_action"] == NEXT_RECOMMENDED_ACTION
    assert contract["real_data_qa_state"] == "BLOCKED"
    assert contract["baseline_backtest_state"] == "BLOCKED"
    assert contract["paper_live_state"] == "LOCKED"
    assert _VALIDATE(contract)["valid"] is True


def test_contract_capability_flags_all_false_and_gates_locked():
    contract = _BUILD()
    assert contract["executes"] is False
    assert contract["calls_provider"] is False
    assert contract["implements_real_provider"] is False
    assert contract["performs_data_fetch"] is False
    assert contract["imports_csv"] is False
    assert contract["reads_file_contents"] is False
    assert contract["uses_network"] is False
    assert contract["fetches_data"] is False
    assert contract["checks_live_credentials"] is False
    assert contract["reads_dotenv"] is False
    assert contract["exposes_secret"] is False
    assert contract["writes_data_files"] is False
    assert contract["runs_qa"] is False
    assert contract["runs_backtest"] is False
    assert contract["authorizes_nothing"] is True
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["unlocks_real_data_qa"] is False


def test_contract_carries_required_adapter_interface_sections():
    contract = _BUILD()
    iface = contract["adapter_interface"]
    assert iface["required_method"] == REQUIRED_ADAPTER_METHOD
    assert iface["method_signature"] == ADAPTER_METHOD_SIGNATURE
    assert iface["allowed_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert iface["allowed_timeframes"] == ["1d"]
    assert iface["required_return_fields"] == list(ADAPTER_REQUIRED_RETURN_FIELDS)
    assert iface["required_instrument_type"] == "spot"
    assert iface["provider_constraints"] == list(ADAPTER_PROVIDER_CONSTRAINTS)
    assert iface["rejection_rules"] == list(ADAPTER_REJECTION_RULES)
    assert iface["forbidden_return_fields"] == list(ADAPTER_FORBIDDEN_RETURN_FIELDS)
    # promoted top-level mirrors
    assert contract["required_adapter_method"] == REQUIRED_ADAPTER_METHOD
    assert contract["allowed_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert contract["allowed_timeframes"] == ["1d"]
    assert contract["required_return_fields"] == list(ADAPTER_REQUIRED_RETURN_FIELDS)
    assert contract["required_instrument_type"] == "spot"
    assert contract["provider_constraints"] == list(ADAPTER_PROVIDER_CONSTRAINTS)
    assert contract["rejection_rules"] == list(ADAPTER_REJECTION_RULES)


def test_contract_embeds_descriptor_verdict_consistently():
    contract = _BUILD()
    dv = contract["descriptor_verdict"]
    assert isinstance(dv, dict)
    assert (
        contract["provider_client_contract_valid"]
        == dv["provider_client_contract_valid"]
    )


def test_supplying_noncompliant_descriptor_marks_contract_invalid_but_still_safe():
    bad = _good_descriptor()
    bad["is_futures_or_perp"] = True
    contract = _BUILD({"descriptor": bad})
    # The contract itself is still safe/locked; it just reports the descriptor invalid.
    assert contract["provider_client_contract_valid"] is False
    assert contract["safe"] is True
    assert contract["real_data_qa_state"] == "BLOCKED"
    assert _VALIDATE(contract)["valid"] is True


# --------------------------------------------------------------------------- #
# Unsafe inputs: forbidden flag / off-boundary mission flow
# --------------------------------------------------------------------------- #
def test_forbidden_flag_marks_contract_unsafe():
    contract = _BUILD({"fetch_data_now": True})
    assert contract["safe"] is False
    assert "fetch_data_now" in contract["forbidden_flag_hits"]
    assert contract["this_contract_fetches_data"] is False
    assert _VALIDATE(contract)["valid"] is True


def test_implement_real_provider_request_marks_contract_unsafe():
    contract = _BUILD({"implement_real_provider": True})
    assert contract["safe"] is False
    assert "implement_real_provider" in contract["forbidden_flag_hits"]


def test_gate_unlock_request_marks_contract_unsafe():
    contract = _BUILD({"unlock_real_data_qa": True})
    assert contract["safe"] is False
    assert "unlock_real_data_qa" in contract["forbidden_flag_hits"]


def test_off_boundary_mission_flow_marks_contract_unsafe():
    contract = _BUILD({"mission_flow_current_stage": "SOMETHING_ELSE"})
    assert contract["safe"] is False
    assert contract["mission_flow_aligned"] is False


# --------------------------------------------------------------------------- #
# Secret never carried
# --------------------------------------------------------------------------- #
def test_secret_value_in_input_is_never_carried_into_contract():
    contract = _BUILD({"api_key": "SHOULD-NEVER-APPEAR"})
    assert "SHOULD-NEVER-APPEAR" not in _RENDER(contract)
    assert _VALIDATE(contract)["no_secret_value_fields"] is True


def test_boolean_secret_flag_is_not_a_secret_value():
    assert _VALIDATE(_BUILD())["no_secret_value_fields"] is True


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_two_builds_are_equivalent():
    assert _BUILD() == _BUILD()


def test_build_does_not_mutate_caller_payload():
    import copy

    payload = {"mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE}
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


# --------------------------------------------------------------------------- #
# Validation tamper rejections
# --------------------------------------------------------------------------- #
def test_validate_rejects_tampered_executes():
    contract = _BUILD()
    contract["executes"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_this_contract_fetches_data_true():
    contract = _BUILD()
    contract["this_contract_fetches_data"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["this_fetches_false"] is False


def test_validate_rejects_unlocked_gate():
    contract = _BUILD()
    contract["real_data_qa_blocked"] = False
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_validate_rejects_unlocked_state():
    contract = _BUILD()
    contract["real_data_qa_state"] = "OPEN"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["states_blocked_locked"] is False


def test_validate_rejects_wrong_next_action():
    contract = _BUILD()
    contract["next_recommended_action"] = "GO_LIVE"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["next_action_ok"] is False


def test_validate_rejects_tampered_method():
    contract = _BUILD()
    contract["required_adapter_method"] = "place_order"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["method_ok"] is False


def test_validate_rejects_tampered_symbols():
    contract = _BUILD()
    contract["allowed_symbols"] = ["BTCUSD", "DOGEUSD"]
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["symbols_ok"] is False


def test_validate_rejects_tampered_timeframe():
    contract = _BUILD()
    contract["allowed_timeframes"] = ["1h"]
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["timeframes_ok"] is False


def test_validate_rejects_tampered_instrument_type():
    contract = _BUILD()
    contract["required_instrument_type"] = "futures"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["instrument_ok"] is False


def test_validate_rejects_tampered_authorizes_nothing():
    contract = _BUILD()
    contract["authorizes_nothing"] = False
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["authorizes_nothing"] is False


def test_validate_rejects_secret_value():
    contract = _BUILD()
    contract["api_key"] = "leaked-value"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["no_secret_value_fields"] is False


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #
def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith(
        "# Selected Read-Only Spot Provider Client Adapter Contract"
    )
    assert "## Allowed Symbols" in text
    assert "## Allowed Timeframe" in text
    assert "## Required Return Fields" in text
    assert "## Provider Constraints" in text
    assert "## Rejection Rules" in text
    assert "## Next Recommended Action" in text
    assert "## Operator Next Step" in text
    assert "fetch_read_only_daily_spot_ohlcv" in text
    assert "HOLD_FOR_CONCRETE_PROVIDER_IMPLEMENTATION_OR_MANUAL_CSV" in text


def test_render_never_leaks_a_secret():
    text = _RENDER(_BUILD({"access_token": "TOP-SECRET-VALUE"}))
    assert "TOP-SECRET-VALUE" not in text


# --------------------------------------------------------------------------- #
# AST purity: __future__ / typing / sparta_commander roots only; no os / json /
# csv / network / credential modules; no os.environ access; no open / write_* call
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORT_ROOTS = {"__future__", "typing", "sparta_commander"}
_FORBIDDEN_MODULE_TOKENS = {
    "os",
    "sys",
    "json",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
    "requests",
    "http",
    "urllib",
    "importlib",
    "pandas",
    "numpy",
    "ccxt",
    "databento",
    "dotenv",
    "datetime",
    "time",
    "random",
    "pickle",
    "sqlite3",
    "csv",
}


def _module_ast():
    return ast.parse(_MODPATH.read_text(encoding="utf-8"))


def test_module_imports_are_within_allowed_roots():
    tree = _module_ast()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in _ALLOWED_IMPORT_ROOTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORT_ROOTS, node.module


def test_module_imports_no_os_network_or_credential_modules():
    imported_roots = set()
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported_roots.add((node.module or "").split(".")[0])
    assert not (imported_roots & _FORBIDDEN_MODULE_TOKENS), (
        imported_roots & _FORBIDDEN_MODULE_TOKENS
    )


def test_module_never_reads_environment():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"environ", "getenv", "environb"}, node.attr


def test_module_has_no_eval_exec_import_dunder():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"eval", "exec", "compile", "__import__", "input"}


def test_module_has_no_filesystem_write_capability_of_its_own():
    # The contract must own NO filesystem-write capability: it never calls open,
    # write_text, write_bytes, or write_json. Asserted both lexically (so the
    # safety verifier's `filesystem_write` pattern cannot match) and via the AST.
    src = _MODPATH.read_text(encoding="utf-8")
    assert "open(" not in src
    assert ".write_text(" not in src
    assert ".write_bytes(" not in src
    assert "write_json(" not in src
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id != "open"
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"write_text", "write_bytes", "write_json"}


# --------------------------------------------------------------------------- #
# commander_2_safety allowlist (exactly two additive lines)
# --------------------------------------------------------------------------- #
def test_commander_safety_allowlist_includes_the_two_additive_entries():
    from sparta_commander.commander_2_safety import (
        COMMANDER_2_MODULES,
        COMMANDER_2_TESTS,
    )

    assert _MODULE_ALLOWLIST_LINE in COMMANDER_2_MODULES
    assert _TEST_ALLOWLIST_LINE in COMMANDER_2_TESTS
    assert COMMANDER_2_MODULES.count(_MODULE_ALLOWLIST_LINE) == 1
    assert COMMANDER_2_TESTS.count(_TEST_ALLOWLIST_LINE) == 1


def test_commander_safety_only_two_new_lines_for_this_module():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert src.count(_MODULE_ALLOWLIST_LINE) == 1
    assert src.count(_TEST_ALLOWLIST_LINE) == 1
