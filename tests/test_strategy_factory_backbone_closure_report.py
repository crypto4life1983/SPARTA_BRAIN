"""Bundle 28 (closure) tests for the Strategy Factory v1 Backbone Closure
Report template (informational, read-only, report/template-only -- NO Strategy
Factory run, NO fake pipeline run, NO runtime state write, NO orchestration, NO
research, NO data access).

Bundle 28's production module imports Bundles 11-27 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 28 spec):
- module imports cleanly + public API limited to expected names,
- schema version / label / status / state / gate / final-status / phase
  constants pinned,
- pure stdlib import-root audit + forbidden-surface audit,
- all 14 posture keys present + all False + keys match Bundle 27,
- posture is mutation-isolated (fresh dicts),
- activates only when end_to_end_fake_pipeline_contract_active True AND the
  pipeline next_gate is BACKBONE_CLOSURE_REPORT_REQUIRED,
- blocked / wrong-gate / malformed pipeline never activate, never raise,
- final_backbone_status is STRATEGY_FACTORY_V1_BACKBONE_COMPLETE when active,
- recommended_next_phase is FAKE_ARTIFACT_SMOKE_TEST_PLANNING_ONLY,
- next_gate defaults to PAUSE_AND_OPERATOR_REVIEW when active,
- completed_bundle_range references "Bundles 11-28",
- no execution/data/backtest/broker/upload/autopilot/live/dashboard-runtime/
  ledger-write/runtime-state flag True,
- the required report description fields present,
- blocked_capabilities include the required set (incl. pipeline_execution +
  runtime_state_write),
- validate passes + detects failure modes; validation not self-required,
- the embedded pipeline contract is preserved,
- markdown says backbone-closure-report-only + no-runtime-state-write +
  research-only + execution-free, writes nothing,
- prose verb audit over chain summary / next steps / operator notes / markdown,
- scoped dirty-tree guard, Bundle 11-27 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_backbone_closure_report import (
    BACKBONE_CLOSURE_REPORT_SCHEMA_VERSION,
    DEFAULT_BACKBONE_CLOSURE_REPORT_LABEL,
    BACKBONE_CLOSURE_REPORT_STATUS,
    BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE,
    BACKBONE_CLOSURE_STATE_ACTIVE,
    BACKBONE_CLOSURE_STATE_BLOCKED,
    FINAL_BACKBONE_STATUS_COMPLETE,
    RECOMMENDED_NEXT_PHASE,
    NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW,
    NEXT_GATE_AWAIT_END_TO_END_FAKE_PIPELINE_CONTRACT,
    build_backbone_closure_report,
    validate_backbone_closure_report,
    render_backbone_closure_report_markdown,
)
import sparta_commander.strategy_factory_backbone_closure_report as BC
from sparta_commander.strategy_factory_end_to_end_fake_pipeline_contract import (
    END_TO_END_FAKE_PIPELINE_CONTRACT_SAFETY_POSTURE,
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
    / "strategy_factory_backbone_closure_report.py"
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

_REQUIRED_REPORT_FIELDS = (
    "backbone_closure_report_active",
    "completed_bundle_range",
    "completed_contract_chain_summary",
    "final_backbone_status",
    "remaining_runtime_capabilities_blocked",
    "remaining_data_capabilities_blocked",
    "remaining_trading_capabilities_blocked",
    "human_operator_required_next_steps",
    "recommended_next_phase",
    "blocked_capabilities", "safety_posture", "next_gate", "operator_notes",
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


def _ready_pipeline() -> dict:
    """A Bundle 27 end-to-end fake pipeline contract that is active."""
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
    return build_end_to_end_fake_pipeline_contract(safety_gate)


def _blocked_pipeline() -> dict:
    """A Bundle 27 end-to-end fake pipeline contract that is NOT active."""
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
    return build_end_to_end_fake_pipeline_contract(safety_gate)


def _active_report() -> dict:
    return build_backbone_closure_report(_ready_pipeline())


def _expected_public() -> set[str]:
    return {
        "BACKBONE_CLOSURE_REPORT_SCHEMA_VERSION",
        "DEFAULT_BACKBONE_CLOSURE_REPORT_LABEL",
        "BACKBONE_CLOSURE_REPORT_STATUS",
        "BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE",
        "BACKBONE_CLOSURE_STATE_ACTIVE",
        "BACKBONE_CLOSURE_STATE_BLOCKED",
        "FINAL_BACKBONE_STATUS_COMPLETE",
        "RECOMMENDED_NEXT_PHASE",
        "NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW",
        "NEXT_GATE_AWAIT_END_TO_END_FAKE_PIPELINE_CONTRACT",
        "build_backbone_closure_report",
        "validate_backbone_closure_report",
        "render_backbone_closure_report_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(BC.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(BC, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        BACKBONE_CLOSURE_REPORT_SCHEMA_VERSION
        == "strategy_factory_backbone_closure_report.v1"
    )


# 3 -- label / status pinned.

def test_label_and_status_pinned():
    assert (
        DEFAULT_BACKBONE_CLOSURE_REPORT_LABEL
        == "Strategy Factory v1 Backbone Closure Report"
    )
    assert (
        BACKBONE_CLOSURE_REPORT_STATUS
        == "READ_ONLY_BACKBONE_CLOSURE_REPORT"
    )


# 4 -- state / final-status / phase / gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        BACKBONE_CLOSURE_STATE_ACTIVE == "BACKBONE_CLOSURE_REPORT_ACTIVE"
    )
    assert (
        BACKBONE_CLOSURE_STATE_BLOCKED == "BACKBONE_CLOSURE_REPORT_BLOCKED"
    )
    assert (
        FINAL_BACKBONE_STATUS_COMPLETE
        == "STRATEGY_FACTORY_V1_BACKBONE_COMPLETE"
    )
    assert (
        RECOMMENDED_NEXT_PHASE == "FAKE_ARTIFACT_SMOKE_TEST_PLANNING_ONLY"
    )
    assert (
        NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW == "PAUSE_AND_OPERATOR_REVIEW"
    )
    assert (
        NEXT_GATE_AWAIT_END_TO_END_FAKE_PIPELINE_CONTRACT
        == "AWAIT_END_TO_END_FAKE_PIPELINE_CONTRACT"
    )


# 5 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 6 -- posture keys match Bundle 27.

def test_posture_keys_match_bundle27():
    assert (
        set(BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE.keys())
        == set(END_TO_END_FAKE_PIPELINE_CONTRACT_SAFETY_POSTURE.keys())
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
    a = build_backbone_closure_report(_ready_pipeline())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_backbone_closure_report(_ready_pipeline())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE["automation_enabled"]
        is False
    )


# 10 -- active pipeline + BACKBONE_CLOSURE gate activates the report.

def test_active_pipeline_activates():
    r = _active_report()
    assert r["backbone_closure_report_active"] is True
    assert r["backbone_closure_state"] == "BACKBONE_CLOSURE_REPORT_ACTIVE"
    assert r["final_backbone_status"] == "STRATEGY_FACTORY_V1_BACKBONE_COMPLETE"
    assert r["recommended_next_phase"] == "FAKE_ARTIFACT_SMOKE_TEST_PLANNING_ONLY"
    assert r["next_gate"] == "PAUSE_AND_OPERATOR_REVIEW"
    assert r["end_to_end_fake_pipeline_contract_active"] is True
    assert (
        r["end_to_end_fake_pipeline_next_gate"]
        == "BACKBONE_CLOSURE_REPORT_REQUIRED"
    )


# 11 -- a blocked (inactive) pipeline does not activate.

def test_blocked_pipeline_does_not_activate():
    r = build_backbone_closure_report(_blocked_pipeline())
    assert r["backbone_closure_report_active"] is False
    assert r["backbone_closure_state"] == "BACKBONE_CLOSURE_REPORT_BLOCKED"
    assert (
        r["final_backbone_status"] == "STRATEGY_FACTORY_V1_BACKBONE_INCOMPLETE"
    )
    assert r["next_gate"] == "AWAIT_END_TO_END_FAKE_PIPELINE_CONTRACT"


# 12 -- active pipeline but wrong next_gate does not activate.

def test_active_pipeline_wrong_gate_does_not_activate():
    import copy
    p = copy.deepcopy(_ready_pipeline())
    p["next_gate"] = "SOMETHING_ELSE"  # tamper: no longer the closure gate
    r = build_backbone_closure_report(p)
    assert r["backbone_closure_report_active"] is False
    assert r["next_gate"] == "AWAIT_END_TO_END_FAKE_PIPELINE_CONTRACT"
    assert (
        r["final_backbone_status"] == "STRATEGY_FACTORY_V1_BACKBONE_INCOMPLETE"
    )


# 13 -- malformed pipeline never raises and never activates.

def test_malformed_pipeline_no_raise():
    for bad in (None, 42, "nope", {},
                {"end_to_end_fake_pipeline_contract_active": True}, []):
        r = build_backbone_closure_report(bad)
        assert r["backbone_closure_report_active"] is False
        assert r["read_only"] is True
        assert r["executes"] is False
        for flag in _AUTH_FLAGS:
            assert r[flag] is False


# 14 -- no authorization flag can become True (active or blocked).

def test_authorization_flags_always_false():
    for r in (_active_report(),
              build_backbone_closure_report(_blocked_pipeline())):
        for flag in _AUTH_FLAGS:
            assert r[flag] is False
        assert all(v is False for v in r["safety_posture"].values())
        assert r["executes"] is False
        assert r["read_only"] is True
        assert r["human_approval_required"] is True
        assert r["stage"] == "PLAN_ONLY"
        assert r["mode"] == "RESEARCH_ONLY"


# 15 -- activation never sets a data/backtest/runtime-state flag or posture.

def test_active_does_not_authorize_data_or_runtime_state():
    r = _active_report()
    assert r["backbone_closure_report_active"] is True
    assert r["data_fetch_authorized"] is False
    assert r["backtest_authorized"] is False
    assert r["execution_authorized"] is False
    assert r["safety_posture"]["data_fetch_enabled"] is False
    assert r["safety_posture"]["backtest_enabled"] is False
    assert r["safety_posture"]["automation_enabled"] is False
    assert "pipeline_execution" in r["blocked_capabilities"]
    assert "runtime_state_write" in r["blocked_capabilities"]


# 16 -- the required report description fields are present.

def test_required_report_fields_present():
    r = _active_report()
    for field in _REQUIRED_REPORT_FIELDS:
        assert field in r, field
    assert isinstance(r["completed_contract_chain_summary"], tuple)
    assert len(r["completed_contract_chain_summary"]) >= 1
    assert isinstance(r["remaining_runtime_capabilities_blocked"], tuple)
    assert len(r["remaining_runtime_capabilities_blocked"]) >= 1
    assert isinstance(r["remaining_data_capabilities_blocked"], tuple)
    assert len(r["remaining_data_capabilities_blocked"]) >= 1
    assert isinstance(r["remaining_trading_capabilities_blocked"], tuple)
    assert len(r["remaining_trading_capabilities_blocked"]) >= 1
    assert isinstance(r["human_operator_required_next_steps"], tuple)
    assert len(r["human_operator_required_next_steps"]) >= 1
    assert isinstance(r["operator_notes"], tuple)
    assert len(r["operator_notes"]) >= 1
    assert r["asset_lane"] == "MNQ"
    assert r["timeframe_lane"] == "5m"


# 17 -- completed_bundle_range references Bundles 11-28.

def test_completed_bundle_range_references_11_to_28():
    r = _active_report()
    assert r["completed_bundle_range"] == "Bundles 11-28"
    assert "11" in r["completed_bundle_range"]
    assert "28" in r["completed_bundle_range"]


# 18 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    r = _active_report()
    blocked = set(r["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 19 -- the embedded pipeline contract is preserved.

def test_pipeline_contract_embedded():
    p = _ready_pipeline()
    r = build_backbone_closure_report(p)
    assert r["end_to_end_fake_pipeline_contract"]["schema_version"] == (
        p["schema_version"]
    )
    assert r["end_to_end_fake_pipeline_contract"]["read_only"] is True


# 20 -- validate passes for an active report + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    r = _active_report()
    v = validate_backbone_closure_report(r)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(r)
    bad["execution_authorized"] = True
    assert validate_backbone_closure_report(bad)["valid"] is False

    bad2 = copy.deepcopy(r)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_backbone_closure_report(bad2)["valid"] is False

    bad3 = copy.deepcopy(r)
    bad3["mode"] = "LIVE"
    assert validate_backbone_closure_report(bad3)["valid"] is False

    bad4 = copy.deepcopy(r)
    bad4["completed_contract_chain_summary"] = ()
    assert validate_backbone_closure_report(bad4)["valid"] is False

    bad5 = copy.deepcopy(r)
    bad5["human_operator_required_next_steps"] = ()
    assert validate_backbone_closure_report(bad5)["valid"] is False

    bad6 = copy.deepcopy(r)
    bad6["recommended_next_phase"] = "SOMETHING_ELSE"
    assert validate_backbone_closure_report(bad6)["valid"] is False


# 21 -- validate never requires the report's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    r = copy.deepcopy(_active_report())
    r.pop("validation", None)
    v = validate_backbone_closure_report(r)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 22 -- fresh dicts; mutation of one result does not taint the next.

def test_results_are_fresh_and_isolated():
    a = _active_report()
    b = _active_report()
    assert a == b
    assert a is not b
    a["completed_contract_chain_summary"] = ()
    a["end_to_end_fake_pipeline_contract"]["read_only"] = False
    fresh = _active_report()
    assert len(fresh["completed_contract_chain_summary"]) >= 1
    assert fresh["end_to_end_fake_pipeline_contract"]["read_only"] is True


# 23 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_template_only_and_execution_free():
    r = _active_report()
    md = render_backbone_closure_report_markdown(r)
    assert isinstance(md, str) and md
    assert "# Strategy Factory v1 Backbone Closure Report" in md
    assert "Template only" in md
    assert "backbone-closure-report-only" in md
    assert "no-runtime-state-write" in md
    assert "research-only" in md
    assert "execution-free" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Backbone closure report active: True" in md
    assert "Final backbone status: STRATEGY_FACTORY_V1_BACKBONE_COMPLETE" in md
    assert (
        "Recommended next phase: FAKE_ARTIFACT_SMOKE_TEST_PLANNING_ONLY" in md
    )
    assert "Next gate: PAUSE_AND_OPERATOR_REVIEW" in md
    assert "Completed bundle range: Bundles 11-28" in md
    assert "## Completed Contract Chain Summary" in md
    assert "## Remaining Runtime Capabilities Blocked" in md
    assert "## Remaining Data Capabilities Blocked" in md
    assert "## Remaining Trading Capabilities Blocked" in md
    assert "## Human Operator Required Next Steps" in md
    assert "## Blocked Capabilities" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 24 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 25 -- prose verb audit over chain summary / next steps / notes / markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    r = _active_report()

    texts.extend(str(s) for s in r["completed_contract_chain_summary"])
    texts.extend(str(s) for s in r["human_operator_required_next_steps"])
    texts.extend(str(s) for s in r["operator_notes"])

    md = render_backbone_closure_report_markdown(r)
    for ln in md.splitlines():
        stripped = ln.lstrip()
        # skip headings, backtick key/value bullets, and `Label: value`
        # metadata header lines -- those are DATA / type descriptors, not
        # narrative prose. The self-descriptive safety banner ("Template
        # only: ... backbone-closure-report-only ...") is a metadata header
        # line and is skipped here too.
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


# 26 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 27 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_backbone_closure_report.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_backbone_closure_report.py"'
        in src
    )


# 28 -- Bundle 27 regression import still works.

def test_bundle27_regression_import_still_works():
    from sparta_commander.strategy_factory_end_to_end_fake_pipeline_contract import (  # noqa: E501
        build_end_to_end_fake_pipeline_contract as build27,
    )
    c = build27(_blocked_pipeline_gate())
    assert c["executes"] is False
    assert c["read_only"] is True


def _blocked_pipeline_gate() -> dict:
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
    return build_safety_kill_switch_contract(ledger)


# 29 -- Bundle 26 regression import still works.

def test_bundle26_regression_import_still_works():
    from sparta_commander.strategy_factory_safety_kill_switch_contract import (
        build_safety_kill_switch_contract as build26,
    )
    draft = build_research_protocol_draft_contract(_good_item())
    gate = build_protocol_review_gate(draft)
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    orchestrator = build_dry_run_orchestrator_contract(runner)
    feed = build_dashboard_registry_feed_contract(orchestrator)
    ledger = build_decision_ledger_contract(feed)
    c = build26(ledger)
    assert c["executes"] is False
    assert c["read_only"] is True


# 30 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
