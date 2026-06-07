"""Tests for the Crypto-D1 Databento Missing Crypto Data Acquisition Plan Contract (Block 141).

The contract is a pure, stdlib-only, read-only RESEARCH_ONLY paper module. It
produces -- on paper only -- a deterministic PLAN for a future, human-approved,
READ-ONLY Databento historical market-data acquisition step that would obtain the
missing Crypto-D1 daily bars (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d). It calls no
Databento, opens no network, inspects no credential, reads no .env, exposes no
secret, reads / writes no data file, writes no manifest / gap / runtime /
dashboard output, and unlocks no gate. These tests assert the schema / constants,
the mission-flow truth sync against the live status module, every one of the ten
required plan outputs, the missing-pair derivation, the Databento historical
read-only provider, the no-exchange/broker/trading block, the no-credential /
.env / secret-logging block, the named-not-written manifest / gap paths, the
forbidden-flag / unlock / fetch-now / read-dotenv-now refusals, that a secret
value is never carried, determinism / isolation, validation (incl. tamper
rejections), render, AST purity (stdlib+typing only, no I/O), and the two
additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract import (  # noqa: E501
    DEFAULT_PLAN_INPUT,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
    PLAN_ALLOWED_LATER_CHANGE_PATHS,
    PLAN_ALLOWED_STORAGE_DESTINATIONS,
    PLAN_AUTHORIZATION_FLAGS,
    PLAN_CORE_RULE,
    PLAN_DEFAULT_MISSING_PAIRS,
    PLAN_DEFAULT_STORAGE_DESTINATION,
    PLAN_FORBIDDEN_TRADE_TERMS,
    PLAN_GAP_REPORT_PATH,
    PLAN_GATE_LOCK_FLAGS,
    PLAN_GATE_UNLOCK_REQUEST_FLAGS,
    PLAN_HARD_STOP_CONDITIONS,
    PLAN_LABEL,
    PLAN_MANIFEST_REPORT_PATH,
    PLAN_MODE,
    PLAN_PROPOSED_PROVIDER,
    PLAN_PROVIDER_DETAIL,
    PLAN_REQUIRED_TESTS,
    PLAN_SAFETY_POSTURE,
    PLAN_SCHEMA_VERSION,
    PLAN_STATUS,
    PLAN_STILL_FORBIDDEN_CAPABILITIES,
    assess_databento_missing_crypto_data_acquisition_plan,
    build_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract,
    render_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract_markdown,
    validate_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract.py"
)

_ASSESS = assess_databento_missing_crypto_data_acquisition_plan
_BUILD = build_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract
_VALIDATE = validate_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract
_RENDER = render_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract_markdown


def _safe_input(**overrides):
    """A safe static plan input: at the human boundary, all gates locked, the
    three missing crypto majors at 1d, storing into the approved cache folder."""
    payload = {
        "mode": "RESEARCH_ONLY",
        "read_only": True,
        "executes": False,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "missing_pairs": ["BTCUSD@1d", "ETHUSD@1d", "SOLUSD@1d"],
        "storage_destination": "data/databento_cache/",
        "databento_config_declared": False,
    }
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert PLAN_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_databento_missing_crypto_data_acquisition_plan_contract.v1"
    )
    assert PLAN_LABEL == (
        "Block 141 - Crypto-D1 Databento Missing Crypto Data Acquisition Plan Contract"
    )
    assert PLAN_STATUS == "READ_ONLY_DATABENTO_PLAN_ONLY"
    assert PLAN_MODE == "RESEARCH_ONLY"
    assert "NEVER unlocks Real Data QA" in PLAN_CORE_RULE


def test_default_missing_pairs_are_the_three_crypto_majors():
    assert PLAN_DEFAULT_MISSING_PAIRS == ("BTCUSD@1d", "ETHUSD@1d", "SOLUSD@1d")


def test_proposed_provider_is_databento_historical_read_only():
    assert PLAN_PROPOSED_PROVIDER == "databento_historical_market_data_read_only"
    detail = PLAN_PROVIDER_DETAIL.lower()
    assert "historical" in detail
    assert "read-only" in detail
    assert "no exchange" in detail
    assert "no broker" in detail
    assert "no trading" in detail


def test_storage_destinations_are_approved_local_folders():
    assert PLAN_DEFAULT_STORAGE_DESTINATION == "data/databento_cache/"
    assert PLAN_DEFAULT_STORAGE_DESTINATION in PLAN_ALLOWED_STORAGE_DESTINATIONS
    for dest in PLAN_ALLOWED_STORAGE_DESTINATIONS:
        assert dest.startswith("data/")


def test_manifest_and_gap_report_paths_are_named():
    assert PLAN_MANIFEST_REPORT_PATH == (
        "reports/research_os/data_qa/crypto_d1_databento_manifest.json"
    )
    assert PLAN_GAP_REPORT_PATH == (
        "reports/research_os/data_qa/crypto_d1_databento_gap_report.md"
    )


def test_still_forbidden_capabilities_cover_every_execution_and_secret_surface():
    f = PLAN_STILL_FORBIDDEN_CAPABILITIES
    for cap in (
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
    ):
        assert cap in f, cap


def test_required_tests_name_this_test_and_the_safety_test():
    assert _TEST_ALLOWLIST_LINE in PLAN_REQUIRED_TESTS
    assert "tests/test_sparta_commander_2_safety.py" in PLAN_REQUIRED_TESTS


def test_hard_stop_conditions_present():
    blob = " ".join(PLAN_HARD_STOP_CONDITIONS).lower()
    assert "credential" in blob
    assert ".env" in blob
    assert "broker" in blob
    assert "databento" in blob
    assert "unlock" in blob
    assert len(PLAN_HARD_STOP_CONDITIONS) >= 8


def test_safety_posture_true_facts_all_capability_false():
    posture = PLAN_SAFETY_POSTURE
    posture_true = {"read_only", "research_only", "human_approval_required"}
    for key in posture_true:
        assert posture[key] is True, key
    for key, value in posture.items():
        if key in posture_true:
            continue
        assert value is False, key


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# Ten required plan outputs
# --------------------------------------------------------------------------- #
def test_plan_exposes_all_ten_required_outputs():
    plan = _BUILD()["plan"]
    for key in (
        "missing_pairs",                    # 1
        "missing_symbols",                  # 1
        "missing_timeframes",               # 1
        "proposed_provider",                # 2
        "provider_detail",                  # 2
        "no_exchange_broker_trading_api",   # 3
        "no_credential_exposure",           # 4
        "proposed_storage_destination",     # 5
        "allowed_future_change_paths",      # 6
        "post_fetch_manifest_path",         # 7
        "post_fetch_gap_report_path",       # 7
        "manifest_written_now",             # 7
        "gap_report_written_now",           # 7
        "hard_stop_conditions",             # 8
        "required_tests",                   # 9
        "no_unlock_confirmation",           # 10
    ):
        assert key in plan, key


def test_missing_pairs_and_symbol_timeframe_derivation():
    plan = _BUILD(_safe_input())["plan"]
    assert plan["missing_pairs"] == ["BTCUSD@1d", "ETHUSD@1d", "SOLUSD@1d"]
    assert plan["missing_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert plan["missing_timeframes"] == ["1d"]


def test_read_only_retrieval_descriptions_match_missing_pairs():
    plan = _BUILD(_safe_input())["plan"]
    calls = plan["read_only_retrieval_descriptions"]
    assert len(calls) == len(plan["missing_pairs"])
    for call in calls:
        low = call.lower()
        assert "read-only" in low
        assert "databento" in low
        assert "historical" in low


def test_no_exchange_broker_trading_api_block():
    nebt = _BUILD()["plan"]["no_exchange_broker_trading_api"]
    assert nebt["uses_exchange_trading_api"] is False
    assert nebt["uses_broker_api"] is False
    assert nebt["uses_trading_endpoint"] is False
    assert nebt["uses_account_endpoint"] is False
    assert nebt["historical_market_data_only"] is True


def test_no_credential_exposure_block():
    nce = _BUILD()["plan"]["no_credential_exposure"]
    assert nce["prints_credentials"] is False
    assert nce["inspects_dotenv"] is False
    assert nce["logs_secret"] is False
    assert nce["stores_secret"] is False
    assert nce["databento_secret_exposed"] is False


def test_storage_destination_and_allowed_future_change_paths():
    plan = _BUILD(_safe_input())["plan"]
    assert plan["proposed_storage_destination"] == "data/databento_cache/"
    assert plan["allowed_storage_destinations"] == list(
        PLAN_ALLOWED_STORAGE_DESTINATIONS
    )
    assert plan["allowed_future_change_paths"] == list(
        PLAN_ALLOWED_LATER_CHANGE_PATHS
    )


def test_unapproved_storage_destination_falls_back_to_default():
    plan = _BUILD(_safe_input(storage_destination="/etc/passwd"))["plan"]
    assert plan["proposed_storage_destination"] == PLAN_DEFAULT_STORAGE_DESTINATION


def test_manifest_and_gap_report_named_but_not_written_now():
    plan = _BUILD()["plan"]
    assert plan["post_fetch_manifest_path"] == PLAN_MANIFEST_REPORT_PATH
    assert plan["post_fetch_gap_report_path"] == PLAN_GAP_REPORT_PATH
    assert plan["manifest_written_now"] is False
    assert plan["gap_report_written_now"] is False


def test_required_tests_echoed_in_plan():
    plan = _BUILD()["plan"]
    assert plan["required_tests"] == list(PLAN_REQUIRED_TESTS)


def test_no_unlock_confirmation_affirms_blocked_and_locked():
    nuc = _BUILD()["plan"]["no_unlock_confirmation"]
    assert nuc["unlocks_real_data_qa"] is False
    assert nuc["unlocks_baseline_backtest"] is False
    assert nuc["unlocks_paper_trading"] is False
    assert nuc["unlocks_micro_live"] is False
    assert nuc["real_data_qa_state"] == "BLOCKED"
    assert nuc["baseline_backtest_state"] == "BLOCKED"
    assert nuc["paper_live_state"] == "LOCKED"


# --------------------------------------------------------------------------- #
# Databento presence without exposing a secret
# --------------------------------------------------------------------------- #
def test_databento_presence_is_a_declared_bool_no_secret():
    plan = _BUILD(_safe_input(databento_config_declared=True))["plan"]
    assert plan["databento_config_present_declared"] is True
    assert plan["no_credential_exposure"]["databento_secret_exposed"] is False
    assert "static operator assertion" in plan["databento_config_note"].lower()


def test_default_input_declares_no_databento_config():
    plan = _BUILD()["plan"]
    assert plan["databento_config_present_declared"] is False


def test_a_secret_value_in_input_is_never_carried_into_contract():
    payload = _safe_input(databento_api_key="SHOULD-NEVER-APPEAR")
    contract = _BUILD(payload)
    assert "SHOULD-NEVER-APPEAR" not in _RENDER(contract)
    assert _VALIDATE(contract)["no_secret_value_fields"] is True


# --------------------------------------------------------------------------- #
# Safety posture in the built contract
# --------------------------------------------------------------------------- #
def test_assessment_reports_safe_at_boundary():
    result = _ASSESS(_safe_input())
    assert result["safe"] is True
    assert result["mission_flow_aligned"] is True
    assert result["forbidden_flag_hits"] == []
    assert result["fetches_data"] is False
    assert result["calls_databento"] is False
    assert result["reads_dotenv"] is False
    assert result["authorizes_nothing"] is True


def test_built_contract_keeps_every_gate_blocked_and_flag_false():
    contract = _BUILD(_safe_input())
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["real_data_qa_state"] == "BLOCKED"
    assert contract["baseline_backtest_state"] == "BLOCKED"
    assert contract["paper_live_state"] == "LOCKED"
    for flag in (
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
        "authorizes_broker_exchange",
        "authorizes_order_placement",
        "authorizes_strategy_promotion",
        "unlocks_real_data_qa",
        "unlocks_baseline_backtest",
        "unlocks_paper_trading",
        "unlocks_micro_live",
    ):
        assert contract[flag] is False, flag
    assert contract["authorizes_nothing"] is True
    assert contract["read_only"] is True
    assert contract["human_approval_required"] is True
    assert contract["requires_separate_future_human_approved_step"] is True


# --------------------------------------------------------------------------- #
# Unsafe-flag refusals
# --------------------------------------------------------------------------- #
def test_authorization_flag_marks_unsafe():
    for flag in PLAN_AUTHORIZATION_FLAGS:
        result = _ASSESS(_safe_input(**{flag: True}))
        assert result["safe"] is False, flag
        assert flag in result["forbidden_flag_hits"], flag


def test_gate_unlock_or_fetch_now_request_marks_unsafe():
    for flag in PLAN_GATE_UNLOCK_REQUEST_FLAGS:
        result = _ASSESS(_safe_input(**{flag: True}))
        assert result["safe"] is False, flag
        assert flag in result["forbidden_flag_hits"], flag


def test_read_dotenv_now_and_call_databento_now_are_refused():
    for flag in ("read_dotenv_now", "call_databento_now", "check_live_credentials_now"):
        assert flag in PLAN_GATE_UNLOCK_REQUEST_FLAGS, flag
        result = _ASSESS(_safe_input(**{flag: True}))
        assert result["safe"] is False, flag


def test_unlocking_a_locked_gate_marks_unsafe():
    for flag in PLAN_GATE_LOCK_FLAGS:
        result = _ASSESS(_safe_input(**{flag: False}))
        assert result["safe"] is False, flag
        assert ("unlocked:" + flag) in result["forbidden_flag_hits"], flag


def test_off_boundary_mission_flow_marks_unsafe():
    result = _ASSESS(_safe_input(mission_flow_current_stage="SOMETHING_ELSE"))
    assert result["mission_flow_aligned"] is False
    assert result["safe"] is False


def test_unsafe_contract_still_keeps_gates_locked_and_flags_false():
    contract = _BUILD(_safe_input(authorizes_trading=True))
    assert contract["safe"] is False
    assert contract["unlocks_real_data_qa"] is False
    assert contract["real_data_qa_blocked"] is True
    assert contract["authorizes_trading"] is False  # contract flag stays False


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_assessment_is_deterministic():
    payload = _safe_input()
    assert _ASSESS(payload) == _ASSESS(payload)


def test_build_does_not_mutate_caller_payload():
    import copy

    payload = _safe_input()
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


def test_default_input_is_not_shared_between_builds():
    d1 = _BUILD()
    d2 = _BUILD()
    d1["plan"]["missing_pairs"].append("TAMPERED@1d")
    assert "TAMPERED@1d" not in d2["plan"]["missing_pairs"]
    assert DEFAULT_PLAN_INPUT["databento_config_declared"] is False


# --------------------------------------------------------------------------- #
# Validation / render
# --------------------------------------------------------------------------- #
def test_default_contract_validates():
    verdict = _VALIDATE(_BUILD())
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == []
    assert verdict["flags_false"] is True
    assert verdict["gates_locked"] is True
    assert verdict["authorizes_nothing"] is True
    assert verdict["mission_flow_refs_ok"] is True
    assert verdict["posture_ok"] is True
    assert verdict["states_blocked_locked"] is True
    assert verdict["plan_keys_ok"] is True
    assert verdict["provider_ok"] is True
    assert verdict["no_exchange_broker_ok"] is True
    assert verdict["no_credential_exposure_ok"] is True
    assert verdict["not_written_now"] is True
    assert verdict["storage_ok"] is True
    assert verdict["no_unlock_ok"] is True
    assert verdict["no_secret_value_fields"] is True
    assert verdict["forbidden_list_intact"] is True
    assert verdict["no_trade_language"] is True


def test_safe_and_unsafe_inputs_both_validate_structurally():
    for payload in (_safe_input(), _safe_input(authorizes_trading=True), None):
        verdict = _VALIDATE(_BUILD(payload))
        assert verdict["valid"] is True, payload


def test_validate_rejects_tampered_executes():
    contract = _BUILD()
    contract["executes"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["executes_false"] is False


def test_validate_rejects_unlocked_real_data_qa():
    contract = _BUILD()
    contract["unlocks_real_data_qa"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_unlocked_gate():
    contract = _BUILD()
    contract["real_data_qa_blocked"] = False
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_validate_rejects_exposed_secret():
    contract = _BUILD()
    contract["plan"]["databento_api_key"] = "leaked-value"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["no_secret_value_fields"] is False


def test_validate_rejects_written_manifest():
    contract = _BUILD()
    contract["plan"]["manifest_written_now"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["not_written_now"] is False


def test_validate_rejects_tampered_provider():
    contract = _BUILD()
    contract["plan"]["proposed_provider"] = "binance_exchange_api"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["provider_ok"] is False


def test_validate_rejects_forbidden_list_tampering():
    contract = _BUILD()
    contract["still_forbidden_capabilities"] = ["only_one"]
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["forbidden_list_intact"] is False


def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith(
        "# Crypto-D1 Databento Missing Crypto Data Acquisition Plan"
    )
    assert "## 1. Missing Pairs" in text
    assert "## 2. Proposed Read-Only Provider" in text
    assert "## 3. No Exchange / Broker / Trading API" in text
    assert "## 4. No Credential Exposure" in text
    assert "## 7. Post-Fetch Manifest / Gap Report" in text
    assert "## 8. Hard-Stop Conditions" in text
    assert "## 10. No-Unlock Confirmation" in text
    assert "## Still Forbidden (always)" in text


def test_authored_narrative_has_no_execution_verbs():
    contract = _BUILD(_safe_input())
    blob = " ".join(
        str(contract.get(k, ""))
        for k in ("operator_next_step", "plan_summary", "core_rule")
    )
    blob += " " + " ".join(
        str(s) for s in contract.get("human_operator_required_next_steps", [])
    )
    tokens = set(
        "".join(
            c if (c.isalnum() or c == "_") else " " for c in blob.lower()
        ).split()
    )
    for term in PLAN_FORBIDDEN_TRADE_TERMS:
        assert term not in tokens, term


# --------------------------------------------------------------------------- #
# AST purity: stdlib-only, no I/O, no forbidden imports
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORTS = {"__future__", "typing"}
_FORBIDDEN_CALL_NAMES = {"open", "__import__", "eval", "exec", "compile", "input"}
_FORBIDDEN_MODULE_TOKENS = {
    "os",
    "sys",
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


def test_module_imports_are_stdlib_typing_only():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in _ALLOWED_IMPORTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORTS, node.module


def test_module_has_no_forbidden_calls():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in _FORBIDDEN_CALL_NAMES, node.func.id


def test_module_has_no_forbidden_module_tokens():
    imported_roots = set()
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported_roots.add((node.module or "").split(".")[0])
    assert not (imported_roots & _FORBIDDEN_MODULE_TOKENS)


def test_building_writes_no_files(tmp_path):
    before = set(tmp_path.iterdir())
    _BUILD()
    _BUILD(_safe_input())
    after = set(tmp_path.iterdir())
    assert before == after


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
