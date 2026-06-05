"""Bundle 21 tests for the Strategy Factory Data QA Contract template v1
(informational, read-only, template-only -- NO real data access).

Bundle 21's production module imports Bundles 11-20 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 21 spec):
- module imports cleanly + public API limited to expected names,
- schema version / label / status / state / gate constants pinned,
- pure stdlib import-root audit + forbidden-surface audit,
- all 14 posture keys present + all False + keys match Bundle 20,
- posture is mutation-isolated (fresh dicts),
- activates only when planning_active True AND planning next_gate is
  DATA_QA_CONTRACT_REQUIRED,
- blocked / wrong-gate / malformed planning never activate and never raise,
- next_gate defaults to RESEARCH_RUNNER_CONTRACT_REQUIRED when active,
- no execution/data/backtest/simulation/broker/upload/autopilot/live flag True,
- the 12 template description fields present,
- blocked_capabilities include the required set,
- validate passes + detects failure modes; validation not self-required,
- markdown non-empty, says template-only + execution-free, writes nothing,
- prose verb audit over rejection/policy/operator-note/markdown prose,
- scoped dirty-tree guard, Bundle 11-20 regression imports,
- commander_2_safety allowlist contains the new module + test paths.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_data_qa_contract import (
    DATA_QA_CONTRACT_SCHEMA_VERSION,
    DEFAULT_DATA_QA_CONTRACT_LABEL,
    DATA_QA_CONTRACT_STATUS,
    DATA_QA_CONTRACT_SAFETY_POSTURE,
    DATA_QA_STATE_ACTIVE,
    DATA_QA_STATE_BLOCKED,
    NEXT_GATE_RESEARCH_RUNNER_CONTRACT_REQUIRED,
    NEXT_GATE_AWAIT_DATA_CONTRACT_PLANNING,
    build_data_qa_contract,
    validate_data_qa_contract,
    render_data_qa_contract_markdown,
)
import sparta_commander.strategy_factory_data_qa_contract as QA
from sparta_commander.strategy_factory_data_contract_planning import (
    DATA_CONTRACT_PLANNING_SAFETY_POSTURE,
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
    / "strategy_factory_data_qa_contract.py"
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
    "required_data_integrity_checks", "missing_bar_policy_placeholder",
    "duplicate_timestamp_policy_placeholder", "timezone_policy_placeholder",
    "fee_slippage_policy_placeholder", "symbol_mapping_policy_placeholder",
    "minimum_coverage_policy_placeholder", "rejection_conditions",
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


def _ready_planning() -> dict:
    """A Bundle 20 planning template that is active (DATA_QA_CONTRACT_REQUIRED)."""
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(
        draft, review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING)
    return build_data_contract_planning(gate)


def _blocked_planning() -> dict:
    """A Bundle 20 planning template that is NOT active."""
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(draft)  # awaiting, not unlocked
    return build_data_contract_planning(gate)


def _active_contract() -> dict:
    return build_data_qa_contract(_ready_planning())


def _expected_public() -> set[str]:
    return {
        "DATA_QA_CONTRACT_SCHEMA_VERSION",
        "DEFAULT_DATA_QA_CONTRACT_LABEL",
        "DATA_QA_CONTRACT_STATUS",
        "DATA_QA_CONTRACT_SAFETY_POSTURE",
        "DATA_QA_STATE_ACTIVE",
        "DATA_QA_STATE_BLOCKED",
        "NEXT_GATE_RESEARCH_RUNNER_CONTRACT_REQUIRED",
        "NEXT_GATE_AWAIT_DATA_CONTRACT_PLANNING",
        "build_data_qa_contract",
        "validate_data_qa_contract",
        "render_data_qa_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(QA.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(QA, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        DATA_QA_CONTRACT_SCHEMA_VERSION
        == "strategy_factory_data_qa_contract.v1"
    )


# 3 -- label / status pinned.

def test_label_and_status_pinned():
    assert DEFAULT_DATA_QA_CONTRACT_LABEL == "Strategy Factory Data QA Contract"
    assert DATA_QA_CONTRACT_STATUS == "READ_ONLY_DATA_QA_CONTRACT"


# 4 -- state / gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert DATA_QA_STATE_ACTIVE == "DATA_QA_CONTRACT_ACTIVE"
    assert DATA_QA_STATE_BLOCKED == "DATA_QA_CONTRACT_BLOCKED"
    assert (
        NEXT_GATE_RESEARCH_RUNNER_CONTRACT_REQUIRED
        == "RESEARCH_RUNNER_CONTRACT_REQUIRED"
    )
    assert (
        NEXT_GATE_AWAIT_DATA_CONTRACT_PLANNING == "AWAIT_DATA_CONTRACT_PLANNING"
    )


# 5 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = DATA_QA_CONTRACT_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 6 -- posture keys match Bundle 20.

def test_posture_keys_match_bundle20():
    assert (
        set(DATA_QA_CONTRACT_SAFETY_POSTURE.keys())
        == set(DATA_CONTRACT_PLANNING_SAFETY_POSTURE.keys())
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
    a = build_data_qa_contract(_ready_planning())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_data_qa_contract(_ready_planning())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert DATA_QA_CONTRACT_SAFETY_POSTURE["automation_enabled"] is False


# 10 -- planning_active + DATA_QA_CONTRACT_REQUIRED activates the QA contract.

def test_active_planning_activates():
    c = _active_contract()
    assert c["data_qa_active"] is True
    assert c["data_qa_state"] == "DATA_QA_CONTRACT_ACTIVE"
    assert c["next_gate"] == "RESEARCH_RUNNER_CONTRACT_REQUIRED"
    assert c["planning_active"] is True
    assert c["planning_next_gate"] == "DATA_QA_CONTRACT_REQUIRED"


# 11 -- a blocked (inactive) planning template does not activate.

def test_blocked_planning_does_not_activate():
    c = build_data_qa_contract(_blocked_planning())
    assert c["data_qa_active"] is False
    assert c["data_qa_state"] == "DATA_QA_CONTRACT_BLOCKED"
    assert c["next_gate"] == "AWAIT_DATA_CONTRACT_PLANNING"


# 12 -- planning active but wrong next_gate does not activate.

def test_active_planning_wrong_gate_does_not_activate():
    import copy
    p = copy.deepcopy(_ready_planning())
    p["next_gate"] = "SOMETHING_ELSE"  # tamper: gate no longer the QA gate
    c = build_data_qa_contract(p)
    assert c["data_qa_active"] is False
    assert c["next_gate"] == "AWAIT_DATA_CONTRACT_PLANNING"


# 13 -- malformed planning never raises and never activates.

def test_malformed_planning_no_raise():
    for bad in (None, 42, "nope", {}, {"planning_active": True}, []):
        c = build_data_qa_contract(bad)
        assert c["data_qa_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert c["validation"]["valid"] is True


# 14 -- no authorization flag can become True (active or blocked).

def test_authorization_flags_always_false():
    for c in (_active_contract(), build_data_qa_contract(_blocked_planning())):
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
    assert c["data_qa_active"] is True
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["backtest_enabled"] is False


# 16 -- the 12 required template description fields are present.

def test_required_template_fields_present():
    c = _active_contract()
    for field in _REQUIRED_TEMPLATE_FIELDS:
        assert field in c, field
    assert isinstance(c["required_data_integrity_checks"], tuple)
    assert len(c["required_data_integrity_checks"]) >= 1
    assert isinstance(c["rejection_conditions"], tuple)
    assert len(c["rejection_conditions"]) >= 1
    assert c["asset_lane"] == "MNQ"
    assert c["timeframe_lane"] == "5m"


# 17 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    c = _active_contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 18 -- the embedded planning template is preserved.

def test_planning_embedded():
    p = _ready_planning()
    c = build_data_qa_contract(p)
    assert c["data_contract_planning"]["schema_version"] == (
        p["schema_version"]
    )
    assert c["data_contract_planning"]["read_only"] is True


# 19 -- validate passes for an active contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _active_contract()
    v = validate_data_qa_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_data_qa_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_data_qa_contract(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_data_qa_contract(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["required_data_integrity_checks"] = ()
    assert validate_data_qa_contract(bad4)["valid"] is False


# 20 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_active_contract())
    c.pop("validation", None)
    v = validate_data_qa_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 21 -- fresh dicts; mutation of one result does not taint the next.

def test_results_are_fresh_and_isolated():
    a = _active_contract()
    b = _active_contract()
    assert a == b
    assert a is not b
    a["required_data_integrity_checks"] = ()
    a["data_contract_planning"]["read_only"] = False
    fresh = _active_contract()
    assert len(fresh["required_data_integrity_checks"]) >= 1
    assert fresh["data_contract_planning"]["read_only"] is True


# 22 -- markdown non-empty, says template-only + execution-free, sections.

def test_markdown_template_only_and_execution_free():
    c = _active_contract()
    md = render_data_qa_contract_markdown(c)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Data QA Contract" in md
    assert "Template only" in md
    assert "execution-free" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Data QA active: True" in md
    assert "Next gate: RESEARCH_RUNNER_CONTRACT_REQUIRED" in md
    assert "## Required Data Integrity Checks" in md
    assert "## Policy Placeholders" in md
    assert "## Rejection Conditions" in md
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


# 24 -- prose verb audit over rejection / policy / notes / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _active_contract()

    texts.extend(str(s) for s in c["rejection_conditions"])
    texts.extend(str(s) for s in c["operator_notes"])
    for key in (
        "missing_bar_policy_placeholder",
        "duplicate_timestamp_policy_placeholder",
        "timezone_policy_placeholder",
        "fee_slippage_policy_placeholder",
        "symbol_mapping_policy_placeholder",
        "minimum_coverage_policy_placeholder",
    ):
        texts.append(str(c[key]))

    md = render_data_qa_contract_markdown(c)
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


# 25 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 26 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_data_qa_contract.py"' in src
    )
    assert (
        '"tests/test_strategy_factory_data_qa_contract.py"' in src
    )


# 27 -- Bundle 20 regression import still works.

def test_bundle20_regression_import_still_works():
    from sparta_commander.strategy_factory_data_contract_planning import (
        build_data_contract_planning as build20,
    )
    p = build20(_blocked_planning_gate())
    assert p["executes"] is False
    assert p["read_only"] is True


def _blocked_planning_gate() -> dict:
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    return build_protocol_review_gate(draft)


# 28 -- Bundle 19 regression import still works.

def test_bundle19_regression_import_still_works():
    from sparta_commander.strategy_factory_protocol_review_gate import (
        build_protocol_review_gate as build19,
    )
    draft = build_research_protocol_draft_contract(_good_item())
    g = build19(draft)
    assert g["executes"] is False
    assert g["read_only"] is True


# 29 -- Bundle 18 regression import still works.

def test_bundle18_regression_import_still_works():
    from sparta_commander.strategy_factory_research_protocol_draft_contract \
        import build_research_protocol_draft_contract as build18
    c = build18(_good_item())
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
