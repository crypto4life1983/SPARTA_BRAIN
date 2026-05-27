"""Tests for sparta_commander/research_orchestrator/ — covers the 10 required behaviors.

1. detecting HEAD changes
2. detecting staged foreign files
3. refusing commit with extra staged files
4. detecting P6 K9 pass/fail from sealed JSON fixture
5. detecting missing REC1_T1 and recommending supplement
6. detecting duplicate chain anchor
7. verifying seal hash
8. preserving lessons.md guard
9. safe executor exact-path commit only
10. pending decision JSON creation
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

import pytest


# Make sparta_commander importable from this test file even when pytest is
# invoked with --rootdir=tests/ (workaround for the `hydra ` ghost dir).
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


from sparta_commander.research_orchestrator import (  # noqa: E402
    anchor_verifier, decision_engine, gate_evaluator, git_sentinel,
    l1_checker, phase_classifier, safe_executor, seal_verifier,
)
from sparta_commander.research_orchestrator.state import (  # noqa: E402
    CandidateState, K9_FAIL, K9_PASS, L1_FULL, L1_MISSING, L1_PARTIAL,
    PHASE_P6_IS,
)
from sparta_commander.research_orchestrator.storage import Storage  # noqa: E402


# --- Helpers --------------------------------------------------------------


def _canonical_seal_of(body: dict) -> str:
    """Recompute the LESSON_HUNTER_004 canonical seal for a body dict."""
    body_check = {k: v for k, v in body.items() if k not in ("report_seal_sha256", "seal_method")}
    canonical = json.dumps(
        body_check, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _write_sealed_report(path: pathlib.Path, body: dict) -> None:
    body["report_seal_sha256"] = _canonical_seal_of(body)
    body["seal_method"] = "LESSON_HUNTER_004 canonical roundtrip"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(body, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )


def _init_git_repo(repo: pathlib.Path) -> None:
    """Init a clean git repo at `repo` with one initial commit on master."""
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@test"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "test"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "commit.gpgsign", "false"], check=True)
    # initial commit so HEAD exists
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True)


@pytest.fixture
def tmp_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """A fresh isolated git repo per test."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    return repo


@pytest.fixture
def sample_p6_pass_body() -> dict:
    """Fixture body resembling a sealed P6 IS diagnostic with K9 PASS."""
    return {
        "schema_id": "sparta.test.s99_d1_in_sample_diagnostic_result_sealed.v1",
        "candidate_record_id": "s99-d1-test-candidate",
        "phase": "P6_IS_DIAGNOSTIC",
        "lifecycle_state": "P6_IS_DIAGNOSTIC_SEALED",
        "verdict": "READY_FOR_LONGER_BACKTEST",
        "parent_references": {
            "tier_n_spec_commit": "aaaaaaa",
            "p1_plan_lock_commit": "bbbbbbb",
            "p2_phase2_plan_commit": "ccccccc",
            "p3_build_commit": "ddddddd",
            "p4_smoke_commit": "eeeeeee",
        },
        "performance_summary": {
            "closed_trades_count": 159,
            "net_pnl_usd": 85975.59,
            "max_drawdown_pct": 0.1768,
            "sharpe_annualized": 0.5503,
            "annual_turnover": 84.79,
            "trades_per_year_observed": 34.34,
            "expectancy_per_trade_usd": 540.73,
            "s1_cost_drag_fraction": 0.0156,
        },
        "config_used": {
            "verdict_min_closed_trades": 100,
            "primary_csv_sha256": "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e",
            "rec1_equivalent_binding": True,
            "rec1_equivalent_oos_k9_disclosure": (
                "If observed IS rate falls below 25/year, OOS K9 unreachability becomes "
                "structurally probable."
            ),
        },
        "scan_diagnostics": {
            "csv_sha_verified_at_load": True,
            "is_window_start_engine_truth": "2019-05-13",
            "is_window_end_engine_truth": "2023-12-29",
        },
        "inherited_constraints_block_VERBATIM_FROM_P2_C6": [
            "REC1-equivalent binding carried byte-equivalent",
        ],
    }


@pytest.fixture
def sample_p6_fail_body(sample_p6_pass_body) -> dict:
    """Same shape, but K9 fails."""
    body = json.loads(json.dumps(sample_p6_pass_body))  # deep copy
    body["verdict"] = "INSUFFICIENT_SAMPLE"
    body["performance_summary"]["closed_trades_count"] = 48
    body["performance_summary"]["trades_per_year_observed"] = 10.37
    return body


