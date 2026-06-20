"""Tests for the Candidate #22 detector-spec + synthetic dry-run contract
(external_signum_trend_radar_gc_long_short_v1).

Verifies: research-only, detector-dry-run-only, executes nothing; chain-gated on the
frozen C22 spec (verdict + pinned commit a6b28da1); SYNTHETIC fixtures only (no real
candles, no fetch, no connection); detector parameters single-sourced from the frozen spec
with every value matching and none invented; and every spec branch validated on
known-truth fixtures -- long entry (upper-band crossover, 8%/2% breakout sizing), long
exit (below band / out-of-radar), hedge short (Red + cross-down-filter 3%), bear short
(BTC downtrend + Red + high>=0.98x filter + close<filter 5%), short exits (stop /
0.65x take-profit / out), already-held + one-position-per-coin skip, held-dust (<$10)
entry exception, entry-dust skip, ticker-collision (>0.5) skip, BTC-absent resolution
(downtrend False -> bear off, hedge on), market-rank validity, perpetual precondition,
>=50 line-item gate, and NAV-snapshot order sizing (never reuse %, cap 100). Plus
capability flags + scope locks, validator anti-tamper, and module purity."""
from __future__ import annotations

import ast

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_detector_spec_dry_run_contract as d22  # noqa: E501


_R = d22.build_c22_detector_dry_run()


# ---- core: research-only, dry-run-only, validates --------------------------

def test_dry_run_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_detector_dry_run_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C22_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert d22.validate_c22_detector_dry_run(_R)["valid"] is True


def test_chain_gated_on_frozen_spec():
    assert _R["spec_valid"] is True
    assert _R["spec_verdict"] == "C22_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["chain_gated_on_c22_spec"] is True
    assert _R["spec_commit"] == "a6b28da1a4190fa16577f1dcdf872b4fecf9d62b"
    bad = {**_R, "spec_commit": "0" * 40}
    assert d22.validate_c22_detector_dry_run(bad)["valid"] is False
    bad2 = {**_R, "spec_verdict": "X"}
    assert d22.validate_c22_detector_dry_run(bad2)["valid"] is False


# ---- synthetic-only + params single-sourced from frozen spec ---------------

def test_synthetic_only_and_params_single_sourced():
    assert _R["uses_synthetic_fixtures_only"] is True
    assert _R["runs_on_real_candles"] is False
    assert _R["params_single_sourced_from_frozen_spec"] is True
    assert _R["no_values_invented"] is True
    p = _R["detector_params"]
    assert p["min_line_items"] == 50 and p["max_fetch_retries"] == 3
    assert p["top_n_rows"] == 50 and p["breakout_recent_days"] == 25
    assert p["long_size_recent_pct"] == 8.0 and p["long_size_else_pct"] == 2.0
    assert p["hedge_short_pct"] == 3.0 and p["bear_short_pct"] == 5.0
    assert p["bear_high_multiple"] == 0.98 and p["short_take_profit_multiple"] == 0.65
    assert p["collision_threshold"] == 0.5
    assert p["entry_dust_pct_nav"] == 1.0 and p["entry_dust_usd"] == 10
    assert p["exit_dust_usd"] == 10 and p["held_dust_usd"] == 10
    assert p["leverage"] == 1
    bad = {**_R, "detector_params": {**p, "short_take_profit_multiple": 0.7}}
    assert d22.validate_c22_detector_dry_run(bad)["valid"] is False


# ---- all 15 synthetic fixtures self-verify ---------------------------------

def test_all_fixtures_pass():
    assert _R["all_fixtures_pass"] is True
    dry = _R["dry_run_results"]
    assert len(dry) == 15
    for name, v in dry.items():
        assert v["all_pass"] is True, name
    # tamper: a failed fixture -> invalid
    bad_dry = {k: dict(v) for k, v in dry.items()}
    bad_dry["hedge_short_3pct"] = {**bad_dry["hedge_short_3pct"], "all_pass": False}
    bad = {**_R, "dry_run_results": bad_dry, "all_fixtures_pass": False}
    assert d22.validate_c22_detector_dry_run(bad)["valid"] is False


# ---- direct detector behaviour: LONG entry + sizing ------------------------

def test_long_entry_upper_band_crossover_and_breakout_sizing():
    fx = d22.build_synthetic_fixtures()
    r = d22.run_detector(fx["long_entry_recent_8pct"])
    assert len(r["long_entries"]) == 1
    e = r["long_entries"][0]
    assert e["side"] == "LONG" and e["target_position_size_sign"] == 1
    assert e["size_pct_nav"] == 8.0 and e["breakout_recent"] is True
    assert e["leverage"] == 1
    assert e["reason"] == "crossover_up_through_upper_gc_band"
    r2 = d22.run_detector(fx["long_entry_else_2pct"])
    assert r2["long_entries"][0]["size_pct_nav"] == 2.0
    assert r2["long_entries"][0]["breakout_recent"] is False


# ---- direct detector behaviour: exits --------------------------------------

def test_long_and_short_exits():
    fx = d22.build_synthetic_fixtures()
    le = d22.run_detector(fx["long_exit_below_band_and_out"])
    assert {e["symbol"] for e in le["long_exits"]} == {"HELDL", "GONE"}
    assert all(e["close_pct"] == 100 and e["target_position_size"] == 0
               for e in le["long_exits"])
    se = d22.run_detector(fx["short_exit_stop_tp_out"])
    reasons = {e["reason"] for e in se["short_exits"]}
    assert "stop_close_above_gc_filter" in reasons
    assert "take_profit_close_le_0_65x_entry" in reasons
    assert "out_of_trend_radar" in reasons
    tp = next(e for e in se["short_exits"]
              if e["reason"] == "take_profit_close_le_0_65x_entry")
    assert tp["derived_entry_price"] == 10.0   # (100+0)/10


