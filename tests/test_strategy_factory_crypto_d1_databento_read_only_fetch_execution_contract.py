"""Tests for the Crypto-D1 Databento Read-Only Fetch Execution Contract (Block 142).

The contract is a pure, stdlib-only, read-only RESEARCH_ONLY spec / boundary
layer. It defines and guards the execution boundary for a future, human-approved,
READ-ONLY Databento historical market-data fetch of the three missing Crypto-D1
daily pairs. THIS contract performs no fetch: it calls no Databento, opens no
network, inspects no credential, reads no .env, exposes no secret, reads / writes
no data file, writes no manifest / gap / runtime / dashboard output, and unlocks
no gate. These tests assert the schema / constants, mission-flow truth sync, all
ten required contract outputs, the fetch-permission gating model (disabled by
default; permitted for a future runner only under explicit human-run approval +
approved scope), out-of-scope and forbidden-flag refusals, that fetch permission
never unlocks a gate, the no-credential / .env / secret-logging rules, that a
secret value is never carried, determinism / isolation, validation (incl. tamper
rejections), render, AST purity (stdlib+typing only, no I/O), and the two additive
commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    DEFAULT_FETCH_INPUT,
    FETCH_APPROVED_DESTINATION,
    FETCH_APPROVED_PAIRS,
    FETCH_APPROVED_PROVIDER,
    FETCH_APPROVED_REPORT_DIR,
    FETCH_APPROVED_SYMBOLS,
    FETCH_APPROVED_TIMEFRAMES,
    FETCH_AUTHORIZATION_FLAGS,
    FETCH_CORE_RULE,
    FETCH_FORBIDDEN_TRADE_TERMS,
    FETCH_GATE_LOCK_FLAGS,
    FETCH_GATE_UNLOCK_REQUEST_FLAGS,
    FETCH_HARD_STOP_CONDITIONS,
    FETCH_HUMAN_RUN_APPROVAL_FLAG,
    FETCH_LABEL,
    FETCH_MODE,
    FETCH_PROVIDER_DETAIL,
    FETCH_SAFETY_POSTURE,
    FETCH_SCHEMA_VERSION,
    FETCH_STATUS,
    FETCH_STILL_FORBIDDEN_CAPABILITIES,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
    assess_databento_read_only_fetch_execution,
    build_crypto_d1_databento_read_only_fetch_execution_contract,
    render_crypto_d1_databento_read_only_fetch_execution_contract_markdown,
    validate_crypto_d1_databento_read_only_fetch_execution_contract,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract.py"
)

_ASSESS = assess_databento_read_only_fetch_execution
_BUILD = build_crypto_d1_databento_read_only_fetch_execution_contract
_VALIDATE = validate_crypto_d1_databento_read_only_fetch_execution_contract
_RENDER = render_crypto_d1_databento_read_only_fetch_execution_contract_markdown


def _safe_input(**overrides):
    """A safe static fetch input: at the human boundary, all gates locked, the
    three approved crypto majors at 1d into the approved destination. By default
    NO human-run approval, so fetch is disabled for a future runner."""
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
        "requested_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "requested_timeframes": ["1d"],
        "requested_provider": FETCH_APPROVED_PROVIDER,
        "requested_destination": FETCH_APPROVED_DESTINATION,
        "requested_report_dir": FETCH_APPROVED_REPORT_DIR,
        "databento_config_declared": False,
    }
    payload.update(overrides)
    return payload


def _approved_input(**overrides):
    payload = _safe_input(**{FETCH_HUMAN_RUN_APPROVAL_FLAG: True})
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert FETCH_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract.v1"
    )
    assert FETCH_LABEL == (
        "Block 142 - Crypto-D1 Databento Read-Only Fetch Execution Contract"
    )
    assert FETCH_STATUS == "READ_ONLY_DATABENTO_FETCH_CONTRACT"
    assert FETCH_MODE == "RESEARCH_ONLY"
    assert "NEVER unlocks Real Data QA" in FETCH_CORE_RULE


def test_approved_scope_constants():
    assert FETCH_APPROVED_PAIRS == ("BTCUSD@1d", "ETHUSD@1d", "SOLUSD@1d")
    assert FETCH_APPROVED_SYMBOLS == ("BTCUSD", "ETHUSD", "SOLUSD")
    assert FETCH_APPROVED_TIMEFRAMES == ("1d",)
    assert FETCH_APPROVED_DESTINATION == "data/databento_cache/crypto_d1/"
    assert FETCH_APPROVED_REPORT_DIR == "reports/research_os/data_qa/"


def test_provider_is_databento_historical_read_only():
    assert FETCH_APPROVED_PROVIDER == "databento_historical_market_data_read_only"
    detail = FETCH_PROVIDER_DETAIL.lower()
    assert "historical" in detail
    assert "read-only" in detail
    assert "no exchange" in detail
    assert "no broker" in detail
    assert "no trading" in detail
    assert "no account" in detail


def test_human_run_approval_flag_name():
    assert FETCH_HUMAN_RUN_APPROVAL_FLAG == "human_run_approved"


def test_still_forbidden_capabilities_cover_every_surface():
    f = FETCH_STILL_FORBIDDEN_CAPABILITIES
    for cap in (
        "exchange_trading_api",
        "broker_api",
        "account_access",
        "portfolio_access",
        "order_placement",
        "paper_trading",
        "live_trading",
        "telegram_trade_command",
        "tradingview_execution_webhook",
        "strategy_promotion",
        "baseline_backtest_qa_execution",
        "runtime_dashboard_writes",
        "secret_printing",
        "credential_logging",
        "dotenv_content_printing",
        "writing_outside_approved_paths",
        "gate_unlock",
    ):
        assert cap in f, cap


def test_hard_stop_conditions_present():
    blob = " ".join(FETCH_HARD_STOP_CONDITIONS).lower()
    assert "human-run approval is absent" in blob
    assert "credential" in blob
    assert ".env" in blob
    assert "broker" in blob
    assert "unlock" in blob
    assert len(FETCH_HARD_STOP_CONDITIONS) >= 8


def test_safety_posture_true_facts_all_capability_false():
    posture = FETCH_SAFETY_POSTURE
    posture_true = {
        "read_only",
        "research_only",
        "human_approval_required",
        "fetch_disabled_by_default",
    }
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
# Ten required contract outputs
# --------------------------------------------------------------------------- #
def test_spec_exposes_all_ten_required_outputs():
    spec = _BUILD()["fetch_contract"]
    for key in (
        "approved_pairs",              # 1
        "approved_symbols",            # 1
        "approved_timeframes",         # 1
        "approved_provider",           # 2
        "approved_destination",        # 3
        "approved_report_dir",         # 4
        "credential_safety_rules",     # 5
        "fetch_permission_model",      # 6
        "pre_fetch_checks",            # 7
        "post_fetch_checks",           # 8
        "hard_stop_conditions",        # 9
        "no_unlock_confirmation",      # 10
    ):
        assert key in spec, key


def test_approved_scope_echoed_in_spec():
    spec = _BUILD()["fetch_contract"]
    assert spec["approved_pairs"] == ["BTCUSD@1d", "ETHUSD@1d", "SOLUSD@1d"]
    assert spec["approved_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert spec["approved_timeframes"] == ["1d"]
    assert spec["approved_destination"] == "data/databento_cache/crypto_d1/"
    assert spec["approved_report_dir"] == "reports/research_os/data_qa/"


def test_credential_safety_rules_forbid_secret_exposure():
    spec = _BUILD()["fetch_contract"]
    blob = " ".join(spec["credential_safety_rules"]).lower()
    assert "presence" in blob
    assert "never print" in blob
    assert "never log a secret" in blob
    assert ".env" in blob
    assert spec["databento_secret_exposed"] is False


def test_pre_and_post_fetch_checks_present():
    spec = _BUILD()["fetch_contract"]
    assert len(spec["pre_fetch_checks"]) >= 6
    assert len(spec["post_fetch_checks"]) >= 6
    post_blob = " ".join(spec["post_fetch_checks"]).lower()
    assert "data/databento_cache/crypto_d1/" in post_blob
    assert "manifest" in post_blob


def test_no_unlock_confirmation_affirms_blocked_and_locked():
    nuc = _BUILD()["fetch_contract"]["no_unlock_confirmation"]
    assert nuc["unlocks_real_data_qa"] is False
    assert nuc["unlocks_baseline_backtest"] is False
    assert nuc["unlocks_paper_trading"] is False
    assert nuc["unlocks_micro_live"] is False
    assert nuc["real_data_qa_state"] == "BLOCKED"
    assert nuc["baseline_backtest_state"] == "BLOCKED"
    assert nuc["paper_live_state"] == "LOCKED"


# --------------------------------------------------------------------------- #
# Fetch permission model
# --------------------------------------------------------------------------- #
def test_fetch_disabled_by_default_no_human_approval():
    contract = _BUILD()
    assert contract["fetch_permitted_for_future_runner"] is False
    fpm = contract["fetch_contract"]["fetch_permission_model"]
    assert fpm["enabled_by_default"] is False
    assert fpm["requires_explicit_human_run_approval"] is True
    assert fpm["human_run_approved"] is False
    assert fpm["fetch_permitted_for_future_runner"] is False
    assert fpm["this_contract_performs_fetch"] is False
    assert "disabled by default" in fpm["fetch_permitted_reason"].lower()


def test_fetch_permitted_for_future_runner_only_with_human_approval():
    contract = _BUILD(_approved_input())
    assert contract["fetch_permitted_for_future_runner"] is True
    fpm = contract["fetch_contract"]["fetch_permission_model"]
    assert fpm["human_run_approved"] is True
    assert fpm["scope_approved"] is True
    assert fpm["fetch_permitted_for_future_runner"] is True
    # even when permitted, this contract performs no fetch.
    assert fpm["this_contract_performs_fetch"] is False
    assert contract["performs_fetch"] is False
    assert contract["executes"] is False


def test_fetch_permission_never_unlocks_a_gate():
    contract = _BUILD(_approved_input())
    assert contract["fetch_permitted_for_future_runner"] is True
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["unlocks_real_data_qa"] is False
    assert contract["unlocks_baseline_backtest"] is False
    assert contract["real_data_qa_state"] == "BLOCKED"
    assert contract["paper_live_state"] == "LOCKED"


def test_out_of_scope_symbol_refuses_fetch_even_with_approval():
    contract = _BUILD(_approved_input(requested_symbols=["DOGEUSD"]))
    assert contract["fetch_permitted_for_future_runner"] is False
    fpm = contract["fetch_contract"]["fetch_permission_model"]
    assert fpm["scope_approved"] is False
    assert "scope" in fpm["fetch_permitted_reason"].lower()


def test_out_of_scope_timeframe_refuses_fetch():
    contract = _BUILD(_approved_input(requested_timeframes=["1h"]))
    assert contract["fetch_permitted_for_future_runner"] is False


def test_out_of_scope_destination_refuses_fetch():
    contract = _BUILD(_approved_input(requested_destination="data/elsewhere/"))
    assert contract["fetch_permitted_for_future_runner"] is False


def test_non_databento_provider_refuses_fetch():
    contract = _BUILD(_approved_input(requested_provider="binance_exchange_api"))
    assert contract["fetch_permitted_for_future_runner"] is False


# --------------------------------------------------------------------------- #
# Databento presence without exposing a secret
# --------------------------------------------------------------------------- #
def test_databento_presence_is_a_declared_bool_no_secret():
    spec = _BUILD(_safe_input(databento_config_declared=True))["fetch_contract"]
    assert spec["databento_config_present_declared"] is True
    assert spec["databento_secret_exposed"] is False
    assert "static operator assertion" in spec["databento_config_note"].lower()


def test_a_secret_value_in_input_is_never_carried_into_contract():
    payload = _approved_input(databento_api_key="SHOULD-NEVER-APPEAR")
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
    for payload in (_safe_input(), _approved_input()):
        contract = _BUILD(payload)
        assert contract["real_data_qa_blocked"] is True
        assert contract["baseline_backtest_blocked"] is True
        assert contract["paper_trading_gate_locked"] is True
        assert contract["micro_live_gate_locked"] is True
        assert contract["real_data_qa_state"] == "BLOCKED"
        assert contract["baseline_backtest_state"] == "BLOCKED"
        assert contract["paper_live_state"] == "LOCKED"
        for flag in (
            "executes",
            "performs_fetch",
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
            "authorizes_qa_baseline",
            "unlocks_real_data_qa",
            "unlocks_baseline_backtest",
            "unlocks_paper_trading",
            "unlocks_micro_live",
        ):
            assert contract[flag] is False, flag
        assert contract["authorizes_nothing"] is True
        assert contract["read_only"] is True
        assert contract["human_approval_required"] is True
        assert contract["requires_explicit_human_run_approval"] is True


# --------------------------------------------------------------------------- #
# Unsafe-flag refusals
# --------------------------------------------------------------------------- #
def test_authorization_flag_marks_unsafe():
    for flag in FETCH_AUTHORIZATION_FLAGS:
        result = _ASSESS(_approved_input(**{flag: True}))
        assert result["safe"] is False, flag
        assert flag in result["forbidden_flag_hits"], flag
        assert result["fetch_permitted_for_future_runner"] is False, flag


def test_gate_unlock_or_run_now_request_marks_unsafe():
    for flag in FETCH_GATE_UNLOCK_REQUEST_FLAGS:
        result = _ASSESS(_approved_input(**{flag: True}))
        assert result["safe"] is False, flag
        assert flag in result["forbidden_flag_hits"], flag
        assert result["fetch_permitted_for_future_runner"] is False, flag


def test_read_dotenv_now_and_check_credentials_now_are_refused():
    for flag in ("read_dotenv_now", "check_live_credentials_now"):
        assert flag in FETCH_GATE_UNLOCK_REQUEST_FLAGS, flag
        result = _ASSESS(_approved_input(**{flag: True}))
        assert result["safe"] is False, flag


def test_unlocking_a_locked_gate_marks_unsafe():
    for flag in FETCH_GATE_LOCK_FLAGS:
        result = _ASSESS(_approved_input(**{flag: False}))
        assert result["safe"] is False, flag
        assert ("unlocked:" + flag) in result["forbidden_flag_hits"], flag
        assert result["fetch_permitted_for_future_runner"] is False, flag


def test_off_boundary_mission_flow_marks_unsafe():
    result = _ASSESS(_approved_input(mission_flow_current_stage="SOMETHING_ELSE"))
    assert result["mission_flow_aligned"] is False
    assert result["safe"] is False
    assert result["fetch_permitted_for_future_runner"] is False


def test_unsafe_contract_still_keeps_gates_locked_and_flags_false():
    contract = _BUILD(_approved_input(authorizes_trading=True))
    assert contract["safe"] is False
    assert contract["fetch_permitted_for_future_runner"] is False
    assert contract["unlocks_real_data_qa"] is False
    assert contract["real_data_qa_blocked"] is True
    assert contract["authorizes_trading"] is False  # contract flag stays False


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_assessment_is_deterministic():
    payload = _approved_input()
    assert _ASSESS(payload) == _ASSESS(payload)


def test_build_does_not_mutate_caller_payload():
    import copy

    payload = _approved_input()
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


def test_default_input_is_not_shared_between_builds():
    d1 = _BUILD()
    d2 = _BUILD()
    d1["fetch_contract"]["approved_pairs"].append("TAMPERED@1d")
    assert "TAMPERED@1d" not in d2["fetch_contract"]["approved_pairs"]
    assert "human_run_approved" not in DEFAULT_FETCH_INPUT


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
    assert verdict["spec_keys_ok"] is True
    assert verdict["provider_ok"] is True
    assert verdict["pairs_ok"] is True
    assert verdict["destination_ok"] is True
    assert verdict["report_dir_ok"] is True
    assert verdict["permission_model_ok"] is True
    assert verdict["no_unlock_ok"] is True
    assert verdict["credential_safe"] is True
    assert verdict["no_secret_value_fields"] is True
    assert verdict["forbidden_list_intact"] is True
    assert verdict["permit_consistent"] is True
    assert verdict["no_trade_language"] is True


def test_safe_unsafe_and_approved_inputs_all_validate_structurally():
    for payload in (
        _safe_input(),
        _approved_input(),
        _approved_input(authorizes_trading=True),
        None,
    ):
        verdict = _VALIDATE(_BUILD(payload))
        assert verdict["valid"] is True, payload


def test_validate_rejects_tampered_executes():
    contract = _BUILD()
    contract["executes"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["executes_false"] is False


def test_validate_rejects_tampered_performs_fetch():
    contract = _BUILD()
    contract["performs_fetch"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["performs_fetch_false"] is False


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
    contract["fetch_contract"]["databento_api_key"] = "leaked-value"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["no_secret_value_fields"] is False


def test_validate_rejects_default_enabled_permission_model():
    contract = _BUILD()
    contract["fetch_contract"]["fetch_permission_model"]["enabled_by_default"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["permission_model_ok"] is False


def test_validate_rejects_permitted_fetch_with_unlocked_gate():
    # If a contract is somehow marked permitted while a gate is unlocked, the
    # permit-consistency check must fail.
    contract = _BUILD(_approved_input())
    assert contract["fetch_permitted_for_future_runner"] is True
    contract["real_data_qa_blocked"] = False
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["permit_consistent"] is False


def test_validate_rejects_tampered_provider():
    contract = _BUILD()
    contract["fetch_contract"]["approved_provider"] = "binance_exchange_api"
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
        "# Crypto-D1 Databento Read-Only Fetch Execution Contract"
    )
    assert "## 1. Approved Pairs" in text
    assert "## 2. Approved Provider" in text
    assert "## 3. Approved Destination" in text
    assert "## 5. Credential Safety Rules" in text
    assert "## 6. Fetch Permission Model" in text
    assert "## 9. Hard-Stop Conditions" in text
    assert "## 10. No-Unlock Confirmation" in text
    assert "## Still Forbidden (always)" in text


def test_authored_narrative_has_no_execution_verbs():
    contract = _BUILD(_approved_input())
    blob = " ".join(
        str(contract.get(k, ""))
        for k in ("operator_next_step", "fetch_summary", "core_rule")
    )
    blob += " " + " ".join(
        str(s) for s in contract.get("human_operator_required_next_steps", [])
    )
    tokens = set(
        "".join(
            c if (c.isalnum() or c == "_") else " " for c in blob.lower()
        ).split()
    )
    for term in FETCH_FORBIDDEN_TRADE_TERMS:
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
    _BUILD(_approved_input())
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
