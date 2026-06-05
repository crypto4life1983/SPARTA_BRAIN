"""Bundle 15 tests for the Strategy Factory Research Report Contract v1
(informational, read-only, report-contract-only).

Bundle 15's production module imports Bundles 11, 12, 13 and 14 via real
package imports, so these tests use normal package imports too. Running
under ``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.

Coverage (per the Bundle 15 spec):
- public API exists and is limited to the expected names,
- schema version / default label / status / verdict constants pinned,
- safety posture all False and keys identical to Bundle 14 posture,
- contract shape, source schemas, read-only / inert / human-gated,
- all authorization flags forced False (even when contract allowed),
- report_contract_allowed gating across ready / awaiting / invalid,
- malformed item -> no raise + invalid validation,
- allowed verdicts exact + default verdict + sections + evidence,
- evidence requirements authorize nothing,
- blocked capabilities include the required set,
- contract embeds the Bundle 14 task packet,
- validate_research_report_contract pass + each failure mode,
- batch shape + deterministic counts + zero authorization counts,
- batch approvals map is read-only input only,
- batch read-only / inert / human-gated / safety-all-false,
- returned dicts are fresh (mutation isolation),
- markdown renderers non-empty + write nothing,
- ast import-root audit + ast forbidden-surface audit,
- prose verb audit over evidence / sections / markdown prose,
- scoped dirty-tree guard, Bundle 11/12/13/14 regression imports.
"""

import ast
import copy
import pathlib
import re

