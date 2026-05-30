"""Tests for the Factory-D8 final-decision / readiness orchestration layer.

Covers module-verdict normalization (known + unknown keys), the hard-blocker set,
the conservative research-decision map (continue / park / fail / redesign), the
conservative readiness-level map (blocked -> research -> validation, with paper/live
unreachable on the default path), the standard-schema report builder + write_report
integration, the human-readable ladder summary, an offline-source token scan, and
empty-input safety.

Synthetic verdict dicts only. No real NQ/ES CSVs are read; no strategy is
backtested; no module decides anything beyond combining the supplied verdicts.
"""

import json
import os

from engine import validation_decision as DC
from engine import validation_reports as VR


def _full_acceptable():
    """A full ladder where every module is at its acceptable verdict."""
    return {
        "is_baseline": "IS_CONTINUE",
        "oos": "PASS",
        "entry_significance": "ENTRY_EDGE_SUPPORTED",
        "sequence_risk": "SEQUENCE_RISK_ACCEPTABLE",
        "regime": "REGIME_RISK_ACCEPTABLE",
        "walk_forward": "WALK_FORWARD_STABLE",
        "friction": "FRICTION_ROBUST",
    }


# 1 -- normalize_module_verdicts accepts known keys without warnings.
def test_normalize_accepts_known_keys():
    out = DC.normalize_module_verdicts({"is_baseline": "IS_CONTINUE", "oos": "PASS"})
    assert out["normalized"] == {"is_baseline": "IS_CONTINUE", "oos": "PASS"}
    assert out["warnings"] == []
    assert out["unknown_keys"] == []


# 2 -- normalize_module_verdicts warns on (but retains) unknown keys.
def test_normalize_warns_on_unknown_keys():
    out = DC.normalize_module_verdicts({"mystery_module": "WHATEVER"})
    assert out["unknown_keys"] == ["mystery_module"]
    assert any("unknown module key" in w for w in out["warnings"])
    assert out["normalized"]["mystery_module"] == "WHATEVER"


# 3 -- IS_FAIL gives FAIL_CANDIDATE and BLOCKED.
def test_is_fail_gives_fail_and_blocked():
    v = {"is_baseline": "IS_FAIL"}
    assert DC.derive_research_decision(v) == DC.FAIL_CANDIDATE
    assert DC.derive_readiness_level(v) == DC.BLOCKED


# 4 -- OOS FAIL gives FAIL_CANDIDATE and BLOCKED.
def test_oos_fail_gives_fail_and_blocked():
    v = {"is_baseline": "IS_CONTINUE", "oos": "OOS_FAIL"}
    assert DC.derive_research_decision(v) == DC.FAIL_CANDIDATE
    assert DC.derive_readiness_level(v) == DC.BLOCKED


# 5 -- OOS PASS but incomplete risk modules stays RESEARCH_CANDIDATE.
def test_oos_pass_incomplete_risk_stays_research():
    v = {"is_baseline": "IS_CONTINUE", "oos": "PASS",
         "entry_significance": "ENTRY_EDGE_SUPPORTED"}
    assert DC.hard_blockers(v) == []
    assert DC.derive_readiness_level(v) == DC.RESEARCH_CANDIDATE


# 6 -- OOS PASS + every core risk acceptable gives VALIDATION_CANDIDATE.
def test_oos_pass_full_core_gives_validation():
    assert DC.derive_readiness_level(_full_acceptable()) == DC.VALIDATION_CANDIDATE


# 7 -- multiple inconclusive core modules gives PARK_CANDIDATE.
def test_multiple_inconclusive_gives_park():
    v = {
        "is_baseline": "IS_CONTINUE", "oos": "PASS",
        "entry_significance": "ENTRY_EDGE_SUPPORTED",
        "sequence_risk": "SEQUENCE_RISK_INCONCLUSIVE",
        "regime": "REGIME_RISK_INCONCLUSIVE",
        "walk_forward": "WALK_FORWARD_INCONCLUSIVE",
        "friction": "FRICTION_SENSITIVE",
    }
    assert DC.hard_blockers(v) == []
    assert DC.derive_research_decision(v) == DC.PARK_CANDIDATE


# 8 -- a fragile trade sequence is a hard blocker -> PARK_CANDIDATE (not fail).
def test_sequence_fragile_gives_park():
    v = dict(_full_acceptable())
    v["sequence_risk"] = "SEQUENCE_RISK_FRAGILE"
    assert "SEQUENCE_RISK_FRAGILE: trade-sequence fragility" in DC.hard_blockers(v)
    assert DC.derive_research_decision(v) == DC.PARK_CANDIDATE
    # ...unless a redesign hint is supplied, then REDESIGN_REQUIRED.
    assert DC.derive_research_decision(v, {"redesign_hint": True}) == DC.REDESIGN_REQUIRED


