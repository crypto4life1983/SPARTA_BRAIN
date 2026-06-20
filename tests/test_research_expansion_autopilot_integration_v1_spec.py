"""Tests for the Research Expansion -> Safe Autopilot Integration Spec v1.

Verifies: the spec is research-only, pure-integration-only, and executes nothing;
the REP gate sequence + every SARA hard stop are preserved; the batch feeds ONLY
the low-risk proposal gate and can NEVER override a SARA stop or reach a real-data
gate; anti-loop uses the canonical 19-family (C1-C14) ledger that reconciles with
SARA(18)+C14; the morning-report summary surfaces portfolio-fit fields; the two
wiring changes are DECLARED not applied; capability flags + scope locks; validator
anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.research_expansion_autopilot_integration_v1_spec as rei
import sparta_commander.safe_research_autopilot_v1_contract as sara


_R = rei.build_integration_spec(".", [])

# A clean, open chain state (no active candidate) -> SARA auto-advanceable.
_OPEN = {"active_candidate": None, "stage": sara.STAGE_NONE,
         "proposed_family": None}
_CLEAN = {"clean": True, "uncommitted_candidate_artifacts": False}
_DIRTY = {"clean": False, "uncommitted_candidate_artifacts": True}

_IDEAS = [
    {"family": "axis_durable", "distinct_edge_axis": True,
     "materially_different_from_all_rejected": True,
     "durability_proxy": 0.9, "timing_signal_proxy": 0.3,
     "portfolio_fit": {"expected_low_correlation": True,
                       "capital_efficiency_proxy": 0.8,
                       "regime_breadth_proxy": 0.8}},
    {"family": "axis_timing_only", "distinct_edge_axis": True,
     "materially_different_from_all_rejected": True,
     "durability_proxy": 0.1, "timing_signal_proxy": 0.95,
     "portfolio_fit": {"expected_low_correlation": False,
                       "capital_efficiency_proxy": 0.2,
                       "regime_breadth_proxy": 0.2}},
    {"family": "conviction_bar_follow_through",  # C14 -> must be excluded
     "distinct_edge_axis": True,
     "materially_different_from_all_rejected": True, "durability_proxy": 0.9},
]


# ---- core: research-only, pure, validates ----------------------------------

def test_spec_pure_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_planner_only"] is True
    assert _R["is_integration_spec_only"] is True
    assert rei.validate_integration_spec(_R)["valid"] is True


def test_gate_sequence_and_sara_hard_stops_preserved():
    assert _R["gate_sequence_preserved_unchanged"] is True
    assert _R["sara_hard_stops_preserved"] is True
    assert _R["batch_feeds_only"] == sara.ACTION_BUILD_PROPOSAL
    bad = dict(_R)
    bad["batch_feeds_only"] = "RUN_REAL_CANDLE_LABELS"
    assert rei.validate_integration_spec(bad)["valid"] is False


# ---- canonical 20-family ledger reconciles with SARA + C14 + C15 -----------

def test_canonical_ledger_is_25_and_reconciles():
    assert _R["canonical_rejected_families_count"] == 26
    assert _R["canonical_includes_c14"] is True
    assert _R["canonical_includes_c15"] is True
    assert _R["canonical_includes_c16"] is True
    recon = _R["rejected_ledger_reconciliation"]
    # SARA's ledger bumps (C14..C21) have been applied; canonical == SARA, no
    # duplicates. Reconciliation holds by set equality.
    assert recon["sara_count"] == 26
    assert recon["canonical_count"] == 26
    assert recon["c14_in_sara"] is True
    assert recon["c15_in_sara"] is True
    assert recon["c16_in_sara"] is True
    assert recon["c16_in_canonical"] is True
    assert recon["missing_from_sara"] == []
    assert recon["extra_in_sara"] == []
    assert recon["reconciles"] is True
    bad = dict(_R)
    bad["canonical_rejected_families_count"] = 20
    assert rei.validate_integration_spec(bad)["valid"] is False


# ---- wiring changes: SARA ledger APPLIED, morning-report still PENDING ------

def test_sara_ledger_applied_morning_report_still_pending():
    assert _R["all_proposed_changes_applied"] is False
    assert _R["sara_ledger_change_applied"] is True
    assert _R["morning_report_change_applied"] is False
    pc = _R["proposed_changes"]
    # morning-report §14 wiring still pending (not applied)
    assert pc["morning_report"]["applied"] is False
    assert pc["morning_report"]["additive_only"] is True
    # SARA ledger bump applied via its token
    assert pc["sara_ledger"]["applied"] is True
    assert pc["sara_ledger"]["applied_via_token"] == (
        "UPDATE_SARA_REJECTED_LEDGER_ADD_C14")
    # tampering: marking all changes applied (i.e. morning-report applied) is bad
    bad = dict(_R)
    bad["all_proposed_changes_applied"] = True
    assert rei.validate_integration_spec(bad)["valid"] is False
    # tampering: SARA ledger change must remain applied (cannot be cleared)
    bad2 = dict(_R)
    bad2["proposed_changes"] = {
        "morning_report": dict(_R["proposed_changes"]["morning_report"]),
        "sara_ledger": {**_R["proposed_changes"]["sara_ledger"], "applied": False},
    }
    assert rei.validate_integration_spec(bad2)["valid"] is False


# ---- the combined planner: actionable only at the open proposal gate -------

def test_plan_actionable_at_open_clean_feeds_proposal_only():
    plan = rei.plan_overnight_expansion(_OPEN, _CLEAN, _IDEAS, build_top_k=1)
    assert plan["integration_actionable"] is True
    assert plan["unified_next_safe_action"] == sara.ACTION_BUILD_PROPOSAL
    assert plan["recommended_token"] == rei.ALLOWED_BATCH_RECOMMENDED_TOKEN
    # durable idea ranks first; C14 excluded by anti-loop.
    assert plan["selected_families"] == ["axis_durable"]
    assert "conviction_bar_follow_through" not in plan["selected_families"]
    assert plan["batch"]["buildable_count"] == 2
    assert plan["executes_nothing"] is True
    assert rei.validate_integration_spec(
        {**_R, **{}}  # spec record still valid alongside a plan
    )["valid"] is True


def test_plan_defers_to_sara_when_dirty_repo():
    plan = rei.plan_overnight_expansion(_OPEN, _DIRTY, _IDEAS, build_top_k=1)
    assert plan["integration_actionable"] is False
    assert plan["unified_next_safe_action"] == sara.ACTION_STOP_DIRTY_REPO
    assert plan["selected_families"] == []
    assert plan["batch_can_override_sara_stop"] is False


def test_plan_defers_to_sara_hard_stop_before_labels():
    detector_ready = {"active_candidate": "C15", "proposed_family": "new_axis",
                      "stage": sara.STAGE_DETECTOR_DRY_RUN_READY}
    plan = rei.plan_overnight_expansion(detector_ready, _CLEAN, _IDEAS)
    assert plan["integration_actionable"] is False
    assert plan["unified_next_safe_action"] == sara.ACTION_STOP_BEFORE_LABELS
    assert plan["sara_decision"]["is_hard_stop"] is True
    assert plan["selected_families"] == []


def test_plan_never_reaches_forbidden_gate():
    for stage in ("real_candle_labels", "replay", "paper_trading",
                  "live_trading", "broker"):
        plan = rei.plan_overnight_expansion(
            {"active_candidate": "Cx", "stage": stage, "proposed_family": "z"},
            _CLEAN, _IDEAS)
        assert plan["integration_actionable"] is False
        assert plan["selected_families"] == []
        assert plan["crosses_into_forbidden_gate"] is False
        assert plan["unified_next_safe_action"] in sara.STOP_ACTIONS


def test_anti_loop_excludes_c14_even_if_top_scored():
    only_c14 = [{"family": "conviction_bar_follow_through",
                 "distinct_edge_axis": True,
                 "materially_different_from_all_rejected": True,
                 "durability_proxy": 0.99, "timing_signal_proxy": 0.99}]
    plan = rei.plan_overnight_expansion(_OPEN, _CLEAN, only_c14, build_top_k=1)
    assert plan["batch"]["buildable_count"] == 0
    assert plan["selected_families"] == []


# ---- morning-report summary surfaces portfolio-fit -------------------------

def test_morning_report_summary_has_portfolio_fit_fields():
    plan = rei.plan_overnight_expansion(_OPEN, _CLEAN, _IDEAS, build_top_k=1)
    summ = rei.summarize_for_morning_report(plan)
    assert summ["section"] == "overnight_research_expansion"
    assert summ["planner_only"] is True
    assert summ["generated_count"] == 3
    assert summ["buildable_count"] == 2
    assert summ["selected_to_build"] == ["axis_durable"]
    assert summ["excluded_rejected_families_count"] == 26
    top = summ["ranked"][0]
    for field in ("family", "priority_score", "durability_proxy",
                  "timing_signal_proxy", "portfolio_fit"):
        assert field in top, field
    for dim in ("trade_time_overlap", "regime_profile", "symbol_exposure",
                "holding_time_bars"):
        assert dim in summ["portfolio_fit_tracked_dimensions"]
    assert summ["executes_nothing"] is True


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rei._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = dict(_R)
        bad[flag] = True
        assert rei.validate_integration_spec(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_labels", "no_replay", "no_data_fetch",
                 "no_commit", "no_push", "no_paper_trading", "no_live_trading",
                 "no_broker", "no_sara_stop_override",
                 "no_mutation_of_sara_or_morning_report_or_rep"):
        assert _R["scope_locks"][must] is True, must


def test_label_no_readiness_and_next_action():
    label = rei.get_integration_spec_label()
    assert "RESEARCH ONLY" in label
    assert "BUILDS NOTHING" in label
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE",
                   "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned not in label.upper(), banned
    nra = _R["next_required_action"]
    assert nra == "HUMAN_DECISION_ADOPT_INTEGRATION_SPEC_OR_AMEND"
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rei.__file__, encoding="utf-8").read()
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
