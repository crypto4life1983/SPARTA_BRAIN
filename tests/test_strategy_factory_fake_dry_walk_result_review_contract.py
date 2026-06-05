"""Bundle 34 tests for the Strategy Factory Fake Dry Walk Result Review
Contract v1 (informational, read-only, fake-only, review-only, deterministic,
execution-free -- NO real dry walk, NO orchestrator, NO real pipeline, NO
smoke-test run, NO runtime state write, NO research, NO data access, NO review
run).

Bundle 34's production module imports Bundles 11-33 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 34 spec):
- module imports cleanly + public API limited to expected names,
- schema / label / status / state / decision / gate constants pinned,
- pure stdlib import-root audit + forbidden-surface audit (open, pathlib, os,
  glob, subprocess, requests, socket, datetime, time, random, importlib,
  __import__, eval, exec, compile),
- no filesystem read/write surface is present,
- all 14 posture keys present + all False + keys match Bundle 33,
- posture is mutation-isolated (fresh dicts),
- activation only from an active Bundle 33 walk with next_gate
  FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED and the required fake outputs present,
- blocked / wrong-gate / inactive / malformed / missing-output never activate,
  never raise,
- allowed decisions exact 4-tuple,
- READY_FOR_FAKE_WALK_REPORT_CONTRACT -> FAKE_WALK_REPORT_CONTRACT_REQUIRED,
- NEEDS_FAKE_WALK_FIX / PARK / REJECT / missing / unknown never unlock report,
- required result / stage / trace / operator fields enforced,
- no execution/data/backtest/broker/upload/autopilot/live/runtime-state flag
  True,
- markdown says fake-dry-walk-result-review-contract-only + review-only +
  placeholder-only + no-runtime-state-write + research-only + execution-free,
  writes nothing,
- prose verb audit, scoped dirty-tree guard, Bundle 11-33 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_fake_dry_walk_result_review_contract import (  # noqa: E501
    RESULT_REVIEW_CONTRACT_SCHEMA_VERSION,
    DEFAULT_RESULT_REVIEW_CONTRACT_LABEL,
    RESULT_REVIEW_CONTRACT_STATUS,
    RESULT_REVIEW_CONTRACT_SAFETY_POSTURE,
    REVIEW_STATE_ACTIVE,
    REVIEW_STATE_BLOCKED,
    RESULT_REVIEW_DECISION_NEEDS_FAKE_WALK_FIX,
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT,
    RESULT_REVIEW_DECISION_PARK,
    RESULT_REVIEW_DECISION_REJECT,
    ALLOWED_RESULT_REVIEW_DECISIONS,
    NEXT_GATE_FAKE_WALK_REPORT_CONTRACT_REQUIRED,
    NEXT_GATE_FAKE_WALK_FIX_REQUIRED,
    NEXT_GATE_FAKE_WALK_PARKED,
    NEXT_GATE_FAKE_WALK_REJECTED,
    NEXT_GATE_AWAIT_RESULT_REVIEW_DECISION,
    NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT,
    REQUIRED_RESULT_FIELDS,
    REQUIRED_STAGE_REVIEW_FIELDS,
    REQUIRED_TRACE_REVIEW_FIELDS,
    REQUIRED_OPERATOR_REVIEW_FIELDS,
    REVIEW_PASS_CRITERIA,
    REVIEW_FAIL_CRITERIA,
    REJECTION_CONDITIONS,
    build_fake_dry_walk_result_review_contract,
    validate_fake_dry_walk_result_review_contract,
    render_fake_dry_walk_result_review_contract_markdown,
)
import sparta_commander.strategy_factory_fake_dry_walk_result_review_contract as RV  # noqa: E501
from sparta_commander.strategy_factory_fake_dry_walk_in_memory import (
    DRY_WALK_IN_MEMORY_SCHEMA_VERSION,
    DRY_WALK_IN_MEMORY_SAFETY_POSTURE,
    NEXT_GATE_FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED,
    build_fake_dry_walk_state,
)
from sparta_commander.strategy_factory_fake_dry_walk_implementation_contract import (  # noqa: E501
    build_fake_dry_walk_implementation_contract,
)
from sparta_commander.strategy_factory_fake_dry_walk_operator_review_gate import (
    OPERATOR_DECISION_NEEDS_MORE_SPEC,
    OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT,
    OPERATOR_DECISION_PARK,
    OPERATOR_DECISION_REJECT,
    build_fake_dry_walk_operator_review_gate,
)
from sparta_commander.strategy_factory_fake_artifact_dry_walk_contract import (
    build_fake_artifact_dry_walk_contract,
)
from sparta_commander.strategy_factory_fake_artifact_smoke_test_contract import (
    build_fake_artifact_smoke_test_contract,
)
from sparta_commander.strategy_factory_backbone_closure_report import (
    build_backbone_closure_report,
)
from sparta_commander.strategy_factory_end_to_end_fake_pipeline_contract import (
    build_end_to_end_fake_pipeline_contract,
)
from sparta_commander.strategy_factory_safety_kill_switch_contract import (
    build_safety_kill_switch_contract,
)
from sparta_commander.strategy_factory_decision_ledger_contract import (
    build_decision_ledger_contract,
)
from sparta_commander.strategy_factory_dashboard_registry_feed_contract import (
    build_dashboard_registry_feed_contract,
)
from sparta_commander.strategy_factory_dry_run_orchestrator_contract import (
    build_dry_run_orchestrator_contract,
)
from sparta_commander.strategy_factory_research_runner_contract import (
    build_research_runner_contract,
)
from sparta_commander.strategy_factory_data_qa_contract import (
    build_data_qa_contract,
)
from sparta_commander.strategy_factory_data_contract_planning import (
    build_data_contract_planning,
)
from sparta_commander.strategy_factory_protocol_review_gate import (
    REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    build_protocol_review_gate,
)
from sparta_commander.strategy_factory_research_protocol_draft_contract import (
    build_research_protocol_draft_contract,
)
from sparta_commander.strategy_factory_research_decision_memo_contract import (
    MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
)
from sparta_commander.strategy_factory_research_queue import (
    build_research_queue_item,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_fake_dry_walk_result_review_contract.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

_BAD_VERBS = (
    "RUN", "EXECUTE", "LAUNCH", "SUBMIT", "TRADE", "ORDER",
    "PROMOTE", "DEPLOY", "UPLOAD", "FETCH", "BACKTEST",
)

_AUTH_FLAGS = (
    "approved_for_research", "execution_authorized",
    "paper_trading_authorized", "live_trading_authorized",
    "data_fetch_authorized", "backtest_authorized", "promotion_authorized",
)

_REQUIRED_BLOCKED = (
    "data_fetch", "backtest", "simulation", "broker", "exchange", "order",
    "live_execution", "paper_execution", "upload", "autopilot",
    "promotion", "subprocess", "network", "file_write", "file_read",
    "directory_listing", "dashboard_runtime_update", "registry_file_write",
    "template_edit", "ledger_runtime_write", "runtime_approval_write",
    "runtime_safety_flag_write", "pipeline_execution", "smoke_test_execution",
    "dry_walk_execution", "operator_review_gate_execution",
    "dry_walk_implementation_execution", "result_review_execution",
    "runtime_state_write",
)

_EXPECTED_POSTURE_KEYS = {
    "automation_enabled", "live_execution_enabled", "paper_execution_enabled",
    "file_write_enabled", "network_enabled", "subprocess_enabled",
    "strategy_promotion_enabled", "broker_enabled", "exchange_enabled",
    "order_enabled", "data_fetch_enabled", "backtest_enabled",
    "upload_enabled", "autopilot_enabled",
}


def _good_item() -> dict:
    return build_research_queue_item(
        "idea-001",
        "Opening Range Mean Reversion",
        "Price tends to revert toward the opening range midpoint intraday.",
        asset_lane="MNQ",
        timeframe="5m",
    )


def _ready_closure() -> dict:
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(
        draft, review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING)
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    orchestrator = build_dry_run_orchestrator_contract(runner)
    feed = build_dashboard_registry_feed_contract(orchestrator)
    ledger = build_decision_ledger_contract(feed)
    safety_gate = build_safety_kill_switch_contract(ledger)
    pipeline = build_end_to_end_fake_pipeline_contract(safety_gate)
    return build_backbone_closure_report(pipeline)


def _blocked_closure() -> dict:
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(draft)  # awaiting, not unlocked
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    orchestrator = build_dry_run_orchestrator_contract(runner)
    feed = build_dashboard_registry_feed_contract(orchestrator)
    ledger = build_decision_ledger_contract(feed)
    safety_gate = build_safety_kill_switch_contract(ledger)
    pipeline = build_end_to_end_fake_pipeline_contract(safety_gate)
    return build_backbone_closure_report(pipeline)


def _active_dry_walk() -> dict:
    smoke = build_fake_artifact_smoke_test_contract(_ready_closure())
    return build_fake_artifact_dry_walk_contract(smoke)


def _blocked_dry_walk() -> dict:
    smoke = build_fake_artifact_smoke_test_contract(_blocked_closure())
    return build_fake_artifact_dry_walk_contract(smoke)


def _active_state() -> dict:
    gate = build_fake_dry_walk_operator_review_gate(
        _active_dry_walk(),
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
        ),
    )
    contract = build_fake_dry_walk_implementation_contract(gate)
    return build_fake_dry_walk_state(contract)


def _blocked_state() -> dict:
    gate = build_fake_dry_walk_operator_review_gate(_blocked_dry_walk())
    contract = build_fake_dry_walk_implementation_contract(gate)
    return build_fake_dry_walk_state(contract)


def _contract(decision=None, walk=None) -> dict:
    return build_fake_dry_walk_result_review_contract(
        walk if walk is not None else _active_state(),
        result_review_decision=decision,
    )


def _expected_public() -> set[str]:
    return {
        "RESULT_REVIEW_CONTRACT_SCHEMA_VERSION",
        "DEFAULT_RESULT_REVIEW_CONTRACT_LABEL",
        "RESULT_REVIEW_CONTRACT_STATUS",
        "RESULT_REVIEW_CONTRACT_SAFETY_POSTURE",
        "REVIEW_STATE_ACTIVE",
        "REVIEW_STATE_BLOCKED",
        "RESULT_REVIEW_DECISION_NEEDS_FAKE_WALK_FIX",
        "RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT",
        "RESULT_REVIEW_DECISION_PARK",
        "RESULT_REVIEW_DECISION_REJECT",
        "ALLOWED_RESULT_REVIEW_DECISIONS",
        "NEXT_GATE_FAKE_WALK_REPORT_CONTRACT_REQUIRED",
        "NEXT_GATE_FAKE_WALK_FIX_REQUIRED",
        "NEXT_GATE_FAKE_WALK_PARKED",
        "NEXT_GATE_FAKE_WALK_REJECTED",
        "NEXT_GATE_AWAIT_RESULT_REVIEW_DECISION",
        "NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT",
        "REQUIRED_RESULT_FIELDS",
        "REQUIRED_STAGE_REVIEW_FIELDS",
        "REQUIRED_TRACE_REVIEW_FIELDS",
        "REQUIRED_OPERATOR_REVIEW_FIELDS",
        "REVIEW_PASS_CRITERIA",
        "REVIEW_FAIL_CRITERIA",
        "REJECTION_CONDITIONS",
        "build_fake_dry_walk_result_review_contract",
        "validate_fake_dry_walk_result_review_contract",
        "render_fake_dry_walk_result_review_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(RV.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(RV, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        RESULT_REVIEW_CONTRACT_SCHEMA_VERSION
        == "strategy_factory_fake_dry_walk_result_review_contract.v1"
    )
    assert (
        DEFAULT_RESULT_REVIEW_CONTRACT_LABEL
        == "Strategy Factory Fake Dry Walk Result Review Contract"
    )
    assert (
        RESULT_REVIEW_CONTRACT_STATUS
        == "READ_ONLY_FAKE_DRY_WALK_RESULT_REVIEW_CONTRACT"
    )


# 3 -- state / decision / next-gate constants pinned.

def test_state_decision_and_gate_constants_pinned():
    assert REVIEW_STATE_ACTIVE == "FAKE_DRY_WALK_RESULT_REVIEW_ACTIVE"
    assert REVIEW_STATE_BLOCKED == "FAKE_DRY_WALK_RESULT_REVIEW_BLOCKED"
    assert RESULT_REVIEW_DECISION_NEEDS_FAKE_WALK_FIX == "NEEDS_FAKE_WALK_FIX"
    assert (
        RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
        == "READY_FOR_FAKE_WALK_REPORT_CONTRACT"
    )
    assert RESULT_REVIEW_DECISION_PARK == "PARK"
    assert RESULT_REVIEW_DECISION_REJECT == "REJECT"
    assert (
        NEXT_GATE_FAKE_WALK_REPORT_CONTRACT_REQUIRED
        == "FAKE_WALK_REPORT_CONTRACT_REQUIRED"
    )
    assert NEXT_GATE_FAKE_WALK_FIX_REQUIRED == "FAKE_WALK_FIX_REQUIRED"
    assert NEXT_GATE_FAKE_WALK_PARKED == "FAKE_WALK_PARKED"
    assert NEXT_GATE_FAKE_WALK_REJECTED == "FAKE_WALK_REJECTED"
    assert (
        NEXT_GATE_AWAIT_RESULT_REVIEW_DECISION
        == "AWAIT_FAKE_WALK_RESULT_REVIEW_DECISION"
    )
    assert (
        NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT == "AWAIT_FAKE_DRY_WALK_RESULT"
    )


# 4 -- allowed decisions exact 4-tuple.

def test_allowed_decisions_exact():
    assert ALLOWED_RESULT_REVIEW_DECISIONS == (
        "NEEDS_FAKE_WALK_FIX",
        "READY_FOR_FAKE_WALK_REPORT_CONTRACT",
        "PARK",
        "REJECT",
    )


# 5 -- pure stdlib import-root audit: allowed roots only.

def test_import_roots_are_allowed_only():
    src = _MODPATH.read_text(encoding="utf-8")
    roots: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {"__future__", "typing", "sparta_commander"}
    assert roots <= allowed, f"unexpected import roots: {sorted(roots - allowed)}"
    for banned in ("os", "sys", "subprocess", "socket", "requests",
                   "urllib", "pathlib", "json", "http", "asyncio",
                   "datetime", "time", "random", "glob", "importlib",
                   "shutil", "io"):
        assert banned not in roots, f"banned import root present: {banned}"


# 6 -- forbidden-surface audit: no file/network/subprocess/exec/dynamic surface.

def test_no_forbidden_call_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    forbidden = (
        "open(", "write_text(", "write_bytes(", ".write(", "read_text(",
        "read_bytes(", ".read(", "json.dump(", "json.load(",
        "import subprocess", "from subprocess", "Popen", "os.system",
        "os.listdir", "os.scandir", "os.walk", "listdir(", "scandir(",
        "glob(", "iglob(", "import socket", "socket.socket", "urllib",
        "requests", "httpx", "http.client", "asyncio", "place_order",
        "submit_order", "create_order", "cancel_order", "ccxt", "freqtrade",
        "paper_trade", "live_trade", "autopilot(", ".upload(", "datetime.",
        "time.time(", "random.", "subprocess.run", "check_output",
        "importlib", "__import__", "eval(", "exec(", "compile(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


# 7 -- no filesystem read/write surface in source.

def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# 8 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = RESULT_REVIEW_CONTRACT_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 9 -- posture keys match Bundle 33.

def test_posture_keys_match_bundle33():
    assert (
        set(RESULT_REVIEW_CONTRACT_SAFETY_POSTURE.keys())
        == set(DRY_WALK_IN_MEMORY_SAFETY_POSTURE.keys())
    )


# 10 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _contract()
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _contract()
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        RESULT_REVIEW_CONTRACT_SAFETY_POSTURE["automation_enabled"] is False
    )


# 11 -- an active Bundle 33 walk activates the result review contract.

def test_active_walk_activates_contract():
    c = _contract()
    assert c["fake_dry_walk_result_review_contract_active"] is True
    assert (
        c["fake_dry_walk_result_review_state"]
        == "FAKE_DRY_WALK_RESULT_REVIEW_ACTIVE"
    )
    assert c["fake_dry_walk_active"] is True
    assert (
        c["fake_dry_walk_next_gate"]
        == "FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED"
    )
    # No decision supplied yet -> awaiting the human decision.
    assert c["next_gate"] == "AWAIT_FAKE_WALK_RESULT_REVIEW_DECISION"
    assert c["schema_version"] == RESULT_REVIEW_CONTRACT_SCHEMA_VERSION
    assert (
        c["fake_dry_walk_in_memory_schema_version"]
        == DRY_WALK_IN_MEMORY_SCHEMA_VERSION
    )


# 12 -- a blocked (inactive) upstream walk does not activate.

def test_blocked_walk_does_not_activate():
    c = _contract(walk=_blocked_state())
    assert c["fake_dry_walk_result_review_contract_active"] is False
    assert (
        c["fake_dry_walk_result_review_state"]
        == "FAKE_DRY_WALK_RESULT_REVIEW_BLOCKED"
    )
    assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_RESULT"


# 13 -- active walk but wrong upstream next_gate does not activate.

def test_active_walk_wrong_next_gate_does_not_activate():
    import copy
    w = copy.deepcopy(_active_state())
    w["next_gate"] = "SOMETHING_ELSE"
    c = _contract(walk=w)
    assert c["fake_dry_walk_result_review_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_RESULT"


# 14 -- active walk flag off does not activate even with right gate/outputs.

def test_inactive_walk_flag_does_not_activate():
    import copy
    w = copy.deepcopy(_active_state())
    w["fake_dry_walk_active"] = False
    c = _contract(walk=w)
    assert c["fake_dry_walk_result_review_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_RESULT"


# 15 -- missing any required upstream output does not activate.

def test_missing_upstream_output_does_not_activate():
    import copy
    for key in ("pass_fail_summary", "stage_records", "trace_records",
                "operator_review_packet"):
        w = copy.deepcopy(_active_state())
        w[key] = {} if key in ("pass_fail_summary",
                               "operator_review_packet") else []
        c = _contract(walk=w)
        assert c["fake_dry_walk_result_review_contract_active"] is False, key
        assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_RESULT", key


# 16 -- malformed input never raises and never activates.

def test_malformed_input_no_raise():
    for bad in (None, 42, "nope", {}, {"fake_dry_walk_active": True}, []):
        c = build_fake_dry_walk_result_review_contract(bad)
        assert c["fake_dry_walk_result_review_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_RESULT"
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 17 -- READY_FOR_FAKE_WALK_REPORT_CONTRACT unlocks the report gate.

def test_ready_decision_unlocks_report_gate():
    c = _contract(
        decision=RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT)
    assert c["result_review_decision"] == "READY_FOR_FAKE_WALK_REPORT_CONTRACT"
    assert c["next_gate"] == "FAKE_WALK_REPORT_CONTRACT_REQUIRED"
    assert c["fake_dry_walk_result_review_contract_active"] is True


# 18 -- each non-READY decision maps to its own gate, never the report gate.

def test_non_ready_decisions_never_unlock_report():
    mapping = {
        RESULT_REVIEW_DECISION_NEEDS_FAKE_WALK_FIX: "FAKE_WALK_FIX_REQUIRED",
        RESULT_REVIEW_DECISION_PARK: "FAKE_WALK_PARKED",
        RESULT_REVIEW_DECISION_REJECT: "FAKE_WALK_REJECTED",
        None: "AWAIT_FAKE_WALK_RESULT_REVIEW_DECISION",
        "BOGUS_DECISION": "AWAIT_FAKE_WALK_RESULT_REVIEW_DECISION",
    }
    for decision, gate in mapping.items():
        c = _contract(decision=decision)
        assert c["next_gate"] == gate, decision
        assert c["next_gate"] != "FAKE_WALK_REPORT_CONTRACT_REQUIRED"


# 19 -- READY on a blocked walk never unlocks the report gate.

def test_ready_decision_on_blocked_walk_never_unlocks():
    c = _contract(
        decision=RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT,
        walk=_blocked_state())
    assert c["fake_dry_walk_result_review_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_RESULT"


# 20 -- unknown decision is normalized to empty on the contract.

def test_unknown_decision_normalized_empty():
    c = _contract(decision="NOT_A_REAL_DECISION")
    assert c["result_review_decision"] == ""
    assert c["next_gate"] == "AWAIT_FAKE_WALK_RESULT_REVIEW_DECISION"


# 21 -- required result / stage / trace / operator field tuples exposed.

def test_required_field_tuples_exposed():
    c = _contract()
    assert tuple(c["required_result_fields"]) == REQUIRED_RESULT_FIELDS
    assert (
        tuple(c["required_stage_review_fields"]) == REQUIRED_STAGE_REVIEW_FIELDS
    )
    assert (
        tuple(c["required_trace_review_fields"]) == REQUIRED_TRACE_REVIEW_FIELDS
    )
    assert (
        tuple(c["required_operator_review_fields"])
        == REQUIRED_OPERATOR_REVIEW_FIELDS
    )
    assert REQUIRED_RESULT_FIELDS == (
        "fake_pass_fail_summary_placeholder",
        "fake_stage_records_placeholder",
        "fake_trace_records_placeholder",
        "fake_operator_review_packet_placeholder",
    )


# 22 -- review pass / fail / rejection criteria present.

def test_review_criteria_present():
    c = _contract()
    assert len(REVIEW_PASS_CRITERIA) >= 1
    assert len(REVIEW_FAIL_CRITERIA) >= 1
    assert len(REJECTION_CONDITIONS) >= 1
    assert tuple(c["review_pass_criteria"]) == REVIEW_PASS_CRITERIA
    assert tuple(c["review_fail_criteria"]) == REVIEW_FAIL_CRITERIA
    assert tuple(c["rejection_conditions"]) == REJECTION_CONDITIONS


# 23 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    c = _contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap
    assert "result_review_execution" in blocked


# 24 -- no authorization flag can become True (any state).

def test_authorization_flags_always_false():
    states = [
        _contract(),
        _contract(
            decision=RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT),
        _contract(walk=_blocked_state()),
        build_fake_dry_walk_result_review_contract({}),
    ]
    for c in states:
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["mode"] == "RESEARCH_ONLY"
        assert c["stage"] == "FAKE_REVIEW_ONLY"


# 25 -- even an active contract authorizes no data/runtime-state surface.

def test_active_contract_authorizes_no_runtime_state():
    c = _contract(
        decision=RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT)
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["automation_enabled"] is False
    assert "result_review_execution" in c["blocked_capabilities"]
    assert "runtime_state_write" in c["blocked_capabilities"]
    assert "file_read" in c["blocked_capabilities"]
    assert "file_write" in c["blocked_capabilities"]


# 26 -- the embedded upstream walk result is preserved.

def test_upstream_walk_result_embedded():
    w = _active_state()
    c = build_fake_dry_walk_result_review_contract(w)
    assert c["fake_dry_walk_result"]["fake_dry_walk_active"] is True
    assert c["fake_dry_walk_result"]["read_only"] is True


# 27 -- validate passes for a clean contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _contract(
        decision=RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT)
    v = validate_fake_dry_walk_result_review_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_fake_dry_walk_result_review_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_fake_dry_walk_result_review_contract(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_fake_dry_walk_result_review_contract(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["stage"] = "EXECUTE"
    assert validate_fake_dry_walk_result_review_contract(bad4)["valid"] is False


# 28 -- validate flags wrong required-field tuples.

def test_validate_flags_wrong_required_field_tuples():
    import copy
    c = _contract()
    for key in ("allowed_result_review_decisions", "required_result_fields",
                "required_stage_review_fields", "required_trace_review_fields",
                "required_operator_review_fields"):
        bad = copy.deepcopy(c)
        bad[key] = ("not", "the", "right", "tuple")
        assert (
            validate_fake_dry_walk_result_review_contract(bad)["valid"] is False
        ), key


# 29 -- validate flags missing review criteria.

def test_validate_flags_missing_review_criteria():
    import copy
    c = _contract()
    for key in ("review_pass_criteria", "review_fail_criteria",
                "rejection_conditions"):
        bad = copy.deepcopy(c)
        bad[key] = ()
        assert (
            validate_fake_dry_walk_result_review_contract(bad)["valid"] is False
        ), key


# 30 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_contract(
        decision=RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT))
    c.pop("validation", None)
    v = validate_fake_dry_walk_result_review_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 31 -- a blocked contract still validates (review safety, not activation).

def test_blocked_contract_still_validates():
    c = _contract(walk=_blocked_state())
    v = validate_fake_dry_walk_result_review_contract(c)
    assert v["valid"] is True
    assert c["fake_dry_walk_result_review_contract_active"] is False


# 32 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    import copy
    c = copy.deepcopy(_contract())
    c.pop("fake_dry_walk_result", None)
    v = validate_fake_dry_walk_result_review_contract(c)
    assert v["valid"] is False
    assert "fake_dry_walk_result" in v["missing_required_fields"]


# 33 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_review_only_and_execution_free():
    c = _contract(
        decision=RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT)
    md = render_fake_dry_walk_result_review_contract_markdown(c)
    assert isinstance(md, str) and md
    assert (
        "# Strategy Factory Fake Dry Walk Result Review Contract" in md
    )
    assert "fake-dry-walk-result-review-contract-only" in md
    assert "review-only" in md
    assert "placeholder-only" in md
    assert "no-runtime-state-write" in md
    assert "research-only" in md
    assert "execution-free" in md
    assert "Stage: FAKE_REVIEW_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert (
        "Fake dry walk result review contract active: True" in md
    )
    assert "Next gate: FAKE_WALK_REPORT_CONTRACT_REQUIRED" in md
    assert "## Source Reference" in md
    assert "## Allowed Result Review Decisions" in md
    assert "## Required Result Fields" in md
    assert "## Required Stage Review Fields" in md
    assert "## Required Trace Review Fields" in md
    assert "## Required Operator Review Fields" in md
    assert "## Review Pass Criteria" in md
    assert "## Review Fail Criteria" in md
    assert "## Rejection Conditions" in md
    assert "## Blocked Capabilities" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 34 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 35 -- module references no real Crypto-D1 dataset path. (Docstring legally
# NAMES forbidden tokens, so we only assert the real dataset path form absent.)

def test_no_real_artifact_path_in_source():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "Crypto-D1/" not in src
    assert "data/Crypto-D1" not in src
    assert "datasets/" not in src


# 36 -- prose verb audit over notes / source ref / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _contract()

    texts.extend(str(x) for x in c["operator_notes"])
    texts.append(
        str(c["source_fake_dry_walk_result_reference_placeholder"]))

    md = render_fake_dry_walk_result_review_contract_markdown(c)
    for ln in md.splitlines():
        stripped = ln.lstrip()
        if stripped.startswith("#") or stripped.startswith("- `"):
            continue
        if stripped.startswith("- ") and "`" in stripped:
            continue
        if re.match(r"^[A-Za-z][A-Za-z0-9 ]*: ", stripped):
            continue
        texts.append(ln)

    for text in texts:
        upper = text.upper()
        for verb in _BAD_VERBS:
            assert not re.search(rf"\b{verb}\b", upper), (
                f"prose {text!r} contains forbidden verb {verb!r}"
            )


# 37 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 38 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_fake_dry_walk_result_review_contract.py"'  # noqa: E501
        in src
    )
    assert (
        '"tests/test_strategy_factory_fake_dry_walk_result_review_contract.py"'
        in src
    )


# 39 -- Bundle 33 regression import still works.

def test_bundle33_regression_import_still_works():
    s = build_fake_dry_walk_state({})
    assert s["executes"] is False
    assert s["read_only"] is True
    assert s["fake_dry_walk_active"] is False


# 40 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
