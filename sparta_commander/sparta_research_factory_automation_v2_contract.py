"""SPARTA Research Factory Automation V2 / Morning Decision Packet Bundle
-- PURE, READ-ONLY, RESEARCH ONLY.

A single cohesive read-only automation layer that lets the research factory advance the
safe (research-only) work while the operator sleeps, then surface ONE clear morning
decision packet: candidate status, last verdict, blockers, evidence, the next recommended
human gate, and the EXACT copy-paste approval token -- WITHOUT ever crossing a human gate,
auto-committing, auto-pushing, fetching data, connecting to Signum/MCP/Hyperliquid, or
allowing paper/live/broker/order/scheduler action. It RECOMMENDS; the human still approves
every commit, push, advance, reject, and dataset staging.

This module executes NOTHING and performs NO git/network I/O: the live candidate-chain
state is read from the already-committed pure contracts, and the repo/git facts are
INJECTED as a declared `repo_state` argument (the caller gathers them; this module never
shells out). Every dangerous capability is pinned False with a full scope_locks set.

Seven cohesive capabilities:
  1. next-safe-task selector       (select_next_safe_task)
  2. morning decision packet       (build_morning_decision_packet)
  3. gate recommendation engine    (recommend_gate, classify_replay_outcome)
  4. dirty-git / clutter blocker    (git_safety_gate)
  5. blast-radius test selector     (blast_radius_tests)
  6. approval-token generator       (approval_tokens)
  7. automation safety locks        (automation_safety_locks)
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane
import sparta_commander.research_expansion_plan_v1_contract as _rep
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_proposal_contract as _c22prop  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_candidate_spec_contract as _c22spec  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_detector_spec_dry_run_contract as _c22det  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_data_readiness_contract as _c22data  # noqa: E501

V2_SCHEMA_VERSION = 1
V2_MODE = "RESEARCH_ONLY"
V2_LANE = "crypto_d1_auto_research"
BUNDLE_NAME = "SPARTA_RESEARCH_FACTORY_AUTOMATION_V2_MORNING_DECISION_PACKET"

# --- recommendation kinds (the COMPLETE allowlist; all are RECOMMENDATIONS) ---
REC_HOLD = "RECOMMEND_HOLD"
REC_ADVANCE = "RECOMMEND_ADVANCE_HUMAN_DECISION"
REC_REJECT = "RECOMMEND_REJECT"
REC_COMMIT = "RECOMMEND_COMMIT_APPROVAL"
REC_PUSH = "RECOMMEND_PUSH_APPROVAL"
REC_STAGE_DATA = "RECOMMEND_DATASET_STAGING"
REC_RESOLVE_REPO = "RECOMMEND_RESOLVE_REPO_BEFORE_AUTOMATION"
REC_AWAIT_HUMAN = "RECOMMEND_AWAIT_HUMAN_DECISION"
ALL_RECOMMENDATION_KINDS = (
    REC_HOLD, REC_ADVANCE, REC_REJECT, REC_COMMIT, REC_PUSH, REC_STAGE_DATA,
    REC_RESOLVE_REPO, REC_AWAIT_HUMAN,
)

# substrings a recommended command/token may NEVER contain (no live execution).
FORBIDDEN_TOKEN_SUBSTRINGS = (
    "paper_trade", "live_trade", "place_order", "send_order", "broker_connect",
    "api_key", "credential", "signum_connect", "use_mcp", "hyperliquid",
    "auto_commit", "auto_push", "auto_fetch", "auto_promote", "deploy_capital",
    "git add .", "git add -a",
)

# --- replay outcome classes (encodes the C20/C21 lesson) --------------------
OUTCOME_TRUE_PASS = "TRUE_PASS"
OUTCOME_PROFITABLE_BUT_FAILED_BENCHMARK = "PROFITABLE_BUT_FAILED_BENCHMARK"
OUTCOME_FAIL = "FAIL"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "performs_git_io", "performs_network_io", "auto_commits",
    "auto_pushes", "auto_fetches_data", "auto_promotes_candidate", "auto_advances_gate",
    "auto_rejects", "skips_any_human_gate", "broad_git_add", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "modifies_scheduler",
    "installs_scheduler", "triggers_scheduler", "sends_notifications", "sends_email",
    "calls_api", "uses_network", "uses_credentials", "uses_api_keys", "connects_signum",
    "uses_mcp", "accesses_hyperliquid", "connects_broker", "connects_exchange",
    "sends_trades", "edits_bots", "creates_claude_routines", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "optimizes_without_gate", "tunes_without_gate",
    "rescues_without_gate", "reopens_closed_candidate", "modifies_strategy_rules",
    "unlocks_downstream_gate", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


# ===========================================================================
# 7. AUTOMATION SAFETY LOCKS
# ===========================================================================

def automation_safety_locks() -> dict[str, Any]:
    """The hard locks that hold for EVERY automation action. Pure."""
    return {
        "mode": V2_MODE, "read_only": True, "executes": False,
        "recommends_only_never_executes": True,
        "no_automatic_commit": True, "no_automatic_push": True,
        "no_automatic_data_fetch": True, "no_automatic_candidate_promotion": True,
        "no_automatic_gate_advance": True, "no_broad_git_add": True,
        "no_optimization_tuning_rescue_without_gate": True,
        "never_skips_human_gates": True,
        # dangerous channels -- all locked
        "live_trading_locked": True, "paper_trading_locked": True,
        "broker_locked": True, "order_logic_locked": True,
        "api_keys_locked": True, "credentials_locked": True,
        "signum_locked": True, "hyperliquid_locked": True, "mcp_locked": True,
        "claude_routines_locked": True, "scheduler_locked": True,
        "bot_edits_locked": True, "trades_locked": True,
    }


# ===========================================================================
# 4. DIRTY-GIT AND CLUTTER BLOCKER
# ===========================================================================

def git_safety_gate(repo_state: dict) -> dict[str, Any]:
    """Refuse automation if the tracked tree is dirty, files are staged, or the local
    branch is behind origin. A local commit AHEAD (clean tree) is allowed -> it routes to
    a PUSH recommendation. Untracked clutter only WARNS (allowed when ignored by path /
    explicitly unrelated). Pure."""
    rs = repo_state or {}
    clean = bool(rs.get("clean"))
    staged = int(rs.get("staged_count", 0) or 0)
    ahead = int(rs.get("ahead", 0) or 0)
    behind = int(rs.get("behind", 0) or 0)
    clutter = bool(rs.get("untracked_clutter_present"))
    clutter_ignored = bool(rs.get("untracked_clutter_ignored_by_path", True))

    blockers: list = []
    if not clean:
        blockers.append("tracked_tree_dirty")
    if staged > 0:
        blockers.append("staged_files_present")
    if behind > 0:
        blockers.append("local_branch_behind_origin")

    warnings: list = []
    if clutter:
        warnings.append("untracked_clutter_present_allowed_if_ignored_by_path"
                        if clutter_ignored else "untracked_clutter_present_unexplained")
    notes: list = []
    if ahead > 0 and not blockers:
        notes.append("local_commit_ahead_needs_human_push_approval")

    return {
        "safe_to_automate": not blockers,
        "blockers": blockers, "warnings": warnings, "notes": notes,
        "ahead": ahead, "behind": behind, "clean": clean, "staged_count": staged,
        "clutter_blocks_automation": False,   # clutter never blocks, only warns
    }


# ===========================================================================
# 5. BLAST-RADIUS TEST SELECTOR
# ===========================================================================

# curated adjacency: changing a core surface should also re-run these.
_ADJACENCY = {
    "crypto_d1_candidate_research_lane_status_v1_contract": (
        "test_crypto_d1_candidate_research_lane_status_v1_contract",
        "test_automation_readiness_bundle_integration_v1_contract",
        "test_gate_decision_coordinator_v1_contract",
        "test_sparta_full_research_factory_autopilot_v1_contract",
        "test_sparta_pipeline_audit_v1_contract"),
    "research_expansion_plan_v1_contract": (
        "test_research_expansion_plan_v1_contract",
        "test_research_expansion_autopilot_integration_v1_spec",
        "test_safe_research_autopilot_v1_contract"),
}


def _test_stem_for(module_stem: str) -> str:
    return "test_%s" % module_stem


def blast_radius_tests(changed_paths: list) -> dict[str, Any]:
    """Given changed module/file paths, recommend the targeted test files + adjacent
    regression. HONEST about the environment: the full tests/ tree is NOT runnable as a
    single gate here (it hangs at import on unrelated heavy suites), so the bundle
    recommends the targeted blast-radius set instead. Pure."""
    targeted: list = []
    adjacent: set = set()
    for p in (changed_paths or []):
        stem = str(p).split("/")[-1]
        if stem.endswith(".py"):
            stem = stem[:-3]
        if stem.startswith("test_"):
            targeted.append("tests/%s.py" % stem)
            continue
        targeted.append("tests/%s.py" % _test_stem_for(stem))
        for adj in _ADJACENCY.get(stem, ()):  # curated adjacency
            adjacent.add("tests/%s.py" % adj)
    # de-dup targeted, drop adjacents already in targeted
    targeted_u = sorted(dict.fromkeys(targeted))
    adjacent_u = sorted(a for a in adjacent if a not in targeted_u)
    return {
        "targeted_tests": targeted_u,
        "adjacent_regression_tests": adjacent_u,
        "full_suite_runnable_as_gate": False,
        "full_suite_unavailable_reason": (
            "the full tests/ tree hangs at import/collection in this environment on "
            "unrelated heavy suites (media / trading / telegram / hydra); use the "
            "targeted blast-radius set + curated adjacency as the gate, and run a "
            "collect-only sweep to confirm no import breakage"),
        "recommended_invocation": (
            "python -m pytest <targeted+adjacent> -q -p no:cacheprovider "
            "--rootdir=tests"),
    }


# ===========================================================================
# 3. GATE RECOMMENDATION ENGINE
# ===========================================================================

def classify_replay_outcome(net_return: float, beats_null: bool,
                            beats_buy_and_hold: bool, oos_holds: bool,
                            all_decisive_gates_pass: bool) -> str:
    """Encodes the C20/C21 lesson: a strategy is a TRUE pass ONLY when it beats the
    benchmark(s) on a risk-adjusted basis AND holds forward-OOS AND all decisive gates
    pass. A NET-POSITIVE result that fails the benchmark or OOS is PROFITABLE_BUT_FAILED_
    BENCHMARK -> still a REJECT, never a pass. Pure."""
    if all_decisive_gates_pass and beats_null and beats_buy_and_hold and oos_holds:
        return OUTCOME_TRUE_PASS
    if net_return > 0 and not (beats_null and beats_buy_and_hold and oos_holds):
        return OUTCOME_PROFITABLE_BUT_FAILED_BENCHMARK
    return OUTCOME_FAIL


def recommend_gate(state: dict) -> dict[str, Any]:
    """PURE. From the assembled (repo + candidate-chain) state, recommend ONE safe gate
    action -- always a HUMAN decision token, never auto-executed. Priority:
      0) repo unsafe (dirty/staged/behind) -> RESOLVE_REPO
      1) a local commit ahead (clean)       -> PUSH approval
      2) candidate blocked DATA_NOT_READY    -> DATASET STAGING (never fake labels)
      3) a frozen artifact awaiting decision -> ADVANCE/REJECT human decision
      4) a replay outcome present            -> classify (true-pass vs
                                                 profitable-but-failed-benchmark -> REJECT)
      5) otherwise                            -> HOLD / await human
    """
    git = state.get("git_safety") or {}
    cand = state.get("candidate") or {}

    rec_kind = None
    reason = None
    token = None

    if not git.get("safe_to_automate", False):
        rec_kind = REC_RESOLVE_REPO
        reason = ("repo is not safe to automate (%s); resolve before any automated "
                  "research work" % ", ".join(git.get("blockers") or []))
    elif int(git.get("ahead", 0) or 0) > 0:
        rec_kind = REC_PUSH
        reason = ("a local commit is ahead of origin on a clean tree; recommend the "
                  "human paste the push-approval token (no auto-push)")
        token = state.get("pending_push_token")
    elif cand.get("blocked_reason") == "DATA_NOT_READY":
        rec_kind = REC_STAGE_DATA
        reason = ("the active candidate is blocked at DATA_NOT_READY (the required "
                  "dataset is not staged); recommend DATASET STAGING -- do NOT proceed "
                  "to labels and do NOT fabricate data")
        token = cand.get("next_required_action")
    elif cand.get("replay_outcome"):
        out = cand["replay_outcome"]
        if out == OUTCOME_TRUE_PASS:
            rec_kind = REC_ADVANCE
            reason = ("fee-honest replay is a TRUE pass (beats benchmark risk-adjusted + "
                      "holds OOS); recommend the human advance decision (paper-trading "
                      "remains a separate human gate)")
        else:
            rec_kind = REC_REJECT
            reason = ("fee-honest replay is %s -- net-positive alone is NOT a pass; "
                      "recommend REJECT" % out)
        token = cand.get("next_required_action")
    elif cand.get("frozen_awaiting_decision"):
        rec_kind = REC_ADVANCE
        reason = ("a frozen artifact is awaiting the human advance-or-reject decision "
                  "at the %s gate" % cand.get("current_stage"))
        token = cand.get("next_required_action")
    else:
        rec_kind = REC_HOLD
        reason = "no safe automated action available; hold and await human direction"

    return {"recommendation_kind": rec_kind, "reason": reason,
            "recommended_token": token, "is_recommendation_only": True,
            "auto_executes": False, "requires_human_approval": True}


# ===========================================================================
# read the live candidate-chain state (pure; from committed contracts).
# ===========================================================================

def _c22_chain_state() -> dict[str, Any]:
    """Assemble C22's furthest-advanced chain state from the committed pure contracts.
    The data-readiness gate (DATA_NOT_READY) is the current authoritative C22 stage."""
    prop = _c22prop.build_c22_proposal()
    spec = _c22spec.build_c22_spec()
    det = _c22det.build_c22_detector_dry_run()
    data = _c22data.build_c22_data_readiness()
    prop_v = _c22prop.validate_c22_proposal(prop)["valid"]
    spec_v = _c22spec.validate_c22_spec(spec)["valid"]
    det_v = _c22det.validate_c22_detector_dry_run(det)["valid"]
    data_v = _c22data.validate_c22_data_readiness(data)["valid"]
    all_valid = prop_v and spec_v and det_v and data_v
    blocked = data.get("readiness_verdict") == "DATA_NOT_READY"
    return {
        "candidate_id": "C22",
        "candidate_token": _c22prop.CANDIDATE_TOKEN,
        "current_stage": "real_candle_labels_data_readiness",
        "stage_verdicts": {
            "family_proposal": prop.get("verdict"),
            "candidate_spec": spec.get("verdict"),
            "detector_spec_dry_run": det.get("verdict"),
            "data_readiness": data.get("readiness_verdict")},
        "last_verdict": data.get("readiness_verdict"),
        "chain_artifacts_valid": all_valid,
        "evidence_test_files": [
            "tests/test_external_signum_trend_radar_gc_long_short_v1_proposal_contract.py",
            "tests/test_external_signum_trend_radar_gc_long_short_v1_candidate_spec_contract.py",
            "tests/test_external_signum_trend_radar_gc_long_short_v1_detector_spec_dry_run_contract.py",
            "tests/test_external_signum_trend_radar_gc_long_short_v1_data_readiness_contract.py"],
        "blocked_reason": "DATA_NOT_READY" if blocked else None,
        "frozen_awaiting_decision": not blocked,
        "replay_outcome": None,   # C22 has no replay (blocked before labels)
        "next_required_action": data.get("next_required_action"),
        "spec_rules_preserved": data.get("preserves_frozen_c22_spec_rules"),
        "labels_produced": data.get("labels_produced"),
    }


# ===========================================================================
# 1. NEXT-SAFE-TASK SELECTOR
# ===========================================================================

def select_next_safe_task(repo_state: dict) -> dict[str, Any]:
    """PURE. Pick the single next SAFE research-only task, never crossing a human gate.
    Detects active/no-active candidate and blocked states (e.g. C22 DATA_NOT_READY)."""
    git = git_safety_gate(repo_state)
    lane = _lane.get_lane_status()
    cand = _c22_chain_state()

    if not git["safe_to_automate"]:
        task = "RESOLVE_REPO_BEFORE_AUTOMATION"
        detail = "repo not safe: %s" % ", ".join(git["blockers"])
    elif git["ahead"] > 0:
        task = "AWAIT_HUMAN_PUSH_APPROVAL_FOR_LOCAL_COMMIT"
        detail = "a local commit is ahead of origin; push needs human approval"
    elif cand["blocked_reason"] == "DATA_NOT_READY":
        task = "STAGE_TREND_RADAR_GC_DETECTOR_DATASET_THEN_REAUTHORISE_LABELS"
        detail = ("C22 is blocked at DATA_NOT_READY; the safe next task is to stage the "
                  "frozen Trend-Radar gc-detector dataset (operator) -- NOT to proceed "
                  "to labels and NOT to fabricate data")
    elif cand["frozen_awaiting_decision"]:
        task = "AWAIT_HUMAN_DECISION_AT_%s" % cand["current_stage"].upper()
        detail = "a frozen artifact awaits the human advance-or-reject decision"
    else:
        task = "AWAIT_HUMAN_DIRECTION"
        detail = "no safe automated task available"

    return {
        "next_safe_task": task, "detail": detail,
        "active_candidate_on_lane": lane.get("active_candidate"),
        "no_active_candidate_on_lane": lane.get("active_candidate") is None,
        "c22_blocked_data_not_ready": cand["blocked_reason"] == "DATA_NOT_READY",
        "never_skips_human_gate": True,
        "auto_executes": False,
        "requires_human_approval": True,
        "is_research_only": True,
    }


# ===========================================================================
# 6. APPROVAL-TOKEN GENERATOR
# ===========================================================================

def approval_tokens(unit_name: str | None = None, files: list | None = None,
                    commit_hash: str | None = None, candidate: str | None = None,
                    stage: str | None = None, advance_token: str | None = None,
                    data_staging_token: str | None = None) -> dict[str, Any]:
    """PURE. Produce the exact copy-paste tokens (with hard restrictions + expected git
    state) for each safe human action. Generates text ONLY -- applies nothing."""
    u = (unit_name or "UNIT").strip().upper().replace(" ", "_")
    c = (candidate or "CANDIDATE").strip().upper()
    base_locks = [
        "no live/paper trading", "no broker/order/API/credentials",
        "no Signum/MCP/Hyperliquid", "no Claude routines / bot edits / trades",
        "no data fetch", "no scheduler install/trigger", "no broad git add",
        "no optimization/tuning/rescue unless this exact gate authorizes it"]
    return {
        "commit": {
            "token": "APPROVE_COMMIT_%s_ONLY" % u,
            "hard_restrictions": base_locks + ["commit ONLY the approved files",
                                               "explicit per-path git add only"],
            "approved_files": list(files or []),
            "expected_git_state_before": {
                "head_equals_origin": True, "ahead": 0, "behind": 0,
                "tracked_tree_clean": True, "nothing_staged": True},
            "stop_after": "commit; STOP before push"},
        "push": {
            "token": "APPROVE_PUSH_%s_ONLY" % u,
            "hard_restrictions": base_locks + [
                "push the existing commit ONLY", "no amend/rebase/squash/new commit"],
            "commit_to_push": commit_hash,
            "expected_git_state_before": {
                "ahead": 1, "behind": 0, "tracked_tree_clean": True,
                "nothing_staged": True},
            "verify_after": {"head_equals_origin": True, "ahead": 0, "behind": 0}},
        "advance": {
            "token": advance_token or (
                "HUMAN_DECISION_%s_ADVANCE_TO_%s_OR_REJECT"
                % (c, (stage or "NEXT_STAGE").upper())),
            "hard_restrictions": base_locks + [
                "advance to the next stage ONLY; build that stage's artifact only"],
            "requires_human_paste": True},
        "hold": {
            "token": "HOLD_%s_AT_%s" % (c, (stage or "CURRENT_STAGE").upper()),
            "hard_restrictions": ["take no further action; preserve current state"]},
        "reject": {
            "token": "HUMAN_DECISION_%s_REJECT_OR_PROMOTE" % c,
            "hard_restrictions": base_locks + [
                "reject + keep on record; bump the rejected ledger; do not rescue"]},
        "data_staging": {
            "token": data_staging_token or (
                "HUMAN_STAGE_FROZEN_DATASET_THEN_REAUTHORISE_%s_LABELS" % c),
            "hard_restrictions": base_locks + [
                "operator stages a FROZEN dataset with provenance (path + source + "
                "retrieval-UTC + recomputable SHA256); SPARTA fetches nothing",
                "do NOT proceed to labels until a fresh authorization is given"]},
    }


# ===========================================================================
# 2. MORNING DECISION PACKET (the assembled deliverable)
# ===========================================================================

def build_morning_decision_packet(repo_state: dict) -> dict[str, Any]:
    """PURE. Assemble the full morning decision packet from the injected repo_state +
    the live committed candidate chain. Read-only; recommends; executes nothing."""
    rs = repo_state or {}
    git = git_safety_gate(rs)
    lane = _lane.get_lane_status()
    cand = _c22_chain_state()

    pending_push_token = None
    if git["ahead"] > 0 and not git["blockers"]:
        pending_push_token = "APPROVE_PUSH_<PENDING_UNIT>_ONLY"

    gate = recommend_gate({
        "git_safety": git,
        "candidate": cand,
        "pending_push_token": pending_push_token})

    task = select_next_safe_task(rs)

    tokens = approval_tokens(
        unit_name="C22_NEXT_APPROVED_UNIT",
        candidate="C22", stage="real_candle_labels",
        advance_token="HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT",
        data_staging_token=cand["next_required_action"])

    record: dict[str, Any] = {
        "schema_version": V2_SCHEMA_VERSION, "mode": V2_MODE, "lane": V2_LANE,
        "bundle_name": BUNDLE_NAME,
        "section": "morning_decision_packet",
        "is_read_only_packet": True,
        "label": (
            "SPARTA Research Factory Automation V2 -- Morning Decision Packet "
            "(READ-ONLY, RESEARCH ONLY). Candidate status + last verdict + blockers + "
            "evidence + the next recommended human gate + the EXACT approval token + "
            "explicit danger-lock status. Recommends only; executes nothing; never "
            "crosses a human gate."),
        # repo sync
        "repo_sync": {
            "head": rs.get("head"), "origin": rs.get("origin"),
            "in_sync": rs.get("head") is not None
            and rs.get("head") == rs.get("origin"),
            "ahead": git["ahead"], "behind": git["behind"],
            "clean": git["clean"], "staged_count": git["staged_count"]},
        "git_safety": git,
        # candidate status
        "candidate_status": {
            "lane_active_candidate": lane.get("active_candidate"),
            "lane_next_required_action": lane.get("next_required_action"),
            "rejected_ledger_count": lane.get("rejected_ledger_count"),
            "rejected_ledger_is_c1_to_c21": lane.get("rejected_ledger_count") == 26,
            "last_rejected_candidate": lane.get("last_rejected_candidate"),
            "c22": cand},
        "last_verdict": cand["last_verdict"],
        "blockers": ([] if git["safe_to_automate"] else list(git["blockers"]))
        + ([cand["blocked_reason"]] if cand["blocked_reason"] else []),
        "evidence": {
            "c22_chain_artifacts_valid": cand["chain_artifacts_valid"],
            "c22_evidence_test_files": cand["evidence_test_files"],
            "spec_rules_preserved": cand["spec_rules_preserved"]},
        # the recommendation + next human action + token
        "recommended_gate": gate,
        "next_safe_task": task,
        "next_recommended_human_action": cand["next_required_action"]
        if cand["blocked_reason"] == "DATA_NOT_READY"
        else gate.get("recommended_token"),
        "copy_paste_approval_tokens": tokens,
        # explicit danger-lock status
        "danger_locks": automation_safety_locks(),
        "requires_human_approval": True,
        "executes_nothing": True,
        "recommends_only": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_git_io": True, "no_network_io": True,
        "no_auto_commit": True, "no_auto_push": True, "no_auto_fetch": True,
        "no_auto_promote": True, "no_auto_advance": True, "no_gate_skip": True,
        "no_broad_git_add": True, "no_data_fetch": True, "no_signum": True,
        "no_mcp": True, "no_hyperliquid": True, "no_api_keys": True,
        "no_credentials": True, "no_bot_edits": True, "no_claude_routines": True,
        "no_send_trades": True, "no_broker": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_scheduler_change": True,
        "no_scheduler_install": True, "no_optimization_without_gate": True,
        "no_reopen_closed_candidate": True, "no_modify_strategy_rules": True,
        "no_downstream_gate_unlock": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_morning_decision_packet(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the packet is research-only, read-only,
    recommends-only (never auto-executes / never skips a gate), surfaces the candidate
    chain + C22 DATA_NOT_READY block with a DATASET-STAGING recommendation (NOT labels),
    carries the danger-lock status with every dangerous channel locked, the C1-C21 (26)
    ledger, copy-paste tokens for every safe action, and pins every capability flag
    False."""
    failures: list = []
    if record.get("mode") != V2_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_read_only_packet") is not True:
        failures.append("not_read_only_packet")
    if record.get("recommends_only") is not True:
        failures.append("not_recommends_only")
    if record.get("executes_nothing") is not True:
        failures.append("executes_something")

    # recommendation kind in the allowlist; recommended token carries no forbidden verb
    gate = record.get("recommended_gate") or {}
    if gate.get("recommendation_kind") not in ALL_RECOMMENDATION_KINDS:
        failures.append("recommendation_kind_not_in_allowlist")
    if gate.get("auto_executes") is not False:
        failures.append("recommendation_auto_executes")
    tok = str(gate.get("recommended_token") or "").lower()
    for bad in FORBIDDEN_TOKEN_SUBSTRINGS:
        if bad in tok:
            failures.append("recommended_token_forbidden_%s" % bad)

    # C22 DATA_NOT_READY must NEVER route to labels and must never claim labels.
    # The STAGING recommendation governs only when the repo is safe + not ahead (a dirty
    # repo or a pending push legitimately takes higher priority -- RESOLVE_REPO / PUSH).
    cand = (record.get("candidate_status") or {}).get("c22") or {}
    git = record.get("git_safety") or {}
    git_safe = bool(git.get("safe_to_automate")) and int(git.get("ahead", 0) or 0) == 0
    if cand.get("blocked_reason") == "DATA_NOT_READY":
        if cand.get("labels_produced") is not False:
            failures.append("must_not_have_produced_labels")
        # never recommend advancing to labels while blocked
        if gate.get("recommendation_kind") == REC_ADVANCE and git_safe:
            failures.append("must_not_advance_while_data_not_ready")
        if git_safe and gate.get("recommendation_kind") != REC_STAGE_DATA:
            failures.append("data_not_ready_must_recommend_staging_when_repo_safe")
        nra = record.get("next_recommended_human_action") or ""
        if "STAGE_FROZEN" not in nra and "STAGE_TREND_RADAR" not in nra:
            failures.append("next_action_not_dataset_staging")

    # ledger C1-C21 (26); strategy rules preserved
    cs = record.get("candidate_status") or {}
    if cs.get("rejected_ledger_count") != 26:
        failures.append("ledger_not_26")
    if (record.get("evidence") or {}).get("spec_rules_preserved") is not True:
        failures.append("spec_rules_not_preserved")

    # danger locks: every dangerous channel locked
    dl = record.get("danger_locks") or {}
    for k in ("no_automatic_commit", "no_automatic_push", "no_automatic_data_fetch",
              "no_automatic_candidate_promotion", "never_skips_human_gates",
              "live_trading_locked", "paper_trading_locked", "broker_locked",
              "api_keys_locked", "credentials_locked", "signum_locked",
              "hyperliquid_locked", "mcp_locked", "claude_routines_locked",
              "scheduler_locked", "bot_edits_locked", "trades_locked"):
        if dl.get(k) is not True:
            failures.append("danger_lock_off_%s" % k)

    # copy-paste tokens present for every safe action
    tokens = record.get("copy_paste_approval_tokens") or {}
    for kind in ("commit", "push", "advance", "hold", "reject", "data_staging"):
        if kind not in tokens or not (tokens[kind] or {}).get("token"):
            failures.append("approval_token_missing_%s" % kind)
        # no forbidden verb in any generated token
        t = str((tokens.get(kind) or {}).get("token", "")).lower()
        for bad in FORBIDDEN_TOKEN_SUBSTRINGS:
            if bad in t:
                failures.append("token_forbidden_%s_in_%s" % (bad, kind))

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_git_io", "no_auto_commit", "no_auto_push",
                "no_auto_fetch", "no_auto_promote", "no_gate_skip", "no_broad_git_add",
                "no_data_fetch", "no_signum", "no_mcp", "no_hyperliquid",
                "no_api_keys", "no_credentials", "no_bot_edits", "no_send_trades",
                "no_paper_trading", "no_live_trading", "no_scheduler_install",
                "no_reopen_closed_candidate", "no_modify_strategy_rules"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
