"""Bundle 6 tests for the Strategy Factory Orchestrator Preview Compiler v1
(informational only).

Bundle 6's production module imports Bundle 5 via a real package import
(``from sparta_commander.strategy_factory_orchestrator_contract import ...``),
so these tests use a normal package import too. Running under
``python -m pytest`` places the repo root on ``sys.path``, so the
``sparta_commander`` package resolves.

Coverage (per the Bundle 6 spec):
- public API exists and is limited to the expected names,
- schema version pinned,
- every SAFETY_POSTURE value is False,
- FORBIDDEN_CAPABILITIES preserved from Bundle 5,
- action set derived from Bundle 5 PLAN_ACTION,
- known/unknown action handling (unknown never raises),
- every preview + every preview step is executes=False and human-gated,
- returned dicts are fresh (mutation isolation),
- markdown renderers return non-empty strings and write nothing,
- ast import-root audit + ast forbidden-surface audit,
- prose verb audit over step descriptions + contract prose,
- Bundle 5 regression import still works.
"""

import ast
import pathlib

from sparta_commander.strategy_factory_orchestrator_preview import (
    DEFAULT_PREVIEW_LABEL,
    PREVIEW_SCHEMA_VERSION,
    SAFETY_POSTURE,
    build_orchestrator_preview,
    build_all_orchestrator_previews,
    render_orchestrator_preview_markdown,
    render_all_orchestrator_previews_markdown,
)
import sparta_commander.strategy_factory_orchestrator_preview as PREVIEW
from sparta_commander.strategy_factory_orchestrator_contract import (
    PLAN_ACTION,
    FORBIDDEN_CAPABILITIES,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_orchestrator_preview.py"
)

# Execution / promotion / trading verbs forbidden in preview prose.
_BAD_VERBS = (
    "RUN", "EXECUTE", "LAUNCH", "SUBMIT", "TRADE", "ORDER",
    "PROMOTE", "DEPLOY", "UPLOAD", "FETCH", "BACKTEST",
)


def _expected_public() -> set[str]:
    return {
        "DEFAULT_PREVIEW_LABEL",
        "PREVIEW_SCHEMA_VERSION",
        "SAFETY_POSTURE",
        "build_orchestrator_preview",
        "build_all_orchestrator_previews",
        "render_orchestrator_preview_markdown",
        "render_all_orchestrator_previews_markdown",
    }


# 1 + 2 -- module imports and the public API is exactly as expected.

