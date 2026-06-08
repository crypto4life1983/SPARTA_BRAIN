"""Tests for the Crypto-D1 Read-Only Market Data Provider Selection Contract (Block 145).

The contract ranks candidate READ-ONLY historical market-data providers for the
three missing Crypto-D1 daily spot pairs (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d) after
Block 144's approved one-time Databento fetch could not run -- the current
Databento account exposes no crypto spot dataset for those pairs. It is a PURE,
stdlib-only reasoning layer: it fetches nothing, calls no API, opens no network,
reads no credential / .env, chooses no provider, and unlocks no gate.

These tests assert: schema / constants; mission-flow truth sync against the live
status module; that the current Databento account is recorded unavailable for the
approved crypto spot pairs; the eight acceptable-provider criteria; the explicit
wrong-instrument rejection rules (CME crypto futures must not substitute spot);
the five ranking categories; deterministic classification covering every category
(incl. a CME-futures candidate landing in REJECTED_WRONG_INSTRUMENT); the single
next recommended action HOLD_FOR_PROVIDER_CHOICE; that the contract chooses no
provider; that every capability flag is False and every gate stays locked; that a
secret value is never carried; determinism / caller-payload isolation; validation
tamper rejections; render; AST purity (only __future__ / typing / sparta_commander
roots, no os / json / network / credential modules, no os.environ access, NO open
/ write_* call); and the two additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_read_only_market_data_provider_selection_contract import (  # noqa: E501
    CATEGORY_APPROVED_CANDIDATE,
    CATEGORY_NEEDS_PROVIDER_REVIEW,
    CATEGORY_REJECTED_INSUFFICIENT_COVERAGE,
    CATEGORY_REJECTED_TRADING_ENDPOINT_RISK,
    CATEGORY_REJECTED_WRONG_INSTRUMENT,
    DATABENTO_CURRENT_ACCOUNT_RECORD,
    DEFAULT_PROVIDER_CANDIDATES,
    NEXT_RECOMMENDED_ACTION,
    SELECTION_APPROVED_SYMBOLS,
    SELECTION_APPROVED_TIMEFRAMES,
    SELECTION_CATEGORIES,
    SELECTION_CORE_RULE,
    SELECTION_LABEL,
    SELECTION_MODE,
    SELECTION_PROVIDER_CRITERIA,
    SELECTION_SCHEMA_VERSION,
    SELECTION_STATUS,
    SELECTION_WRONG_INSTRUMENT_REJECTION_RULES,
    build_crypto_d1_read_only_market_data_provider_selection_contract,
    classify_provider_candidate,
    render_crypto_d1_read_only_market_data_provider_selection_contract_markdown,
    validate_crypto_d1_read_only_market_data_provider_selection_contract,
)
from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_read_only_market_data_provider_selection_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_read_only_market_data_provider_selection_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_read_only_market_data_provider_selection_contract.py"
)

_BUILD = build_crypto_d1_read_only_market_data_provider_selection_contract
_VALIDATE = validate_crypto_d1_read_only_market_data_provider_selection_contract
_RENDER = render_crypto_d1_read_only_market_data_provider_selection_contract_markdown


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert SELECTION_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_read_only_market_data_provider_selection_contract.v1"
    )
    assert SELECTION_LABEL == (
        "Block 145 - Crypto-D1 Read-Only Market Data Provider Selection Contract"
    )
    assert SELECTION_STATUS == "READ_ONLY_PROVIDER_SELECTION_CONTRACT"
    assert SELECTION_MODE == "RESEARCH_ONLY"
    assert "authorizes" in SELECTION_CORE_RULE.lower()
    assert "blocked" in SELECTION_CORE_RULE.lower()


def test_approved_scope_constants():
    assert SELECTION_APPROVED_SYMBOLS == ("BTCUSD", "ETHUSD", "SOLUSD")
    assert SELECTION_APPROVED_TIMEFRAMES == ("1d",)


def test_ranking_categories_are_the_five_required():
    assert SELECTION_CATEGORIES == (
        CATEGORY_APPROVED_CANDIDATE,
        CATEGORY_NEEDS_PROVIDER_REVIEW,
        CATEGORY_REJECTED_WRONG_INSTRUMENT,
        CATEGORY_REJECTED_TRADING_ENDPOINT_RISK,
        CATEGORY_REJECTED_INSUFFICIENT_COVERAGE,
    )
    assert CATEGORY_APPROVED_CANDIDATE == "APPROVED_CANDIDATE"
    assert CATEGORY_NEEDS_PROVIDER_REVIEW == "NEEDS_PROVIDER_REVIEW"
    assert CATEGORY_REJECTED_WRONG_INSTRUMENT == "REJECTED_WRONG_INSTRUMENT"
    assert CATEGORY_REJECTED_TRADING_ENDPOINT_RISK == "REJECTED_TRADING_ENDPOINT_RISK"
    assert CATEGORY_REJECTED_INSUFFICIENT_COVERAGE == "REJECTED_INSUFFICIENT_COVERAGE"


def test_next_recommended_action_is_hold_for_provider_choice():
    assert NEXT_RECOMMENDED_ACTION == "HOLD_FOR_PROVIDER_CHOICE"


def test_databento_current_account_recorded_unavailable():
    assert DATABENTO_CURRENT_ACCOUNT_RECORD["available_for_approved_crypto_spot"] is False
    assert "no crypto spot dataset" in DATABENTO_CURRENT_ACCOUNT_RECORD["finding"].lower()


def test_provider_criteria_cover_required_dimensions():
    blob = " ".join(SELECTION_PROVIDER_CRITERIA).lower()
    assert len(SELECTION_PROVIDER_CRITERIA) >= 8
    assert "read-only historical" in blob
    assert "btcusd" in blob and "ethusd" in blob and "solusd" in blob
    assert "daily" in blob
    assert "no trading endpoint" in blob
    assert "no account / portfolio endpoint" in blob
    assert "no order endpoint" in blob
    assert "no secret exposure" in blob
    assert "license" in blob


def test_wrong_instrument_rejection_rules_name_cme_futures():
    blob = " ".join(SELECTION_WRONG_INSTRUMENT_REJECTION_RULES).lower()
    assert "cme crypto futures" in blob
    assert "spot" in blob


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# Classification: deterministic, one bucket per candidate
# --------------------------------------------------------------------------- #
def test_cme_crypto_futures_substitute_is_rejected_wrong_instrument():
    descriptor = {
        "name": "cme_crypto_futures",
        "instrument": "CME crypto futures",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "has_license_metadata": True,
        "is_crypto_futures_substitute": True,
    }
    out = classify_provider_candidate(descriptor)
    assert out["category"] == CATEGORY_REJECTED_WRONG_INSTRUMENT
    assert out["criteria"]["wrong_instrument_substitute"] is True


def test_trading_endpoint_candidate_is_rejected_trading_endpoint_risk():
    descriptor = {
        "name": "exchange_trading_api",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "requires_trading_endpoint": True,
        "requires_account_endpoint": True,
        "has_license_metadata": True,
    }
    out = classify_provider_candidate(descriptor)
    assert out["category"] == CATEGORY_REJECTED_TRADING_ENDPOINT_RISK


def test_insufficient_coverage_candidate_is_rejected_insufficient_coverage():
    descriptor = {
        "name": "partial_coverage_provider",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD"],
        "daily_timeframe": True,
        "has_license_metadata": True,
    }
    out = classify_provider_candidate(descriptor)
    assert out["category"] == CATEGORY_REJECTED_INSUFFICIENT_COVERAGE


def test_unavailable_candidate_is_rejected_insufficient_coverage():
    descriptor = {
        "name": "databento_current_account",
        "read_only_historical": True,
        "covers_symbols": [],
        "daily_timeframe": True,
        "has_license_metadata": True,
        "available_on_current_account": False,
    }
    out = classify_provider_candidate(descriptor)
    assert out["category"] == CATEGORY_REJECTED_INSUFFICIENT_COVERAGE


def test_clean_provider_without_license_needs_review():
    descriptor = {
        "name": "clean_but_unclear_license",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "has_license_metadata": False,
    }
    out = classify_provider_candidate(descriptor)
    assert out["category"] == CATEGORY_NEEDS_PROVIDER_REVIEW


def test_clean_provider_with_license_is_approved_candidate():
    descriptor = {
        "name": "clean_read_only_spot_provider",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "has_license_metadata": True,
    }
    out = classify_provider_candidate(descriptor)
    assert out["category"] == CATEGORY_APPROVED_CANDIDATE


def test_default_candidates_cover_every_category():
    cats = {
        classify_provider_candidate(c)["category"] for c in DEFAULT_PROVIDER_CANDIDATES
    }
    assert cats == set(SELECTION_CATEGORIES)


def test_classification_is_deterministic():
    for c in DEFAULT_PROVIDER_CANDIDATES:
        assert classify_provider_candidate(c) == classify_provider_candidate(c)


# --------------------------------------------------------------------------- #
# Build: happy path is valid and locked
# --------------------------------------------------------------------------- #
def test_default_contract_builds_and_validates():
    contract = _BUILD()
    assert contract["status"] == "READ_ONLY_PROVIDER_SELECTION_CONTRACT"
    assert contract["safe"] is True
    assert contract["this_contract_chooses_provider"] is False
    assert contract["requires_human_provider_choice"] is True
    assert contract["next_recommended_action"] == "HOLD_FOR_PROVIDER_CHOICE"
    assert contract["real_data_qa_state"] == "BLOCKED"
    assert contract["baseline_backtest_state"] == "BLOCKED"
    assert contract["paper_live_state"] == "LOCKED"
    assert _VALIDATE(contract)["valid"] is True


def test_contract_capability_flags_all_false_and_gates_locked():
    contract = _BUILD()
    assert contract["executes"] is False
    assert contract["performs_data_fetch"] is False
    assert contract["calls_provider_api"] is False
    assert contract["uses_network"] is False
    assert contract["chooses_provider"] is False
    assert contract["connects_provider"] is False
    assert contract["authorizes_nothing"] is True
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["unlocks_real_data_qa"] is False


def test_contract_spec_carries_required_sections():
    spec = _BUILD()["selection_contract"]
    assert spec["databento_current_account_record"]["available_for_approved_crypto_spot"] is False
    assert spec["wrong_instrument_rejection_rules"]
    assert spec["provider_criteria"]
    assert spec["ranking_categories"] == list(SELECTION_CATEGORIES)
    assert spec["classifications"]
    assert spec["next_recommended_action"] == "HOLD_FOR_PROVIDER_CHOICE"
    nuc = spec["no_unlock_confirmation"]
    assert nuc["unlocks_real_data_qa"] is False
    assert nuc["real_data_qa_state"] == "BLOCKED"


def test_contract_every_default_candidate_is_classified():
    spec = _BUILD()["selection_contract"]
    assert len(spec["classifications"]) == len(DEFAULT_PROVIDER_CANDIDATES)
    assert spec["category_counts"][CATEGORY_REJECTED_WRONG_INSTRUMENT] >= 1
    assert spec["category_counts"][CATEGORY_APPROVED_CANDIDATE] >= 1


# --------------------------------------------------------------------------- #
# Unsafe inputs: forbidden flag / off-boundary mission flow
# --------------------------------------------------------------------------- #
def test_forbidden_flag_marks_contract_unsafe():
    contract = _BUILD({"choose_provider_now": True})
    assert contract["safe"] is False
    assert "choose_provider_now" in contract["forbidden_flag_hits"]
    # but every real capability flag is still False and gates still locked
    assert contract["executes"] is False
    assert contract["chooses_provider"] is False
    assert _VALIDATE(contract)["valid"] is True


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
    # exposes_secret=False is a flag, not a secret VALUE -> must not trip detection
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


def test_validate_rejects_chooses_provider_true():
    contract = _BUILD()
    contract["this_contract_chooses_provider"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["this_chooses_false"] is False


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


def test_validate_rejects_databento_marked_available():
    contract = _BUILD()
    contract["selection_contract"]["databento_current_account_record"][
        "available_for_approved_crypto_spot"
    ] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["databento_recorded_unavailable"] is False


def test_validate_rejects_futures_misclassified_as_approved():
    contract = _BUILD()
    for item in contract["selection_contract"]["classifications"]:
        if item["criteria"].get("wrong_instrument_substitute") is True:
            item["category"] = CATEGORY_APPROVED_CANDIDATE
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["futures_rejected_ok"] is False


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
        "# Crypto-D1 Read-Only Market Data Provider Selection Contract"
    )
    assert "## 1. Databento Current-Account Record" in text
    assert "## 2. Wrong-Instrument Rejection Rules" in text
    assert "## 3. Provider Criteria" in text
    assert "## 4. Ranking Categories" in text
    assert "## 5. Next Recommended Action" in text
    assert "HOLD_FOR_PROVIDER_CHOICE" in text


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
