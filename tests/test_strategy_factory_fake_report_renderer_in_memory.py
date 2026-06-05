"""Bundle 38 tests for the Strategy Factory Fake Report Renderer In-Memory
implementation v1 (informational, read-only, fake-only, in-memory-only,
deterministic, execution-free -- NO written report on disk, NO report file
write, NO real dry walk, NO orchestrator, NO real pipeline, NO smoke-test run,
NO runtime state write, NO research, NO data access).

This is the FIRST renderer bundle that actually constructs fake placeholder
report content IN MEMORY (dicts + a markdown string). It still writes nothing,
reads nothing, and grants nothing. Its novel guard: validation REJECTS any
content that smuggles in a real artifact name (Crypto-D1, qa_report.json,
manifest.json, CHECKSUMS.txt, FREEZE_RECORD.txt, fees.json, baseline outputs,
dataset names, .csv, .parquet, /data/, real market-data paths).

Bundle 38's production module imports Bundles 11-37 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_fake_report_renderer_in_memory import (
    RENDERER_IN_MEMORY_SCHEMA_VERSION,
    DEFAULT_RENDERER_IN_MEMORY_LABEL,
    RENDERER_IN_MEMORY_STATUS,
    RENDERER_IN_MEMORY_SAFETY_POSTURE,
    RENDERER_IN_MEMORY_STATE_ACTIVE,
    RENDERER_IN_MEMORY_STATE_BLOCKED,
    NEXT_GATE_FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED,
    NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_CONTRACT,
    REQUIRED_REPORT_SECTIONS,
    REAL_ARTIFACT_GUARD_TOKENS,
    build_fake_report_renderer_state,
    validate_fake_report_renderer_state,
    render_fake_report_markdown,
)
import sparta_commander.strategy_factory_fake_report_renderer_in_memory as RM
from sparta_commander.strategy_factory_fake_report_renderer_contract import (
    RENDERER_CONTRACT_SCHEMA_VERSION,
    RENDERER_CONTRACT_SAFETY_POSTURE,
    RENDERER_SCOPE,
    build_fake_report_renderer_contract,
)
from sparta_commander.strategy_factory_fake_walk_report_operator_review_gate import (  # noqa: E501
    OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT,
    build_fake_walk_report_operator_review_gate,
)
from sparta_commander.strategy_factory_fake_walk_report_contract import (
    build_fake_walk_report_contract,
)
from sparta_commander.strategy_factory_fake_dry_walk_result_review_contract import (  # noqa: E501
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT,
    build_fake_dry_walk_result_review_contract,
)
from sparta_commander.strategy_factory_fake_dry_walk_in_memory import (
    build_fake_dry_walk_state,
)
from sparta_commander.strategy_factory_fake_dry_walk_implementation_contract import (  # noqa: E501
    build_fake_dry_walk_implementation_contract,
)
from sparta_commander.strategy_factory_fake_dry_walk_operator_review_gate import (
    OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT,
    build_fake_dry_walk_operator_review_gate,
)
from sparta_commander.strategy_factory_fake_artifact_dry_walk_contract import (
    build_fake_artifact_dry_walk_contract,
)
from sparta_commander.strategy_factory_fake_artifact_smoke_test_contract import (
    build_fake_artifact_smoke_test_contract,
)
from sparta_commander.strategy_factory_backbone_closure_report import (
    build_backbone_closure_report,
)
from sparta_commander.strategy_factory_end_to_end_fake_pipeline_contract import (
    build_end_to_end_fake_pipeline_contract,
)
from sparta_commander.strategy_factory_safety_kill_switch_contract import (
    build_safety_kill_switch_contract,
)
from sparta_commander.strategy_factory_decision_ledger_contract import (
    build_decision_ledger_contract,
)
from sparta_commander.strategy_factory_dashboard_registry_feed_contract import (
    build_dashboard_registry_feed_contract,
)
from sparta_commander.strategy_factory_dry_run_orchestrator_contract import (
    build_dry_run_orchestrator_contract,
)
from sparta_commander.strategy_factory_research_runner_contract import (
    build_research_runner_contract,
)
from sparta_commander.strategy_factory_data_qa_contract import (
    build_data_qa_contract,
)
from sparta_commander.strategy_factory_data_contract_planning import (
    build_data_contract_planning,
)
from sparta_commander.strategy_factory_protocol_review_gate import (
    REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    build_protocol_review_gate,
)
from sparta_commander.strategy_factory_research_protocol_draft_contract import (
    build_research_protocol_draft_contract,
)
from sparta_commander.strategy_factory_research_decision_memo_contract import (
    MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
)
from sparta_commander.strategy_factory_research_queue import (
    build_research_queue_item,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_fake_report_renderer_in_memory.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

_BAD_VERBS = (
    "RUN", "EXECUTE", "LAUNCH", "SUBMIT", "TRADE", "ORDER",
    "PROMOTE", "DEPLOY", "UPLOAD", "FETCH", "BACKTEST",
)

_AUTH_FLAGS = (
    "approved_for_research", "execution_authorized",
    "paper_trading_authorized", "live_trading_authorized",
    "data_fetch_authorized", "backtest_authorized", "promotion_authorized",
)

_EXPECTED_POSTURE_KEYS = {
    "automation_enabled", "live_execution_enabled", "paper_execution_enabled",
    "file_write_enabled", "network_enabled", "subprocess_enabled",
    "strategy_promotion_enabled", "broker_enabled", "exchange_enabled",
    "order_enabled", "data_fetch_enabled", "backtest_enabled",
    "upload_enabled", "autopilot_enabled",
}

_EXPECTED_SECTION_HEADERS = (
    "## Executive Summary",
    "## Fake Walk Scope",
    "## Fake Stage Walk Summary",
    "## Fake Trace Summary",
    "## Operator Review Summary",
    "## Pass Fail Summary",
    "## Safety Attestation",
    "## Blocked Capabilities",
    "## Next Steps",
    "## Operator Notes",
    "## Safety",
)


def _good_item() -> dict:
    return build_research_queue_item(
        "idea-001",
        "Opening Range Mean Reversion",
        "Price tends to revert toward the opening range midpoint intraday.",
        asset_lane="MNQ",
        timeframe="5m",
    )


def _ready_closure() -> dict:
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(
        draft, review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING)
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    orchestrator = build_dry_run_orchestrator_contract(runner)
    feed = build_dashboard_registry_feed_contract(orchestrator)
    ledger = build_decision_ledger_contract(feed)
    safety_gate = build_safety_kill_switch_contract(ledger)
    pipeline = build_end_to_end_fake_pipeline_contract(safety_gate)
    return build_backbone_closure_report(pipeline)


def _blocked_closure() -> dict:
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(draft)  # awaiting, not unlocked
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    orchestrator = build_dry_run_orchestrator_contract(runner)
    feed = build_dashboard_registry_feed_contract(orchestrator)
    ledger = build_decision_ledger_contract(feed)
    safety_gate = build_safety_kill_switch_contract(ledger)
    pipeline = build_end_to_end_fake_pipeline_contract(safety_gate)
    return build_backbone_closure_report(pipeline)


def _active_walk_state() -> dict:
    smoke = build_fake_artifact_smoke_test_contract(_ready_closure())
    dry_walk = build_fake_artifact_dry_walk_contract(smoke)
    gate = build_fake_dry_walk_operator_review_gate(
        dry_walk,
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
        ),
    )
    contract = build_fake_dry_walk_implementation_contract(gate)
    return build_fake_dry_walk_state(contract)


def _blocked_walk_state() -> dict:
    smoke = build_fake_artifact_smoke_test_contract(_blocked_closure())
    dry_walk = build_fake_artifact_dry_walk_contract(smoke)
    gate = build_fake_dry_walk_operator_review_gate(dry_walk)
    contract = build_fake_dry_walk_implementation_contract(gate)
    return build_fake_dry_walk_state(contract)


def _active_contract() -> dict:
    review = build_fake_dry_walk_result_review_contract(
        _active_walk_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
        ),
    )
    report = build_fake_walk_report_contract(review)
    gate = build_fake_walk_report_operator_review_gate(
        report,
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT
        ),
    )
    return build_fake_report_renderer_contract(gate)


def _blocked_contract() -> dict:
    review = build_fake_dry_walk_result_review_contract(
        _blocked_walk_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
        ),
    )
    report = build_fake_walk_report_contract(review)
    gate = build_fake_walk_report_operator_review_gate(
        report,
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT
        ),
    )
    return build_fake_report_renderer_contract(gate)


def _state(contract=None, **kw) -> dict:
    return build_fake_report_renderer_state(
        contract if contract is not None else _active_contract(), **kw)


def _expected_public() -> set[str]:
    return {
        "RENDERER_IN_MEMORY_SCHEMA_VERSION",
        "DEFAULT_RENDERER_IN_MEMORY_LABEL",
        "RENDERER_IN_MEMORY_STATUS",
        "RENDERER_IN_MEMORY_SAFETY_POSTURE",
        "RENDERER_IN_MEMORY_STATE_ACTIVE",
        "RENDERER_IN_MEMORY_STATE_BLOCKED",
        "NEXT_GATE_FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED",
        "NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_CONTRACT",
        "REQUIRED_REPORT_SECTIONS",
        "REAL_ARTIFACT_GUARD_TOKENS",
        "build_fake_report_renderer_state",
        "validate_fake_report_renderer_state",
        "render_fake_report_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(RM.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(RM, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        RENDERER_IN_MEMORY_SCHEMA_VERSION
        == "strategy_factory_fake_report_renderer_in_memory.v1"
    )
    assert (
        DEFAULT_RENDERER_IN_MEMORY_LABEL
        == "Strategy Factory Fake Report Renderer In Memory"
    )
    assert (
        RENDERER_IN_MEMORY_STATUS
        == "READ_ONLY_FAKE_REPORT_RENDERER_IN_MEMORY"
    )


# 3 -- state / next-gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        RENDERER_IN_MEMORY_STATE_ACTIVE
        == "FAKE_REPORT_RENDERER_IN_MEMORY_ACTIVE"
    )
    assert (
        RENDERER_IN_MEMORY_STATE_BLOCKED
        == "FAKE_REPORT_RENDERER_IN_MEMORY_BLOCKED"
    )
    assert (
        NEXT_GATE_FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED
        == "FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED"
    )
    assert (
        NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_CONTRACT
        == "AWAIT_FAKE_REPORT_RENDERER_CONTRACT"
    )


# 4 -- required report sections are the exact 9-tuple.

def test_required_report_sections_exact():
    assert REQUIRED_REPORT_SECTIONS == (
        "executive_summary",
        "fake_walk_scope",
        "fake_stage_walk_summary",
        "fake_trace_summary",
        "operator_review_summary",
        "pass_fail_summary",
        "safety_attestation",
        "blocked_capabilities",
        "next_steps",
    )


# 5 -- real artifact guard tokens include every required real name.

def test_real_artifact_guard_tokens_present():
    for tok in ("Crypto-D1", "qa_report.json", "manifest.json",
                "CHECKSUMS.txt", "FREEZE_RECORD.txt", "fees.json",
                ".csv", ".parquet", "/data/"):
        assert tok in REAL_ARTIFACT_GUARD_TOKENS, tok
    assert "real_dataset_name" in REAL_ARTIFACT_GUARD_TOKENS
    assert "baseline_output" in REAL_ARTIFACT_GUARD_TOKENS
    assert "real_market_data_path" in REAL_ARTIFACT_GUARD_TOKENS


# 6 -- pure stdlib import-root audit: allowed roots only.

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
                   "datetime", "time", "random", "glob", "importlib",
                   "shutil", "io"):
        assert banned not in roots, f"banned import root present: {banned}"


# 7 -- forbidden-surface audit: no file/network/subprocess/exec/dynamic surface.

def test_no_forbidden_call_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    forbidden = (
        "open(", "write_text(", "write_bytes(", ".write(", "read_text(",
        "read_bytes(", ".read(", "json.dump(", "json.load(",
        "import subprocess", "from subprocess", "Popen", "os.system",
        "os.listdir", "os.scandir", "os.walk", "listdir(", "scandir(",
        "glob(", "iglob(", "import socket", "socket.socket", "urllib",
        "requests", "httpx", "http.client", "asyncio", "place_order",
        "submit_order", "create_order", "cancel_order", "ccxt", "freqtrade",
        "paper_trade", "live_trade", "autopilot(", ".upload(", "datetime.",
        "time.time(", "random.", "subprocess.run", "check_output",
        "importlib", "__import__", "eval(", "exec(", "compile(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


# 8 -- no filesystem read/write surface in source.

def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# 9 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = RENDERER_IN_MEMORY_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 10 -- posture keys + values match Bundle 37.

def test_posture_matches_bundle37():
    assert (
        RENDERER_IN_MEMORY_SAFETY_POSTURE == RENDERER_CONTRACT_SAFETY_POSTURE
    )


# 11 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _state()
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _state()
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert RENDERER_IN_MEMORY_SAFETY_POSTURE["automation_enabled"] is False


# 12 -- an active Bundle 37 contract activates the in-memory renderer.

def test_active_contract_activates_renderer():
    s = _state()
    assert s["fake_report_renderer_active"] is True
    assert (
        s["fake_report_renderer_state"]
        == "FAKE_REPORT_RENDERER_IN_MEMORY_ACTIVE"
    )
    assert s["fake_report_renderer_contract_active"] is True
    assert (
        s["fake_report_renderer_contract_next_gate"]
        == "FAKE_REPORT_RENDERER_BUILD_REVIEW_REQUIRED"
    )
    assert s["next_gate"] == "FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED"
    assert s["schema_version"] == RENDERER_IN_MEMORY_SCHEMA_VERSION
    assert (
        s["fake_report_renderer_contract_schema_version"]
        == RENDERER_CONTRACT_SCHEMA_VERSION
    )


# 13 -- a blocked (inactive) upstream contract does not activate.

def test_blocked_contract_does_not_activate():
    s = _state(_blocked_contract())
    assert s["fake_report_renderer_active"] is False
    assert (
        s["fake_report_renderer_state"]
        == "FAKE_REPORT_RENDERER_IN_MEMORY_BLOCKED"
    )
    assert s["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_CONTRACT"


# 14 -- active contract but wrong next_gate does not activate.

def test_wrong_next_gate_does_not_activate():
    import copy
    c = copy.deepcopy(_active_contract())
    c["next_gate"] = "SOMETHING_ELSE"
    s = _state(c)
    assert s["fake_report_renderer_active"] is False
    assert s["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_CONTRACT"


# 15 -- active contract but wrong renderer_scope does not activate.

def test_wrong_scope_does_not_activate():
    import copy
    c = copy.deepcopy(_active_contract())
    c["renderer_scope"] = ("fake_only", "wrong")
    s = _state(c)
    assert s["fake_report_renderer_active"] is False
    assert s["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_CONTRACT"


# 16 -- inactive contract flag does not activate even with right gate + scope.

def test_inactive_contract_flag_does_not_activate():
    import copy
    c = copy.deepcopy(_active_contract())
    c["fake_report_renderer_contract_active"] = False
    s = _state(c)
    assert s["fake_report_renderer_active"] is False
    assert s["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_CONTRACT"


# 17 -- malformed input never raises and never activates.

def test_malformed_input_no_raise():
    for bad in (None, 42, "nope", {},
                {"fake_report_renderer_contract_active": True}, []):
        s = build_fake_report_renderer_state(bad)
        assert s["fake_report_renderer_active"] is False
        assert s["read_only"] is True
        assert s["executes"] is False
        assert s["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_CONTRACT"
        for flag in _AUTH_FLAGS:
            assert s[flag] is False


# 18 -- all 9 required report sections present in report_sections dict.

def test_all_required_sections_present():
    s = _state()
    sections = s["report_sections"]
    assert isinstance(sections, dict)
    for name in REQUIRED_REPORT_SECTIONS:
        assert name in sections
        assert isinstance(sections[name], str) and sections[name]


# 19 -- rendered_markdown_preview is a non-empty in-memory string.

def test_rendered_markdown_preview_in_memory_only():
    s = _state()
    preview = s["rendered_markdown_preview"]
    assert isinstance(preview, str) and preview
    assert preview.startswith(
        "# Strategy Factory Fake Report (Fake In-Memory Render)")


# 20 -- markdown says the required descriptors + every section header.

def test_markdown_descriptors_and_headers():
    s = _state()
    md = render_fake_report_markdown(s)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Fake Report (Fake In-Memory Render)" in md
    for descriptor in ("fake-report-renderer-in-memory-only",
                       "placeholder-only", "research-only", "execution-free",
                       "no-report-file-write", "no-runtime-state-write"):
        assert descriptor in md, descriptor
    for header in _EXPECTED_SECTION_HEADERS:
        assert header in md, header
    assert "Stage: FAKE_REPORT_RENDER_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "Next gate: FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED" in md


# 21 -- the build-time preview matches a fresh re-render of the state.

def test_preview_matches_rerender():
    s = _state()
    assert s["rendered_markdown_preview"] == render_fake_report_markdown(s)


# 22 -- default fake content is clean (no real artifact references).

def test_default_content_has_no_real_artifacts():
    s = _state()
    v = validate_fake_report_renderer_state(s)
    assert v["valid"] is True
    assert v["real_artifact_hits"] == ()
    assert v["no_real_artifacts"] is True


# 23 -- validation flags an injected real artifact reference.

def test_validation_flags_injected_real_artifact():
    s = _state(
        fake_overrides={
            "fake_walk_summary": {
                "fake_walk_note_placeholder": "see Crypto-D1 data",
            },
        },
    )
    v = validate_fake_report_renderer_state(s)
    assert v["valid"] is False
    assert "Crypto-D1" in v["real_artifact_hits"]
    assert v["no_real_artifacts"] is False
    # The state's own embedded validation agrees.
    assert s["validation"]["valid"] is False


# 24 -- validation flags a real artifact smuggled into report_sections too.

def test_validation_flags_injected_artifact_in_sections():
    s = _state(
        fake_overrides={
            "report_sections": {
                "executive_summary": "loads qa_report.json and a .csv file",
            },
        },
    )
    v = validate_fake_report_renderer_state(s)
    assert v["valid"] is False
    hits = set(v["real_artifact_hits"])
    assert "qa_report.json" in hits
    assert ".csv" in hits


# 25 -- no authorization flag can become True (any state).

def test_authorization_flags_always_false():
    states = [
        _state(),
        _state(_blocked_contract()),
        build_fake_report_renderer_state({}),
        _state(fake_overrides={
            "fake_walk_summary": {
                "fake_walk_note_placeholder": "Crypto-D1",
            },
        }),
    ]
    for s in states:
        for flag in _AUTH_FLAGS:
            assert s[flag] is False
        assert all(v is False for v in s["safety_posture"].values())
        assert s["executes"] is False
        assert s["read_only"] is True
        assert s["human_approval_required"] is True
        assert s["mode"] == "RESEARCH_ONLY"
        assert s["stage"] == "FAKE_REPORT_RENDER_ONLY"


# 26 -- even an active state authorizes no data/runtime/report-write surface.

def test_active_state_authorizes_no_runtime_or_report_write():
    s = _state()
    assert s["data_fetch_authorized"] is False
    assert s["backtest_authorized"] is False
    assert s["execution_authorized"] is False
    assert s["promotion_authorized"] is False
    assert s["safety_posture"]["data_fetch_enabled"] is False
    assert s["safety_posture"]["file_write_enabled"] is False
    assert s["safety_posture"]["automation_enabled"] is False
    blocked = set(s["blocked_capabilities"])
    assert "report_file_write" in blocked
    assert "report_renderer_implementation_execution" in blocked
    assert "runtime_state_write" in blocked
    assert "file_write" in blocked
    assert "file_read" in blocked


# 27 -- validate passes for a clean state + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    s = _state()
    v = validate_fake_report_renderer_state(s)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(s)
    bad["execution_authorized"] = True
    assert validate_fake_report_renderer_state(bad)["valid"] is False

    bad2 = copy.deepcopy(s)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_fake_report_renderer_state(bad2)["valid"] is False

    bad3 = copy.deepcopy(s)
    bad3["mode"] = "LIVE"
    assert validate_fake_report_renderer_state(bad3)["valid"] is False

    bad4 = copy.deepcopy(s)
    bad4["stage"] = "EXECUTE"
    assert validate_fake_report_renderer_state(bad4)["valid"] is False

    bad5 = copy.deepcopy(s)
    bad5["human_approval_required"] = False
    assert validate_fake_report_renderer_state(bad5)["valid"] is False


# 28 -- validate flags missing required sections + empty preview.

def test_validate_flags_missing_sections_and_preview():
    import copy
    s = _state()
    bad = copy.deepcopy(s)
    bad["report_sections"] = {"executive_summary": "only one"}
    assert validate_fake_report_renderer_state(bad)["valid"] is False

    bad2 = copy.deepcopy(s)
    bad2["rendered_markdown_preview"] = ""
    v2 = validate_fake_report_renderer_state(bad2)
    assert v2["valid"] is False
    assert v2["rendered_markdown_preview_ok"] is False


# 29 -- validate never requires the state's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    s = copy.deepcopy(_state())
    s.pop("validation", None)
    v = validate_fake_report_renderer_state(s)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 30 -- a blocked state still validates (renderer safety, not activation).

def test_blocked_state_still_validates():
    s = _state(_blocked_contract())
    v = validate_fake_report_renderer_state(s)
    assert v["valid"] is True
    assert s["fake_report_renderer_active"] is False


# 31 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    import copy
    s = copy.deepcopy(_state())
    s.pop("report_sections", None)
    v = validate_fake_report_renderer_state(s)
    assert v["valid"] is False
    assert "report_sections" in v["missing_required_fields"]


# 32 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 33 -- module references no real Crypto-D1 dataset PATH. (Source legally NAMES
# the bare token "Crypto-D1" in the guard list, so we only assert the real
# dataset path forms absent.)

def test_no_real_artifact_path_in_source():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "Crypto-D1/" not in src
    assert "data/Crypto-D1" not in src
    assert "datasets/" not in src


# 34 -- prose verb audit over notes / guard / source ref / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    s = _state()

    texts.extend(str(x) for x in s["operator_notes"])
    texts.append(str(s["placeholder_only_guard"]))
    texts.append(str(s["source_renderer_contract_reference_placeholder"]))
    for value in s["report_sections"].values():
        texts.append(str(value))

    md = render_fake_report_markdown(s)
    for ln in md.splitlines():
        stripped = ln.lstrip()
        if stripped.startswith("#") or stripped.startswith("- `"):
            continue
        if stripped.startswith("- ") and "`" in stripped:
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


# 36 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_fake_report_renderer_in_memory.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_fake_report_renderer_in_memory.py"' in src
    )


# 37 -- Bundle 37 regression import still works.

def test_bundle37_regression_import_still_works():
    c = build_fake_report_renderer_contract({})
    assert c["executes"] is False
    assert c["read_only"] is True
    assert c["fake_report_renderer_contract_active"] is False


# 38 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0
