"""Bundle 23 tests for the Strategy Factory Dry-Run Orchestrator Contract
template v1 (informational, read-only, template-only -- NO orchestration,
NO research, NO data access; fake/sample artifact placeholders only).

Bundle 23's production module imports Bundles 11-22 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 23 spec):
- module imports cleanly + public API limited to expected names,
- schema version / label / status / state / gate constants pinned,
- pure stdlib import-root audit + forbidden-surface audit,
- all 14 posture keys present + all False + keys match Bundle 22,
- posture is mutation-isolated (fresh dicts),
- activates only when runner_contract_active True AND runner next_gate is
  DRY_RUN_ORCHESTRATOR_CONTRACT_REQUIRED,
- blocked / wrong-gate / malformed runner never activate and never raise,
- next_gate defaults to DASHBOARD_REGISTRY_FEED_REQUIRED when active,
- no execution/data/backtest/simulation/broker/upload/autopilot/live flag True,
- the 14 template description fields present,
- blocked_capabilities include the required set,
- validate passes + detects failure modes; validation not self-required,
- markdown says dry-run-orchestrator-contract-only + fake-artifact-
  placeholders-only + research-only + execution-free, writes nothing,
- prose verb audit over steps/failures/notes/source/markdown prose,
- scoped dirty-tree guard, Bundle 11-22 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_dry_run_orchestrator_contract import (
    DRY_RUN_ORCHESTRATOR_CONTRACT_SCHEMA_VERSION,
    DEFAULT_DRY_RUN_ORCHESTRATOR_CONTRACT_LABEL,
    DRY_RUN_ORCHESTRATOR_CONTRACT_STATUS,
    DRY_RUN_ORCHESTRATOR_CONTRACT_SAFETY_POSTURE,
    DRY_RUN_ORCHESTRATOR_STATE_ACTIVE,
    DRY_RUN_ORCHESTRATOR_STATE_BLOCKED,
    NEXT_GATE_DASHBOARD_REGISTRY_FEED_REQUIRED,
    NEXT_GATE_AWAIT_RESEARCH_RUNNER_CONTRACT,
    build_dry_run_orchestrator_contract,
    validate_dry_run_orchestrator_contract,
    render_dry_run_orchestrator_contract_markdown,
)
import sparta_commander.strategy_factory_dry_run_orchestrator_contract as DO
from sparta_commander.strategy_factory_research_runner_contract import (
    RESEARCH_RUNNER_CONTRACT_SAFETY_POSTURE,
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
    / "strategy_factory_dry_run_orchestrator_contract.py"
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
)

_REQUIRED_TEMPLATE_FIELDS = (
    "dry_run_orchestrator_contract_active",
    "source_protocol_reference_placeholder",
    "source_data_contract_reference_placeholder",
    "source_data_qa_reference_placeholder",
    "source_runner_contract_reference_placeholder",
    "fake_artifact_inputs_required", "fake_artifact_outputs_required",
    "orchestration_steps_placeholder", "expected_trace_fields",
    "expected_failure_modes", "expected_operator_review_fields",
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


def _ready_runner() -> dict:
    """A Bundle 22 runner contract that is active (DRY_RUN_ORCHESTRATOR gate)."""
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(
        draft, review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING)
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    return build_research_runner_contract(data_qa)


def _blocked_runner() -> dict:
    """A Bundle 22 runner contract that is NOT active."""
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(draft)  # awaiting, not unlocked
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    return build_research_runner_contract(data_qa)


def _active_contract() -> dict:
    return build_dry_run_orchestrator_contract(_ready_runner())


def _expected_public() -> set[str]:
    return {
        "DRY_RUN_ORCHESTRATOR_CONTRACT_SCHEMA_VERSION",
        "DEFAULT_DRY_RUN_ORCHESTRATOR_CONTRACT_LABEL",
        "DRY_RUN_ORCHESTRATOR_CONTRACT_STATUS",
        "DRY_RUN_ORCHESTRATOR_CONTRACT_SAFETY_POSTURE",
        "DRY_RUN_ORCHESTRATOR_STATE_ACTIVE",
        "DRY_RUN_ORCHESTRATOR_STATE_BLOCKED",
        "NEXT_GATE_DASHBOARD_REGISTRY_FEED_REQUIRED",
        "NEXT_GATE_AWAIT_RESEARCH_RUNNER_CONTRACT",
        "build_dry_run_orchestrator_contract",
        "validate_dry_run_orchestrator_contract",
        "render_dry_run_orchestrator_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(DO.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(DO, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        DRY_RUN_ORCHESTRATOR_CONTRACT_SCHEMA_VERSION
        == "strategy_factory_dry_run_orchestrator_contract.v1"
    )


# 3 -- label / status pinned.

def test_label_and_status_pinned():
    assert (
        DEFAULT_DRY_RUN_ORCHESTRATOR_CONTRACT_LABEL
        == "Strategy Factory Dry Run Orchestrator Contract"
    )
    assert (
        DRY_RUN_ORCHESTRATOR_CONTRACT_STATUS
        == "READ_ONLY_DRY_RUN_ORCHESTRATOR_CONTRACT"
    )


# 4 -- state / gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        DRY_RUN_ORCHESTRATOR_STATE_ACTIVE
        == "DRY_RUN_ORCHESTRATOR_CONTRACT_ACTIVE"
    )
    assert (
        DRY_RUN_ORCHESTRATOR_STATE_BLOCKED
        == "DRY_RUN_ORCHESTRATOR_CONTRACT_BLOCKED"
    )
    assert (
        NEXT_GATE_DASHBOARD_REGISTRY_FEED_REQUIRED
        == "DASHBOARD_REGISTRY_FEED_REQUIRED"
    )
    assert (
        NEXT_GATE_AWAIT_RESEARCH_RUNNER_CONTRACT
        == "AWAIT_RESEARCH_RUNNER_CONTRACT"
    )


# 5 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = DRY_RUN_ORCHESTRATOR_CONTRACT_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 6 -- posture keys match Bundle 22.

def test_posture_keys_match_bundle22():
    assert (
        set(DRY_RUN_ORCHESTRATOR_CONTRACT_SAFETY_POSTURE.keys())
        == set(RESEARCH_RUNNER_CONTRACT_SAFETY_POSTURE.keys())
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
    a = build_dry_run_orchestrator_contract(_ready_runner())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_dry_run_orchestrator_contract(_ready_runner())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        DRY_RUN_ORCHESTRATOR_CONTRACT_SAFETY_POSTURE["automation_enabled"]
        is False
    )


# 10 -- runner active + DRY_RUN_ORCHESTRATOR gate activates the contract.

def test_active_runner_activates():
    c = _active_contract()
    assert c["dry_run_orchestrator_contract_active"] is True
    assert c["dry_run_orchestrator_state"] == "DRY_RUN_ORCHESTRATOR_CONTRACT_ACTIVE"
    assert c["next_gate"] == "DASHBOARD_REGISTRY_FEED_REQUIRED"
    assert c["runner_contract_active"] is True
    assert c["runner_next_gate"] == "DRY_RUN_ORCHESTRATOR_CONTRACT_REQUIRED"


# 11 -- a blocked (inactive) runner contract does not activate.

def test_blocked_runner_does_not_activate():
    c = build_dry_run_orchestrator_contract(_blocked_runner())
    assert c["dry_run_orchestrator_contract_active"] is False
    assert c["dry_run_orchestrator_state"] == "DRY_RUN_ORCHESTRATOR_CONTRACT_BLOCKED"
    assert c["next_gate"] == "AWAIT_RESEARCH_RUNNER_CONTRACT"


# 12 -- runner active but wrong next_gate does not activate.

def test_active_runner_wrong_gate_does_not_activate():
    import copy
    r = copy.deepcopy(_ready_runner())
    r["next_gate"] = "SOMETHING_ELSE"  # tamper: no longer the orchestrator gate
    c = build_dry_run_orchestrator_contract(r)
    assert c["dry_run_orchestrator_contract_active"] is False
    assert c["next_gate"] == "AWAIT_RESEARCH_RUNNER_CONTRACT"


# 13 -- malformed runner never raises and never activates.

def test_malformed_runner_no_raise():
    for bad in (None, 42, "nope", {}, {"runner_contract_active": True}, []):
        c = build_dry_run_orchestrator_contract(bad)
        assert c["dry_run_orchestrator_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert c["validation"]["valid"] is True


# 14 -- no authorization flag can become True (active or blocked).

def test_authorization_flags_always_false():
    for c in (_active_contract(),
              build_dry_run_orchestrator_contract(_blocked_runner())):
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["stage"] == "PLAN_ONLY"
        assert c["mode"] == "RESEARCH_ONLY"


# 15 -- activation never sets a data/backtest authorization flag or posture key.

def test_active_does_not_authorize_data_or_backtest():
    c = _active_contract()
    assert c["dry_run_orchestrator_contract_active"] is True
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["backtest_enabled"] is False


# 16 -- the 14 required template description fields are present.

def test_required_template_fields_present():
    c = _active_contract()
    for field in _REQUIRED_TEMPLATE_FIELDS:
        assert field in c, field
    assert isinstance(c["fake_artifact_inputs_required"], tuple)
    assert len(c["fake_artifact_inputs_required"]) >= 1
    assert isinstance(c["fake_artifact_outputs_required"], tuple)
    assert len(c["fake_artifact_outputs_required"]) >= 1
    assert isinstance(c["orchestration_steps_placeholder"], tuple)
    assert len(c["orchestration_steps_placeholder"]) >= 1
    assert c["asset_lane"] == "MNQ"
    assert c["timeframe_lane"] == "5m"


# 17 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    c = _active_contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 18 -- the embedded runner contract is preserved.

def test_runner_embedded():
    r = _ready_runner()
    c = build_dry_run_orchestrator_contract(r)
    assert c["research_runner_contract"]["schema_version"] == (
        r["schema_version"]
    )
    assert c["research_runner_contract"]["read_only"] is True


# 19 -- validate passes for an active contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _active_contract()
    v = validate_dry_run_orchestrator_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_dry_run_orchestrator_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_dry_run_orchestrator_contract(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_dry_run_orchestrator_contract(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["fake_artifact_inputs_required"] = ()
    assert validate_dry_run_orchestrator_contract(bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["fake_artifact_outputs_required"] = ()
    assert validate_dry_run_orchestrator_contract(bad5)["valid"] is False


# 20 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_active_contract())
    c.pop("validation", None)
    v = validate_dry_run_orchestrator_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 21 -- fresh dicts; mutation of one result does not taint the next.

def test_results_are_fresh_and_isolated():
    a = _active_contract()
    b = _active_contract()
    assert a == b
    assert a is not b
    a["fake_artifact_inputs_required"] = ()
    a["research_runner_contract"]["read_only"] = False
    fresh = _active_contract()
    assert len(fresh["fake_artifact_inputs_required"]) >= 1
    assert fresh["research_runner_contract"]["read_only"] is True


# 22 -- markdown non-empty, says the four required descriptors, sections.

def test_markdown_template_only_and_execution_free():
    c = _active_contract()
    md = render_dry_run_orchestrator_contract_markdown(c)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Dry Run Orchestrator Contract" in md
    assert "Template only" in md
    assert "dry-run-orchestrator-contract-only" in md
    assert "fake-artifact-placeholders-only" in md
    assert "research-only" in md
    assert "execution-free" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Dry run orchestrator contract active: True" in md
    assert "Next gate: DASHBOARD_REGISTRY_FEED_REQUIRED" in md
    assert "## Fake Artifact Inputs Required" in md
    assert "## Fake Artifact Outputs Required" in md
    assert "## Orchestration Steps Placeholder" in md
    assert "## Expected Trace Fields" in md
    assert "## Expected Failure Modes" in md
    assert "## Expected Operator Review Fields" in md
    assert "## Blocked Capabilities" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 23 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 24 -- prose verb audit over steps / failures / notes / source / markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _active_contract()

    texts.extend(str(s) for s in c["orchestration_steps_placeholder"])
    texts.extend(str(s) for s in c["expected_failure_modes"])
    texts.extend(str(s) for s in c["operator_notes"])
    for key in (
        "source_protocol_reference_placeholder",
        "source_data_contract_reference_placeholder",
        "source_data_qa_reference_placeholder",
        "source_runner_contract_reference_placeholder",
    ):
        texts.append(str(c[key]))

    md = render_dry_run_orchestrator_contract_markdown(c)
    for ln in md.splitlines():
        stripped = ln.lstrip()
        # skip headings, backtick key/value bullets, and `Label: value`
        # metadata header lines -- those are DATA / type descriptors, not
        # narrative prose. The self-descriptive safety banner ("Template
        # only: ... dry-run-orchestrator-contract-only ...") is a metadata
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


# 25 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 26 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_dry_run_orchestrator_contract.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_dry_run_orchestrator_contract.py"' in src
    )


# 27 -- Bundle 22 regression import still works.

def test_bundle22_regression_import_still_works():
    from sparta_commander.strategy_factory_research_runner_contract import (
        build_research_runner_contract as build22,
    )
    c = build22(_blocked_data_qa())
    assert c["executes"] is False
    assert c["read_only"] is True


def _blocked_data_qa() -> dict:
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(draft)
    planning = build_data_contract_planning(gate)
    return build_data_qa_contract(planning)


# 28 -- Bundle 21 regression import still works.

def test_bundle21_regression_import_still_works():
    from sparta_commander.strategy_factory_data_qa_contract import (
        build_data_qa_contract as build21,
    )
    draft = build_research_protocol_draft_contract(_good_item())
    gate = build_protocol_review_gate(draft)
    planning = build_data_contract_planning(gate)
    c = build21(planning)
    assert c["executes"] is False
    assert c["read_only"] is True


# 29 -- Bundle 19 regression import still works.

def test_bundle19_regression_import_still_works():
    from sparta_commander.strategy_factory_protocol_review_gate import (
        build_protocol_review_gate as build19,
    )
    draft = build_research_protocol_draft_contract(_good_item())
    g = build19(draft)
    assert g["executes"] is False
    assert g["read_only"] is True


# 30 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
