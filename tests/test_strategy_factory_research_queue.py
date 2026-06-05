"""Bundle 11 tests for the Strategy Factory Research Queue Intake v1
(informational, research-intake only).

Bundle 11's production module is self-contained pure stdlib: it imports only
``__future__`` and ``typing``. These tests import it as a normal package
module. Running under ``python -m pytest`` places the repo root on
``sys.path`` so the ``sparta_commander`` package resolves.

Coverage (per the Bundle 11 spec):
- public API exists and is limited to the expected names,
- schema version / default label / status / stage / mode pinned,
- safety posture all False,
- queue item required shape + RESEARCH_ONLY / PLAN_ONLY / human-gated / inert,
- all authorization flags False,
- validation: valid item, empty fields, wrong schema, non-research mode,
  non-plan stage, any auth flag flipped, any safety flag flipped,
- queue shape + deterministic counts + zero authorization counts,
- queue inert / human-gated / safety-all-false,
- fresh dicts (mutation isolation),
- markdown renderers non-empty + write nothing,
- ast import-root audit + ast forbidden-surface audit,
- prose verb audit over human-readable markdown prose,
- scoped dirty-tree guard (no brain_memory files needed).
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_research_queue import (
    RESEARCH_QUEUE_SCHEMA_VERSION,
    DEFAULT_RESEARCH_QUEUE_LABEL,
    RESEARCH_QUEUE_STATUS,
    RESEARCH_QUEUE_SAFETY_POSTURE,
    DEFAULT_RESEARCH_STAGE,
    DEFAULT_RESEARCH_MODE,
    build_research_queue_item,
    build_research_queue,
    validate_research_queue_item,
    render_research_queue_item_markdown,
    render_research_queue_markdown,
)
import sparta_commander.strategy_factory_research_queue as RQ

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_research_queue.py"
)

# Execution / promotion / trading verbs forbidden in human-readable prose.
_BAD_VERBS = (
    "RUN", "EXECUTE", "LAUNCH", "SUBMIT", "TRADE", "ORDER",
    "PROMOTE", "DEPLOY", "UPLOAD", "FETCH", "BACKTEST",
)


def _expected_public() -> set[str]:
    return {
        "RESEARCH_QUEUE_SCHEMA_VERSION",
        "DEFAULT_RESEARCH_QUEUE_LABEL",
        "RESEARCH_QUEUE_STATUS",
        "RESEARCH_QUEUE_SAFETY_POSTURE",
        "DEFAULT_RESEARCH_STAGE",
        "DEFAULT_RESEARCH_MODE",
        "build_research_queue_item",
        "build_research_queue",
        "validate_research_queue_item",
        "render_research_queue_item_markdown",
        "render_research_queue_markdown",
    }


def _good_item() -> dict:
    return build_research_queue_item(
        "idea-001",
        "Opening Range Mean Reversion",
        "Price tends to revert toward the opening range midpoint intraday.",
        asset_lane="MNQ",
        timeframe="5m",
        source="operator",
        notes=("seed idea", "needs human review"),
    )


# 1 + 2 -- module imports and public API is exactly as expected.

def test_public_api_is_limited_to_expected_names():
    assert set(RQ.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(RQ, name)


# 3 -- schema version pinned.

def test_schema_version_is_pinned():
    assert RESEARCH_QUEUE_SCHEMA_VERSION == "strategy_factory_research_queue.v1"


# 4 -- default label pinned.

def test_default_label_is_pinned():
    assert DEFAULT_RESEARCH_QUEUE_LABEL == "Strategy Factory Research Queue"


# 5 -- status pinned.

def test_status_is_pinned():
    assert RESEARCH_QUEUE_STATUS == "RESEARCH_ONLY_AWAITING_HUMAN_APPROVAL"


# 6 -- default stage pinned.

def test_default_stage_is_pinned():
    assert DEFAULT_RESEARCH_STAGE == "PLAN_ONLY"


# 7 -- default mode pinned.

def test_default_mode_is_pinned():
    assert DEFAULT_RESEARCH_MODE == "RESEARCH_ONLY"


# 8 -- safety posture all exactly False.

def test_safety_posture_all_false():
    assert all(v is False for v in RESEARCH_QUEUE_SAFETY_POSTURE.values())
    assert len(RESEARCH_QUEUE_SAFETY_POSTURE) == 14


# 9 -- build_research_queue_item returns required shape.

def test_item_required_shape():
    item = _good_item()
    required_keys = {
        "schema_version", "idea_id", "title", "thesis", "asset_lane",
        "timeframe", "source", "stage", "mode", "status",
        "approved_for_research", "execution_authorized",
        "paper_trading_authorized", "live_trading_authorized",
        "data_fetch_authorized", "backtest_authorized",
        "promotion_authorized", "human_approval_required", "executes",
        "safety", "notes", "required_next_gate", "validation",
    }
    assert required_keys <= set(item.keys())
    assert item["schema_version"] == RESEARCH_QUEUE_SCHEMA_VERSION
    assert item["status"] == RESEARCH_QUEUE_STATUS
    assert item["required_next_gate"] == "human_research_approval"
    assert item["notes"] == ("seed idea", "needs human review")


# 10 -- item mode is RESEARCH_ONLY.

def test_item_mode_research_only():
    assert _good_item()["mode"] == "RESEARCH_ONLY"


# 11 -- item stage is PLAN_ONLY.

def test_item_stage_plan_only():
    assert _good_item()["stage"] == "PLAN_ONLY"


# 12 -- item human_approval_required True.

def test_item_human_approval_required():
    assert _good_item()["human_approval_required"] is True


# 13 -- item executes False.

def test_item_executes_false():
    assert _good_item()["executes"] is False


# 14 -- all authorization flags False.

def test_item_all_authorization_flags_false():
    item = _good_item()
    for flag in (
        "approved_for_research", "execution_authorized",
        "paper_trading_authorized", "live_trading_authorized",
        "data_fetch_authorized", "backtest_authorized",
        "promotion_authorized",
    ):
        assert item[flag] is False
    assert all(v is False for v in item["safety"].values())


# 15 -- valid item validates valid=True.

def test_valid_item_is_valid():
    v = validate_research_queue_item(_good_item())
    assert v["valid"] is True
    assert v["schema_version_ok"] is True
    assert v["research_only"] is True
    assert v["plan_only"] is True
    assert v["human_approval_required"] is True
    assert v["safety_all_false"] is True
    assert v["missing_required_fields"] == ()


# 16 -- empty required fields validate valid=False and list missing fields.

def test_empty_required_fields_invalid():
    item = build_research_queue_item("", "", "")
    v = item["validation"]
    assert v["valid"] is False
    assert set(v["missing_required_fields"]) == {"idea_id", "title", "thesis"}


# 17 -- validation detects wrong schema version.

def test_validation_detects_wrong_schema_version():
    item = _good_item()
    item["schema_version"] = "wrong.v9"
    v = validate_research_queue_item(item)
    assert v["schema_version_ok"] is False
    assert v["valid"] is False


# 18 -- validation detects non-research mode.

def test_validation_detects_non_research_mode():
    item = _good_item()
    item["mode"] = "SOMETHING_ELSE"
    v = validate_research_queue_item(item)
    assert v["research_only"] is False
    assert v["valid"] is False


# 19 -- validation detects non-plan stage.

def test_validation_detects_non_plan_stage():
    item = _good_item()
    item["stage"] = "SOMETHING_ELSE"
    v = validate_research_queue_item(item)
    assert v["plan_only"] is False
    assert v["valid"] is False


# 20 -- validation detects any authorization flag turned True.

def test_validation_detects_authorization_flag_true():
    for flag in (
        "execution_authorized", "paper_trading_authorized",
        "live_trading_authorized", "data_fetch_authorized",
        "backtest_authorized", "promotion_authorized",
    ):
        item = _good_item()
        item[flag] = True
        v = validate_research_queue_item(item)
        assert v[flag] is True, flag
        assert v["valid"] is False, flag


# 21 -- validation detects any safety flag turned True.

def test_validation_detects_safety_flag_true():
    item = _good_item()
    item["safety"]["live_execution_enabled"] = True
    v = validate_research_queue_item(item)
    assert v["safety_all_false"] is False
    assert v["valid"] is False


# 22 -- build_research_queue returns required shape + deterministic counts.

def test_queue_shape_and_counts():
    good = _good_item()
    bad = build_research_queue_item("", "", "")
    q = build_research_queue((good, bad))
    required_keys = {
        "schema_version", "label", "status", "mode", "stage",
        "total_items", "valid_item_count", "invalid_item_count",
        "approved_for_research_count", "execution_authorized_count",
        "paper_trading_authorized_count", "live_trading_authorized_count",
        "data_fetch_authorized_count", "backtest_authorized_count",
        "promotion_authorized_count", "human_approval_required",
        "executes", "safety", "items", "validation",
    }
    assert required_keys <= set(q.keys())
    assert q["total_items"] == 2
    assert q["valid_item_count"] == 1
    assert q["invalid_item_count"] == 1
    assert q["label"] == DEFAULT_RESEARCH_QUEUE_LABEL
    assert q["status"] == RESEARCH_QUEUE_STATUS
    # deterministic: same inputs -> equal queue
    q2 = build_research_queue((good, bad))
    assert q == q2


# 23 -- queue authorization counts all 0.

def test_queue_authorization_counts_zero():
    q = build_research_queue((_good_item(),))
    for key in (
        "execution_authorized_count", "paper_trading_authorized_count",
        "live_trading_authorized_count", "data_fetch_authorized_count",
        "backtest_authorized_count", "promotion_authorized_count",
    ):
        assert q[key] == 0


# 24 -- queue approved_for_research_count 0.

def test_queue_approved_for_research_count_zero():
    assert build_research_queue((_good_item(),))[
        "approved_for_research_count"] == 0


# 25 -- queue executes False.

def test_queue_executes_false():
    assert build_research_queue((_good_item(),))["executes"] is False


# 26 -- queue human_approval_required True.

def test_queue_human_approval_required():
    assert build_research_queue(())["human_approval_required"] is True


# 27 -- queue safety all False.

def test_queue_safety_all_false():
    q = build_research_queue((_good_item(),))
    assert all(v is False for v in q["safety"].values())


# 28 -- fresh dicts; mutating one result must not taint the next call.

def test_results_are_fresh_and_isolated():
    a = build_research_queue_item("x", "y", "z")
    b = build_research_queue_item("x", "y", "z")
    assert a == b
    assert a is not b
    a["safety"]["automation_enabled"] = True
    a["execution_authorized"] = True
    fresh = build_research_queue_item("x", "y", "z")
    assert fresh["safety"]["automation_enabled"] is False
    assert fresh["execution_authorized"] is False
    assert RESEARCH_QUEUE_SAFETY_POSTURE["automation_enabled"] is False

    q1 = build_research_queue((_good_item(),))
    q1["safety"]["network_enabled"] = True
    q2 = build_research_queue((_good_item(),))
    assert q2["safety"]["network_enabled"] is False


# 29 -- markdown renderers return non-empty strings.

def test_markdown_renderers_non_empty():
    item = _good_item()
    md_item = render_research_queue_item_markdown(item)
    assert isinstance(md_item, str) and md_item
    assert "# Strategy Factory Research Queue Item" in md_item
    assert "Stage: PLAN_ONLY" in md_item
    assert "Mode: RESEARCH_ONLY" in md_item
    assert "Human approval required: True" in md_item
    assert "Executes: False" in md_item
    assert "## Thesis" in md_item
    assert "## Safety" in md_item
    assert "## Validation" in md_item
    assert "## Next Gate" in md_item

    q = build_research_queue((item,))
    md_q = render_research_queue_markdown(q)
    assert isinstance(md_q, str) and md_q
    assert "# Strategy Factory Research Queue" in md_q
    assert "Stage: PLAN_ONLY" in md_q
    assert "Mode: RESEARCH_ONLY" in md_q
    assert "Approved for research count: 0" in md_q
    assert "Execution authorized count: 0" in md_q
    assert "Backtest authorized count: 0" in md_q
    assert "Data fetch authorized count: 0" in md_q
    assert "Human approval required: True" in md_q
    assert "Executes: False" in md_q
    assert "## Items" in md_q
    assert "## Safety" in md_q
    assert "## Validation Summary" in md_q
    assert "## Next Gate" in md_q


# 30 -- markdown renderers write nothing (no file surface in module source).

def test_markdown_renderers_write_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


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
    allowed = {"__future__", "typing"}
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
        "random.", "subprocess.run", "check_output",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


# 33 -- prose verb audit over human-readable markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    item = _good_item()
    q = build_research_queue((item,))

    for md in (
        render_research_queue_item_markdown(item),
        render_research_queue_markdown(q),
    ):
        for ln in md.splitlines():
            stripped = ln.lstrip()
            # skip headings, backtick key/value bullets, and `Label: value`
            # metadata header lines -- those are DATA, not narrative prose:
            # schema-derived count/flag labels legitimately contain words like
            # "Backtest authorized count" / "Data fetch authorized count".
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


# 34 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    # The production module never references the operator's Brain Memory
    # notes, so this bundle cannot require touching brain_memory files.
    assert "brain_memory" not in src