def test_public_api_is_limited_to_expected_names():
    assert set(PREVIEW.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(PREVIEW, name)


# 3 -- schema version pinned.

def test_schema_version_is_pinned():
    assert PREVIEW_SCHEMA_VERSION == "strategy_factory_orchestrator_preview.v1"


# 4 -- all safety posture values are False.

def test_safety_posture_all_false():
    expected_keys = {
        "automation_enabled", "live_execution_enabled", "file_write_enabled",
        "network_enabled", "subprocess_enabled", "strategy_promotion_enabled",
        "broker_enabled", "exchange_enabled", "order_enabled",
        "data_fetch_enabled", "backtest_enabled", "upload_enabled",
        "autopilot_enabled",
    }
    assert set(SAFETY_POSTURE.keys()) == expected_keys
    assert all(v is False for v in SAFETY_POSTURE.values())


# 5 -- FORBIDDEN_CAPABILITIES preserved from Bundle 5.

def test_forbidden_capabilities_preserved_from_bundle5():
    assert PREVIEW.FORBIDDEN_CAPABILITIES == FORBIDDEN_CAPABILITIES


# 6 -- action set derived from Bundle 5 PLAN_ACTION.

def test_action_set_is_derived_from_bundle5():
    allp = build_all_orchestrator_previews()
    assert set(allp["previews"].keys()) == set(PLAN_ACTION)
    assert allp["actions"] == list(PLAN_ACTION)
    assert PREVIEW.PLAN_ACTION == PLAN_ACTION


# 7 + 9 + 10 -- known action preview shape.

def test_known_action_preview():
    for action in PLAN_ACTION:
        p = build_orchestrator_preview(action)
        assert p["schema_version"] == PREVIEW_SCHEMA_VERSION
        assert p["action"] == action
        assert p["known_action"] is True
        assert p["executes"] is False
        assert p["human_gated"] is True
        assert p["label"] == DEFAULT_PREVIEW_LABEL
        assert p["forbidden_capabilities"] == FORBIDDEN_CAPABILITIES
        assert all(v is False for v in p["safety"].values())


# 8 -- unknown action never raises, falls back safely.

def test_unknown_action_is_safe_fallback():
    for junk in ("ROCKET", "", None, 123, "PROMOTE"):
        p = build_orchestrator_preview(junk)
        assert p["known_action"] is False
        assert p["executes"] is False
        assert p["human_gated"] is True
        assert p["contract"]["action"] == "UNKNOWN"
        for step in p["preview_steps"]:
            assert step["executes"] is False
            assert step["human_gate_required"] is True


# 11 + 12 -- every step executes=False and human_gate_required=True.

def test_every_step_is_gated_and_inert():
    allp = build_all_orchestrator_previews()
    for preview in allp["previews"].values():
        assert preview["preview_steps"]
        for step in preview["preview_steps"]:
            assert step["executes"] is False
            assert step["human_gate_required"] is True
            assert step["step_id"]
            assert step["name"]
            assert step["description"]


# 13 -- fresh dicts; mutating one result must not taint the next.

def test_results_are_fresh_and_isolated():
    a = build_orchestrator_preview("ADVANCE_TO_NEXT_PHASE")
    b = build_orchestrator_preview("ADVANCE_TO_NEXT_PHASE")
    assert a == b
    assert a is not b
    a["safety"]["automation_enabled"] = True
    a["contract"]["preconditions"].append("tampered")
    a["label"] = "tampered"
    fresh = build_orchestrator_preview("ADVANCE_TO_NEXT_PHASE")
    assert fresh["safety"]["automation_enabled"] is False
    assert "tampered" not in fresh["contract"]["preconditions"]
    assert fresh["label"] == DEFAULT_PREVIEW_LABEL
    # the shared module constant must be untouched too
    assert SAFETY_POSTURE["automation_enabled"] is False


# 14 + 15 -- markdown renderers return non-empty strings (write nothing).

def test_markdown_renderers_return_strings():
    one = render_orchestrator_preview_markdown("ADVANCE_TO_NEXT_PHASE")
    allmd = render_all_orchestrator_previews_markdown()
    assert isinstance(one, str) and one
    assert isinstance(allmd, str) and allmd
    assert "Strategy Factory Orchestrator Preview" in one
    assert "Executes: False" in one
    assert "Human gated: True" in one
    assert "## Contract" in one
    assert "## Preview Steps" in one
    assert "## Forbidden Capabilities" in one
    for action in PLAN_ACTION:
        assert action in allmd


def test_custom_label_flows_into_preview_and_markdown():
    p = build_orchestrator_preview("HOLD_BLOCKED", label="Custom Label")
    assert p["label"] == "Custom Label"
    md = render_orchestrator_preview_markdown("HOLD_BLOCKED", label="Custom Label")
    assert "Custom Label" in md


# 16 -- ast import-root audit: allowed roots only.

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
    # explicitly assert the risky stdlib roots are absent
    for banned in ("os", "sys", "subprocess", "socket", "requests",
                   "urllib", "pathlib", "json", "http", "asyncio"):
        assert banned not in roots, f"banned import root present: {banned}"


# 17 -- ast forbidden-surface audit: no file/network/subprocess/exec surface.

def test_no_forbidden_call_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    forbidden = (
        "open(", "write_text(", "write_bytes(", ".write(", "json.dump(",
        "import subprocess", "from subprocess", "Popen", "os.system",
        "import socket", "socket.socket", "urllib", "requests", "httpx",
        "http.client", "asyncio", "place_order", "submit_order",
        "create_order", "cancel_order", "ccxt", "freqtrade", "paper_trade",
        "live_trade", "autopilot(", ".upload(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


# 18 -- prose verb audit over step descriptions + contract prose.

def test_prose_has_no_execution_or_trading_verb():
    import re

    def _prose(preview: dict) -> list[str]:
        out = [s["description"] for s in preview["preview_steps"]]
        contract = preview["contract"]
        out.append(str(contract.get("intent", "")))
        out.extend(str(p) for p in contract.get("preconditions", []))
        return out

    allp = build_all_orchestrator_previews()
    texts: list[str] = []
    for preview in allp["previews"].values():
        texts.extend(_prose(preview))
    texts.extend(_prose(build_orchestrator_preview("UNKNOWN_ACTION_XYZ")))

    for text in texts:
        upper = text.upper()
        for verb in _BAD_VERBS:
            assert not re.search(rf"\b{verb}\b", upper), (
                f"prose {text!r} contains forbidden verb {verb!r}"
            )


# 19 -- Bundle 5 regression import still works.

def test_bundle5_regression_import_still_works():
    from sparta_commander.strategy_factory_orchestrator_contract import (
        describe_orchestrator_contract,
    )
    c = describe_orchestrator_contract()
    assert set(c["steps"].keys()) == set(PLAN_ACTION)
    assert c["executes"] is False
