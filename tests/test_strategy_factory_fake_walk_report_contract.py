"""Bundle 35 tests for the Strategy Factory Fake Walk Report Contract v1
(informational, read-only, fake-only, report-contract-only, deterministic,
execution-free -- NO written report, NO report file write, NO real dry walk, NO
orchestrator, NO real pipeline, NO smoke-test run, NO runtime state write, NO
research, NO data access).

Bundle 35's production module imports Bundles 11-34 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 35 spec):
- module imports cleanly + public API limited to expected names,
- schema / label / status / state / gate constants pinned,
- pure stdlib import-root audit + forbidden-surface audit (open, pathlib, os,
  glob, subprocess, requests, socket, datetime, time, random, importlib,
  __import__, eval, exec, compile),
- no filesystem read/write surface is present,
- all 14 posture keys present + all False + keys match Bundle 34,
- posture is mutation-isolated (fresh dicts),
- activation only from an active Bundle 34 result review with
  result_review_decision == READY_FOR_FAKE_WALK_REPORT_CONTRACT and next_gate ==
  FAKE_WALK_REPORT_CONTRACT_REQUIRED,
- blocked / wrong-gate / not-ready / inactive / malformed never activate,
  never raise,
- active next_gate == FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED,
- all required report sections present,
- fake summary / stage / trace / operator / pass-fail / safety fields present,
- no report file write or runtime write capability exists,
- no execution/data/backtest/broker/upload/autopilot/live/dashboard-runtime/
  ledger-write/runtime-state flag True,
- markdown says fake-walk-report-contract-only + no-report-file-write +
  review-only + no-runtime-state-write + research-only + execution-free,
  writes nothing,
- prose verb audit, scoped dirty-tree guard, Bundle 11-34 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_fake_walk_report_contract import (
    FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION,
    DEFAULT_FAKE_WALK_REPORT_CONTRACT_LABEL,
    FAKE_WALK_REPORT_CONTRACT_STATUS,
    FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE,
    REPORT_STATE_ACTIVE,
    REPORT_STATE_BLOCKED,
    NEXT_GATE_FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED,
    NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT_REVIEW,
    REQUIRED_REPORT_SECTIONS,
    FAKE_WALK_SUMMARY_FIELDS,
    FAKE_STAGE_SUMMARY_FIELDS,
    FAKE_TRACE_SUMMARY_FIELDS,
    OPERATOR_REVIEW_SUMMARY_FIELDS,
    PASS_FAIL_SUMMARY_FIELDS,
    SAFETY_ATTESTATION_FIELDS,
    build_fake_walk_report_contract,
    validate_fake_walk_report_contract,
    render_fake_walk_report_contract_markdown,
)
import sparta_commander.strategy_factory_fake_walk_report_contract as RP
from sparta_commander.strategy_factory_fake_dry_walk_result_review_contract import (  # noqa: E501
    RESULT_REVIEW_CONTRACT_SCHEMA_VERSION,
    RESULT_REVIEW_CONTRACT_SAFETY_POSTURE,
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT,
    RESULT_REVIEW_DECISION_NEEDS_FAKE_WALK_FIX,
    RESULT_REVIEW_DECISION_PARK,
    RESULT_REVIEW_DECISION_REJECT,
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
    / "strategy_factory_fake_walk_report_contract.py"
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
    "report_file_write", "report_contract_execution", "runtime_state_write",
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


def _contract(review=None) -> dict:
    return build_fake_walk_report_contract(
        review if review is not None else _ready_review())


def _expected_public() -> set[str]:
    return {
        "FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION",
        "DEFAULT_FAKE_WALK_REPORT_CONTRACT_LABEL",
        "FAKE_WALK_REPORT_CONTRACT_STATUS",
        "FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE",
        "REPORT_STATE_ACTIVE",
        "REPORT_STATE_BLOCKED",
        "NEXT_GATE_FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED",
        "NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT_REVIEW",
        "REQUIRED_REPORT_SECTIONS",
        "FAKE_WALK_SUMMARY_FIELDS",
        "FAKE_STAGE_SUMMARY_FIELDS",
        "FAKE_TRACE_SUMMARY_FIELDS",
        "OPERATOR_REVIEW_SUMMARY_FIELDS",
        "PASS_FAIL_SUMMARY_FIELDS",
        "SAFETY_ATTESTATION_FIELDS",
        "build_fake_walk_report_contract",
        "validate_fake_walk_report_contract",
        "render_fake_walk_report_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(RP.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(RP, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION
        == "strategy_factory_fake_walk_report_contract.v1"
    )
    assert (
        DEFAULT_FAKE_WALK_REPORT_CONTRACT_LABEL
        == "Strategy Factory Fake Walk Report Contract"
    )
    assert (
        FAKE_WALK_REPORT_CONTRACT_STATUS
        == "READ_ONLY_FAKE_WALK_REPORT_CONTRACT"
    )


# 3 -- state / next-gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert REPORT_STATE_ACTIVE == "FAKE_WALK_REPORT_CONTRACT_ACTIVE"
    assert REPORT_STATE_BLOCKED == "FAKE_WALK_REPORT_CONTRACT_BLOCKED"
    assert (
        NEXT_GATE_FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED
        == "FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED"
    )
    assert (
        NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT_REVIEW
        == "AWAIT_FAKE_DRY_WALK_RESULT_REVIEW"
    )


# 4 -- required report sections exact.

def test_required_report_sections_exact():
    assert REQUIRED_REPORT_SECTIONS == (
        "executive_summary",
        "fake_walk_scope",
        "fake_stage_walk_summary",
        "fake_trace_summary",
        "operator_review_summary",
        "pass_fail_summary",
        "safety_attestation",
        "blocked_capabilities",
        "next_steps",
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
    posture = FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 9 -- posture keys match Bundle 34.

def test_posture_keys_match_bundle34():
    assert (
        set(FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE.keys())
        == set(RESULT_REVIEW_CONTRACT_SAFETY_POSTURE.keys())
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
        FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE["automation_enabled"] is False
    )


# 11 -- an active READY Bundle 34 review activates the report contract.

def test_active_ready_review_activates_contract():
    c = _contract()
    assert c["fake_walk_report_contract_active"] is True
    assert (
        c["fake_walk_report_contract_state"]
        == "FAKE_WALK_REPORT_CONTRACT_ACTIVE"
    )
    assert c["fake_dry_walk_result_review_contract_active"] is True
    assert c["result_review_decision"] == "READY_FOR_FAKE_WALK_REPORT_CONTRACT"
    assert (
        c["fake_dry_walk_result_review_next_gate"]
        == "FAKE_WALK_REPORT_CONTRACT_REQUIRED"
    )
    assert c["next_gate"] == "FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED"
    assert c["schema_version"] == FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION
    assert (
        c["fake_dry_walk_result_review_contract_schema_version"]
        == RESULT_REVIEW_CONTRACT_SCHEMA_VERSION
    )


# 12 -- a blocked (inactive) upstream review does not activate.

def test_blocked_review_does_not_activate():
    review = build_fake_dry_walk_result_review_contract(
        _blocked_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
        ),
    )
    c = _contract(review)
    assert c["fake_walk_report_contract_active"] is False
    assert (
        c["fake_walk_report_contract_state"]
        == "FAKE_WALK_REPORT_CONTRACT_BLOCKED"
    )
    assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_RESULT_REVIEW"


# 13 -- active review but non-READY decision does not activate.

def test_non_ready_decisions_never_activate():
    for decision in (
        RESULT_REVIEW_DECISION_NEEDS_FAKE_WALK_FIX,
        RESULT_REVIEW_DECISION_PARK,
        RESULT_REVIEW_DECISION_REJECT,
        None,
    ):
        review = build_fake_dry_walk_result_review_contract(
            _active_state(), result_review_decision=decision)
        c = _contract(review)
        assert c["fake_walk_report_contract_active"] is False, decision
        assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_RESULT_REVIEW", decision


# 14 -- active READY review but wrong next_gate does not activate.

def test_active_review_wrong_next_gate_does_not_activate():
    import copy
    r = copy.deepcopy(_ready_review())
    r["next_gate"] = "SOMETHING_ELSE"
    c = _contract(r)
    assert c["fake_walk_report_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_RESULT_REVIEW"


# 15 -- inactive review flag does not activate even with READY + right gate.

def test_inactive_review_flag_does_not_activate():
    import copy
    r = copy.deepcopy(_ready_review())
    r["fake_dry_walk_result_review_contract_active"] = False
    c = _contract(r)
    assert c["fake_walk_report_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_RESULT_REVIEW"


# 16 -- malformed input never raises and never activates.

def test_malformed_input_no_raise():
    for bad in (None, 42, "nope", {},
                {"fake_dry_walk_result_review_contract_active": True}, []):
        c = build_fake_walk_report_contract(bad)
        assert c["fake_walk_report_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_RESULT_REVIEW"
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 17 -- all required report sections present on the contract.

def test_report_sections_present():
    c = _contract()
    assert tuple(c["report_sections_required"]) == REQUIRED_REPORT_SECTIONS
    for section in REQUIRED_REPORT_SECTIONS:
        assert section in c["report_sections_required"]


# 18 -- fake summary / stage / trace / operator / pass-fail / safety fields.

def test_all_field_collections_present():
    c = _contract()
    assert tuple(c["fake_walk_summary_fields"]) == FAKE_WALK_SUMMARY_FIELDS
    assert tuple(c["fake_stage_summary_fields"]) == FAKE_STAGE_SUMMARY_FIELDS
    assert tuple(c["fake_trace_summary_fields"]) == FAKE_TRACE_SUMMARY_FIELDS
    assert (
        tuple(c["operator_review_summary_fields"])
        == OPERATOR_REVIEW_SUMMARY_FIELDS
    )
    assert tuple(c["pass_fail_summary_fields"]) == PASS_FAIL_SUMMARY_FIELDS
    assert tuple(c["safety_attestation_fields"]) == SAFETY_ATTESTATION_FIELDS
    for coll in (FAKE_WALK_SUMMARY_FIELDS, FAKE_STAGE_SUMMARY_FIELDS,
                 FAKE_TRACE_SUMMARY_FIELDS, OPERATOR_REVIEW_SUMMARY_FIELDS,
                 PASS_FAIL_SUMMARY_FIELDS, SAFETY_ATTESTATION_FIELDS):
        assert len(coll) >= 1
        for f in coll:
            assert "placeholder" in f


# 19 -- blocked capabilities include the required set + report-specific ones.

def test_blocked_capabilities():
    c = _contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap
    assert "report_file_write" in blocked
    assert "report_contract_execution" in blocked


# 20 -- no authorization flag can become True (any state).

def test_authorization_flags_always_false():
    states = [
        _contract(),
        _contract(_ready_review()),
        build_fake_walk_report_contract({}),
        _contract(build_fake_dry_walk_result_review_contract(
            _blocked_state(),
            result_review_decision=(
                RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT))),
    ]
    for c in states:
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["mode"] == "RESEARCH_ONLY"
        assert c["stage"] == "FAKE_REPORT_CONTRACT_ONLY"


# 21 -- even an active contract authorizes no data/runtime/report-write surface.

def test_active_contract_authorizes_no_runtime_or_report_write():
    c = _contract()
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["file_write_enabled"] is False
    assert c["safety_posture"]["automation_enabled"] is False
    assert "report_file_write" in c["blocked_capabilities"]
    assert "runtime_state_write" in c["blocked_capabilities"]
    assert "file_write" in c["blocked_capabilities"]
    assert "file_read" in c["blocked_capabilities"]


# 22 -- the embedded upstream review contract is preserved.

def test_upstream_review_embedded():
    r = _ready_review()
    c = build_fake_walk_report_contract(r)
    assert (
        c["fake_walk_result_review"]["fake_dry_walk_result_review_contract_active"]  # noqa: E501
        is True
    )
    assert c["fake_walk_result_review"]["read_only"] is True


# 23 -- validate passes for a clean contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _contract()
    v = validate_fake_walk_report_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_fake_walk_report_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_fake_walk_report_contract(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_fake_walk_report_contract(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["stage"] = "EXECUTE"
    assert validate_fake_walk_report_contract(bad4)["valid"] is False


# 24 -- validate flags wrong required section / field tuples.

def test_validate_flags_wrong_section_and_field_tuples():
    import copy
    c = _contract()
    for key in ("report_sections_required", "fake_walk_summary_fields",
                "fake_stage_summary_fields", "fake_trace_summary_fields",
                "operator_review_summary_fields", "pass_fail_summary_fields",
                "safety_attestation_fields"):
        bad = copy.deepcopy(c)
        bad[key] = ("not", "the", "right", "tuple")
        assert (
            validate_fake_walk_report_contract(bad)["valid"] is False
        ), key


# 25 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_contract())
    c.pop("validation", None)
    v = validate_fake_walk_report_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 26 -- a blocked contract still validates (report safety, not activation).

def test_blocked_contract_still_validates():
    review = build_fake_dry_walk_result_review_contract(
        _blocked_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
        ),
    )
    c = _contract(review)
    v = validate_fake_walk_report_contract(c)
    assert v["valid"] is True
    assert c["fake_walk_report_contract_active"] is False


# 27 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    import copy
    c = copy.deepcopy(_contract())
    c.pop("fake_walk_result_review", None)
    v = validate_fake_walk_report_contract(c)
    assert v["valid"] is False
    assert "fake_walk_result_review" in v["missing_required_fields"]


# 28 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_report_contract_only_and_execution_free():
    c = _contract()
    md = render_fake_walk_report_contract_markdown(c)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Fake Walk Report Contract" in md
    assert "fake-walk-report-contract-only" in md
    assert "no-report-file-write" in md
    assert "review-only" in md
    assert "no-runtime-state-write" in md
    assert "research-only" in md
    assert "execution-free" in md
    assert "Stage: FAKE_REPORT_CONTRACT_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Fake walk report contract active: True" in md
    assert "Next gate: FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED" in md
    assert "## Source Reference" in md
    assert "## Report Title" in md
    assert "## Required Report Sections" in md
    assert "## Fake Walk Summary Fields" in md
    assert "## Fake Stage Summary Fields" in md
    assert "## Fake Trace Summary Fields" in md
    assert "## Operator Review Summary Fields" in md
    assert "## Pass Fail Summary Fields" in md
    assert "## Safety Attestation Fields" in md
    assert "## Blocked Capabilities" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md
    for section in REQUIRED_REPORT_SECTIONS:
        assert section in md


# 29 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 30 -- module references no real Crypto-D1 dataset path. (Docstring legally
# NAMES forbidden tokens, so we only assert the real dataset path form absent.)

def test_no_real_artifact_path_in_source():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "Crypto-D1/" not in src
    assert "data/Crypto-D1" not in src
    assert "datasets/" not in src


# 31 -- prose verb audit over notes / source ref / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _contract()

    texts.extend(str(x) for x in c["operator_notes"])
    texts.append(
        str(c["source_fake_walk_result_review_reference_placeholder"]))
    texts.append(str(c["report_title_placeholder"]))

    md = render_fake_walk_report_contract_markdown(c)
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


# 32 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 33 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_fake_walk_report_contract.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_fake_walk_report_contract.py"' in src
    )


# 34 -- Bundle 34 regression import still works.

def test_bundle34_regression_import_still_works():
    r = build_fake_dry_walk_result_review_contract({})
    assert r["executes"] is False
    assert r["read_only"] is True
    assert r["fake_dry_walk_result_review_contract_active"] is False


# 35 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
