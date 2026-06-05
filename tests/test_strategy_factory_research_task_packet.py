"""Bundle 14 tests for the Strategy Factory Research Task Packet v1
(informational, read-only, task-packet-only).

Bundle 14's production module imports Bundles 11, 12 and 13 via real
package imports, so these tests use normal package imports too. Running
under ``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 14 spec):
- public API exists and is limited to the expected names,
- schema version / default label / status / packet-status constants pinned,
- safety posture all False and keys identical to Bundle 13 posture,
- packet shape, source schemas, read-only / inert / human-gated,
- all authorization flags forced False (even when ready for spec),
- packet status rule across invalid / awaiting / ready,
- malformed item -> no raise + BLOCKED_INVALID_ITEM,
- research scope + research questions + blocked capabilities deterministic,
- packet embeds the Bundle 13 planner decision packet,
- batch shape + deterministic counts + zero authorization counts,
- batch approvals map is read-only input only,
- batch read-only / inert / human-gated / safety-all-false,
- returned dicts are fresh (mutation isolation),
- markdown renderers non-empty + write nothing,
- ast import-root audit + ast forbidden-surface audit,
- prose verb audit over scope / questions / markdown prose,
- scoped dirty-tree guard, Bundle 11 + 12 + 13 regression imports.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_research_task_packet import (
    RESEARCH_TASK_PACKET_SCHEMA_VERSION,
    DEFAULT_RESEARCH_TASK_PACKET_LABEL,
    RESEARCH_TASK_PACKET_STATUS,
    RESEARCH_TASK_PACKET_SAFETY_POSTURE,
    TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL,
    TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC,
    TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM,
    build_research_task_packet,
    build_research_task_packet_batch,
    render_research_task_packet_markdown,
    render_research_task_packet_batch_markdown,
)
import sparta_commander.strategy_factory_research_task_packet as TP
from sparta_commander.strategy_factory_queue_planner import (
    QUEUE_PLANNER_SCHEMA_VERSION,
    QUEUE_PLANNER_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_queue_reader import (
    QUEUE_READER_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_research_queue import (
    RESEARCH_QUEUE_SCHEMA_VERSION,
    build_research_queue_item,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_research_task_packet.py"
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

_AUTH_COUNTS = (
    "approved_for_research_count", "execution_authorized_count",
    "paper_trading_authorized_count", "live_trading_authorized_count",
    "data_fetch_authorized_count", "backtest_authorized_count",
    "promotion_authorized_count",
)

_REQUIRED_BLOCKED = (
    "data_fetch", "backtest", "broker", "exchange", "order",
    "live_execution", "paper_execution", "upload", "autopilot",
    "promotion", "subprocess", "network", "file_write",
)


def _good_item() -> dict:
    return build_research_queue_item(
        "idea-001",
        "Opening Range Mean Reversion",
        "Price tends to revert toward the opening range midpoint intraday.",
        asset_lane="MNQ",
        timeframe="5m",
    )


def _expected_public() -> set[str]:
    return {
        "RESEARCH_TASK_PACKET_SCHEMA_VERSION",
        "DEFAULT_RESEARCH_TASK_PACKET_LABEL",
        "RESEARCH_TASK_PACKET_STATUS",
        "RESEARCH_TASK_PACKET_SAFETY_POSTURE",
        "TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL",
        "TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC",
        "TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM",
        "build_research_task_packet",
        "build_research_task_packet_batch",
        "render_research_task_packet_markdown",
        "render_research_task_packet_batch_markdown",
    }


# 1 + 2 -- module imports and public API is exactly as expected.

def test_public_api_is_limited_to_expected_names():
    assert set(TP.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(TP, name)


# 3 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        RESEARCH_TASK_PACKET_SCHEMA_VERSION
        == "strategy_factory_research_task_packet.v1"
    )


# 4 -- default label pinned.

def test_default_label_is_pinned():
    assert (
        DEFAULT_RESEARCH_TASK_PACKET_LABEL
        == "Strategy Factory Research Task Packet"
    )


# 5 -- status pinned.

def test_status_is_pinned():
    assert RESEARCH_TASK_PACKET_STATUS == "READ_ONLY_TASK_PACKET_REVIEW"


# 6 -- task packet status constants pinned.

def test_packet_status_constants_are_pinned():
    assert (
        TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL
        == "BLOCKED_AWAITING_HUMAN_APPROVAL"
    )
    assert (
        TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC == "READY_FOR_RESEARCH_SPEC"
    )
    assert TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM == "BLOCKED_INVALID_ITEM"


# 7 -- safety posture all False.

def test_safety_posture_all_false():
    assert all(
        v is False for v in RESEARCH_TASK_PACKET_SAFETY_POSTURE.values()
    )


# 8 -- safety posture keys match Bundle 13.

def test_safety_posture_keys_match_bundle13():
    assert (
        set(RESEARCH_TASK_PACKET_SAFETY_POSTURE.keys())
        == set(QUEUE_PLANNER_SAFETY_POSTURE.keys())
    )


# 9 -- packet required shape for a valid approved item.

def test_packet_required_shape():
    p = build_research_task_packet(_good_item(), human_research_approved=True)
    required_keys = {
        "schema_version", "planner_schema_version", "reader_schema_version",
        "research_queue_schema_version", "idea_id", "title", "stage", "mode",
        "status", "task_packet_status", "planner_decision",
        "human_research_approved", "valid", "research_spec_allowed",
        "approved_for_research", "execution_authorized",
        "paper_trading_authorized", "live_trading_authorized",
        "data_fetch_authorized", "backtest_authorized",
        "promotion_authorized", "human_approval_required", "read_only",
        "executes", "safety", "planner_decision_packet", "research_scope",
        "required_research_questions", "blocked_capabilities", "next_gate",
    }
    assert required_keys <= set(p.keys())
    assert p["schema_version"] == RESEARCH_TASK_PACKET_SCHEMA_VERSION
    assert p["status"] == RESEARCH_TASK_PACKET_STATUS
    assert p["idea_id"] == "idea-001"


# 10 -- packet planner_schema_version matches Bundle 13.

def test_packet_planner_schema_matches_bundle13():
    p = build_research_task_packet(_good_item())
    assert p["planner_schema_version"] == QUEUE_PLANNER_SCHEMA_VERSION
    assert p["planner_schema_version"] == "strategy_factory_queue_planner.v1"


# 11 -- packet reader_schema_version matches Bundle 12.

def test_packet_reader_schema_matches_bundle12():
    p = build_research_task_packet(_good_item())
    assert p["reader_schema_version"] == QUEUE_READER_SCHEMA_VERSION
    assert p["reader_schema_version"] == "strategy_factory_queue_reader.v1"


# 12 -- packet research_queue_schema_version matches Bundle 11.

def test_packet_research_queue_schema_matches_bundle11():
    p = build_research_task_packet(_good_item())
    assert p["research_queue_schema_version"] == RESEARCH_QUEUE_SCHEMA_VERSION
    assert (
        p["research_queue_schema_version"]
        == "strategy_factory_research_queue.v1"
    )


# 13 -- packet stage PLAN_ONLY.

def test_packet_stage_plan_only():
    assert build_research_task_packet(_good_item())["stage"] == "PLAN_ONLY"


# 14 -- packet mode RESEARCH_ONLY.

def test_packet_mode_research_only():
    assert build_research_task_packet(_good_item())["mode"] == "RESEARCH_ONLY"


# 15 -- packet human_approval_required True.

def test_packet_human_approval_required():
    assert build_research_task_packet(_good_item())[
        "human_approval_required"] is True


# 16 -- packet read_only True.

def test_packet_read_only_true():
    assert build_research_task_packet(_good_item())["read_only"] is True


# 17 -- packet executes False.

def test_packet_executes_false():
    assert build_research_task_packet(_good_item())["executes"] is False


# 18 -- packet authorization flags all False.

def test_packet_authorization_flags_false():
    p = build_research_task_packet(_good_item())
    for flag in _AUTH_FLAGS:
        assert p[flag] is False
    assert all(v is False for v in p["safety"].values())


# 19 -- valid item without approval -> BLOCKED_AWAITING_HUMAN_APPROVAL.

def test_valid_unapproved_blocked_awaiting():
    p = build_research_task_packet(_good_item())
    assert p["valid"] is True
    assert (
        p["task_packet_status"]
        == TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL
    )
    assert p["research_spec_allowed"] is False
    assert p["next_gate"] == "human_research_approval"


# 20 -- valid item with approval -> READY_FOR_RESEARCH_SPEC.

def test_valid_approved_ready_for_spec():
    p = build_research_task_packet(_good_item(), human_research_approved=True)
    assert p["valid"] is True
    assert (
        p["task_packet_status"] == TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC
    )
    assert p["research_spec_allowed"] is True
    assert p["next_gate"] == "research_spec_contract"


# 21 -- invalid item -> BLOCKED_INVALID_ITEM.

def test_invalid_item_blocked():
    p = build_research_task_packet(build_research_queue_item("", "", ""))
    assert p["valid"] is False
    assert p["task_packet_status"] == TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM
    assert p["research_spec_allowed"] is False
    assert p["next_gate"] == "human_item_repair"


# 22 -- malformed item does not raise and is BLOCKED_INVALID_ITEM.

def test_malformed_item_no_raise():
    for bad in (None, 42, "nope", {}, {"idea_id": ""}, []):
        p = build_research_task_packet(bad)
        assert (
            p["task_packet_status"]
            == TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM
        )
        assert p["valid"] is False
        assert p["research_spec_allowed"] is False
        assert p["read_only"] is True
        assert p["executes"] is False
        for flag in _AUTH_FLAGS:
            assert p[flag] is False


# 23 -- READY allows spec but authorizes no data/backtest/execution/trading.

def test_ready_allows_spec_only_no_authorization():
    p = build_research_task_packet(_good_item(), human_research_approved=True)
    assert p["research_spec_allowed"] is True
    for flag in _AUTH_FLAGS:
        assert p[flag] is False, flag
    assert all(v is False for v in p["safety"].values())
    assert p["executes"] is False
    assert p["read_only"] is True
    assert p["human_approval_required"] is True


# 24 -- packet embeds Bundle 13 planner decision packet.

def test_packet_embeds_planner_decision_packet():
    p = build_research_task_packet(_good_item())
    pdp = p["planner_decision_packet"]
    assert pdp["schema_version"] == QUEUE_PLANNER_SCHEMA_VERSION
    assert pdp["read_only"] is True
    assert pdp["executes"] is False
    assert p["planner_decision"] == pdp["decision"]


# 25 -- research scope deterministic with required fields.

def test_research_scope_fields():
    p = build_research_task_packet(_good_item())
    scope = p["research_scope"]
    for key in ("objective", "asset_lane", "timeframe", "source", "thesis"):
        assert key in scope
    assert scope["asset_lane"] == "MNQ"
    assert scope["timeframe"] == "5m"
    p2 = build_research_task_packet(_good_item())
    assert p["research_scope"] == p2["research_scope"]


# 26 -- required research questions deterministic and non-empty.

def test_required_research_questions():
    p = build_research_task_packet(_good_item())
    q = p["required_research_questions"]
    assert isinstance(q, tuple) and len(q) >= 1
    assert all(isinstance(x, str) and x for x in q)
    p2 = build_research_task_packet(_good_item())
    assert p["required_research_questions"] == p2["required_research_questions"]


# 27 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    p = build_research_task_packet(_good_item())
    blocked = set(p["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 28 -- batch returns required shape.

def test_batch_required_shape():
    b = build_research_task_packet_batch((_good_item(),))
    required_keys = {
        "schema_version", "planner_schema_version", "reader_schema_version",
        "research_queue_schema_version", "label", "status", "stage", "mode",
        "total_items", "ready_for_research_spec_count",
        "blocked_awaiting_approval_count", "blocked_invalid_item_count",
        "approved_for_research_count", "execution_authorized_count",
        "paper_trading_authorized_count", "live_trading_authorized_count",
        "data_fetch_authorized_count", "backtest_authorized_count",
        "promotion_authorized_count", "human_approval_required", "read_only",
        "executes", "safety", "planner_summary", "task_packets", "next_gate",
    }
    assert required_keys <= set(b.keys())
    assert b["schema_version"] == RESEARCH_TASK_PACKET_SCHEMA_VERSION
    assert b["label"] == DEFAULT_RESEARCH_TASK_PACKET_LABEL
    assert b["next_gate"] == "research_spec_contract"


# 29 -- batch schema versions match Bundles 11/12/13.

def test_batch_schema_versions_match():
    b = build_research_task_packet_batch(())
    assert b["planner_schema_version"] == QUEUE_PLANNER_SCHEMA_VERSION
    assert b["reader_schema_version"] == QUEUE_READER_SCHEMA_VERSION
    assert b["research_queue_schema_version"] == RESEARCH_QUEUE_SCHEMA_VERSION


# 30 + 31 -- batch total + status counts deterministic.

def test_batch_counts_deterministic():
    a = build_research_queue_item("idea-a", "A", "Thesis A is well-formed.")
    bb = build_research_queue_item("idea-b", "B", "Thesis B is well-formed.")
    bad = build_research_queue_item("", "", "")
    b = build_research_task_packet_batch(
        (a, bb, bad),
        human_research_approved_by_id={"idea-a": True},
    )
    assert b["total_items"] == 3
    assert b["ready_for_research_spec_count"] == 1
    assert b["blocked_awaiting_approval_count"] == 1
    assert b["blocked_invalid_item_count"] == 1
    b2 = build_research_task_packet_batch(
        (a, bb, bad),
        human_research_approved_by_id={"idea-a": True},
    )
    assert b == b2


# 32 -- batch authorization counts all 0 (even with approvals).

def test_batch_authorization_counts_zero():
    b = build_research_task_packet_batch(
        (_good_item(),), human_research_approved_by_id={"idea-001": True})
    for key in _AUTH_COUNTS:
        assert b[key] == 0


# 33 -- batch human_approval_required True.

def test_batch_human_approval_required():
    assert build_research_task_packet_batch(())["human_approval_required"] \
        is True


# 34 -- batch read_only True.

def test_batch_read_only_true():
    assert build_research_task_packet_batch(())["read_only"] is True


# 35 -- batch executes False.

def test_batch_executes_false():
    assert build_research_task_packet_batch(())["executes"] is False


# 36 -- batch safety all False.

def test_batch_safety_all_false():
    b = build_research_task_packet_batch((_good_item(),))
    assert all(v is False for v in b["safety"].values())


# 37 -- batch embeds Bundle 13 planner summary.

def test_batch_embeds_planner_summary():
    b = build_research_task_packet_batch((_good_item(),))
    ps = b["planner_summary"]
    assert ps["schema_version"] == QUEUE_PLANNER_SCHEMA_VERSION
    assert ps["read_only"] is True
    assert ps["executes"] is False


# 38 -- fresh dicts; mutating one result must not taint the next.

def test_results_are_fresh_and_isolated():
    a = build_research_task_packet(_good_item())
    b = build_research_task_packet(_good_item())
    assert a == b
    assert a is not b
    a["safety"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_research_task_packet(_good_item())
    assert fresh["safety"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert RESEARCH_TASK_PACKET_SAFETY_POSTURE["automation_enabled"] is False

    b1 = build_research_task_packet_batch((_good_item(),))
    b1["safety"]["network_enabled"] = True
    b1["task_packets"][0]["read_only"] = False
    b2 = build_research_task_packet_batch((_good_item(),))
    assert b2["safety"]["network_enabled"] is False
    assert b2["task_packets"][0]["read_only"] is True


# 39 -- approvals map is read-only input (caller dict untouched).

def test_batch_approvals_map_not_mutated():
    approvals = {"idea-001": True}
    snapshot = dict(approvals)
    build_research_task_packet_batch(
        (_good_item(),), human_research_approved_by_id=approvals)
    assert approvals == snapshot


# 40 -- markdown renderers return non-empty strings + expected sections.

def test_markdown_renderers_non_empty():
    p = build_research_task_packet(_good_item(), human_research_approved=True)
    md_p = render_research_task_packet_markdown(p)
    assert isinstance(md_p, str) and md_p
    assert "# Strategy Factory Research Task Packet" in md_p
    assert "Stage: PLAN_ONLY" in md_p
    assert "Mode: RESEARCH_ONLY" in md_p
    assert "Human approval required: True" in md_p
    assert "Read only: True" in md_p
    assert "Executes: False" in md_p
    assert "## Research Scope" in md_p
    assert "## Required Research Questions" in md_p
    assert "## Blocked Capabilities" in md_p
    assert "## Safety" in md_p
    assert "## Planner Decision" in md_p
    assert "## Next Gate" in md_p

    b = build_research_task_packet_batch((_good_item(),))
    md_b = render_research_task_packet_batch_markdown(b)
    assert isinstance(md_b, str) and md_b
    assert "# Strategy Factory Research Task Packet Batch" in md_b
    assert "Stage: PLAN_ONLY" in md_b
    assert "Mode: RESEARCH_ONLY" in md_b
    assert "Execution authorized count: 0" in md_b
    assert "Backtest authorized count: 0" in md_b
    assert "Data fetch authorized count: 0" in md_b
    assert "Human approval required: True" in md_b
    assert "Read only: True" in md_b
    assert "Executes: False" in md_b
    assert "## Task Packets" in md_b
    assert "## Safety" in md_b
    assert "## Planner Summary" in md_b
    assert "## Next Gate" in md_b


# 41 -- markdown renderers write nothing (no file surface in module source).

def test_markdown_renderers_write_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 42 -- ast import-root audit: allowed roots only.

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


# 43 -- ast forbidden-surface audit: no file/network/subprocess/exec surface.

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


# 44 -- prose verb audit over scope / questions / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    p = build_research_task_packet(_good_item(), human_research_approved=True)
    batch = build_research_task_packet_batch((_good_item(),))

    # research scope + research questions are human-readable narrative.
    scope = p["research_scope"]
    texts.append(str(scope["objective"]))
    texts.extend(str(q) for q in p["required_research_questions"])

    for md in (
        render_research_task_packet_markdown(p),
        render_research_task_packet_batch_markdown(batch),
    ):
        for ln in md.splitlines():
            stripped = ln.lstrip()
            # skip headings, backtick key/value bullets, and `Label: value`
            # metadata header lines -- those are DATA, not narrative prose
            # (schema-derived count/flag labels legitimately contain words
            # like "Backtest authorized count").
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


# 45 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 46 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["human_approval_required"] is True
    assert q["approved_for_research_count"] == 0


# 47 -- Bundle 12 regression import still works.

def test_bundle12_regression_import_still_works():
    from sparta_commander.strategy_factory_queue_reader import (
        build_queue_reader_summary,
    )
    s = build_queue_reader_summary((_good_item(),))
    assert s["executes"] is False
    assert s["valid_item_count"] == 1


# 48 -- Bundle 13 regression import still works.

def test_bundle13_regression_import_still_works():
    from sparta_commander.strategy_factory_queue_planner import (
        build_queue_plan_summary,
    )
    s = build_queue_plan_summary((_good_item(),))
    assert s["executes"] is False
    assert s["human_approval_required"] is True
    assert s["valid_item_count"] == 1
