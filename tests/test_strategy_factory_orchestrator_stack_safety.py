"""Bundle 10 tests for the Strategy Factory Orchestrator Stack Safety
Closure v1 (informational, read-only, push-prep only).

Bundle 10's production module imports Bundles 5-9 via real package imports
(``from sparta_commander.X import ...``), so these tests use normal package
imports too. Running under ``python -m pytest`` places the repo root on
``sys.path``, so the ``sparta_commander`` package resolves.

Coverage (per the Bundle 10 spec):
- public API exists and is limited to the expected names,
- schema version / default label / status pinned,
- safety posture all False and keys identical to Bundle 9 posture,
- FORBIDDEN_CAPABILITIES preserved from Bundle 5,
- action set derived from Bundle 5 PLAN_ACTION,
- ORCHESTRATOR_STACK_SEQUENCE immutable + Bundles 5-9 in order,
- summary counts + read-only / no-push / no-controls / no-recording flags,
- summary schema_versions + statuses match Bundle 6-9 exact constants,
- five layer checks, all read-only / safety-all-false / inert / human-gated,
- closure checks all assert the inert, push-operator-gated posture,
- returned dicts are fresh (mutation isolation),
- markdown renderer non-empty + writes nothing + no git push command,
- ast import-root audit + ast forbidden-surface audit,
- prose verb audit over layer summaries / closure text / markdown prose,
- Bundle 5-9 regression imports + the targeted stack regression.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_orchestrator_stack_safety import (
    STACK_SAFETY_SCHEMA_VERSION,
    DEFAULT_STACK_SAFETY_LABEL,
    STACK_SAFETY_STATUS,
    STACK_SAFETY_POSTURE,
    ORCHESTRATOR_STACK_SEQUENCE,
    build_orchestrator_stack_safety_summary,
    render_orchestrator_stack_safety_markdown,
)
import sparta_commander.strategy_factory_orchestrator_stack_safety as STACK
from sparta_commander.strategy_factory_orchestrator_contract import (
    PLAN_ACTION,
    FORBIDDEN_CAPABILITIES,
)
from sparta_commander.strategy_factory_orchestrator_preview import (
    PREVIEW_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_orchestrator_approval_packet import (
    APPROVAL_PACKET_SCHEMA_VERSION,
    APPROVAL_PACKET_STATUS,
)
from sparta_commander.strategy_factory_orchestrator_approval_index import (
    APPROVAL_INDEX_SCHEMA_VERSION,
    APPROVAL_INDEX_STATUS,
)
from sparta_commander.strategy_factory_orchestrator_display_adapter import (
    DISPLAY_ADAPTER_SCHEMA_VERSION,
    DISPLAY_ADAPTER_STATUS,
    DISPLAY_ADAPTER_SAFETY_POSTURE,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_orchestrator_stack_safety.py"
)

# Execution / promotion / trading verbs forbidden in closure prose.
_BAD_VERBS = (
    "RUN", "EXECUTE", "LAUNCH", "SUBMIT", "TRADE", "ORDER",
    "PROMOTE", "DEPLOY", "UPLOAD", "FETCH", "BACKTEST",
)


def _expected_public() -> set[str]:
    return {
        "STACK_SAFETY_SCHEMA_VERSION",
        "DEFAULT_STACK_SAFETY_LABEL",
        "STACK_SAFETY_STATUS",
        "STACK_SAFETY_POSTURE",
        "ORCHESTRATOR_STACK_SEQUENCE",
        "build_orchestrator_stack_safety_summary",
        "render_orchestrator_stack_safety_markdown",
    }


# 1 + 2 -- module imports and public API is exactly as expected.

def test_public_api_is_limited_to_expected_names():
    assert set(STACK.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(STACK, name)


# 3 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        STACK_SAFETY_SCHEMA_VERSION
        == "strategy_factory_orchestrator_stack_safety.v1"
    )


# 4 -- default label pinned.

def test_default_label_is_pinned():
    assert (
        DEFAULT_STACK_SAFETY_LABEL
        == "Strategy Factory Orchestrator Stack Safety Closure"
    )


# 5 -- status pinned.

def test_status_is_pinned():
    assert STACK_SAFETY_STATUS == "PENDING_OPERATOR_PUSH_APPROVAL"


# 6 -- safety posture all False.

def test_safety_posture_all_false():
    assert all(v is False for v in STACK_SAFETY_POSTURE.values())


# 7 -- safety posture keys match Bundle 9.

def test_safety_posture_keys_match_bundle9():
    assert (
        set(STACK_SAFETY_POSTURE.keys())
        == set(DISPLAY_ADAPTER_SAFETY_POSTURE.keys())
    )


# 8 -- FORBIDDEN_CAPABILITIES preserved from Bundle 5.

def test_forbidden_capabilities_preserved_from_bundle5():
    assert STACK.FORBIDDEN_CAPABILITIES == FORBIDDEN_CAPABILITIES


# 9 -- action set derived from Bundle 5 PLAN_ACTION.

def test_action_set_is_derived_from_bundle5():
    s = build_orchestrator_stack_safety_summary()
    assert s["total_actions"] == len(PLAN_ACTION)
    assert STACK.PLAN_ACTION == PLAN_ACTION


# 10 -- ORCHESTRATOR_STACK_SEQUENCE immutable + Bundles 5-9 in order.

def test_stack_sequence_is_immutable_and_ordered():
    assert isinstance(ORCHESTRATOR_STACK_SEQUENCE, tuple)
    ids = [row[0] for row in ORCHESTRATOR_STACK_SEQUENCE]
    assert ids == ["bundle_5", "bundle_6", "bundle_7", "bundle_8", "bundle_9"]
    names = [row[1] for row in ORCHESTRATOR_STACK_SEQUENCE]
    assert names == [
        "contract", "preview", "approval_packet",
        "approval_index", "display_adapter",
    ]
    for row in ORCHESTRATOR_STACK_SEQUENCE:
        assert isinstance(row, tuple) and len(row) == 3


# 11-20 -- summary counts + flags.

def test_summary_counts_and_flags():
    s = build_orchestrator_stack_safety_summary()
    assert s["total_actions"] == len(PLAN_ACTION)
    assert s["known_action_count"] == len(PLAN_ACTION)
    assert s["approved_count"] == 0
    assert s["read_only"] is True
    assert s["push_enabled"] is False
    assert s["push_requires_operator"] is True
    assert s["approval_recording_enabled"] is False
    assert s["action_controls_enabled"] is False
    assert s["executes"] is False
    assert s["human_gated"] is True
    assert s["status"] == STACK_SAFETY_STATUS


# 21 -- schema_versions match Bundle 6, 7, 8, 9 exact constants.

def test_summary_schema_versions_match():
    s = build_orchestrator_stack_safety_summary()
    sv = s["schema_versions"]
    assert sv["preview"] == PREVIEW_SCHEMA_VERSION
    assert sv["approval_packet"] == APPROVAL_PACKET_SCHEMA_VERSION
    assert sv["approval_index"] == APPROVAL_INDEX_SCHEMA_VERSION
    assert sv["display_adapter"] == DISPLAY_ADAPTER_SCHEMA_VERSION


# 22 -- statuses match Bundle 7, 8, 9 exact constants.

def test_summary_statuses_match():
    s = build_orchestrator_stack_safety_summary()
    st = s["statuses"]
    assert st["approval_packet"] == APPROVAL_PACKET_STATUS
    assert st["approval_index"] == APPROVAL_INDEX_STATUS
    assert st["display_adapter"] == DISPLAY_ADAPTER_STATUS


# 23 -- module_sequence equals ORCHESTRATOR_STACK_SEQUENCE.

def test_summary_module_sequence_matches_constant():
    s = build_orchestrator_stack_safety_summary()
    assert s["module_sequence"] == ORCHESTRATOR_STACK_SEQUENCE


# 24-28 -- five layer checks, all read-only / safe / inert / human-gated.

def test_layer_checks_are_inert_and_complete():
    s = build_orchestrator_stack_safety_summary()
    checks = s["layer_checks"]
    assert len(checks) == 5
    for check in checks:
        assert check["read_only"] is True
        assert check["safety_all_false"] is True
        assert check["executes"] is False
        assert check["human_gated"] is True
        assert check["layer_id"]
        assert check["name"]
        assert check["summary"]


# 29-35 -- closure checks assert the inert, push-operator-gated posture.

def test_closure_checks():
    s = build_orchestrator_stack_safety_summary()
    cc = s["closure_checks"]
    assert cc["all_safety_flags_false"] is True
    assert cc["all_approvals_false"] is True
    assert cc["all_action_controls_disabled"] is True
    assert cc["all_approval_recording_disabled"] is True
    assert cc["all_read_only"] is True
    assert cc["push_enabled"] is False
    assert cc["push_requires_operator"] is True


# 36 -- fresh dicts; mutating one result must not taint the next.

def test_results_are_fresh_and_isolated():
    a = build_orchestrator_stack_safety_summary()
    b = build_orchestrator_stack_safety_summary()
    assert a == b
    assert a is not b
    a["safety"]["automation_enabled"] = True
    a["approved_count"] = 99
    a["closure_checks"]["push_enabled"] = True
    a["layer_checks"][0]["read_only"] = False
    fresh = build_orchestrator_stack_safety_summary()
    assert fresh["safety"]["automation_enabled"] is False
    assert fresh["approved_count"] == 0
    assert fresh["closure_checks"]["push_enabled"] is False
    assert fresh["layer_checks"][0]["read_only"] is True
    assert STACK_SAFETY_POSTURE["automation_enabled"] is False


# 37 + 38 -- markdown renderer returns non-empty string (writes nothing).

def test_markdown_renderer_returns_string():
    md = render_orchestrator_stack_safety_markdown()
    assert isinstance(md, str) and md
    assert "Strategy Factory Orchestrator Stack Safety Closure" in md
    assert "Read only: True" in md
    assert "Push enabled: False" in md
    assert "Push requires operator: True" in md
    assert "Approval recording enabled: False" in md
    assert "Action controls enabled: False" in md
    assert "Approved count: 0" in md
    assert "## Schema Versions" in md
    assert "## Layer Checks" in md
    assert "## Closure Checks" in md
    assert "## Safety Posture" in md
    assert "## Forbidden Capabilities" in md
    assert "## Operator Gate" in md


# 39 -- markdown must not include a git push command.

def test_markdown_has_no_git_push_command():
    md = render_orchestrator_stack_safety_markdown()
    assert "git push" not in md.lower()


# 40 -- ast import-root audit: allowed roots only.

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


# 41 -- ast forbidden-surface audit: no file/network/subprocess/exec surface.

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


# 42 -- prose verb audit over layer summaries + closure text + markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    s = build_orchestrator_stack_safety_summary()
    for check in s["layer_checks"]:
        texts.append(str(check["summary"]))

    # markdown prose, excluding heading lines and inherited backtick
    # key/value bullets (schema versions, closure checks, safety posture and
    # forbidden capabilities are DATA, not a step's own prose).
    md = render_orchestrator_stack_safety_markdown()
    for ln in md.splitlines():
        stripped = ln.lstrip()
        if stripped.startswith("#") or stripped.startswith("- `"):
            continue
        texts.append(ln)

    for text in texts:
        upper = text.upper()
        for verb in _BAD_VERBS:
            assert not re.search(rf"\b{verb}\b", upper), (
                f"prose {text!r} contains forbidden verb {verb!r}"
            )


# 43 -- Bundle 5 regression import still works.

def test_bundle5_regression_import_still_works():
    from sparta_commander.strategy_factory_orchestrator_contract import (
        describe_orchestrator_contract,
    )
    c = describe_orchestrator_contract()
    assert set(c["steps"].keys()) == set(PLAN_ACTION)
    assert c["executes"] is False


# 44 -- Bundle 6 regression import still works.

def test_bundle6_regression_import_still_works():
    from sparta_commander.strategy_factory_orchestrator_preview import (
        build_all_orchestrator_previews,
    )
    allp = build_all_orchestrator_previews()
    assert set(allp["previews"].keys()) == set(PLAN_ACTION)
    assert allp["executes"] is False


# 45 -- Bundle 7 regression import still works.

def test_bundle7_regression_import_still_works():
    from sparta_commander.strategy_factory_orchestrator_approval_packet import (
        build_all_orchestrator_approval_packets,
    )
    allp = build_all_orchestrator_approval_packets()
    assert set(allp["packets"].keys()) == set(PLAN_ACTION)
    assert allp["approved"] is False


# 46 -- Bundle 8 regression import still works.

def test_bundle8_regression_import_still_works():
    from sparta_commander.strategy_factory_orchestrator_approval_index import (
        build_orchestrator_approval_index,
    )
    idx = build_orchestrator_approval_index()
    assert idx["actions"] == tuple(PLAN_ACTION)
    assert idx["approved_count"] == 0


# 47 -- Bundle 9 regression import still works.

def test_bundle9_regression_import_still_works():
    from sparta_commander.strategy_factory_orchestrator_display_adapter import (
        build_orchestrator_display_panel,
    )
    panel = build_orchestrator_display_panel()
    assert panel["read_only"] is True
    assert panel["approved_count"] == 0
    assert panel["executes"] is False


# 48 -- targeted Strategy Factory orchestrator stack regression passes.

def test_targeted_stack_regression():
    s = build_orchestrator_stack_safety_summary()
    # every consumed layer reports inert, and the closure agrees
    assert all(c["safety_all_false"] for c in s["layer_checks"])
    assert s["closure_checks"]["all_read_only"] is True
    assert s["closure_checks"]["push_enabled"] is False
    assert s["executes"] is False
    assert s["human_gated"] is True
    assert s["approved_count"] == 0