from sparta_commander.strategy_factory_research_report_contract import (
    RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION,
    DEFAULT_RESEARCH_REPORT_CONTRACT_LABEL,
    RESEARCH_REPORT_CONTRACT_STATUS,
    RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE,
    REPORT_VERDICT_NEEDS_MORE_SPEC,
    REPORT_VERDICT_READY_FOR_PROTOCOL_DRAFT,
    REPORT_VERDICT_PARK_RESEARCH_ONLY,
    REPORT_VERDICT_REJECT_RESEARCH_ONLY,
    build_research_report_contract,
    build_research_report_contract_batch,
    validate_research_report_contract,
    render_research_report_contract_markdown,
    render_research_report_contract_batch_markdown,
)
import sparta_commander.strategy_factory_research_report_contract as RC
from sparta_commander.strategy_factory_research_task_packet import (
    RESEARCH_TASK_PACKET_SCHEMA_VERSION,
    RESEARCH_TASK_PACKET_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_queue_planner import (
    QUEUE_PLANNER_SCHEMA_VERSION,
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
    / "strategy_factory_research_report_contract.py"
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

_EXPECTED_VERDICTS = (
    "NEEDS_MORE_SPEC", "READY_FOR_PROTOCOL_DRAFT",
    "PARK_RESEARCH_ONLY", "REJECT_RESEARCH_ONLY",
)

_REQUIRED_SECTIONS = (
    "hypothesis_summary", "asset_lane_and_timeframe", "assumptions_to_verify",
    "risk_notes", "invalidation_conditions", "evidence_needed_later",
    "blocked_capabilities", "research_only_verdict", "next_gate",
)


def _good_item() -> dict:
    return build_research_queue_item(
        "idea-001",
        "Opening Range Mean Reversion",
        "Price tends to revert toward the opening range midpoint intraday.",
        asset_lane="MNQ",
        timeframe="5m",
    )


def _ready_contract() -> dict:
    return build_research_report_contract(
        _good_item(), human_research_approved=True)


def _expected_public() -> set[str]:
    return {
        "RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION",
        "DEFAULT_RESEARCH_REPORT_CONTRACT_LABEL",
        "RESEARCH_REPORT_CONTRACT_STATUS",
        "RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE",
        "REPORT_VERDICT_NEEDS_MORE_SPEC",
        "REPORT_VERDICT_READY_FOR_PROTOCOL_DRAFT",
        "REPORT_VERDICT_PARK_RESEARCH_ONLY",
        "REPORT_VERDICT_REJECT_RESEARCH_ONLY",
        "build_research_report_contract",
        "build_research_report_contract_batch",
        "validate_research_report_contract",
        "render_research_report_contract_markdown",
        "render_research_report_contract_batch_markdown",
    }


# 1 + 2 -- module imports and public API is exactly as expected.

def test_public_api_is_limited_to_expected_names():
    assert set(RC.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(RC, name)


# 3 -- schema version pinned.

def test_schema_version_is_pinned():
    assert (
        RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION
        == "strategy_factory_research_report_contract.v1"
    )


# 4 -- default label pinned.

def test_default_label_is_pinned():
    assert (
        DEFAULT_RESEARCH_REPORT_CONTRACT_LABEL
        == "Strategy Factory Research Report Contract"
    )


# 5 -- status pinned.

def test_status_is_pinned():
    assert RESEARCH_REPORT_CONTRACT_STATUS == "READ_ONLY_REPORT_CONTRACT"


# 6 -- verdict constants pinned.

def test_verdict_constants_are_pinned():
    assert REPORT_VERDICT_NEEDS_MORE_SPEC == "NEEDS_MORE_SPEC"
    assert REPORT_VERDICT_READY_FOR_PROTOCOL_DRAFT == "READY_FOR_PROTOCOL_DRAFT"
    assert REPORT_VERDICT_PARK_RESEARCH_ONLY == "PARK_RESEARCH_ONLY"
    assert REPORT_VERDICT_REJECT_RESEARCH_ONLY == "REJECT_RESEARCH_ONLY"


# 7 -- safety posture all False.

def test_safety_posture_all_false():
    assert all(
        v is False for v in RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE.values()
    )


# 8 -- safety posture keys match Bundle 14.

def test_safety_posture_keys_match_bundle14():
    assert (
        set(RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE.keys())
        == set(RESEARCH_TASK_PACKET_SAFETY_POSTURE.keys())
    )


# 9 -- contract required shape for a valid approved item.

def test_contract_required_shape():
    c = _ready_contract()
    required_keys = {
        "schema_version", "task_packet_schema_version",
        "planner_schema_version", "reader_schema_version",
        "research_queue_schema_version", "idea_id", "title", "stage", "mode",
        "status", "task_packet_status", "research_spec_allowed",
        "report_contract_allowed", "allowed_verdicts", "default_verdict",
        "approved_for_research", "execution_authorized",
        "paper_trading_authorized", "live_trading_authorized",
        "data_fetch_authorized", "backtest_authorized",
        "promotion_authorized", "human_approval_required", "read_only",
        "executes", "safety", "task_packet", "required_report_sections",
        "evidence_requirements", "blocked_capabilities", "validation",
        "next_gate",
    }
    assert required_keys <= set(c.keys())
    assert c["schema_version"] == RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION
    assert c["status"] == RESEARCH_REPORT_CONTRACT_STATUS
    assert c["idea_id"] == "idea-001"


# 10 -- contract schema versions match Bundles 11/12/13/14.

def test_contract_schema_versions_match():
    c = _ready_contract()
    assert c["task_packet_schema_version"] == RESEARCH_TASK_PACKET_SCHEMA_VERSION
    assert c["planner_schema_version"] == QUEUE_PLANNER_SCHEMA_VERSION
    assert c["reader_schema_version"] == QUEUE_READER_SCHEMA_VERSION
    assert c["research_queue_schema_version"] == RESEARCH_QUEUE_SCHEMA_VERSION


# 11 -- contract stage PLAN_ONLY.

def test_contract_stage_plan_only():
    assert build_research_report_contract(_good_item())["stage"] == "PLAN_ONLY"


# 12 -- contract mode RESEARCH_ONLY.

def test_contract_mode_research_only():
    assert build_research_report_contract(_good_item())["mode"] \
        == "RESEARCH_ONLY"


# 13 -- contract human_approval_required True.

def test_contract_human_approval_required():
    assert build_research_report_contract(_good_item())[
        "human_approval_required"] is True


# 14 -- contract read_only True.

def test_contract_read_only_true():
    assert build_research_report_contract(_good_item())["read_only"] is True


# 15 -- contract executes False.

def test_contract_executes_false():
    assert build_research_report_contract(_good_item())["executes"] is False


# 16 -- contract authorization flags all False.

def test_contract_authorization_flags_false():
    c = build_research_report_contract(_good_item())
    for flag in _AUTH_FLAGS:
        assert c[flag] is False
    assert all(v is False for v in c["safety"].values())


# 17 -- valid approved item allows report_contract_allowed=True.

def test_valid_approved_allows_contract():
    c = _ready_contract()
    assert c["report_contract_allowed"] is True
    assert c["next_gate"] == "research_report_draft"
    for flag in _AUTH_FLAGS:
        assert c[flag] is False, flag


# 18 -- valid unapproved item blocks contract, gate human_research_approval.

def test_valid_unapproved_blocks_contract():
    c = build_research_report_contract(_good_item())
    assert c["report_contract_allowed"] is False
    assert c["next_gate"] == "human_research_approval"


# 19 -- invalid item blocks contract, gate fix_research_queue_item.

def test_invalid_item_blocks_contract():
    c = build_research_report_contract(build_research_queue_item("", "", ""))
    assert c["report_contract_allowed"] is False
    assert c["next_gate"] == "fix_research_queue_item"


# 20 -- malformed item does not raise and validates invalid.

def test_malformed_item_no_raise():
    for bad in (None, 42, "nope", {}, {"idea_id": ""}, []):
        c = build_research_report_contract(bad)
        assert c["report_contract_allowed"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        # the contract dict itself is always well-formed and valid.
        assert c["validation"]["valid"] is True


# 21 -- allowed verdicts are exactly the four required constants.

def test_allowed_verdicts_exact():
    c = build_research_report_contract(_good_item())
    assert tuple(c["allowed_verdicts"]) == _EXPECTED_VERDICTS


# 22 -- default verdict is NEEDS_MORE_SPEC.

def test_default_verdict():
    assert build_research_report_contract(_good_item())["default_verdict"] \
        == "NEEDS_MORE_SPEC"


# 23 -- required report sections deterministic and non-empty.

def test_required_report_sections():
    c = build_research_report_contract(_good_item())
    sections = c["required_report_sections"]
    assert isinstance(sections, tuple) and len(sections) >= 1
    for s in _REQUIRED_SECTIONS:
        assert s in sections
    c2 = build_research_report_contract(_good_item())
    assert c["required_report_sections"] == c2["required_report_sections"]


# 24 -- evidence requirements deterministic and non-empty.

def test_evidence_requirements_present():
    c = build_research_report_contract(_good_item())
    ev = c["evidence_requirements"]
    assert isinstance(ev, tuple) and len(ev) >= 1
    assert all(isinstance(x, str) and x for x in ev)
    c2 = build_research_report_contract(_good_item())
    assert c["evidence_requirements"] == c2["evidence_requirements"]


# 25 -- evidence requirements authorize nothing (no bad verbs).

def test_evidence_requirements_authorize_nothing():
    c = build_research_report_contract(_good_item())
    for text in c["evidence_requirements"]:
        upper = text.upper()
        for verb in _BAD_VERBS:
            assert not re.search(rf"\b{verb}\b", upper), (
                f"evidence {text!r} contains forbidden verb {verb!r}"
            )


# 26 -- blocked capabilities include the required set.

def test_blocked_capabilities():
    c = build_research_report_contract(_good_item())
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 27 -- contract embeds Bundle 14 task packet.

def test_contract_embeds_task_packet():
    c = build_research_report_contract(_good_item())
    tp = c["task_packet"]
    assert tp["schema_version"] == RESEARCH_TASK_PACKET_SCHEMA_VERSION
    assert tp["read_only"] is True
    assert tp["executes"] is False


# 28 -- validate passes for a safe contract.

def test_validate_passes_for_safe_contract():
    c = _ready_contract()
    v = validate_research_report_contract(c)
    assert v["valid"] is True
    assert v["schema_version_ok"] is True
    assert v["allowed_verdicts_ok"] is True
    assert v["required_sections_present"] is True
    assert v["missing_required_fields"] == ()


# 29 -- validation detects wrong schema version.

def test_validate_detects_wrong_schema():
    c = copy.deepcopy(_ready_contract())
    c["schema_version"] = "nope.v0"
    v = validate_research_report_contract(c)
    assert v["schema_version_ok"] is False
    assert v["valid"] is False


# 30 -- validation detects non-research mode.

def test_validate_detects_non_research_mode():
    c = copy.deepcopy(_ready_contract())
    c["mode"] = "LIVE"
    v = validate_research_report_contract(c)
    assert v["research_only"] is False
    assert v["valid"] is False


# 31 -- validation detects non-plan stage.

def test_validate_detects_non_plan_stage():
    c = copy.deepcopy(_ready_contract())
    c["stage"] = "EXECUTE_ONLY"
    v = validate_research_report_contract(c)
    assert v["plan_only"] is False
    assert v["valid"] is False


# 32 -- validation detects read_only False.

def test_validate_detects_read_only_false():
    c = copy.deepcopy(_ready_contract())
    c["read_only"] = False
    v = validate_research_report_contract(c)
    assert v["read_only"] is False
    assert v["valid"] is False


# 33 -- validation detects executes True.

def test_validate_detects_executes_true():
    c = copy.deepcopy(_ready_contract())
    c["executes"] = True
    v = validate_research_report_contract(c)
    assert v["valid"] is False


# 34 -- validation detects any authorization flag True.

def test_validate_detects_authorization_flag_true():
    c = copy.deepcopy(_ready_contract())
    c["execution_authorized"] = True
    v = validate_research_report_contract(c)
    assert v["all_authorization_flags_false"] is False
    assert v["valid"] is False


# 35 -- validation detects any safety flag True.

def test_validate_detects_safety_flag_true():
    c = copy.deepcopy(_ready_contract())
    first_key = next(iter(c["safety"]))
    c["safety"][first_key] = True
    v = validate_research_report_contract(c)
    assert v["safety_all_false"] is False
    assert v["valid"] is False


# 36 -- validation detects wrong allowed verdicts.

def test_validate_detects_wrong_verdicts():
    c = copy.deepcopy(_ready_contract())
    c["allowed_verdicts"] = ("ONLY_ONE",)
    v = validate_research_report_contract(c)
    assert v["allowed_verdicts_ok"] is False
    assert v["valid"] is False


# 37 -- validation detects missing required sections.

def test_validate_detects_missing_sections():
    c = copy.deepcopy(_ready_contract())
    c["required_report_sections"] = ("hypothesis_summary",)
    v = validate_research_report_contract(c)
    assert v["required_sections_present"] is False
    assert v["valid"] is False


# 38 -- batch returns required shape.

def test_batch_required_shape():
    b = build_research_report_contract_batch((_good_item(),))
    required_keys = {
        "schema_version", "task_packet_schema_version",
        "planner_schema_version", "reader_schema_version",
        "research_queue_schema_version", "label", "status", "stage", "mode",
        "total_items", "report_contract_allowed_count",
        "blocked_contract_count", "valid_contract_count",
        "invalid_contract_count", "approved_for_research_count",
        "execution_authorized_count", "paper_trading_authorized_count",
        "live_trading_authorized_count", "data_fetch_authorized_count",
        "backtest_authorized_count", "promotion_authorized_count",
        "human_approval_required", "read_only", "executes", "safety",
        "task_packet_batch", "contracts", "validation", "next_gate",
    }
    assert required_keys <= set(b.keys())
    assert b["schema_version"] == RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION
    assert b["label"] == DEFAULT_RESEARCH_REPORT_CONTRACT_LABEL
    assert b["next_gate"] == "research_report_review"


# 39 -- batch schema versions match Bundles 11/12/13/14.

def test_batch_schema_versions_match():
    b = build_research_report_contract_batch(())
    assert b["task_packet_schema_version"] == RESEARCH_TASK_PACKET_SCHEMA_VERSION
    assert b["planner_schema_version"] == QUEUE_PLANNER_SCHEMA_VERSION
    assert b["reader_schema_version"] == QUEUE_READER_SCHEMA_VERSION
    assert b["research_queue_schema_version"] == RESEARCH_QUEUE_SCHEMA_VERSION


# 40 -- batch total_items deterministic.

def test_batch_total_items():
    b = build_research_report_contract_batch((_good_item(), _good_item()))
    assert b["total_items"] == 2


# 41 + 42 -- batch allowed/blocked + valid/invalid counts deterministic.

def test_batch_counts_deterministic():
    a = build_research_queue_item("idea-a", "A", "Thesis A is well-formed.")
    bb = build_research_queue_item("idea-b", "B", "Thesis B is well-formed.")
    bad = build_research_queue_item("", "", "")
    b = build_research_report_contract_batch(
        (a, bb, bad),
        human_research_approved_by_id={"idea-a": True},
    )
    assert b["total_items"] == 3
    assert b["report_contract_allowed_count"] == 1
    assert b["blocked_contract_count"] == 2
    # each contract dict is itself well-formed -> all valid.
    assert b["valid_contract_count"] == 3
    assert b["invalid_contract_count"] == 0
    b2 = build_research_report_contract_batch(
        (a, bb, bad),
        human_research_approved_by_id={"idea-a": True},
    )
    assert b == b2


# 43 -- batch authorization counts all 0 (even with approvals).

def test_batch_authorization_counts_zero():
    b = build_research_report_contract_batch(
        (_good_item(),), human_research_approved_by_id={"idea-001": True})
    for key in _AUTH_COUNTS:
        assert b[key] == 0


# 44 -- batch human_approval_required True.

def test_batch_human_approval_required():
    assert build_research_report_contract_batch(())[
        "human_approval_required"] is True


# 45 -- batch read_only True.

def test_batch_read_only_true():
    assert build_research_report_contract_batch(())["read_only"] is True


# 46 -- batch executes False.

def test_batch_executes_false():
    assert build_research_report_contract_batch(())["executes"] is False


# 47 -- batch safety all False.

def test_batch_safety_all_false():
    b = build_research_report_contract_batch((_good_item(),))
    assert all(v is False for v in b["safety"].values())


# 48 -- batch embeds Bundle 14 task packet batch.

def test_batch_embeds_task_packet_batch():
    b = build_research_report_contract_batch((_good_item(),))
    tpb = b["task_packet_batch"]
    assert tpb["schema_version"] == RESEARCH_TASK_PACKET_SCHEMA_VERSION
    assert tpb["read_only"] is True
    assert tpb["executes"] is False


# 49 -- fresh dicts; mutating one result must not taint the next.

def test_results_are_fresh_and_isolated():
    a = build_research_report_contract(_good_item())
    b = build_research_report_contract(_good_item())
    assert a == b
    assert a is not b
    a["safety"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = build_research_report_contract(_good_item())
    assert fresh["safety"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE["automation_enabled"] is False

    b1 = build_research_report_contract_batch((_good_item(),))
    b1["safety"]["network_enabled"] = True
    b1["contracts"][0]["read_only"] = False
    b2 = build_research_report_contract_batch((_good_item(),))
    assert b2["safety"]["network_enabled"] is False
    assert b2["contracts"][0]["read_only"] is True


# 49b -- approvals map is read-only input (caller dict untouched).

def test_batch_approvals_map_not_mutated():
    approvals = {"idea-001": True}
    snapshot = dict(approvals)
    build_research_report_contract_batch(
        (_good_item(),), human_research_approved_by_id=approvals)
    assert approvals == snapshot


# 50 -- markdown renderers return non-empty strings + expected sections.

def test_markdown_renderers_non_empty():
    c = _ready_contract()
    md_c = render_research_report_contract_markdown(c)
    assert isinstance(md_c, str) and md_c
    assert "# Strategy Factory Research Report Contract" in md_c
    assert "Stage: PLAN_ONLY" in md_c
    assert "Mode: RESEARCH_ONLY" in md_c
    assert "Human approval required: True" in md_c
    assert "Read only: True" in md_c
    assert "Executes: False" in md_c
    assert "## Required Report Sections" in md_c
    assert "## Evidence Requirements" in md_c
    assert "## Allowed Verdicts" in md_c
    assert "## Blocked Capabilities" in md_c
    assert "## Safety" in md_c
    assert "## Task Packet" in md_c
    assert "## Validation" in md_c
    assert "## Next Gate" in md_c

    b = build_research_report_contract_batch((_good_item(),))
    md_b = render_research_report_contract_batch_markdown(b)
    assert isinstance(md_b, str) and md_b
    assert "# Strategy Factory Research Report Contract Batch" in md_b
    assert "Stage: PLAN_ONLY" in md_b
    assert "Mode: RESEARCH_ONLY" in md_b
    assert "Execution authorized count: 0" in md_b
    assert "Backtest authorized count: 0" in md_b
    assert "Data fetch authorized count: 0" in md_b
    assert "Human approval required: True" in md_b
    assert "Read only: True" in md_b
    assert "Executes: False" in md_b
    assert "## Contracts" in md_b
    assert "## Safety" in md_b
    assert "## Task Packet Batch" in md_b
    assert "## Validation Summary" in md_b
    assert "## Next Gate" in md_b


# 51 -- markdown renderers write nothing (no file surface in module source).

def test_markdown_renderers_write_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 52 -- ast import-root audit: allowed roots only.

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


# 53 -- ast forbidden-surface audit: no file/network/subprocess/exec surface.

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


# 54 -- prose verb audit over evidence / sections descriptions / markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _ready_contract()
    batch = build_research_report_contract_batch((_good_item(),))

    texts.extend(str(e) for e in c["evidence_requirements"])

    for md in (
        render_research_report_contract_markdown(c),
        render_research_report_contract_batch_markdown(batch),
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


# 55 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 56 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["human_approval_required"] is True
    assert q["approved_for_research_count"] == 0


# 57 -- Bundle 12 regression import still works.

def test_bundle12_regression_import_still_works():
    from sparta_commander.strategy_factory_queue_reader import (
        build_queue_reader_summary,
    )
    s = build_queue_reader_summary((_good_item(),))
    assert s["executes"] is False
    assert s["valid_item_count"] == 1


# 58 -- Bundle 13 regression import still works.

def test_bundle13_regression_import_still_works():
    from sparta_commander.strategy_factory_queue_planner import (
        build_queue_plan_summary,
    )
    s = build_queue_plan_summary((_good_item(),))
    assert s["executes"] is False
    assert s["valid_item_count"] == 1


# 59 -- Bundle 14 regression import still works.

def test_bundle14_regression_import_still_works():
    from sparta_commander.strategy_factory_research_task_packet import (
        build_research_task_packet_batch,
    )
    b = build_research_task_packet_batch((_good_item(),))
    assert b["executes"] is False
    assert b["human_approval_required"] is True
    assert b["total_items"] == 1
