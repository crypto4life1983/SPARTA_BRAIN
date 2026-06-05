"""Bundle 33 tests for the Strategy Factory Fake Dry Walk In-Memory
implementation v1 (informational, read-only, fake-only, in-memory-only,
deterministic, execution-free -- NO real dry walk, NO orchestrator, NO real
pipeline, NO smoke-test run, NO runtime state write, NO research, NO data
access).

Bundle 33's production module imports Bundles 11-32 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 33 spec):
- module imports cleanly + public API limited to expected names,
- schema / label / status / state / gate constants pinned,
- pure stdlib import-root audit + forbidden-surface audit (open, pathlib, os,
  glob, subprocess, requests, socket, datetime, time, random, importlib,
  __import__, eval, exec),
- no filesystem read/write surface is present,
- all 14 posture keys present + all False + keys match Bundle 32,
- posture is mutation-isolated (fresh dicts),
- activation only from an active Bundle 32 implementation contract with
  next_gate FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED and the exact
  fake-only implementation scope,
- blocked / wrong-gate / inactive / malformed never activate, never raise,
- active next_gate == FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED,
- all 10 stage names present in order,
- every stage input/output is fake/placeholder-only,
- trace records exist for every stage and are fake-placeholder-only,
- operator review packet exists and is fake-placeholder-only,
- validation flags real artifact names injected into stage records,
- markdown says fake-dry-walk-only + in-memory-only + placeholder-only +
  no-runtime-state-write + research-only + execution-free, writes nothing,
- no execution/data/backtest/broker/upload/autopilot/live/dashboard-runtime/
  ledger-write/runtime-state flag True,
- prose verb audit, scoped dirty-tree guard, Bundle 11-32 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_fake_dry_walk_in_memory import (
    DRY_WALK_IN_MEMORY_SCHEMA_VERSION,
    DEFAULT_DRY_WALK_IN_MEMORY_LABEL,
    DRY_WALK_IN_MEMORY_STATUS,
    DRY_WALK_IN_MEMORY_SAFETY_POSTURE,
    WALK_STATE_ACTIVE,
    WALK_STATE_BLOCKED,
    NEXT_GATE_FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED,
    NEXT_GATE_AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT,
    STAGE_SEQUENCE,
    PROHIBITED_REAL_ARTIFACT_REFERENCES,
    build_fake_dry_walk_state,
    validate_fake_dry_walk_state,
    render_fake_dry_walk_markdown,
)
import sparta_commander.strategy_factory_fake_dry_walk_in_memory as WK
from sparta_commander.strategy_factory_fake_dry_walk_implementation_contract import (  # noqa: E501
    DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE,
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
    / "strategy_factory_fake_dry_walk_in_memory.py"
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
    "dry_walk_implementation_execution", "runtime_state_write",
)

_EXPECTED_STAGES = (
    "research_queue_intake",
    "research_protocol_draft",
    "protocol_review_gate",
    "data_contract_planning",
    "data_qa_review",
    "research_runner_review",
    "dry_walk_orchestrator_review",
    "dashboard_registry_feed_review",
    "decision_ledger_review",
    "safety_kill_switch_review",
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


def _ready_gate() -> dict:
    return build_fake_dry_walk_operator_review_gate(
        _active_dry_walk(),
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
        ),
    )


def _active_contract() -> dict:
    return build_fake_dry_walk_implementation_contract(_ready_gate())


def _state(contract=None) -> dict:
    return build_fake_dry_walk_state(
        contract if contract is not None else _active_contract())


def _expected_public() -> set[str]:
    return {
        "DRY_WALK_IN_MEMORY_SCHEMA_VERSION",
        "DEFAULT_DRY_WALK_IN_MEMORY_LABEL",
        "DRY_WALK_IN_MEMORY_STATUS",
        "DRY_WALK_IN_MEMORY_SAFETY_POSTURE",
        "WALK_STATE_ACTIVE",
        "WALK_STATE_BLOCKED",
        "NEXT_GATE_FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED",
        "NEXT_GATE_AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT",
        "STAGE_SEQUENCE",
        "PROHIBITED_REAL_ARTIFACT_REFERENCES",
        "build_fake_dry_walk_state",
        "validate_fake_dry_walk_state",
        "render_fake_dry_walk_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(WK.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(WK, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        DRY_WALK_IN_MEMORY_SCHEMA_VERSION
        == "strategy_factory_fake_dry_walk_in_memory.v1"
    )
    assert (
        DEFAULT_DRY_WALK_IN_MEMORY_LABEL
        == "Strategy Factory Fake Dry Walk In Memory"
    )
    assert DRY_WALK_IN_MEMORY_STATUS == "READ_ONLY_FAKE_DRY_WALK_IN_MEMORY"


# 3 -- state / next-gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert WALK_STATE_ACTIVE == "FAKE_DRY_WALK_ACTIVE"
    assert WALK_STATE_BLOCKED == "FAKE_DRY_WALK_BLOCKED"
    assert (
        NEXT_GATE_FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED
        == "FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED"
    )
    assert (
        NEXT_GATE_AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
        == "AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"
    )


# 4 -- pure stdlib import-root audit: allowed roots only.

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


# 5 -- forbidden-surface audit: no file/network/subprocess/exec/dynamic surface.

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


# 6 -- no filesystem read/write surface in source.

def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# 7 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = DRY_WALK_IN_MEMORY_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 8 -- posture keys match Bundle 32.

def test_posture_keys_match_bundle32():
    assert (
        set(DRY_WALK_IN_MEMORY_SAFETY_POSTURE.keys())
        == set(DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE.keys())
    )


# 9 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _state()
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _state()
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        DRY_WALK_IN_MEMORY_SAFETY_POSTURE["automation_enabled"] is False
    )


# 10 -- an active Bundle 32 contract activates the walk.

def test_active_contract_activates_walk():
    s = _state()
    assert s["fake_dry_walk_active"] is True
    assert s["fake_dry_walk_state"] == "FAKE_DRY_WALK_ACTIVE"
    assert s["fake_dry_walk_implementation_contract_active"] is True
    assert (
        s["fake_dry_walk_implementation_contract_next_gate"]
        == "FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED"
    )
    assert s["next_gate"] == "FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED"


# 11 -- a non-active (blocked upstream) contract does not activate the walk.

def test_blocked_contract_does_not_activate():
    blocked_contract = build_fake_dry_walk_implementation_contract(
        build_fake_dry_walk_operator_review_gate(_blocked_dry_walk()))
    s = _state(blocked_contract)
    assert s["fake_dry_walk_active"] is False
    assert s["fake_dry_walk_state"] == "FAKE_DRY_WALK_BLOCKED"
    assert s["next_gate"] == "AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"


# 12 -- non-READY upstream decisions never activate the walk.

def test_non_ready_decisions_never_activate():
    for decision in (
        OPERATOR_DECISION_NEEDS_MORE_SPEC,
        OPERATOR_DECISION_PARK,
        OPERATOR_DECISION_REJECT,
        None,
    ):
        gate = build_fake_dry_walk_operator_review_gate(
            _active_dry_walk(), operator_decision=decision)
        contract = build_fake_dry_walk_implementation_contract(gate)
        s = _state(contract)
        assert s["fake_dry_walk_active"] is False
        assert s["next_gate"] == "AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"


# 13 -- active contract but wrong upstream next_gate does not activate.

def test_active_contract_wrong_next_gate_does_not_activate():
    import copy
    c = copy.deepcopy(_active_contract())
    c["next_gate"] = "SOMETHING_ELSE"
    s = _state(c)
    assert s["fake_dry_walk_active"] is False
    assert s["next_gate"] == "AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"


# 14 -- active contract but wrong implementation scope does not activate.

def test_active_contract_wrong_scope_does_not_activate():
    import copy
    c = copy.deepcopy(_active_contract())
    c["implementation_scope"] = ("fake_only",)
    s = _state(c)
    assert s["fake_dry_walk_active"] is False
    assert s["next_gate"] == "AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"


# 15 -- inactive contract flag does not activate even with right gate/scope.

def test_inactive_contract_flag_does_not_activate():
    import copy
    c = copy.deepcopy(_active_contract())
    c["fake_dry_walk_implementation_contract_active"] = False
    s = _state(c)
    assert s["fake_dry_walk_active"] is False
    assert s["next_gate"] == "AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"


# 16 -- malformed contract never raises and never activates.

def test_malformed_contract_no_raise():
    for bad in (None, 42, "nope", {},
                {"fake_dry_walk_implementation_contract_active": True}, []):
        s = build_fake_dry_walk_state(bad)
        assert s["fake_dry_walk_active"] is False
        assert s["read_only"] is True
        assert s["executes"] is False
        for flag in _AUTH_FLAGS:
            assert s[flag] is False


# 17 -- all 10 stage names present in order.

def test_stage_sequence_exact_order():
    assert tuple(STAGE_SEQUENCE) == _EXPECTED_STAGES
    s = _state()
    assert tuple(s["stage_sequence"]) == _EXPECTED_STAGES
    assert tuple(r["stage_name"] for r in s["stage_records"]) == (
        _EXPECTED_STAGES
    )


# 18 -- every stage input/output is fake/placeholder-only.

def test_stage_inputs_outputs_placeholder_only():
    s = _state()
    assert len(s["stage_records"]) == len(_EXPECTED_STAGES)
    for r in s["stage_records"]:
        assert "fake" in r["fake_input_placeholder"]
        assert "placeholder" in r["fake_input_placeholder"]
        assert "fake" in r["fake_output_placeholder"]
        assert "placeholder" in r["fake_output_placeholder"]
        assert r["stage_status"] == "FAKE_PASS_PLACEHOLDER"


# 19 -- trace records exist for every stage and are fake-placeholder-only.

def test_trace_records_per_stage_placeholder_only():
    s = _state()
    traces = s["trace_records"]
    assert len(traces) == len(_EXPECTED_STAGES)
    for t, name in zip(traces, _EXPECTED_STAGES):
        assert t["stage_name_placeholder"] == name
        assert "placeholder" in t["trace_id_placeholder"]
        assert "placeholder" in t["input_digest_placeholder"]
        assert "placeholder" in t["output_digest_placeholder"]
        assert t["stage_status_placeholder"] == "FAKE_PASS_PLACEHOLDER"


# 20 -- operator review packet exists and is fake-placeholder-only.

def test_operator_review_packet_placeholder_only():
    s = _state()
    packet = s["operator_review_packet"]
    for key in ("reviewer_identity_placeholder",
                "stage_assessment_placeholder",
                "blocking_findings_placeholder",
                "human_sign_off_placeholder"):
        assert key in packet
        assert "placeholder" in str(packet[key])
        assert "fake" in str(packet[key]) or "none" in str(packet[key])


# 21 -- pass/fail summary is deterministic and all-fake-pass.

def test_pass_fail_summary_all_fake_pass():
    s = _state()
    summary = s["pass_fail_summary"]
    assert summary["total_stages"] == len(_EXPECTED_STAGES)
    assert summary["fake_pass_count"] == len(_EXPECTED_STAGES)
    assert summary["fake_fail_count"] == 0
    assert summary["all_fake_stages_passed_placeholder"] is True


# 22 -- placeholder-only guard holds for a clean state.

def test_placeholder_only_guard_holds():
    s = _state()
    guard = s["placeholder_only_guard"]
    assert guard["all_stage_inputs_placeholder_only"] is True
    assert guard["all_stage_outputs_placeholder_only"] is True
    assert guard["no_real_artifact_reference"] is True
    assert guard["guard_holds"] is True


# 23 -- validation fails if any stage contains a real artifact name.

def test_validation_flags_real_artifact_names():
    import copy
    real_tokens = (
        "Crypto-D1", "qa_report.json", "manifest.json", "CHECKSUMS.txt",
        "FREEZE_RECORD.txt", "fees.json", "baseline_outputs",
        "my_dataset.csv", "prices.parquet", "/data/real_prices",
    )
    for tok in real_tokens:
        s = copy.deepcopy(_state())
        s["stage_records"][0]["fake_input_placeholder"] = tok
        v = validate_fake_dry_walk_state(s)
        assert v["valid"] is False, tok
        assert v["placeholder_only_guard_holds"] is False, tok


# 24 -- validation also flags real artifact names in trace records.

def test_validation_flags_real_artifact_in_traces():
    import copy
    s = copy.deepcopy(_state())
    s["trace_records"][2]["input_digest_placeholder"] = "Crypto-D1"
    v = validate_fake_dry_walk_state(s)
    assert v["valid"] is False
    assert v["placeholder_only_guard_holds"] is False


# 25 -- prohibited real artifact references list is exposed and complete.

def test_prohibited_real_artifact_references():
    refs = set(PROHIBITED_REAL_ARTIFACT_REFERENCES)
    for item in ("Crypto-D1", "qa_report.json", "manifest.json",
                 "CHECKSUMS.txt", "FREEZE_RECORD.txt", "fees.json",
                 ".csv", ".parquet", "/data/"):
        assert item in refs, item
    s = _state()
    assert set(s["prohibited_real_artifact_references"]) == refs


# 26 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    s = _state()
    blocked = set(s["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 27 -- no authorization flag can become True (any state).

def test_authorization_flags_always_false():
    states = [
        _state(),
        _state(build_fake_dry_walk_implementation_contract(
            build_fake_dry_walk_operator_review_gate(_active_dry_walk()))),
        build_fake_dry_walk_state({}),
        _state(build_fake_dry_walk_implementation_contract(
            build_fake_dry_walk_operator_review_gate(_blocked_dry_walk()))),
    ]
    for s in states:
        for flag in _AUTH_FLAGS:
            assert s[flag] is False
        assert all(v is False for v in s["safety_posture"].values())
        assert s["executes"] is False
        assert s["read_only"] is True
        assert s["human_approval_required"] is True
        assert s["mode"] == "RESEARCH_ONLY"
        assert s["stage"] == "FAKE_WALK_ONLY"


# 28 -- even an active walk authorizes no data/runtime-state surface.

def test_active_walk_authorizes_no_runtime_state():
    s = _state()
    assert s["data_fetch_authorized"] is False
    assert s["backtest_authorized"] is False
    assert s["execution_authorized"] is False
    assert s["safety_posture"]["data_fetch_enabled"] is False
    assert s["safety_posture"]["automation_enabled"] is False
    assert "pipeline_execution" in s["blocked_capabilities"]
    assert "runtime_state_write" in s["blocked_capabilities"]
    assert "dry_walk_execution" in s["blocked_capabilities"]
    assert "file_read" in s["blocked_capabilities"]
    assert "file_write" in s["blocked_capabilities"]


# 29 -- the embedded upstream contract is preserved.

def test_upstream_contract_embedded():
    c = _active_contract()
    s = build_fake_dry_walk_state(c)
    assert s["fake_dry_walk_implementation_contract"]["schema_version"] == (
        c["schema_version"]
    )
    assert s["fake_dry_walk_implementation_contract"]["read_only"] is True


# 30 -- validate passes for a clean state + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    s = _state()
    v = validate_fake_dry_walk_state(s)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(s)
    bad["execution_authorized"] = True
    assert validate_fake_dry_walk_state(bad)["valid"] is False

    bad2 = copy.deepcopy(s)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_fake_dry_walk_state(bad2)["valid"] is False

    bad3 = copy.deepcopy(s)
    bad3["mode"] = "LIVE"
    assert validate_fake_dry_walk_state(bad3)["valid"] is False

    bad4 = copy.deepcopy(s)
    bad4["stage_sequence"] = ("only_one",)
    assert validate_fake_dry_walk_state(bad4)["valid"] is False

    bad5 = copy.deepcopy(s)
    bad5["stage_records"] = bad5["stage_records"][:5]
    assert validate_fake_dry_walk_state(bad5)["valid"] is False

    bad6 = copy.deepcopy(s)
    bad6["operator_review_packet"] = {}
    assert validate_fake_dry_walk_state(bad6)["valid"] is False


# 31 -- validate never requires the state's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    s = copy.deepcopy(_state())
    s.pop("validation", None)
    v = validate_fake_dry_walk_state(s)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 32 -- a blocked state still validates (walk safety, not activation).

def test_blocked_state_still_validates():
    blocked_contract = build_fake_dry_walk_implementation_contract(
        build_fake_dry_walk_operator_review_gate(_blocked_dry_walk()))
    s = _state(blocked_contract)
    v = validate_fake_dry_walk_state(s)
    assert v["valid"] is True
    assert s["fake_dry_walk_active"] is False


# 33 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_fake_only_and_execution_free():
    s = _state()
    md = render_fake_dry_walk_markdown(s)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Fake Dry Walk In Memory" in md
    assert "fake-dry-walk-only" in md
    assert "in-memory-only" in md
    assert "placeholder-only" in md
    assert "no-runtime-state-write" in md
    assert "research-only" in md
    assert "execution-free" in md
    assert "Stage: FAKE_WALK_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Fake dry walk active: True" in md
    assert "Next gate: FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED" in md
    assert "## Source Reference" in md
    assert "## Stage Sequence" in md
    assert "## Stage Records" in md
    assert "## Trace Records" in md
    assert "## Operator Review Packet" in md
    assert "## Pass Fail Summary" in md
    assert "## Placeholder Only Guard" in md
    assert "## Prohibited Real Artifact References" in md
    assert "## Blocked Capabilities" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md
    # every stage name appears in markdown
    for name in _EXPECTED_STAGES:
        assert name in md


# 34 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 35 -- module references no real Crypto-D1 dataset path. (Docstring and the
# PROHIBITED_REAL_ARTIFACT_REFERENCES / guard token list legally NAME forbidden
# tokens, so we only assert the real dataset path form is absent.)

def test_no_real_artifact_path_in_source():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "Crypto-D1/" not in src
    assert "data/Crypto-D1" not in src
    assert "datasets/" not in src


# 36 -- prose verb audit over notes / source / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    s = _state()

    texts.extend(str(x) for x in s["operator_notes"])
    texts.append(str(s["source_implementation_contract_reference_placeholder"]))

    md = render_fake_dry_walk_markdown(s)
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
        '"sparta_commander/strategy_factory_fake_dry_walk_in_memory.py"' in src
    )
    assert (
        '"tests/test_strategy_factory_fake_dry_walk_in_memory.py"' in src
    )


# 39 -- Bundle 32 regression import still works.

def test_bundle32_regression_import_still_works():
    from sparta_commander.strategy_factory_fake_dry_walk_implementation_contract import (  # noqa: E501
        build_fake_dry_walk_implementation_contract as build32,
    )
    r = build32({})
    assert r["executes"] is False
    assert r["read_only"] is True
    assert r["fake_dry_walk_implementation_contract_active"] is False


# 40 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
