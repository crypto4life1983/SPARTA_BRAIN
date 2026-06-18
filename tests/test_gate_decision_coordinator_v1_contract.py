"""Tests for the SPARTA Gate Decision Coordinator v1 (thin, pure, research-only).

Proves: (1) clean+synced+no open gate -> recommend next candidate research;
(2) local-ahead -> recommend push approval; (3) uncommitted approved unit ->
recommend commit approval; (4) rejected-ledger mismatch -> recommend ledger-bump
approval; (5) closed C15 summarized as rejected/shipped/excluded; (6) human
approval gates preserved; (7) never recommends paper/live/broker/order action;
(8) supports morning-report-style output. Plus: allowlist, scope locks, capability
flags, validator anti-tamper, module purity. Deterministic."""
from __future__ import annotations

import ast

import sparta_commander.gate_decision_coordinator_v1_contract as gdc


# --- shared fixtures --------------------------------------------------------

_C15_CLOSED = {
    "C15": {"family": "slow_vol_targeted_time_series_momentum",
            "status": "REJECTED_KEPT_ON_RECORD", "active": False,
            "next_action": "NONE__C15_CLOSED", "shipped": True},
}
_LEDGER_OK = {"canonical_count": 20, "expected_count": 20, "reconciles": True}


def _clean_synced_state():
    return {"repo": {"clean": True, "ahead": 0, "behind": 0,
                     "uncommitted_changes": False},
            "candidates": dict(_C15_CLOSED), "ledger": dict(_LEDGER_OK)}


# --- 1. clean synced + no open gate -> AUTOMATION READINESS (post-C16) -------

def test_clean_synced_recommends_automation_readiness_after_c16():
    # the candidate-research lane is complete through C16, so the idle/default
    # recommendation must NOT drift back to "next candidate research".
    d = gdc.coordinate(_clean_synced_state())
    assert d["detected_gate"] == "candidate_lane_complete_automation_readiness"
    assert d["recommendation_kind"] == gdc.REC_AUTOMATION_READINESS
    assert d["next_safe_command"] == gdc.AUTOMATION_READINESS_TOKEN
    assert d["next_safe_command"] == "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"
    assert d["next_research_recommended"] is False   # NOT a new candidate
    assert d["automation_lane_continues"] is True
    assert gdc.validate_coordinator_decision(d)["valid"] is True


# --- 2. local ahead -> recommend push approval ------------------------------

def test_local_ahead_recommends_push_approval():
    state = _clean_synced_state()
    state["repo"] = {"clean": True, "ahead": 2, "behind": 0,
                     "uncommitted_changes": False}
    d = gdc.coordinate(state)
    assert d["detected_gate"] == "local_ahead_of_origin"
    assert d["recommendation_kind"] == gdc.REC_PUSH
    assert d["next_safe_command"] == "APPROVE_PUSH_LOCAL_STACK"
    assert d["requires_human_approval"] is True
    assert gdc.validate_coordinator_decision(d)["valid"] is True


# --- 3. uncommitted approved unit -> recommend commit approval --------------

def test_uncommitted_approved_recommends_commit_approval():
    state = _clean_synced_state()
    state["repo"] = {"clean": False, "ahead": 0, "behind": 0,
                     "uncommitted_changes": True,
                     "approved_unit_pending_commit": "candidate_16_family_spec"}
    d = gdc.coordinate(state)
    assert d["detected_gate"] == "uncommitted_approved_unit"
    assert d["recommendation_kind"] == gdc.REC_COMMIT
    assert d["next_safe_command"] == "APPROVE_COMMIT_CANDIDATE_16_FAMILY_SPEC"
    assert d["auto_commits"] is False
    assert gdc.validate_coordinator_decision(d)["valid"] is True


def test_uncommitted_unapproved_stops_for_approval():
    state = _clean_synced_state()
    state["repo"] = {"clean": False, "ahead": 0, "behind": 0,
                     "uncommitted_changes": True}
    d = gdc.coordinate(state)
    assert d["recommendation_kind"] == gdc.REC_STOP_AWAIT_APPROVAL
    assert "STOP_AWAIT_HUMAN_APPROVAL" in d["next_safe_command"]
    assert d["auto_commits"] is False


# --- 4. rejected-ledger mismatch -> recommend ledger bump -------------------

def test_ledger_mismatch_recommends_bump():
    state = _clean_synced_state()
    state["ledger"] = {"canonical_count": 19, "expected_count": 20,
                       "reconciles": False,
                       "missing_family": "slow_vol_targeted_time_series_momentum"}
    d = gdc.coordinate(state)
    assert d["detected_gate"] == "rejected_ledger_mismatch"
    assert d["recommendation_kind"] == gdc.REC_LEDGER_BUMP
    assert d["next_safe_command"].startswith("UPDATE_REJECTED_LEDGERS_ADD_")
    assert d["ledger_status"]["consistent"] is False
    assert gdc.validate_coordinator_decision(d)["valid"] is True


def test_open_gate_recommends_gate_decision():
    state = _clean_synced_state()
    state["candidates"] = {**_C15_CLOSED, "C16": {
        "family": "statistical_arbitrage_pairs", "active": True,
        "next_action": "HUMAN_DECISION_C16_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"}}
    d = gdc.coordinate(state)
    assert d["detected_gate"] == "open_candidate_gate"
    assert d["recommendation_kind"] == gdc.REC_GATE_DECISION
    assert d["next_safe_command"].startswith("HUMAN_DECISION_C16_")
    assert d["open_candidates"][0]["candidate"] == "C16"


# --- 5. closed C15 summarized as rejected / shipped / excluded --------------

