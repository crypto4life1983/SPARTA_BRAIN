"""Bundle 36 tests for the Strategy Factory Fake Walk Report Operator Review
Gate v1 (informational, read-only, fake-only, review-gate-only, deterministic,
execution-free -- NO written report, NO report render, NO report file write, NO
real dry walk, NO orchestrator, NO real pipeline, NO smoke-test run, NO runtime
state write, NO approval persistence, NO research, NO data access).

Bundle 36's production module imports Bundles 11-35 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 36 spec):
- module imports cleanly + public API limited to expected names,
- schema / label / status / state / decision / gate constants pinned,
- allowed operator decisions exact 4-tuple,
- pure stdlib import-root audit + forbidden-surface audit (open, pathlib, os,
  glob, subprocess, requests, socket, datetime, time, random, importlib,
  __import__, eval, exec, compile),
- no filesystem read/write surface is present,
- all 14 posture keys present + all False + keys match Bundle 35,
- posture is mutation-isolated (fresh dicts),
- activation only from an active Bundle 35 report contract with next_gate ==
  FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED,
- blocked / wrong-gate / inactive / malformed never activate, never raise,
- READY_FOR_FAKE_REPORT_RENDERER_CONTRACT maps to
  FAKE_REPORT_RENDERER_CONTRACT_REQUIRED,
- non-READY decisions (NEEDS_FIX / PARK / REJECT / missing / unknown) never
  unlock the renderer,
- required operator / report / safety-attestation field tuples enforced,
- no report file write or runtime write capability exists,
- no execution/data/backtest/broker/upload/autopilot/live/dashboard-runtime/
  ledger-write/runtime-state flag True,
- markdown says fake-walk-report-operator-review-gate-only +
  no-report-file-write + review-only + no-runtime-state-write + research-only +
  execution-free, writes nothing,
- prose verb audit, scoped dirty-tree guard, Bundle 11-35 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_fake_walk_report_operator_review_gate import (  # noqa: E501
    REPORT_REVIEW_GATE_SCHEMA_VERSION,
    DEFAULT_REPORT_REVIEW_GATE_LABEL,
    REPORT_REVIEW_GATE_STATUS,
    REPORT_REVIEW_GATE_SAFETY_POSTURE,
    GATE_STATE_ACTIVE,
    GATE_STATE_BLOCKED,
    OPERATOR_DECISION_NEEDS_FAKE_REPORT_FIX,
    OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT,
    OPERATOR_DECISION_PARK,
    OPERATOR_DECISION_REJECT,
    ALLOWED_OPERATOR_DECISIONS,
    NEXT_GATE_FAKE_REPORT_RENDERER_CONTRACT_REQUIRED,
    NEXT_GATE_FAKE_REPORT_FIX_REQUIRED,
    NEXT_GATE_FAKE_REPORT_PARKED,
    NEXT_GATE_FAKE_REPORT_REJECTED,
    NEXT_GATE_AWAIT_REPORT_OPERATOR_REVIEW_DECISION,
    NEXT_GATE_AWAIT_FAKE_WALK_REPORT_CONTRACT,
    REQUIRED_OPERATOR_REVIEW_FIELDS,
    REQUIRED_REPORT_REVIEW_FIELDS,
    REQUIRED_SAFETY_ATTESTATION_FIELDS,
    REJECTION_CONDITIONS,
    build_fake_walk_report_operator_review_gate,
    validate_fake_walk_report_operator_review_gate,
    render_fake_walk_report_operator_review_gate_markdown,
)
import sparta_commander.strategy_factory_fake_walk_report_operator_review_gate as GT  # noqa: E501
from sparta_commander.strategy_factory_fake_walk_report_contract import (
    FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION,
    FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED,
    build_fake_walk_report_contract,
)
from sparta_commander.strategy_factory_fake_dry_walk_result_review_contract import (  # noqa: E501
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT,
    build_fake_dry_walk_result_review_contract,
)
from sparta_commander.strategy_factory_fake_dry_walk_in_memory import (
    build_fake_dry_walk_state,
)
from sparta_commander.strategy_factory_fake_dry_walk_implementation_contract import (  # noqa: E501
    build_fake_dry_walk_implementation_contract,
)
from sparta_commander.strategy_factory_fake_dry_walk_operator_review_gate import (
    OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT,
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
    / "strategy_factory_fake_walk_report_operator_review_gate.py"
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
    "report_file_write", "report_contract_execution",
    "report_render_execution", "report_operator_review_execution",
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


def _active_state() -> dict:
    smoke = build_fake_artifact_smoke_test_contract(_ready_closure())
    dry_walk = build_fake_artifact_dry_walk_contract(smoke)
    gate = build_fake_dry_walk_operator_review_gate(
        dry_walk,
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
        ),
    )
    contract = build_fake_dry_walk_implementation_contract(gate)
    return build_fake_dry_walk_state(contract)


def _blocked_state() -> dict:
    smoke = build_fake_artifact_smoke_test_contract(_blocked_closure())
    dry_walk = build_fake_artifact_dry_walk_contract(smoke)
    gate = build_fake_dry_walk_operator_review_gate(dry_walk)
    contract = build_fake_dry_walk_implementation_contract(gate)
    return build_fake_dry_walk_state(contract)


def _ready_review() -> dict:
    return build_fake_dry_walk_result_review_contract(
        _active_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
        ),
    )


def _active_report() -> dict:
    return build_fake_walk_report_contract(_ready_review())


def _blocked_report() -> dict:
    review = build_fake_dry_walk_result_review_contract(
        _blocked_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
        ),
    )
    return build_fake_walk_report_contract(review)


def _gate(report=None, operator_decision=None) -> dict:
    return build_fake_walk_report_operator_review_gate(
        report if report is not None else _active_report(),
        operator_decision=operator_decision,
    )


def _expected_public() -> set[str]:
    return {
        "REPORT_REVIEW_GATE_SCHEMA_VERSION",
        "DEFAULT_REPORT_REVIEW_GATE_LABEL",
        "REPORT_REVIEW_GATE_STATUS",
        "REPORT_REVIEW_GATE_SAFETY_POSTURE",
        "GATE_STATE_ACTIVE",
        "GATE_STATE_BLOCKED",
        "OPERATOR_DECISION_NEEDS_FAKE_REPORT_FIX",
        "OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT",
        "OPERATOR_DECISION_PARK",
        "OPERATOR_DECISION_REJECT",
        "ALLOWED_OPERATOR_DECISIONS",
        "NEXT_GATE_FAKE_REPORT_RENDERER_CONTRACT_REQUIRED",
        "NEXT_GATE_FAKE_REPORT_FIX_REQUIRED",
        "NEXT_GATE_FAKE_REPORT_PARKED",
        "NEXT_GATE_FAKE_REPORT_REJECTED",
        "NEXT_GATE_AWAIT_REPORT_OPERATOR_REVIEW_DECISION",
        "NEXT_GATE_AWAIT_FAKE_WALK_REPORT_CONTRACT",
        "REQUIRED_OPERATOR_REVIEW_FIELDS",
        "REQUIRED_REPORT_REVIEW_FIELDS",
        "REQUIRED_SAFETY_ATTESTATION_FIELDS",
        "REJECTION_CONDITIONS",
        "build_fake_walk_report_operator_review_gate",
        "validate_fake_walk_report_operator_review_gate",
        "render_fake_walk_report_operator_review_gate_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(GT.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(GT, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        REPORT_REVIEW_GATE_SCHEMA_VERSION
        == "strategy_factory_fake_walk_report_operator_review_gate.v1"
    )
    assert (
        DEFAULT_REPORT_REVIEW_GATE_LABEL
        == "Strategy Factory Fake Walk Report Operator Review Gate"
    )
    assert (
        REPORT_REVIEW_GATE_STATUS
        == "READ_ONLY_FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE"
    )


# 3 -- state / decision / next-gate constants pinned.

def test_state_decision_and_gate_constants_pinned():
    assert (
        GATE_STATE_ACTIVE
        == "FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE_ACTIVE"
    )
    assert (
        GATE_STATE_BLOCKED
        == "FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE_BLOCKED"
    )
    assert OPERATOR_DECISION_NEEDS_FAKE_REPORT_FIX == "NEEDS_FAKE_REPORT_FIX"
    assert (
        OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT
        == "READY_FOR_FAKE_REPORT_RENDERER_CONTRACT"
    )
    assert OPERATOR_DECISION_PARK == "PARK"
    assert OPERATOR_DECISION_REJECT == "REJECT"
    assert (
        NEXT_GATE_FAKE_REPORT_RENDERER_CONTRACT_REQUIRED
        == "FAKE_REPORT_RENDERER_CONTRACT_REQUIRED"
    )
    assert NEXT_GATE_FAKE_REPORT_FIX_REQUIRED == "FAKE_REPORT_FIX_REQUIRED"
    assert NEXT_GATE_FAKE_REPORT_PARKED == "FAKE_REPORT_PARKED"
    assert NEXT_GATE_FAKE_REPORT_REJECTED == "FAKE_REPORT_REJECTED"
    assert (
        NEXT_GATE_AWAIT_REPORT_OPERATOR_REVIEW_DECISION
        == "AWAIT_FAKE_REPORT_OPERATOR_REVIEW_DECISION"
    )
    assert (
        NEXT_GATE_AWAIT_FAKE_WALK_REPORT_CONTRACT
        == "AWAIT_FAKE_WALK_REPORT_CONTRACT"
    )


# 4 -- allowed operator decisions exact 4-tuple.

def test_allowed_operator_decisions_exact():
    assert ALLOWED_OPERATOR_DECISIONS == (
        "NEEDS_FAKE_REPORT_FIX",
        "READY_FOR_FAKE_REPORT_RENDERER_CONTRACT",
        "PARK",
        "REJECT",
    )


# 5 -- required operator / report / safety field tuples exact.

def test_required_field_tuples_exact():
    assert REQUIRED_OPERATOR_REVIEW_FIELDS == (
        "reviewer_identity_placeholder",
        "report_assessment_placeholder",
        "blocking_findings_placeholder",
        "human_sign_off_placeholder",
    )
    assert REQUIRED_REPORT_REVIEW_FIELDS == (
        "report_title_review_placeholder",
        "report_sections_review_placeholder",
        "fake_walk_summary_review_placeholder",
        "pass_fail_summary_review_placeholder",
    )
    assert REQUIRED_SAFETY_ATTESTATION_FIELDS == (
        "read_only_attestation_placeholder",
        "execution_free_attestation_placeholder",
        "no_real_data_attestation_placeholder",
        "no_runtime_state_write_attestation_placeholder",
        "no_report_file_write_attestation_placeholder",
    )
    assert len(REJECTION_CONDITIONS) >= 1


# 6 -- pure stdlib import-root audit: allowed roots only.

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


# 7 -- forbidden-surface audit: no file/network/subprocess/exec/dynamic surface.

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


# 8 -- no filesystem read/write surface in source.

def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# 9 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = REPORT_REVIEW_GATE_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 10 -- posture keys match Bundle 35.

def test_posture_keys_match_bundle35():
    assert (
        set(REPORT_REVIEW_GATE_SAFETY_POSTURE.keys())
        == set(FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE.keys())
    )


# 11 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _gate()
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _gate()
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert REPORT_REVIEW_GATE_SAFETY_POSTURE["automation_enabled"] is False


# 12 -- an active Bundle 35 report contract activates the gate.

def test_active_report_activates_gate():
    g = _gate()
    assert g["fake_walk_report_operator_review_gate_active"] is True
    assert (
        g["fake_walk_report_operator_review_gate_state"]
        == "FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE_ACTIVE"
    )
    assert g["fake_walk_report_contract_active"] is True
    assert (
        g["fake_walk_report_contract_next_gate"]
        == "FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED"
    )
    assert g["schema_version"] == REPORT_REVIEW_GATE_SCHEMA_VERSION
    assert (
        g["fake_walk_report_contract_schema_version"]
        == FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION
    )
    # No decision yet -> awaiting the operator's review decision.
    assert g["next_gate"] == "AWAIT_FAKE_REPORT_OPERATOR_REVIEW_DECISION"


# 13 -- a blocked (inactive) upstream report does not activate.

def test_blocked_report_does_not_activate():
    g = _gate(_blocked_report())
    assert g["fake_walk_report_operator_review_gate_active"] is False
    assert (
        g["fake_walk_report_operator_review_gate_state"]
        == "FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE_BLOCKED"
    )
    assert g["next_gate"] == "AWAIT_FAKE_WALK_REPORT_CONTRACT"


# 14 -- active report but wrong next_gate does not activate.

def test_active_report_wrong_next_gate_does_not_activate():
    import copy
    r = copy.deepcopy(_active_report())
    r["next_gate"] = "SOMETHING_ELSE"
    g = _gate(r)
    assert g["fake_walk_report_operator_review_gate_active"] is False
    assert g["next_gate"] == "AWAIT_FAKE_WALK_REPORT_CONTRACT"


# 15 -- inactive report flag does not activate even with right next_gate.

def test_inactive_report_flag_does_not_activate():
    import copy
    r = copy.deepcopy(_active_report())
    r["fake_walk_report_contract_active"] = False
    g = _gate(r)
    assert g["fake_walk_report_operator_review_gate_active"] is False
    assert g["next_gate"] == "AWAIT_FAKE_WALK_REPORT_CONTRACT"


# 16 -- malformed input never raises and never activates.

def test_malformed_input_no_raise():
    for bad in (None, 42, "nope", {},
                {"fake_walk_report_contract_active": True}, []):
        g = build_fake_walk_report_operator_review_gate(bad)
        assert g["fake_walk_report_operator_review_gate_active"] is False
        assert g["read_only"] is True
        assert g["executes"] is False
        assert g["next_gate"] == "AWAIT_FAKE_WALK_REPORT_CONTRACT"
        for flag in _AUTH_FLAGS:
            assert g[flag] is False


# 17 -- READY decision on an active report unlocks the renderer gate.

def test_ready_decision_unlocks_renderer():
    g = _gate(
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT
        ),
    )
    assert g["fake_walk_report_operator_review_gate_active"] is True
    assert g["operator_decision"] == "READY_FOR_FAKE_REPORT_RENDERER_CONTRACT"
    assert g["next_gate"] == "FAKE_REPORT_RENDERER_CONTRACT_REQUIRED"


# 18 -- non-READY decisions on an active report never unlock the renderer.

def test_non_ready_decisions_never_unlock_renderer():
    cases = {
        OPERATOR_DECISION_NEEDS_FAKE_REPORT_FIX: "FAKE_REPORT_FIX_REQUIRED",
        OPERATOR_DECISION_PARK: "FAKE_REPORT_PARKED",
        OPERATOR_DECISION_REJECT: "FAKE_REPORT_REJECTED",
        None: "AWAIT_FAKE_REPORT_OPERATOR_REVIEW_DECISION",
        "BOGUS_DECISION": "AWAIT_FAKE_REPORT_OPERATOR_REVIEW_DECISION",
    }
    for decision, expected_next in cases.items():
        g = _gate(operator_decision=decision)
        assert g["next_gate"] == expected_next, decision
        assert (
            g["next_gate"] != "FAKE_REPORT_RENDERER_CONTRACT_REQUIRED"
        ), decision


# 19 -- a READY decision on a BLOCKED report still never unlocks the renderer.

def test_ready_on_blocked_report_never_unlocks_renderer():
    g = _gate(
        _blocked_report(),
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT
        ),
    )
    assert g["fake_walk_report_operator_review_gate_active"] is False
    assert g["next_gate"] == "AWAIT_FAKE_WALK_REPORT_CONTRACT"


# 20 -- contract carries the exact required field tuples.

def test_contract_carries_required_field_tuples():
    g = _gate()
    assert (
        tuple(g["allowed_operator_decisions"]) == ALLOWED_OPERATOR_DECISIONS
    )
    assert (
        tuple(g["required_operator_review_fields"])
        == REQUIRED_OPERATOR_REVIEW_FIELDS
    )
    assert (
        tuple(g["required_report_review_fields"])
        == REQUIRED_REPORT_REVIEW_FIELDS
    )
    assert (
        tuple(g["required_safety_attestation_fields"])
        == REQUIRED_SAFETY_ATTESTATION_FIELDS
    )
    for coll in (REQUIRED_OPERATOR_REVIEW_FIELDS, REQUIRED_REPORT_REVIEW_FIELDS,
                 REQUIRED_SAFETY_ATTESTATION_FIELDS):
        assert len(coll) >= 1
        for f in coll:
            assert "placeholder" in f


# 21 -- blocked capabilities include the required set + report-review ones.

def test_blocked_capabilities():
    g = _gate()
    blocked = set(g["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap
    assert "report_file_write" in blocked
    assert "report_render_execution" in blocked
    assert "report_operator_review_execution" in blocked
    assert "runtime_state_write" in blocked


# 22 -- no authorization flag can become True (any state).

def test_authorization_flags_always_false():
    states = [
        _gate(),
        _gate(operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT)),
        build_fake_walk_report_operator_review_gate({}),
        _gate(_blocked_report()),
    ]
    for g in states:
        for flag in _AUTH_FLAGS:
            assert g[flag] is False
        assert all(v is False for v in g["safety_posture"].values())
        assert g["executes"] is False
        assert g["read_only"] is True
        assert g["human_approval_required"] is True
        assert g["mode"] == "RESEARCH_ONLY"
        assert g["stage"] == "FAKE_REPORT_REVIEW_ONLY"


# 23 -- even an active gate authorizes no data/runtime/report-write surface.

def test_active_gate_authorizes_no_runtime_or_report_write():
    g = _gate(operator_decision=(
        OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT))
    assert g["data_fetch_authorized"] is False
    assert g["backtest_authorized"] is False
    assert g["execution_authorized"] is False
    assert g["promotion_authorized"] is False
    assert g["safety_posture"]["data_fetch_enabled"] is False
    assert g["safety_posture"]["file_write_enabled"] is False
    assert g["safety_posture"]["automation_enabled"] is False
    assert "report_file_write" in g["blocked_capabilities"]
    assert "report_render_execution" in g["blocked_capabilities"]
    assert "runtime_state_write" in g["blocked_capabilities"]
    assert "file_write" in g["blocked_capabilities"]
    assert "file_read" in g["blocked_capabilities"]


# 24 -- the embedded upstream report contract is preserved.

def test_upstream_report_embedded():
    r = _active_report()
    g = build_fake_walk_report_operator_review_gate(r)
    assert (
        g["fake_walk_report_contract"]["fake_walk_report_contract_active"]
        is True
    )
    assert g["fake_walk_report_contract"]["read_only"] is True


# 25 -- validate passes for a clean contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    g = _gate()
    v = validate_fake_walk_report_operator_review_gate(g)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(g)
    bad["execution_authorized"] = True
    assert (
        validate_fake_walk_report_operator_review_gate(bad)["valid"] is False
    )

    bad2 = copy.deepcopy(g)
    bad2["safety_posture"]["network_enabled"] = True
    assert (
        validate_fake_walk_report_operator_review_gate(bad2)["valid"] is False
    )

    bad3 = copy.deepcopy(g)
    bad3["mode"] = "LIVE"
    assert (
        validate_fake_walk_report_operator_review_gate(bad3)["valid"] is False
    )

    bad4 = copy.deepcopy(g)
    bad4["stage"] = "EXECUTE"
    assert (
        validate_fake_walk_report_operator_review_gate(bad4)["valid"] is False
    )

    bad5 = copy.deepcopy(g)
    bad5["human_approval_required"] = False
    assert (
        validate_fake_walk_report_operator_review_gate(bad5)["valid"] is False
    )


# 26 -- validate flags wrong required decision / field tuples.

def test_validate_flags_wrong_field_tuples():
    import copy
    g = _gate()
    for key in ("allowed_operator_decisions",
                "required_operator_review_fields",
                "required_report_review_fields",
                "required_safety_attestation_fields"):
        bad = copy.deepcopy(g)
        bad[key] = ("not", "the", "right", "tuple")
        assert (
            validate_fake_walk_report_operator_review_gate(bad)["valid"]
            is False
        ), key


# 27 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    g = copy.deepcopy(_gate())
    g.pop("validation", None)
    v = validate_fake_walk_report_operator_review_gate(g)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 28 -- a blocked gate still validates (gate safety, not activation).

def test_blocked_gate_still_validates():
    g = _gate(_blocked_report())
    v = validate_fake_walk_report_operator_review_gate(g)
    assert v["valid"] is True
    assert g["fake_walk_report_operator_review_gate_active"] is False


# 29 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    import copy
    g = copy.deepcopy(_gate())
    g.pop("fake_walk_report_contract", None)
    v = validate_fake_walk_report_operator_review_gate(g)
    assert v["valid"] is False
    assert "fake_walk_report_contract" in v["missing_required_fields"]


# 30 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_review_gate_only_and_execution_free():
    g = _gate()
    md = render_fake_walk_report_operator_review_gate_markdown(g)
    assert isinstance(md, str) and md
    assert (
        "# Strategy Factory Fake Walk Report Operator Review Gate" in md
    )
    assert "fake-walk-report-operator-review-gate-only" in md
    assert "no-report-file-write" in md
    assert "review-only" in md
    assert "no-runtime-state-write" in md
    assert "research-only" in md
    assert "execution-free" in md
    assert "Stage: FAKE_REPORT_REVIEW_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert (
        "Fake walk report operator review gate active: True" in md
    )
    assert "Next gate: AWAIT_FAKE_REPORT_OPERATOR_REVIEW_DECISION" in md
    assert "## Source Reference" in md
    assert "## Approval Expiry" in md
    assert "## Allowed Operator Decisions" in md
    assert "## Required Operator Review Fields" in md
    assert "## Required Report Review Fields" in md
    assert "## Required Safety Attestation Fields" in md
    assert "## Rejection Conditions" in md
    assert "## Blocked Capabilities" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 31 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 32 -- module references no real Crypto-D1 dataset path. (Docstring legally
# NAMES forbidden tokens, so we only assert the real dataset path form absent.)

def test_no_real_artifact_path_in_source():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "Crypto-D1/" not in src
    assert "data/Crypto-D1" not in src
    assert "datasets/" not in src


# 33 -- prose verb audit over notes / source ref / approval / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    g = _gate()

    texts.extend(str(x) for x in g["operator_notes"])
    texts.append(
        str(g["source_fake_walk_report_contract_reference_placeholder"]))
    texts.append(str(g["approval_expiry_placeholder"]))

    md = render_fake_walk_report_operator_review_gate_markdown(g)
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


# 34 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 35 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_fake_walk_report_operator_review_gate.py"'  # noqa: E501
        in src
    )
    assert (
        '"tests/test_strategy_factory_fake_walk_report_operator_review_gate.py"'  # noqa: E501
        in src
    )


# 36 -- Bundle 35 regression import still works.

def test_bundle35_regression_import_still_works():
    r = build_fake_walk_report_contract({})
    assert r["executes"] is False
    assert r["read_only"] is True
    assert r["fake_walk_report_contract_active"] is False


# 37 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
