"""Tests for the Crypto-D1 Manual CSV Spot Data Import Plan Contract (Block 147).

The contract DEFINES the requirements and validation plan for a FUTURE,
human-performed manual CSV import of the three missing Crypto-D1 daily SPOT pairs
(BTCUSD@1d, ETHUSD@1d, SOLUSD@1d). It is a PURE, stdlib-only, read-only reasoning
layer: it imports no CSV, reads or parses no file's contents, writes nothing (no
cache, no report), calls no provider, opens no network, reads no credential / .env,
runs no validation / QA / baseline / backtest, and unlocks no gate. It only reasons
over static, metadata-only candidate CSV *source descriptors* (NEVER file contents).

These tests assert: schema / constants; mission-flow truth sync against the live
status module; the required source criteria / symbols / columns; the rejection
rules; the future validation checks; the hard stops; the seven import categories;
deterministic evaluation covering every category (clean -> ACCEPTED_FOR_FUTURE_IMPORT,
partial -> NEEDS_SOURCE_REVIEW, futures -> REJECTED_WRONG_INSTRUMENT, trading-export
-> REJECTED_TRADING_EXPORT, unclear-license -> REJECTED_LICENSE_OR_SOURCE_UNCLEAR,
account-required -> REJECTED_REQUIRES_ACCOUNT_ACCESS, intraday -> REJECTED_INTRADAY_ONLY);
symbol-alias coverage (BTC/USD); the single next recommended action
HOLD_FOR_MANUAL_CSV_IMPORT_APPROVAL; that the contract imports / reads / writes
nothing; the approved FUTURE-only input / output / report paths recorded without any
write; that every capability flag is False and every gate stays locked; that a
secret value is never carried; determinism / caller-payload isolation; validation
tamper rejections; render; AST purity (only __future__ / typing / sparta_commander
roots, no os / json / network / credential modules, no os.environ access, NO open /
write_* call); and the two additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_manual_csv_spot_data_import_plan_contract import (  # noqa: E501
    CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT,
    CATEGORY_NEEDS_SOURCE_REVIEW,
    CATEGORY_REJECTED_INTRADAY_ONLY,
    CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR,
    CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS,
    CATEGORY_REJECTED_TRADING_EXPORT,
    CATEGORY_REJECTED_WRONG_INSTRUMENT,
    DEFAULT_CSV_SOURCE_CANDIDATES,
    IMPORT_CATEGORIES,
    IMPORT_CORE_RULE,
    IMPORT_HARD_STOPS,
    IMPORT_INPUT_CANDIDATE_PATH,
    IMPORT_LABEL,
    IMPORT_MODE,
    IMPORT_REJECTION_RULES,
    IMPORT_REPORT_DIR,
    IMPORT_REQUIRED_COLUMNS,
    IMPORT_REQUIRED_SYMBOLS,
    IMPORT_REQUIRED_TIMEFRAMES,
    IMPORT_SCHEMA_VERSION,
    IMPORT_SOURCE_CRITERIA,
    IMPORT_STATUS,
    IMPORT_SYMBOL_ALIASES,
    IMPORT_VALIDATED_OUTPUT_PATH,
    IMPORT_VALIDATION_CHECKS,
    NEXT_RECOMMENDED_ACTION,
    build_crypto_d1_manual_csv_spot_data_import_plan_contract,
    evaluate_csv_source_descriptor,
    render_crypto_d1_manual_csv_spot_data_import_plan_contract_markdown,
    validate_crypto_d1_manual_csv_spot_data_import_plan_contract,
)
from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_manual_csv_spot_data_import_plan_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_manual_csv_spot_data_import_plan_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_manual_csv_spot_data_import_plan_contract.py"
)

_BUILD = build_crypto_d1_manual_csv_spot_data_import_plan_contract
_VALIDATE = validate_crypto_d1_manual_csv_spot_data_import_plan_contract
_RENDER = render_crypto_d1_manual_csv_spot_data_import_plan_contract_markdown


def _clean_descriptor(**overrides):
    base = {
        "name": "clean",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_ohlcv_columns": True,
        "has_date_column_with_format": True,
        "has_clear_license_metadata": True,
        "has_account_or_order_fields": False,
        "requires_account_access": False,
        "intraday_only": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    }
    base.update(overrides)
    return base


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert IMPORT_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_manual_csv_spot_data_import_plan_contract.v1"
    )
    assert IMPORT_LABEL == (
        "Block 147 - Crypto-D1 Manual CSV Spot Data Import Plan Contract"
    )
    assert IMPORT_STATUS == "MANUAL_CSV_IMPORT_PLAN_ONLY"
    assert IMPORT_MODE == "RESEARCH_ONLY"
    assert "authorizes nothing" in IMPORT_CORE_RULE.lower()
    assert "blocked" in IMPORT_CORE_RULE.lower()


def test_required_symbols_timeframes_columns():
    assert IMPORT_REQUIRED_SYMBOLS == ("BTCUSD", "ETHUSD", "SOLUSD")
    assert IMPORT_REQUIRED_TIMEFRAMES == ("1d",)
    assert IMPORT_REQUIRED_COLUMNS == (
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    )


def test_symbol_aliases_include_slash_and_dash_forms():
    assert "BTC/USD" in IMPORT_SYMBOL_ALIASES["BTCUSD"]
    assert "ETH-USD" in IMPORT_SYMBOL_ALIASES["ETHUSD"]
    assert "SOL/USD" in IMPORT_SYMBOL_ALIASES["SOLUSD"]


def test_import_categories_are_the_seven_required():
    assert IMPORT_CATEGORIES == (
        CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT,
        CATEGORY_NEEDS_SOURCE_REVIEW,
        CATEGORY_REJECTED_WRONG_INSTRUMENT,
        CATEGORY_REJECTED_TRADING_EXPORT,
        CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR,
        CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS,
        CATEGORY_REJECTED_INTRADAY_ONLY,
    )
    assert CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT == "ACCEPTED_FOR_FUTURE_IMPORT"
    assert CATEGORY_NEEDS_SOURCE_REVIEW == "NEEDS_SOURCE_REVIEW"
    assert CATEGORY_REJECTED_WRONG_INSTRUMENT == "REJECTED_WRONG_INSTRUMENT"
    assert CATEGORY_REJECTED_TRADING_EXPORT == "REJECTED_TRADING_EXPORT"
    assert (
        CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR
        == "REJECTED_LICENSE_OR_SOURCE_UNCLEAR"
    )
    assert (
        CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS
        == "REJECTED_REQUIRES_ACCOUNT_ACCESS"
    )
    assert CATEGORY_REJECTED_INTRADAY_ONLY == "REJECTED_INTRADAY_ONLY"


def test_next_recommended_action_is_hold_for_manual_csv_import_approval():
    assert NEXT_RECOMMENDED_ACTION == "HOLD_FOR_MANUAL_CSV_IMPORT_APPROVAL"


def test_source_criteria_cover_the_six_required_dimensions():
    blob = " ".join(IMPORT_SOURCE_CRITERIA).lower()
    assert len(IMPORT_SOURCE_CRITERIA) >= 6
    assert "license" in blob
    assert "spot" in blob and "futures" in blob
    assert "usd" in blob
    assert "daily" in blob
    assert "ohlcv" in blob
    assert "date column" in blob


def test_rejection_rules_present():
    blob = " ".join(IMPORT_REJECTION_RULES).lower()
    assert len(IMPORT_REJECTION_RULES) >= 5
    assert "futures" in blob
    assert "account" in blob or "order" in blob
    assert "license" in blob
    assert "intraday" in blob


def test_validation_checks_cover_the_seven_required():
    blob = " ".join(IMPORT_VALIDATION_CHECKS).lower()
    assert len(IMPORT_VALIDATION_CHECKS) >= 7
    assert "schema_check" in blob
    assert "symbol_timeframe_check" in blob
    assert "duplicate_date_check" in blob
    assert "missing_date_gap_check" in blob
    assert "ohlc_sanity_check" in blob
    assert "volume_sanity_check" in blob
    assert "source_license_check" in blob


def test_hard_stops_present():
    blob = " ".join(IMPORT_HARD_STOPS).lower()
    assert len(IMPORT_HARD_STOPS) >= 6
    assert "account" in blob or "order" in blob
    assert "futures" in blob
    assert "license" in blob
    assert "unlock" in blob


def test_approved_future_paths_constants():
    assert IMPORT_INPUT_CANDIDATE_PATH == "data/manual_import_candidates/crypto_d1/"
    assert IMPORT_VALIDATED_OUTPUT_PATH == "data/crypto_d1_spot_cache/"
    assert IMPORT_REPORT_DIR == "reports/research_os/data_qa/"


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# Evaluation: deterministic, one bucket per descriptor
# --------------------------------------------------------------------------- #
def test_clean_spot_csv_is_accepted_for_future_import():
    out = evaluate_csv_source_descriptor(_clean_descriptor())
    assert out["category"] == CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT


def test_partial_columns_csv_needs_source_review():
    out = evaluate_csv_source_descriptor(
        _clean_descriptor(name="partial", has_ohlcv_columns=False)
    )
    assert out["category"] == CATEGORY_NEEDS_SOURCE_REVIEW


def test_futures_csv_is_rejected_wrong_instrument():
    out = evaluate_csv_source_descriptor(
        _clean_descriptor(name="futures", instrument="futures", is_futures_or_perp=True)
    )
    assert out["category"] == CATEGORY_REJECTED_WRONG_INSTRUMENT
    assert out["criteria"]["is_futures_or_perp"] is True


def test_perps_instrument_string_is_rejected_wrong_instrument():
    out = evaluate_csv_source_descriptor(
        _clean_descriptor(name="perps", instrument="perps", is_futures_or_perp=False)
    )
    assert out["category"] == CATEGORY_REJECTED_WRONG_INSTRUMENT


def test_trading_export_csv_is_rejected_trading_export():
    out = evaluate_csv_source_descriptor(
        _clean_descriptor(name="export", has_account_or_order_fields=True)
    )
    assert out["category"] == CATEGORY_REJECTED_TRADING_EXPORT
    assert out["criteria"]["has_account_or_order_fields"] is True


def test_unclear_license_csv_is_rejected_license_or_source_unclear():
    out = evaluate_csv_source_descriptor(
        _clean_descriptor(name="unclear", has_clear_license_metadata=False)
    )
    assert out["category"] == CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR


def test_account_required_csv_is_rejected_requires_account_access():
    out = evaluate_csv_source_descriptor(
        _clean_descriptor(name="broker", requires_account_access=True)
    )
    assert out["category"] == CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS


def test_intraday_only_csv_is_rejected_intraday_only():
    out = evaluate_csv_source_descriptor(
        _clean_descriptor(name="intraday", daily_timeframe=False, intraday_only=True)
    )
    assert out["category"] == CATEGORY_REJECTED_INTRADAY_ONLY


def test_symbol_alias_slash_form_satisfies_coverage():
    out = evaluate_csv_source_descriptor(
        _clean_descriptor(
            name="aliased", covers_symbols=["BTC/USD", "ETH-USD", "SOL/USD"]
        )
    )
    assert out["category"] == CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT


def test_missing_one_symbol_needs_source_review():
    out = evaluate_csv_source_descriptor(
        _clean_descriptor(name="btc_eth_only", covers_symbols=["BTCUSD", "ETHUSD"])
    )
    assert out["category"] == CATEGORY_NEEDS_SOURCE_REVIEW


def test_trading_export_takes_priority_over_futures():
    # safety-first: account/order fields rejection precedes instrument check
    out = evaluate_csv_source_descriptor(
        _clean_descriptor(
            name="both",
            instrument="futures",
            is_futures_or_perp=True,
            has_account_or_order_fields=True,
        )
    )
    assert out["category"] == CATEGORY_REJECTED_TRADING_EXPORT


def test_default_candidates_cover_every_category():
    cats = {
        evaluate_csv_source_descriptor(c)["category"]
        for c in DEFAULT_CSV_SOURCE_CANDIDATES
    }
    assert cats == set(IMPORT_CATEGORIES)


def test_evaluation_is_deterministic():
    for c in DEFAULT_CSV_SOURCE_CANDIDATES:
        assert evaluate_csv_source_descriptor(c) == evaluate_csv_source_descriptor(c)


# --------------------------------------------------------------------------- #
# Build: happy path is valid and locked
# --------------------------------------------------------------------------- #
def test_default_contract_builds_and_validates():
    contract = _BUILD()
    assert contract["status"] == "MANUAL_CSV_IMPORT_PLAN_ONLY"
    assert contract["safe"] is True
    assert contract["this_contract_imports_csv"] is False
    assert contract["this_contract_reads_file_contents"] is False
    assert contract["this_contract_writes_files"] is False
    assert contract["requires_human_import"] is True
    assert contract["next_recommended_action"] == "HOLD_FOR_MANUAL_CSV_IMPORT_APPROVAL"
    assert contract["real_data_qa_state"] == "BLOCKED"
    assert contract["baseline_backtest_state"] == "BLOCKED"
    assert contract["paper_live_state"] == "LOCKED"
    assert _VALIDATE(contract)["valid"] is True


def test_contract_capability_flags_all_false_and_gates_locked():
    contract = _BUILD()
    assert contract["executes"] is False
    assert contract["imports_csv"] is False
    assert contract["reads_file_contents"] is False
    assert contract["reads_csv"] is False
    assert contract["parses_csv"] is False
    assert contract["calls_provider_api"] is False
    assert contract["uses_network"] is False
    assert contract["fetches_data"] is False
    assert contract["writes_cache"] is False
    assert contract["writes_report"] is False
    assert contract["runs_validation"] is False
    assert contract["authorizes_nothing"] is True
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["unlocks_real_data_qa"] is False


def test_contract_spec_carries_required_sections():
    spec = _BUILD()["import_plan"]
    assert len(spec["source_criteria"]) >= 6
    assert spec["required_columns"] == list(IMPORT_REQUIRED_COLUMNS)
    assert spec["required_symbols"] == list(IMPORT_REQUIRED_SYMBOLS)
    assert len(spec["rejection_rules"]) >= 5
    assert len(spec["future_validation_checks"]) >= 7
    assert len(spec["hard_stops"]) >= 6
    assert spec["categories"] == list(IMPORT_CATEGORIES)
    assert spec["evaluations"]
    assert spec["next_recommended_action"] == "HOLD_FOR_MANUAL_CSV_IMPORT_APPROVAL"
    paths = spec["approved_future_paths"]
    assert paths["input_candidate_path"] == IMPORT_INPUT_CANDIDATE_PATH
    assert paths["validated_output_path"] == IMPORT_VALIDATED_OUTPUT_PATH
    assert paths["report_dir"] == IMPORT_REPORT_DIR
    nwc = spec["no_write_confirmation"]
    assert nwc["reads_file_contents"] is False
    assert nwc["writes_cache"] is False
    assert nwc["writes_report"] is False
    assert nwc["approved_paths_are_future_only"] is True
    assert nwc["paths_created_now"] is False
    nuc = spec["no_unlock_confirmation"]
    assert nuc["unlocks_real_data_qa"] is False
    assert nuc["real_data_qa_state"] == "BLOCKED"
    assert nuc["baseline_backtest_state"] == "BLOCKED"
    assert nuc["paper_live_state"] == "LOCKED"


def test_contract_every_default_candidate_is_evaluated():
    spec = _BUILD()["import_plan"]
    assert len(spec["evaluations"]) == len(DEFAULT_CSV_SOURCE_CANDIDATES)
    counts = spec["category_counts"]
    assert counts[CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT] >= 1
    assert counts[CATEGORY_REJECTED_WRONG_INSTRUMENT] >= 1
    assert counts[CATEGORY_REJECTED_TRADING_EXPORT] >= 1
    assert counts[CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS] >= 1
    assert counts[CATEGORY_REJECTED_INTRADAY_ONLY] >= 1


# --------------------------------------------------------------------------- #
# Unsafe inputs: forbidden flag / off-boundary mission flow
# --------------------------------------------------------------------------- #
def test_forbidden_flag_marks_contract_unsafe():
    contract = _BUILD({"import_csv_now": True})
    assert contract["safe"] is False
    assert "import_csv_now" in contract["forbidden_flag_hits"]
    # but every real capability flag is still False and gates still locked
    assert contract["executes"] is False
    assert contract["imports_csv"] is False
    assert _VALIDATE(contract)["valid"] is True


def test_read_file_contents_request_marks_contract_unsafe():
    contract = _BUILD({"read_file_contents_now": True})
    assert contract["safe"] is False
    assert "read_file_contents_now" in contract["forbidden_flag_hits"]


def test_write_cache_request_marks_contract_unsafe():
    contract = _BUILD({"write_cache_now": True})
    assert contract["safe"] is False
    assert "write_cache_now" in contract["forbidden_flag_hits"]


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


def test_validate_rejects_imports_csv_true():
    contract = _BUILD()
    contract["this_contract_imports_csv"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["this_imports_false"] is False


def test_validate_rejects_reads_file_contents_true():
    contract = _BUILD()
    contract["this_contract_reads_file_contents"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["this_reads_false"] is False


def test_validate_rejects_writes_files_true():
    contract = _BUILD()
    contract["this_contract_writes_files"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["this_writes_false"] is False


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


def test_validate_rejects_cache_write_marked_true():
    contract = _BUILD()
    contract["import_plan"]["no_write_confirmation"]["writes_cache"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["no_write_ok"] is False


def test_validate_rejects_futures_misclassified_as_accepted():
    contract = _BUILD()
    for item in contract["import_plan"]["evaluations"]:
        if item["criteria"].get("is_futures_or_perp") is True:
            item["category"] = CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["futures_rejected_ok"] is False


def test_validate_rejects_trading_export_misclassified_as_accepted():
    contract = _BUILD()
    for item in contract["import_plan"]["evaluations"]:
        if item["criteria"].get("has_account_or_order_fields") is True:
            item["category"] = CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["trading_export_rejected_ok"] is False


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
        "# Crypto-D1 Manual CSV Spot Data Import Plan Contract"
    )
    assert "## 1. Required CSV Source Criteria" in text
    assert "## 3. Required Columns" in text
    assert "## 4. Rejection Rules" in text
    assert "## 6. Future Validation Checks" in text
    assert "## 7. Hard Stops" in text
    assert "HOLD_FOR_MANUAL_CSV_IMPORT_APPROVAL" in text
    assert "data/manual_import_candidates/crypto_d1/" in text


def test_render_never_leaks_a_secret():
    text = _RENDER(_BUILD({"access_token": "TOP-SECRET-VALUE"}))
    assert "TOP-SECRET-VALUE" not in text


# --------------------------------------------------------------------------- #
# AST purity: __future__ / typing / sparta_commander roots only; no os / json /
# network / credential modules; no os.environ access; no open / write_* call
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
