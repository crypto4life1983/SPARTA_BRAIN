"""Tests for the Automated Read-Only Crypto-D1 Spot Data Source Acquisition
Orchestrator (Block 148).

The orchestrator AUTOMATICALLY ranks / selects the safest source path for the three
missing Crypto-D1 daily SPOT pairs (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d) from static,
metadata-only candidate descriptors and emits a human-approval packet. It is a
PURE, stdlib-only reasoning layer: it calls no provider, fetches nothing, imports no
CSV, reads/parses no file's contents, opens no network, reads no credential / .env,
writes nothing, runs no QA / baseline / backtest, and unlocks no gate -- even when a
caller passes human_run_approved.

These tests assert: schema / constants; mission-flow truth sync against the live
status module; the eight evaluation categories; deterministic evaluation covering
every category (trading API -> REJECTED_TRADING_API, broker/account API ->
REJECTED_BROKER_ACCOUNT_API, account/portfolio access -> REJECTED_REQUIRES_ACCOUNT_ACCESS,
futures -> REJECTED_WRONG_INSTRUMENT, unclear-license -> REJECTED_LICENSE_OR_SOURCE_UNCLEAR,
clean API -> ELIGIBLE_CLEAR_LICENSE_API, manual CSV -> ELIGIBLE_MANUAL_CSV,
incomplete -> NEEDS_SOURCE_REVIEW); the ranking (clear-license API > manual CSV >
hold); the required orchestrator outputs (selected_candidate_type /
selected_candidate_name / reason / required_human_approval_packet / allowed_paths /
forbidden_paths / scoped_tests / hard_stop_rules / next_recommended_action); that
human_run_approved never causes a run; that every capability flag is False and every
gate stays locked; that a secret value is never carried; determinism / caller-payload
isolation; validation tamper rejections; render; AST purity (only __future__ /
typing / sparta_commander roots, no os / json / network / credential modules, no
os.environ access, NO open / write_* call); and the two additive commander_2_safety
allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator import (  # noqa: E501
    CATEGORY_ELIGIBLE_CLEAR_LICENSE_API,
    CATEGORY_ELIGIBLE_MANUAL_CSV,
    CATEGORY_NEEDS_SOURCE_REVIEW,
    CATEGORY_REJECTED_BROKER_ACCOUNT_API,
    CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR,
    CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS,
    CATEGORY_REJECTED_TRADING_API,
    CATEGORY_REJECTED_WRONG_INSTRUMENT,
    DEFAULT_SOURCE_CANDIDATES,
    NEXT_ACTION_API,
    NEXT_ACTION_CSV,
    NEXT_ACTION_HOLD,
    ORCH_ALLOWED_PATHS,
    ORCH_CATEGORIES,
    ORCH_CORE_RULE,
    ORCH_FORBIDDEN_PATHS,
    ORCH_HARD_STOP_RULES,
    ORCH_LABEL,
    ORCH_MODE,
    ORCH_REQUIRED_SYMBOLS,
    ORCH_REQUIRED_TIMEFRAMES,
    ORCH_SCHEMA_VERSION,
    ORCH_SCOPED_TESTS,
    ORCH_STATUS,
    ORCH_SYMBOL_ALIASES,
    SELECTED_TYPE_CLEAR_LICENSE_API,
    SELECTED_TYPE_HOLD,
    SELECTED_TYPE_MANUAL_CSV,
    build_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator,
    evaluate_source_candidate,
    orchestrate_crypto_d1_spot_data_source_acquisition,
    render_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator_markdown,
    validate_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator,
)
from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator.py"
)

_BUILD = build_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator
_VALIDATE = validate_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator
_RENDER = render_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator_markdown


def _clean_api(**overrides):
    base = {
        "name": "clean_api",
        "endpoint_type": "read_only_historical",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "read_only_historical": True,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_clear_license_metadata": True,
        "requires_trading_endpoint": False,
        "requires_order_endpoint": False,
        "requires_account_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_account_access": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    }
    base.update(overrides)
    return base


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert ORCH_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator.v1"
    )
    assert ORCH_LABEL == (
        "Block 148 - Automated Read-Only Crypto-D1 Spot Data Source Acquisition Orchestrator"
    )
    assert ORCH_STATUS == "AUTOMATED_SOURCE_SELECTION_ONLY"
    assert ORCH_MODE == "RESEARCH_ONLY"
    assert "authorizes nothing" in ORCH_CORE_RULE.lower()
    assert "blocked" in ORCH_CORE_RULE.lower()
    assert "human_run_approved" in ORCH_CORE_RULE.lower()


def test_required_symbols_and_timeframes():
    assert ORCH_REQUIRED_SYMBOLS == ("BTCUSD", "ETHUSD", "SOLUSD")
    assert ORCH_REQUIRED_TIMEFRAMES == ("1d",)


def test_symbol_aliases_include_slash_and_dash_forms():
    assert "BTC/USD" in ORCH_SYMBOL_ALIASES["BTCUSD"]
    assert "ETH-USD" in ORCH_SYMBOL_ALIASES["ETHUSD"]
    assert "SOL/USD" in ORCH_SYMBOL_ALIASES["SOLUSD"]


def test_categories_are_the_eight_required():
    assert ORCH_CATEGORIES == (
        CATEGORY_ELIGIBLE_CLEAR_LICENSE_API,
        CATEGORY_ELIGIBLE_MANUAL_CSV,
        CATEGORY_NEEDS_SOURCE_REVIEW,
        CATEGORY_REJECTED_TRADING_API,
        CATEGORY_REJECTED_BROKER_ACCOUNT_API,
        CATEGORY_REJECTED_WRONG_INSTRUMENT,
        CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR,
        CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS,
    )
    assert CATEGORY_ELIGIBLE_CLEAR_LICENSE_API == "ELIGIBLE_CLEAR_LICENSE_API"
    assert CATEGORY_ELIGIBLE_MANUAL_CSV == "ELIGIBLE_MANUAL_CSV"
    assert CATEGORY_REJECTED_TRADING_API == "REJECTED_TRADING_API"
    assert CATEGORY_REJECTED_BROKER_ACCOUNT_API == "REJECTED_BROKER_ACCOUNT_API"
    assert CATEGORY_REJECTED_WRONG_INSTRUMENT == "REJECTED_WRONG_INSTRUMENT"
    assert (
        CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR
        == "REJECTED_LICENSE_OR_SOURCE_UNCLEAR"
    )
    assert (
        CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS
        == "REJECTED_REQUIRES_ACCOUNT_ACCESS"
    )


def test_selected_types_and_next_actions():
    assert SELECTED_TYPE_CLEAR_LICENSE_API == (
        "CLEAR_LICENSE_READ_ONLY_SPOT_HISTORICAL_PROVIDER"
    )
    assert SELECTED_TYPE_MANUAL_CSV == "MANUAL_CSV_IMPORT"
    assert SELECTED_TYPE_HOLD == "HOLD_NO_SAFE_SOURCE"
    assert NEXT_ACTION_API == (
        "HOLD_FOR_HUMAN_RUN_APPROVAL_OF_SELECTED_READ_ONLY_PROVIDER"
    )
    assert NEXT_ACTION_CSV == "HOLD_FOR_MANUAL_CSV_IMPORT_APPROVAL"
    assert NEXT_ACTION_HOLD == "HOLD_NO_SAFE_SOURCE_AVAILABLE"


def test_allowed_forbidden_paths_and_scoped_tests():
    assert ORCH_ALLOWED_PATHS == (
        "data/manual_import_candidates/crypto_d1/",
        "data/crypto_d1_spot_cache/",
        "reports/research_os/data_qa/",
    )
    assert len(ORCH_FORBIDDEN_PATHS) >= 6
    assert len(ORCH_HARD_STOP_RULES) >= 6
    assert ORCH_SCOPED_TESTS == (
        "tests/test_strategy_factory_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator.py",
    )


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
def test_clean_api_is_eligible_clear_license_api():
    out = evaluate_source_candidate(_clean_api())
    assert out["category"] == CATEGORY_ELIGIBLE_CLEAR_LICENSE_API


def test_manual_csv_is_eligible_manual_csv():
    out = evaluate_source_candidate(
        _clean_api(name="csv", endpoint_type="manual_import", kind="manual_import")
    )
    assert out["category"] == CATEGORY_ELIGIBLE_MANUAL_CSV


def test_trading_api_is_rejected_trading_api():
    out = evaluate_source_candidate(
        _clean_api(name="trade", endpoint_type="trading_api", requires_trading_endpoint=True)
    )
    assert out["category"] == CATEGORY_REJECTED_TRADING_API
    assert out["criteria"]["requires_trading_endpoint"] is True


def test_broker_account_api_is_rejected_broker_account_api():
    out = evaluate_source_candidate(
        _clean_api(name="broker", endpoint_type="broker_account_api")
    )
    assert out["category"] == CATEGORY_REJECTED_BROKER_ACCOUNT_API
    assert out["criteria"]["requires_broker_account_api"] is True


def test_account_access_is_rejected_requires_account_access():
    out = evaluate_source_candidate(
        _clean_api(name="acct", requires_account_endpoint=True)
    )
    assert out["category"] == CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS


def test_portfolio_access_is_rejected_requires_account_access():
    out = evaluate_source_candidate(
        _clean_api(name="pf", requires_portfolio_endpoint=True)
    )
    assert out["category"] == CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS


def test_futures_is_rejected_wrong_instrument():
    out = evaluate_source_candidate(
        _clean_api(name="fut", instrument="futures", is_futures_or_perp=True)
    )
    assert out["category"] == CATEGORY_REJECTED_WRONG_INSTRUMENT


def test_perps_instrument_string_is_rejected_wrong_instrument():
    out = evaluate_source_candidate(
        _clean_api(name="perp", instrument="perps", is_futures_or_perp=False)
    )
    assert out["category"] == CATEGORY_REJECTED_WRONG_INSTRUMENT


def test_unclear_license_is_rejected_license_or_source_unclear():
    out = evaluate_source_candidate(
        _clean_api(name="unclear", has_clear_license_metadata=False)
    )
    assert out["category"] == CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR


def test_incomplete_coverage_needs_source_review():
    out = evaluate_source_candidate(
        _clean_api(name="partial", covers_symbols=["BTCUSD"])
    )
    assert out["category"] == CATEGORY_NEEDS_SOURCE_REVIEW


def test_symbol_alias_slash_form_satisfies_coverage():
    out = evaluate_source_candidate(
        _clean_api(name="aliased", covers_symbols=["BTC/USD", "ETH-USD", "SOL/USD"])
    )
    assert out["category"] == CATEGORY_ELIGIBLE_CLEAR_LICENSE_API


def test_trading_api_takes_priority_over_futures():
    # safety-first: trading endpoint rejection precedes instrument check
    out = evaluate_source_candidate(
        _clean_api(
            name="both",
            endpoint_type="trading_api",
            requires_trading_endpoint=True,
            instrument="futures",
            is_futures_or_perp=True,
        )
    )
    assert out["category"] == CATEGORY_REJECTED_TRADING_API


def test_default_candidates_cover_every_category():
    cats = {
        evaluate_source_candidate(c)["category"] for c in DEFAULT_SOURCE_CANDIDATES
    }
    assert cats == set(ORCH_CATEGORIES)


def test_evaluation_is_deterministic():
    for c in DEFAULT_SOURCE_CANDIDATES:
        assert evaluate_source_candidate(c) == evaluate_source_candidate(c)


# --------------------------------------------------------------------------- #
# Ranking / selection
# --------------------------------------------------------------------------- #
def test_default_selection_picks_clear_license_api():
    out = orchestrate_crypto_d1_spot_data_source_acquisition()
    assert out["selected_candidate_type"] == SELECTED_TYPE_CLEAR_LICENSE_API
    assert out["selected_candidate_name"] == (
        "clear_license_readonly_spot_history_api_archetype"
    )
    assert out["next_recommended_action"] == NEXT_ACTION_API


def test_selection_falls_back_to_manual_csv_when_no_safe_api():
    # only a manual CSV candidate is eligible
    out = orchestrate_crypto_d1_spot_data_source_acquisition(
        {
            "candidates": [
                _clean_api(name="csv", endpoint_type="manual_import", kind="manual_import"),
                _clean_api(name="trade", endpoint_type="trading_api", requires_trading_endpoint=True),
            ]
        }
    )
    assert out["selected_candidate_type"] == SELECTED_TYPE_MANUAL_CSV
    assert out["selected_candidate_name"] == "csv"
    assert out["next_recommended_action"] == NEXT_ACTION_CSV


def test_selection_holds_when_no_safe_source():
    out = orchestrate_crypto_d1_spot_data_source_acquisition(
        {
            "candidates": [
                _clean_api(name="trade", endpoint_type="trading_api", requires_trading_endpoint=True),
                _clean_api(name="fut", instrument="futures", is_futures_or_perp=True),
                _clean_api(name="unclear", has_clear_license_metadata=False),
            ]
        }
    )
    assert out["selected_candidate_type"] == SELECTED_TYPE_HOLD
    assert out["selected_candidate_name"] is None
    assert out["next_recommended_action"] == NEXT_ACTION_HOLD


def test_orchestration_outputs_have_all_required_keys():
    out = orchestrate_crypto_d1_spot_data_source_acquisition()
    for key in (
        "selected_candidate_type",
        "selected_candidate_name",
        "reason",
        "required_human_approval_packet",
        "allowed_paths",
        "forbidden_paths",
        "scoped_tests",
        "hard_stop_rules",
        "next_recommended_action",
    ):
        assert key in out


def test_human_run_approved_never_runs():
    out = orchestrate_crypto_d1_spot_data_source_acquisition(
        {"human_run_approved": True}
    )
    assert out["human_run_approved_echo"] is True
    assert out["run_executed"] is False
    assert out["required_human_approval_packet"]["run_executed"] is False
    assert out["required_human_approval_packet"]["run_performed_by_this_block"] is False


# --------------------------------------------------------------------------- #
# Build: happy path is valid and locked
# --------------------------------------------------------------------------- #
def test_default_contract_builds_and_validates():
    contract = _BUILD()
    assert contract["status"] == "AUTOMATED_SOURCE_SELECTION_ONLY"
    assert contract["safe"] is True
    assert contract["this_orchestrator_fetches_data"] is False
    assert contract["this_orchestrator_imports_csv"] is False
    assert contract["this_orchestrator_reads_file_contents"] is False
    assert contract["this_orchestrator_writes_files"] is False
    assert contract["this_orchestrator_runs_acquisition"] is False
    assert contract["requires_human_run"] is True
    assert contract["selected_candidate_type"] == SELECTED_TYPE_CLEAR_LICENSE_API
    assert contract["next_recommended_action"] == NEXT_ACTION_API
    assert contract["real_data_qa_state"] == "BLOCKED"
    assert contract["baseline_backtest_state"] == "BLOCKED"
    assert contract["paper_live_state"] == "LOCKED"
    assert _VALIDATE(contract)["valid"] is True


def test_contract_capability_flags_all_false_and_gates_locked():
    contract = _BUILD()
    assert contract["executes"] is False
    assert contract["fetches_data"] is False
    assert contract["imports_csv"] is False
    assert contract["reads_file_contents"] is False
    assert contract["calls_provider_api"] is False
    assert contract["uses_network"] is False
    assert contract["writes_cache"] is False
    assert contract["writes_report"] is False
    assert contract["runs_qa"] is False
    assert contract["run_executed"] is False
    assert contract["authorizes_nothing"] is True
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["unlocks_real_data_qa"] is False


def test_contract_required_outputs_present():
    contract = _BUILD()
    assert contract["allowed_paths"] == list(ORCH_ALLOWED_PATHS)
    assert contract["forbidden_paths"] == list(ORCH_FORBIDDEN_PATHS)
    assert contract["scoped_tests"] == list(ORCH_SCOPED_TESTS)
    assert contract["hard_stop_rules"] == list(ORCH_HARD_STOP_RULES)
    packet = contract["required_human_approval_packet"]
    assert packet["human_run_approval_required"] is True
    assert packet["run_executed"] is False
    assert packet["target_symbols"] == list(ORCH_REQUIRED_SYMBOLS)
    assert packet["target_timeframes"] == list(ORCH_REQUIRED_TIMEFRAMES)


def test_contract_every_default_candidate_is_evaluated():
    orch = _BUILD()["orchestration"]
    assert len(orch["evaluations"]) == len(DEFAULT_SOURCE_CANDIDATES)
    counts = orch["category_counts"]
    assert counts[CATEGORY_ELIGIBLE_CLEAR_LICENSE_API] >= 1
    assert counts[CATEGORY_ELIGIBLE_MANUAL_CSV] >= 1
    assert counts[CATEGORY_REJECTED_TRADING_API] >= 1
    assert counts[CATEGORY_REJECTED_BROKER_ACCOUNT_API] >= 1
    assert counts[CATEGORY_REJECTED_WRONG_INSTRUMENT] >= 1


def test_human_run_approved_in_build_does_not_run():
    contract = _BUILD({"human_run_approved": True})
    assert contract["human_run_approved_echo"] is True
    assert contract["run_executed"] is False
    assert contract["executes"] is False
    assert contract["fetches_data"] is False
    assert _VALIDATE(contract)["valid"] is True


# --------------------------------------------------------------------------- #
# Unsafe inputs: forbidden flag / off-boundary mission flow
# --------------------------------------------------------------------------- #
def test_forbidden_flag_marks_contract_unsafe():
    contract = _BUILD({"fetch_data_now": True})
    assert contract["safe"] is False
    assert "fetch_data_now" in contract["forbidden_flag_hits"]
    assert contract["executes"] is False
    assert contract["fetches_data"] is False
    assert _VALIDATE(contract)["valid"] is True


def test_run_acquisition_request_marks_contract_unsafe():
    contract = _BUILD({"run_acquisition_now": True})
    assert contract["safe"] is False
    assert "run_acquisition_now" in contract["forbidden_flag_hits"]


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


def test_validate_rejects_fetches_data_true():
    contract = _BUILD()
    contract["this_orchestrator_fetches_data"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["this_fetches_false"] is False


def test_validate_rejects_run_executed_true():
    contract = _BUILD()
    contract["run_executed"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["run_executed_false"] is False


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


def test_validate_rejects_invalid_selected_type():
    contract = _BUILD()
    contract["selected_candidate_type"] = "GO_LIVE"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["selected_type_ok"] is False


def test_validate_rejects_wrong_next_action():
    contract = _BUILD()
    contract["next_recommended_action"] = "GO_LIVE"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["next_action_ok"] is False


def test_validate_rejects_packet_marked_run_executed():
    contract = _BUILD()
    contract["required_human_approval_packet"]["run_executed"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["packet_ok"] is False


def test_validate_rejects_trading_api_misclassified_as_eligible():
    contract = _BUILD()
    for item in contract["orchestration"]["evaluations"]:
        if item["criteria"].get("requires_trading_endpoint") is True:
            item["category"] = CATEGORY_ELIGIBLE_CLEAR_LICENSE_API
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["unsafe_never_selected_ok"] is False


def test_validate_rejects_futures_misclassified_as_eligible():
    contract = _BUILD()
    for item in contract["orchestration"]["evaluations"]:
        if item["criteria"].get("is_futures_or_perp") is True:
            item["category"] = CATEGORY_ELIGIBLE_CLEAR_LICENSE_API
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["unsafe_never_selected_ok"] is False


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
        "# Automated Read-Only Crypto-D1 Spot Data Source Acquisition Orchestrator"
    )
    assert "## Required Human Approval Packet" in text
    assert "## Allowed Paths" in text
    assert "## Forbidden Paths" in text
    assert "## Scoped Tests" in text
    assert "## Hard Stop Rules" in text
    assert "CLEAR_LICENSE_READ_ONLY_SPOT_HISTORICAL_PROVIDER" in text
    assert "data/crypto_d1_spot_cache/" in text


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
    # The orchestrator must own NO filesystem-write capability: it never calls open,
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
