"""Bundle 29 tests for the Strategy Factory Fake Artifact Smoke Test Contract
template v1 (informational, read-only, planning/template-only, FAKE artifacts
only -- NO smoke-test run, NO fake pipeline run, NO dry-walk, NO runtime state
write, NO orchestration, NO research, NO data access).

Bundle 29's production module imports Bundles 11-28 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 29 spec):
- module imports cleanly + public API limited to expected names,
- pure stdlib import-root audit + forbidden-surface audit,
- all 14 posture keys present + all False + keys match Bundle 28,
- posture is mutation-isolated (fresh dicts),
- activates only when the Bundle 28 closure report is active with
  final_backbone_status STRATEGY_FACTORY_V1_BACKBONE_COMPLETE,
  next_gate PAUSE_AND_OPERATOR_REVIEW, and recommended_next_phase
  FAKE_ARTIFACT_SMOKE_TEST_PLANNING_ONLY,
- blocked / wrong-gate / wrong-phase / inactive closure never activate,
  never raise,
- next_gate defaults to FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED when active,
- all fake input / output artifacts present, all 10 stages in order,
  all trace fields, all operator review fields present,
- placeholder-only guard flags real artifact names,
- no execution/data/backtest/broker/upload/autopilot/live/dashboard-runtime/
  ledger-write/runtime-state flag True,
- validate passes + detects failure modes; validation not self-required,
- markdown says fake-artifact-smoke-test-contract-only + planning-only +
  placeholder-only + no-runtime-state-write + research-only + execution-free,
  writes nothing,
- prose verb audit over pass / fail / notes / source / markdown prose,
- scoped dirty-tree guard, Bundle 11-28 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_fake_artifact_smoke_test_contract import (  # noqa: E501
    SMOKE_TEST_CONTRACT_SCHEMA_VERSION,
    DEFAULT_SMOKE_TEST_CONTRACT_LABEL,
    SMOKE_TEST_CONTRACT_STATUS,
    SMOKE_TEST_CONTRACT_SAFETY_POSTURE,
    SMOKE_TEST_STATE_ACTIVE,
    SMOKE_TEST_STATE_BLOCKED,
    NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED,
    NEXT_GATE_AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW,
    FAKE_INPUT_ARTIFACTS_REQUIRED,
    FAKE_OUTPUT_ARTIFACTS_EXPECTED,
    FAKE_PIPELINE_STAGE_SEQUENCE,
    EXPECTED_TRACE_FIELDS,
    EXPECTED_OPERATOR_REVIEW_FIELDS,
    FORBIDDEN_REAL_ARTIFACT_TOKENS,
    build_fake_artifact_smoke_test_contract,
    validate_fake_artifact_smoke_test_contract,
    render_fake_artifact_smoke_test_contract_markdown,
)
import sparta_commander.strategy_factory_fake_artifact_smoke_test_contract as ST
from sparta_commander.strategy_factory_backbone_closure_report import (
    BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE,
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
    / "strategy_factory_fake_artifact_smoke_test_contract.py"
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
    "runtime_safety_flag_write", "pipeline_execution", "runtime_state_write",
)

_REQUIRED_INPUTS = (
    "fake_idea_record_placeholder",
    "fake_protocol_draft_placeholder",
    "fake_data_contract_placeholder",
    "fake_data_qa_report_placeholder",
)

_REQUIRED_OUTPUTS = (
    "fake_summary_metrics_placeholder",
    "fake_risk_metrics_placeholder",
    "fake_trace_manifest_placeholder",
    "fake_operator_review_packet_placeholder",
)

_REQUIRED_STAGES = (
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

_REQUIRED_TRACE = (
    "trace_id_placeholder",
    "stage_name_placeholder",
    "input_digest_placeholder",
    "output_digest_placeholder",
    "stage_status_placeholder",
)

_REQUIRED_REVIEW = (
    "reviewer_identity_placeholder",
    "stage_assessment_placeholder",
    "blocking_findings_placeholder",
    "human_sign_off_placeholder",
)

_REAL_ARTIFACT_NAMES = (
    "Crypto-D1",
    "data/Crypto-D1/MNQ_1d.csv",
    "qa_report.json",
    "manifest.json",
    "CHECKSUMS.txt",
    "FREEZE_RECORD.txt",
    "fees.json",
    "baseline_equity_curve",
    "datasets/MNQ.parquet",
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
    """A Bundle 28 backbone closure report that is active + complete."""
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
    """A Bundle 28 backbone closure report that is NOT active."""
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


def _active_contract() -> dict:
    return build_fake_artifact_smoke_test_contract(_ready_closure())


def _expected_public() -> set[str]:
    return {
        "SMOKE_TEST_CONTRACT_SCHEMA_VERSION",
        "DEFAULT_SMOKE_TEST_CONTRACT_LABEL",
        "SMOKE_TEST_CONTRACT_STATUS",
        "SMOKE_TEST_CONTRACT_SAFETY_POSTURE",
        "SMOKE_TEST_STATE_ACTIVE",
        "SMOKE_TEST_STATE_BLOCKED",
        "NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED",
        "NEXT_GATE_AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW",
        "FAKE_INPUT_ARTIFACTS_REQUIRED",
        "FAKE_OUTPUT_ARTIFACTS_EXPECTED",
        "FAKE_PIPELINE_STAGE_SEQUENCE",
        "EXPECTED_TRACE_FIELDS",
        "EXPECTED_OPERATOR_REVIEW_FIELDS",
        "FORBIDDEN_REAL_ARTIFACT_TOKENS",
        "build_fake_artifact_smoke_test_contract",
        "validate_fake_artifact_smoke_test_contract",
        "render_fake_artifact_smoke_test_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(ST.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(ST, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        SMOKE_TEST_CONTRACT_SCHEMA_VERSION
        == "strategy_factory_fake_artifact_smoke_test_contract.v1"
    )


# 3 -- label / status pinned.

def test_label_and_status_pinned():
    assert (
        DEFAULT_SMOKE_TEST_CONTRACT_LABEL
        == "Strategy Factory Fake Artifact Smoke Test Contract"
    )
    assert (
        SMOKE_TEST_CONTRACT_STATUS
        == "READ_ONLY_FAKE_ARTIFACT_SMOKE_TEST_CONTRACT"
    )


# 4 -- state / gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        SMOKE_TEST_STATE_ACTIVE == "FAKE_ARTIFACT_SMOKE_TEST_CONTRACT_ACTIVE"
    )
    assert (
        SMOKE_TEST_STATE_BLOCKED == "FAKE_ARTIFACT_SMOKE_TEST_CONTRACT_BLOCKED"
    )
    assert (
        NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED
        == "FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED"
    )
    assert (
        NEXT_GATE_AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW
        == "AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW"
    )


# 5 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = SMOKE_TEST_CONTRACT_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 6 -- posture keys match Bundle 28.

def test_posture_keys_match_bundle28():
    assert (
        set(SMOKE_TEST_CONTRACT_SAFETY_POSTURE.keys())
        == set(BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE.keys())
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
    a = build_fake_artifact_smoke_test_contract(_ready_closure())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_fake_artifact_smoke_test_contract(_ready_closure())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        SMOKE_TEST_CONTRACT_SAFETY_POSTURE["automation_enabled"] is False
    )


# 10 -- active closure (complete + review gate + planning phase) activates.

def test_active_closure_activates():
    c = _active_contract()
    assert c["fake_artifact_smoke_test_contract_active"] is True
    assert (
        c["fake_artifact_smoke_test_state"]
        == "FAKE_ARTIFACT_SMOKE_TEST_CONTRACT_ACTIVE"
    )
    assert c["next_gate"] == "FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED"
    assert c["backbone_closure_report_active"] is True
    assert (
        c["backbone_closure_final_status"]
        == "STRATEGY_FACTORY_V1_BACKBONE_COMPLETE"
    )
    assert c["backbone_closure_next_gate"] == "PAUSE_AND_OPERATOR_REVIEW"
    assert (
        c["backbone_closure_recommended_next_phase"]
        == "FAKE_ARTIFACT_SMOKE_TEST_PLANNING_ONLY"
    )


# 11 -- a blocked (inactive) closure does not activate.

def test_blocked_closure_does_not_activate():
    c = build_fake_artifact_smoke_test_contract(_blocked_closure())
    assert c["fake_artifact_smoke_test_contract_active"] is False
    assert (
        c["fake_artifact_smoke_test_state"]
        == "FAKE_ARTIFACT_SMOKE_TEST_CONTRACT_BLOCKED"
    )
    assert c["next_gate"] == "AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW"


# 12 -- active closure but wrong next_gate does not activate.

def test_active_closure_wrong_gate_does_not_activate():
    import copy
    cl = copy.deepcopy(_ready_closure())
    cl["next_gate"] = "SOMETHING_ELSE"  # tamper: no longer operator review
    c = build_fake_artifact_smoke_test_contract(cl)
    assert c["fake_artifact_smoke_test_contract_active"] is False
    assert c["next_gate"] == "AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW"


# 13 -- active closure but wrong recommended phase does not activate.

def test_active_closure_wrong_phase_does_not_activate():
    import copy
    cl = copy.deepcopy(_ready_closure())
    cl["recommended_next_phase"] = "SOMETHING_ELSE"
    c = build_fake_artifact_smoke_test_contract(cl)
    assert c["fake_artifact_smoke_test_contract_active"] is False
    assert c["next_gate"] == "AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW"


# 14 -- active closure but wrong final status does not activate.

def test_active_closure_wrong_final_status_does_not_activate():
    import copy
    cl = copy.deepcopy(_ready_closure())
    cl["final_backbone_status"] = "STRATEGY_FACTORY_V1_BACKBONE_INCOMPLETE"
    c = build_fake_artifact_smoke_test_contract(cl)
    assert c["fake_artifact_smoke_test_contract_active"] is False
    assert c["next_gate"] == "AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW"


# 15 -- malformed closure never raises and never activates.

def test_malformed_closure_no_raise():
    for bad in (None, 42, "nope", {},
                {"backbone_closure_report_active": True}, []):
        c = build_fake_artifact_smoke_test_contract(bad)
        assert c["fake_artifact_smoke_test_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 16 -- no authorization flag can become True (active or blocked).

def test_authorization_flags_always_false():
    for c in (_active_contract(),
              build_fake_artifact_smoke_test_contract(_blocked_closure())):
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["stage"] == "PLAN_ONLY"
        assert c["mode"] == "RESEARCH_ONLY"


# 17 -- activation never sets a data/backtest/runtime-state flag or posture.

def test_active_does_not_authorize_data_or_runtime_state():
    c = _active_contract()
    assert c["fake_artifact_smoke_test_contract_active"] is True
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["backtest_enabled"] is False
    assert c["safety_posture"]["automation_enabled"] is False
    assert "pipeline_execution" in c["blocked_capabilities"]
    assert "runtime_state_write" in c["blocked_capabilities"]
    assert "smoke_test_execution" in c["blocked_capabilities"]
    assert "dry_walk_execution" in c["blocked_capabilities"]


# 18 -- all required fake input artifacts present (placeholder names).

def test_fake_input_artifacts_present():
    c = _active_contract()
    assert tuple(c["fake_input_artifacts_required"]) == _REQUIRED_INPUTS
    for x in c["fake_input_artifacts_required"]:
        assert "fake" in x and "placeholder" in x


# 19 -- all required fake output artifacts present (placeholder names).

def test_fake_output_artifacts_present():
    c = _active_contract()
    assert tuple(c["fake_output_artifacts_expected"]) == _REQUIRED_OUTPUTS
    for x in c["fake_output_artifacts_expected"]:
        assert "fake" in x and "placeholder" in x


# 20 -- all 10 stage names present, in order.

def test_stage_sequence_present_in_order():
    c = _active_contract()
    assert tuple(c["fake_pipeline_stage_sequence"]) == _REQUIRED_STAGES
    assert len(c["fake_pipeline_stage_sequence"]) == 10
    assert "dry_walk_orchestrator_review" in c["fake_pipeline_stage_sequence"]


# 21 -- all trace + operator review fields present.

def test_trace_and_review_fields_present():
    c = _active_contract()
    assert tuple(c["expected_trace_fields"]) == _REQUIRED_TRACE
    assert tuple(c["expected_operator_review_fields"]) == _REQUIRED_REVIEW


# 22 -- placeholder-only guard holds and flags any real artifact name.

def test_placeholder_only_guard_flags_real_names():
    c = _active_contract()
    guard = c["placeholder_only_guard"]
    assert guard["guard_holds"] is True
    assert guard["all_inputs_placeholder_only"] is True
    assert guard["all_outputs_placeholder_only"] is True
    assert guard["no_real_artifact_reference"] is True

    tokens = tuple(t.lower() for t in FORBIDDEN_REAL_ARTIFACT_TOKENS)
    # every real artifact name must be caught by at least one forbidden token
    for real in _REAL_ARTIFACT_NAMES:
        lowered = real.lower()
        assert any(tok in lowered for tok in tokens), real
    # the built-in fake names must NOT be caught by any forbidden token
    for name in (tuple(c["fake_input_artifacts_required"])
                 + tuple(c["fake_output_artifacts_expected"])
                 + tuple(c["fake_pipeline_stage_sequence"])):
        lowered = name.lower()
        assert not any(tok in lowered for tok in tokens), name


# 23 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    c = _active_contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 24 -- the embedded closure report is preserved.

def test_closure_report_embedded():
    cl = _ready_closure()
    c = build_fake_artifact_smoke_test_contract(cl)
    assert c["backbone_closure_report"]["schema_version"] == (
        cl["schema_version"]
    )
    assert c["backbone_closure_report"]["read_only"] is True


# 25 -- validate passes for an active contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _active_contract()
    v = validate_fake_artifact_smoke_test_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_fake_artifact_smoke_test_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_fake_artifact_smoke_test_contract(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_fake_artifact_smoke_test_contract(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["fake_input_artifacts_required"] = ()
    assert validate_fake_artifact_smoke_test_contract(bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["pass_criteria"] = ()
    assert validate_fake_artifact_smoke_test_contract(bad5)["valid"] is False

    bad6 = copy.deepcopy(c)
    bad6["placeholder_only_guard"] = {"guard_holds": False}
    assert validate_fake_artifact_smoke_test_contract(bad6)["valid"] is False


# 26 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_active_contract())
    c.pop("validation", None)
    v = validate_fake_artifact_smoke_test_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 27 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_template_only_and_execution_free():
    c = _active_contract()
    md = render_fake_artifact_smoke_test_contract_markdown(c)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Fake Artifact Smoke Test Contract" in md
    assert "Template only" in md
    assert "fake-artifact-smoke-test-contract-only" in md
    assert "planning-only" in md
    assert "placeholder-only" in md
    assert "no-runtime-state-write" in md
    assert "research-only" in md
    assert "execution-free" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Fake artifact smoke test contract active: True" in md
    assert "Next gate: FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED" in md
    assert "## Source Reference" in md
    assert "## Fake Input Artifacts Required" in md
    assert "## Fake Output Artifacts Expected" in md
    assert "## Fake Pipeline Stage Sequence" in md
    assert "## Expected Trace Fields" in md
    assert "## Expected Operator Review Fields" in md
    assert "## Pass Criteria" in md
    assert "## Fail Criteria" in md
    assert "## Placeholder Only Guard" in md
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


# 29 -- no artifact NAME is a real artifact (the guard token list may legally
# surface those strings, but no input/output/stage/trace/review name is real).

def test_no_real_artifact_name_in_any_collection():
    c = _active_contract()
    tokens = tuple(t.lower() for t in FORBIDDEN_REAL_ARTIFACT_TOKENS)
    names = (
        tuple(c["fake_input_artifacts_required"])
        + tuple(c["fake_output_artifacts_expected"])
        + tuple(c["fake_pipeline_stage_sequence"])
        + tuple(c["expected_trace_fields"])
        + tuple(c["expected_operator_review_fields"])
    )
    for name in names:
        lowered = name.lower()
        assert not any(tok in lowered for tok in tokens), name
    # the module names no real Crypto-D1 dataset path
    src = _MODPATH.read_text(encoding="utf-8")
    assert "Crypto-D1/" not in src


# 30 -- prose verb audit over pass / fail / notes / source / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _active_contract()

    texts.extend(str(s) for s in c["pass_criteria"])
    texts.extend(str(s) for s in c["fail_criteria"])
    texts.extend(str(s) for s in c["operator_notes"])
    texts.append(str(c["source_backbone_closure_reference_placeholder"]))

    md = render_fake_artifact_smoke_test_contract_markdown(c)
    for ln in md.splitlines():
        stripped = ln.lstrip()
        # skip headings, backtick key/value bullets, and `Label: value`
        # metadata header lines -- those are DATA / type descriptors, not
        # narrative prose. The self-descriptive safety banner ("Template
        # only: ... fake-artifact-smoke-test-contract-only ...") is a metadata
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
        '"sparta_commander/strategy_factory_fake_artifact_smoke_test_contract.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_fake_artifact_smoke_test_contract.py"'
        in src
    )


# 33 -- Bundle 28 regression import still works.

def test_bundle28_regression_import_still_works():
    from sparta_commander.strategy_factory_backbone_closure_report import (
        build_backbone_closure_report as build28,
    )
    r = build28(_blocked_closure_pipeline())
    assert r["executes"] is False
    assert r["read_only"] is True


def _blocked_closure_pipeline() -> dict:
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(draft)
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    orchestrator = build_dry_run_orchestrator_contract(runner)
    feed = build_dashboard_registry_feed_contract(orchestrator)
    ledger = build_decision_ledger_contract(feed)
    safety_gate = build_safety_kill_switch_contract(ledger)
    return build_end_to_end_fake_pipeline_contract(safety_gate)


# 34 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
