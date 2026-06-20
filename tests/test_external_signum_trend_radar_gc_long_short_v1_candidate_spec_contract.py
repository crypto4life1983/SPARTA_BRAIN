"""Tests for the Candidate #22 candidate-spec contract
(external_signum_trend_radar_gc_long_short_v1) -- the deterministic transcription of the
Signum TR-GC-Crypto-LS-2 rules.

Verifies: research-only, spec-only, executes nothing; chain-gated on the frozen C22
proposal (verdict + pinned pushed commit b1b92795); a FAITHFUL verbatim transcription
where every pinned numeric value matches the source (0.65 short take-profit, 0.98 bear
high multiple, 25-day breakout window, 8%/2%/3%/5% NAV sizing, top-50, 50-line / 3-retry
fetch, 0.5 collision guard, 1%-NAV / $10 dust floors, 100% closes) and NO values are
invented; the live steps (8 re-fetch, 9 email, 10 bot-title edit) + set-pair / convert /
signal-send are represented ONLY as locked research-only/simulated behaviour; the
directional buy-and-hold + random/null + forward-OOS benchmark set; the three genuine
ambiguities flagged SPEC_AMBIGUITY_REQUIRES_HUMAN_REVIEW; downstream gates locked;
advances nothing; capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_candidate_spec_contract as s22  # noqa: E501


_R = s22.build_c22_spec()


# ---- core: research-only, spec-only, validates -----------------------------

def test_spec_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_candidate_spec_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C22_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert s22.validate_c22_spec(_R)["valid"] is True


def test_identity_and_source():
    assert _R["candidate_id"] == "C22"
    assert _R["candidate_token"] == "C22_EXTERNAL_SIGNUM_TREND_RADAR_GC_LONG_SHORT_V1"
    src = _R["source"]
    assert src["provider"] == "Signum"
    assert src["strategy_prompt_id"] == "TR-GC-Crypto-LS-2"
    assert src["bot_id"] == "25792"
    assert _R["transcribed_verbatim_read_only"] is True
    assert _R["no_values_invented"] is True
    assert _R["original_strategy_intent_preserved"] is True


# ---- chain-gated on the frozen, pushed C22 proposal ------------------------

def test_chain_gated_on_frozen_proposal():
    assert _R["proposal_valid"] is True
    assert _R["proposal_verdict"] == "C22_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["chain_gated_on_c22_proposal"] is True
    assert _R["proposal_commit"] == "b1b927957eb41669a9b5d1959aab93da0903cd77"
    bad = {**_R, "proposal_commit": "0" * 40}
    assert s22.validate_c22_spec(bad)["valid"] is False
    bad2 = {**_R, "proposal_verdict": "X"}
    assert s22.validate_c22_spec(bad2)["valid"] is False


# ---- exact numeric transcription of the entry/exit/sizing rules ------------

def test_precondition_and_data_schema():
    pre = _R["precondition"]
    assert pre["requires_perpetual_trading_account"] is True
    assert pre["if_not_perpetual"] == "STOP_ROUTINE_CANNOT_SHORT_AND_NOTIFY"
    assert pre["nav_not_recomputed_midrun"] is True
    di = _R["data_input_schema"]
    assert di["detector"] == "gc"
    assert di["min_line_items"] == 50
    assert di["max_fetch_retries"] == 3
    assert di["research_only_no_mcp_fetch"] is True


def test_btc_regime_and_exits():
    assert _R["btc_regime"]["downtrend_when"] == "btc_latest_closed_close < btc.gc.filter"
    le = _R["long_exit"]
    assert le["close_pct"] == 100
    assert "latest_closed_close < gc.upper" in le["triggers_any_of"]
    se = _R["short_exit"]
    assert se["stop_trigger"] == "latest_closed_close > gc.filter"
    assert se["take_profit_multiple"] == 0.65
    assert se["take_profit_entry_price_formula"] == (
        "(currentCollateralAsQuoteCoin + unrealizedPnlAsQuoteCoin) / sizeAsBaseCoin")


def test_long_entry_rules_and_sizing():
    lon = _R["long_entry"]
    assert lon["top_n_rows"] == 50
    assert lon["sort_key"] == "market_rank" and lon["sort_order"] == "ascending"
    assert lon["never_enter_long_on_asset_long_exited_this_run"] is True
    assert lon["one_position_per_coin"] is True
    sz = lon["sizing_by_breakout_recency"]
    assert sz["breakout_recent_window_calendar_days"] == 25
    assert sz["size_pct_nav_if_breakout_within_window"] == 8.0
    assert sz["size_pct_nav_otherwise"] == 2.0
    assert sz["breakout_not_required_to_enter_only_sets_size"] is True
    # tamper any frozen value -> invalid
    bad_sz = {**sz, "size_pct_nav_if_breakout_within_window": 9.0}
    bad = {**_R, "long_entry": {**lon, "sizing_by_breakout_recency": bad_sz}}
    assert s22.validate_c22_spec(bad)["valid"] is False


def test_short_entry_hedge_and_bear():
    sh = _R["short_entry"]
    assert sh["hedge_short"]["size_pct_nav"] == 3.0
    assert sh["bear_short"]["size_pct_nav"] == 5.0
    assert sh["bear_short"]["high_reaches_filter_multiple"] == 0.98
    assert sh["bear_short"]["evaluated_only_if_hedge_short_not_met"] is True
    assert sh["never_enter_short_on_asset_short_exited_this_run"] is True
    assert sh["when_in_doubt_skip_short"] is True
    bad_bear = {**sh["bear_short"], "high_reaches_filter_multiple": 0.95}
    bad = {**_R, "short_entry": {**sh, "bear_short": bad_bear}}
    assert s22.validate_c22_spec(bad)["valid"] is False


def test_order_size_and_collision_dust_rules():
    os_ = _R["order_size"]
    assert os_["percentage_ordersize_is_pct_of_base_or_quote_coin_not_nav"] is True
    assert os_["entry_min_order_value_pct_nav"] == 1.0
    assert os_["entry_min_order_value_usd"] == 10
    assert os_["exit_min_order_value_usd"] == 10
    nav = os_["nav_pct_to_ordersize"]
    assert nav["never_reuse_a_percentage_calculated_earlier_in_the_run"] is True
    assert nav["cap_ordersize_pct_at_100"] is True
    assert nav["do_not_recompute_nav_midrun"] is True
    tp = _R["trading_pair_rules"]
    assert tp["ticker_collision_guard"]["skip_and_report_if_relative_diff_exceeds"] == 0.5


# ---- live steps 8/9/10 + actions represented ONLY as locked research-only ---

def test_live_steps_locked_research_only():
    assert _R["post_action_check"]["never_executes_live_refetch"] is True
    assert _R["summary_report"]["never_sends_email"] is True
    bte = _R["bot_title_edit"]
    assert bte["research_only_representation"] == "PROHIBITED_LIVE_BEHAVIOUR_LOCKED_OUT"
    assert bte["never_edits_bot"] is True
    assert _R["trading_pair_rules"]["never_sets_trading_pair_live"] is True
    assert _R["conversion_rules"]["never_executes_conversion"] is True
    assert _R["signal_translation"]["never_sends_signal"] is True
    for bad_key, sub in (("post_action_check", "never_executes_live_refetch"),
                         ("summary_report", "never_sends_email")):
        bad_block = {**_R[bad_key], sub: False}
        bad = {**_R, bad_key: bad_block}
        assert s22.validate_c22_spec(bad)["valid"] is False, bad_key


# ---- no Signum/MCP/Hyperliquid/API/order/live execution --------------------

def test_no_execution_no_connection_locks():
    for flag in ("executes", "connects_signum", "uses_mcp", "accesses_hyperliquid",
                 "uses_api_keys", "uses_credentials", "sends_email", "edits_bots",
                 "edits_bot_title", "sets_trading_pair", "converts_funds",
                 "sends_signal", "sends_trades", "places_orders", "contains_order_logic",
                 "creates_claude_routines", "runs_detector", "runs_labels",
                 "runs_replay", "fetches_data", "paper_trading", "live_trading",
                 "installs_scheduler", "invents_rule_values"):
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert s22.validate_c22_spec(bad)["valid"] is False, flag


# ---- benchmarks: directional -> buy-and-hold + random/null + forward-OOS ----

def test_benchmarks_directional():
    bm = _R["benchmarks"]
    assert bm["judged_vs_buy_and_hold"] is True
    assert bm["judged_vs_random_null"] is True
    assert bm["net_of_fees_funding_slippage"] is True
    assert bm["forward_oos_required"] is True
    assert bm["do_not_promote_on_net_positive_alone"] is True
    bad = {**_R, "benchmarks": {**bm, "do_not_promote_on_net_positive_alone": False}}
    assert s22.validate_c22_spec(bad)["valid"] is False


# ---- three ambiguities flagged then RESOLVED BY HUMAN (not vendor text) -----

def test_three_ambiguities_resolved_by_human():
    ambs = _R["spec_ambiguities"]
    assert len(ambs) == 3
    ids = {a["id"] for a in ambs}
    assert ids == {"btc_absent_from_trend_radar", "market_rank_field_source",
                   "held_dust_exception_threshold"}
    for a in ambs:
        assert a["status"] == "RESOLVED_BY_HUMAN_AMBIGUITY_RESOLUTION"
        assert a["resolution_origin"] == "HUMAN_AMBIGUITY_RESOLUTION_NOT_VENDOR_ORIGINAL"
        assert a["rule_ref"] and a["description"] and a["resolution"]
    assert _R["ambiguities_flagged_not_guessed"] is True
    assert _R["all_ambiguities_resolved_by_human"] is True
    assert _R["spec_has_unresolved_ambiguities"] is False
    assert _R["resolutions_are_human_not_vendor_original"] is True
    # tamper: revert an ambiguity to unresolved status -> invalid
    bad_ambs = [dict(a) for a in ambs]
    bad_ambs[0] = {**bad_ambs[0], "status": "SPEC_AMBIGUITY_REQUIRES_HUMAN_REVIEW"}
    bad = {**_R, "spec_ambiguities": bad_ambs}
    assert s22.validate_c22_spec(bad)["valid"] is False
    # tamper: strip the human-origin marker -> invalid
    bad_ambs2 = [dict(a) for a in ambs]
    bad_ambs2[1] = {**bad_ambs2[1], "resolution_origin": "VENDOR"}
    assert s22.validate_c22_spec({**_R, "spec_ambiguities": bad_ambs2})["valid"] is False


# ---- the three resolutions are encoded deterministically into the rules -----

def test_ambiguity_resolutions_encoded_in_rules():
    # 1. BTC absent -> downtrend False -> bear shorts disabled; hedge still evaluated
    btc = _R["btc_regime"]["btc_absent_resolution"]
    assert btc["origin"] == "HUMAN_AMBIGUITY_RESOLUTION_NOT_VENDOR_ORIGINAL"
    assert btc["btc_downtrend_defaults_false_when_absent_or_incomplete"] is True
    assert btc["disables_bear_short_when_btc_downtrend_false"] is True
    assert btc["hedge_short_still_evaluated_when_btc_absent"] is True
    bear = _R["short_entry"]["bear_short"]
    assert bear["requires_btc_downtrend_true"] is True
    assert bear["disabled_when_btc_downtrend_false_per_human_resolution"] is True
    # 2. market rank: unique numeric field, mapped at adapter gate, else skip/reject
    mr = _R["long_entry"]["market_rank_resolution"]
    assert mr["origin"] == "HUMAN_AMBIGUITY_RESOLUTION_NOT_VENDOR_ORIGINAL"
    assert mr["requires_unique_numeric_market_rank_field"] is True
    assert mr["skip_or_reject_entries_if_no_unique_numeric_market_rank"] is True
    assert _R["short_entry"]["market_rank_resolution"][
        "requires_unique_numeric_market_rank_field"] is True
    # 3. held dust uses the EXIT threshold ($10), not the entry threshold
    hd = _R["long_entry"]["held_dust_resolution"]
    assert hd["origin"] == "HUMAN_AMBIGUITY_RESOLUTION_NOT_VENDOR_ORIGINAL"
    assert hd["held_dust_threshold_usd"] == 10
    assert hd["uses_exit_dust_threshold_for_held_position"] is True
    assert hd["does_not_use_entry_threshold_for_held_position"] is True
    # tamper: held-dust using the entry threshold -> invalid
    bad_hd = {**hd, "does_not_use_entry_threshold_for_held_position": False}
    bad_le = {**_R["long_entry"], "held_dust_resolution": bad_hd}
    assert s22.validate_c22_spec({**_R, "long_entry": bad_le})["valid"] is False
    # tamper: bear short no longer requires BTC downtrend -> invalid
    bad_bear = {**bear, "requires_btc_downtrend_true": False}
    bad_se = {**_R["short_entry"], "bear_short": bad_bear}
    assert s22.validate_c22_spec({**_R, "short_entry": bad_se})["valid"] is False


# ---- the ORIGINAL vendor rules are preserved unchanged ---------------------

def test_original_vendor_rules_preserved():
    # the resolutions are additive; the original transcribed values are untouched
    assert _R["short_exit"]["take_profit_multiple"] == 0.65
    assert _R["short_entry"]["bear_short"]["high_reaches_filter_multiple"] == 0.98
    assert _R["long_entry"]["sizing_by_breakout_recency"][
        "size_pct_nav_if_breakout_within_window"] == 8.0
    assert _R["btc_regime"]["downtrend_when"] == "btc_latest_closed_close < btc.gc.filter"
    assert _R["original_strategy_intent_preserved"] is True
    assert _R["no_values_invented"] is True


# ---- gate sequence + downstream locked + advances nothing ------------------

def test_gate_sequence_and_downstream_locked():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    nra = s22.get_candidate_22_spec_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C22_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"
    assert _R["advances_nothing"] is True
    for gate in ("detector_gate_locked", "labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert s22.validate_c22_spec(bad)["valid"] is False, gate


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false():
    for flag in s22._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_detector", "no_labels", "no_replay", "no_data_fetch",
                 "no_invent_values", "no_signum_connection", "no_mcp", "no_hyperliquid",
                 "no_api_keys", "no_send_email", "no_bot_edits", "no_set_trading_pair",
                 "no_convert_funds", "no_send_trades", "no_paper_trading",
                 "no_live_trading", "no_commit", "no_push"):
        assert _R["scope_locks"][must] is True, must


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(s22.__file__, encoding="utf-8").read()
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
