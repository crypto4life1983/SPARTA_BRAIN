"""Bundle 18 tests for the Strategy Factory Research Protocol Draft Contract v1
(informational, read-only, template-only).

Bundle 18's production module imports Bundles 11-16 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 18 spec):
- module imports cleanly + public API limited to expected names,
- schema version / label / status / state / gate constants pinned,
- pure stdlib import-root audit + forbidden-surface audit,
- all 14 posture keys present + all False + keys match Bundle 16,
- posture is mutation-isolated (fresh dicts),
- READY_FOR_PROTOCOL_DRAFT (with approval) activates the draft contract,
- NEEDS_MORE_SPEC / PARK / REJECT do not activate,
- unapproved / invalid / malformed never activate and never raise,
- next_gate is PROTOCOL_REVIEW_REQUIRED when active,
- no execution/data/backtest/broker/upload/autopilot/live flag can be True,
- the 11 required template fields are present,
- blocked_capabilities include the required set,
- markdown is non-empty, says template-only + execution-free, writes nothing,
- prose verb audit over placeholders / operator notes / markdown prose,
- scoped dirty-tree guard, Bundle 11-16 regression imports,
- commander_2_safety allowlist contains exactly the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_research_protocol_draft_contract import (
    RESEARCH_PROTOCOL_DRAFT_CONTRACT_SCHEMA_VERSION,
    DEFAULT_RESEARCH_PROTOCOL_DRAFT_CONTRACT_LABEL,
    RESEARCH_PROTOCOL_DRAFT_CONTRACT_STATUS,
    RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE,
    PROTOCOL_DRAFT_STATE_ACTIVE,
    PROTOCOL_DRAFT_STATE_BLOCKED,
    NEXT_GATE_PROTOCOL_REVIEW_REQUIRED,
    NEXT_GATE_AWAIT_PROTOCOL_DRAFT_DECISION,
    build_research_protocol_draft_contract,
    validate_research_protocol_draft_contract,
    render_research_protocol_draft_contract_markdown,
)
import sparta_commander.strategy_factory_research_protocol_draft_contract as PD
from sparta_commander.strategy_factory_research_decision_memo_contract import (
    RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE,
    MEMO_DECISION_NEEDS_MORE_SPEC,
    MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
    MEMO_DECISION_PARK_RESEARCH_ONLY,
    MEMO_DECISION_REJECT_RESEARCH_ONLY,
)
from sparta_commander.strategy_factory_research_queue import (
    build_research_queue_item,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_research_protocol_draft_contract.py"
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
    "objective", "hypothesis_restated", "asset_lane", "timeframe_lane",
    "required_sections", "success_criteria_placeholders",
    "invalidation_criteria_placeholders", "blocked_capabilities",
    "safety_posture", "next_gate", "operator_notes",
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


def _active_contract() -> dict:
    return build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )


def _expected_public() -> set[str]:
    return {
        "RESEARCH_PROTOCOL_DRAFT_CONTRACT_SCHEMA_VERSION",
        "DEFAULT_RESEARCH_PROTOCOL_DRAFT_CONTRACT_LABEL",
        "RESEARCH_PROTOCOL_DRAFT_CONTRACT_STATUS",
        "RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE",
        "PROTOCOL_DRAFT_STATE_ACTIVE",
        "PROTOCOL_DRAFT_STATE_BLOCKED",
        "NEXT_GATE_PROTOCOL_REVIEW_REQUIRED",
        "NEXT_GATE_AWAIT_PROTOCOL_DRAFT_DECISION",
        "build_research_protocol_draft_contract",
        "validate_research_protocol_draft_contract",
        "render_research_protocol_draft_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(PD.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(PD, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        RESEARCH_PROTOCOL_DRAFT_CONTRACT_SCHEMA_VERSION
        == "strategy_factory_research_protocol_draft_contract.v1"
    )


# 3 -- label / status pinned.

def test_label_and_status_pinned():
    assert (
        DEFAULT_RESEARCH_PROTOCOL_DRAFT_CONTRACT_LABEL
        == "Strategy Factory Research Protocol Draft Contract"
    )
    assert (
        RESEARCH_PROTOCOL_DRAFT_CONTRACT_STATUS
        == "READ_ONLY_PROTOCOL_DRAFT_CONTRACT"
    )


# 4 -- state / gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert PROTOCOL_DRAFT_STATE_ACTIVE == "PROTOCOL_DRAFT_ACTIVE"
    assert PROTOCOL_DRAFT_STATE_BLOCKED == "PROTOCOL_DRAFT_BLOCKED"
    assert NEXT_GATE_PROTOCOL_REVIEW_REQUIRED == "PROTOCOL_REVIEW_REQUIRED"
    assert (
        NEXT_GATE_AWAIT_PROTOCOL_DRAFT_DECISION
        == "AWAIT_PROTOCOL_DRAFT_DECISION"
    )


# 5 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 6 -- posture keys match Bundle 16.

def test_posture_keys_match_bundle16():
    assert (
        set(RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE.keys())
        == set(RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE.keys())
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
    a = build_research_protocol_draft_contract(_good_item())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_research_protocol_draft_contract(_good_item())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE["automation_enabled"]
        is False
    )


# 10 -- READY_FOR_PROTOCOL_DRAFT (with approval) activates the contract.

def test_ready_for_protocol_draft_activates():
    c = _active_contract()
    assert c["protocol_draft_active"] is True
    assert c["protocol_draft_state"] == "PROTOCOL_DRAFT_ACTIVE"
    assert c["next_gate"] == "PROTOCOL_REVIEW_REQUIRED"
    assert c["decision_memo_allowed"] is True


# 11 -- NEEDS_MORE_SPEC does not activate.

def test_needs_more_spec_does_not_activate():
    c = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_NEEDS_MORE_SPEC,
        human_research_approved=True,
    )
    assert c["protocol_draft_active"] is False
    assert c["protocol_draft_state"] == "PROTOCOL_DRAFT_BLOCKED"
    assert c["next_gate"] == "AWAIT_PROTOCOL_DRAFT_DECISION"


# 12 -- PARK does not activate.

def test_park_does_not_activate():
    c = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_PARK_RESEARCH_ONLY,
        human_research_approved=True,
    )
    assert c["protocol_draft_active"] is False
    assert c["next_gate"] == "AWAIT_PROTOCOL_DRAFT_DECISION"


# 13 -- REJECT does not activate.

def test_reject_does_not_activate():
    c = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_REJECT_RESEARCH_ONLY,
        human_research_approved=True,
    )
    assert c["protocol_draft_active"] is False
    assert c["next_gate"] == "AWAIT_PROTOCOL_DRAFT_DECISION"


# 14 -- READY decision but unapproved item does not activate.

def test_ready_but_unapproved_does_not_activate():
    c = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=False,
    )
    assert c["decision_memo_allowed"] is False
    assert c["protocol_draft_active"] is False
    assert c["next_gate"] == "AWAIT_PROTOCOL_DRAFT_DECISION"


# 15 -- READY decision but invalid item does not activate.

def test_ready_but_invalid_item_does_not_activate():
    c = build_research_protocol_draft_contract(
        build_research_queue_item("", "", ""),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    assert c["decision_memo_allowed"] is False
    assert c["protocol_draft_active"] is False


# 16 -- no memo_decision given defaults to non-active.

def test_default_decision_does_not_activate():
    c = build_research_protocol_draft_contract(
        _good_item(), human_research_approved=True)
    assert c["memo_decision"] == "NEEDS_MORE_SPEC"
    assert c["protocol_draft_active"] is False


# 17 -- malformed item never raises and never activates.

def test_malformed_item_no_raise():
    for bad in (None, 42, "nope", {}, {"idea_id": ""}, []):
        c = build_research_protocol_draft_contract(
            bad,
            memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
            human_research_approved=True,
        )
        assert c["protocol_draft_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert c["validation"]["valid"] is True


# 18 -- no authorization flag can become True (active or blocked).

def test_authorization_flags_always_false():
    for c in (
        _active_contract(),
        build_research_protocol_draft_contract(_good_item()),
    ):
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["stage"] == "PLAN_ONLY"
        assert c["mode"] == "RESEARCH_ONLY"


# 19 -- the 11 required template fields are present.

def test_required_template_fields_present():
    c = _active_contract()
    for field in _REQUIRED_TEMPLATE_FIELDS:
        assert field in c, field
    assert isinstance(c["required_sections"], tuple)
    assert len(c["required_sections"]) >= 1
    assert c["asset_lane"] == "MNQ"
    assert c["timeframe_lane"] == "5m"


# 20 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    c = _active_contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 21 -- validate passes for an active contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _active_contract()
    v = validate_research_protocol_draft_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_research_protocol_draft_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_research_protocol_draft_contract(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_research_protocol_draft_contract(bad3)["valid"] is False


# 22 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_active_contract())
    c.pop("validation", None)
    v = validate_research_protocol_draft_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 23 -- fresh dicts; mutation of one result does not taint the next.

def test_results_are_fresh_and_isolated():
    a = _active_contract()
    b = _active_contract()
    assert a == b
    assert a is not b
    a["required_sections"] = ()
    a["decision_memo_contract"]["read_only"] = False
    fresh = _active_contract()
    assert len(fresh["required_sections"]) >= 1
    assert fresh["decision_memo_contract"]["read_only"] is True


# 24 -- markdown non-empty, says template-only + execution-free, sections.

def test_markdown_template_only_and_execution_free():
    c = _active_contract()
    md = render_research_protocol_draft_contract_markdown(c)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Research Protocol Draft Contract" in md
    assert "Template only" in md
    assert "execution-free" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Protocol draft active: True" in md
    assert "Next gate: PROTOCOL_REVIEW_REQUIRED" in md
    assert "## Required Sections" in md
    assert "## Success Criteria Placeholders" in md
    assert "## Invalidation Criteria Placeholders" in md
    assert "## Blocked Capabilities" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 25 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 26 -- prose verb audit over placeholders / operator notes / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _active_contract()

    texts.extend(str(s) for s in c["success_criteria_placeholders"])
    texts.extend(str(s) for s in c["invalidation_criteria_placeholders"])
    texts.extend(str(s) for s in c["operator_notes"])

    md = render_research_protocol_draft_contract_markdown(c)
    for ln in md.splitlines():
        stripped = ln.lstrip()
        # skip headings, backtick key/value bullets, and `Label: value`
        # metadata header lines -- those are DATA, not narrative prose.
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


# 27 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 28 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_research_protocol_draft_contract.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_research_protocol_draft_contract.py"'
        in src
    )


# 29 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0


# 30 -- Bundle 12 regression import still works.

def test_bundle12_regression_import_still_works():
    from sparta_commander.strategy_factory_queue_reader import (
        build_queue_reader_summary,
    )
    s = build_queue_reader_summary((_good_item(),))
    assert s["executes"] is False
    assert s["valid_item_count"] == 1


# 31 -- Bundle 13 regression import still works.

def test_bundle13_regression_import_still_works():
    from sparta_commander.strategy_factory_queue_planner import (
        build_queue_plan_summary,
    )
    s = build_queue_plan_summary((_good_item(),))
    assert s["executes"] is False
    assert s["valid_item_count"] == 1


# 32 -- Bundle 14 regression import still works.

def test_bundle14_regression_import_still_works():
    from sparta_commander.strategy_factory_research_task_packet import (
        build_research_task_packet_batch,
    )
    b = build_research_task_packet_batch((_good_item(),))
    assert b["executes"] is False
    assert b["total_items"] == 1


# 33 -- Bundle 15 regression import still works.

def test_bundle15_regression_import_still_works():
    from sparta_commander.strategy_factory_research_report_contract import (
        build_research_report_contract_batch,
    )
    b = build_research_report_contract_batch((_good_item(),))
    assert b["executes"] is False
    assert b["total_items"] == 1


# 34 -- Bundle 16 regression import still works.

def test_bundle16_regression_import_still_works():
    from sparta_commander.strategy_factory_research_decision_memo_contract \
        import build_research_decision_memo_contract_batch
    b = build_research_decision_memo_contract_batch((_good_item(),))
    assert b["executes"] is False
    assert b["total_items"] == 1