# ---- direct detector behaviour: hedge vs bear shorts + BTC regime ----------

def test_hedge_and_bear_shorts_and_btc_regime():
    fx = d22.build_synthetic_fixtures()
    h = d22.run_detector(fx["hedge_short_3pct"])
    assert len(h["short_entries"]) == 1
    assert h["short_entries"][0]["kind"] == "hedge"
    assert h["short_entries"][0]["size_pct_nav"] == 3.0
    assert h["short_entries"][0]["target_position_size_sign"] == -1
    b = d22.run_detector(fx["bear_short_5pct"])
    assert b["btc"]["downtrend"] is True
    bears = [s for s in b["short_entries"] if s["kind"] == "bear"]
    assert len(bears) == 1 and bears[0]["size_pct_nav"] == 5.0


def test_btc_absent_disables_bear_but_hedge_still_fires():
    fx = d22.build_synthetic_fixtures()
    r = d22.run_detector(fx["btc_absent_disables_bear_hedge_ok"])
    assert r["btc"]["present"] is False
    assert r["btc"]["downtrend"] is False           # human resolution
    assert all(s["kind"] != "bear" for s in r["short_entries"])
    assert any(s["kind"] == "hedge" for s in r["short_entries"])


# ---- direct detector behaviour: skips, dust, collision, market-rank --------

def test_held_active_skip_vs_held_dust_entry():
    fx = d22.build_synthetic_fixtures()
    r = d22.run_detector(fx["held_active_skip_vs_held_dust_entry"])
    # ACTV held >=$10 -> skipped (one position per coin)
    assert any(s["symbol"] == "ACTV" and s["stage"] == "long_entry"
               and s["reason"] == "already_held_or_touched_this_run"
               for s in r["skips"])
    # DUSTH held <$10 -> dust exception lets a new entry through
    assert any(e["symbol"] == "DUSTH" for e in r["long_entries"])


def test_entry_dust_and_collision_and_missing_indicator_skips():
    fx = d22.build_synthetic_fixtures()
    dd = d22.run_detector(fx["entry_dust_skip"])
    assert dd["long_entries"] == []
    assert any(s["reason"] == "dust_below_entry_threshold" for s in dd["skips"])
    cc = d22.run_detector(fx["ticker_collision_skip"])
    assert cc["long_entries"] == []
    assert any("ticker_collision" in s["reason"] for s in cc["skips"])
    mi = d22.run_detector(fx["missing_indicator_skip"])
    assert mi["long_entries"] == []
    assert any(s["reason"] == "missing_indicator_data" for s in mi["skips"])


def test_market_rank_validity_and_perpetual_precondition():
    fx = d22.build_synthetic_fixtures()
    mr = d22.run_detector(fx["market_rank_invalid_skips_entries"])
    assert mr["market_rank_valid"] is False
    assert mr["entries_invalid_no_market_rank"] is True
    assert mr["long_entries"] == [] and mr["short_entries"] == []
    npr = d22.run_detector(fx["not_perpetual_aborts"])
    assert npr["aborted_not_perpetual"] is True
    assert npr["long_entries"] == [] and npr["short_entries"] == []


# ---- direct detector behaviour: NAV-snapshot order sizing ------------------

def test_nav_snapshot_order_sizing_never_reuses_pct():
    fx = d22.build_synthetic_fixtures()
    r = d22.run_detector(fx["nav_snapshot_two_entries"])
    sim = r["order_sizing_simulation"]
    assert len(sim) == 2
    assert r["nav_recomputed_midrun"] is False
    # quote balance decrements after each simulated order
    assert sim[1]["quote_balance_after"] < sim[0]["quote_balance_after"]
    # the percentage is recomputed against the CURRENT balance -> never reused
    assert sim[0]["ordersize_pct_of_quote"] != sim[1]["ordersize_pct_of_quote"]
    # NAV snapshot is the starting quote balance and is not recomputed
    assert r["nav_snapshot"] == 1000.0


def test_insufficient_line_items_flagged():
    fx = d22.build_synthetic_fixtures()
    r = d22.run_detector(fx["insufficient_line_items"])
    assert r["data_quality"]["sufficient"] is False
    assert r["data_quality"]["min_required"] == 50
    assert r["data_quality"]["max_fetch_retries"] == 3


# ---- no execution / connection ---------------------------------------------

def test_no_execution_no_connection_locks():
    for flag in ("executes", "runs_detector_on_real_candles", "runs_labels",
                 "runs_replay", "fetches_data", "connects_signum", "uses_mcp",
                 "accesses_hyperliquid", "uses_api_keys", "uses_credentials",
                 "sends_email", "edits_bots", "sets_trading_pair", "converts_funds",
                 "sends_signal", "sends_trades", "places_orders", "creates_claude_routines",
                 "paper_trading", "live_trading", "installs_scheduler",
                 "invents_rule_values"):
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert d22.validate_c22_detector_dry_run(bad)["valid"] is False, flag


# ---- gate sequence + downstream locked + advances nothing ------------------

def test_gate_sequence_and_downstream_locked():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    nra = d22.get_candidate_22_detector_dry_run_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"
    assert _R["advances_nothing"] is True
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert d22.validate_c22_detector_dry_run(bad)["valid"] is False, gate


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(d22.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "datetime", "random", "numpy", "pandas"}
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
