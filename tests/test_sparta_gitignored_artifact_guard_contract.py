"""SPARTA gitignored-artifact / repo-cleanliness guard test (Bundle E1).

The LIVE guard: gathers the real tracked (`git ls-files`) + staged (`git diff --cached
--name-only`) paths READ-ONLY and asserts SPARTA tracks/stages NONE of the forbidden
provider-data / artifact / label / report / log / secret paths. Plus synthetic fixtures
proving the guard CATCHES forbidden paths and does NOT flag legitimate code / other-candidate
evidence."""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import sparta_commander.sparta_gitignored_artifact_guard_contract as ga

_REPO_ROOT = Path(ga.__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _git(args):
    """READ-ONLY git query (ls-files / diff --cached --name-only only)."""
    assert args[0] in ("ls-files", "diff"), "read-only git only"
    proc = subprocess.run(["git", *args], cwd=str(_REPO_ROOT),
                          capture_output=True, text=True)
    return [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]


# ---- LIVE repo: tracks/stages no forbidden artifact ------------------------

def test_live_repo_has_no_forbidden_tracked_or_staged_artifacts():
    tracked = _git(["ls-files"])
    staged = _git(["diff", "--cached", "--name-only"])
    g = ga.build_guard(tracked, staged)
    assert ga.validate_guard(g)["valid"] is True
    assert g["clean"] is True, (
        "forbidden tracked/staged artifacts: %s | %s"
        % (g["tracked_violations"], g["staged_violations"]))
    assert g["n_tracked_violations"] == 0
    assert g["n_staged_violations"] == 0
    assert g["dangerous_staged_artifact_present"] is False


# ---- the guard CATCHES forbidden paths -------------------------------------

_FORBIDDEN_FIXTURES = [
    "data/external_signum_trend_radar_gc/gc_crypto_trendradar_daily.json",
    "data/external_signum_trend_radar_gc/detector_labels/c22_gc_real_candle_entry_labels.json",
    "data/external_signum_trend_radar_gc_inbox/gc_crypto_trendradar_daily_20260621.json",
    "reports/automation_v2_daily/automation_v2_daily_report_2026-06-20.md",
    "reports/autopilot_morning/latest.md",
    "reports/autopilot_morning/latest.json",
    "data/c10_labels_review.log",
    "reports/some_run.log",
    "local_secrets/telegram_token.txt",
    "config/server.pem",
    "secrets/id_rsa",
    "app/.env",
    "session/cookies.txt",
    "auth/credentials.json",
]


def test_guard_catches_every_forbidden_fixture():
    for path in _FORBIDDEN_FIXTURES:
        assert ga.classify_path(path) is not None, path
    # as tracked violations
    g = ga.build_guard(_FORBIDDEN_FIXTURES, [])
    assert g["clean"] is False
    assert g["n_tracked_violations"] == len(_FORBIDDEN_FIXTURES)
    assert ga.validate_guard(g)["valid"] is True
    # as a dangerous STAGED artifact
    s = ga.build_guard([], ["data/external_signum_trend_radar_gc/x.json"])
    assert s["dangerous_staged_artifact_present"] is True
    assert s["clean"] is False
    assert ga.validate_guard(s)["valid"] is True


# ---- the guard does NOT flag legit code / other-candidate evidence ---------

_LEGIT_FIXTURES = [
    "sparta_commander/sparta_gitignored_artifact_guard_contract.py",
    "sparta_commander/external_signum_trend_radar_gc_long_short_v1_proposal_contract.py",
    "sparta_commander/crypto_intraday_breakout_pullback_structure_real_candle_detector_labels_review_contract.py",
    "sparta_commander/conviction_bar_follow_through_v1_replay_results_review_contract.py",
    "tools/c22_signum_gc_download_pickup_once.py",
    "tests/test_sparta_gitignored_artifact_guard_contract.py",
    ".gitignore",
    "README.md",
    "data/breakout_pullback/detector_labels/notes.py",   # CODE under a data path, not .log
]


def test_guard_does_not_flag_legit_paths():
    for path in _LEGIT_FIXTURES:
        assert ga.classify_path(path) is None, path
    g = ga.build_guard(_LEGIT_FIXTURES, _LEGIT_FIXTURES)
    assert g["clean"] is True
    assert ga.validate_guard(g)["valid"] is True


# ---- anti-tamper -----------------------------------------------------------

def test_tamper_rejected():
    g = ga.build_guard([], [])
    # claim clean while listing a real violation
    bad = {**g, "tracked_violations": [{"path": "data/external_signum_trend_radar_gc/x",
                                        "reason": "x"}], "clean": True}
    assert ga.validate_guard(bad)["valid"] is False
    # list a non-violation as a violation
    bad2 = {**g, "tracked_violations": [{"path": "sparta_commander/foo.py", "reason": "x"}],
            "n_tracked_violations": 1, "clean": False}
    assert ga.validate_guard(bad2)["valid"] is False
    # claim it modifies .gitignore
    assert ga.validate_guard({**g, "modifies_gitignore": True})["valid"] is False
    for flag in ga._CAPABILITY_FLAGS_FALSE:
        assert ga.validate_guard({**g, flag: True})["valid"] is False


# ---- contract module purity (no git run / no file content read) ------------

def test_contract_module_purity():
    src = Path(ga.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    # actionable verbs only -- "git ls-files" appears solely in the docstring (the pure
    # contract runs no git; the test gathers the paths and passes them in).
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "json.load", "read_text", "glob("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
