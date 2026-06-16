"""Tests for the Candidate #10 robustness / sensitivity evaluation review /
evidence-freeze contract (INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1).

Verifies: chain-gate on the pushed FROZEN replay-results review; frozen SHA pins
of the replay ledger + the untracked robustness artifact; the frozen robustness
findings (cost stress 37/50/75/100 bps, per-year + half sub-period, drawdown,
horizon 3/5/7/10, regime 2025); the HONEST disposition (cost-robust + horizon-
robust BUT front-loaded/decaying with negative 2025 -> WARNING, KEEP FOR
RESEARCH, promotion to paper/live BARRED); all downstream gates locked; no
profitability claim; the robustness artifact remains untracked; AST/purity green.

Optimization: the shared C10 build chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.intraweek_calendar_seasonality_drift_v1_robustness_review_contract as c10rob  # noqa: E501


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
    _R = c10rob.build_c10_robustness_review(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + frozen verdict -------------------------------------------

def test_review_frozen_and_validates():
    assert _R["verdict"] == c10rob.VERDICT_C10ROB_FROZEN
    assert _R["blockers"] == []
    assert _R["replay_review_verdict"] == c10rob.VERDICT_C10RR_FROZEN
    assert c10rob.validate_c10_robustness_review(_R)["valid"] is True


def test_verdict_is_one_of_allowed():
    assert c10rob.VERDICT_C10ROB_FROZEN == "C10_ROBUSTNESS_FROZEN_FOR_HUMAN_REVIEW"
    assert c10rob.VERDICT_C10ROB_REJECTED == "C10_REJECTED_AFTER_ROBUSTNESS_REVIEW"
    assert c10rob.VERDICT_C10ROB_INCONCLUSIVE == "C10_ROBUSTNESS_INCONCLUSIVE"
    assert _R["verdict"] in (c10rob.VERDICT_C10ROB_FROZEN,
                             c10rob.VERDICT_C10ROB_REJECTED,
                             c10rob.VERDICT_C10ROB_INCONCLUSIVE)


def test_sha_pins_frozen():
    assert _R["expected_replay_ledger_sha256"] == (
        c10rob.EXPECTED_REPLAY_LEDGER_SHA256)
    assert _R["expected_robustness_sha256"] == c10rob.EXPECTED_ROBUSTNESS_SHA256
    assert _R["head_at_replay_review"] == (
        "9a03e638610c371efe8bde1255f958277f7b5bbe")
    for field in ("expected_replay_ledger_sha256",
                  "expected_robustness_sha256", "head_at_replay_review"):
        bad = copy.deepcopy(_R)
        bad[field] = "0" * 64 if "sha" in field else "deadbeef"
        assert c10rob.validate_c10_robustness_review(bad)["valid"] is False, field


# ---- 1. cost stress --------------------------------------------------------

def test_cost_stress_survival():
    cs = _R["cost_stress_net_r"]
    # all variants net positive through 75 bps
    for name in ("2r", "3r", "4r"):
        assert cs[name]["37"] > 0
        assert cs[name]["50"] > 0
        assert cs[name]["75"] > 0
    # 2r turns negative at 100 bps; 3r/4r survive 100 bps
    assert cs["2r"]["100"] < 0
    assert cs["3r"]["100"] > 0
    assert cs["4r"]["100"] > 0
    sf = _R["survival_flags"]
    assert sf["survives_cost_75bps_all_variants"] is True
    assert sf["survives_cost_100bps_all_variants"] is False
    assert sf["survives_cost_100bps_3r_and_4r"] is True
    assert _R["survives_realistic_cost_stress"] is True


# ---- 2. sub-period + front-loading ----------------------------------------

def test_sub_period_decay_and_front_loading():
    sub = _R["sub_period_net_r"]
    for name in ("2r", "3r", "4r"):
        # monotonic decline 2023 > 2024 > 2025, with 2025 negative
        assert sub[name]["2023"] > sub[name]["2024"] > sub[name]["2025"]
        assert sub[name]["2025"] < 0
        # front-loaded: first half dominates second half
        assert sub[name]["first_half"] > sub[name]["second_half"]
    # tampering away the 2025 negativity invalidates
    bad = copy.deepcopy(_R)
    bad["sub_period_net_r"]["3r"]["2025"] = 5.0
    assert c10rob.validate_c10_robustness_review(bad)["valid"] is False


# ---- 3/4. variant + horizon robustness ------------------------------------

def test_horizon_robustness_all_positive_canonical_strongest():
    hs = _R["horizon_sensitivity_net_r"]
    for name in ("2r", "3r", "4r"):
        for h in ("h3", "h5", "h7", "h10"):
            assert hs[name][h] > 0
        # canonical 5-bar horizon is the strongest
        assert hs[name]["h5"] == max(hs[name].values())
    assert _R["survival_flags"]["all_horizons_3_to_10_net_positive_all_variants"] is True
    assert _R["survival_flags"]["canonical_5bar_horizon_is_strongest"] is True
    bad = copy.deepcopy(_R)
    bad["horizon_sensitivity_net_r"]["2r"]["h7"] = -1.0
    assert c10rob.validate_c10_robustness_review(bad)["valid"] is False


# ---- 5. drawdown -----------------------------------------------------------

def test_drawdown_worst_periods_in_2025():
    dd = _R["drawdown"]
    for name in ("2r", "3r", "4r"):
        assert dd[name]["max_drawdown_r"] > 0
        assert dd[name]["worst_losing_streak_trades"] == 6
        assert dd[name]["worst_year"][0] == "2025"
        assert dd[name]["worst_quarter"][0].startswith("2025")
        assert dd[name]["worst_month"][0].startswith("2025")


# ---- 6. regime decay 2025 --------------------------------------------------

def test_regime_2025_explained_elevated_stops_drift_still_positive():
    r = _R["regime_decay_2025"]
    for name in ("2r", "3r", "4r"):
        assert r[name]["net_r_total"] < 0
        assert r[name]["miss"] == 13               # elevated stop-outs
        # the 5-day horizon drift itself stayed mildly POSITIVE in 2025
        assert r[name]["horizon_exit_mean_gross_r"] > 0
    assert _R["decay_2025_classification"] == (
        "WARNING_NOT_BLOCKER_NOT_AUTOREJECTION")
    assert _R["decay_2025_is_warning"] is True
    assert _R["decay_2025_is_blocker"] is False
    assert _R["decay_2025_is_auto_rejection"] is False


# ---- disposition + locks ---------------------------------------------------

def test_disposition_keep_for_research_promotion_barred():
    assert _R["recommended_disposition"] == (
        "KEEP_FOR_FURTHER_RESEARCH_ONLY_DO_NOT_PROMOTE_TO_PAPER_OR_LIVE")
    assert _R["promotion_to_paper_or_live_barred"] is True
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C10_KEEP_FOR_FURTHER_RESEARCH_OR_REJECT")
    bad = copy.deepcopy(_R)
    bad["promotion_to_paper_or_live_barred"] = False
    assert c10rob.validate_c10_robustness_review(bad)["valid"] is False


def test_all_downstream_gates_locked():
    assert _R["is_robustness_review_only"] is True
    assert _R["current_loop_stage"] == "robustness_sensitivity_review"
    assert _R["human_review_required"] is True
    for key in ("relabel_gate_locked", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked"):
        assert _R[key] is True, key
    for key, val in _R["scope_locks"].items():
        assert val is True, key


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c10rob._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c10rob.validate_c10_robustness_review(bad)["valid"] is False, flag


def test_no_fitting_no_weekday_change_no_optimization_locks():
    for flag in ("fits_parameters", "changes_weekday", "optimizes",
                 "selects_best_cell_as_promotion"):
        assert _R[flag] is False, flag
    for lock in ("no_parameter_fitting", "no_weekday_change"):
        assert _R["scope_locks"][lock] is True


def test_claim_locks_and_label():
    for required in ("no_profitability_claim", "no_paper_approval",
                     "no_live_approval", "no_capital_deployment",
                     "promotion_to_paper_or_live_barred",
                     "regime_decay_2025_disclosed_as_warning",
                     "no_best_cell_selected_as_promotion"):
        assert required in _R["claim_locks"], required
    label = c10rob.get_candidate_10_robustness_review_label()
    assert "RESEARCH ONLY" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    assert "KEEP FOR FURTHER RESEARCH ONLY" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "EDGE CONFIRMED",
                   "PROFITABLE", "GUARANTEE", "DEPLOY CAPITAL"):
        assert banned not in label.upper(), banned


def test_honest_caveats_present():
    joined = " || ".join(_R["honest_caveats"]).lower()
    assert "not a profitability claim" in joined
    assert "front-loaded" in joined and "decaying" in joined
    assert "elevated stop-outs" in joined
    assert "single asset" in joined


# ---- artifact remains untracked --------------------------------------------

def test_robustness_artifact_remains_untracked():
    tracked = _tracked_paths()
    assert c10rob.ROBUSTNESS_PATH not in tracked
    for p in tracked:
        assert not p.startswith(
            "data/intraweek_calendar_seasonality_c10/robustness_eval/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c10rob.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib"}
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