# 9 -- entry edge not supported plus another weakness blocks promotion.
def test_entry_not_supported_plus_weakness_blocks():
    v = {
        "is_baseline": "IS_CONTINUE", "oos": "PASS",
        "entry_significance": "ENTRY_EDGE_NOT_SUPPORTED",
        "sequence_risk": "SEQUENCE_RISK_FRAGILE",
    }
    blockers = DC.hard_blockers(v)
    assert any("ENTRY_EDGE_NOT_SUPPORTED" in b for b in blockers)
    assert DC.derive_readiness_level(v) == DC.BLOCKED


# 10 -- with no OOS pass yet, readiness never exceeds RESEARCH_CANDIDATE.
def test_no_oos_caps_at_research():
    v = dict(_full_acceptable())
    del v["oos"]
    assert DC.derive_readiness_level(v) == DC.RESEARCH_CANDIDATE


# 11 -- paper/live levels are unreachable without an explicit separate-memo flag.
def test_paper_live_unreachable_without_memo():
    v = _full_acceptable()
    # Default path: no paper/live, only VALIDATION_CANDIDATE.
    assert DC.derive_readiness_level(v) == DC.VALIDATION_CANDIDATE
    # Passed paper gates lift to PAPER_REVIEW_CANDIDATE -- still not paper/live ready.
    rl = DC.derive_readiness_level(v, {"paper_review_gates_passed": True})
    assert rl == DC.PAPER_REVIEW_CANDIDATE
    assert rl not in (DC.PAPER_READY, DC.LIVE_READY)
    # The override fields DO reach them, proving the gate is real (not used by default).
    assert DC.derive_readiness_level(
        v, {"paper_review_gates_passed": True,
            "paper_ready_override": True, "paper_ready_memo_commit": "deadbeef"}
    ) == DC.PAPER_READY


# 12 -- build_decision_report returns a valid D2-schema report.
def test_build_report_valid_schema():
    rep = DC.build_decision_report(
        branch_id="S99",
        title="Synthetic Final Decision",
        verdicts=_full_acceptable(),
        source_commits={"engine": "deadbeef"},
        input_files=["data/synthetic_trades.json"],
        data_window={"years": [2020]},
        created_utc="2026-05-30T00:00:00+00:00",
    )
    assert VR.validate_report(rep) == []
    assert rep["module_id"] == "final_decision"
    assert rep["next_allowed_step"] == "human_review"
    assert rep["verdict"] == DC.CONTINUE_RESEARCH
    assert rep["metrics"]["readiness_level"] == DC.VALIDATION_CANDIDATE
    assert "no_auto_promotion" in rep["forbidden_actions"]
    assert "no_paper_or_live" in rep["forbidden_actions"]


# 13 -- write_report integration produces report.json + report.md.
def test_write_report_integration(tmp_path):
    rep = DC.build_decision_report(
        branch_id="S99",
        title="Synthetic Final Decision",
        verdicts={"is_baseline": "IS_FAIL"},
        created_utc="2026-05-30T00:00:00+00:00",
    )
    dest = str(tmp_path / "rep")
    paths = VR.write_report(rep, dest)
    assert os.path.isfile(paths["report_json"])
    assert os.path.isfile(paths["report_md"])
    with open(paths["report_json"], "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    assert loaded["verdict"] == DC.FAIL_CANDIDATE
    assert loaded["metrics"]["readiness_level"] == DC.BLOCKED


# 14 -- the ladder summary includes module names and their verdicts.
def test_summary_includes_modules_and_verdicts():
    s = DC.summarize_validation_ladder(_full_acceptable())
    assert "is_baseline: IS_CONTINUE" in s
    assert "friction: FRICTION_ROBUST" in s
    # unknown keys are surfaced, not hidden.
    s2 = DC.summarize_validation_ladder({"mystery": "X"})
    assert "mystery: X (unknown module)" in s2


# 15 -- module source is offline/inert (no network/broker/dynamic-exec/VC tokens).
def test_module_source_is_offline_inert():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_decision.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "subprocess", "socket", "urllib", "requests", "httpx", "aiohttp",
        "websockets", "ccxt", "binance", "bybit", "alpaca", "ib_insync",
        "broker", "api_key", "os.system", "exec(", "eval(",
        "importlib", "__import__", "git",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in module source: {hits}"


# 16 -- empty verdict dict is handled safely / conservatively.
def test_empty_verdicts_handled_conservatively():
    assert DC.hard_blockers({}) == []
    assert DC.derive_research_decision({}) == DC.PARK_CANDIDATE
    assert DC.derive_readiness_level({}) == DC.RESEARCH_CANDIDATE
    assert DC.summarize_validation_ladder({}) == "(no module verdicts supplied)"
    out = DC.normalize_module_verdicts({})
    assert out == {"normalized": {}, "warnings": [], "unknown_keys": []}
