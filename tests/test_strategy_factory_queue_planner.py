"""Bundle 13 tests for the Strategy Factory Queue Planner v1
(informational, read-only, planning-only).

Bundle 13's production module imports Bundle 11 and Bundle 12 via real
package imports, so these tests use normal package imports too. Running
under ``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 13 spec):
- public API exists and is limited to the expected names,
- schema version / default label / status / decision constants pinned,
- safety posture all False and keys identical to Bundle 12 posture,
- decision shape, source schemas, read-only / inert / human-gated,
- all authorization flags forced False (even when human-approved),
- decision rule: invalid -> needs-fix, valid+unapproved -> wait,
  valid+approved -> ready,
- malformed item -> no raise + invalid -> needs-fix,
- unsafe source authorization flags forced False + decision needs-fix,
- summary shape + deterministic counts + zero authorization counts,
- summary approvals map is read-only input only,
- summary read-only / inert / human-gated / safety-all-false,
- returned dicts are fresh (mutation isolation),
- markdown renderers non-empty + write nothing,
- ast import-root audit + ast forbidden-surface audit,
- prose verb audit over human-readable reasons / markdown prose,
- scoped dirty-tree guard, Bundle 11 + Bundle 12 regression imports.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_queue_planner import (
    QUEUE_PLANNER_SCHEMA_VERSION,
    DEFAULT_QUEUE_PLANNER_LABEL,
    QUEUE_PLANNER_STATUS,
    QUEUE_PLANNER_SAFETY_POSTURE,
    PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL,
    PLAN_DECISION_READY_FOR_RESEARCH_PLAN,
    PLAN_DECISION_INVALID_ITEM_NEEDS_FIX,
    build_queue_plan_decision,
    build_queue_plan_summary,
    render_queue_plan_decision_markdown,
    render_queue_plan_summary_markdown,
)
import sparta_commander.strategy_factory_queue_planner as QP
from sparta_commander.strategy_factory_queue_reader import (
    QUEUE_READER_SCHEMA_VERSION,
    QUEUE_READER_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_research_queue import (
    RESEARCH_QUEUE_SCHEMA_VERSION,
    build_research_queue_item,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_queue_planner.py"
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
        "QUEUE_PLANNER_SCHEMA_VERSION",
        "DEFAULT_QUEUE_PLANNER_LABEL",
        "QUEUE_PLANNER_STATUS",
        "QUEUE_PLANNER_SAFETY_POSTURE",
        "PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL",
        "PLAN_DECISION_READY_FOR_RESEARCH_PLAN",
        "PLAN_DECISION_INVALID_ITEM_NEEDS_FIX",
        "build_queue_plan_decision",
        "build_queue_plan_summary",
        "render_queue_plan_decision_markdown",
        "render_queue_plan_summary_markdown",
    }


# 1 + 2 -- module imports and public API is exactly as expected.

def test_public_api_is_limited_to_expected_names():
    assert set(QP.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(QP, name)


# 3 -- schema version pinned.

def test_schema_version_is_pinned():
    assert QUEUE_PLANNER_SCHEMA_VERSION == "strategy_factory_queue_planner.v1"


# 4 -- default label pinned.

def test_default_label_is_pinned():
    assert DEFAULT_QUEUE_PLANNER_LABEL == "Strategy Factory Queue Planner"


# 5 -- status pinned.

def test_status_is_pinned():
    assert QUEUE_PLANNER_STATUS == "READ_ONLY_PLANNING_REVIEW"


# 6 -- decision constants pinned.

def test_decision_constants_are_pinned():
    assert PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL == "WAIT_FOR_HUMAN_APPROVAL"
    assert PLAN_DECISION_READY_FOR_RESEARCH_PLAN == "READY_FOR_RESEARCH_PLAN"
    assert PLAN_DECISION_INVALID_ITEM_NEEDS_FIX == "INVALID_ITEM_NEEDS_FIX"


# 7 -- decision constants are distinct.

def test_decision_constants_are_distinct():
    assert len({
        PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL,
        PLAN_DECISION_READY_FOR_RESEARCH_PLAN,
        PLAN_DECISION_INVALID_ITEM_NEEDS_FIX,
    }) == 3


# 8 -- safety posture all False.

def test_safety_posture_all_false():
    assert all(v is False for v in QUEUE_PLANNER_SAFETY_POSTURE.values())


# 9 -- safety posture keys match Bundle 12.

def test_safety_posture_keys_match_bundle12():
    assert (
        set(QUEUE_PLANNER_SAFETY_POSTURE.keys())
        == set(QUEUE_READER_SAFETY_POSTURE.keys())
    )


# 10 -- decision required shape for a valid Bundle 11 item.

def test_decision_required_shape():
    d = build_queue_plan_decision(_good_item())
    required_keys = {
        "schema_version", "source_schema_version",
        "research_queue_schema_version", "idea_id", "title", "stage",
        "mode", "status", "decision", "decision_reason",
        "human_research_approved", "valid", "approved_for_research",
        "execution_authorized", "paper_trading_authorized",
        "live_trading_authorized", "data_fetch_authorized",
        "backtest_authorized", "promotion_authorized",
        "human_approval_required", "read_only", "executes", "safety",
        "reader_entry", "next_gate",
    }
    assert required_keys <= set(d.keys())
    assert d["schema_version"] == QUEUE_PLANNER_SCHEMA_VERSION
    assert d["status"] == QUEUE_PLANNER_STATUS
    assert d["idea_id"] == "idea-001"


# 11 -- decision source schema versions match Bundles 12 + 11.

def test_decision_source_schemas_match():
    d = build_queue_plan_decision(_good_item())
    assert d["source_schema_version"] == QUEUE_READER_SCHEMA_VERSION
    assert d["source_schema_version"] == "strategy_factory_queue_reader.v1"
    assert d["research_queue_schema_version"] == RESEARCH_QUEUE_SCHEMA_VERSION
    assert (
        d["research_queue_schema_version"]
        == "strategy_factory_research_queue.v1"
    )


# 12 -- decision stage PLAN_ONLY.

def test_decision_stage_plan_only():
    assert build_queue_plan_decision(_good_item())["stage"] == "PLAN_ONLY"


# 13 -- decision mode RESEARCH_ONLY.

def test_decision_mode_research_only():
    assert build_queue_plan_decision(_good_item())["mode"] == "RESEARCH_ONLY"


# 14 -- decision human_approval_required True.

def test_decision_human_approval_required():
    assert build_queue_plan_decision(_good_item())[
        "human_approval_required"] is True


# 15 -- decision read_only True.

def test_decision_read_only_true():
    assert build_queue_plan_decision(_good_item())["read_only"] is True


# 16 -- decision executes False.

def test_decision_executes_false():
    assert build_queue_plan_decision(_good_item())["executes"] is False


# 17 -- decision authorization flags all False (unapproved).

def test_decision_authorization_flags_false_unapproved():
    d = build_queue_plan_decision(_good_item())
    for flag in _AUTH_FLAGS:
        assert d[flag] is False
    assert all(v is False for v in d["safety"].values())


# 18 -- decision rule: valid + not approved -> WAIT_FOR_HUMAN_APPROVAL.

def test_decision_valid_unapproved_waits():
    d = build_queue_plan_decision(_good_item())
    assert d["valid"] is True
    assert d["decision"] == PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL
    assert d["human_research_approved"] is False
    assert d["next_gate"] == "human_research_approval"


# 19 -- decision rule: valid + approved -> READY_FOR_RESEARCH_PLAN.

def test_decision_valid_approved_is_ready():
    d = build_queue_plan_decision(_good_item(), human_research_approved=True)
    assert d["valid"] is True
    assert d["decision"] == PLAN_DECISION_READY_FOR_RESEARCH_PLAN
    assert d["human_research_approved"] is True
    assert d["next_gate"] == "human_research_plan_shaping"


# 20 -- READY decision STILL forces every authorization flag False.

def test_ready_decision_still_forces_flags_false():
    d = build_queue_plan_decision(_good_item(), human_research_approved=True)
    for flag in _AUTH_FLAGS:
        assert d[flag] is False, flag
    assert all(v is False for v in d["safety"].values())
    assert d["executes"] is False
    assert d["read_only"] is True
    assert d["human_approval_required"] is True


# 21 -- decision rule: invalid -> INVALID_ITEM_NEEDS_FIX (even if approved).

def test_decision_invalid_needs_fix_even_if_approved():
    bad = build_research_queue_item("", "", "")
    d = build_queue_plan_decision(bad, human_research_approved=True)
    assert d["valid"] is False
    assert d["decision"] == PLAN_DECISION_INVALID_ITEM_NEEDS_FIX
    assert d["next_gate"] == "human_item_repair"
    for flag in _AUTH_FLAGS:
        assert d[flag] is False


# 22 -- decision reason is non-empty and matches the decision.

def test_decision_reason_present_for_each_decision():
    good = build_queue_plan_decision(_good_item())
    ready = build_queue_plan_decision(
        _good_item(), human_research_approved=True)
    bad = build_queue_plan_decision(build_research_queue_item("", "", ""))
    for d in (good, ready, bad):
        assert isinstance(d["decision_reason"], str) and d["decision_reason"]


# 23 -- malformed items never raise and resolve to needs-fix.

def test_decision_malformed_item_no_raise():
    for bad in (None, 42, "nope", {}, {"idea_id": ""}, []):
        d = build_queue_plan_decision(bad)
        assert d["valid"] is False
        assert d["decision"] == PLAN_DECISION_INVALID_ITEM_NEEDS_FIX
        assert d["read_only"] is True
        assert d["executes"] is False
        for flag in _AUTH_FLAGS:
            assert d[flag] is False


# 24 -- non-bool truthy approval flag does not grant readiness.

def test_decision_non_strict_true_approval_does_not_ready():
    # Only the literal True grants readiness; truthy-but-not-True stays wait.
    d = build_queue_plan_decision(_good_item(), human_research_approved=1)
    assert d["human_research_approved"] is False
    assert d["decision"] == PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL


# 25 -- decision forces unsafe source authorization flags False + needs-fix.

def test_decision_forces_unsafe_flags_false():
    item = _good_item()
    item["execution_authorized"] = True
    item["backtest_authorized"] = True
    item["safety"]["live_execution_enabled"] = True
    d = build_queue_plan_decision(item, human_research_approved=True)
    assert d["valid"] is False
    assert d["decision"] == PLAN_DECISION_INVALID_ITEM_NEEDS_FIX
    for flag in _AUTH_FLAGS:
        assert d[flag] is False, flag
    assert all(v is False for v in d["safety"].values())
    assert d["executes"] is False
    assert d["read_only"] is True


# 26 -- decision embeds a Bundle 12 reader entry.

def test_decision_embeds_reader_entry():
    d = build_queue_plan_decision(_good_item())
    entry = d["reader_entry"]
    assert entry["schema_version"] == QUEUE_READER_SCHEMA_VERSION
    assert entry["read_only"] is True
    assert entry["executes"] is False


# 27 -- build_queue_plan_summary returns required shape.

def test_summary_required_shape():
    s = build_queue_plan_summary((_good_item(),))
    required_keys = {
        "schema_version", "source_schema_version",
        "research_queue_schema_version", "label", "status", "stage", "mode",
        "total_items", "valid_item_count", "invalid_item_count",
        "wait_for_human_approval_count", "ready_for_research_plan_count",
        "invalid_item_needs_fix_count", "approved_for_research_count",
        "execution_authorized_count", "paper_trading_authorized_count",
        "live_trading_authorized_count", "data_fetch_authorized_count",
        "backtest_authorized_count", "promotion_authorized_count",
        "human_approval_required", "read_only", "executes", "safety",
        "reader_summary", "decisions", "next_gate",
    }
    assert required_keys <= set(s.keys())
    assert s["schema_version"] == QUEUE_PLANNER_SCHEMA_VERSION
    assert s["label"] == DEFAULT_QUEUE_PLANNER_LABEL
    assert s["next_gate"] == "operator_review"


# 28 -- summary source schema versions match Bundles 12 + 11.

def test_summary_source_schemas_match():
    s = build_queue_plan_summary(())
    assert s["source_schema_version"] == QUEUE_READER_SCHEMA_VERSION
    assert s["research_queue_schema_version"] == RESEARCH_QUEUE_SCHEMA_VERSION


# 29 -- deterministic total / valid / invalid counts.

def test_summary_counts_are_deterministic():
    good = _good_item()
    bad = build_research_queue_item("", "", "")
    s = build_queue_plan_summary((good, bad))
    assert s["total_items"] == 2
    assert s["valid_item_count"] == 1
    assert s["invalid_item_count"] == 1
    s2 = build_queue_plan_summary((good, bad))
    assert s == s2


# 30 -- decision-bucket counts reflect approvals map.

def test_summary_decision_bucket_counts():
    a = build_research_queue_item("idea-a", "A", "Thesis A is well-formed.")
    b = build_research_queue_item("idea-b", "B", "Thesis B is well-formed.")
    bad = build_research_queue_item("", "", "")
    s = build_queue_plan_summary(
        (a, b, bad),
        human_research_approved_by_id={"idea-a": True},
    )
    assert s["ready_for_research_plan_count"] == 1
    assert s["wait_for_human_approval_count"] == 1
    assert s["invalid_item_needs_fix_count"] == 1
    assert (
        s["ready_for_research_plan_count"]
        + s["wait_for_human_approval_count"]
        + s["invalid_item_needs_fix_count"]
        == s["total_items"]
    )


# 31 -- summary approvals map is read-only input (caller dict untouched).

def test_summary_approvals_map_not_mutated():
    approvals = {"idea-001": True}
    snapshot = dict(approvals)
    build_queue_plan_summary(
        (_good_item(),), human_research_approved_by_id=approvals)
    assert approvals == snapshot


# 32 -- summary authorization counts all 0 (even with approvals).

def test_summary_authorization_counts_zero():
    s = build_queue_plan_summary(
        (_good_item(),), human_research_approved_by_id={"idea-001": True})
    for key in _AUTH_COUNTS:
        assert s[key] == 0


# 33 -- summary human_approval_required True.

def test_summary_human_approval_required():
    assert build_queue_plan_summary(())["human_approval_required"] is True


# 34 -- summary read_only True.

def test_summary_read_only_true():
    assert build_queue_plan_summary(())["read_only"] is True


# 35 -- summary executes False.

def test_summary_executes_false():
    assert build_queue_plan_summary(())["executes"] is False


# 36 -- summary safety all False.

def test_summary_safety_all_false():
    s = build_queue_plan_summary((_good_item(),))
    assert all(v is False for v in s["safety"].values())


# 37 -- summary embeds a Bundle 12 reader summary.

def test_summary_embeds_reader_summary():
    s = build_queue_plan_summary((_good_item(),))
    rs = s["reader_summary"]
    assert rs["schema_version"] == QUEUE_READER_SCHEMA_VERSION
    assert rs["read_only"] is True
    assert rs["executes"] is False


# 38 -- empty input yields empty, inert summary.

def test_summary_empty_input():
    s = build_queue_plan_summary(())
    assert s["total_items"] == 0
    assert s["decisions"] == ()
    assert s["ready_for_research_plan_count"] == 0
    assert s["executes"] is False


# 39 -- fresh dicts; mutating one result must not taint the next.

def test_results_are_fresh_and_isolated():
    a = build_queue_plan_decision(_good_item())
    b = build_queue_plan_decision(_good_item())
    assert a == b
    assert a is not b
    a["safety"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_queue_plan_decision(_good_item())
    assert fresh["safety"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert QUEUE_PLANNER_SAFETY_POSTURE["automation_enabled"] is False

    s1 = build_queue_plan_summary((_good_item(),))
    s1["safety"]["network_enabled"] = True
    s1["decisions"][0]["read_only"] = False
    s2 = build_queue_plan_summary((_good_item(),))
    assert s2["safety"]["network_enabled"] is False
    assert s2["decisions"][0]["read_only"] is True


# 40 -- markdown decision renderer non-empty + expected sections.

def test_decision_markdown_non_empty():
    d = build_queue_plan_decision(_good_item())
    md = render_queue_plan_decision_markdown(d)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Queue Plan Decision" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Human approval required: True" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "## Decision Reason" in md
    assert "## Safety" in md
    assert "## Reader Entry" in md
    assert "## Next Gate" in md


# 41 -- markdown summary renderer non-empty + expected sections.

def test_summary_markdown_non_empty():
    s = build_queue_plan_summary((_good_item(),))
    md = render_queue_plan_summary_markdown(s)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Queue Plan Summary" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Execution authorized count: 0" in md
    assert "Backtest authorized count: 0" in md
    assert "Data fetch authorized count: 0" in md
    assert "Human approval required: True" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "## Decisions" in md
    assert "## Safety" in md
    assert "## Reader Summary" in md
    assert "## Next Gate" in md


# 42 -- markdown renderers write nothing (no file surface in module source).

def test_markdown_renderers_write_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 43 -- ast import-root audit: allowed roots only.

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


# 44 -- ast forbidden-surface audit: no file/network/subprocess/exec surface.

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


# 45 -- prose verb audit over human-readable reasons + markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    good = build_queue_plan_decision(_good_item())
    ready = build_queue_plan_decision(
        _good_item(), human_research_approved=True)
    bad = build_queue_plan_decision(build_research_queue_item("", "", ""))
    summary = build_queue_plan_summary((_good_item(),))
    for d in (good, ready, bad):
        texts.append(str(d["decision_reason"]))

    for md in (
        render_queue_plan_decision_markdown(good),
        render_queue_plan_decision_markdown(ready),
        render_queue_plan_decision_markdown(bad),
        render_queue_plan_summary_markdown(summary),
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


# 46 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 47 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["human_approval_required"] is True
    assert q["approved_for_research_count"] == 0


# 48 -- Bundle 12 regression import still works.

def test_bundle12_regression_import_still_works():
    from sparta_commander.strategy_factory_queue_reader import (
        build_queue_reader_summary,
    )
    s = build_queue_reader_summary((_good_item(),))
    assert s["executes"] is False
    assert s["human_approval_required"] is True
    assert s["valid_item_count"] == 1
