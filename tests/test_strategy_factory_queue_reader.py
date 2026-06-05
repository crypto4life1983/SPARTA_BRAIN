"""Bundle 12 tests for the Strategy Factory Queue Reader v1
(informational, read-only).

Bundle 12's production module imports Bundle 11 via a real package import
(``from sparta_commander.strategy_factory_research_queue import ...``), so
these tests use normal package imports too. Running under ``python -m
pytest`` places the repo root on ``sys.path`` so ``sparta_commander``
resolves.

Coverage (per the Bundle 12 spec):
- public API exists and is limited to the expected names,
- schema version / default label / status pinned,
- safety posture all False and keys identical to Bundle 11 posture,
- entry shape, source schema, read-only / inert / human-gated,
- all authorization flags forced False (even when source is unsafe),
- valid item -> valid True; malformed item -> no raise + valid False,
- unsafe source authorization flags forced False + flagged invalid,
- summary shape + deterministic counts + zero authorization counts,
- summary read-only / inert / human-gated / safety-all-false,
- returned dicts are fresh (mutation isolation),
- markdown renderers non-empty + write nothing,
- ast import-root audit + ast forbidden-surface audit,
- prose verb audit over human-readable summaries / markdown prose,
- scoped dirty-tree guard, Bundle 11 regression import.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_queue_reader import (
    QUEUE_READER_SCHEMA_VERSION,
    DEFAULT_QUEUE_READER_LABEL,
    QUEUE_READER_STATUS,
    QUEUE_READER_SAFETY_POSTURE,
    build_queue_reader_entry,
    build_queue_reader_summary,
    render_queue_reader_entry_markdown,
    render_queue_reader_summary_markdown,
)
import sparta_commander.strategy_factory_queue_reader as QR
from sparta_commander.strategy_factory_research_queue import (
    RESEARCH_QUEUE_SCHEMA_VERSION,
    RESEARCH_QUEUE_SAFETY_POSTURE,
    build_research_queue_item,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_queue_reader.py"
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
        "QUEUE_READER_SCHEMA_VERSION",
        "DEFAULT_QUEUE_READER_LABEL",
        "QUEUE_READER_STATUS",
        "QUEUE_READER_SAFETY_POSTURE",
        "build_queue_reader_entry",
        "build_queue_reader_summary",
        "render_queue_reader_entry_markdown",
        "render_queue_reader_summary_markdown",
    }


# 1 + 2 -- module imports and public API is exactly as expected.

def test_public_api_is_limited_to_expected_names():
    assert set(QR.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(QR, name)


# 3 -- schema version pinned.

def test_schema_version_is_pinned():
    assert QUEUE_READER_SCHEMA_VERSION == "strategy_factory_queue_reader.v1"


# 4 -- default label pinned.

def test_default_label_is_pinned():
    assert DEFAULT_QUEUE_READER_LABEL == "Strategy Factory Queue Reader"


# 5 -- status pinned.

def test_status_is_pinned():
    assert QUEUE_READER_STATUS == "READ_ONLY_QUEUE_REVIEW"


# 6 -- safety posture all False.

def test_safety_posture_all_false():
    assert all(v is False for v in QUEUE_READER_SAFETY_POSTURE.values())


# 7 -- safety posture keys match Bundle 11.

def test_safety_posture_keys_match_bundle11():
    assert (
        set(QUEUE_READER_SAFETY_POSTURE.keys())
        == set(RESEARCH_QUEUE_SAFETY_POSTURE.keys())
    )


# 8 -- entry required shape for a valid Bundle 11 item.

def test_entry_required_shape():
    entry = build_queue_reader_entry(_good_item())
    required_keys = {
        "schema_version", "source_schema_version", "idea_id", "title",
        "stage", "mode", "status", "item_status", "valid",
        "approved_for_research", "execution_authorized",
        "paper_trading_authorized", "live_trading_authorized",
        "data_fetch_authorized", "backtest_authorized",
        "promotion_authorized", "human_approval_required", "read_only",
        "executes", "safety", "validation", "next_gate", "summary",
    }
    assert required_keys <= set(entry.keys())
    assert entry["schema_version"] == QUEUE_READER_SCHEMA_VERSION
    assert entry["status"] == QUEUE_READER_STATUS
    assert entry["next_gate"] == "human_research_approval"
    assert entry["idea_id"] == "idea-001"


# 9 -- entry source_schema_version matches Bundle 11.

def test_entry_source_schema_matches_bundle11():
    entry = build_queue_reader_entry(_good_item())
    assert entry["source_schema_version"] == RESEARCH_QUEUE_SCHEMA_VERSION
    assert entry["source_schema_version"] == "strategy_factory_research_queue.v1"


# 10 -- entry stage PLAN_ONLY.

def test_entry_stage_plan_only():
    assert build_queue_reader_entry(_good_item())["stage"] == "PLAN_ONLY"


# 11 -- entry mode RESEARCH_ONLY.

def test_entry_mode_research_only():
    assert build_queue_reader_entry(_good_item())["mode"] == "RESEARCH_ONLY"


# 12 -- entry human_approval_required True.

def test_entry_human_approval_required():
    assert build_queue_reader_entry(_good_item())[
        "human_approval_required"] is True


# 13 -- entry read_only True.

def test_entry_read_only_true():
    assert build_queue_reader_entry(_good_item())["read_only"] is True


# 14 -- entry executes False.

def test_entry_executes_false():
    assert build_queue_reader_entry(_good_item())["executes"] is False


# 15 -- entry authorization flags all False.

def test_entry_authorization_flags_false():
    entry = build_queue_reader_entry(_good_item())
    for flag in _AUTH_FLAGS:
        assert entry[flag] is False
    assert all(v is False for v in entry["safety"].values())


# 16 -- entry for valid item has valid=True.

def test_entry_valid_item_is_valid():
    assert build_queue_reader_entry(_good_item())["valid"] is True


# 17 -- entry for malformed item does not raise and has valid=False.

def test_entry_malformed_item_no_raise():
    for bad in (None, 42, "nope", {}, {"idea_id": ""}, []):
        entry = build_queue_reader_entry(bad)
        assert entry["valid"] is False
        assert entry["read_only"] is True
        assert entry["executes"] is False
        for flag in _AUTH_FLAGS:
            assert entry[flag] is False


# 18 -- entry forces unsafe source authorization flags back to False.

def test_entry_forces_unsafe_flags_false():
    item = _good_item()
    item["execution_authorized"] = True
    item["backtest_authorized"] = True
    item["approved_for_research"] = True
    item["safety"]["live_execution_enabled"] = True
    entry = build_queue_reader_entry(item)
    for flag in _AUTH_FLAGS:
        assert entry[flag] is False, flag
    assert all(v is False for v in entry["safety"].values())
    assert entry["executes"] is False
    assert entry["read_only"] is True


# 19 -- entry validation detects unsafe source authorization flags.

def test_entry_validation_detects_unsafe_source():
    item = _good_item()
    item["execution_authorized"] = True
    entry = build_queue_reader_entry(item)
    assert entry["valid"] is False
    assert entry["validation"]["execution_authorized"] is True


# 20 -- build_queue_reader_summary returns required shape.

def test_summary_required_shape():
    s = build_queue_reader_summary((_good_item(),))
    required_keys = {
        "schema_version", "source_schema_version", "label", "status",
        "stage", "mode", "total_items", "valid_item_count",
        "invalid_item_count", "approved_for_research_count",
        "execution_authorized_count", "paper_trading_authorized_count",
        "live_trading_authorized_count", "data_fetch_authorized_count",
        "backtest_authorized_count", "promotion_authorized_count",
        "human_approval_required", "read_only", "executes", "safety",
        "entries", "queue_validation", "next_gate",
    }
    assert required_keys <= set(s.keys())
    assert s["schema_version"] == QUEUE_READER_SCHEMA_VERSION
    assert s["label"] == DEFAULT_QUEUE_READER_LABEL
    assert s["next_gate"] == "human_research_approval"


# 21 -- summary source_schema_version matches Bundle 11.

def test_summary_source_schema_matches_bundle11():
    s = build_queue_reader_summary(())
    assert s["source_schema_version"] == RESEARCH_QUEUE_SCHEMA_VERSION


# 22 + 23 -- deterministic total / valid / invalid counts.

def test_summary_counts_are_deterministic():
    good = _good_item()
    bad = build_research_queue_item("", "", "")
    s = build_queue_reader_summary((good, bad))
    assert s["total_items"] == 2
    assert s["valid_item_count"] == 1
    assert s["invalid_item_count"] == 1
    s2 = build_queue_reader_summary((good, bad))
    assert s == s2


# 24 -- summary authorization counts all 0.

def test_summary_authorization_counts_zero():
    s = build_queue_reader_summary((_good_item(),))
    for key in (
        "approved_for_research_count", "execution_authorized_count",
        "paper_trading_authorized_count", "live_trading_authorized_count",
        "data_fetch_authorized_count", "backtest_authorized_count",
        "promotion_authorized_count",
    ):
        assert s[key] == 0


# 25 -- summary human_approval_required True.

def test_summary_human_approval_required():
    assert build_queue_reader_summary(())["human_approval_required"] is True


# 26 -- summary read_only True.

def test_summary_read_only_true():
    assert build_queue_reader_summary(())["read_only"] is True


# 27 -- summary executes False.

def test_summary_executes_false():
    assert build_queue_reader_summary(())["executes"] is False


# 28 -- summary safety all False.

def test_summary_safety_all_false():
    s = build_queue_reader_summary((_good_item(),))
    assert all(v is False for v in s["safety"].values())


# 29 -- fresh dicts; mutating one result must not taint the next.

def test_results_are_fresh_and_isolated():
    a = build_queue_reader_entry(_good_item())
    b = build_queue_reader_entry(_good_item())
    assert a == b
    assert a is not b
    a["safety"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_queue_reader_entry(_good_item())
    assert fresh["safety"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert QUEUE_READER_SAFETY_POSTURE["automation_enabled"] is False

    s1 = build_queue_reader_summary((_good_item(),))
    s1["safety"]["network_enabled"] = True
    s1["entries"][0]["read_only"] = False
    s2 = build_queue_reader_summary((_good_item(),))
    assert s2["safety"]["network_enabled"] is False
    assert s2["entries"][0]["read_only"] is True


# 30 -- markdown renderers return non-empty strings.

def test_markdown_renderers_non_empty():
    entry = build_queue_reader_entry(_good_item())
    md_e = render_queue_reader_entry_markdown(entry)
    assert isinstance(md_e, str) and md_e
    assert "# Strategy Factory Queue Reader Entry" in md_e
    assert "Stage: PLAN_ONLY" in md_e
    assert "Mode: RESEARCH_ONLY" in md_e
    assert "Human approval required: True" in md_e
    assert "Read only: True" in md_e
    assert "Executes: False" in md_e
    assert "## Summary" in md_e
    assert "## Safety" in md_e
    assert "## Validation" in md_e
    assert "## Next Gate" in md_e

    s = build_queue_reader_summary((_good_item(),))
    md_s = render_queue_reader_summary_markdown(s)
    assert isinstance(md_s, str) and md_s
    assert "# Strategy Factory Queue Reader Summary" in md_s
    assert "Stage: PLAN_ONLY" in md_s
    assert "Mode: RESEARCH_ONLY" in md_s
    assert "Approved for research count: 0" in md_s
    assert "Execution authorized count: 0" in md_s
    assert "Backtest authorized count: 0" in md_s
    assert "Data fetch authorized count: 0" in md_s
    assert "Human approval required: True" in md_s
    assert "Read only: True" in md_s
    assert "Executes: False" in md_s
    assert "## Entries" in md_s
    assert "## Safety" in md_s
    assert "## Queue Validation" in md_s
    assert "## Next Gate" in md_s


# 31 -- markdown renderers write nothing (no file surface in module source).

def test_markdown_renderers_write_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 32 -- ast import-root audit: allowed roots only.

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


# 33 -- ast forbidden-surface audit: no file/network/subprocess/exec surface.

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


# 34 -- prose verb audit over human-readable summaries + markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    entry = build_queue_reader_entry(_good_item())
    summary = build_queue_reader_summary((_good_item(),))
    texts.append(str(entry["summary"]))

    for md in (
        render_queue_reader_entry_markdown(entry),
        render_queue_reader_summary_markdown(summary),
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


# 35 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 36 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["human_approval_required"] is True
    assert q["approved_for_research_count"] == 0
