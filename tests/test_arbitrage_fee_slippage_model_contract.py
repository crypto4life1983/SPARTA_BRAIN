"""Tests for the SPARTA Arbitrage Factory V1 Fee/Slippage Model Contract.

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no staged-file read, no scanner, no scheduler, no gate is
unlocked. The model charges every cost conservatively and its classification is a
research readiness input, never a trade signal."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_data_contract as dc
import sparta_commander.arbitrage_fee_slippage_model_contract as fm


def _edge_inputs(**overrides):
    inputs = {
        "gross_edge_bps": 30.0,
        "taker_fee_bps": 5.0,
        "spread_cost_bps": 2.0,
        "slippage_bps": 1.5,
        "funding_adjustment_bps": 1.0,
        "withdrawal_amortization_bps": 0.5,
    }
    inputs.update(overrides)
    return inputs


# --------------------------------------------------------------------------- #
# ready data contract -> READY model
# --------------------------------------------------------------------------- #
def test_model_ready_on_real_chain():
    m = fm.build_arbitrage_fee_slippage_model()
    assert m["verdict"] == fm.VERDICT_MODEL_READY
    assert m["blockers"] == []
    assert m["data_contract_verdict"] == dc.VERDICT_DATA_CONTRACT_READY
    assert m["lane"] == "arbitrage_factory_v1"
    assert m["roadmap_seq"] == 3
    assert m["next_required_action"] == "HUMAN_APPROVED_ALERT_REPORT_SCHEMA"


def test_required_fields_align_with_seq2_data_contract():
    assert fm.REQUIRED_FEE_FIELDS == (
        dc.STAGED_DATASET_SPECS["fee_schedule"]["required_columns"])
    assert fm.REQUIRED_LIQUIDITY_FIELDS == (
        dc.STAGED_DATASET_SPECS["liquidity_depth"]["required_columns"])
    assert fm.MODEL_INPUT_KINDS == ("fee_schedule", "liquidity_depth",
                                    "funding_rates")


def test_cost_rules_and_assumptions_are_conservative():
    rules = " ".join(fm.COST_MODEL_RULES)
    assert "taker_rate_on_both_legs" in rules
    assert "never_a_forward_forecast" in rules
    assert "flat_venue_label_fees_no_chain_lookup" in rules
    assert "full_half_spread_per_leg" in rules
    assert "never_assumed_zero" in rules
    assert "never_a_trade_signal" in rules
    assumptions = " ".join(fm.CONSERVATIVE_ASSUMPTIONS)
    assert "more_expensive_choice" in assumptions
    assert "no_cost_ever_defaults_to_zero" in assumptions
    assert "when_in_doubt_the_classification_is_FAIL" in assumptions


def test_thresholds_are_sane():
    assert fm.MIN_NET_EDGE_PASS_BPS > fm.MIN_NET_EDGE_WATCH_BPS >= 0
    assert 0 < fm.MAX_DEPTH_UTILIZATION_PCT <= 10.0


def test_build_is_deterministic():
    assert (fm.build_arbitrage_fee_slippage_model()
            == fm.build_arbitrage_fee_slippage_model())


# --------------------------------------------------------------------------- #
# net edge arithmetic
# --------------------------------------------------------------------------- #
def test_net_edge_charges_every_cost():
    r = fm.estimate_net_edge_bps(_edge_inputs())
    assert r["computable"] is True
    # 30 - 2*5 - 2 - 1.5 - 1 - 0.5 = 15.0
    assert abs(r["net_edge_bps"] - 15.0) < 1e-9


def test_classification_thresholds():
    assert fm.classify_net_edge(15.0) == "PASS"
    assert fm.classify_net_edge(fm.MIN_NET_EDGE_PASS_BPS) == "PASS"
    assert fm.classify_net_edge(5.0) == "WATCH"
    assert fm.classify_net_edge(0.0) == "WATCH"
    assert fm.classify_net_edge(-0.1) == "FAIL"
    assert fm.classify_net_edge(None) == "FAIL"
    assert fm.classify_net_edge("ten") == "FAIL"
    assert fm.classify_net_edge(float("nan")) == "FAIL"
    assert fm.classify_net_edge(float("inf")) == "FAIL"
    assert fm.classify_net_edge(True) == "FAIL"


def test_fees_eat_the_edge_realistically():
    # a 10 bps gross edge dies after taker fees on both legs
    r = fm.estimate_net_edge_bps(_edge_inputs(gross_edge_bps=10.0))
    assert r["computable"] is True
    assert r["net_edge_bps"] < 0
    assert fm.classify_net_edge(r["net_edge_bps"]) == "FAIL"


def test_missing_cost_never_defaults_to_zero():
    bad = _edge_inputs()
    del bad["slippage_bps"]
    r = fm.estimate_net_edge_bps(bad)
    assert r["computable"] is False
    assert r["net_edge_bps"] is None
    assert "missing_or_non_numeric:slippage_bps" in r["errors"]


def test_negative_cost_is_refused():
    r = fm.estimate_net_edge_bps(_edge_inputs(taker_fee_bps=-1.0))
    assert r["computable"] is False
    assert "negative_cost:taker_fee_bps" in r["errors"]


def test_non_finite_and_non_numeric_inputs_refused():
    r = fm.estimate_net_edge_bps(_edge_inputs(spread_cost_bps=float("nan")))
    assert r["computable"] is False
    assert "non_finite:spread_cost_bps" in r["errors"]
    r2 = fm.estimate_net_edge_bps(_edge_inputs(gross_edge_bps="big"))
    assert r2["computable"] is False
    r3 = fm.estimate_net_edge_bps(_edge_inputs(gross_edge_bps=True))
    assert r3["computable"] is False
    assert fm.estimate_net_edge_bps(None)["computable"] is False


def test_depth_utilization_cap_refuses_slippage():
    r = fm.estimate_net_edge_bps(_edge_inputs(depth_utilization_pct=25.0))
    assert r["computable"] is False
    assert "depth_utilization_above_cap_slippage_not_estimable" in r["errors"]
    ok = fm.estimate_net_edge_bps(_edge_inputs(depth_utilization_pct=5.0))
    assert ok["computable"] is True


def test_forbidden_input_keys_refuse_whole_estimate():
    for bad_key in ("position_size", "account_balance", "order_id", "leverage"):
        r = fm.estimate_net_edge_bps(_edge_inputs(**{bad_key: 1.0}))
        assert r["computable"] is False, bad_key
        assert any("forbidden_input" in e for e in r["errors"])


def test_estimate_is_deterministic():
    assert fm.estimate_net_edge_bps(_edge_inputs()) == fm.estimate_net_edge_bps(
        _edge_inputs())


# --------------------------------------------------------------------------- #
# input descriptors: valid staged shapes accepted, unsafe refused
# --------------------------------------------------------------------------- #
def test_valid_fee_schedule_descriptor_accepted():
    v = fm.validate_model_input_descriptor(
        "fee_schedule",
        ["venue", "symbol", "taker_fee_pct", "maker_fee_pct",
         "withdrawal_flat_fee"])
    assert v["acceptable"] is True


def test_valid_liquidity_descriptor_accepted():
    v = fm.validate_model_input_descriptor(
        "liquidity_depth",
        ["timestamp_utc", "symbol", "venue", "bid_depth_usd_10bps",
         "ask_depth_usd_10bps", "spread_bps"])
    assert v["acceptable"] is True


def test_non_model_input_kind_refused():
    v = fm.validate_model_input_descriptor(
        "cross_exchange_quotes",
        ["timestamp_utc", "symbol", "venue", "bid", "ask", "mid"])
    assert v["acceptable"] is False
    assert any("kind_not_a_model_input" in e for e in v["errors"])


def test_credential_account_order_position_fields_refused():
    for bad_col in ("api_key", "account_id", "wallet_balance", "order_id",
                    "open_position", "margin_used", "realized_pnl"):
        v = fm.validate_model_input_descriptor(
            "fee_schedule",
            ["venue", "symbol", "taker_fee_pct", "maker_fee_pct",
             "withdrawal_flat_fee", bad_col])
        assert v["acceptable"] is False, bad_col
        assert any("forbidden_field" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# gating on the seq-2 data contract
# --------------------------------------------------------------------------- #
def test_missing_data_contract_blocks():
    m = fm.record_arbitrage_fee_slippage_model(None)
    assert m["verdict"] == fm.VERDICT_MODEL_BLOCKED
    assert "data_contract_missing" in m["blockers"]


def test_invalid_data_contract_blocks():
    contract = dc.build_arbitrage_data_contract()
    contract["fetches_data"] = True
    m = fm.record_arbitrage_fee_slippage_model(contract)
    assert m["verdict"] == fm.VERDICT_MODEL_BLOCKED
    assert "data_contract_invalid" in m["blockers"]


def test_blocked_data_contract_blocks():
    blocked = dc.record_arbitrage_data_contract(None)
    m = fm.record_arbitrage_fee_slippage_model(blocked)
    assert m["verdict"] == fm.VERDICT_MODEL_BLOCKED
    assert "data_contract_not_ready" in m["blockers"]


# --------------------------------------------------------------------------- #
# posture
# --------------------------------------------------------------------------- #
def test_model_is_inert_on_all_paths():
    models = [
        fm.build_arbitrage_fee_slippage_model(),
        fm.record_arbitrage_fee_slippage_model(None),
    ]
    for m in models:
        assert m["classification_is_research_readiness_not_a_trade_signal"] is True
        assert m["costs_never_default_to_zero"] is True
        assert m["withdrawal_costs_are_labels_only_no_chain_lookup"] is True
        assert m["model_reads_no_files"] is True
        assert m["output_is_model_readiness_only"] is True
        assert m["human_review_required"] is True
        for key in (
            "executes", "writes_files", "runs_scanner", "runs_simulation",
            "runs_backtest", "runs_optimization", "starts_scheduler",
            "starts_daemon", "starts_background_worker", "runs_loop",
            "fetches_data", "calls_api", "connects_broker", "connects_exchange",
            "uses_real_money", "uses_network", "uses_credentials",
            "contains_order_logic", "authorizes_paper_execution",
            "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
            "unlocks_downstream_gate",
        ):
            assert m[key] is False, key
        assert m["paper_trading_gate_locked"] is True
        assert m["micro_live_gate_locked"] is True
        assert m["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_blocked():
    assert fm.validate_arbitrage_fee_slippage_model(
        fm.build_arbitrage_fee_slippage_model())["valid"] is True
    assert fm.validate_arbitrage_fee_slippage_model(
        fm.record_arbitrage_fee_slippage_model(None))["valid"] is True


def test_validate_rejects_weakened_assumptions_or_rules():
    m = fm.build_arbitrage_fee_slippage_model()
    m["conservative_assumptions"] = m["conservative_assumptions"][:3]
    v = fm.validate_arbitrage_fee_slippage_model(m)
    assert v["valid"] is False
    assert "conservative_assumptions_weakened" in v["errors"]
    m2 = fm.build_arbitrage_fee_slippage_model()
    m2["cost_model_rules"][0] = "fees_use_maker_rate_when_convenient"
    v2 = fm.validate_arbitrage_fee_slippage_model(m2)
    assert v2["valid"] is False
    assert "cost_rules_tampered" in v2["errors"]


def test_validate_rejects_loosened_thresholds_or_cap():
    m = fm.build_arbitrage_fee_slippage_model()
    m["min_net_edge_watch_bps"] = -5.0
    v = fm.validate_arbitrage_fee_slippage_model(m)
    assert v["valid"] is False
    assert "thresholds_not_conservative" in v["errors"]
    m2 = fm.build_arbitrage_fee_slippage_model()
    m2["max_depth_utilization_pct"] = 50.0
    v2 = fm.validate_arbitrage_fee_slippage_model(m2)
    assert v2["valid"] is False
    assert "depth_utilization_cap_loosened" in v2["errors"]


def test_validate_rejects_diverged_fields_or_weakened_tokens():
    m = fm.build_arbitrage_fee_slippage_model()
    m["required_fee_fields"] = m["required_fee_fields"][:2]
    v = fm.validate_arbitrage_fee_slippage_model(m)
    assert v["valid"] is False
    assert "fee_fields_diverge_from_data_contract" in v["errors"]
    m2 = fm.build_arbitrage_fee_slippage_model()
    m2["forbidden_field_tokens"] = [
        t for t in m2["forbidden_field_tokens"] if t != "position"]
    v2 = fm.validate_arbitrage_fee_slippage_model(m2)
    assert v2["valid"] is False
    assert "forbidden_tokens_weakened" in v2["errors"]


def test_validate_rejects_trade_signal_or_zero_cost_claims():
    m = fm.build_arbitrage_fee_slippage_model()
    m["classification_is_research_readiness_not_a_trade_signal"] = False
    v = fm.validate_arbitrage_fee_slippage_model(m)
    assert v["valid"] is False
    assert "trade_signal_claimed" in v["errors"]
    m2 = fm.build_arbitrage_fee_slippage_model()
    m2["costs_never_default_to_zero"] = False
    v2 = fm.validate_arbitrage_fee_slippage_model(m2)
    assert v2["valid"] is False
    assert "zero_cost_default_allowed" in v2["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    m = fm.build_arbitrage_fee_slippage_model()
    m["micro_live_gate_locked"] = False
    v = fm.validate_arbitrage_fee_slippage_model(m)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])
    m2 = fm.build_arbitrage_fee_slippage_model()
    m2["contains_order_logic"] = True
    v2 = fm.validate_arbitrage_fee_slippage_model(m2)
    assert v2["valid"] is False
    assert any("capability_not_false:contains_order_logic" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_ready_and_blocked():
    md = fm.render_arbitrage_fee_slippage_model_markdown(
        fm.build_arbitrage_fee_slippage_model())
    assert md.startswith(
        "# SPARTA Arbitrage Factory V1 Fee/Slippage Model (MODEL ONLY)")
    assert "NEVER a trade signal" in md
    assert "when in doubt, FAIL" in md
    assert "net = gross - 2*taker_fee" in md
    assert "LOCKED" in md
    md2 = fm.render_arbitrage_fee_slippage_model_markdown(
        fm.record_arbitrage_fee_slippage_model(None))
    assert "BLOCKED defines nothing usable" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_model_label():
    assert fm.get_arbitrage_fee_slippage_model_label() == fm.MODEL_LABEL
    assert "READ-ONLY" in fm.MODEL_LABEL
    assert "MODEL ONLY" in fm.MODEL_LABEL
    assert fm.MODEL_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in fm.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_exchange_or_credential_modules():
    with open(fm.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp",
              "schedule", "apscheduler", "threading", "multiprocessing", "asyncio",
              "sched", "time", "telegram", "email", "csv", "sqlite3", "pandas"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
