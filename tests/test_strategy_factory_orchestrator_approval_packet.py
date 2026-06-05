"""Bundle 7 tests for the Strategy Factory Orchestrator Human Approval
Packet Compiler v1 (informational only).

Bundle 7's production module imports Bundle 5 and Bundle 6 via real package
imports (``from sparta_commander.X import ...``), so these tests use normal
package imports too. Running under ``python -m pytest`` places the repo root
on ``sys.path``, so the ``sparta_commander`` package resolves.

Coverage (per the Bundle 7 spec):
- public API exists and is limited to the expected names,
- schema version / default label / status pinned,
- safety posture all False and keys identical to Bundle 6 SAFETY_POSTURE,
- FORBIDDEN_CAPABILITIES preserved from Bundle 5,
- action set derived from Bundle 5 PLAN_ACTION,
- known/unknown action handling (unknown never raises),
- every packet approved=False, approval_required=True, executes=False,
  human_gated=True; every slot approved=False, executes=False,
  human_approval_required=True,
- each packet embeds the Bundle 6 preview + preview schema version,
- approval state is neutral and unapproved,
- returned dicts are fresh (mutation isolation),
- build_all yields exactly one packet per PLAN_ACTION action,
- operator + custom label flow through,
- markdown renderers return non-empty strings and write nothing,
- ast import-root audit + ast forbidden-surface audit,
- prose verb audit over slot descriptions / approval state / markdown prose,
- Bundle 5 + Bundle 6 regression imports still work.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_orchestrator_approval_packet import (
    APPROVAL_PACKET_SCHEMA_VERSION,
    DEFAULT_APPROVAL_PACKET_LABEL,
    APPROVAL_PACKET_STATUS,
    APPROVAL_PACKET_SAFETY_POSTURE,
    build_orchestrator_approval_packet,
    build_all_orchestrator_approval_packets,
    render_orchestrator_approval_packet_markdown,
    render_all_orchestrator_approval_packets_markdown,
)
import sparta_commander.strategy_factory_orchestrator_approval_packet as PACKET
from sparta_commander.strategy_factory_orchestrator_contract import (
    PLAN_ACTION,
    FORBIDDEN_CAPABILITIES,
)
from sparta_commander.strategy_factory_orchestrator_preview import (
    PREVIEW_SCHEMA_VERSION,
    SAFETY_POSTURE,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_orchestrator_approval_packet.py"
)

# Execution / promotion / trading verbs forbidden in packet prose.
_BAD_VERBS = (
    "RUN", "EXECUTE", "LAUNCH", "SUBMIT", "TRADE", "ORDER",
    "PROMOTE", "DEPLOY", "UPLOAD", "FETCH", "BACKTEST",
)


def _expected_public() -> set[str]:
    return {
        "APPROVAL_PACKET_SCHEMA_VERSION",
        "DEFAULT_APPROVAL_PACKET_LABEL",
        "APPROVAL_PACKET_STATUS",
        "APPROVAL_PACKET_SAFETY_POSTURE",
        "build_orchestrator_approval_packet",
        "build_all_orchestrator_approval_packets",
        "render_orchestrator_approval_packet_markdown",
        "render_all_orchestrator_approval_packets_markdown",
    }


# 1 -- module imports and the public API is exactly as expected.

def test_public_api_is_limited_to_expected_names():
    assert set(PACKET.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(PACKET, name)


# 2 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        APPROVAL_PACKET_SCHEMA_VERSION
        == "strategy_factory_orchestrator_approval_packet.v1"
    )


# 3 -- default label pinned.

def test_default_label_is_pinned():
    assert (
        DEFAULT_APPROVAL_PACKET_LABEL
        == "Strategy Factory Orchestrator Human Approval Packet"
    )


# 4 -- status pinned.

def test_status_is_pinned():
    assert APPROVAL_PACKET_STATUS == "PENDING_HUMAN_APPROVAL"


# 5 -- safety posture all False and keys identical to Bundle 6.

def test_safety_posture_all_false_and_keys_match_bundle6():
    assert set(APPROVAL_PACKET_SAFETY_POSTURE.keys()) == set(SAFETY_POSTURE)
    assert all(v is False for v in APPROVAL_PACKET_SAFETY_POSTURE.values())


# 6 -- FORBIDDEN_CAPABILITIES preserved from Bundle 5.

def test_forbidden_capabilities_preserved_from_bundle5():
    assert PACKET.FORBIDDEN_CAPABILITIES == FORBIDDEN_CAPABILITIES


# 7 -- action set derived from Bundle 5 PLAN_ACTION.

def test_action_set_is_derived_from_bundle5():
    allp = build_all_orchestrator_approval_packets()
    assert set(allp["packets"].keys()) == set(PLAN_ACTION)
    assert allp["actions"] == list(PLAN_ACTION)
    assert PACKET.PLAN_ACTION == PLAN_ACTION


# 8 -- known action packet shape.

def test_known_action_packet_shape():
    for action in PLAN_ACTION:
        p = build_orchestrator_approval_packet(action)
        assert p["schema_version"] == APPROVAL_PACKET_SCHEMA_VERSION
        assert p["status"] == APPROVAL_PACKET_STATUS
        assert p["action"] == action
        assert p["known_action"] is True
        assert p["approval_required"] is True
        assert p["approved"] is False
        assert p["executes"] is False
        assert p["human_gated"] is True
        assert p["label"] == DEFAULT_APPROVAL_PACKET_LABEL
        assert p["operator"] == ""
        assert p["forbidden_capabilities"] == FORBIDDEN_CAPABILITIES
        assert all(v is False for v in p["safety"].values())


# 9 -- unknown action never raises, falls back safely.

def test_unknown_action_is_safe_fallback():
    for junk in ("ROCKET", "", None, 123, "PROMOTE"):
        p = build_orchestrator_approval_packet(junk)
        assert p["known_action"] is False
        assert p["status"] == APPROVAL_PACKET_STATUS
        assert p["approved"] is False
        assert p["approval_required"] is True
        assert p["executes"] is False
        assert p["human_gated"] is True
        for slot in p["approval_slots"]:
            assert slot["approved"] is False
            assert slot["executes"] is False
            assert slot["human_approval_required"] is True


# 10 -- every packet is gated and inert.

def test_every_packet_is_gated_and_inert():
    allp = build_all_orchestrator_approval_packets()
    assert allp["status"] == APPROVAL_PACKET_STATUS
    assert allp["approved"] is False
    assert allp["approval_required"] is True
    assert allp["executes"] is False
    assert allp["human_gated"] is True
    for packet in allp["packets"].values():
        assert packet["approved"] is False
        assert packet["approval_required"] is True
        assert packet["executes"] is False
        assert packet["human_gated"] is True


# 11 -- every slot is gated and inert.

def test_every_slot_is_gated_and_inert():
    allp = build_all_orchestrator_approval_packets()
    for packet in allp["packets"].values():
        assert packet["approval_slots"]
        for slot in packet["approval_slots"]:
            assert slot["approved"] is False
            assert slot["executes"] is False
            assert slot["human_approval_required"] is True
            assert slot["slot_id"]
            assert slot["name"]
            assert slot["description"]


# 12 -- each packet embeds the Bundle 6 preview + preview schema version.

def test_packet_embeds_bundle6_preview():
    p = build_orchestrator_approval_packet("ADVANCE_TO_NEXT_PHASE")
    assert p["preview_schema_version"] == PREVIEW_SCHEMA_VERSION
    assert p["preview"]["schema_version"] == PREVIEW_SCHEMA_VERSION
    assert p["preview"]["action"] == "ADVANCE_TO_NEXT_PHASE"
    assert p["preview"]["executes"] is False
    assert p["preview"]["human_gated"] is True
    assert p["preview"]["preview_steps"]


# 13 -- approval state is neutral and unapproved.

def test_approval_state_is_neutral_and_unapproved():
    p = build_orchestrator_approval_packet("AWAIT_HUMAN")
    state = p["approval_state"]
    assert state["approved"] is False
    assert state["decision_recorded"] is False
    assert state["approval_reference"] == ""
    assert state["approval_notes"] == ""
    assert state["next_gate"] == "await_human_decision"


# 14 -- fresh dicts; mutating one result must not taint the next.

def test_results_are_fresh_and_isolated():
    a = build_orchestrator_approval_packet("ADVANCE_TO_NEXT_PHASE")
    b = build_orchestrator_approval_packet("ADVANCE_TO_NEXT_PHASE")
    assert a == b
    assert a is not b
    a["safety"]["automation_enabled"] = True
    a["approved"] = True
    a["approval_state"]["approved"] = True
    a["approval_slots"][0]["approved"] = True
    a["label"] = "tampered"
    fresh = build_orchestrator_approval_packet("ADVANCE_TO_NEXT_PHASE")
    assert fresh["safety"]["automation_enabled"] is False
    assert fresh["approved"] is False
    assert fresh["approval_state"]["approved"] is False
    assert fresh["approval_slots"][0]["approved"] is False
    assert fresh["label"] == DEFAULT_APPROVAL_PACKET_LABEL
    # the shared module constant must be untouched too
    assert APPROVAL_PACKET_SAFETY_POSTURE["automation_enabled"] is False


# 15 -- build_all yields exactly one packet per action.

def test_build_all_has_one_packet_per_action():
    allp = build_all_orchestrator_approval_packets()
    assert len(allp["packets"]) == len(PLAN_ACTION)
    for action in PLAN_ACTION:
        assert allp["packets"][action]["action"] == action


# 16 -- operator flows into the packet.

def test_operator_flows_into_packet():
    p = build_orchestrator_approval_packet(
        "HOLD_BLOCKED", operator="mahmoud"
    )
    assert p["operator"] == "mahmoud"
    allp = build_all_orchestrator_approval_packets(operator="mahmoud")
    assert allp["operator"] == "mahmoud"
    for packet in allp["packets"].values():
        assert packet["operator"] == "mahmoud"


# 17 -- custom label flows into packet and markdown.

def test_custom_label_flows_into_packet_and_markdown():
    p = build_orchestrator_approval_packet("HOLD_BLOCKED", label="Custom Label")
    assert p["label"] == "Custom Label"
    md = render_orchestrator_approval_packet_markdown(
        "HOLD_BLOCKED", label="Custom Label"
    )
    assert "Custom Label" in md


# 18 -- markdown renderers return non-empty strings (write nothing).

def test_markdown_renderers_return_strings():
    one = render_orchestrator_approval_packet_markdown("ADVANCE_TO_NEXT_PHASE")
    allmd = render_all_orchestrator_approval_packets_markdown()
    assert isinstance(one, str) and one
    assert isinstance(allmd, str) and allmd
    assert "Strategy Factory Orchestrator Human Approval Packet" in one
    assert "Status: PENDING_HUMAN_APPROVAL" in one
    assert "Approval required: True" in one
    assert "Approved: False" in one
    assert "Executes: False" in one
    assert "Human gated: True" in one
    assert "## Preview Summary" in one
    assert "## Approval State" in one
    assert "## Approval Slots" in one
    assert "## Safety Posture" in one
    assert "## Forbidden Capabilities" in one


# 19 -- render-all contains every action.

def test_render_all_contains_every_action():
    allmd = render_all_orchestrator_approval_packets_markdown()
    for action in PLAN_ACTION:
        assert action in allmd


# 20 -- ast import-root audit: allowed roots only.

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


# 21 -- ast forbidden-surface audit: no file/network/subprocess/exec surface.

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


# 22 -- prose verb audit over slot descriptions + approval state text.

def test_prose_has_no_execution_or_trading_verb():
    def _prose(packet: dict) -> list[str]:
        out = [s["description"] for s in packet["approval_slots"]]
        state = packet["approval_state"]
        out.append(str(state.get("next_gate", "")))
        out.append(str(state.get("approval_reference", "")))
        out.append(str(state.get("approval_notes", "")))
        return out

    allp = build_all_orchestrator_approval_packets()
    texts: list[str] = []
    for packet in allp["packets"].values():
        texts.extend(_prose(packet))
    texts.extend(_prose(build_orchestrator_approval_packet("UNKNOWN_XYZ")))

    for text in texts:
        upper = text.upper()
        for verb in _BAD_VERBS:
            assert not re.search(rf"\b{verb}\b", upper), (
                f"prose {text!r} contains forbidden verb {verb!r}"
            )


# 23 -- markdown prose audit (excludes heading + safety/forbidden key bullets).

def test_markdown_prose_has_no_execution_or_trading_verb():
    md = render_all_orchestrator_approval_packets_markdown()
    # Exclude heading lines and the backtick-key bullets used by the safety
    # posture + forbidden-capability enumerations (those are inherited
    # capability/key DATA, not a step's own prose).
    body_lines = [
        ln for ln in md.splitlines()
        if not ln.lstrip().startswith("#")
        and not ln.lstrip().startswith("- `")
    ]
    body = "\n".join(body_lines).upper()
    for verb in _BAD_VERBS:
        assert not re.search(rf"\b{verb}\b", body), (
            f"markdown prose contains forbidden verb {verb!r}"
        )


# 24 -- Bundle 5 regression import still works.

def test_bundle5_regression_import_still_works():
    from sparta_commander.strategy_factory_orchestrator_contract import (
        describe_orchestrator_contract,
    )
    c = describe_orchestrator_contract()
    assert set(c["steps"].keys()) == set(PLAN_ACTION)
    assert c["executes"] is False


# 25 -- Bundle 6 regression import still works.

def test_bundle6_regression_import_still_works():
    from sparta_commander.strategy_factory_orchestrator_preview import (
        build_all_orchestrator_previews,
    )
    allp = build_all_orchestrator_previews()
    assert set(allp["previews"].keys()) == set(PLAN_ACTION)
    assert allp["executes"] is False


# 26 -- the status constant is the one stamped into every packet.

def test_status_constant_used_in_every_packet():
    allp = build_all_orchestrator_approval_packets()
    for packet in allp["packets"].values():
        assert packet["status"] == APPROVAL_PACKET_STATUS


# 27 -- packet safety is a fresh copy, not the shared module constant.

def test_packet_safety_is_fresh_copy_not_shared_constant():
    p = build_orchestrator_approval_packet("NO_ACTION")
    assert p["safety"] == APPROVAL_PACKET_SAFETY_POSTURE
    assert p["safety"] is not APPROVAL_PACKET_SAFETY_POSTURE


# 28 -- top-level aggregate is itself pending human approval.

def test_aggregate_status_is_pending():
    allp = build_all_orchestrator_approval_packets()
    assert allp["status"] == "PENDING_HUMAN_APPROVAL"
    assert allp["preview_schema_version"] == PREVIEW_SCHEMA_VERSION
