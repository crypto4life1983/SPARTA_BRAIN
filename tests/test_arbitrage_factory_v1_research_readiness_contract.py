"""Tests for the SPARTA Arbitrage Factory V1 Research Readiness Contract (READ-ONLY).

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no scanner, no order logic, no file write, no gate is unlocked.
The contract opens the arbitrage research lane as a spec only: alerts and reports
forever, execution absent by construction."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_factory_v1_research_readiness_contract as ar

_EXPECTED_FAMILY_IDS = {
    "ARB_F1_spot_perp_funding_basis",
    "ARB_F2_cross_exchange_basis_monitoring",
    "ARB_F3_btc_eth_sol_pair_spread_alerts",
    "ARB_F4_fee_adjusted_net_edge_scanner",
    "ARB_F5_liquidity_spread_slippage_filters",
    "ARB_F6_pass_watch_fail_report_framework",
}


# --------------------------------------------------------------------------- #
# the readiness spec is READY and structurally inert
# --------------------------------------------------------------------------- #
def test_readiness_is_ready_and_inert():
    s = ar.build_arbitrage_factory_v1_readiness()
    assert s["verdict"] == ar.VERDICT_READINESS_READY
    assert s["lane"] == "arbitrage_factory_v1"
    assert s["alerts_and_reports_only"] is True
    assert s["execution_capability_exists"] is False
    assert s["scanner_exists"] is False
    assert s["modifies_crypto_d1_lane"] is False
    assert s["blockers"] == []
    assert s["next_required_action"] == "HUMAN_APPROVED_ARBITRAGE_SCANNER_SPEC"


def test_all_six_families_defined():
    fams = ar.candidate_arbitrage_families()
    assert {f["family_id"] for f in fams} == _EXPECTED_FAMILY_IDS
    for f in fams:
        assert f["description"]
        assert f["research_question"]
        assert f["data_needs"]


def test_no_trade_rules_are_strict():
    rules = ar.no_trade_rules()
    assert len(rules) >= 5
    joined = " ".join(rules)
    assert "never_orders" in joined
    assert "no_order_logic" in joined
    assert "no_exchange_credentials" in joined
    assert "execution_is_absent_by_construction" in joined
    assert "top_level_architecture_authorization" in joined
    assert "preregistered" in joined  # Crypto-D1 lessons carried


def test_data_source_requirements_fetch_nothing():
    src = ar.data_source_requirements()
    assert src["fetched_by_this_contract"] is False
    assert "manually_staged_csv_files_placed_by_the_operator" in (
        src["allowed_source_classes"]
    )
    forbidden = " ".join(src["forbidden"])
    assert "credentialed_api_key" in forbidden
    assert "authenticated_or_private_endpoint" in forbidden
    assert "any_fetch_performed_by_a_contract_module" in forbidden


def test_safety_gates_cover_the_full_pre_scanner_path():
    gates = ar.safety_gates_before_scanner()
    ids = [g["gate_id"] for g in gates]
    assert ids == ["G1_scanner_spec_approved", "G2_data_contract_approved",
                   "G3_fee_slippage_model_approved", "G4_report_schema_approved",
                   "G5_commander_safety_review", "G6_explicit_human_run_approval"]
    joined = " ".join(g["requirement"] for g in gates)
    assert "human-approved" in joined
    assert "no scheduler" in joined


def test_roadmap_is_complete_and_ordered():
    roadmap = ar.future_blocks_roadmap()
    assert [b["seq"] for b in roadmap] == [1, 2, 3, 4, 5, 6]
    blocks = [b["block"] for b in roadmap]
    assert blocks == [
        "arbitrage_scanner_spec_contract",
        "arbitrage_data_contract",
        "arbitrage_fee_slippage_model_contract",
        "arbitrage_report_schema_contract",
        "arbitrage_scanner_review_contract",
        "arbitrage_mission_flow_registration",
    ]


def test_accessors_return_copies():
    a = ar.candidate_arbitrage_families()
    a[0]["family_id"] = "tampered"
    assert ar.candidate_arbitrage_families()[0]["family_id"] != "tampered"
    r = ar.no_trade_rules()
    r.append("tampered")
    assert "tampered" not in ar.no_trade_rules()
    g = ar.safety_gates_before_scanner()
    g[0]["gate_id"] = "tampered"
    assert ar.safety_gates_before_scanner()[0]["gate_id"] != "tampered"


# --------------------------------------------------------------------------- #
# capability posture: nothing real, gates untouched
# --------------------------------------------------------------------------- #
def test_spec_runs_fetches_connects_nothing():
    s = ar.build_arbitrage_factory_v1_readiness()
    for key in (
        "executes", "writes_files", "runs_scanner", "runs_simulation", "runs_backtest",
        "runs_optimization", "fetches_data", "calls_api", "connects_broker",
        "connects_exchange", "uses_real_money", "uses_network", "uses_credentials",
        "contains_order_logic", "authorizes_paper_execution", "authorizes_micro_live",
        "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
    ):
        assert s[key] is False, key
    assert s["paper_trading_gate_locked"] is True
    assert s["micro_live_gate_locked"] is True
    assert s["live_gate_locked"] is True


def test_build_is_deterministic():
    assert ar.build_arbitrage_factory_v1_readiness() == (
        ar.build_arbitrage_factory_v1_readiness()
    )


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_built_spec():
    s = ar.build_arbitrage_factory_v1_readiness()
    assert ar.validate_arbitrage_factory_v1_readiness(s)["valid"] is True


def test_validate_rejects_missing_family():
    s = ar.build_arbitrage_factory_v1_readiness()
    s["candidate_arbitrage_families"] = s["candidate_arbitrage_families"][:4]
    v = ar.validate_arbitrage_factory_v1_readiness(s)
    assert v["valid"] is False
    assert "families_not_six" in v["errors"]


def test_validate_rejects_dropped_never_orders_rule():
    s = ar.build_arbitrage_factory_v1_readiness()
    s["no_trade_rules"] = [r for r in s["no_trade_rules"] if "never_orders" not in r]
    v = ar.validate_arbitrage_factory_v1_readiness(s)
    assert v["valid"] is False
    assert "never_orders_rule_missing" in v["errors"]


def test_validate_rejects_fetching_contract():
    s = ar.build_arbitrage_factory_v1_readiness()
    s["data_source_requirements"]["fetched_by_this_contract"] = True
    v = ar.validate_arbitrage_factory_v1_readiness(s)
    assert v["valid"] is False
    assert "contract_claims_to_fetch" in v["errors"]


def test_validate_rejects_execution_capability():
    s = ar.build_arbitrage_factory_v1_readiness()
    s["execution_capability_exists"] = True
    v = ar.validate_arbitrage_factory_v1_readiness(s)
    assert v["valid"] is False
    assert "execution_capability_claimed" in v["errors"]


def test_validate_rejects_existing_scanner():
    s = ar.build_arbitrage_factory_v1_readiness()
    s["scanner_exists"] = True
    v = ar.validate_arbitrage_factory_v1_readiness(s)
    assert v["valid"] is False
    assert "scanner_claimed_to_exist" in v["errors"]


def test_validate_rejects_crypto_d1_modification():
    s = ar.build_arbitrage_factory_v1_readiness()
    s["modifies_crypto_d1_lane"] = True
    v = ar.validate_arbitrage_factory_v1_readiness(s)
    assert v["valid"] is False
    assert "crypto_d1_lane_touched" in v["errors"]


def test_validate_rejects_incomplete_gates_or_roadmap():
    s = ar.build_arbitrage_factory_v1_readiness()
    s["safety_gates_before_scanner"] = s["safety_gates_before_scanner"][:3]
    v = ar.validate_arbitrage_factory_v1_readiness(s)
    assert v["valid"] is False
    assert "safety_gates_incomplete" in v["errors"]
    s2 = ar.build_arbitrage_factory_v1_readiness()
    s2["future_blocks_roadmap"] = s2["future_blocks_roadmap"][:2]
    v2 = ar.validate_arbitrage_factory_v1_readiness(s2)
    assert v2["valid"] is False
    assert "roadmap_incomplete" in v2["errors"]


def test_validate_rejects_unlocked_gate():
    s = ar.build_arbitrage_factory_v1_readiness()
    s["micro_live_gate_locked"] = False
    v = ar.validate_arbitrage_factory_v1_readiness(s)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_capability_true():
    s = ar.build_arbitrage_factory_v1_readiness()
    s["contains_order_logic"] = True
    v = ar.validate_arbitrage_factory_v1_readiness(s)
    assert v["valid"] is False
    assert any("capability_not_false:contains_order_logic" in e for e in v["errors"])


def test_validate_rejects_api_call_capability():
    s = ar.build_arbitrage_factory_v1_readiness()
    s["calls_api"] = True
    v = ar.validate_arbitrage_factory_v1_readiness(s)
    assert v["valid"] is False
    assert any("capability_not_false:calls_api" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = ar.render_arbitrage_factory_v1_readiness_markdown(
        ar.build_arbitrage_factory_v1_readiness()
    )
    assert md.startswith("# SPARTA Arbitrage Factory V1 Research Readiness")
    assert "ARB_F1_spot_perp_funding_basis" in md
    assert "execution: absent by construction" in md
    assert "LOCKED" in md
    assert "never fetched here" in md


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert ar.get_arbitrage_factory_v1_readiness_label() == ar.ARB_LABEL
    assert "READ-ONLY" in ar.ARB_LABEL
    assert ar.ARB_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in ar.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_subprocess_or_credential_modules():
    with open(ar.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
