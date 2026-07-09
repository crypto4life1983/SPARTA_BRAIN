"""Tests for the C26 Little RZY measured-move / trendline geometry SPEC-ONLY contract.

Verifies the spec is research-only, spec-only, defines no entry rule, keeps the rejected
entry mechanisms INHERITED_BLOCKED, freezes constants without optimization, carries the full
pre-committed failure rule, and pins every capability flag False. Also verifies the
anti-tamper validator rejects weakened records.
"""
import sparta_commander.c26_little_rzy_measured_move_trendline_geometry_spec_contract as g


def test_spec_builds_and_validates():
    rec = g.build_geometry_spec()
    assert rec["verdict"] == g.VERDICT_SPEC_FROZEN
    assert not rec["blockers"]
    assert g.validate_geometry_spec(rec)["valid"] is True


def test_spec_is_spec_only_no_entry_no_activation():
    rec = g.build_geometry_spec()
    assert rec["is_spec_only"] is True
    assert rec["is_candidate"] is False and rec["is_proposal"] is False
    assert rec["entry_rule_defined"] is False
    assert rec["reopens_rejected_entry_families"] is False
    assert rec["optimization_permitted"] is False
    assert rec["constants_frozen_before_test"] is True


def test_all_capability_flags_false():
    rec = g.build_geometry_spec()
    for flag in g._CAPABILITY_FLAGS_FALSE:
        assert rec[flag] is False, flag
    # spot-check the safety-critical ones explicitly
    for flag in ("builds_labels", "runs_replay", "fetches_data", "optimizes_parameters",
                 "activates_candidate", "live_trading", "paper_trading", "places_orders",
                 "modifies_c22", "modifies_ledgers", "relaxes_safety_gate",
                 "reopens_rejected_entry_families", "auto_commits", "auto_pushes"):
        assert rec[flag] is False, flag


def test_frozen_constants_locked():
    rec = g.build_geometry_spec()
    fc = rec["frozen_constants"]
    assert fc["bar_basis"] == "closed_candles_only"
    assert fc["entry_timing"] == "next_bar_open"
    assert fc["atr_period"] == 14
    assert fc["bb_period"] == 20 and fc["bb_stddev"] == 2.0
    assert fc["fractal_half_window"] == 2 and fc["trendline_anchor_pivots"] == 2
    assert fc["min_reward_risk"] == 2.0
    assert fc["timeframes_allowed_first"] == ("1D", "4H")
    assert fc["assets_scope"] == ("BTC", "ETH", "SOL")


def test_rejected_entry_families_inherited_blocked():
    rec = g.build_geometry_spec()
    amap = rec["anti_loop_map"]
    blocked = {tuple(r["duplicates_of"]): r["status"]
               for r in amap if r["in_scope"] is False}
    assert blocked[("crypto_intraday_breakout_pullback_structure",
                    "ny_session_fvg_choch",
                    "c25_video_momentum_breakout_scalping")] == "INHERITED_BLOCKED"
    assert blocked[("liquidity_sweep_mean_reversion",
                    "low_volume_downside_capitulation_mean_reversion")] == "INHERITED_BLOCKED"
    # exactly one in-scope geometry mechanism
    assert sum(1 for r in amap if r["in_scope"] is True) == 1


def test_precommitted_failure_rule_complete():
    rec = g.build_geometry_spec()
    fr = rec["precommitted_failure_rule"]
    for b in ("buy_and_hold", "donchian_breakout", "bollinger_mean_reversion",
              "simple_trend_following", "random_entry_baseline"):
        assert b in fr["must_beat_net_of_costs"]
    for h in ("forward_oos_positive", "btc_risk_adjusted_benchmark_beaten",
              "min_sample_gate_100_labels"):
        assert h in fr["must_hold"]
    assert fr["otherwise"] == "AUTO_REJECT_KEPT_ON_RECORD"


def test_validator_rejects_activation_tamper():
    rec = g.build_geometry_spec()
    rec["activates_candidate"] = True
    assert g.validate_geometry_spec(rec)["valid"] is False


def test_validator_rejects_entry_rule_tamper():
    rec = g.build_geometry_spec()
    rec["entry_rule_defined"] = True
    assert g.validate_geometry_spec(rec)["valid"] is False


def test_validator_rejects_constant_retuning():
    rec = g.build_geometry_spec()
    rec["frozen_constants"] = dict(rec["frozen_constants"])
    rec["frozen_constants"]["min_reward_risk"] = 1.0   # silent re-tune
    assert g.validate_geometry_spec(rec)["valid"] is False


def test_validator_rejects_unblocking_rejected_family():
    rec = g.build_geometry_spec()
    rec["anti_loop_map"] = [dict(r) for r in rec["anti_loop_map"]]
    for r in rec["anti_loop_map"]:
        if r["in_scope"] is False:
            r["status"] = "REOPENED"
    assert g.validate_geometry_spec(rec)["valid"] is False
