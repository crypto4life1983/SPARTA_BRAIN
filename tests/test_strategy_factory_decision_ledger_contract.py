"""Bundle 25 tests for the Strategy Factory Decision Ledger Contract template
v1 (informational, read-only, template-only -- NO runtime ledger write, NO
dashboard runtime update, NO registry file write, NO orchestration, NO
research, NO data access).

Bundle 25's production module imports Bundles 11-24 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 25 spec):
- module imports cleanly + public API limited to expected names,
- schema version / label / status / state / gate constants pinned,
- pure stdlib import-root audit + forbidden-surface audit,
- all 14 posture keys present + all False + keys match Bundle 24,
- posture is mutation-isolated (fresh dicts),
- activates only when dashboard_registry_feed_contract_active True AND
  feed next_gate is DECISION_LEDGER_CONTRACT_REQUIRED,
- blocked / wrong-gate / malformed feed never activate, never raise,
- next_gate defaults to SAFETY_KILL_SWITCH_CONTRACT_REQUIRED when active,
- allowed_decision_values are exactly the expected safe decision set,
- no execution/data/backtest/broker/upload/autopilot/live/dashboard-runtime/
  ledger-write flag True,
- the 16 template description fields present,
- blocked_capabilities include the required set (incl. ledger_runtime_write),
- validate passes + detects failure modes; validation not self-required,
- markdown says decision-ledger-contract-only + no-runtime-ledger-write +
  research-only + execution-free, writes nothing,
- prose verb audit over notes / reasons / source / markdown prose,
- scoped dirty-tree guard, Bundle 11-24 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_decision_ledger_contract import (
    DECISION_LEDGER_CONTRACT_SCHEMA_VERSION,
    DEFAULT_DECISION_LEDGER_CONTRACT_LABEL,
    DECISION_LEDGER_CONTRACT_STATUS,
    DECISION_LEDGER_CONTRACT_SAFETY_POSTURE,
    DECISION_LEDGER_STATE_ACTIVE,
    DECISION_LEDGER_STATE_BLOCKED,
    ALLOWED_DECISION_VALUES,
    NEXT_GATE_SAFETY_KILL_SWITCH_CONTRACT_REQUIRED,
    NEXT_GATE_AWAIT_DASHBOARD_REGISTRY_FEED_CONTRACT,
    build_decision_ledger_contract,
    validate_decision_ledger_contract,
    render_decision_ledger_contract_markdown,
)
import sparta_commander.strategy_factory_decision_ledger_contract as DL
from sparta_commander.strategy_factory_dashboard_registry_feed_contract import (
    DASHBOARD_REGISTRY_FEED_CONTRACT_SAFETY_POSTURE,
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
    / "strategy_factory_decision_ledger_contract.py"
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
    "ledger_runtime_write",
)

_REQUIRED_TEMPLATE_FIELDS = (
    "decision_ledger_contract_active",
    "source_protocol_reference_placeholder",
    "source_runner_contract_reference_placeholder",
    "source_orchestrator_reference_placeholder",
    "source_dashboard_feed_reference_placeholder",
    "ledger_entry_fields", "allowed_decision_values",
    "required_human_review_fields", "required_safety_attestation_fields",
    "required_evidence_placeholders", "decision_blocking_reasons",
    "expected_audit_fields",
    "blocked_capabilities", "safety_posture", "next_gate", "operator_notes",
)

_EXPECTED_DECISION_VALUES = (
    "NEEDS_MORE_SPEC",
    "READY_FOR_FAKE_ARTIFACT_DRY_RUN_REVIEW",
    "WATCH",
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


def _ready_feed() -> dict:
    """A Bundle 24 dashboard registry feed contract that is active."""
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
    return build_dashboard_registry_feed_contract(orchestrator)


def _blocked_feed() -> dict:
    """A Bundle 24 dashboard registry feed contract that is NOT active."""
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
    return build_dashboard_registry_feed_contract(orchestrator)


def _active_contract() -> dict:
    return build_decision_ledger_contract(_ready_feed())


def _expected_public() -> set[str]:
    return {
        "DECISION_LEDGER_CONTRACT_SCHEMA_VERSION",
        "DEFAULT_DECISION_LEDGER_CONTRACT_LABEL",
        "DECISION_LEDGER_CONTRACT_STATUS",
        "DECISION_LEDGER_CONTRACT_SAFETY_POSTURE",
        "DECISION_LEDGER_STATE_ACTIVE",
        "DECISION_LEDGER_STATE_BLOCKED",
        "ALLOWED_DECISION_VALUES",
        "NEXT_GATE_SAFETY_KILL_SWITCH_CONTRACT_REQUIRED",
        "NEXT_GATE_AWAIT_DASHBOARD_REGISTRY_FEED_CONTRACT",
        "build_decision_ledger_contract",
        "validate_decision_ledger_contract",
        "render_decision_ledger_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(DL.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(DL, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        DECISION_LEDGER_CONTRACT_SCHEMA_VERSION
        == "strategy_factory_decision_ledger_contract.v1"
    )


# 3 -- label / status pinned.

def test_label_and_status_pinned():
    assert (
        DEFAULT_DECISION_LEDGER_CONTRACT_LABEL
        == "Strategy Factory Decision Ledger Contract"
    )
    assert (
        DECISION_LEDGER_CONTRACT_STATUS
        == "READ_ONLY_DECISION_LEDGER_CONTRACT"
    )


# 4 -- state / gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        DECISION_LEDGER_STATE_ACTIVE
        == "DECISION_LEDGER_CONTRACT_ACTIVE"
    )
    assert (
        DECISION_LEDGER_STATE_BLOCKED
        == "DECISION_LEDGER_CONTRACT_BLOCKED"
    )
    assert (
        NEXT_GATE_SAFETY_KILL_SWITCH_CONTRACT_REQUIRED
        == "SAFETY_KILL_SWITCH_CONTRACT_REQUIRED"
    )
    assert (
        NEXT_GATE_AWAIT_DASHBOARD_REGISTRY_FEED_CONTRACT
        == "AWAIT_DASHBOARD_REGISTRY_FEED_CONTRACT"
    )


# 5 -- allowed decision values are exactly the expected safe decision set.

def test_allowed_decision_values_are_exact_safe_set():
    assert ALLOWED_DECISION_VALUES == _EXPECTED_DECISION_VALUES
    assert isinstance(ALLOWED_DECISION_VALUES, tuple)
    # None of these labels authorizes execution.
    assert "EXECUTE" not in ALLOWED_DECISION_VALUES
    assert "PROMOTE" not in ALLOWED_DECISION_VALUES


# 6 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = DECISION_LEDGER_CONTRACT_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 7 -- posture keys match Bundle 24.

def test_posture_keys_match_bundle24():
    assert (
        set(DECISION_LEDGER_CONTRACT_SAFETY_POSTURE.keys())
        == set(DASHBOARD_REGISTRY_FEED_CONTRACT_SAFETY_POSTURE.keys())
    )


# 8 -- pure stdlib import-root audit: allowed roots only.

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


# 9 -- forbidden-surface audit: no file/network/subprocess/exec surface.

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


# 10 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = build_decision_ledger_contract(_ready_feed())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_decision_ledger_contract(_ready_feed())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        DECISION_LEDGER_CONTRACT_SAFETY_POSTURE["automation_enabled"]
        is False
    )


# 11 -- feed active + DECISION_LEDGER gate activates the contract.

def test_active_feed_activates():
    c = _active_contract()
    assert c["decision_ledger_contract_active"] is True
    assert (
        c["decision_ledger_state"]
        == "DECISION_LEDGER_CONTRACT_ACTIVE"
    )
    assert c["next_gate"] == "SAFETY_KILL_SWITCH_CONTRACT_REQUIRED"
    assert c["dashboard_registry_feed_contract_active"] is True
    assert (
        c["dashboard_registry_feed_next_gate"]
        == "DECISION_LEDGER_CONTRACT_REQUIRED"
    )


# 12 -- a blocked (inactive) feed contract does not activate.

def test_blocked_feed_does_not_activate():
    c = build_decision_ledger_contract(_blocked_feed())
    assert c["decision_ledger_contract_active"] is False
    assert (
        c["decision_ledger_state"]
        == "DECISION_LEDGER_CONTRACT_BLOCKED"
    )
    assert c["next_gate"] == "AWAIT_DASHBOARD_REGISTRY_FEED_CONTRACT"


# 13 -- feed active but wrong next_gate does not activate.

def test_active_feed_wrong_gate_does_not_activate():
    import copy
    f = copy.deepcopy(_ready_feed())
    f["next_gate"] = "SOMETHING_ELSE"  # tamper: no longer the ledger gate
    c = build_decision_ledger_contract(f)
    assert c["decision_ledger_contract_active"] is False
    assert c["next_gate"] == "AWAIT_DASHBOARD_REGISTRY_FEED_CONTRACT"


# 14 -- malformed feed never raises and never activates.

def test_malformed_feed_no_raise():
    for bad in (None, 42, "nope", {},
                {"dashboard_registry_feed_contract_active": True}, []):
        c = build_decision_ledger_contract(bad)
        assert c["decision_ledger_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 15 -- no authorization flag can become True (active or blocked).

def test_authorization_flags_always_false():
    for c in (_active_contract(),
              build_decision_ledger_contract(_blocked_feed())):
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["stage"] == "PLAN_ONLY"
        assert c["mode"] == "RESEARCH_ONLY"


# 16 -- activation never sets a data/backtest/ledger-write flag or posture key.

def test_active_does_not_authorize_data_or_ledger_write():
    c = _active_contract()
    assert c["decision_ledger_contract_active"] is True
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["backtest_enabled"] is False
    assert c["safety_posture"]["automation_enabled"] is False
    assert "ledger_runtime_write" in c["blocked_capabilities"]


# 17 -- the 16 required template description fields are present.

def test_required_template_fields_present():
    c = _active_contract()
    for field in _REQUIRED_TEMPLATE_FIELDS:
        assert field in c, field
    assert isinstance(c["ledger_entry_fields"], tuple)
    assert len(c["ledger_entry_fields"]) >= 1
    assert isinstance(c["allowed_decision_values"], tuple)
    assert c["allowed_decision_values"] == _EXPECTED_DECISION_VALUES
    assert isinstance(c["required_human_review_fields"], tuple)
    assert len(c["required_human_review_fields"]) >= 1
    assert isinstance(c["required_safety_attestation_fields"], tuple)
    assert len(c["required_safety_attestation_fields"]) >= 1
    assert isinstance(c["required_evidence_placeholders"], tuple)
    assert len(c["required_evidence_placeholders"]) >= 1
    assert isinstance(c["expected_audit_fields"], tuple)
    assert len(c["expected_audit_fields"]) >= 1
    assert c["asset_lane"] == "MNQ"
    assert c["timeframe_lane"] == "5m"


# 18 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    c = _active_contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 19 -- the embedded feed contract is preserved.

def test_feed_embedded():
    f = _ready_feed()
    c = build_decision_ledger_contract(f)
    assert c["dashboard_registry_feed_contract"]["schema_version"] == (
        f["schema_version"]
    )
    assert c["dashboard_registry_feed_contract"]["read_only"] is True


# 20 -- validate passes for an active contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _active_contract()
    v = validate_decision_ledger_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_decision_ledger_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_decision_ledger_contract(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_decision_ledger_contract(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["ledger_entry_fields"] = ()
    assert validate_decision_ledger_contract(bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["allowed_decision_values"] = ("ANYTHING_ELSE",)
    assert validate_decision_ledger_contract(bad5)["valid"] is False


# 21 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_active_contract())
    c.pop("validation", None)
    v = validate_decision_ledger_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 22 -- fresh dicts; mutation of one result does not taint the next.

def test_results_are_fresh_and_isolated():
    a = _active_contract()
    b = _active_contract()
    assert a == b
    assert a is not b
    a["ledger_entry_fields"] = ()
    a["dashboard_registry_feed_contract"]["read_only"] = False
    fresh = _active_contract()
    assert len(fresh["ledger_entry_fields"]) >= 1
    assert fresh["dashboard_registry_feed_contract"]["read_only"] is True


# 23 -- markdown non-empty, says the four required descriptors, sections.

def test_markdown_template_only_and_execution_free():
    c = _active_contract()
    md = render_decision_ledger_contract_markdown(c)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Decision Ledger Contract" in md
    assert "Template only" in md
    assert "decision-ledger-contract-only" in md
    assert "no-runtime-ledger-write" in md
    assert "research-only" in md
    assert "execution-free" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Decision ledger contract active: True" in md
    assert "Next gate: SAFETY_KILL_SWITCH_CONTRACT_REQUIRED" in md
    assert "## Ledger Entry Fields" in md
    assert "## Allowed Decision Values" in md
    assert "## Required Human Review Fields" in md
    assert "## Required Safety Attestation Fields" in md
    assert "## Required Evidence Placeholders" in md
    assert "## Decision Blocking Reasons" in md
    assert "## Expected Audit Fields" in md
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


# 25 -- prose verb audit over notes / reasons / source / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _active_contract()

    texts.extend(str(s) for s in c["operator_notes"])
    texts.extend(str(s) for s in c["decision_blocking_reasons"])
    for key in (
        "source_protocol_reference_placeholder",
        "source_runner_contract_reference_placeholder",
        "source_orchestrator_reference_placeholder",
        "source_dashboard_feed_reference_placeholder",
    ):
        texts.append(str(c[key]))

    md = render_decision_ledger_contract_markdown(c)
    for ln in md.splitlines():
        stripped = ln.lstrip()
        # skip headings, backtick key/value bullets, and `Label: value`
        # metadata header lines -- those are DATA / type descriptors, not
        # narrative prose. The self-descriptive safety banner ("Template
        # only: ... decision-ledger-contract-only ...") is a metadata header
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
        '"sparta_commander/strategy_factory_decision_ledger_contract.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_decision_ledger_contract.py"'
        in src
    )


# 28 -- Bundle 24 regression import still works.

def test_bundle24_regression_import_still_works():
    from sparta_commander.strategy_factory_dashboard_registry_feed_contract import (
        build_dashboard_registry_feed_contract as build24,
    )
    c = build24(_blocked_orchestrator())
    assert c["executes"] is False
    assert c["read_only"] is True


def _blocked_orchestrator() -> dict:
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(draft)
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    return build_dry_run_orchestrator_contract(runner)


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
