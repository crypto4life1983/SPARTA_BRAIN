"""Bundle 17 tests for the Strategy Factory Research Pipeline Closure Report v1
(informational, read-only, closure-report-only).

Bundle 17's production module imports Bundles 11, 12, 13, 14, 15 and 16 via
real package imports, so these tests use normal package imports too. Running
under ``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 17 spec):
- public API exists and is limited to the expected names,
- schema version / default label / status / gate constants pinned,
- safety posture all False and keys identical to Bundle 16 posture,
- report shape, read-only / inert / human-gated / phase-complete,
- next phase gate defaults to PAUSE_AND_REVIEW + exact options,
- schema_versions / statuses match Bundles 11-16,
- pipeline_sequence is Bundles 11-16 in order,
- layer_checks count 6, each read_only / inert / safety-all-false,
- sample_flow members + zero authorization counts + no auth surface,
- closure_checks booleans as specified,
- recommended_next_steps deterministic + non-empty,
- returned dicts are fresh (mutation isolation),
- markdown renderer non-empty + writes nothing,
- ast import-root audit + ast forbidden-surface audit,
- prose verb audit over next-steps / closure checks / markdown prose,
- scoped dirty-tree guard, Bundle 11/12/13/14/15/16 regression imports.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_research_pipeline_closure import (
    RESEARCH_PIPELINE_CLOSURE_SCHEMA_VERSION,
    DEFAULT_RESEARCH_PIPELINE_CLOSURE_LABEL,
    RESEARCH_PIPELINE_CLOSURE_STATUS,
    RESEARCH_PIPELINE_CLOSURE_SAFETY_POSTURE,
    NEXT_PHASE_GATE_PAUSE_AND_REVIEW,
    NEXT_PHASE_GATE_PROTOCOL_DRAFT_ONLY,
    NEXT_PHASE_GATE_DATA_CONTRACT_PLANNING_ONLY,
    build_research_pipeline_closure_report,
    render_research_pipeline_closure_markdown,
)
import sparta_commander.strategy_factory_research_pipeline_closure as PC
from sparta_commander.strategy_factory_research_queue import (
    RESEARCH_QUEUE_SCHEMA_VERSION,
    RESEARCH_QUEUE_STATUS,
)
from sparta_commander.strategy_factory_queue_reader import (
    QUEUE_READER_SCHEMA_VERSION,
    QUEUE_READER_STATUS,
)
from sparta_commander.strategy_factory_queue_planner import (
    QUEUE_PLANNER_SCHEMA_VERSION,
    QUEUE_PLANNER_STATUS,
)
from sparta_commander.strategy_factory_research_task_packet import (
    RESEARCH_TASK_PACKET_SCHEMA_VERSION,
    RESEARCH_TASK_PACKET_STATUS,
)
from sparta_commander.strategy_factory_research_report_contract import (
    RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION,
    RESEARCH_REPORT_CONTRACT_STATUS,
)
from sparta_commander.strategy_factory_research_decision_memo_contract import (
    RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION,
    RESEARCH_DECISION_MEMO_CONTRACT_STATUS,
    RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_research_pipeline_closure.py"
)

# Execution / promotion / trading verbs forbidden in human-readable prose.
_BAD_VERBS = (
    "RUN", "EXECUTE", "LAUNCH", "SUBMIT", "TRADE", "ORDER",
    "PROMOTE", "DEPLOY", "UPLOAD", "FETCH", "BACKTEST",
)

_AUTH_COUNTS = (
    "approved_for_research_count", "execution_authorized_count",
    "paper_trading_authorized_count", "live_trading_authorized_count",
    "data_fetch_authorized_count", "backtest_authorized_count",
    "promotion_authorized_count",
)

_EXPECTED_GATES = (
    "PAUSE_AND_REVIEW", "PROTOCOL_DRAFT_ONLY",
    "DATA_CONTRACT_PLANNING_ONLY",
)

_EXPECTED_SEQUENCE = (
    "research_queue", "queue_reader", "queue_planner",
    "research_task_packet", "research_report_contract",
    "research_decision_memo_contract",
)


def _report() -> dict:
    return build_research_pipeline_closure_report()


def _expected_public() -> set[str]:
    return {
        "RESEARCH_PIPELINE_CLOSURE_SCHEMA_VERSION",
        "DEFAULT_RESEARCH_PIPELINE_CLOSURE_LABEL",
        "RESEARCH_PIPELINE_CLOSURE_STATUS",
        "RESEARCH_PIPELINE_CLOSURE_SAFETY_POSTURE",
        "NEXT_PHASE_GATE_PAUSE_AND_REVIEW",
        "NEXT_PHASE_GATE_PROTOCOL_DRAFT_ONLY",
        "NEXT_PHASE_GATE_DATA_CONTRACT_PLANNING_ONLY",
        "build_research_pipeline_closure_report",
        "render_research_pipeline_closure_markdown",
    }


# 1 + 2 -- module imports and public API is exactly as expected.

def test_public_api_is_limited_to_expected_names():
    assert set(PC.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(PC, name)


# 3 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        RESEARCH_PIPELINE_CLOSURE_SCHEMA_VERSION
        == "strategy_factory_research_pipeline_closure.v1"
    )


# 4 -- default label pinned.

def test_default_label_is_pinned():
    assert (
        DEFAULT_RESEARCH_PIPELINE_CLOSURE_LABEL
        == "Strategy Factory Research Pipeline Closure Report"
    )


# 5 -- status pinned.

def test_status_is_pinned():
    assert RESEARCH_PIPELINE_CLOSURE_STATUS == "READ_ONLY_PHASE_CLOSURE"


# 6 -- next phase gate constants pinned.

def test_next_phase_gate_constants_are_pinned():
    assert NEXT_PHASE_GATE_PAUSE_AND_REVIEW == "PAUSE_AND_REVIEW"
    assert NEXT_PHASE_GATE_PROTOCOL_DRAFT_ONLY == "PROTOCOL_DRAFT_ONLY"
    assert (
        NEXT_PHASE_GATE_DATA_CONTRACT_PLANNING_ONLY
        == "DATA_CONTRACT_PLANNING_ONLY"
    )


# 7 -- safety posture all False.

def test_safety_posture_all_false():
    assert all(
        v is False for v in RESEARCH_PIPELINE_CLOSURE_SAFETY_POSTURE.values()
    )


# 8 -- safety posture keys match Bundle 16.

def test_safety_posture_keys_match_bundle16():
    assert (
        set(RESEARCH_PIPELINE_CLOSURE_SAFETY_POSTURE.keys())
        == set(RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE.keys())
    )


# 9 -- report required shape.

def test_report_required_shape():
    r = _report()
    required_keys = {
        "schema_version", "label", "status", "stage", "mode", "read_only",
        "executes", "human_approval_required", "phase_complete",
        "next_phase_gate", "next_phase_options", "schema_versions",
        "statuses", "pipeline_sequence", "safety", "layer_checks",
        "sample_flow", "closure_checks", "recommended_next_steps",
    }
    assert required_keys <= set(r.keys())
    assert r["schema_version"] == RESEARCH_PIPELINE_CLOSURE_SCHEMA_VERSION
    assert r["status"] == RESEARCH_PIPELINE_CLOSURE_STATUS
    assert r["label"] == DEFAULT_RESEARCH_PIPELINE_CLOSURE_LABEL


# 10 -- report stage PLAN_ONLY.

def test_report_stage_plan_only():
    assert _report()["stage"] == "PLAN_ONLY"


# 11 -- report mode RESEARCH_ONLY.

def test_report_mode_research_only():
    assert _report()["mode"] == "RESEARCH_ONLY"


# 12 -- report read_only True.

def test_report_read_only_true():
    assert _report()["read_only"] is True


# 13 -- report executes False.

def test_report_executes_false():
    assert _report()["executes"] is False


# 14 -- report human_approval_required True.

def test_report_human_approval_required():
    assert _report()["human_approval_required"] is True


# 15 -- report phase_complete True.

def test_report_phase_complete_true():
    assert _report()["phase_complete"] is True


# 16 -- report next_phase_gate defaults to PAUSE_AND_REVIEW.

def test_report_next_phase_gate_default():
    assert _report()["next_phase_gate"] == "PAUSE_AND_REVIEW"


# 17 -- next_phase_options contain exactly the three gate constants.

def test_next_phase_options_exact():
    assert tuple(_report()["next_phase_options"]) == _EXPECTED_GATES


# 18 -- schema_versions match Bundles 11/12/13/14/15/16.

def test_schema_versions_match():
    sv = _report()["schema_versions"]
    assert sv["research_queue"] == RESEARCH_QUEUE_SCHEMA_VERSION
    assert sv["queue_reader"] == QUEUE_READER_SCHEMA_VERSION
    assert sv["queue_planner"] == QUEUE_PLANNER_SCHEMA_VERSION
    assert sv["research_task_packet"] == RESEARCH_TASK_PACKET_SCHEMA_VERSION
    assert sv["research_report_contract"] \
        == RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION
    assert sv["research_decision_memo_contract"] \
        == RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION


# 19 -- statuses match Bundles 11/12/13/14/15/16.

def test_statuses_match():
    st = _report()["statuses"]
    assert st["research_queue"] == RESEARCH_QUEUE_STATUS
    assert st["queue_reader"] == QUEUE_READER_STATUS
    assert st["queue_planner"] == QUEUE_PLANNER_STATUS
    assert st["research_task_packet"] == RESEARCH_TASK_PACKET_STATUS
    assert st["research_report_contract"] == RESEARCH_REPORT_CONTRACT_STATUS
    assert st["research_decision_memo_contract"] \
        == RESEARCH_DECISION_MEMO_CONTRACT_STATUS


# 20 -- pipeline_sequence includes Bundles 11-16 in order.

def test_pipeline_sequence_order():
    assert tuple(_report()["pipeline_sequence"]) == _EXPECTED_SEQUENCE


# 21 -- safety all False.

def test_report_safety_all_false():
    assert all(v is False for v in _report()["safety"].values())


# 22 -- layer_checks count equals 6.

def test_layer_checks_count():
    assert len(_report()["layer_checks"]) == 6


# 23 + 24 + 25 -- every layer check read_only / executes False / safe.

def test_layer_checks_inert():
    for check in _report()["layer_checks"]:
        assert check["read_only"] is True
        assert check["executes"] is False
        assert check["safety_all_false"] is True


# 26 -- sample_flow includes all six members.

def test_sample_flow_members():
    sf = _report()["sample_flow"]
    for key in (
        "queue_item", "reader_summary", "planner_summary",
        "task_packet_batch", "report_contract_batch",
        "decision_memo_contract_batch",
    ):
        assert key in sf


# 27 -- sample_flow authorization counts remain zero.

def test_sample_flow_authorization_counts_zero():
    sf = _report()["sample_flow"]
    for batch_key in (
        "task_packet_batch", "report_contract_batch",
        "decision_memo_contract_batch",
    ):
        batch = sf[batch_key]
        for count_key in _AUTH_COUNTS:
            assert batch.get(count_key, 0) == 0, (batch_key, count_key)


# 28 -- sample_flow does not authorize data/backtest/execution/trading.

def test_sample_flow_authorizes_nothing():
    sf = _report()["sample_flow"]
    for batch_key in (
        "task_packet_batch", "report_contract_batch",
        "decision_memo_contract_batch",
    ):
        batch = sf[batch_key]
        assert batch["executes"] is False
        assert batch["human_approval_required"] is True


# 29 -- closure_checks booleans are as specified.

def test_closure_checks_booleans():
    cc = _report()["closure_checks"]
    assert cc["all_safety_flags_false"] is True
    assert cc["all_authorization_counts_zero"] is True
    assert cc["read_only"] is True
    assert cc["executes"] is False
    assert cc["no_data_fetch"] is True
    assert cc["no_backtest"] is True
    assert cc["no_market_data_inspection"] is True
    assert cc["no_broker_exchange_order"] is True
    assert cc["no_upload_autopilot"] is True
    assert cc["requires_operator_next_phase_decision"] is True


# 30 -- recommended_next_steps deterministic and non-empty.

def test_recommended_next_steps():
    r = _report()
    steps = r["recommended_next_steps"]
    assert isinstance(steps, tuple) and len(steps) >= 1
    assert all(isinstance(s, str) and s for s in steps)
    assert _report()["recommended_next_steps"] == steps


# 31 -- fresh dicts; mutating one result must not taint the next.

def test_results_are_fresh_and_isolated():
    a = build_research_pipeline_closure_report()
    b = build_research_pipeline_closure_report()
    assert a == b
    assert a is not b
    a["safety"]["automation_enabled"] = True
    a["read_only"] = False
    a["closure_checks"]["read_only"] = False
    fresh = build_research_pipeline_closure_report()
    assert fresh["safety"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert fresh["closure_checks"]["read_only"] is True
    assert (
        RESEARCH_PIPELINE_CLOSURE_SAFETY_POSTURE["automation_enabled"] is False
    )


# 32 -- markdown renderer returns non-empty string + expected sections.

def test_markdown_renderer_non_empty():
    md = render_research_pipeline_closure_markdown(_report())
    assert isinstance(md, str) and md
    assert "# Strategy Factory Research Pipeline Closure Report" in md
    assert "Stage: PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Phase complete: True" in md
    assert "Next phase gate: PAUSE_AND_REVIEW" in md
    assert "Human approval required: True" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "## Pipeline Sequence" in md
    assert "## Schema Versions" in md
    assert "## Layer Checks" in md
    assert "## Closure Checks" in md
    assert "## Recommended Next Steps" in md
    assert "## Safety" in md


# 33 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 34 -- ast import-root audit: allowed roots only.

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


# 35 -- ast forbidden-surface audit: no file/network/subprocess/exec surface.

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


# 36 -- prose verb audit over next steps / closure checks / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    r = _report()

    texts.extend(str(s) for s in r["recommended_next_steps"])
    # closure_check VALUES are booleans (data), not narrative; audit them too.
    texts.extend(str(v) for v in r["closure_checks"].values())

    md = render_research_pipeline_closure_markdown(r)
    for ln in md.splitlines():
        stripped = ln.lstrip()
        # skip headings, backtick key/value bullets, and `Label: value`
        # metadata header lines -- those are DATA, not narrative prose
        # (schema-derived keys legitimately contain words like "backtest").
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


# 37 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 38 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue, build_research_queue_item,
    )
    item = build_research_queue_item("idea-x", "X", "Thesis X is well-formed.")
    q = build_research_queue((item,))
    assert q["executes"] is False
    assert q["human_approval_required"] is True
    assert q["approved_for_research_count"] == 0


# 39 -- Bundle 12 regression import still works.

def test_bundle12_regression_import_still_works():
    from sparta_commander.strategy_factory_queue_reader import (
        build_queue_reader_summary,
    )
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue_item,
    )
    item = build_research_queue_item("idea-x", "X", "Thesis X is well-formed.")
    s = build_queue_reader_summary((item,))
    assert s["executes"] is False
    assert s["valid_item_count"] == 1


# 40 -- Bundle 13 regression import still works.

def test_bundle13_regression_import_still_works():
    from sparta_commander.strategy_factory_queue_planner import (
        build_queue_plan_summary,
    )
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue_item,
    )
    item = build_research_queue_item("idea-x", "X", "Thesis X is well-formed.")
    s = build_queue_plan_summary((item,))
    assert s["executes"] is False
    assert s["valid_item_count"] == 1


# 41 -- Bundle 14 regression import still works.

def test_bundle14_regression_import_still_works():
    from sparta_commander.strategy_factory_research_task_packet import (
        build_research_task_packet_batch,
    )
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue_item,
    )
    item = build_research_queue_item("idea-x", "X", "Thesis X is well-formed.")
    b = build_research_task_packet_batch((item,))
    assert b["executes"] is False
    assert b["human_approval_required"] is True
    assert b["total_items"] == 1


# 42 -- Bundle 15 regression import still works.

def test_bundle15_regression_import_still_works():
    from sparta_commander.strategy_factory_research_report_contract import (
        build_research_report_contract_batch,
    )
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue_item,
    )
    item = build_research_queue_item("idea-x", "X", "Thesis X is well-formed.")
    b = build_research_report_contract_batch((item,))
    assert b["executes"] is False
    assert b["human_approval_required"] is True
    assert b["total_items"] == 1


# 43 -- Bundle 16 regression import still works.

def test_bundle16_regression_import_still_works():
    from sparta_commander.strategy_factory_research_decision_memo_contract \
        import build_research_decision_memo_contract_batch
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue_item,
    )
    item = build_research_queue_item("idea-x", "X", "Thesis X is well-formed.")
    b = build_research_decision_memo_contract_batch((item,))
    assert b["executes"] is False
    assert b["human_approval_required"] is True
    assert b["total_items"] == 1
