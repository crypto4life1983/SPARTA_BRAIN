"""Tests for the Crypto-D1 Databento One-Time Fetch Human-Run Approval Packet (Block 144).

The packet is the human-facing approval form a human operator reads and signs off
before authorizing ONE controlled, read-only Databento historical fetch of the
three missing Crypto-D1 daily pairs. It is a PURE, stdlib-only document layer: it
states the exact operator command / payload shape, the safety checks, the allowed
outputs, and the hard stops -- and performs NOTHING.

These tests assert: schema / constants; mission-flow truth sync against the live
status module; the approved scope (symbols / timeframe / provider / destination /
report path); the exact approved run payload (human_run_approved=True, in scope);
the operator command shape (names the Block 143 runner, requires an injected
provider client + writer, invokes nothing); provider / credential boundary rules;
expected outputs; the hard-stop list; that a forbidden flag / off-boundary input
marks the packet unsafe; that every capability flag is False and every gate stays
locked; that a secret value is never carried; determinism; validation tamper
rejections; render; AST purity (only typing / sparta_commander roots, no os /
network / credential modules, no os.environ access, NO open / write_* call); and
the two additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_databento_one_time_fetch_human_approval_packet import (  # noqa: E501
    DEFAULT_PACKET_INPUT,
    PACKET_APPROVED_DESTINATION,
    PACKET_APPROVED_PROVIDER,
    PACKET_APPROVED_REPORT_DIR,
    PACKET_APPROVED_SYMBOLS,
    PACKET_APPROVED_TIMEFRAMES,
    PACKET_CORE_RULE,
    PACKET_HARD_STOPS,
    PACKET_LABEL,
    PACKET_MODE,
    PACKET_REQUIRED_RUN_FLAG,
    PACKET_SCHEMA_VERSION,
    PACKET_STATUS,
    build_approved_run_payload,
    build_one_time_fetch_human_approval_packet,
    render_one_time_fetch_human_approval_packet_markdown,
    validate_one_time_fetch_human_approval_packet,
)
from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    FETCH_HUMAN_RUN_APPROVAL_FLAG,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_databento_one_time_fetch_human_approval_packet.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_databento_one_time_fetch_human_approval_packet.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_databento_one_time_fetch_human_approval_packet.py"
)

_BUILD = build_one_time_fetch_human_approval_packet
_VALIDATE = validate_one_time_fetch_human_approval_packet
_RENDER = render_one_time_fetch_human_approval_packet_markdown


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert PACKET_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_databento_one_time_fetch_human_approval_packet.v1"
    )
    assert PACKET_LABEL == (
        "Block 144 - Crypto-D1 Databento One-Time Fetch Human-Run Approval Packet"
    )
    assert PACKET_STATUS == "HUMAN_APPROVAL_PACKET_ONLY"
    assert PACKET_MODE == "RESEARCH_ONLY"
    assert "authorizes nothing" in PACKET_CORE_RULE.lower()
    assert "blocked" in PACKET_CORE_RULE.lower()


def test_required_run_flag_is_human_run_approved():
    assert PACKET_REQUIRED_RUN_FLAG == FETCH_HUMAN_RUN_APPROVAL_FLAG
    assert PACKET_REQUIRED_RUN_FLAG == "human_run_approved"


def test_default_packet_input_has_no_human_approval():
    assert PACKET_REQUIRED_RUN_FLAG not in DEFAULT_PACKET_INPUT


def test_approved_scope_constants():
    assert PACKET_APPROVED_SYMBOLS == ("BTCUSD", "ETHUSD", "SOLUSD")
    assert PACKET_APPROVED_TIMEFRAMES == ("1d",)
    assert PACKET_APPROVED_PROVIDER == "databento_historical_market_data_read_only"
    assert PACKET_APPROVED_DESTINATION == "data/databento_cache/crypto_d1/"
    assert PACKET_APPROVED_REPORT_DIR == "reports/research_os/data_qa/"


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# Approved run payload (exact operator command shape)
# --------------------------------------------------------------------------- #
def test_approved_run_payload_carries_flag_and_scope():
    payload = build_approved_run_payload()
    assert payload[PACKET_REQUIRED_RUN_FLAG] is True
    assert payload["requested_symbols"] == list(PACKET_APPROVED_SYMBOLS)
    assert payload["requested_timeframes"] == list(PACKET_APPROVED_TIMEFRAMES)
    assert payload["requested_provider"] == PACKET_APPROVED_PROVIDER
    assert payload["requested_destination"] == PACKET_APPROVED_DESTINATION
    assert payload["requested_report_dir"] == PACKET_APPROVED_REPORT_DIR


def test_approved_run_payload_is_fresh_each_call():
    a = build_approved_run_payload()
    b = build_approved_run_payload()
    assert a == b
    a["requested_symbols"].append("DOGEUSD")
    assert b["requested_symbols"] == list(PACKET_APPROVED_SYMBOLS)


def test_operator_command_shape_targets_runner_and_invokes_nothing():
    spec = _BUILD()["approval_packet"]
    ocs = spec["operator_command_shape"]
    assert ocs["callable"] == "run_databento_read_only_fetch"
    assert ocs["module"].endswith("read_only_fetch_runner")
    assert ocs["required_run_flag"] == PACKET_REQUIRED_RUN_FLAG
    assert ocs["required_run_flag_value"] is True
    assert ocs["this_packet_invokes_it"] is False
    assert "provider_client" in ocs["keyword_arguments"]
    assert "writer" in ocs["keyword_arguments"]


# --------------------------------------------------------------------------- #
# Build: happy path is valid and locked
# --------------------------------------------------------------------------- #
def test_default_packet_builds_and_validates():
    packet = _BUILD()
    assert packet["status"] == "HUMAN_APPROVAL_PACKET_ONLY"
    assert packet["safe"] is True
    assert packet["this_packet_invokes_runner"] is False
    assert packet["real_data_qa_state"] == "BLOCKED"
    assert packet["baseline_backtest_state"] == "BLOCKED"
    assert packet["paper_live_state"] == "LOCKED"
    assert _VALIDATE(packet)["valid"] is True


def test_packet_capability_flags_all_false_and_gates_locked():
    packet = _BUILD()
    assert packet["executes"] is False
    assert packet["performs_data_fetch"] is False
    assert packet["calls_databento"] is False
    assert packet["uses_network"] is False
    assert packet["authorizes_nothing"] is True
    assert packet["real_data_qa_blocked"] is True
    assert packet["baseline_backtest_blocked"] is True
    assert packet["paper_trading_gate_locked"] is True
    assert packet["micro_live_gate_locked"] is True
    assert packet["unlocks_real_data_qa"] is False


def test_hard_stops_cover_every_required_category():
    blob = " ".join(PACKET_HARD_STOPS).lower()
    assert len(PACKET_HARD_STOPS) >= 10
    assert "wrong symbol" in blob
    assert "wrong timeframe" in blob
    assert "wrong provider" in blob
    assert "destination outside" in blob
    assert "report path outside" in blob
    assert "missing human_run_approved" in blob
    assert "broker" in blob
    assert "portfolio" in blob
    assert "secret" in blob
    assert "gate unlock" in blob


def test_provider_boundary_requires_injected_client():
    spec = _BUILD()["approval_packet"]
    blob = " ".join(spec["provider_boundary_rules"]).lower()
    assert "outside the runner" in blob
    assert "provider_client" in blob
    assert "writer" in blob


def test_credential_rules_present_and_no_secret_exposed():
    spec = _BUILD()["approval_packet"]
    rules = " ".join(spec["credential_handling_rules"]).lower()
    assert "no secret value is ever printed" in rules
    assert ".env" in rules
    assert spec["databento_secret_exposed"] is False


def test_expected_outputs_are_scoped_to_approved_paths():
    spec = _BUILD()["approval_packet"]
    blob = " ".join(spec["expected_outputs"]).lower()
    assert "data/databento_cache/crypto_d1/" in blob
    assert "reports/research_os/data_qa/" in blob


# --------------------------------------------------------------------------- #
# Unsafe inputs: forbidden flag / off-boundary mission flow
# --------------------------------------------------------------------------- #
def test_forbidden_flag_marks_packet_unsafe():
    packet = _BUILD({"authorizes_trading": True})
    assert packet["safe"] is False
    assert "authorizes_trading" in packet["forbidden_flag_hits"]
    # but every real capability flag is still False and gates still locked
    assert packet["executes"] is False
    assert packet["authorizes_trading"] is False
    assert _VALIDATE(packet)["valid"] is True


def test_gate_unlock_request_marks_packet_unsafe():
    packet = _BUILD({"unlock_real_data_qa": True})
    assert packet["safe"] is False
    assert "unlock_real_data_qa" in packet["forbidden_flag_hits"]


def test_off_boundary_mission_flow_marks_packet_unsafe():
    packet = _BUILD({"mission_flow_current_stage": "SOMETHING_ELSE"})
    assert packet["safe"] is False
    assert packet["mission_flow_aligned"] is False


# --------------------------------------------------------------------------- #
# Secret never carried
# --------------------------------------------------------------------------- #
def test_secret_value_in_input_is_never_carried_into_packet():
    packet = _BUILD({"databento_api_key": "SHOULD-NEVER-APPEAR"})
    assert "SHOULD-NEVER-APPEAR" not in _RENDER(packet)
    assert _VALIDATE(packet)["no_secret_value_fields"] is True


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
    packet = _BUILD()
    packet["executes"] = True
    verdict = _VALIDATE(packet)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_unlocked_gate():
    packet = _BUILD()
    packet["real_data_qa_blocked"] = False
    verdict = _VALIDATE(packet)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_validate_rejects_unlocked_state():
    packet = _BUILD()
    packet["real_data_qa_state"] = "OPEN"
    verdict = _VALIDATE(packet)
    assert verdict["valid"] is False
    assert verdict["states_blocked_locked"] is False


def test_validate_rejects_invokes_runner_true():
    packet = _BUILD()
    packet["this_packet_invokes_runner"] = True
    verdict = _VALIDATE(packet)
    assert verdict["valid"] is False
    assert verdict["invokes_runner_false"] is False


def test_validate_rejects_payload_without_run_flag():
    packet = _BUILD()
    packet["approval_packet"]["approved_run_payload"].pop(PACKET_REQUIRED_RUN_FLAG)
    verdict = _VALIDATE(packet)
    assert verdict["valid"] is False
    assert verdict["approved_payload_ok"] is False


def test_validate_rejects_out_of_scope_payload_symbol():
    packet = _BUILD()
    packet["approval_packet"]["approved_run_payload"]["requested_symbols"] = ["DOGEUSD"]
    verdict = _VALIDATE(packet)
    assert verdict["valid"] is False
    assert verdict["approved_payload_ok"] is False


def test_validate_rejects_secret_value():
    packet = _BUILD()
    packet["databento_api_key"] = "leaked-value"
    verdict = _VALIDATE(packet)
    assert verdict["valid"] is False
    assert verdict["no_secret_value_fields"] is False


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #
def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith(
        "# Crypto-D1 Databento One-Time Fetch Human-Run Approval Packet"
    )
    assert "## 1. Approved Symbols" in text
    assert "## 6. Required Run Flag + Operator Command Shape" in text
    assert "## 10. Hard Stops" in text


def test_render_never_leaks_a_secret():
    text = _RENDER(_BUILD({"databento_secret": "TOP-SECRET-VALUE"}))
    assert "TOP-SECRET-VALUE" not in text


# --------------------------------------------------------------------------- #
# AST purity: typing / sparta_commander roots only; no os / network / credential
# modules; no os.environ access; no open / write_* call
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORT_ROOTS = {"__future__", "typing", "sparta_commander"}
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