# --- Test 1: detecting HEAD changes ---------------------------------------


def test_detect_head_changes(tmp_repo):
    initial_head = git_sentinel.head_sha(tmp_repo)
    # Make a new commit
    (tmp_repo / "another.txt").write_text("more\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_repo), "add", "another.txt"], check=True)
    subprocess.run(["git", "-C", str(tmp_repo), "commit", "-q", "-m", "second"], check=True)
    new_head = git_sentinel.head_sha(tmp_repo)
    assert new_head != initial_head
    assert "second" in git_sentinel.head_subject(tmp_repo)

    commits = git_sentinel.recent_commits(tmp_repo, n=3)
    assert len(commits) == 2
    assert commits[0][1] == "second"


# --- Test 2: detecting staged foreign files -------------------------------


def test_detect_staged_foreign_files(tmp_repo):
    # Stage one expected + one unexpected file
    (tmp_repo / "expected.txt").write_text("e\n", encoding="utf-8")
    (tmp_repo / "foreign.txt").write_text("f\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_repo), "add", "expected.txt", "foreign.txt"], check=True)

    staged = git_sentinel.staged_files(tmp_repo)
    assert set(staged) == {"expected.txt", "foreign.txt"}

    foreign = git_sentinel.detect_foreign_staged(staged, expected_paths={"expected.txt"})
    assert foreign == ["foreign.txt"]


# --- Test 3: safe_executor refuses commit with extra staged files ---------


def test_safe_executor_refuses_commit_with_extra_staged(tmp_repo):
    # Pre-stage a foreign file the operator didn't intend to commit
    (tmp_repo / "foreign.txt").write_text("not-mine\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_repo), "add", "foreign.txt"], check=True)

    # Operator intends to commit a different file
    (tmp_repo / "mine.txt").write_text("mine\n", encoding="utf-8")
    result = safe_executor.execute_commit_exact_paths(
        tmp_repo, ["mine.txt"], "intended commit", approval_level=2
    )
    assert result.status == "REFUSED"
    assert "index not clean before stage" in (result.refused_because or "")


# --- Test 4: detecting K9 pass/fail from sealed JSON ----------------------


def test_k9_extract_pass(tmp_path, sample_p6_pass_body):
    p = tmp_path / "p6_pass.json"
    _write_sealed_report(p, sample_p6_pass_body)
    g = gate_evaluator.extract_gates(p)
    assert g["closed_trades"] == 159
    assert g["k9_threshold"] == 100
    assert g["k9_status"] == "PASS"
    assert g["k9_margin_ratio"] == pytest.approx(1.59, abs=0.01)
    assert g["verdict"] == "READY_FOR_LONGER_BACKTEST"
    assert g["annual_turnover"] == 84.79


def test_k9_extract_fail(tmp_path, sample_p6_fail_body):
    p = tmp_path / "p6_fail.json"
    _write_sealed_report(p, sample_p6_fail_body)
    g = gate_evaluator.extract_gates(p)
    assert g["closed_trades"] == 48
    assert g["k9_status"] == "FAIL"
    assert g["k9_margin_ratio"] == pytest.approx(0.48, abs=0.01)
    assert g["verdict"] == "INSUFFICIENT_SAMPLE"


# --- Test 5: detecting missing REC1_T1 and recommending supplement --------


def test_l1_checker_missing_rec1_t1_recommends_supplement(tmp_path, sample_p6_pass_body):
    p = tmp_path / "p6.json"
    _write_sealed_report(p, sample_p6_pass_body)
    l1 = l1_checker.check_l1(p)
    assert l1["status"] == L1_PARTIAL
    assert l1["rec1_t1_hits"] == 0  # no REC1_T1 in fixture
    assert l1["rec1_equivalent_hits"] >= 1
    assert l1["needs_supplement"] is True
    assert "write_l1_carry_supplement" in l1["recommendation"]


def test_l1_checker_full_rec1_t1_no_action(tmp_path):
    body = {
        "schema_id": "test",
        "candidate_record_id": "x",
        "rec1_t1_binding_text_verbatim": (
            "REC1_T1 (binding): Under the L1 epistemic-discount framework..."
        ),
        "cross_references_binding": {
            "l1_gap_addendum": {
                "commit": "e2ae683",
                "seal_sha256": "769eac9954e3da940d09913b63a6095e2d807da9f7b4d3291d7dc67236a64055",
                "json_path": "reports/external_research_hunter/x_draft_l1_gap_closure_addendum_sealed.json",
            },
        },
    }
    p = tmp_path / "supplement.json"
    _write_sealed_report(p, body)
    l1 = l1_checker.check_l1(p)
    assert l1["status"] == L1_FULL
    assert l1["rec1_t1_hits"] >= 1
    assert l1["needs_supplement"] is False


# --- Test 6: detecting duplicate chain anchor -----------------------------


def test_anchor_verifier_flags_duplicate_chain(tmp_path):
    body = {
        "schema_id": "test",
        "candidate_record_id": "x",
        "parent_references": {
            # Pretend this report anchors a SEAL-B duplicate-chain commit
            "p3_build_commit": "b97331a",  # known SEAL-B P3-B
            "tier_n_spec_commit": "9ce4d66",  # known SEAL-B SEAL
        },
    }
    p = tmp_path / "report.json"
    _write_sealed_report(p, body)
    result = anchor_verifier.verify_anchors(
        p,
        canonical_chain=["66bbbd1", "d8bd359", "0b8d948", "91e740e"],  # SEAL-A chain
        duplicate_chain=["9ce4d66", "bd7245e", "2b27acc", "b97331a"],  # SEAL-B chain
    )
    assert result["risk"] == "HIGH"
    assert set(result["anchors_in_duplicate"]) == {"9ce4d66", "b97331a"}


def test_phase_classifier_detects_duplicate_chain():
    # Files using SEAL-B short-slug convention (no `external_research_hunter`, no `databento_long_history`)
    files = [
        "reports/s12_d1_p11_lifecycle_memo_sealed.json",
        "reports/s12_d1_p11_lifecycle_memo_sealed.md",
    ]
    assert phase_classifier.classify("Some subject", files) == "DUPLICATE_CHAIN"


# --- Test 7: verifying seal hash ------------------------------------------


def test_seal_verifier_pass(tmp_path, sample_p6_pass_body):
    p = tmp_path / "report.json"
    _write_sealed_report(p, sample_p6_pass_body)
    result = seal_verifier.verify_seal(p)
    assert result["status"] == "PASS"
    assert result["declared"] == result["recomputed"]


def test_seal_verifier_fail_on_tamper(tmp_path, sample_p6_pass_body):
    p = tmp_path / "report.json"
    _write_sealed_report(p, sample_p6_pass_body)
    # Tamper with a non-seal field
    body = json.loads(p.read_text(encoding="utf-8"))
    body["performance_summary"]["closed_trades_count"] = 9999
    p.write_text(json.dumps(body, indent=2), encoding="utf-8")
    result = seal_verifier.verify_seal(p)
    assert result["status"] == "FAIL"
    assert result["declared"] != result["recomputed"]


def test_seal_verifier_missing_field(tmp_path):
    p = tmp_path / "no_seal.json"
    p.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")
    result = seal_verifier.verify_seal(p)
    assert result["status"] == "MISSING"


# --- Test 8: preserving lessons.md guard -----------------------------------


def test_lessons_md_guard_refuses_commit(tmp_repo):
    # Simulate lessons.md as a tracked file modified in working tree + staged
    lessons = tmp_repo / "brain_memory" / "projects" / "trading_bot" / "lessons.md"
    lessons.parent.mkdir(parents=True, exist_ok=True)
    lessons.write_text("initial\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_repo), "add", str(lessons.relative_to(tmp_repo))], check=True)
    subprocess.run(["git", "-C", str(tmp_repo), "commit", "-q", "-m", "add lessons"], check=True)
    lessons.write_text("dirty\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_repo), "add", str(lessons.relative_to(tmp_repo))], check=True)

    # safe_executor must refuse any commit while lessons.md is staged
    result = safe_executor.execute_commit_exact_paths(
        tmp_repo,
        ["brain_memory/projects/trading_bot/lessons.md"],
        "evil",
        approval_level=2,
    )
    assert result.status == "REFUSED"
    msg = (result.refused_because or "").lower()
    # Either guard string fires (`protected path` is the first-line guard,
    # `hard-guarded` is the substring-match fallback); both are safe.
    assert "protected" in msg or "hard-guarded" in msg
    # And lessons.md path must appear in the refusal reason
    assert "lessons.md" in msg


def test_lessons_md_guard_refuses_via_unstage(tmp_repo):
    """Even index-only unstage of lessons.md is refused."""
    result = safe_executor.execute_unstage_exact(
        tmp_repo,
        ["brain_memory/projects/trading_bot/lessons.md"],
        approval_level=1,
    )
    assert result.status == "REFUSED"
    assert "protected" in (result.refused_because or "")


# --- Test 9: safe_executor exact-path commit only -------------------------


def test_safe_executor_commits_exactly_two_files(tmp_repo):
    a = tmp_repo / "a.json"
    b = tmp_repo / "b.md"
    a.write_text("{}", encoding="utf-8")
    b.write_text("# b\n", encoding="utf-8")

    # Pre-flight: index must be clean
    assert git_sentinel.staged_files(tmp_repo) == []

    result = safe_executor.execute_commit_exact_paths(
        tmp_repo, ["a.json", "b.md"], "test commit", approval_level=2,
    )
    assert result.status == "OK"
    assert set(result.artifacts["committed_paths"]) == {"a.json", "b.md"}
    # New HEAD exists
    new_head = result.artifacts["new_head_sha"]
    assert len(new_head) == 40  # full sha
    # The commit changed exactly 2 files
    show = subprocess.run(
        ["git", "-C", str(tmp_repo), "show", "--name-only", "--format=", new_head],
        check=True, capture_output=True, text=True,
    ).stdout
    files = [ln for ln in show.splitlines() if ln.strip()]
    assert set(files) == {"a.json", "b.md"}


def test_safe_executor_real_diagnostic_always_refused(tmp_repo):
    """LEVEL_3 actions (P6/P10/fetch/broker) are always refused by orchestrator."""
    from sparta_commander.research_orchestrator.safe_executor import dispatch
    for evil_action in ["RUN_P6_IS_DIAGNOSTIC", "FETCH_DATABENTO", "RUN_P10_OOS_GATE", "BROKER_CALL"]:
        result = dispatch(evil_action, {"reason": "test"}, approval_level=3, repo=tmp_repo)
        assert result.status == "REFUSED"


# --- Test 10: pending decision JSON creation ------------------------------


def test_pending_decision_created_for_k9_fail(tmp_path):
    storage = Storage(tmp_path / "rs")
    state = CandidateState(
        candidate_id="s99-d1-test",
        current_phase=PHASE_P6_IS,
        latest_verdict="INSUFFICIENT_SAMPLE",
        closed_trades_observed=48,
        k9_threshold=100,
        k9_status=K9_FAIL,
        rec1_t1_carry_status=L1_PARTIAL,
    )
    decisions = decision_engine.evaluate(state)
    assert len(decisions) >= 2
    actions = [d["action"] for d in decisions]
    assert "ACCEPT_AND_PARK" in actions
    assert "AUTHORIZE_P11_PARK_MEMO" in actions
    assert "WRITE_L1_CARRY_SUPPLEMENT" in actions
    # Round-trip one through storage
    p = storage.save_pending_decision(decisions[0])
    assert p.exists()
    loaded = storage.list_pending_decisions()
    assert any(d["action"] == decisions[0]["action"] for d in loaded)


def test_pending_decision_for_k9_pass_recommends_p6_5(tmp_path):
    state = CandidateState(
        candidate_id="s99-d1-test",
        current_phase=PHASE_P6_IS,
        latest_verdict="READY_FOR_LONGER_BACKTEST",
        closed_trades_observed=159,
        k9_threshold=100,
        k9_status=K9_PASS,
        rec1_t1_carry_status=L1_FULL,
    )
    audit = {"annual_turnover": 84.79, "trades_per_year_observed": 34.34}
    decisions = decision_engine.evaluate(state, latest_audit=audit)
    actions = [d["action"] for d in decisions]
    assert "AUTHORIZE_P6_5_COST_STRESS" in actions
    # Implied OOS K9 fail (34.34 * 2 < 100) should also propose ACCEPT_AND_PARK
    assert "ACCEPT_AND_PARK" in actions
