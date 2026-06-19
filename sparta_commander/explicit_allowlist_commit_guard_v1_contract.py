"""SPARTA Explicit-Allowlist Commit Guard v1 -- PURE, RESEARCH-ONLY POLICY CONTRACT.

A pure, stdlib-only DECLARATION + decision function that formalizes EXPLICIT-PATH
staging for any future research automation. It exists because the tracked tree is
clean but the repository carries large pre-existing UNTRACKED clutter (thousands of
files under strategy_lab/, reports/, data/, plus stray/malformed entries); a broad
`git add .` / `git add -A` would sweep that clutter -- including generated data
artifacts -- into a commit. This guard makes that impossible by policy.

It is a policy/decision contract, NOT a runner: it executes nothing, runs no git,
stages/commits/pushes nothing, touches no network/data/paper/live surface. It only
takes a DECLARED staging plan (the staging command + the exact expected-file
allowlist + the files that WOULD be staged + any reviewed exemptions) and returns
the single safe verdict: APPROVE_STAGING (the plan is explicit, scoped, and
artifact-free) or STOP_FOR_HUMAN (broad staging, an out-of-allowlist file, or an
un-exempted data/report/CSV/JSON/JSONL/log artifact), with reasons.

Core rules (all enforced by evaluate_staging_plan):
  1. The staging command MUST be explicit per-path `git add <path> [<path> ...]`.
     `git add .`, `git add -A`, `git add --all`, `git add -u`, `git add :/`, and
     `git commit -a/-am/--all` are FORBIDDEN in automation.
  2. Every commit bundle MUST declare its exact expected files BEFORE staging (a
     non-empty allowlist).
  3. STOP if any staged file is OUTSIDE the declared allowlist.
  4. STOP if any staged file is a data/report/CSV/JSON/JSONL/log artifact or lives
     under data/ -- UNLESS that exact path is exempted by a reviewed contract.
  5. Pre-existing UNTRACKED clutter is TOLERATED: clutter that is not in the staging
     set never blocks a clean explicit-path commit. The guard only ever inspects the
     STAGED set against the declared allowlist.

Every capability flag is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

CG_SCHEMA_VERSION = 1
CG_MODE = "RESEARCH_ONLY"
CG_LANE = "crypto_d1_auto_research"

# ---- the two verdicts (the COMPLETE allowlist) -----------------------------
VERDICT_APPROVE_STAGING = "APPROVE_STAGING"
VERDICT_STOP_FOR_HUMAN = "STOP_FOR_HUMAN"
ALL_VERDICTS = (VERDICT_APPROVE_STAGING, VERDICT_STOP_FOR_HUMAN)

# ---- forbidden broad-staging commands (closed blocklist) --------------------
# Any of these tokens appearing as a standalone argument to `git add` / `git commit`
# means broad staging -> forbidden in automation.
FORBIDDEN_ADD_ARG_TOKENS = (".", "-A", "--all", "-u", "--update", ":/", "*", "-Av",
                            "-vA")
FORBIDDEN_COMMIT_ARG_TOKENS = ("-a", "-am", "-am.", "--all", "-a.")
# human-readable canonical forbidden forms (for the declared policy surface)
FORBIDDEN_STAGING_FORMS = (
    "git add .", "git add -A", "git add --all", "git add -u", "git add :/",
    "git add *", "git commit -a", "git commit -am", "git commit --all",
)

# ---- artifact detection (un-exempted -> STOP) -------------------------------
DATA_ARTIFACT_EXTENSIONS = (".csv", ".json", ".jsonl", ".log", ".parquet",
                            ".feather", ".pkl", ".npy", ".npz", ".db", ".sqlite")
DATA_ARTIFACT_PATH_PREFIXES = ("data/",)
REPORT_ARTIFACT_PATH_PREFIXES = ("reports/",)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "runs_git", "stages_files", "auto_commits", "auto_pushes",
    "writes_files", "runs_shell", "runs_detector", "runs_labels", "runs_replay",
    "computes_pnl", "optimizes_parameters", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "deletes_clutter", "moves_clutter",
    "stashes_clutter", "modifies_clutter", "installs_scheduler", "starts_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "starts_new_candidate", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "weakens_human_gates", "broad_stages",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def _norm(path: str) -> str:
    return str(path).replace("\\", "/").strip().lstrip("./")


def is_artifact_path(path: str) -> bool:
    """Pure: True if the path is a data/report/CSV/JSON/JSONL/log artifact or lives
    under data/. Source (.py / .md / .txt / .toml / .cfg / .ini) is NOT an artifact.
    Note: JSON under any path is treated as an artifact by policy (config JSON that
    must be tracked has to be exempted by a reviewed contract)."""
    p = _norm(path).lower()
    if any(p.startswith(pre) for pre in DATA_ARTIFACT_PATH_PREFIXES):
        return True
    if any(p.startswith(pre) for pre in REPORT_ARTIFACT_PATH_PREFIXES):
        return True
    return any(p.endswith(ext) for ext in DATA_ARTIFACT_EXTENSIONS)


def is_broad_staging_command(command: str) -> bool:
    """Pure: True if the declared staging/commit command performs BROAD staging
    (`git add .` / `-A` / `--all` / `-u` / `:/` / `*`, or `git commit -a/-am`)."""
    if not command:
        return False
    raw = str(command).replace("\\", "/").strip()
    tokens = raw.split()
    low = [t for t in tokens]
    # locate `git add` / `git commit` segments
    for i in range(len(low) - 1):
        if low[i] == "git" and low[i + 1] == "add":
            for arg in low[i + 2:]:
                if arg in FORBIDDEN_ADD_ARG_TOKENS:
                    return True
        if low[i] == "git" and low[i + 1] == "commit":
            for arg in low[i + 2:]:
                if arg in FORBIDDEN_COMMIT_ARG_TOKENS:
                    return True
                # combined short flags like -am / -a contain 'a' for --all
                if arg.startswith("-") and not arg.startswith("--") and "a" in arg:
                    return True
    return False


def evaluate_staging_plan(plan: dict) -> dict[str, Any]:
    """PURE. Given a DECLARED staging plan, return APPROVE_STAGING or STOP_FOR_HUMAN.

    plan = {
        "staging_command": "git add <path> [<path> ...]",   # the exact command
        "expected_files": [<path>, ...],                    # declared allowlist
        "staged_files":   [<path>, ...],                    # what WOULD be staged
        "exemptions":     [{"path": <path>, "reviewed_contract": <name>}, ...],
        # optional, informational only -- never blocks:
        "untracked_clutter_present": True/False,
    }

    Executes nothing; performs no git. The actual `git add` is still done by a human
    (or a separately-approved runner) -- this only says whether the declared plan is
    safe to stage.
    """
    plan = plan or {}
    command = plan.get("staging_command") or ""
    expected = [_norm(p) for p in (plan.get("expected_files") or [])]
    staged = [_norm(p) for p in (plan.get("staged_files") or [])]
    exemptions = plan.get("exemptions") or []
    exempt_paths = {_norm(e.get("path")): e for e in exemptions
                    if isinstance(e, dict) and e.get("path")}

    expected_set = set(expected)
    reasons: list = []
    stop = False

    # 1) broad staging forbidden
    if is_broad_staging_command(command):
        stop = True
        reasons.append("broad_staging_forbidden")
    # the command must be an explicit `git add <path>` form (or empty plan rejected)
    if command and "git add" not in command and "git commit" not in command:
        stop = True
        reasons.append("staging_command_not_recognized")

    # 2) the bundle must declare a non-empty expected-file allowlist
    if not expected:
        stop = True
        reasons.append("no_expected_files_declared")

    # 3) every staged file must be inside the declared allowlist
    outside = [f for f in staged if f not in expected_set]
    for f in outside:
        stop = True
        reasons.append("staged_file_outside_allowlist__%s" % f)

    # 4) artifact files (staged OR declared) must be exempted by a reviewed contract
    artifacts_blocked = []
    for f in sorted(set(staged) | expected_set):
        if is_artifact_path(f):
            ex = exempt_paths.get(f)
            if not (ex and ex.get("reviewed_contract")):
                stop = True
                artifacts_blocked.append(f)
                reasons.append("data_or_report_artifact_not_exempted__%s" % f)

    # an exemption that does not cite a reviewed contract is itself invalid
    for e in exemptions:
        if isinstance(e, dict) and e.get("path") and not e.get("reviewed_contract"):
            stop = True
            reasons.append("exemption_missing_reviewed_contract__%s"
                           % _norm(e.get("path")))

    # 5) untracked clutter is tolerated -- it NEVER contributes a stop reason.

    # informational: declared files not yet staged (not a stop by itself)
    missing = [f for f in expected if f not in set(staged)]

    verdict = VERDICT_STOP_FOR_HUMAN if stop else VERDICT_APPROVE_STAGING
    return {
        "schema_version": CG_SCHEMA_VERSION, "mode": CG_MODE, "lane": CG_LANE,
        "is_pure_policy_only": True,
        "verdict": verdict,
        "approve_staging": verdict == VERDICT_APPROVE_STAGING,
        "stop_for_human": verdict == VERDICT_STOP_FOR_HUMAN,
        "reasons": reasons,
        "staged_files_in_allowlist": [f for f in staged if f in expected_set],
        "staged_files_outside_allowlist": outside,
        "artifacts_blocked": artifacts_blocked,
        "declared_but_not_staged": missing,
        "broad_staging_detected": is_broad_staging_command(command),
        "untracked_clutter_tolerated": True,
        "requires_human_approval": verdict == VERDICT_STOP_FOR_HUMAN,
        "executes_nothing": True,
    }


def build_commit_guard_contract() -> dict[str, Any]:
    """PURE. The full declared explicit-allowlist staging policy + locked capability
    posture. Stages / commits / pushes NOTHING."""
    record: dict[str, Any] = {
        "schema_version": CG_SCHEMA_VERSION, "mode": CG_MODE, "lane": CG_LANE,
        "is_pure_policy_only": True,
        "is_runner": False,
        "label": (
            "Explicit-Allowlist Commit Guard v1 (READ-ONLY POLICY, RESEARCH ONLY). "
            "Future automation must stage by EXPLICIT per-path `git add <path>` only "
            "-- `git add .` / `-A` / `--all` / `-u` / `:/` / `*` and `git commit "
            "-a/-am` are FORBIDDEN. Every commit bundle declares its exact expected "
            "files before staging; any staged file outside the allowlist, or any "
            "un-exempted data/report/CSV/JSON/JSONL/log artifact (or anything under "
            "data/), STOPS for a human. Pre-existing untracked clutter is tolerated "
            "and never blocks a clean explicit-path commit. Pure policy: executes "
            "nothing, runs no git, deletes/moves/stashes/modifies no clutter. Every "
            "capability flag is False."),
        "verdicts": list(ALL_VERDICTS),
        "explicit_path_staging_required": True,
        "forbidden_staging_forms": list(FORBIDDEN_STAGING_FORMS),
        "forbids_git_add_dot": True,
        "forbids_git_add_all": True,
        "requires_declared_expected_files_before_staging": True,
        "stops_if_staged_outside_allowlist": True,
        "stops_on_unexempted_data_artifact": True,
        "data_artifact_extensions": list(DATA_ARTIFACT_EXTENSIONS),
        "data_artifact_path_prefixes": list(DATA_ARTIFACT_PATH_PREFIXES),
        "report_artifact_path_prefixes": list(REPORT_ARTIFACT_PATH_PREFIXES),
        "artifact_exemption_requires_reviewed_contract": True,
        "tolerates_preexisting_untracked_clutter": True,
        "never_deletes_moves_or_modifies_clutter": True,
        "does_not_weaken_human_gates": True,
        "human_review_required": True,
        "pairs_with": "autopilot_research_orchestrator_v2_contract",
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_git": True, "no_stage": True, "no_auto_commit": True,
        "no_auto_push": True, "no_write": True, "no_shell": True,
        "no_broad_staging": True, "no_git_add_dot": True, "no_git_add_all": True,
        "no_unexempted_data_artifact": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_data_mutation": True,
        "no_clutter_deletion": True, "no_clutter_move": True, "no_clutter_stash": True,
        "no_clutter_modification": True, "no_scheduler_install": True,
        "no_new_candidate": True, "no_paper_trading": True, "no_live_trading": True,
        "no_broker": True, "no_order_logic": True, "no_credentials": True,
        "no_human_gate_weakening": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_commit_guard_contract(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the contract is research-only, pure
    policy (not a runner), forbids broad staging, requires a declared allowlist,
    stops on out-of-allowlist files and un-exempted data/report artifacts, tolerates
    pre-existing untracked clutter without ever deleting/moving/modifying it, does
    not weaken human gates, and pins every capability flag False with scope locks."""
    failures: list = []
    if record.get("mode") != CG_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_policy_only") is not True:
        failures.append("not_pure_policy_only")
    if record.get("is_runner") is not False:
        failures.append("must_not_be_runner")

    for k in ("explicit_path_staging_required", "forbids_git_add_dot",
              "forbids_git_add_all",
              "requires_declared_expected_files_before_staging",
              "stops_if_staged_outside_allowlist",
              "stops_on_unexempted_data_artifact",
              "artifact_exemption_requires_reviewed_contract",
              "tolerates_preexisting_untracked_clutter",
              "never_deletes_moves_or_modifies_clutter",
              "does_not_weaken_human_gates"):
        if record.get(k) is not True:
            failures.append("policy_flag_off_%s" % k)

    # the forbidden forms must include the two named broad commands
    forms = record.get("forbidden_staging_forms") or []
    for must in ("git add .", "git add -A"):
        if must not in forms:
            failures.append("forbidden_form_missing__%s" % must)

    # artifact extension policy must cover csv/json/jsonl/log
    exts = record.get("data_artifact_extensions") or []
    for must in (".csv", ".json", ".jsonl", ".log"):
        if must not in exts:
            failures.append("artifact_ext_missing__%s" % must)
    if "data/" not in (record.get("data_artifact_path_prefixes") or []):
        failures.append("data_prefix_missing")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_git", "no_stage", "no_broad_staging",
                "no_git_add_dot", "no_git_add_all", "no_unexempted_data_artifact",
                "no_clutter_deletion", "no_clutter_move", "no_clutter_stash",
                "no_clutter_modification", "no_new_candidate", "no_paper_trading",
                "no_live_trading", "no_human_gate_weakening", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
