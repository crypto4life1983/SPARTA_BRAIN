"""Bundle 19 tests for the Strategy Factory Protocol Review Gate v1
(informational, read-only, gate-only).

Bundle 19's production module imports Bundles 11-18 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 19 spec):
- module imports cleanly + public API limited to expected names,
- schema version / label / status / state / gate constants pinned,
- pure stdlib import-root audit + forbidden-surface audit,
- all 14 posture keys present + all False + keys match Bundle 18,
- posture is mutation-isolated (fresh dicts),
- gate accepts only contracts with next_gate=PROTOCOL_REVIEW_REQUIRED,
- the five review states resolve correctly,
- a non-accepted contract never advances and stays awaiting,
- unknown / malformed review decisions never raise and default to awaiting,
- no execution/data/backtest/simulation/broker/upload/autopilot/live flag True,
- data-contract planning unlock only on READY decision of an accepted gate,
- validate passes + detects failure modes; validation not self-required,
- markdown is non-empty, says gate-only + execution-free, writes nothing,
- prose verb audit over operator notes / markdown prose,
- scoped dirty-tree guard, Bundle 11-18 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_protocol_review_gate import (
    PROTOCOL_REVIEW_GATE_SCHEMA_VERSION,
    DEFAULT_PROTOCOL_REVIEW_GATE_LABEL,
    PROTOCOL_REVIEW_GATE_STATUS,
    PROTOCOL_REVIEW_GATE_SAFETY_POSTURE,
    REVIEW_STATE_AWAITING_HUMAN_PROTOCOL_REVIEW,
    REVIEW_STATE_NEEDS_PROTOCOL_FIXES,
    REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    REVIEW_STATE_PARK_PROTOCOL,
    REVIEW_STATE_REJECT_PROTOCOL,
    ALLOWED_REVIEW_DECISIONS,
    NEXT_GATE_AWAIT_HUMAN_PROTOCOL_REVIEW,
    NEXT_GATE_RETURN_TO_PROTOCOL_DRAFT,
    NEXT_GATE_DATA_CONTRACT_PLANNING_REVIEW,
    NEXT_GATE_PROTOCOL_PARKED,
    NEXT_GATE_PROTOCOL_REJECTED,
    build_protocol_review_gate,
    validate_protocol_review_gate,
    render_protocol_review_gate_markdown,
)
import sparta_commander.strategy_factory_protocol_review_gate as RG
from sparta_commander.strategy_factory_research_protocol_draft_contract import (
    RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE,
    build_research_protocol_draft_contract,
)
from sparta_commander.strategy_factory_research_decision_memo_contract import (
    MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
    MEMO_DECISION_NEEDS_MORE_SPEC,
)
from sparta_commander.strategy_factory_research_queue import (
    build_research_queue_item,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_protocol_review_gate.py"
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


def _open_contract() -> dict:
    """A Bundle 18 contract that is open for review (PROTOCOL_REVIEW_REQUIRED)."""
    return build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )


def _blocked_contract() -> dict:
    """A Bundle 18 contract that is NOT open for review."""
    return build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_NEEDS_MORE_SPEC,
        human_research_approved=True,
    )


def _expected_public() -> set[str]:
    return {
        "PROTOCOL_REVIEW_GATE_SCHEMA_VERSION",
        "DEFAULT_PROTOCOL_REVIEW_GATE_LABEL",
        "PROTOCOL_REVIEW_GATE_STATUS",
        "PROTOCOL_REVIEW_GATE_SAFETY_POSTURE",
        "REVIEW_STATE_AWAITING_HUMAN_PROTOCOL_REVIEW",
        "REVIEW_STATE_NEEDS_PROTOCOL_FIXES",
        "REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING",
        "REVIEW_STATE_PARK_PROTOCOL",
        "REVIEW_STATE_REJECT_PROTOCOL",
        "ALLOWED_REVIEW_DECISIONS",
        "NEXT_GATE_AWAIT_HUMAN_PROTOCOL_REVIEW",
        "NEXT_GATE_RETURN_TO_PROTOCOL_DRAFT",
        "NEXT_GATE_DATA_CONTRACT_PLANNING_REVIEW",
        "NEXT_GATE_PROTOCOL_PARKED",
        "NEXT_GATE_PROTOCOL_REJECTED",
        "build_protocol_review_gate",
        "validate_protocol_review_gate",
        "render_protocol_review_gate_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(RG.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(RG, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        PROTOCOL_REVIEW_GATE_SCHEMA_VERSION
        == "strategy_factory_protocol_review_gate.v1"
    )


# 3 -- label / status pinned.

def test_label_and_status_pinned():
    assert (
        DEFAULT_PROTOCOL_REVIEW_GATE_LABEL
        == "Strategy Factory Protocol Review Gate"
    )
    assert PROTOCOL_REVIEW_GATE_STATUS == "READ_ONLY_PROTOCOL_REVIEW_GATE"


# 4 -- review state constants pinned.

def test_review_state_constants_pinned():
    assert (
        REVIEW_STATE_AWAITING_HUMAN_PROTOCOL_REVIEW
        == "AWAITING_HUMAN_PROTOCOL_REVIEW"
    )
    assert REVIEW_STATE_NEEDS_PROTOCOL_FIXES == "NEEDS_PROTOCOL_FIXES"
    assert (
        REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING
        == "READY_FOR_DATA_CONTRACT_PLANNING"
    )
    assert REVIEW_STATE_PARK_PROTOCOL == "PARK_PROTOCOL"
    assert REVIEW_STATE_REJECT_PROTOCOL == "REJECT_PROTOCOL"


# 5 -- allowed review decisions are exactly the five states.

def test_allowed_review_decisions_are_the_five_states():
    assert ALLOWED_REVIEW_DECISIONS == (
        "AWAITING_HUMAN_PROTOCOL_REVIEW",
        "NEEDS_PROTOCOL_FIXES",
        "READY_FOR_DATA_CONTRACT_PLANNING",
        "PARK_PROTOCOL",
        "REJECT_PROTOCOL",
    )


# 6 -- next-gate constants pinned.

def test_next_gate_constants_pinned():
    assert NEXT_GATE_AWAIT_HUMAN_PROTOCOL_REVIEW == "AWAIT_HUMAN_PROTOCOL_REVIEW"
    assert NEXT_GATE_RETURN_TO_PROTOCOL_DRAFT == "RETURN_TO_PROTOCOL_DRAFT"
    assert (
        NEXT_GATE_DATA_CONTRACT_PLANNING_REVIEW
        == "DATA_CONTRACT_PLANNING_REVIEW_REQUIRED"
    )
    assert NEXT_GATE_PROTOCOL_PARKED == "PROTOCOL_PARKED"
    assert NEXT_GATE_PROTOCOL_REJECTED == "PROTOCOL_REJECTED"


# 7 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = PROTOCOL_REVIEW_GATE_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 8 -- posture keys match Bundle 18.

def test_posture_keys_match_bundle18():
    assert (
        set(PROTOCOL_REVIEW_GATE_SAFETY_POSTURE.keys())
        == set(RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE.keys())
    )


# 9 -- pure stdlib import-root audit: allowed roots only.

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


# 10 -- forbidden-surface audit: no file/network/subprocess/exec surface.

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


# 11 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = build_protocol_review_gate(_open_contract())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_protocol_review_gate(_open_contract())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        PROTOCOL_REVIEW_GATE_SAFETY_POSTURE["automation_enabled"] is False
    )


# 12 -- gate accepts a contract open for review (default awaiting state).

def test_open_contract_is_accepted_and_awaits():
    g = build_protocol_review_gate(_open_contract())
    assert g["gate_accepts_contract"] is True
    assert g["review_state"] == "AWAITING_HUMAN_PROTOCOL_REVIEW"
    assert g["next_gate"] == "AWAIT_HUMAN_PROTOCOL_REVIEW"
    assert g["data_contract_planning_unlocked"] is False


# 13 -- READY decision on an accepted gate unlocks data-contract planning.

def test_ready_decision_unlocks_data_contract_planning():
    g = build_protocol_review_gate(
        _open_contract(),
        review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    )
    assert g["gate_accepts_contract"] is True
    assert g["review_state"] == "READY_FOR_DATA_CONTRACT_PLANNING"
    assert g["next_gate"] == "DATA_CONTRACT_PLANNING_REVIEW_REQUIRED"
    assert g["data_contract_planning_unlocked"] is True


# 14 -- NEEDS_PROTOCOL_FIXES returns to redrafting.

def test_needs_fixes_returns_to_draft():
    g = build_protocol_review_gate(
        _open_contract(),
        review_decision=REVIEW_STATE_NEEDS_PROTOCOL_FIXES,
    )
    assert g["review_state"] == "NEEDS_PROTOCOL_FIXES"
    assert g["next_gate"] == "RETURN_TO_PROTOCOL_DRAFT"
    assert g["data_contract_planning_unlocked"] is False


# 15 -- PARK decision parks the protocol.

def test_park_decision_parks_protocol():
    g = build_protocol_review_gate(
        _open_contract(), review_decision=REVIEW_STATE_PARK_PROTOCOL)
    assert g["review_state"] == "PARK_PROTOCOL"
    assert g["next_gate"] == "PROTOCOL_PARKED"
    assert g["data_contract_planning_unlocked"] is False


# 16 -- REJECT decision rejects the protocol.

def test_reject_decision_rejects_protocol():
    g = build_protocol_review_gate(
        _open_contract(), review_decision=REVIEW_STATE_REJECT_PROTOCOL)
    assert g["review_state"] == "REJECT_PROTOCOL"
    assert g["next_gate"] == "PROTOCOL_REJECTED"
    assert g["data_contract_planning_unlocked"] is False


# 17 -- a non-accepted (blocked) contract never advances.

def test_blocked_contract_not_accepted_and_awaits():
    g = build_protocol_review_gate(
        _blocked_contract(),
        review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    )
    assert g["gate_accepts_contract"] is False
    # even with a READY decision, a non-accepted gate stays awaiting.
    assert g["review_state"] == "AWAITING_HUMAN_PROTOCOL_REVIEW"
    assert g["next_gate"] == "AWAIT_HUMAN_PROTOCOL_REVIEW"
    assert g["data_contract_planning_unlocked"] is False


# 18 -- unknown review decision defaults to awaiting (accepted contract).

def test_unknown_decision_defaults_to_awaiting():
    g = build_protocol_review_gate(
        _open_contract(), review_decision="YOLO_SHIP_IT")
    assert g["review_state"] == "AWAITING_HUMAN_PROTOCOL_REVIEW"
    assert g["next_gate"] == "AWAIT_HUMAN_PROTOCOL_REVIEW"


# 19 -- malformed contract never raises and never advances.

def test_malformed_contract_no_raise():
    for bad in (None, 42, "nope", {}, {"next_gate": "WRONG"}, []):
        g = build_protocol_review_gate(
            bad,
            review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
        )
        assert g["gate_accepts_contract"] is False
        assert g["review_state"] == "AWAITING_HUMAN_PROTOCOL_REVIEW"
        assert g["data_contract_planning_unlocked"] is False
        assert g["read_only"] is True
        assert g["executes"] is False
        for flag in _AUTH_FLAGS:
            assert g[flag] is False
        assert g["validation"]["valid"] is True


# 20 -- no authorization flag can become True (any decision / acceptance).

def test_authorization_flags_always_false():
    gates = [build_protocol_review_gate(_blocked_contract())]
    for decision in ALLOWED_REVIEW_DECISIONS:
        gates.append(
            build_protocol_review_gate(
                _open_contract(), review_decision=decision)
        )
    for g in gates:
        for flag in _AUTH_FLAGS:
            assert g[flag] is False
        assert all(v is False for v in g["safety_posture"].values())
        assert g["executes"] is False
        assert g["read_only"] is True
        assert g["human_approval_required"] is True
        assert g["stage"] == "PLAN_ONLY"
        assert g["mode"] == "RESEARCH_ONLY"


# 21 -- data-contract planning unlock is the ONLY forward signal, and is read
#       only -- it never sets a data/backtest authorization flag.

def test_unlock_does_not_authorize_data_or_backtest():
    g = build_protocol_review_gate(
        _open_contract(),
        review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    )
    assert g["data_contract_planning_unlocked"] is True
    assert g["data_fetch_authorized"] is False
    assert g["backtest_authorized"] is False
    assert g["execution_authorized"] is False


# 22 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    g = build_protocol_review_gate(_open_contract())
    blocked = set(g["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 23 -- idea id / title carried from the accepted contract.

def test_idea_id_and_title_carried_through():
    g = build_protocol_review_gate(_open_contract())
    assert g["idea_id"] == "idea-001"
    assert g["title"] == "Opening Range Mean Reversion"


# 24 -- the embedded protocol draft contract is preserved.

def test_protocol_draft_contract_embedded():
    c = _open_contract()
    g = build_protocol_review_gate(c)
    assert g["protocol_draft_contract"]["schema_version"] == (
        c["schema_version"]
    )
    assert g["protocol_draft_contract"]["read_only"] is True


# 25 -- validate passes for accepted gates + detects failure modes.

def test_validate_passes_and_detects_failures():
    import copy
    g = build_protocol_review_gate(
        _open_contract(),
        review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    )
    v = validate_protocol_review_gate(g)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(g)
    bad["execution_authorized"] = True
    assert validate_protocol_review_gate(bad)["valid"] is False

    bad2 = copy.deepcopy(g)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_protocol_review_gate(bad2)["valid"] is False

    bad3 = copy.deepcopy(g)
    bad3["mode"] = "LIVE"
    assert validate_protocol_review_gate(bad3)["valid"] is False

    bad4 = copy.deepcopy(g)
    bad4["next_gate"] = "PROTOCOL_PARKED"  # inconsistent with READY state
    assert validate_protocol_review_gate(bad4)["valid"] is False


# 26 -- validate rejects an unlock that is inconsistent with the state.

def test_validate_rejects_inconsistent_unlock():
    import copy
    g = build_protocol_review_gate(_open_contract())  # awaiting, unlock False
    bad = copy.deepcopy(g)
    bad["data_contract_planning_unlocked"] = True  # not READY -> inconsistent
    assert validate_protocol_review_gate(bad)["valid"] is False


# 27 -- validate never requires the gate's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    g = copy.deepcopy(build_protocol_review_gate(_open_contract()))
    g.pop("validation", None)
    v = validate_protocol_review_gate(g)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 28 -- fresh dicts; mutation of one result does not taint the next.

def test_results_are_fresh_and_isolated():
    a = build_protocol_review_gate(_open_contract())
    b = build_protocol_review_gate(_open_contract())
    assert a == b
    assert a is not b
    a["blocked_capabilities"] = ()
    a["protocol_draft_contract"]["read_only"] = False
    fresh = build_protocol_review_gate(_open_contract())
    assert len(fresh["blocked_capabilities"]) >= 1
    assert fresh["protocol_draft_contract"]["read_only"] is True


# 29 -- markdown non-empty, says gate-only + execution-free, sections.

def test_markdown_gate_only_and_execution_free():
    g = build_protocol_review_gate(
        _open_contract(),
        review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    )
    md = render_protocol_review_gate_markdown(g)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Protocol Review Gate" in md
    assert "Gate only" in md
    assert "execution-free" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Review state: READY_FOR_DATA_CONTRACT_PLANNING" in md
    assert "Next gate: DATA_CONTRACT_PLANNING_REVIEW_REQUIRED" in md
    assert "## Allowed Review Decisions" in md
    assert "## Blocked Capabilities" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 30 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 31 -- prose verb audit over operator notes / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    g = build_protocol_review_gate(
        _open_contract(),
        review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    )

    texts.extend(str(s) for s in g["operator_notes"])

    md = render_protocol_review_gate_markdown(g)
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


# 32 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 33 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_protocol_review_gate.py"' in src
    )
    assert (
        '"tests/test_strategy_factory_protocol_review_gate.py"' in src
    )


# 34 -- Bundle 17 regression import still works.

def test_bundle17_regression_import_still_works():
    from sparta_commander.strategy_factory_research_pipeline_closure import (
        build_research_pipeline_closure_report,
    )
    r = build_research_pipeline_closure_report()
    assert r["executes"] is False
    assert r["phase_complete"] is True


# 35 -- Bundle 18 regression import still works.

def test_bundle18_regression_import_still_works():
    from sparta_commander.strategy_factory_research_protocol_draft_contract \
        import build_research_protocol_draft_contract as build18
    c = build18(_good_item())
    assert c["executes"] is False
    assert c["read_only"] is True


# 36 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
