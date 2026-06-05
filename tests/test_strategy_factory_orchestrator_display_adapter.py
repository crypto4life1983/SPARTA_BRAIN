"""Bundle 9 tests for the Strategy Factory Orchestrator Read-Only Display
Adapter v1 (informational, display-only).

Bundle 9's production module imports Bundles 5 + 8 via real package imports
(``from sparta_commander.X import ...``), so these tests use normal package
imports too. Running under ``python -m pytest`` places the repo root on
``sys.path``, so the ``sparta_commander`` package resolves.

Coverage (per the Bundle 9 spec):
- public API exists and is limited to the expected names,
- schema version / default label / status pinned,
- safety posture all False and keys identical to Bundle 8 posture,
- FORBIDDEN_CAPABILITIES preserved from Bundle 5,
- action set derived from Bundle 5 PLAN_ACTION,
- panel counts + read-only/no-controls/no-recording flags,
- one display row per action; every row fully gated + read-only,
- known/unknown action panels (never raises); every section read-only/inert,
- action panel embeds Bundle 8 entry + Bundle 7 packet,
- returned dicts are fresh (mutation isolation),
- markdown renderers non-empty + write nothing,
- ast import-root audit + ast forbidden-surface audit,
- prose verb audit over summaries / sections / packet summary / markdown,
- Bundle 5 + 6 + 7 + 8 regression imports still work.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_orchestrator_display_adapter import (
    DISPLAY_ADAPTER_SCHEMA_VERSION,
    DEFAULT_DISPLAY_ADAPTER_LABEL,
    DISPLAY_ADAPTER_STATUS,
    DISPLAY_ADAPTER_SAFETY_POSTURE,
    build_orchestrator_display_panel,
    build_orchestrator_action_display_panel,
    render_orchestrator_display_markdown,
    render_orchestrator_action_display_markdown,
)
import sparta_commander.strategy_factory_orchestrator_display_adapter as DISPLAY
from sparta_commander.strategy_factory_orchestrator_contract import (
    PLAN_ACTION,
    FORBIDDEN_CAPABILITIES,
)
from sparta_commander.strategy_factory_orchestrator_approval_index import (
    APPROVAL_INDEX_SCHEMA_VERSION,
    APPROVAL_INDEX_SAFETY_POSTURE,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_orchestrator_display_adapter.py"
)

_PACKET_SCHEMA = "strategy_factory_orchestrator_approval_packet.v1"

# Execution / promotion / trading verbs forbidden in display prose.
_BAD_VERBS = (
    "RUN", "EXECUTE", "LAUNCH", "SUBMIT", "TRADE", "ORDER",
    "PROMOTE", "DEPLOY", "UPLOAD", "FETCH", "BACKTEST",
)


def _expected_public() -> set[str]:
    return {
        "DISPLAY_ADAPTER_SCHEMA_VERSION",
        "DEFAULT_DISPLAY_ADAPTER_LABEL",
        "DISPLAY_ADAPTER_STATUS",
        "DISPLAY_ADAPTER_SAFETY_POSTURE",
        "build_orchestrator_display_panel",
        "build_orchestrator_action_display_panel",
        "render_orchestrator_display_markdown",
        "render_orchestrator_action_display_markdown",
    }


# 1 + 2 -- module imports and the public API is exactly as expected.

def test_public_api_is_limited_to_expected_names():
    assert set(DISPLAY.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(DISPLAY, name)


# 3 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        DISPLAY_ADAPTER_SCHEMA_VERSION
        == "strategy_factory_orchestrator_display_adapter.v1"
    )


# 4 -- default label pinned.

def test_default_label_is_pinned():
    assert (
        DEFAULT_DISPLAY_ADAPTER_LABEL
        == "Strategy Factory Orchestrator Read-Only Display"
    )


# 5 -- status pinned.

def test_status_is_pinned():
    assert DISPLAY_ADAPTER_STATUS == "READ_ONLY_PENDING_HUMAN_APPROVAL"


# 6 -- safety posture all False.

def test_safety_posture_all_false():
    assert all(v is False for v in DISPLAY_ADAPTER_SAFETY_POSTURE.values())


# 7 -- safety posture keys match Bundle 8.

def test_safety_posture_keys_match_bundle8():
    assert (
        set(DISPLAY_ADAPTER_SAFETY_POSTURE.keys())
        == set(APPROVAL_INDEX_SAFETY_POSTURE.keys())
    )


# 8 -- FORBIDDEN_CAPABILITIES preserved from Bundle 5.

def test_forbidden_capabilities_preserved_from_bundle5():
    assert DISPLAY.FORBIDDEN_CAPABILITIES == FORBIDDEN_CAPABILITIES


# 9 -- action set derived from Bundle 5 PLAN_ACTION.

def test_action_set_is_derived_from_bundle5():
    panel = build_orchestrator_display_panel()
    rows_actions = tuple(r["action"] for r in panel["display_rows"])
    assert rows_actions == tuple(PLAN_ACTION)
    assert DISPLAY.PLAN_ACTION == PLAN_ACTION


# 10-13 -- panel counts.

def test_panel_counts():
    panel = build_orchestrator_display_panel()
    assert panel["total_actions"] == len(PLAN_ACTION)
    assert panel["known_action_count"] == len(PLAN_ACTION)
    assert panel["approval_required_count"] == len(PLAN_ACTION)
    assert panel["approved_count"] == 0


# 14-18 -- panel flags.

def test_panel_flags_are_read_only_and_inert():
    panel = build_orchestrator_display_panel()
    assert panel["read_only"] is True
    assert panel["approval_recording_enabled"] is False
    assert panel["action_controls_enabled"] is False
    assert panel["executes"] is False
    assert panel["human_gated"] is True
    assert all(v is False for v in panel["safety"].values())
    assert panel["status"] == DISPLAY_ADAPTER_STATUS


# 19 -- display rows count equals len(PLAN_ACTION).

def test_display_rows_count():
    panel = build_orchestrator_display_panel()
    assert len(panel["display_rows"]) == len(PLAN_ACTION)


# 20-24 -- every display row is gated and read-only.

def test_every_display_row_is_gated_and_read_only():
    panel = build_orchestrator_display_panel()
    assert panel["display_rows"]
    for row in panel["display_rows"]:
        assert row["approval_required"] is True
        assert row["approved"] is False
        assert row["read_only"] is True
        assert row["executes"] is False
        assert row["human_gated"] is True
        assert row["row_id"]
        assert row["summary"]


# 25 -- known action display panel has known_action=True.

def test_known_action_display_panel():
    for action in PLAN_ACTION:
        p = build_orchestrator_action_display_panel(action)
        assert p["known_action"] is True
        assert p["action"] == action
        assert p["schema_version"] == DISPLAY_ADAPTER_SCHEMA_VERSION
        assert p["packet_schema_version"] == _PACKET_SCHEMA


# 26 -- unknown action display panel has known_action=False and no raise.

def test_unknown_action_display_panel_is_safe():
    for junk in ("ROCKET", "", None, 123, "PROMOTE"):
        p = build_orchestrator_action_display_panel(junk)
        assert p["known_action"] is False
        assert p["read_only"] is True
        assert p["approved"] is False
        assert p["approval_required"] is True
        assert p["executes"] is False
        assert p["human_gated"] is True


# 27-33 -- every action display panel is gated, read-only, no controls.

def test_action_panel_flags_for_every_action():
    for action in list(PLAN_ACTION) + ["UNKNOWN_XYZ"]:
        p = build_orchestrator_action_display_panel(action)
        assert p["approval_required"] is True
        assert p["approved"] is False
        assert p["read_only"] is True
        assert p["approval_recording_enabled"] is False
        assert p["action_controls_enabled"] is False
        assert p["executes"] is False
        assert p["human_gated"] is True


# 34 + 35 -- every display section is read-only and inert.

def test_every_display_section_is_read_only_and_inert():
    for action in list(PLAN_ACTION) + ["UNKNOWN_XYZ"]:
        p = build_orchestrator_action_display_panel(action)
        assert p["display_sections"]
        for section in p["display_sections"]:
            assert section["read_only"] is True
            assert section["executes"] is False
            assert section["section_id"]
            assert section["name"]
            assert section["description"]


# 36 -- action panel embeds Bundle 8 entry and Bundle 7 packet.

def test_action_panel_embeds_entry_and_packet():
    p = build_orchestrator_action_display_panel("ADVANCE_TO_NEXT_PHASE")
    entry = p["entry"]
    packet = p["packet"]
    assert entry["action"] == "ADVANCE_TO_NEXT_PHASE"
    assert entry["packet_schema_version"] == _PACKET_SCHEMA
    assert packet["schema_version"] == _PACKET_SCHEMA
    assert packet["action"] == "ADVANCE_TO_NEXT_PHASE"
    assert packet["approved"] is False
    assert packet["preview"]["preview_steps"]


# 37 -- fresh dicts; mutating one result must not taint the next.

def test_results_are_fresh_and_isolated():
    a = build_orchestrator_display_panel()
    b = build_orchestrator_display_panel()
    assert a == b
    assert a is not b
    a["safety"]["automation_enabled"] = True
    a["approved_count"] = 99
    a["display_rows"][0]["approved"] = True
    fresh = build_orchestrator_display_panel()
    assert fresh["safety"]["automation_enabled"] is False
    assert fresh["approved_count"] == 0
    assert fresh["display_rows"][0]["approved"] is False
    assert DISPLAY_ADAPTER_SAFETY_POSTURE["automation_enabled"] is False

    pa = build_orchestrator_action_display_panel("HOLD_BLOCKED")
    pb = build_orchestrator_action_display_panel("HOLD_BLOCKED")
    assert pa == pb
    assert pa is not pb
    pa["display_sections"][0]["read_only"] = False
    pa["packet"]["approved"] = True
    fresh2 = build_orchestrator_action_display_panel("HOLD_BLOCKED")
    assert fresh2["display_sections"][0]["read_only"] is True
    assert fresh2["packet"]["approved"] is False


# 38 + 39 -- markdown renderers return non-empty strings (write nothing).

def test_markdown_renderers_return_strings():
    panel_md = render_orchestrator_display_markdown()
    action_md = render_orchestrator_action_display_markdown(
        "ADVANCE_TO_NEXT_PHASE"
    )
    assert isinstance(panel_md, str) and panel_md
    assert isinstance(action_md, str) and action_md
    assert "Strategy Factory Orchestrator Read-Only Display" in panel_md
    assert "Read only: True" in panel_md
    assert "Approval recording enabled: False" in panel_md
    assert "Action controls enabled: False" in panel_md
    assert "Approved count: 0" in panel_md
    assert "Executes: False" in panel_md
    assert "## Display Rows" in panel_md
    assert "## Safety Posture" in panel_md
    assert "## Forbidden Capabilities" in panel_md
    for action in PLAN_ACTION:
        assert action in panel_md
    assert "Strategy Factory Orchestrator Action Display" in action_md
    assert "## Entry" in action_md
    assert "## Packet Summary" in action_md
    assert "## Display Sections" in action_md
    assert "## Safety Posture" in action_md
    # unknown action must not raise
    assert render_orchestrator_action_display_markdown("ROCKET_XYZ")


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
        "random.",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


# 42 -- prose verb audit over row summaries + section descriptions + markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    panel = build_orchestrator_display_panel()
    for row in panel["display_rows"]:
        texts.append(str(row["summary"]))
    for action in list(PLAN_ACTION) + ["UNKNOWN_XYZ"]:
        p = build_orchestrator_action_display_panel(action)
        for section in p["display_sections"]:
            texts.append(str(section["description"]))

    # markdown prose, excluding heading lines and inherited backtick
    # key/value bullets (safety posture + forbidden capabilities are DATA).
    for md in (
        render_orchestrator_display_markdown(),
        render_orchestrator_action_display_markdown("ADVANCE_TO_NEXT_PHASE"),
        render_orchestrator_action_display_markdown("ROCKET_XYZ"),
    ):
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
    assert idx["executes"] is False
