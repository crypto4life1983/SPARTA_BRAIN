"""Tests for the Candidate #10 formal rejection / closeout record contract.

Verifies: chain-gate on the pushed C10 generalization review (must be
DOES_NOT_GENERALIZE); verdict REJECTED_KEPT_ON_RECORD; not an active candidate;
the full pushed evidence trail (labels -> replay -> robustness -> generalization)
is cited with 40-hex commit hashes; rejection reasons + kept-on-record-as
lesson present; all downstream gates locked; no profitability/promotion;
original frozen C10 result unchanged; AST/purity green.

The shared C10 build chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.intraweek_calendar_seasonality_drift_v1_rejection_record_contract as c10rj  # noqa: E501


def _tracked_paths():
    return subprocess.check_output(
        ["git", "ls-files"]).decode("utf-8").splitlines()


def _install_pure_gate_memoization():
    cache: dict = {}
    wrappers: dict = {}
    restore: list = []

    def _make(orig):
        def _wrapped(*args, **kwargs):
            if args or kwargs:
                return orig(*args, **kwargs)
            oid = id(orig)
            if oid not in cache:
                cache[oid] = orig()
            return copy.deepcopy(cache[oid])
        return _wrapped

    def _is_target(fn) -> bool:
        return inspect.isfunction(fn) and (
            fn.__name__.startswith("build_")
            or fn.__name__ == "_recompute_live_dry_run")

    for _mname, _mod in list(sys.modules.items()):
        if _mod is None or not _mname.startswith("sparta_commander"):
            continue
        for _orig in list(vars(_mod).values()):
            if _is_target(_orig) and id(_orig) not in wrappers:
                wrappers[id(_orig)] = _make(_orig)
    for _mname, _mod in list(sys.modules.items()):
        if _mod is None or not _mname.startswith("sparta_commander"):
            continue
        for _attr, _val in list(vars(_mod).items()):
            if inspect.isfunction(_val) and id(_val) in wrappers:
                restore.append((_mod, _attr, _val))
                setattr(_mod, _attr, wrappers[id(_val)])
    return restore


_memo_restore = _install_pure_gate_memoization()
try:
    _R = c10rj.build_c10_rejection_record(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_record_recorded_and_validates():
    assert _R["verdict"] == c10rj.VERDICT_RJ10_RECORDED
    assert _R["blockers"] == []
    assert _R["generalization_review_verdict"] == (
        c10rj.VERDICT_C10GEN_DOES_NOT_GENERALIZE)
    assert c10rj.validate_c10_rejection_record(_R)["valid"] is True


def test_rejection_verdict_wording():
    assert c10rj.VERDICT_RJ10_RECORDED == (
        "C10_REJECTED_KEPT_ON_RECORD_FAILED_GENERALIZATION_GATE")
    assert _R["rejection_status"] == "REJECTED_KEPT_ON_RECORD"


def test_not_active_kept_on_record():
    assert _R["is_active_candidate"] is False
    assert _R["kept_on_record"] is True
    assert _R["keeps_as_active_candidate"] is False
    assert _R["kept_on_record_as"]
    assert _R["current_loop_stage"] == "closed_rejected_kept_on_record"
    bad = copy.deepcopy(_R)
    bad["is_active_candidate"] = True
    assert c10rj.validate_c10_rejection_record(bad)["valid"] is False


# ---- evidence trail cited --------------------------------------------------

def test_full_evidence_trail_cited():
    chain = _R["pushed_evidence_chain"]
    stages = {e["stage"] for e in chain}
    for required in ("detector_labels_review",
                     "fee_slippage_honest_replay_review",
                     "robustness_sensitivity_review",
                     "cross_asset_weekday_forward_oos_generalization_review"):
        assert required in stages, required
    # every stage cites a 40-hex commit hash
    for e in chain:
        assert len(e["commit"]) == 40, e
    # the four known pushed commits are present
    commits = {e["commit"] for e in chain}
    for h in ("0de0f7c1089a9650204a786a983502b34b0417be",
              "9a03e638610c371efe8bde1255f958277f7b5bbe",
              "85e2cd6a4b49ec6e07f74ee920caab23516a14ca",
              "67f6d66379b35b4b0092e9da7b7b494aaf0cbbe5"):
        assert h in commits, h
    bad = copy.deepcopy(_R)
    bad["pushed_evidence_chain"] = [e for e in chain
                                    if e["stage"] != "robustness_sensitivity_review"]
    assert c10rj.validate_c10_rejection_record(bad)["valid"] is False


def test_head_at_generalization_review_pinned():
    assert _R["head_at_generalization_review"] == (
        "67f6d66379b35b4b0092e9da7b7b494aaf0cbbe5")
    bad = copy.deepcopy(_R)
    bad["head_at_generalization_review"] = "deadbeef"
    assert c10rj.validate_c10_rejection_record(bad)["valid"] is False


# ---- rejection reasons + lesson --------------------------------------------

def test_rejection_reasons_and_lesson():
    reasons = " || ".join(_R["rejection_reasons"]).lower()
    assert "general bullish long-drift" in reasons or "general" in reasons
    assert "forward-oos" in reasons and "negative" in reasons
    assert "not a robust tradeable" in reasons
    lesson = " || ".join(_R["kept_on_record_as"]).lower()
    assert "decaying long-drift artifact" in lesson
    assert "research seed" in lesson


def test_evidence_headline_facts():
    h = _R["evidence_headline"]
    assert h["accepted_setups"] == 156
    assert h["cross_weekday_positive_count_of_7"] == 6
    assert h["friday_is_unique_positive_weekday"] is False
    assert h["forward_oos_2026_positive_any_asset"] is False


# ---- locks + capability flags ----------------------------------------------

def test_all_downstream_gates_locked():
    for key in ("relabel_gate_locked", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked"):
        assert _R[key] is True, key
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for lock in ("no_relabel", "no_weekday_reselection", "no_optimization",
                 "no_regime_filter", "no_portfolio_allocation"):
        assert _R["scope_locks"][lock] is True


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c10rj._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c10rj.validate_c10_rejection_record(bad)["valid"] is False, flag


def test_claim_locks_and_label():
    for required in ("no_profitability_claim", "kept_on_record_not_active_candidate",
                     "no_relabel_of_original_result",
                     "no_optimization_or_weekday_reselection"):
        assert required in _R["claim_locks"], required
    label = c10rj.get_candidate_10_rejection_record_label()
    assert "REJECTED_KEPT_ON_RECORD" in label
    assert "NOT AN ACTIVE CANDIDATE" in label
    assert "RESEARCH ONLY" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "GUARANTEE"):
        assert banned not in label.upper(), banned


def test_next_action_closed_record():
    assert _R["next_required_action"] == (
        "NONE__C10_CLOSED__KEPT_ON_RECORD_AS_DECAYING_LONG_DRIFT_RESEARCH_LESSON")


# ---- chain blocks when generalization not failed (BLOCKED branch) ----------

def test_chain_blocks_when_generalization_verdict_changed(monkeypatch):
    """If the generalization review did not return DOES_NOT_GENERALIZE the
    rejection record short-circuits to BLOCKED."""
    monkeypatch.setattr(
        c10rj, "build_c10_generalization_review",
        lambda repo_root, tracked: {"verdict": "SOMETHING_ELSE"})
    blocked = c10rj.build_c10_rejection_record(".", [])
    assert blocked["verdict"] == c10rj.VERDICT_RJ10_BLOCKED
    assert "generalization_review_not_does_not_generalize" in blocked["blockers"]


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c10rj.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime"}
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