def test_c15_summarized_closed_shipped_excluded():
    d = gdc.coordinate(_clean_synced_state())
    closed = {c["candidate"]: c for c in d["closed_excluded_candidates"]}
    assert "C15" in closed
    c15 = closed["C15"]
    assert c15["status"] == "rejected"
    assert c15["shipped"] is True
    assert c15["kept_on_record"] is True
    assert c15["excluded_from_reproposal"] is True
    assert c15["family"] == "slow_vol_targeted_time_series_momentum"


# --- 6. human approval gates preserved (in every branch) --------------------

def test_human_approval_preserved_in_all_branches():
    states = [
        _clean_synced_state(),
        {**_clean_synced_state(), "repo": {"ahead": 3, "uncommitted_changes": False}},
        {**_clean_synced_state(),
         "repo": {"uncommitted_changes": True,
                  "approved_unit_pending_commit": "u"}},
        {**_clean_synced_state(),
         "ledger": {"canonical_count": 19, "expected_count": 20,
                    "reconciles": False}},
    ]
    for st in states:
        d = gdc.coordinate(st)
        assert d["requires_human_approval"] is True
        assert d["executes_nothing"] is True
        assert d["auto_commits"] is False and d["auto_pushes"] is False
        assert d["auto_advances"] is False and d["auto_rejects"] is False
        assert d["is_recommendation_only"] is True


# --- 7. never recommends paper/live/broker/order ----------------------------

def test_never_recommends_trading_adjacent_action():
    # across all branches, the recommended command carries no forbidden substring
    states = [
        _clean_synced_state(),
        {**_clean_synced_state(), "repo": {"ahead": 1, "uncommitted_changes": False}},
        {**_clean_synced_state(),
         "repo": {"uncommitted_changes": True, "approved_unit_pending_commit": "u"}},
        {**_clean_synced_state(),
         "ledger": {"canonical_count": 1, "expected_count": 20,
                    "reconciles": False}},
        {**_clean_synced_state(),
         "candidates": {"C16": {"active": True, "family": "x",
                                "next_action": "HUMAN_DECISION_C16_X_OR_REJECT"}}},
    ]
    for st in states:
        d = gdc.coordinate(st)
        cmd = d["next_safe_command"].lower()
        for bad in ("paper", "live", "broker", "order", "exchange", "wallet",
                    "credential"):
            assert bad not in cmd, (bad, d["next_safe_command"])
        assert gdc.validate_coordinator_decision(d)["valid"] is True
    # a tampered decision recommending a forbidden action is rejected
    bad = gdc.coordinate(_clean_synced_state())
    bad["next_safe_command"] = "APPROVE_LIVE_BROKER_ORDER"
    assert gdc.validate_coordinator_decision(bad)["valid"] is False


def test_label_carries_no_readiness_or_trading_claim():
    label = gdc.get_gate_decision_coordinator_label()
    assert "RESEARCH ONLY" in label
    assert "EXECUTES NOTHING" in label.upper()
    assert "does NOT replace" in label or "Does NOT replace" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "READY FOR LIVE", "EDGE CONFIRMED"):
        assert banned not in label.upper(), banned


# --- 8. morning-report-style output -----------------------------------------

def test_supports_morning_report_output():
    d = gdc.coordinate(_clean_synced_state())
    summ = gdc.summarize_for_morning_report(d)
    assert summ["section"] == "gate_decision_coordinator"
    assert summ["decision_ready"] is True
    assert summ["paste_this"] == d["next_safe_command"]
    assert summ["requires_human_approval"] is True
    # idle now defers to automation readiness, not a new candidate
    assert summ["next_research_recommended"] is False
    assert summ["paste_this"] == "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"
    assert summ["automation_lane_continues"] is True
    assert summ["executes_nothing"] is True
    c15 = next(c for c in summ["closed_excluded"] if c["candidate"] == "C15")
    assert c15["excluded_from_reproposal"] is True and c15["shipped"] is True


# --- integration + allowlist + flags ----------------------------------------

def test_integrates_with_existing_pieces_does_not_replace():
    d = gdc.coordinate(_clean_synced_state())
    for piece in ("safe_research_autopilot_v1", "research_expansion_plan_v1",
                  "research_expansion_autopilot_integration_v1",
                  "sparta_autopilot_morning_report", "rejected_ledger_status"):
        assert piece in d["integrates_with"]
    assert d["does_not_replace_autopilot_or_orchestrator"] is True
    assert d["replaces_autopilot_or_orchestrator"] is False
    # canonical ledger is reused, not redefined (20 = C1-C15)
    assert gdc.EXPECTED_LEDGER_COUNT == 21


def test_capability_flags_all_false_and_tamper_rejected():
    d = gdc.coordinate(_clean_synced_state())
    for flag in gdc._CAPABILITY_FLAGS_FALSE:
        assert d[flag] is False, flag
        bad = {**d, flag: True}
        assert gdc.validate_coordinator_decision(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    d = gdc.coordinate(_clean_synced_state())
    for key, val in d["scope_locks"].items():
        assert val is True, key
    for must in ("no_auto_commit", "no_auto_push", "no_auto_advance",
                 "no_auto_reject", "no_replay", "no_optimization", "no_broker",
                 "no_paper_trading", "no_live_trading",
                 "no_replace_autopilot_or_orchestrator"):
        assert d["scope_locks"][must] is True, must


# --- module purity ----------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(gdc.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    for call in ast.walk(tree):
        if isinstance(call, ast.Call):
            name = (call.func.attr if isinstance(call.func, ast.Attribute)
                    else getattr(call.func, "id", ""))
            assert name not in ("open", "exec", "eval", "compile"), name
