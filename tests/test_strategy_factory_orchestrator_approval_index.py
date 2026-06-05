"""Bundle 8 tests for the Strategy Factory Orchestrator Approval Index v1
(informational only).

Bundle 8's production module imports Bundles 5 + 7 via real package imports
(``from sparta_commander.X import ...``), so these tests use normal package
imports too. Running under ``python -m pytest`` places the repo root on
``sys.path``, so the ``sparta_commander`` package resolves.

Coverage (per the Bundle 8 spec):
- public API exists and is limited to the expected names,
- schema version / default label / status pinned,
- safety posture all False and keys identical to Bundle 7 posture,
- FORBIDDEN_CAPABILITIES preserved from Bundle 5,
- action set + list_orchestrator_approval_actions derived from PLAN_ACTION,
- known/unknown action handling for packets and entries (never raises),
- every entry approved=False / approval_required=True / executes=False /
  human_gated=True,
- index counts (total/known/approval_required/approved) + flags,
- entries/packets one-per-action; packets embed Bundle 7 schema version,
- returned dicts are fresh (mutation isolation),
- markdown renderers non-empty + write nothing,
- ast import-root audit + ast forbidden-surface audit,
- prose verb audit over summaries / packet summary / markdown prose,
- Bundle 5 + Bundle 6 + Bundle 7 regression imports still work.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_orchestrator_approval_index import (
    APPROVAL_INDEX_SCHEMA_VERSION,
    DEFAULT_APPROVAL_INDEX_LABEL,
    APPROVAL_INDEX_STATUS,
    APPROVAL_INDEX_SAFETY_POSTURE,
    build_orchestrator_approval_index,
    list_orchestrator_approval_actions,
    entry_for_orchestrator_action,
    packet_for_orchestrator_action,
    render_orchestrator_approval_index_markdown,
    render_orchestrator_approval_action_markdown,
)
import sparta_commander.strategy_factory_orchestrator_approval_index as INDEX
from sparta_commander.strategy_factory_orchestrator_contract import (
    PLAN_ACTION,
    FORBIDDEN_CAPABILITIES,
)
from sparta_commander.strategy_factory_orchestrator_approval_packet import (
    APPROVAL_PACKET_SCHEMA_VERSION,
    APPROVAL_PACKET_SAFETY_POSTURE,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_orchestrator_approval_index.py"
)

# Execution / promotion / trading verbs forbidden in index prose.
_BAD_VERBS = (
    "RUN", "EXECUTE", "LAUNCH", "SUBMIT", "TRADE", "ORDER",
    "PROMOTE", "DEPLOY", "UPLOAD", "FETCH", "BACKTEST",
)


def _expected_public() -> set[str]:
    return {
        "APPROVAL_INDEX_SCHEMA_VERSION",
        "DEFAULT_APPROVAL_INDEX_LABEL",
        "APPROVAL_INDEX_STATUS",
        "APPROVAL_INDEX_SAFETY_POSTURE",
        "build_orchestrator_approval_index",
        "list_orchestrator_approval_actions",
        "entry_for_orchestrator_action",
        "packet_for_orchestrator_action",
        "render_orchestrator_approval_index_markdown",
        "render_orchestrator_approval_action_markdown",
    }


# 1 + 2 -- module imports and the public API is exactly as expected.

def test_public_api_is_limited_to_expected_names():
    assert set(INDEX.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(INDEX, name)


# 3 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        APPROVAL_INDEX_SCHEMA_VERSION
        == "strategy_factory_orchestrator_approval_index.v1"
    )


# 4 -- default label pinned.

def test_default_label_is_pinned():
    assert (
        DEFAULT_APPROVAL_INDEX_LABEL
        == "Strategy Factory Orchestrator Approval Index"
    )


# 5 -- status pinned.

def test_status_is_pinned():
    assert APPROVAL_INDEX_STATUS == "PENDING_HUMAN_APPROVAL"


# 6 -- safety posture all False.

def test_safety_posture_all_false():
    assert all(v is False for v in APPROVAL_INDEX_SAFETY_POSTURE.values())


# 7 -- safety posture keys match Bundle 7.

def test_safety_posture_keys_match_bundle7():
    assert (
        set(APPROVAL_INDEX_SAFETY_POSTURE.keys())
        == set(APPROVAL_PACKET_SAFETY_POSTURE.keys())
    )


# 8 -- FORBIDDEN_CAPABILITIES preserved from Bundle 5.

def test_forbidden_capabilities_preserved_from_bundle5():
    assert INDEX.FORBIDDEN_CAPABILITIES == FORBIDDEN_CAPABILITIES


# 9 -- action set derived from Bundle 5 PLAN_ACTION.

def test_action_set_is_derived_from_bundle5():
    idx = build_orchestrator_approval_index()
    assert idx["actions"] == tuple(PLAN_ACTION)
    assert INDEX.PLAN_ACTION == PLAN_ACTION


# 10 -- list_orchestrator_approval_actions returns tuple(PLAN_ACTION).

def test_list_actions_returns_tuple_plan_action():
    assert list_orchestrator_approval_actions() == tuple(PLAN_ACTION)


# 11 -- known action packet has known_action=True.

def test_known_action_packet():
    for action in PLAN_ACTION:
        p = packet_for_orchestrator_action(action)
        assert p["known_action"] is True
        assert p["approved"] is False
        assert p["approval_required"] is True
        assert p["executes"] is False
        assert p["human_gated"] is True


# 12 -- unknown action packet has known_action=False and does not raise.

def test_unknown_action_packet_is_safe():
    for junk in ("ROCKET", "", None, 123, "PROMOTE"):
        p = packet_for_orchestrator_action(junk)
        assert p["known_action"] is False
        assert p["approved"] is False
        assert p["approval_required"] is True
        assert p["executes"] is False
        assert p["human_gated"] is True


# 13 -- known action entry has known_action=True.

def test_known_action_entry():
    for action in PLAN_ACTION:
        e = entry_for_orchestrator_action(action)
        assert e["entry_id"] == action
        assert e["action"] == action
        assert e["known_action"] is True
        assert e["status"] == APPROVAL_INDEX_STATUS
        assert e["packet_schema_version"] == APPROVAL_PACKET_SCHEMA_VERSION
        assert e["summary"]


# 14 -- unknown action entry has known_action=False and does not raise.

def test_unknown_action_entry_is_safe():
    for junk in ("ROCKET", "", None, 123, "PROMOTE"):
        e = entry_for_orchestrator_action(junk)
        assert e["known_action"] is False
        assert e["entry_id"] == "UNKNOWN"
        assert e["approved"] is False
        assert e["approval_required"] is True
        assert e["executes"] is False
        assert e["human_gated"] is True


# 15-18 -- every entry is gated and inert.

def test_every_entry_is_gated_and_inert():
    idx = build_orchestrator_approval_index()
    assert idx["entries"]
    for e in idx["entries"]:
        assert e["approval_required"] is True
        assert e["approved"] is False
        assert e["executes"] is False
        assert e["human_gated"] is True


# 19 -- total_actions == len(PLAN_ACTION).

def test_index_total_actions():
    idx = build_orchestrator_approval_index()
    assert idx["total_actions"] == len(PLAN_ACTION)


# 20 -- known_action_count == len(PLAN_ACTION).

def test_index_known_action_count():
    idx = build_orchestrator_approval_index()
    assert idx["known_action_count"] == len(PLAN_ACTION)


# 21 -- approval_required_count == len(PLAN_ACTION).

def test_index_approval_required_count():
    idx = build_orchestrator_approval_index()
    assert idx["approval_required_count"] == len(PLAN_ACTION)


# 22 -- approved_count == 0.

def test_index_approved_count_is_zero():
    idx = build_orchestrator_approval_index()
    assert idx["approved_count"] == 0


# 23 + 24 -- index executes=False and human_gated=True.

def test_index_flags_are_inert():
    idx = build_orchestrator_approval_index()
    assert idx["executes"] is False
    assert idx["human_gated"] is True
    assert all(v is False for v in idx["safety"].values())


# 25 -- entries count equals len(PLAN_ACTION).

def test_index_entries_count():
    idx = build_orchestrator_approval_index()
    assert len(idx["entries"]) == len(PLAN_ACTION)


# 26 -- packets_by_action keys equal PLAN_ACTION.

def test_index_packets_by_action_keys():
    idx = build_orchestrator_approval_index()
    assert set(idx["packets_by_action"].keys()) == set(PLAN_ACTION)


# 27 -- every indexed packet embeds Bundle 7 packet schema version.

def test_indexed_packets_embed_bundle7_schema():
    idx = build_orchestrator_approval_index()
    assert idx["packet_schema_version"] == APPROVAL_PACKET_SCHEMA_VERSION
    for packet in idx["packets_by_action"].values():
        assert packet["schema_version"] == APPROVAL_PACKET_SCHEMA_VERSION


# 28 -- fresh dicts; mutating one result must not taint the next.

def test_results_are_fresh_and_isolated():
    a = build_orchestrator_approval_index()
    b = build_orchestrator_approval_index()
    assert a == b
    assert a is not b
    a["safety"]["automation_enabled"] = True
    a["approved_count"] = 99
    a["entries"][0]["approved"] = True
    a["packets_by_action"]["NO_ACTION"]["approved"] = True
    fresh = build_orchestrator_approval_index()
    assert fresh["safety"]["automation_enabled"] is False
    assert fresh["approved_count"] == 0
    assert fresh["entries"][0]["approved"] is False
    assert fresh["packets_by_action"]["NO_ACTION"]["approved"] is False
    assert APPROVAL_INDEX_SAFETY_POSTURE["automation_enabled"] is False


# 29 + 30 -- markdown renderers return non-empty strings (write nothing).

def test_markdown_renderers_return_strings():
    idx_md = render_orchestrator_approval_index_markdown()
    act_md = render_orchestrator_approval_action_markdown(
        "ADVANCE_TO_NEXT_PHASE"
    )
    assert isinstance(idx_md, str) and idx_md
    assert isinstance(act_md, str) and act_md
    assert "Strategy Factory Orchestrator Approval Index" in idx_md
    assert "Approved count: 0" in idx_md
    assert "Executes: False" in idx_md
    assert "Human gated: True" in idx_md
    assert "## Entries" in idx_md
    assert "## Safety Posture" in idx_md
    assert "## Forbidden Capabilities" in idx_md
    for action in PLAN_ACTION:
        assert action in idx_md
    assert "Strategy Factory Orchestrator Approval Action" in act_md
    assert "## Entry" in act_md
    assert "## Packet Summary" in act_md
    assert "## Safety Posture" in act_md
    # unknown action must not raise
    assert render_orchestrator_approval_action_markdown("ROCKET_XYZ")


# 31 -- ast import-root audit: allowed roots only.

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


# 32 -- ast forbidden-surface audit: no file/network/subprocess/exec surface.

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


# 33 -- prose verb audit over entry summaries + packet summary + markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    idx = build_orchestrator_approval_index()
    for e in idx["entries"]:
        texts.append(str(e["summary"]))
    texts.append(entry_for_orchestrator_action("UNKNOWN_XYZ")["summary"])

    # markdown prose, excluding heading lines and the inherited backtick
    # key/value bullets (safety posture + forbidden capabilities are DATA).
    for md in (
        render_orchestrator_approval_index_markdown(),
        render_orchestrator_approval_action_markdown("ADVANCE_TO_NEXT_PHASE"),
        render_orchestrator_approval_action_markdown("ROCKET_XYZ"),
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


# 34 -- Bundle 5 regression import still works.

def test_bundle5_regression_import_still_works():
    from sparta_commander.strategy_factory_orchestrator_contract import (
        describe_orchestrator_contract,
    )
    c = describe_orchestrator_contract()
    assert set(c["steps"].keys()) == set(PLAN_ACTION)
    assert c["executes"] is False


# 35 -- Bundle 6 regression import still works.

def test_bundle6_regression_import_still_works():
    from sparta_commander.strategy_factory_orchestrator_preview import (
        build_all_orchestrator_previews,
    )
    allp = build_all_orchestrator_previews()
    assert set(allp["previews"].keys()) == set(PLAN_ACTION)
    assert allp["executes"] is False


# 36 -- Bundle 7 regression import still works.

def test_bundle7_regression_import_still_works():
    from sparta_commander.strategy_factory_orchestrator_approval_packet import (
        build_all_orchestrator_approval_packets,
    )
    allp = build_all_orchestrator_approval_packets()
    assert set(allp["packets"].keys()) == set(PLAN_ACTION)
    assert allp["approved"] is False
    assert allp["executes"] is False
