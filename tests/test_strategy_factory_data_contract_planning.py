"""Bundle 20 tests for the Strategy Factory Data Contract Planning template v1
(informational, read-only, template-only -- NO real data access).

Bundle 20's production module imports Bundles 11-19 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 20 spec):
- module imports cleanly + public API limited to expected names,
- schema version / label / status / state / gate constants pinned,
- pure stdlib import-root audit + forbidden-surface audit,
- all 14 posture keys present + all False + keys match Bundle 19,
- posture is mutation-isolated (fresh dicts),
- activates only on READY_FOR_DATA_CONTRACT_PLANNING + unlocked True,
- blocked / not-unlocked / malformed gates never activate and never raise,
- next_gate defaults to DATA_QA_CONTRACT_REQUIRED when active,
- no execution/data/backtest/simulation/broker/upload/autopilot/live flag True,
- the 11 template description fields present,
- blocked_capabilities include the required set,
- validate passes + detects failure modes; validation not self-required,
- markdown non-empty, says template-only + execution-free, writes nothing,
- prose verb audit over placeholders / questions / operator notes / markdown,
- scoped dirty-tree guard, Bundle 11-19 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_data_contract_planning import (
    DATA_CONTRACT_PLANNING_SCHEMA_VERSION,
    DEFAULT_DATA_CONTRACT_PLANNING_LABEL,
    DATA_CONTRACT_PLANNING_STATUS,
    DATA_CONTRACT_PLANNING_SAFETY_POSTURE,
    PLANNING_STATE_ACTIVE,
    PLANNING_STATE_BLOCKED,
    NEXT_GATE_DATA_QA_CONTRACT_REQUIRED,
    NEXT_GATE_AWAIT_PLANNING_UNLOCK,
    build_data_contract_planning,
    validate_data_contract_planning,
    render_data_contract_planning_markdown,
)
import sparta_commander.strategy_factory_data_contract_planning as DC
from sparta_commander.strategy_factory_protocol_review_gate import (
    PROTOCOL_REVIEW_GATE_SAFETY_POSTURE,
    REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    REVIEW_STATE_NEEDS_PROTOCOL_FIXES,
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
    / "strategy_factory_data_contract_planning.py"
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
    "asset_lane", "timeframe_lane", "required_data_fields",
    "expected_granularity", "coverage_window_placeholder",
    "fee_slippage_assumption_placeholders", "data_quality_questions",
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


def _open_contract() -> dict:
    return build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )


def _ready_gate() -> dict:
    """A Bundle 19 gate with a READY decision -> planning unlocked."""
    return build_protocol_review_gate(
        _open_contract(),
        review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    )


def _awaiting_gate() -> dict:
    """A Bundle 19 gate that accepts the contract but is still awaiting."""
    return build_protocol_review_gate(_open_contract())


def _fixes_gate() -> dict:
    """A Bundle 19 gate with a NEEDS_PROTOCOL_FIXES decision (not unlocked)."""
    return build_protocol_review_gate(
        _open_contract(), review_decision=REVIEW_STATE_NEEDS_PROTOCOL_FIXES)


def _active_contract() -> dict:
    return build_data_contract_planning(_ready_gate())


def _expected_public() -> set[str]:
    return {
        "DATA_CONTRACT_PLANNING_SCHEMA_VERSION",
        "DEFAULT_DATA_CONTRACT_PLANNING_LABEL",
        "DATA_CONTRACT_PLANNING_STATUS",
        "DATA_CONTRACT_PLANNING_SAFETY_POSTURE",
        "PLANNING_STATE_ACTIVE",
        "PLANNING_STATE_BLOCKED",
        "NEXT_GATE_DATA_QA_CONTRACT_REQUIRED",
        "NEXT_GATE_AWAIT_PLANNING_UNLOCK",
        "build_data_contract_planning",
        "validate_data_contract_planning",
        "render_data_contract_planning_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(DC.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(DC, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        DATA_CONTRACT_PLANNING_SCHEMA_VERSION
        == "strategy_factory_data_contract_planning.v1"
    )


# 3 -- label / status pinned.

def test_label_and_status_pinned():
    assert (
        DEFAULT_DATA_CONTRACT_PLANNING_LABEL
        == "Strategy Factory Data Contract Planning"
    )
    assert DATA_CONTRACT_PLANNING_STATUS == "READ_ONLY_DATA_CONTRACT_PLANNING"


# 4 -- state / gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert PLANNING_STATE_ACTIVE == "DATA_CONTRACT_PLANNING_ACTIVE"
    assert PLANNING_STATE_BLOCKED == "DATA_CONTRACT_PLANNING_BLOCKED"
    assert NEXT_GATE_DATA_QA_CONTRACT_REQUIRED == "DATA_QA_CONTRACT_REQUIRED"
    assert NEXT_GATE_AWAIT_PLANNING_UNLOCK == "AWAIT_PLANNING_UNLOCK"


# 5 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = DATA_CONTRACT_PLANNING_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 6 -- posture keys match Bundle 19.

def test_posture_keys_match_bundle19():
    assert (
        set(DATA_CONTRACT_PLANNING_SAFETY_POSTURE.keys())
        == set(PROTOCOL_REVIEW_GATE_SAFETY_POSTURE.keys())
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
    a = build_data_contract_planning(_ready_gate())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_data_contract_planning(_ready_gate())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert (
        DATA_CONTRACT_PLANNING_SAFETY_POSTURE["automation_enabled"] is False
    )


# 10 -- READY + unlocked activates the planning template.

def test_ready_and_unlocked_activates():
    c = _active_contract()
    assert c["planning_active"] is True
    assert c["planning_state"] == "DATA_CONTRACT_PLANNING_ACTIVE"
    assert c["next_gate"] == "DATA_QA_CONTRACT_REQUIRED"
    assert c["data_contract_planning_unlocked"] is True
    assert c["gate_review_state"] == "READY_FOR_DATA_CONTRACT_PLANNING"


# 11 -- an awaiting gate (accepted, not unlocked) does not activate.

def test_awaiting_gate_does_not_activate():
    c = build_data_contract_planning(_awaiting_gate())
    assert c["planning_active"] is False
    assert c["planning_state"] == "DATA_CONTRACT_PLANNING_BLOCKED"
    assert c["next_gate"] == "AWAIT_PLANNING_UNLOCK"
    assert c["data_contract_planning_unlocked"] is False


# 12 -- a NEEDS_PROTOCOL_FIXES gate does not activate.

def test_fixes_gate_does_not_activate():
    c = build_data_contract_planning(_fixes_gate())
    assert c["planning_active"] is False
    assert c["next_gate"] == "AWAIT_PLANNING_UNLOCK"


# 13 -- a gate that reads READY but is not unlocked does not activate.

def test_ready_state_without_unlock_does_not_activate():
    import copy
    g = copy.deepcopy(_ready_gate())
    g["data_contract_planning_unlocked"] = False  # tamper: unlock revoked
    c = build_data_contract_planning(g)
    assert c["planning_active"] is False
    assert c["next_gate"] == "AWAIT_PLANNING_UNLOCK"


# 14 -- malformed gate never raises and never activates.

def test_malformed_gate_no_raise():
    for bad in (None, 42, "nope", {}, {"review_state": "READY"}, []):
        c = build_data_contract_planning(bad)
        assert c["planning_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert c["validation"]["valid"] is True


# 15 -- no authorization flag can become True (active or blocked).

def test_authorization_flags_always_false():
    for c in (_active_contract(), build_data_contract_planning(_fixes_gate())):
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["stage"] == "PLAN_ONLY"
        assert c["mode"] == "RESEARCH_ONLY"


# 16 -- activation never sets a data/backtest authorization flag.

def test_active_does_not_authorize_data_or_backtest():
    c = _active_contract()
    assert c["planning_active"] is True
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["backtest_enabled"] is False


# 17 -- the 11 required template description fields are present.

def test_required_template_fields_present():
    c = _active_contract()
    for field in _REQUIRED_TEMPLATE_FIELDS:
        assert field in c, field
    assert isinstance(c["required_data_fields"], tuple)
    assert len(c["required_data_fields"]) >= 1
    assert c["asset_lane"] == "MNQ"
    assert c["timeframe_lane"] == "5m"
    assert isinstance(c["data_quality_questions"], tuple)
    assert len(c["data_quality_questions"]) >= 1
    assert isinstance(c["fee_slippage_assumption_placeholders"], tuple)


# 18 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    c = _active_contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 19 -- expected granularity reflects the timeframe lane.

def test_expected_granularity_reflects_timeframe():
    c = _active_contract()
    assert "5m" in c["expected_granularity"]


# 20 -- the embedded review gate is preserved.

def test_review_gate_embedded():
    g = _ready_gate()
    c = build_data_contract_planning(g)
    assert c["protocol_review_gate"]["schema_version"] == g["schema_version"]
    assert c["protocol_review_gate"]["read_only"] is True


# 21 -- validate passes for an active contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _active_contract()
    v = validate_data_contract_planning(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_data_contract_planning(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_data_contract_planning(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_data_contract_planning(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["required_data_fields"] = ()
    assert validate_data_contract_planning(bad4)["valid"] is False


# 22 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_active_contract())
    c.pop("validation", None)
    v = validate_data_contract_planning(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 23 -- fresh dicts; mutation of one result does not taint the next.

def test_results_are_fresh_and_isolated():
    a = _active_contract()
    b = _active_contract()
    assert a == b
    assert a is not b
    a["required_data_fields"] = ()
    a["protocol_review_gate"]["read_only"] = False
    fresh = _active_contract()
    assert len(fresh["required_data_fields"]) >= 1
    assert fresh["protocol_review_gate"]["read_only"] is True


# 24 -- markdown non-empty, says template-only + execution-free, sections.

def test_markdown_template_only_and_execution_free():
    c = _active_contract()
    md = render_data_contract_planning_markdown(c)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Data Contract Planning" in md
    assert "Template only" in md
    assert "execution-free" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Planning active: True" in md
    assert "Next gate: DATA_QA_CONTRACT_REQUIRED" in md
    assert "## Required Data Fields" in md
    assert "## Fee And Slippage Assumption Placeholders" in md
    assert "## Data Quality Questions" in md
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


# 26 -- prose verb audit over placeholders / questions / notes / markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _active_contract()

    texts.extend(str(s) for s in c["fee_slippage_assumption_placeholders"])
    texts.extend(str(s) for s in c["data_quality_questions"])
    texts.extend(str(s) for s in c["operator_notes"])

    md = render_data_contract_planning_markdown(c)
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
        '"sparta_commander/strategy_factory_data_contract_planning.py"' in src
    )
    assert (
        '"tests/test_strategy_factory_data_contract_planning.py"' in src
    )


# 29 -- Bundle 19 regression import still works.

def test_bundle19_regression_import_still_works():
    from sparta_commander.strategy_factory_protocol_review_gate import (
        build_protocol_review_gate as build19,
    )
    g = build19(_open_contract())
    assert g["executes"] is False
    assert g["read_only"] is True


# 30 -- Bundle 18 regression import still works.

def test_bundle18_regression_import_still_works():
    from sparta_commander.strategy_factory_research_protocol_draft_contract \
        import build_research_protocol_draft_contract as build18
    c = build18(_good_item())
    assert c["executes"] is False
    assert c["read_only"] is True


# 31 -- Bundle 17 regression import still works.

def test_bundle17_regression_import_still_works():
    from sparta_commander.strategy_factory_research_pipeline_closure import (
        build_research_pipeline_closure_report,
    )
    r = build_research_pipeline_closure_report()
    assert r["executes"] is False
    assert r["phase_complete"] is True


# 32 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
