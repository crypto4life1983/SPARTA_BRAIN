"""Bundle 26 tests for the Strategy Factory Safety Kill-Switch / Approval Gate
Contract template v1 (informational, read-only, template-only -- NO runtime
approval write, NO runtime safety flag write, NO ledger/dashboard/registry
write, NO orchestration, NO research, NO data access).

Bundle 26's production module imports Bundles 11-25 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 26 spec):
- module imports cleanly + public API limited to expected names,
- schema version / label / status / state / gate constants pinned,
- pure stdlib import-root audit + forbidden-surface audit,
- all 14 posture keys present + all False + keys match Bundle 25,
- posture is mutation-isolated (fresh dicts),
- activates only when decision_ledger_contract_active True AND ledger
  next_gate is SAFETY_KILL_SWITCH_CONTRACT_REQUIRED,
- blocked / wrong-gate / malformed ledger never activate, never raise,
- next_gate defaults to END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED when active,
- no execution/data/backtest/broker/upload/autopilot/live/dashboard-runtime/
  ledger-write/runtime-approval flag True,
- the 15 template description fields present,
- blocked_capabilities include the required set (incl. runtime_approval_write),
- validate passes + detects failure modes; validation not self-required,
- markdown says safety-kill-switch-contract-only + no-runtime-approval-write +
  research-only + execution-free, writes nothing,
- prose verb audit over notes / conditions / source / markdown prose,
- scoped dirty-tree guard, Bundle 11-25 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_safety_kill_switch_contract import (
    SAFETY_KILL_SWITCH_CONTRACT_SCHEMA_VERSION,
    DEFAULT_SAFETY_KILL_SWITCH_CONTRACT_LABEL,
    SAFETY_KILL_SWITCH_CONTRACT_STATUS,
    SAFETY_KILL_SWITCH_CONTRACT_SAFETY_POSTURE,
    SAFETY_KILL_SWITCH_STATE_ACTIVE,
    SAFETY_KILL_SWITCH_STATE_BLOCKED,
    NEXT_GATE_END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED,
    NEXT_GATE_AWAIT_DECISION_LEDGER_CONTRACT,
    build_safety_kill_switch_contract,
    validate_safety_kill_switch_contract,
    render_safety_kill_switch_contract_markdown,
)
import sparta_commander.strategy_factory_safety_kill_switch_contract as KS
from sparta_commander.strategy_factory_decision_ledger_contract import (
    DECISION_LEDGER_CONTRACT_SAFETY_POSTURE,
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
    / "strategy_factory_safety_kill_switch_contract.py"
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
    "runtime_safety_flag_write",
)

_REQUIRED_TEMPLATE_FIELDS = (
    "safety_kill_switch_contract_active",
    "source_decision_ledger_reference_placeholder",
    "required_manual_approval_fields",
    "required_operator_attestation_fields",
    "blocked_execution_surfaces", "blocked_data_surfaces",
    "blocked_broker_surfaces", "blocked_automation_surfaces",
    "emergency_stop_conditions", "approval_expiry_placeholder",
    "required_preflight_checks", "required_rejection_conditions",
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


def _ready_ledger() -> dict:
    """A Bundle 25 decision ledger contract that is active."""
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
    return build_decision_ledger_contract(feed)


def _blocked_ledger() -> dict:
    """A Bundle 25 decision ledger contract that is NOT active."""
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
    return build_decision_ledger_contract(feed)


def _active_contract() -> dict:
    return build_safety_kill_switch_contract(_ready_ledger())


def _expected_public() -> set[str]:
    return {
        "SAFETY_KILL_SWITCH_CONTRACT_SCHEMA_VERSION",
        "DEFAULT_SAFETY_KILL_SWITCH_CONTRACT_LABEL",
        "SAFETY_KILL_SWITCH_CONTRACT_STATUS",
        "SAFETY_KILL_SWITCH_CONTRACT_SAFETY_POSTURE",
        "SAFETY_KILL_SWITCH_STATE_ACTIVE",
        "SAFETY_KILL_SWITCH_STATE_BLOCKED",
        "NEXT_GATE_END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED",
        "NEXT_GATE_AWAIT_DECISION_LEDGER_CONTRACT",
        "build_safety_kill_switch_contract",
        "validate_safety_kill_switch_contract",
        "render_safety_kill_switch_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(KS.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(KS, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        SAFETY_KILL_SWITCH_CONTRACT_SCHEMA_VERSION
        == "strategy_factory_safety_kill_switch_contract.v1"
    )


# 3 -- label / status pinned.

def test_label_and_status_pinned():
    assert (
        DEFAULT_SAFETY_KILL_SWITCH_CONTRACT_LABEL
        == "Strategy Factory Safety Kill-Switch / Approval Gate Contract"
    )
    assert (
        SAFETY_KILL_SWITCH_CONTRACT_STATUS
        == "READ_ONLY_SAFETY_KILL_SWITCH_CONTRACT"
    )


# 4 -- state / gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        SAFETY_KILL_SWITCH_STATE_ACTIVE
        == "SAFETY_KILL_SWITCH_CONTRACT_ACTIVE"
    )
    assert (
        SAFETY_KILL_SWITCH_STATE_BLOCKED
        == "SAFETY_KILL_SWITCH_CONTRACT_BLOCKED"
    )
    assert (
        NEXT_GATE_END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED
        == "END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED"
    )
    assert (
        NEXT_GATE_AWAIT_DECISION_LEDGER_CONTRACT
        == "AWAIT_DECISION_LEDGER_CONTRACT"
    )


# 5 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = SAFETY_KILL_SWITCH_CONTRACT_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 6 -- posture keys match Bundle 25.

def test_posture_keys_match_bundle25():
    assert (
        set(SAFETY_KILL_SWITCH_CONTRACT_SAFETY_POSTURE.keys())
        == set(DECISION_LEDGER_CONTRACT_SAFETY_POSTURE.keys())
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
    a = build_safety_kill_switch_contract(_ready_ledger())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_safety_kill_switch_contract(_ready_ledger())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        SAFETY_KILL_SWITCH_CONTRACT_SAFETY_POSTURE["automation_enabled"]
        is False
    )


# 10 -- ledger active + SAFETY_KILL_SWITCH gate activates the contract.

def test_active_ledger_activates():
    c = _active_contract()
    assert c["safety_kill_switch_contract_active"] is True
    assert (
        c["safety_kill_switch_state"]
        == "SAFETY_KILL_SWITCH_CONTRACT_ACTIVE"
    )
    assert c["next_gate"] == "END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED"
    assert c["decision_ledger_contract_active"] is True
    assert (
        c["decision_ledger_next_gate"]
        == "SAFETY_KILL_SWITCH_CONTRACT_REQUIRED"
    )


# 11 -- a blocked (inactive) ledger contract does not activate.

def test_blocked_ledger_does_not_activate():
    c = build_safety_kill_switch_contract(_blocked_ledger())
    assert c["safety_kill_switch_contract_active"] is False
    assert (
        c["safety_kill_switch_state"]
        == "SAFETY_KILL_SWITCH_CONTRACT_BLOCKED"
    )
    assert c["next_gate"] == "AWAIT_DECISION_LEDGER_CONTRACT"


# 12 -- ledger active but wrong next_gate does not activate.

def test_active_ledger_wrong_gate_does_not_activate():
    import copy
    led = copy.deepcopy(_ready_ledger())
    led["next_gate"] = "SOMETHING_ELSE"  # tamper: no longer the safety gate
    c = build_safety_kill_switch_contract(led)
    assert c["safety_kill_switch_contract_active"] is False
    assert c["next_gate"] == "AWAIT_DECISION_LEDGER_CONTRACT"


# 13 -- malformed ledger never raises and never activates.

def test_malformed_ledger_no_raise():
    for bad in (None, 42, "nope", {},
                {"decision_ledger_contract_active": True}, []):
        c = build_safety_kill_switch_contract(bad)
        assert c["safety_kill_switch_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 14 -- no authorization flag can become True (active or blocked).

def test_authorization_flags_always_false():
    for c in (_active_contract(),
              build_safety_kill_switch_contract(_blocked_ledger())):
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["stage"] == "PLAN_ONLY"
        assert c["mode"] == "RESEARCH_ONLY"


# 15 -- activation never sets a data/backtest/runtime-approval flag or posture.

def test_active_does_not_authorize_data_or_runtime_approval():
    c = _active_contract()
    assert c["safety_kill_switch_contract_active"] is True
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["backtest_enabled"] is False
    assert c["safety_posture"]["automation_enabled"] is False
    assert "runtime_approval_write" in c["blocked_capabilities"]
    assert "runtime_safety_flag_write" in c["blocked_capabilities"]


# 16 -- the required template description fields are present.

def test_required_template_fields_present():
    c = _active_contract()
    for field in _REQUIRED_TEMPLATE_FIELDS:
        assert field in c, field
    assert isinstance(c["required_manual_approval_fields"], tuple)
    assert len(c["required_manual_approval_fields"]) >= 1
    assert isinstance(c["required_operator_attestation_fields"], tuple)
    assert len(c["required_operator_attestation_fields"]) >= 1
    assert isinstance(c["blocked_execution_surfaces"], tuple)
    assert len(c["blocked_execution_surfaces"]) >= 1
    assert isinstance(c["blocked_data_surfaces"], tuple)
    assert len(c["blocked_data_surfaces"]) >= 1
    assert isinstance(c["blocked_broker_surfaces"], tuple)
    assert len(c["blocked_broker_surfaces"]) >= 1
    assert isinstance(c["blocked_automation_surfaces"], tuple)
    assert len(c["blocked_automation_surfaces"]) >= 1
    assert c["asset_lane"] == "MNQ"
    assert c["timeframe_lane"] == "5m"


# 17 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    c = _active_contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 18 -- the embedded ledger contract is preserved.

def test_ledger_embedded():
    led = _ready_ledger()
    c = build_safety_kill_switch_contract(led)
    assert c["decision_ledger_contract"]["schema_version"] == (
        led["schema_version"]
    )
    assert c["decision_ledger_contract"]["read_only"] is True


# 19 -- validate passes for an active contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _active_contract()
    v = validate_safety_kill_switch_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_safety_kill_switch_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_safety_kill_switch_contract(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_safety_kill_switch_contract(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["required_manual_approval_fields"] = ()
    assert validate_safety_kill_switch_contract(bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["required_operator_attestation_fields"] = ()
    assert validate_safety_kill_switch_contract(bad5)["valid"] is False


# 20 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_active_contract())
    c.pop("validation", None)
    v = validate_safety_kill_switch_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 21 -- fresh dicts; mutation of one result does not taint the next.

def test_results_are_fresh_and_isolated():
    a = _active_contract()
    b = _active_contract()
    assert a == b
    assert a is not b
    a["required_manual_approval_fields"] = ()
    a["decision_ledger_contract"]["read_only"] = False
    fresh = _active_contract()
    assert len(fresh["required_manual_approval_fields"]) >= 1
    assert fresh["decision_ledger_contract"]["read_only"] is True


# 22 -- markdown non-empty, says the four required descriptors, sections.

def test_markdown_template_only_and_execution_free():
    c = _active_contract()
    md = render_safety_kill_switch_contract_markdown(c)
    assert isinstance(md, str) and md
    assert (
        "# Strategy Factory Safety Kill-Switch / Approval Gate Contract" in md
    )
    assert "Template only" in md
    assert "safety-kill-switch-contract-only" in md
    assert "no-runtime-approval-write" in md
    assert "research-only" in md
    assert "execution-free" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Safety kill switch contract active: True" in md
    assert "Next gate: END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED" in md
    assert "## Required Manual Approval Fields" in md
    assert "## Required Operator Attestation Fields" in md
    assert "## Blocked Execution Surfaces" in md
    assert "## Blocked Data Surfaces" in md
    assert "## Blocked Broker Surfaces" in md
    assert "## Blocked Automation Surfaces" in md
    assert "## Emergency Stop Conditions" in md
    assert "## Required Preflight Checks" in md
    assert "## Required Rejection Conditions" in md
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


# 24 -- prose verb audit over notes / conditions / source / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _active_contract()

    texts.extend(str(s) for s in c["operator_notes"])
    texts.extend(str(s) for s in c["emergency_stop_conditions"])
    texts.extend(str(s) for s in c["required_preflight_checks"])
    texts.extend(str(s) for s in c["required_rejection_conditions"])
    texts.append(str(c["source_decision_ledger_reference_placeholder"]))
    texts.append(str(c["approval_expiry_placeholder"]))

    md = render_safety_kill_switch_contract_markdown(c)
    for ln in md.splitlines():
        stripped = ln.lstrip()
        # skip headings, backtick key/value bullets, and `Label: value`
        # metadata header lines -- those are DATA / type descriptors, not
        # narrative prose. The self-descriptive safety banner ("Template
        # only: ... safety-kill-switch-contract-only ...") is a metadata
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
        '"sparta_commander/strategy_factory_safety_kill_switch_contract.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_safety_kill_switch_contract.py"'
        in src
    )


# 27 -- Bundle 25 regression import still works.

def test_bundle25_regression_import_still_works():
    from sparta_commander.strategy_factory_decision_ledger_contract import (
        build_decision_ledger_contract as build25,
    )
    c = build25(_blocked_feed())
    assert c["executes"] is False
    assert c["read_only"] is True


def _blocked_feed() -> dict:
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
    return build_dashboard_registry_feed_contract(orchestrator)


# 28 -- Bundle 24 regression import still works.

def test_bundle24_regression_import_still_works():
    from sparta_commander.strategy_factory_dashboard_registry_feed_contract import (
        build_dashboard_registry_feed_contract as build24,
    )
    draft = build_research_protocol_draft_contract(_good_item())
    gate = build_protocol_review_gate(draft)
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    orchestrator = build_dry_run_orchestrator_contract(runner)
    c = build24(orchestrator)
    assert c["executes"] is False
    assert c["read_only"] is True


# 29 -- Bundle 23 regression import still works.

def test_bundle23_regression_import_still_works():
    from sparta_commander.strategy_factory_dry_run_orchestrator_contract import (
        build_dry_run_orchestrator_contract as build23,
    )
    draft = build_research_protocol_draft_contract(_good_item())
    gate = build_protocol_review_gate(draft)
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    c = build23(runner)
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
