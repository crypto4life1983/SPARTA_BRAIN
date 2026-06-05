"""Bundle 31 tests for the Strategy Factory Fake Dry Walk Operator Review Gate
template v1 (informational, read-only, planning/template-only, FAKE artifacts
only -- NO operator-review run, NO dry walk, NO smoke-test run, NO fake pipeline
run, NO runtime state write, NO orchestration, NO research, NO data access).

Bundle 31's production module imports Bundles 11-30 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 31 spec):
- module imports cleanly + public API limited to expected names,
- schema / label / status / state / gate / decision constants pinned,
- pure stdlib import-root audit + forbidden-surface audit,
- all 14 posture keys present + all False + keys match Bundle 30,
- posture is mutation-isolated (fresh dicts),
- activates only when the Bundle 30 fake-artifact dry walk contract is active
  with next_gate FAKE_ARTIFACT_DRY_WALK_OPERATOR_REVIEW_REQUIRED,
- blocked / wrong-gate / inactive / malformed never activate, never raise,
- allowed operator decisions are exactly the expected four,
- READY decision maps to FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED,
- NEEDS_MORE_SPEC / PARK / REJECT / missing decision never unlock
  implementation,
- no execution/data/backtest/broker/upload/autopilot/live/dashboard-runtime/
  ledger-write/runtime-state flag True,
- validate passes + detects failure modes; validation not self-required,
- markdown says fake-dry-walk-operator-review-gate-only + planning-only +
  placeholder-only + no-runtime-state-write + research-only + execution-free,
  writes nothing,
- prose verb audit over rejection / notes / source / expiry / markdown prose,
- scoped dirty-tree guard, Bundle 11-30 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_fake_dry_walk_operator_review_gate import (  # noqa: E501
    DRY_WALK_OPERATOR_REVIEW_GATE_SCHEMA_VERSION,
    DEFAULT_DRY_WALK_OPERATOR_REVIEW_GATE_LABEL,
    DRY_WALK_OPERATOR_REVIEW_GATE_STATUS,
    DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE,
    GATE_STATE_ACTIVE,
    GATE_STATE_BLOCKED,
    OPERATOR_DECISION_NEEDS_MORE_SPEC,
    OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT,
    OPERATOR_DECISION_PARK,
    OPERATOR_DECISION_REJECT,
    ALLOWED_OPERATOR_DECISIONS,
    NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED,
    NEXT_GATE_FAKE_DRY_WALK_SPEC_FIX_REQUIRED,
    NEXT_GATE_FAKE_DRY_WALK_PARKED,
    NEXT_GATE_FAKE_DRY_WALK_REJECTED,
    NEXT_GATE_AWAIT_OPERATOR_DECISION,
    NEXT_GATE_AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT,
    REQUIRED_OPERATOR_REVIEW_FIELDS,
    REQUIRED_SAFETY_ATTESTATION_FIELDS,
    REJECTION_CONDITIONS,
    build_fake_dry_walk_operator_review_gate,
    validate_fake_dry_walk_operator_review_gate,
    render_fake_dry_walk_operator_review_gate_markdown,
)
import sparta_commander.strategy_factory_fake_dry_walk_operator_review_gate as GT
from sparta_commander.strategy_factory_fake_artifact_dry_walk_contract import (
    DRY_WALK_CONTRACT_SAFETY_POSTURE,
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
    / "strategy_factory_fake_dry_walk_operator_review_gate.py"
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
    "runtime_state_write",
)

_EXPECTED_DECISIONS = (
    "NEEDS_MORE_SPEC",
    "READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT",
    "PARK",
    "REJECT",
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
    """A Bundle 30 fake-artifact dry walk contract that is active."""
    smoke = build_fake_artifact_smoke_test_contract(_ready_closure())
    return build_fake_artifact_dry_walk_contract(smoke)


def _blocked_dry_walk() -> dict:
    """A Bundle 30 fake-artifact dry walk contract that is NOT active."""
    smoke = build_fake_artifact_smoke_test_contract(_blocked_closure())
    return build_fake_artifact_dry_walk_contract(smoke)


def _gate(decision=None) -> dict:
    return build_fake_dry_walk_operator_review_gate(
        _active_dry_walk(), operator_decision=decision)


def _expected_public() -> set[str]:
    return {
        "DRY_WALK_OPERATOR_REVIEW_GATE_SCHEMA_VERSION",
        "DEFAULT_DRY_WALK_OPERATOR_REVIEW_GATE_LABEL",
        "DRY_WALK_OPERATOR_REVIEW_GATE_STATUS",
        "DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE",
        "GATE_STATE_ACTIVE",
        "GATE_STATE_BLOCKED",
        "OPERATOR_DECISION_NEEDS_MORE_SPEC",
        "OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT",
        "OPERATOR_DECISION_PARK",
        "OPERATOR_DECISION_REJECT",
        "ALLOWED_OPERATOR_DECISIONS",
        "NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED",
        "NEXT_GATE_FAKE_DRY_WALK_SPEC_FIX_REQUIRED",
        "NEXT_GATE_FAKE_DRY_WALK_PARKED",
        "NEXT_GATE_FAKE_DRY_WALK_REJECTED",
        "NEXT_GATE_AWAIT_OPERATOR_DECISION",
        "NEXT_GATE_AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT",
        "REQUIRED_OPERATOR_REVIEW_FIELDS",
        "REQUIRED_SAFETY_ATTESTATION_FIELDS",
        "REJECTION_CONDITIONS",
        "build_fake_dry_walk_operator_review_gate",
        "validate_fake_dry_walk_operator_review_gate",
        "render_fake_dry_walk_operator_review_gate_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(GT.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(GT, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        DRY_WALK_OPERATOR_REVIEW_GATE_SCHEMA_VERSION
        == "strategy_factory_fake_dry_walk_operator_review_gate.v1"
    )


# 3 -- label / status pinned.

def test_label_and_status_pinned():
    assert (
        DEFAULT_DRY_WALK_OPERATOR_REVIEW_GATE_LABEL
        == "Strategy Factory Fake Dry Walk Operator Review Gate"
    )
    assert (
        DRY_WALK_OPERATOR_REVIEW_GATE_STATUS
        == "READ_ONLY_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE"
    )


# 4 -- state / gate / decision constants pinned.

def test_state_and_gate_constants_pinned():
    assert GATE_STATE_ACTIVE == "FAKE_DRY_WALK_OPERATOR_REVIEW_GATE_ACTIVE"
    assert GATE_STATE_BLOCKED == "FAKE_DRY_WALK_OPERATOR_REVIEW_GATE_BLOCKED"
    assert (
        NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED
        == "FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED"
    )
    assert (
        NEXT_GATE_FAKE_DRY_WALK_SPEC_FIX_REQUIRED
        == "FAKE_DRY_WALK_SPEC_FIX_REQUIRED"
    )
    assert NEXT_GATE_FAKE_DRY_WALK_PARKED == "FAKE_DRY_WALK_PARKED"
    assert NEXT_GATE_FAKE_DRY_WALK_REJECTED == "FAKE_DRY_WALK_REJECTED"
    assert NEXT_GATE_AWAIT_OPERATOR_DECISION == "AWAIT_OPERATOR_DECISION"
    assert (
        NEXT_GATE_AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT
        == "AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT"
    )


# 5 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 6 -- posture keys match Bundle 30.

def test_posture_keys_match_bundle30():
    assert (
        set(DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE.keys())
        == set(DRY_WALK_CONTRACT_SAFETY_POSTURE.keys())
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
    a = _gate()
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _gate()
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE["automation_enabled"]
        is False
    )


# 10 -- active dry walk (correct next_gate) activates the gate.

def test_active_dry_walk_activates_gate():
    c = _gate()
    assert c["fake_dry_walk_operator_review_gate_active"] is True
    assert (
        c["fake_dry_walk_operator_review_gate_state"]
        == "FAKE_DRY_WALK_OPERATOR_REVIEW_GATE_ACTIVE"
    )
    assert c["fake_artifact_dry_walk_contract_active"] is True
    assert (
        c["fake_artifact_dry_walk_next_gate"]
        == "FAKE_ARTIFACT_DRY_WALK_OPERATOR_REVIEW_REQUIRED"
    )
    # no decision yet -> awaiting the operator
    assert c["next_gate"] == "AWAIT_OPERATOR_DECISION"


# 11 -- a blocked (inactive) dry walk does not activate the gate.

def test_blocked_dry_walk_does_not_activate():
    c = build_fake_dry_walk_operator_review_gate(_blocked_dry_walk())
    assert c["fake_dry_walk_operator_review_gate_active"] is False
    assert (
        c["fake_dry_walk_operator_review_gate_state"]
        == "FAKE_DRY_WALK_OPERATOR_REVIEW_GATE_BLOCKED"
    )
    assert c["next_gate"] == "AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT"


# 12 -- active dry walk but wrong next_gate does not activate the gate.

def test_active_dry_walk_wrong_gate_does_not_activate():
    import copy
    dw = copy.deepcopy(_active_dry_walk())
    dw["next_gate"] = "SOMETHING_ELSE"
    c = build_fake_dry_walk_operator_review_gate(
        dw,
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
        ),
    )
    assert c["fake_dry_walk_operator_review_gate_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT"


# 13 -- inactive dry walk flag does not activate even with READY decision.

def test_inactive_dry_walk_flag_does_not_activate():
    import copy
    dw = copy.deepcopy(_active_dry_walk())
    dw["fake_artifact_dry_walk_contract_active"] = False
    c = build_fake_dry_walk_operator_review_gate(
        dw,
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
        ),
    )
    assert c["fake_dry_walk_operator_review_gate_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT"


# 14 -- malformed dry walk never raises and never activates.

def test_malformed_dry_walk_no_raise():
    for bad in (None, 42, "nope", {},
                {"fake_artifact_dry_walk_contract_active": True}, []):
        c = build_fake_dry_walk_operator_review_gate(bad)
        assert c["fake_dry_walk_operator_review_gate_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 15 -- allowed operator decisions are exactly the expected four.

def test_allowed_operator_decisions_exact_set():
    assert tuple(ALLOWED_OPERATOR_DECISIONS) == _EXPECTED_DECISIONS
    c = _gate()
    assert tuple(c["allowed_operator_decisions"]) == _EXPECTED_DECISIONS
    assert OPERATOR_DECISION_NEEDS_MORE_SPEC == "NEEDS_MORE_SPEC"
    assert (
        OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
        == "READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"
    )
    assert OPERATOR_DECISION_PARK == "PARK"
    assert OPERATOR_DECISION_REJECT == "REJECT"


# 16 -- READY decision maps to FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED.

def test_ready_decision_unlocks_implementation_gate():
    c = _gate(
        OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT)
    assert c["fake_dry_walk_operator_review_gate_active"] is True
    assert c["operator_decision"] == (
        "READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"
    )
    assert c["next_gate"] == "FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED"


# 17 -- non-ready decisions never unlock the implementation gate.

def test_non_ready_decisions_never_unlock_implementation():
    mapping = {
        OPERATOR_DECISION_NEEDS_MORE_SPEC: "FAKE_DRY_WALK_SPEC_FIX_REQUIRED",
        OPERATOR_DECISION_PARK: "FAKE_DRY_WALK_PARKED",
        OPERATOR_DECISION_REJECT: "FAKE_DRY_WALK_REJECTED",
        None: "AWAIT_OPERATOR_DECISION",
        "BOGUS_DECISION": "AWAIT_OPERATOR_DECISION",
    }
    for decision, expected_gate in mapping.items():
        c = _gate(decision)
        assert c["fake_dry_walk_operator_review_gate_active"] is True
        assert c["next_gate"] == expected_gate
        assert (
            c["next_gate"]
            != "FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED"
        )


# 18 -- unknown decision is normalized away (operator_decision left empty).

def test_unknown_decision_normalized_to_empty():
    c = _gate("BOGUS_DECISION")
    assert c["operator_decision"] == ""
    assert c["next_gate"] == "AWAIT_OPERATOR_DECISION"


# 19 -- no authorization flag can become True (any decision / state).

def test_authorization_flags_always_false():
    contracts = [
        _gate(),
        _gate(OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT),
        _gate(OPERATOR_DECISION_REJECT),
        build_fake_dry_walk_operator_review_gate(_blocked_dry_walk()),
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


# 20 -- even the READY decision authorizes no data/runtime-state surface.

def test_ready_decision_authorizes_no_runtime_state():
    c = _gate(
        OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT)
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["automation_enabled"] is False
    assert "pipeline_execution" in c["blocked_capabilities"]
    assert "runtime_state_write" in c["blocked_capabilities"]
    assert "dry_walk_execution" in c["blocked_capabilities"]
    assert "operator_review_gate_execution" in c["blocked_capabilities"]


# 21 -- required operator review + safety attestation fields present.

def test_required_review_and_attestation_fields_present():
    c = _gate()
    assert tuple(c["required_operator_review_fields"]) == (
        tuple(REQUIRED_OPERATOR_REVIEW_FIELDS)
    )
    assert tuple(c["required_safety_attestation_fields"]) == (
        tuple(REQUIRED_SAFETY_ATTESTATION_FIELDS)
    )
    assert len(REQUIRED_OPERATOR_REVIEW_FIELDS) >= 1
    assert len(REQUIRED_SAFETY_ATTESTATION_FIELDS) >= 1
    for x in (tuple(REQUIRED_OPERATOR_REVIEW_FIELDS)
              + tuple(REQUIRED_SAFETY_ATTESTATION_FIELDS)):
        assert "placeholder" in x


# 22 -- rejection conditions present.

def test_rejection_conditions_present():
    c = _gate()
    assert tuple(c["rejection_conditions"]) == tuple(REJECTION_CONDITIONS)
    assert len(REJECTION_CONDITIONS) >= 1


# 23 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    c = _gate()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 24 -- the embedded dry walk contract is preserved.

def test_dry_walk_contract_embedded():
    dw = _active_dry_walk()
    c = build_fake_dry_walk_operator_review_gate(dw)
    assert c["fake_artifact_dry_walk_contract"]["schema_version"] == (
        dw["schema_version"]
    )
    assert c["fake_artifact_dry_walk_contract"]["read_only"] is True


# 25 -- validate passes for a gate contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _gate(
        OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT)
    v = validate_fake_dry_walk_operator_review_gate(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_fake_dry_walk_operator_review_gate(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_fake_dry_walk_operator_review_gate(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_fake_dry_walk_operator_review_gate(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["allowed_operator_decisions"] = ("ONLY_ONE",)
    assert validate_fake_dry_walk_operator_review_gate(bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["required_safety_attestation_fields"] = ()
    assert validate_fake_dry_walk_operator_review_gate(bad5)["valid"] is False

    bad6 = copy.deepcopy(c)
    bad6["rejection_conditions"] = ()
    assert validate_fake_dry_walk_operator_review_gate(bad6)["valid"] is False


# 26 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_gate())
    c.pop("validation", None)
    v = validate_fake_dry_walk_operator_review_gate(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 27 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_template_only_and_execution_free():
    c = _gate(
        OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT)
    md = render_fake_dry_walk_operator_review_gate_markdown(c)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Fake Dry Walk Operator Review Gate" in md
    assert "Template only" in md
    assert "fake-dry-walk-operator-review-gate-only" in md
    assert "planning-only" in md
    assert "placeholder-only" in md
    assert "no-runtime-state-write" in md
    assert "research-only" in md
    assert "execution-free" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Fake dry walk operator review gate active: True" in md
    assert (
        "Next gate: FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED" in md
    )
    assert "## Source Reference" in md
    assert "## Allowed Operator Decisions" in md
    assert "## Required Operator Review Fields" in md
    assert "## Required Safety Attestation Fields" in md
    assert "## Approval Expiry" in md
    assert "## Rejection Conditions" in md
    assert "## Blocked Capabilities" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 28 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 29 -- module references no real Crypto-D1 dataset path. (The docstring may
# legally NAME forbidden tokens in its "references no ..." safety statement, so
# we only assert the real dataset path form is absent, not the bare tokens.)

def test_no_real_artifact_path_in_source():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "Crypto-D1/" not in src
    assert "data/Crypto-D1" not in src
    assert "datasets/" not in src


# 30 -- prose verb audit over rejection / notes / source / expiry / markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _gate(
        OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT)

    texts.extend(str(s) for s in c["rejection_conditions"])
    texts.extend(str(s) for s in c["operator_notes"])
    texts.append(str(c["source_fake_dry_walk_contract_reference_placeholder"]))
    texts.append(str(c["approval_expiry_placeholder"]))

    md = render_fake_dry_walk_operator_review_gate_markdown(c)
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


# 31 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 32 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_fake_dry_walk_operator_review_gate.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_fake_dry_walk_operator_review_gate.py"'
        in src
    )


# 33 -- Bundle 30 regression import still works.

def test_bundle30_regression_import_still_works():
    from sparta_commander.strategy_factory_fake_artifact_dry_walk_contract import (  # noqa: E501
        build_fake_artifact_dry_walk_contract as build30,
    )
    r = build30({})
    assert r["executes"] is False
    assert r["read_only"] is True
    assert r["fake_artifact_dry_walk_contract_active"] is False


# 34 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
