"""SPARTA gitignored-artifact / repo-cleanliness GUARD -- PURE, READ-ONLY, REPORTING ONLY.

A pure guard that fails if SPARTA ever accidentally TRACKS or STAGES a forbidden
provider-data / artifact / label / report / log / secret path. It is PURE: it operates on
git path lists (the test gathers `git ls-files` + `git diff --cached --name-only` read-only)
and classifies them with deterministic path-prefix / filename-pattern checks -- it runs no
git command, reads no file content, and modifies nothing.

Scoped DELIBERATELY to the GITIGNORED C22 / generated paths + secret-file patterns, so it
NEVER flags the legitimately-committed frozen evidence of OTHER candidates (whose
detector-label / replay-review CONTRACTS live under sparta_commander/, not data/):

  * forbidden tracked/staged directory prefixes:
      data/external_signum_trend_radar_gc/        (C22 dataset + detector labels + replay)
      data/external_signum_trend_radar_gc_inbox/  (C22 import inbox)
      reports/automation_v2_daily/                (generated daily reports)
      reports/autopilot_morning/                  (generated latest.md / latest.json)
  * gitignored log artifacts: any *.log under data/ or reports/;
  * secret files: anything under local_secrets/, *.pem/.key/.p12/.pfx, id_rsa, .env*,
    cookies/credentials/session files.

This guard advances nothing, modifies no file, changes no .gitignore (a missing ignore rule
is REPORTED, never written), and connects to nothing. Every dangerous capability is pinned
False.
"""
from __future__ import annotations

from typing import Any

GA_SCHEMA_VERSION = 1
GA_MODE = "RESEARCH_ONLY"

# gitignored artifact directory prefixes that must NEVER be tracked or staged.
FORBIDDEN_TRACKED_PREFIXES = (
    "data/external_signum_trend_radar_gc/",
    "data/external_signum_trend_radar_gc_inbox/",
    "reports/automation_v2_daily/",
    "reports/autopilot_morning/",
)
# *.log artifacts are forbidden only under these (generated) roots.
LOG_FORBIDDEN_ROOTS = ("data/", "reports/")
# secret-file basename suffixes / exact names.
SECRET_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".session")
SECRET_BASENAMES = ("id_rsa", "id_rsa.pub", "cookies.txt", "cookies.json",
                    "credentials.json", "session.json")

VERDICT_GUARD = "SPARTA_GITIGNORED_ARTIFACT_GUARD"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "performs_io", "runs_git", "reads_file_content", "modifies_files",
    "modifies_gitignore", "writes_gitignore", "stages_files", "commits", "pushes",
    "fetches_data", "performs_network_io", "connects_signum", "uses_mcp", "calls_api",
    "places_orders", "sends_trades", "paper_trading", "live_trading",
    "modifies_c22_pipeline", "crosses_into_forbidden_gate",
)


def classify_path(path: Any) -> str | None:
    """PURE. Return a violation reason if the path is a forbidden tracked/staged artifact,
    else None. Deterministic prefix/pattern checks; no I/O."""
    if not isinstance(path, str) or not path.strip():
        return None
    p = path.replace("\\", "/").strip()
    base = p.rsplit("/", 1)[-1].lower()
    for pref in FORBIDDEN_TRACKED_PREFIXES:
        if p.startswith(pref):
            return "gitignored_artifact_dir:" + pref
    if p.endswith(".log") and any(p.startswith(r) for r in LOG_FORBIDDEN_ROOTS):
        return "gitignored_log_artifact"
    if "local_secrets/" in p or p.startswith("local_secrets/"):
        return "secret_path:local_secrets"
    if base.endswith(SECRET_SUFFIXES):
        return "secret_file:" + base.rsplit(".", 1)[-1]
    if base in SECRET_BASENAMES:
        return "secret_file:" + base
    if base == ".env" or base.startswith(".env."):
        return "secret_file:env"
    return None


def classify_paths(paths: Any) -> list:
    """PURE. The forbidden paths in a list, each as {path, reason}."""
    out = []
    for path in (paths or []):
        reason = classify_path(path)
        if reason is not None:
            out.append({"path": path, "reason": reason})
    return out


def build_guard(tracked_paths: Any, staged_paths: Any) -> dict[str, Any]:
    """PURE. Build the guard result from the tracked + staged path lists. No I/O."""
    tracked_violations = classify_paths(tracked_paths)
    staged_violations = classify_paths(staged_paths)
    clean = not tracked_violations and not staged_violations

    record: dict[str, Any] = {
        "schema_version": GA_SCHEMA_VERSION, "mode": GA_MODE,
        "section": "sparta_gitignored_artifact_guard",
        "is_read_only_guard": True,
        "verdict": VERDICT_GUARD,
        "clean": clean,
        "tracked_violations": tracked_violations,
        "staged_violations": staged_violations,
        "n_tracked_violations": len(tracked_violations),
        "n_staged_violations": len(staged_violations),
        "dangerous_staged_artifact_present": len(staged_violations) > 0,
        "forbidden_prefixes": list(FORBIDDEN_TRACKED_PREFIXES),
        # the guard never writes .gitignore -- a missing rule is REPORTED, not fixed.
        "modifies_gitignore": False,
        "advances_nothing": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_io": True, "no_run_git": True,
        "no_read_file_content": True, "no_modify_files": True,
        "no_modify_gitignore": True, "no_stage": True, "no_commit": True, "no_push": True,
        "no_data_fetch": True, "no_network_io": True, "no_signum_connection": True,
        "no_mcp": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_modify_c22_pipeline": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_guard(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, read-only guard; the violation
    lists are consistent with classify_paths; `clean` matches (no tracked + no staged
    violations); the guard modifies no .gitignore; and every capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != GA_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_read_only_guard") is not True:
        failures.append("not_read_only_guard")
    if r.get("verdict") != VERDICT_GUARD:
        failures.append("bad_verdict")

    tv = r.get("tracked_violations") or []
    sv = r.get("staged_violations") or []
    # every listed violation must genuinely classify as forbidden
    for v in list(tv) + list(sv):
        if classify_path((v or {}).get("path")) is None:
            failures.append("non_violation_listed:%s" % (v or {}).get("path"))
    if r.get("n_tracked_violations") != len(tv):
        failures.append("tracked_count_inconsistent")
    if r.get("n_staged_violations") != len(sv):
        failures.append("staged_count_inconsistent")
    if r.get("clean") is not (not tv and not sv):
        failures.append("clean_flag_inconsistent")
    if r.get("dangerous_staged_artifact_present") is not (len(sv) > 0):
        failures.append("staged_present_inconsistent")
    if tuple(r.get("forbidden_prefixes") or ()) != FORBIDDEN_TRACKED_PREFIXES:
        failures.append("forbidden_prefixes_tampered")
    if r.get("modifies_gitignore") is not False:
        failures.append("must_not_modify_gitignore")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_io", "no_run_git", "no_read_file_content",
                "no_modify_files", "no_modify_gitignore", "no_stage", "no_commit",
                "no_push", "no_data_fetch", "no_network_io", "no_signum_connection",
                "no_mcp", "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_modify_c22_pipeline"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
