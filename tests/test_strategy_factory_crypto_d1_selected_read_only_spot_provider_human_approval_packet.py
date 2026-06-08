"""Tests for the Human Approval Packet for Selected Read-Only Spot Provider Run
(Block 149).

This module emits a PURE, stdlib-only, *read-only* STATIC packet describing the exact
scope of a FUTURE, human-approved read-only acquisition run for the source the Block
148 orchestrator already selected (the clear-license READ-ONLY spot historical
provider). It calls no provider, fetches nothing, imports no CSV, reads / parses no
file's contents, opens no network, reads no credential / .env, writes nothing, runs
no QA / baseline / backtest, and unlocks no gate -- even when a caller passes
human_spot_provider_run_approved.

These tests assert: schema / constants; mission-flow truth sync against the live
status module; the ten required packet sections (selected_candidate_type /
selected_candidate_name, required_run_approval_flag=human_spot_provider_run_approved,
approved symbols BTCUSD/ETHUSD/SOLUSD, approved timeframe 1d, approved future cache /
report paths, provider_criteria (8), required_future_outputs (2), hard_stops (10));
custom selected_candidate_name handling; that human_spot_provider_run_approved is only
echoed and never runs; that every capability flag is False and every gate stays
locked; that a secret value is never carried; determinism / caller-payload isolation;
validation tamper rejections; render; AST purity (only __future__ / typing /
sparta_commander roots, no os / json / csv / network / credential modules, no
os.environ access, NO open / write_* call); and the two additive commander_2_safety
allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_selected_read_only_spot_provider_human_approval_packet import (  # noqa: E501
    DEFAULT_SELECTED_CANDIDATE_NAME,
    NEXT_RECOMMENDED_ACTION,
    PACKET_APPROVED_CACHE_PATH,
    PACKET_APPROVED_REPORT_DIR,
    PACKET_APPROVED_SYMBOLS,
    PACKET_APPROVED_TIMEFRAMES,
    PACKET_CORE_RULE,
    PACKET_HARD_STOPS,
    PACKET_LABEL,
    PACKET_MODE,
    PACKET_PROVIDER_CRITERIA,
    PACKET_REQUIRED_FUTURE_OUTPUTS,
    PACKET_SCHEMA_VERSION,
    PACKET_STATUS,
    PACKET_SYMBOL_ALIASES,
    REQUIRED_RUN_APPROVAL_FLAG,
    SELECTED_CANDIDATE_TYPE,
    build_crypto_d1_selected_read_only_spot_provider_human_approval_packet,
    render_crypto_d1_selected_read_only_spot_provider_human_approval_packet_markdown,
    validate_crypto_d1_selected_read_only_spot_provider_human_approval_packet,
)
from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_selected_read_only_spot_provider_human_approval_packet.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_selected_read_only_spot_provider_human_approval_packet.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_selected_read_only_spot_provider_human_approval_packet.py"
)

_BUILD = build_crypto_d1_selected_read_only_spot_provider_human_approval_packet
_VALIDATE = validate_crypto_d1_selected_read_only_spot_provider_human_approval_packet
_RENDER = render_crypto_d1_selected_read_only_spot_provider_human_approval_packet_markdown


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert PACKET_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_selected_read_only_spot_provider_human_approval_packet.v1"
    )
    assert PACKET_LABEL == (
        "Block 149 - Human Approval Packet for Selected Read-Only Spot Provider Run"
    )
    assert PACKET_STATUS == "HUMAN_APPROVAL_PACKET_ONLY"
    assert PACKET_MODE == "RESEARCH_ONLY"
    assert "authorizes nothing" in PACKET_CORE_RULE.lower()
    assert "blocked" in PACKET_CORE_RULE.lower()
    assert "human_spot_provider_run_approved" in PACKET_CORE_RULE.lower()


def test_selected_candidate_type_and_default_name():
    assert SELECTED_CANDIDATE_TYPE == (
        "CLEAR_LICENSE_READ_ONLY_SPOT_HISTORICAL_PROVIDER"
    )
    assert DEFAULT_SELECTED_CANDIDATE_NAME == (
        "clear_license_readonly_spot_history_api_archetype"
    )


def test_required_run_approval_flag():
    assert REQUIRED_RUN_APPROVAL_FLAG == "human_spot_provider_run_approved"


def test_approved_symbols_and_timeframes():
    assert PACKET_APPROVED_SYMBOLS == ("BTCUSD", "ETHUSD", "SOLUSD")
    assert PACKET_APPROVED_TIMEFRAMES == ("1d",)


def test_symbol_aliases_include_slash_and_dash_forms():
    assert "BTC/USD" in PACKET_SYMBOL_ALIASES["BTCUSD"]
    assert "ETH-USD" in PACKET_SYMBOL_ALIASES["ETHUSD"]
    assert "SOL/USD" in PACKET_SYMBOL_ALIASES["SOLUSD"]


def test_approved_future_paths():
    assert PACKET_APPROVED_CACHE_PATH == "data/crypto_d1_spot_cache/"
    assert PACKET_APPROVED_REPORT_DIR == "reports/research_os/data_qa/"


def test_provider_criteria_required_outputs_and_hard_stops_counts():
    assert len(PACKET_PROVIDER_CRITERIA) == 8
    assert len(PACKET_REQUIRED_FUTURE_OUTPUTS) == 2
    assert len(PACKET_HARD_STOPS) == 10


def test_next_recommended_action():
    assert NEXT_RECOMMENDED_ACTION == "HOLD_FOR_EXPLICIT_HUMAN_PROVIDER_RUN_APPROVAL"


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# Build: happy path is valid and locked
# --------------------------------------------------------------------------- #
def test_default_contract_builds_and_validates():
    contract = _BUILD()
    assert contract["status"] == "HUMAN_APPROVAL_PACKET_ONLY"
    assert contract["safe"] is True
    assert contract["this_packet_calls_provider"] is False
    assert contract["this_packet_fetches_data"] is False
    assert contract["this_packet_reads_files"] is False
    assert contract["this_packet_writes_files"] is False
    assert contract["this_packet_runs_acquisition"] is False
    assert contract["requires_human_run_approval"] is True
    assert contract["selected_candidate_type"] == SELECTED_CANDIDATE_TYPE
    assert contract["next_recommended_action"] == NEXT_RECOMMENDED_ACTION
    assert contract["real_data_qa_state"] == "BLOCKED"
    assert contract["baseline_backtest_state"] == "BLOCKED"
    assert contract["paper_live_state"] == "LOCKED"
    assert _VALIDATE(contract)["valid"] is True


def test_contract_capability_flags_all_false_and_gates_locked():
    contract = _BUILD()
    assert contract["executes"] is False
    assert contract["calls_provider"] is False
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


def test_contract_carries_all_ten_required_packet_sections():
    contract = _BUILD()
    # 1 + 2: selected source
    assert contract["selected_candidate_type"] == SELECTED_CANDIDATE_TYPE
    assert contract["selected_candidate_name"] == DEFAULT_SELECTED_CANDIDATE_NAME
    # 3: required future approval flag
    assert contract["required_run_approval_flag"] == REQUIRED_RUN_APPROVAL_FLAG
    # 4: approved symbols
    assert contract["approved_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    # 5: approved timeframe
    assert contract["approved_timeframes"] == ["1d"]
    # 6: approved future cache path
    assert contract["approved_future_cache_path"] == "data/crypto_d1_spot_cache/"
    # 7: approved future report path
    assert contract["approved_future_report_dir"] == "reports/research_os/data_qa/"
    # 8: provider criteria
    assert contract["provider_criteria"] == list(PACKET_PROVIDER_CRITERIA)
    assert len(contract["provider_criteria"]) == 8
    # 9: required future outputs
    assert contract["required_future_outputs"] == list(PACKET_REQUIRED_FUTURE_OUTPUTS)
    assert len(contract["required_future_outputs"]) == 2
    # 10: hard stops
    assert contract["hard_stops"] == list(PACKET_HARD_STOPS)
    assert len(contract["hard_stops"]) == 10


def test_approval_packet_subdict_is_locked():
    packet = _BUILD()["approval_packet"]
    assert packet["selected_candidate_type"] == SELECTED_CANDIDATE_TYPE
    assert packet["required_run_approval_flag"] == REQUIRED_RUN_APPROVAL_FLAG
    assert packet["required_run_approval_value"] is True
    assert packet["human_run_approval_required"] is True
    assert packet["run_executed"] is False
    assert packet["run_performed_by_this_block"] is False
    assert packet["approved_symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert packet["approved_timeframes"] == ["1d"]
    assert packet["approved_future_cache_path"] == "data/crypto_d1_spot_cache/"
    assert packet["approved_future_report_dir"] == "reports/research_os/data_qa/"
    assert packet["real_data_qa_state"] == "BLOCKED"
    assert packet["baseline_backtest_state"] == "BLOCKED"
    assert packet["paper_live_state"] == "LOCKED"


def test_custom_selected_candidate_name_is_accepted():
    contract = _BUILD({"selected_candidate_name": "some_clear_license_spot_archive"})
    assert contract["selected_candidate_name"] == "some_clear_license_spot_archive"
    assert contract["approval_packet"]["selected_candidate_name"] == (
        "some_clear_license_spot_archive"
    )
    assert _VALIDATE(contract)["valid"] is True


def test_non_string_selected_candidate_name_falls_back_to_default():
    contract = _BUILD({"selected_candidate_name": 12345})
    assert contract["selected_candidate_name"] == DEFAULT_SELECTED_CANDIDATE_NAME


def test_human_run_approved_is_only_echoed_and_never_runs():
    contract = _BUILD({"human_spot_provider_run_approved": True})
    assert contract["human_run_approved_echo"] is True
    assert contract["run_executed"] is False
    assert contract["this_packet_calls_provider"] is False
    assert contract["this_packet_fetches_data"] is False
    assert contract["this_packet_writes_files"] is False
    assert contract["approval_packet"]["run_executed"] is False
    assert contract["approval_packet"]["run_performed_by_this_block"] is False
    assert _VALIDATE(contract)["valid"] is True


# --------------------------------------------------------------------------- #
# Unsafe inputs: forbidden flag / off-boundary mission flow
# --------------------------------------------------------------------------- #
def test_forbidden_flag_marks_contract_unsafe():
    contract = _BUILD({"fetch_data_now": True})
    assert contract["safe"] is False
    assert "fetch_data_now" in contract["forbidden_flag_hits"]
    assert contract["this_packet_fetches_data"] is False
    assert _VALIDATE(contract)["valid"] is True


def test_call_provider_request_marks_contract_unsafe():
    contract = _BUILD({"call_provider_now": True})
    assert contract["safe"] is False
    assert "call_provider_now" in contract["forbidden_flag_hits"]


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


def test_validate_rejects_this_packet_fetches_data_true():
    contract = _BUILD()
    contract["this_packet_fetches_data"] = True
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


def test_validate_rejects_wrong_approval_flag():
    contract = _BUILD()
    contract["required_run_approval_flag"] = "auto_go"
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["approval_flag_ok"] is False


def test_validate_rejects_tampered_symbols():
    contract = _BUILD()
    contract["approved_symbols"] = ["BTCUSD", "DOGEUSD"]
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["symbols_ok"] is False


def test_validate_rejects_tampered_timeframe():
    contract = _BUILD()
    contract["approved_timeframes"] = ["1h"]
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["timeframes_ok"] is False


def test_validate_rejects_tampered_hard_stops():
    contract = _BUILD()
    contract["hard_stops"] = ["nothing"]
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["hard_stops_ok"] is False


def test_validate_rejects_packet_marked_run_executed():
    contract = _BUILD()
    contract["approval_packet"]["run_executed"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["packet_locked_ok"] is False


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
        "# Human Approval Packet for Selected Read-Only Spot Provider Run"
    )
    assert "## Approved Symbols" in text
    assert "## Approved Timeframe" in text
    assert "## Approved Future Paths" in text
    assert "## Provider Criteria" in text
    assert "## Required Future Outputs" in text
    assert "## Hard Stops" in text
    assert "## Next Recommended Action" in text
    assert "## Operator Next Step" in text
    assert "CLEAR_LICENSE_READ_ONLY_SPOT_HISTORICAL_PROVIDER" in text
    assert "data/crypto_d1_spot_cache/" in text
    assert "reports/research_os/data_qa/" in text


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
    # The packet must own NO filesystem-write capability: it never calls open,
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
