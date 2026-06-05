"""Bundle 32 tests for the Strategy Factory Fake Dry Walk Implementation
Contract template v1 (informational, read-only, planning/template-only, FAKE
artifacts only -- NO dry walk, NO dry-walk implementation, NO operator-review
run, NO smoke-test run, NO fake pipeline run, NO runtime state write, NO
orchestration, NO research, NO data access).

Bundle 32's production module imports Bundles 11-31 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 32 spec):
- module imports cleanly + public API limited to expected names,
- schema / label / status / state / gate constants pinned,
- pure stdlib import-root audit + forbidden-surface audit,
- all 14 posture keys present + all False + keys match Bundle 31,
- posture is mutation-isolated (fresh dicts),
- activates only when the Bundle 31 operator review gate is active with
  operator_decision READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT and
  next_gate FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED,
- non-READY decisions / wrong-gate / inactive / malformed never activate,
  never raise,
- active next_gate == FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED,
- implementation_scope is exactly the six-label tuple,
- allowed in-memory inputs/outputs are fake/placeholder-only,
- prohibited_real_artifact_references include the named real artifacts,
- prohibited_runtime_side_effects include the named side effects,
- no execution/data/backtest/broker/upload/autopilot/live/dashboard-runtime/
  ledger-write/runtime-state flag True,
- validate passes + detects failure modes; validation not self-required,
- markdown says fake-dry-walk-implementation-contract-only + not-implemented-yet
  + planning-only + placeholder-only + no-runtime-state-write + research-only +
  execution-free, writes nothing,
- prose verb audit over notes / source / markdown prose,
- scoped dirty-tree guard, Bundle 11-31 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_fake_dry_walk_implementation_contract import (  # noqa: E501
    DRY_WALK_IMPLEMENTATION_CONTRACT_SCHEMA_VERSION,
    DEFAULT_DRY_WALK_IMPLEMENTATION_CONTRACT_LABEL,
    DRY_WALK_IMPLEMENTATION_CONTRACT_STATUS,
    DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE,
    IMPLEMENTATION_STATE_ACTIVE,
    IMPLEMENTATION_STATE_BLOCKED,
    NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED,
    NEXT_GATE_AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE,
    IMPLEMENTATION_SCOPE,
    ALLOWED_IN_MEMORY_INPUTS,
    ALLOWED_IN_MEMORY_OUTPUTS,
    DRY_WALK_FUNCTION_CONTRACT,
    STAGE_WALK_CONTRACT,
    TRACE_RECORD_CONTRACT,
    OPERATOR_REVIEW_PACKET_CONTRACT,
    PROHIBITED_REAL_ARTIFACT_REFERENCES,
    PROHIBITED_RUNTIME_SIDE_EFFECTS,
    build_fake_dry_walk_implementation_contract,
    validate_fake_dry_walk_implementation_contract,
    render_fake_dry_walk_implementation_contract_markdown,
)
import sparta_commander.strategy_factory_fake_dry_walk_implementation_contract as IC  # noqa: E501
from sparta_commander.strategy_factory_fake_dry_walk_operator_review_gate import (
    DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE,
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
    / "strategy_factory_fake_dry_walk_implementation_contract.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

# Execution / promotion / trading verbs forbidden in human-readable prose.
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
    "promotion", "subprocess", "network", "file_write",
    "dashboard_runtime_update", "registry_file_write", "template_edit",
    "ledger_runtime_write", "runtime_approval_write",
    "runtime_safety_flag_write", "pipeline_execution", "smoke_test_execution",
    "dry_walk_execution", "operator_review_gate_execution",
    "dry_walk_implementation_execution", "runtime_state_write",
)

_EXPECTED_SCOPE = (
    "fake_only",
    "in_memory_only",
    "deterministic",
    "no_real_data",
    "no_runtime_write",
    "no_execution_authority",
)

_REQUIRED_PROHIBITED_REFS = (
    "Crypto-D1", "qa_report.json", "manifest.json", "CHECKSUMS.txt",
    "FREEZE_RECORD.txt", "fees.json", "dataset_files", "baseline_outputs",
    ".csv", ".parquet", "real_market_data_paths",
)

_REQUIRED_PROHIBITED_FX = (
    "file_write", "runtime_state_write", "dashboard_runtime_update",
    "registry_file_write", "ledger_runtime_write", "network", "subprocess",
    "broker_action", "exchange_action", "order_action",
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


def _gate(decision=None) -> dict:
    return build_fake_dry_walk_operator_review_gate(
        _active_dry_walk(), operator_decision=decision)


def _ready_gate() -> dict:
    return _gate(
        OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT)


def _contract(gate=None) -> dict:
    return build_fake_dry_walk_implementation_contract(
        gate if gate is not None else _ready_gate())


def _expected_public() -> set[str]:
    return {
        "DRY_WALK_IMPLEMENTATION_CONTRACT_SCHEMA_VERSION",
        "DEFAULT_DRY_WALK_IMPLEMENTATION_CONTRACT_LABEL",
        "DRY_WALK_IMPLEMENTATION_CONTRACT_STATUS",
        "DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE",
        "IMPLEMENTATION_STATE_ACTIVE",
        "IMPLEMENTATION_STATE_BLOCKED",
        "NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED",
        "NEXT_GATE_AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE",
        "IMPLEMENTATION_SCOPE",
        "ALLOWED_IN_MEMORY_INPUTS",
        "ALLOWED_IN_MEMORY_OUTPUTS",
        "DRY_WALK_FUNCTION_CONTRACT",
        "STAGE_WALK_CONTRACT",
        "TRACE_RECORD_CONTRACT",
        "OPERATOR_REVIEW_PACKET_CONTRACT",
        "PROHIBITED_REAL_ARTIFACT_REFERENCES",
        "PROHIBITED_RUNTIME_SIDE_EFFECTS",
        "build_fake_dry_walk_implementation_contract",
        "validate_fake_dry_walk_implementation_contract",
        "render_fake_dry_walk_implementation_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(IC.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(IC, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        DRY_WALK_IMPLEMENTATION_CONTRACT_SCHEMA_VERSION
        == "strategy_factory_fake_dry_walk_implementation_contract.v1"
    )


# 3 -- label / status pinned.

def test_label_and_status_pinned():
    assert (
        DEFAULT_DRY_WALK_IMPLEMENTATION_CONTRACT_LABEL
        == "Strategy Factory Fake Dry Walk Implementation Contract"
    )
    assert (
        DRY_WALK_IMPLEMENTATION_CONTRACT_STATUS
        == "READ_ONLY_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"
    )


# 4 -- state / next-gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        IMPLEMENTATION_STATE_ACTIVE
        == "FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_ACTIVE"
    )
    assert (
        IMPLEMENTATION_STATE_BLOCKED
        == "FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_BLOCKED"
    )
    assert (
        NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED
        == "FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED"
    )
    assert (
        NEXT_GATE_AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE
        == "AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE"
    )


# 5 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 6 -- posture keys match Bundle 31.

def test_posture_keys_match_bundle31():
    assert (
        set(DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE.keys())
        == set(DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE.keys())
    )


# 7 -- pure stdlib import-root audit: allowed roots only.

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
                   "datetime", "time", "random"):
        assert banned not in roots, f"banned import root present: {banned}"


# 8 -- forbidden-surface audit: no file/network/subprocess/exec surface.

def test_no_forbidden_call_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    forbidden = (
        "open(", "write_text(", "write_bytes(", ".write(", "json.dump(",
        "import subprocess", "from subprocess", "Popen", "os.system",
        "import socket", "socket.socket", "urllib", "requests", "httpx",
        "http.client", "asyncio", "place_order", "submit_order",
        "create_order", "cancel_order", "ccxt", "freqtrade", "paper_trade",
        "live_trade", "autopilot(", ".upload(", "datetime.", "time.time(",
        "random.", "subprocess.run", "check_output",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


# 9 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _contract()
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _contract()
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE["automation_enabled"]
        is False
    )


# 10 -- a READY active gate activates the implementation contract.

def test_ready_gate_activates_contract():
    c = _contract()
    assert c["fake_dry_walk_implementation_contract_active"] is True
    assert (
        c["fake_dry_walk_implementation_state"]
        == "FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_ACTIVE"
    )
    assert c["fake_dry_walk_operator_review_gate_active"] is True
    assert (
        c["fake_dry_walk_operator_review_gate_decision"]
        == "READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"
    )
    assert (
        c["fake_dry_walk_operator_review_gate_next_gate"]
        == "FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED"
    )
    assert (
        c["next_gate"] == "FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED"
    )


# 11 -- a non-active (awaiting) gate does not activate the contract.

def test_awaiting_gate_does_not_activate():
    c = _contract(_gate())  # no operator decision -> AWAIT_OPERATOR_DECISION
    assert c["fake_dry_walk_implementation_contract_active"] is False
    assert (
        c["fake_dry_walk_implementation_state"]
        == "FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_BLOCKED"
    )
    assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE"


# 12 -- non-READY operator decisions never activate the contract.

def test_non_ready_decisions_never_activate():
    for decision in (
        OPERATOR_DECISION_NEEDS_MORE_SPEC,
        OPERATOR_DECISION_PARK,
        OPERATOR_DECISION_REJECT,
        None,
        "BOGUS_DECISION",
    ):
        c = _contract(_gate(decision))
        assert c["fake_dry_walk_implementation_contract_active"] is False
        assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE"


# 13 -- a blocked (inactive) upstream gate does not activate.

def test_blocked_gate_does_not_activate():
    blocked_gate = build_fake_dry_walk_operator_review_gate(_blocked_dry_walk())
    c = _contract(blocked_gate)
    assert c["fake_dry_walk_implementation_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE"


# 14 -- READY decision but wrong upstream next_gate does not activate.

def test_ready_but_wrong_next_gate_does_not_activate():
    import copy
    g = copy.deepcopy(_ready_gate())
    g["next_gate"] = "SOMETHING_ELSE"
    c = _contract(g)
    assert c["fake_dry_walk_implementation_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE"


# 15 -- gate active flag off does not activate even with READY decision.

def test_gate_inactive_flag_does_not_activate():
    import copy
    g = copy.deepcopy(_ready_gate())
    g["fake_dry_walk_operator_review_gate_active"] = False
    c = _contract(g)
    assert c["fake_dry_walk_implementation_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE"


# 16 -- malformed gate never raises and never activates.

def test_malformed_gate_no_raise():
    for bad in (None, 42, "nope", {},
                {"fake_dry_walk_operator_review_gate_active": True}, []):
        c = build_fake_dry_walk_implementation_contract(bad)
        assert c["fake_dry_walk_implementation_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 17 -- implementation scope is exactly the six-label tuple.

def test_implementation_scope_exact():
    assert tuple(IMPLEMENTATION_SCOPE) == _EXPECTED_SCOPE
    c = _contract()
    assert tuple(c["implementation_scope"]) == _EXPECTED_SCOPE


# 18 -- allowed in-memory inputs are fake/placeholder-only.

def test_allowed_inputs_are_fake_placeholder_only():
    assert len(ALLOWED_IN_MEMORY_INPUTS) >= 1
    for x in ALLOWED_IN_MEMORY_INPUTS:
        assert "fake" in x and "placeholder" in x
    c = _contract()
    assert tuple(c["allowed_in_memory_inputs"]) == tuple(
        ALLOWED_IN_MEMORY_INPUTS)


# 19 -- allowed in-memory outputs are fake/placeholder-only.

def test_allowed_outputs_are_fake_placeholder_only():
    assert len(ALLOWED_IN_MEMORY_OUTPUTS) >= 1
    for x in ALLOWED_IN_MEMORY_OUTPUTS:
        assert "fake" in x and "placeholder" in x
    c = _contract()
    assert tuple(c["allowed_in_memory_outputs"]) == tuple(
        ALLOWED_IN_MEMORY_OUTPUTS)


# 20 -- the four shape contracts (fn/stage/trace/packet) are present + labels.

def test_shape_contracts_present():
    c = _contract()
    assert len(DRY_WALK_FUNCTION_CONTRACT) >= 1
    assert len(STAGE_WALK_CONTRACT) >= 1
    assert len(TRACE_RECORD_CONTRACT) >= 1
    assert len(OPERATOR_REVIEW_PACKET_CONTRACT) >= 1
    assert tuple(c["dry_walk_function_contract"]) == tuple(
        DRY_WALK_FUNCTION_CONTRACT)
    assert tuple(c["stage_walk_contract"]) == tuple(STAGE_WALK_CONTRACT)
    assert tuple(c["trace_record_contract"]) == tuple(TRACE_RECORD_CONTRACT)
    assert tuple(c["operator_review_packet_contract"]) == tuple(
        OPERATOR_REVIEW_PACKET_CONTRACT)


# 21 -- prohibited real artifact references include the named real artifacts.

def test_prohibited_real_artifact_references():
    refs = set(PROHIBITED_REAL_ARTIFACT_REFERENCES)
    for item in _REQUIRED_PROHIBITED_REFS:
        assert item in refs, item
    c = _contract()
    assert set(c["prohibited_real_artifact_references"]) == refs


# 22 -- prohibited runtime side effects include the named side effects.

def test_prohibited_runtime_side_effects():
    fx = set(PROHIBITED_RUNTIME_SIDE_EFFECTS)
    for item in _REQUIRED_PROHIBITED_FX:
        assert item in fx, item
    c = _contract()
    assert set(c["prohibited_runtime_side_effects"]) == fx


# 23 -- placeholder-only guard holds for the contract.

def test_placeholder_only_guard_holds():
    c = _contract()
    guard = c["placeholder_only_guard"]
    assert guard["all_inputs_placeholder_only"] is True
    assert guard["all_outputs_placeholder_only"] is True
    assert guard["no_real_artifact_reference"] is True
    assert guard["guard_holds"] is True


# 24 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    c = _contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 25 -- no authorization flag can become True (any state).

def test_authorization_flags_always_false():
    contracts = [
        _contract(),
        _contract(_gate()),
        _contract(_gate(OPERATOR_DECISION_REJECT)),
        _contract(build_fake_dry_walk_operator_review_gate(
            _blocked_dry_walk())),
    ]
    for c in contracts:
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["stage"] == "PLAN_ONLY"
        assert c["mode"] == "RESEARCH_ONLY"


# 26 -- even an active contract authorizes no data/runtime-state surface.

def test_active_contract_authorizes_no_runtime_state():
    c = _contract()
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["automation_enabled"] is False
    assert "pipeline_execution" in c["blocked_capabilities"]
    assert "runtime_state_write" in c["blocked_capabilities"]
    assert "dry_walk_execution" in c["blocked_capabilities"]
    assert "dry_walk_implementation_execution" in c["blocked_capabilities"]


# 27 -- the embedded upstream gate is preserved.

def test_upstream_gate_embedded():
    g = _ready_gate()
    c = build_fake_dry_walk_implementation_contract(g)
    assert c["fake_dry_walk_operator_review_gate"]["schema_version"] == (
        g["schema_version"]
    )
    assert c["fake_dry_walk_operator_review_gate"]["read_only"] is True


# 28 -- validate passes for a contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _contract()
    v = validate_fake_dry_walk_implementation_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_fake_dry_walk_implementation_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert (
        validate_fake_dry_walk_implementation_contract(bad2)["valid"] is False
    )

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert (
        validate_fake_dry_walk_implementation_contract(bad3)["valid"] is False
    )

    bad4 = copy.deepcopy(c)
    bad4["implementation_scope"] = ("only_one",)
    assert (
        validate_fake_dry_walk_implementation_contract(bad4)["valid"] is False
    )

    bad5 = copy.deepcopy(c)
    bad5["allowed_in_memory_inputs"] = ()
    assert (
        validate_fake_dry_walk_implementation_contract(bad5)["valid"] is False
    )

    bad6 = copy.deepcopy(c)
    bad6["prohibited_runtime_side_effects"] = ()
    assert (
        validate_fake_dry_walk_implementation_contract(bad6)["valid"] is False
    )

    bad7 = copy.deepcopy(c)
    bad7["placeholder_only_guard"] = {"guard_holds": False}
    assert (
        validate_fake_dry_walk_implementation_contract(bad7)["valid"] is False
    )


# 29 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_contract())
    c.pop("validation", None)
    v = validate_fake_dry_walk_implementation_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 30 -- a blocked contract still validates (template safety, not activation).

def test_blocked_contract_still_validates():
    c = _contract(_gate())  # awaiting -> blocked
    v = validate_fake_dry_walk_implementation_contract(c)
    assert v["valid"] is True
    assert c["fake_dry_walk_implementation_contract_active"] is False


# 31 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_template_only_and_execution_free():
    c = _contract()
    md = render_fake_dry_walk_implementation_contract_markdown(c)
    assert isinstance(md, str) and md
    assert (
        "# Strategy Factory Fake Dry Walk Implementation Contract" in md
    )
    assert "Template only" in md
    assert "fake-dry-walk-implementation-contract-only" in md
    assert "not-implemented-yet" in md
    assert "planning-only" in md
    assert "placeholder-only" in md
    assert "no-runtime-state-write" in md
    assert "research-only" in md
    assert "execution-free" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Fake dry walk implementation contract active: True" in md
    assert (
        "Next gate: FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED" in md
    )
    assert "## Source Reference" in md
    assert "## Implementation Scope" in md
    assert "## Allowed In Memory Inputs" in md
    assert "## Allowed In Memory Outputs" in md
    assert "## Dry Walk Function Contract" in md
    assert "## Stage Walk Contract" in md
    assert "## Trace Record Contract" in md
    assert "## Operator Review Packet Contract" in md
    assert "## Placeholder Only Guard" in md
    assert "## Prohibited Real Artifact References" in md
    assert "## Prohibited Runtime Side Effects" in md
    assert "## Blocked Capabilities" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 32 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 33 -- module references no real Crypto-D1 dataset path. (The docstring and
# the PROHIBITED_REAL_ARTIFACT_REFERENCES tuple legally NAME forbidden tokens,
# so we only assert the real dataset path form is absent, not the bare tokens.)

def test_no_real_artifact_path_in_source():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "Crypto-D1/" not in src
    assert "data/Crypto-D1" not in src
    assert "datasets/" not in src


# 34 -- prose verb audit over notes / source / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _contract()

    texts.extend(str(s) for s in c["operator_notes"])
    texts.append(str(c["source_operator_review_gate_reference_placeholder"]))

    md = render_fake_dry_walk_implementation_contract_markdown(c)
    for ln in md.splitlines():
        stripped = ln.lstrip()
        # skip headings, backtick key/value bullets, and `Label: value`
        # metadata header lines -- those are DATA / type descriptors, not
        # narrative prose. The self-descriptive safety banner is a metadata
        # header line and is skipped here too.
        if stripped.startswith("#") or stripped.startswith("- `"):
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


# 35 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 36 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_fake_dry_walk_implementation_contract.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_fake_dry_walk_implementation_contract.py"'
        in src
    )


# 37 -- Bundle 31 regression import still works.

def test_bundle31_regression_import_still_works():
    from sparta_commander.strategy_factory_fake_dry_walk_operator_review_gate import (  # noqa: E501
        build_fake_dry_walk_operator_review_gate as build31,
    )
    r = build31({})
    assert r["executes"] is False
    assert r["read_only"] is True
    assert r["fake_dry_walk_operator_review_gate_active"] is False


# 38 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
