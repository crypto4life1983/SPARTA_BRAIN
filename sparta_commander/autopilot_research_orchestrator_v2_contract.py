"""SPARTA Autopilot Research Orchestrator v2 -- PURE, RESEARCH-ONLY POLICY CONTRACT.

A pure, stdlib-only DECLARATION of how the research autopilot may auto-continue the
safe, bounded build->test->commit->push steps of candidate-family research WITHOUT a
human re-typing every token -- while STILL stopping dead at every real human
decision gate. It is a policy/decision contract, NOT a runner: it executes nothing,
installs no scheduler, runs no overnight automation, touches no git, no network, no
data, and no paper/live/broker/order surface. It only takes a DECLARED step
descriptor (category + precheck snapshot + test result + scoped-diff snapshot) and
returns the single safe verdict: AUTO_CONTINUE (proceed with the named safe step) or
STOP_FOR_HUMAN (await an explicit human token), with the reason.

Discipline it encodes (the same discipline a human has been applying by hand):
  1. PRECHECK first, every step: clean working tree, HEAD == origin/master, no
     mutating shell pending, and ONLY the expected files changed.
  2. RUN TESTS before any commit.
  3. COMMIT only the expected files (never data artifacts; never unrelated clutter).
  4. PUSH only after tests pass AND the scoped diff is clean (expected-files-only).
  5. STOP and report on ANY of: dirty tree, unexpected files, failing tests, SHA
     drift (HEAD != origin/master at start), staged data artifacts, or an unclear /
     unrecognized gate.
  6. Produce ONE compact report per step.

What it may AUTO-CONTINUE (bounded, reversible, additive research steps only) and
what it must ALWAYS HUMAN-STOP for (real decisions / forbidden gates) are pinned as
the two closed allowlists/blocklists below. The blocklist always wins: if a step
touches anything in the human-stop set, the orchestrator stops even if the step also
looks like an auto-continue category. Every capability flag is pinned False with a
full scope_locks set.
"""
from __future__ import annotations

from typing import Any

ARO2_SCHEMA_VERSION = 2
ARO2_MODE = "RESEARCH_ONLY"
ARO2_LANE = "crypto_d1_auto_research"

# ---- the two verdicts (the COMPLETE allowlist) -----------------------------
VERDICT_AUTO_CONTINUE = "AUTO_CONTINUE"
VERDICT_STOP_FOR_HUMAN = "STOP_FOR_HUMAN"
ALL_VERDICTS = (VERDICT_AUTO_CONTINUE, VERDICT_STOP_FOR_HUMAN)

# ---- categories the orchestrator MAY auto-continue (closed allowlist) -------
# Each is a bounded, additive, reversible RESEARCH artifact build (a pure contract /
# spec / runner-without-execution / surface realignment / test) that does NOT make a
# strategy decision, fetch data, or touch a forbidden gate. "after_explicit_advance"
# / "after_explicit_reject" mean the HUMAN has already given that decision token in a
# prior step; the orchestrator only continues the safe BUILD that follows it.
AUTO_CONTINUE_CATEGORIES = (
    "proposal_surface_realignment",
    "spec_build_after_explicit_advance",
    "detector_dry_run_build_after_explicit_advance",
    "data_readiness_contract",
    "safe_runner_build_without_execution",
    "review_ledger_surface_realignment_after_explicit_reject",
    "morning_jarvis_panel_human_gate_surface_update",
    "research_only_contract_or_test",
)

# ---- categories the orchestrator MUST always stop for (closed blocklist) ----
# Real human decisions or forbidden / trading-adjacent gates. The blocklist ALWAYS
# wins over any auto-continue match.
HUMAN_STOP_CATEGORIES = (
    "start_new_candidate_c_number",
    "advance_vs_reject_decision",
    "network_fetch_execution",            # unless separately human-approved
    "labels_to_replay_advance",
    "replay_result_decision",
    "optimization_tuning_or_rescue_variant",
    "add_new_instrument_class",           # e.g. XAUUSD / gold
    "paper_live_broker_order_or_trading_code",
    "scheduler_change_beyond_research_only_reporting",
    "credentials_env_secrets_account_api_or_private_broker_endpoint",
)

# ---- the precheck gates that must ALL hold before any auto-continue ----------
REQUIRED_PRECHECKS = (
    "clean_working_tree",
    "head_equals_origin_master",
    "no_mutating_shell_pending",
    "expected_files_only",
)

# ---- the hard stop conditions (any one -> STOP_FOR_HUMAN) --------------------
STOP_CONDITIONS = (
    "dirty_tree",
    "unexpected_files",
    "failing_tests",
    "sha_drift",
    "data_artifact_staged",
    "unclear_or_unrecognized_gate",
)

# the ordered safe pipeline a single auto-continue step is allowed to perform
SAFE_STEP_PIPELINE = ("precheck", "build", "run_tests", "commit_expected_only",
                      "push_after_pass_and_clean_diff", "report")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "runs_git", "auto_commits", "auto_pushes", "writes_files",
    "runs_tests", "runs_shell", "runs_detector", "runs_labels", "runs_replay",
    "computes_pnl", "optimizes_parameters", "runs_robustness",
    "runs_portfolio_compute", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "installs_scheduler", "starts_scheduler",
    "runs_overnight_automation", "modifies_scheduler", "sends_notifications",
    "calls_api", "uses_network", "uses_credentials", "connects_broker",
    "connects_exchange", "uses_real_money", "places_orders", "contains_order_logic",
    "paper_trading", "live_trading", "deploys_capital", "starts_new_candidate",
    "makes_advance_or_reject_decision", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "weakens_human_gates", "advances_without_human_approval",
    "reproposes_rejected_family", "adds_new_instrument_class", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def _precheck_failures(precheck: dict) -> list:
    """Pure: which required prechecks are NOT satisfied (declared snapshot)."""
    precheck = precheck or {}
    out = []
    if precheck.get("clean_working_tree") is not True:
        out.append("dirty_tree")
    if precheck.get("head_equals_origin_master") is not True:
        out.append("sha_drift")
    if precheck.get("no_mutating_shell_pending") is not True:
        out.append("mutating_shell_pending")
    if precheck.get("expected_files_only") is not True:
        out.append("unexpected_files")
    return out


def decide_orchestrator_step(step: dict) -> dict[str, Any]:
    """PURE. Given a DECLARED step descriptor, return the single safe verdict
    (AUTO_CONTINUE or STOP_FOR_HUMAN) with the reason and the named safe action.
    Executes nothing; the human (or a separately-approved runner) still performs the
    actual build/test/commit/push -- this only says whether the next bounded step is
    allowed to proceed unattended or must wait for an explicit human token.

    Decision order (the blocklist always wins):
      1. category in HUMAN_STOP_CATEGORIES                 -> STOP
      2. any hard stop condition present                  -> STOP
      3. category NOT in AUTO_CONTINUE_CATEGORIES          -> STOP (unclear gate)
      4. any required precheck not satisfied              -> STOP
      5. tests not green (when a commit/push is intended)  -> STOP
      6. scoped diff not expected-files-only               -> STOP
      otherwise                                            -> AUTO_CONTINUE
    """
    step = step or {}
    category = step.get("category")
    precheck = step.get("precheck") or {}
    tests = step.get("tests") or {}
    diff = step.get("scoped_diff") or {}
    intends_commit = bool(step.get("intends_commit", True))
    intends_push = bool(step.get("intends_push", True))

    reasons: list = []
    stop = False

    # 1) blocklist always wins
    if category in HUMAN_STOP_CATEGORIES:
        stop = True
        reasons.append("human_decision_or_forbidden_gate__%s" % category)

    # 2) hard stop conditions (independent of category)
    if precheck.get("clean_working_tree") is not True:
        stop = True
        reasons.append("dirty_tree")
    if precheck.get("head_equals_origin_master") is not True:
        stop = True
        reasons.append("sha_drift")
    if precheck.get("no_mutating_shell_pending") is not True:
        stop = True
        reasons.append("mutating_shell_pending")
    if precheck.get("expected_files_only") is not True:
        stop = True
        reasons.append("unexpected_files")
    if diff.get("contains_data_artifact") is True:
        stop = True
        reasons.append("data_artifact_staged")
    if diff.get("only_expected_files") is False:
        stop = True
        reasons.append("scoped_diff_not_expected_files_only")

    # 3) unknown / unrecognized category is itself an unclear gate -> stop
    if category not in AUTO_CONTINUE_CATEGORIES and category not in (
            HUMAN_STOP_CATEGORIES):
        stop = True
        reasons.append("unclear_or_unrecognized_gate")

    # 5) tests must be green before a commit/push is permitted
    if (intends_commit or intends_push):
        if tests.get("ran") is not True:
            stop = True
            reasons.append("tests_not_run_before_commit")
        elif tests.get("passed") is not True:
            stop = True
            reasons.append("failing_tests")

    verdict = VERDICT_STOP_FOR_HUMAN if stop else VERDICT_AUTO_CONTINUE
    safe_action = ("await_explicit_human_token" if stop
                   else "proceed_build_test_commit_push_for__%s" % category)

    return {
        "schema_version": ARO2_SCHEMA_VERSION, "mode": ARO2_MODE, "lane": ARO2_LANE,
        "is_pure_policy_only": True,
        "category": category,
        "verdict": verdict,
        "auto_continue": verdict == VERDICT_AUTO_CONTINUE,
        "stop_for_human": verdict == VERDICT_STOP_FOR_HUMAN,
        "reasons": reasons,
        "safe_action": safe_action,
        "blocklist_wins": category in HUMAN_STOP_CATEGORIES,
        "required_pipeline": list(SAFE_STEP_PIPELINE),
        "precheck_failures": _precheck_failures(precheck),
        "requires_human_approval": verdict == VERDICT_STOP_FOR_HUMAN,
        "executes_nothing": True,
    }


def build_orchestrator_contract() -> dict[str, Any]:
    """PURE. The full declared orchestration policy: the two closed lists, the
    precheck gates, the stop conditions, the safe pipeline, and the locked-down
    capability posture. Builds / runs / commits / pushes NOTHING."""
    record: dict[str, Any] = {
        "schema_version": ARO2_SCHEMA_VERSION, "mode": ARO2_MODE, "lane": ARO2_LANE,
        "is_pure_policy_only": True,
        "is_runner": False,
        "installs_scheduler": False,
        "runs_overnight_automation": False,
        "label": (
            "Autopilot Research Orchestrator v2 (READ-ONLY POLICY, RESEARCH ONLY). "
            "Declares how the research autopilot may auto-continue bounded "
            "build->test->commit->push research steps (precheck -> build -> tests -> "
            "commit expected-only -> push after pass+clean-diff -> report) while "
            "ALWAYS stopping at real human decision gates and forbidden / "
            "trading-adjacent gates. Pure policy: executes nothing, installs no "
            "scheduler, runs no overnight automation, touches no git/network/data/"
            "paper/live. The blocklist always wins; every capability flag is False."),
        "verdicts": list(ALL_VERDICTS),
        "auto_continue_categories": list(AUTO_CONTINUE_CATEGORIES),
        "human_stop_categories": list(HUMAN_STOP_CATEGORIES),
        "required_prechecks": list(REQUIRED_PRECHECKS),
        "stop_conditions": list(STOP_CONDITIONS),
        "safe_step_pipeline": list(SAFE_STEP_PIPELINE),
        "blocklist_always_wins": True,
        "tests_required_before_commit": True,
        "push_requires_pass_and_clean_diff": True,
        "commit_expected_files_only": True,
        "never_stages_data_artifacts": True,
        "does_not_weaken_human_gates": True,
        "one_compact_report_per_step": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_git": True, "no_auto_commit": True,
        "no_auto_push": True, "no_write": True, "no_run_tests": True,
        "no_shell": True, "no_detector": True, "no_labels": True, "no_replay": True,
        "no_pnl": True, "no_optimization": True, "no_robustness": True,
        "no_portfolio_compute": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_data_mutation": True, "no_data_staging": True, "no_scheduler_install": True,
        "no_scheduler_start": True, "no_overnight_automation": True,
        "no_new_candidate": True, "no_advance_or_reject_decision": True,
        "no_network_fetch": True, "no_labels_to_replay_advance": True,
        "no_replay_decision": True, "no_optimization_or_rescue_variant": True,
        "no_new_instrument_class": True, "no_xauusd": True,
        "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
        "no_order_logic": True, "no_credentials": True, "no_account_api": True,
        "no_private_broker_endpoint": True, "no_gate_skip": True,
        "no_human_gate_weakening": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_orchestrator_contract(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the contract is research-only, pure
    policy (not a runner / scheduler / overnight automation), declares BOTH closed
    lists with the blocklist-always-wins rule, the full precheck/stop/pipeline
    discipline (tests before commit, expected-files-only, no data artifacts, no
    human-gate weakening), and pins every capability flag False with the scope locks
    set."""
    failures: list = []
    if record.get("mode") != ARO2_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_policy_only") is not True:
        failures.append("not_pure_policy_only")
    for k in ("is_runner", "installs_scheduler", "runs_overnight_automation"):
        if record.get(k) is not False:
            failures.append("must_be_false_%s" % k)

    # both closed lists present and disjoint
    ac = record.get("auto_continue_categories") or []
    hs = record.get("human_stop_categories") or []
    if set(ac) != set(AUTO_CONTINUE_CATEGORIES):
        failures.append("auto_continue_list_tampered")
    if set(hs) != set(HUMAN_STOP_CATEGORIES):
        failures.append("human_stop_list_tampered")
    if set(ac) & set(hs):
        failures.append("lists_not_disjoint")
    if record.get("blocklist_always_wins") is not True:
        failures.append("blocklist_must_always_win")

    # discipline flags
    for k in ("tests_required_before_commit", "push_requires_pass_and_clean_diff",
              "commit_expected_files_only", "never_stages_data_artifacts",
              "does_not_weaken_human_gates", "one_compact_report_per_step"):
        if record.get(k) is not True:
            failures.append("discipline_flag_off_%s" % k)

    # precheck / stop / pipeline declared in full
    if set(record.get("required_prechecks") or []) != set(REQUIRED_PRECHECKS):
        failures.append("required_prechecks_tampered")
    if set(record.get("stop_conditions") or []) != set(STOP_CONDITIONS):
        failures.append("stop_conditions_tampered")
    if list(record.get("safe_step_pipeline") or []) != list(SAFE_STEP_PIPELINE):
        failures.append("safe_step_pipeline_tampered")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_git", "no_auto_commit", "no_auto_push",
                "no_data_fetch", "no_data_staging", "no_scheduler_install",
                "no_overnight_automation", "no_new_candidate",
                "no_advance_or_reject_decision", "no_optimization_or_rescue_variant",
                "no_new_instrument_class", "no_xauusd", "no_paper_trading",
                "no_live_trading", "no_broker", "no_order_logic", "no_credentials",
                "no_human_gate_weakening", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
