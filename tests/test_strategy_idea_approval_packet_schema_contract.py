"""Tests for the SPARTA Strategy Idea Approval Packet Schema Contract (READ-ONLY).

Everything here is pure and in-memory; no network, no credentials, no API call, no
queue or ledger write, no scheduler, no gate is unlocked. Packets are born UNSIGNED
and a rejected idea can never reach a signature request."""

from __future__ import annotations

import ast

import sparta_commander.intake_to_orchestrator_adapter_contract as ad
import sparta_commander.strategy_idea_approval_packet_schema_contract as pk
import sparta_commander.strategy_idea_intake_automation_contract as it


def _created_arbitrage():
    return ad.adapt_intake_decision(
        it.intake_strategy_idea("funding rate arbitrage research on btc basis")
    )


def _created_crypto_d1():
    return ad.adapt_intake_decision(it.intake_strategy_idea(
        "When fresh evidence accrues, evaluate RP4 under the trend filter rules."
    ))


# --------------------------------------------------------------------------- #
# created proposals become unsigned, lane-aware packets
# --------------------------------------------------------------------------- #
def test_arbitrage_proposal_becomes_packet():
    p = pk.generate_approval_packet(_created_arbitrage())
    assert p["verdict"] == pk.VERDICT_PACKET_GENERATED
    assert p["blockers"] == []
    assert p["lane"] == it.LANE_ARBITRAGE
    assert p["packet_id"].startswith("packet_")
    assert p["covered_proposal"]["phase"] == "idea_intake"


def test_packet_grants_exactly_the_verbatim_command():
    record = _created_arbitrage()
    p = pk.generate_approval_packet(record)
    assert p["approval_grants_exactly"] == [
        record["proposed_queue_entry"]["suggested_next_safe_command"]
    ]
    assert len(p["approval_grants_exactly"]) == 1


def test_packet_is_born_unsigned():
    p = pk.generate_approval_packet(_created_arbitrage())
    assert p["signed"] is False
    assert p["human_signature"] is None
    assert p["human_decision"] is None
    assert p["packet_is_a_request_not_an_authorization"] is True
    assert p["generated_packet_activates_nothing"] is True


def test_lane_constraints_are_embedded_per_lane():
    arb = pk.generate_approval_packet(_created_arbitrage())
    assert any("execution_is_absent_by_construction" in c
               for c in arb["lane_constraints"])
    d1 = pk.generate_approval_packet(_created_crypto_d1())
    assert any("frozen_block_190_bars" in c for c in d1["lane_constraints"])
    assert any("do_not_promote_resume_policy_yet" in c
               for c in d1["lane_constraints"])


def test_does_not_grant_list_is_complete():
    p = pk.generate_approval_packet(_created_arbitrage())
    joined = " ".join(p["approval_does_not_grant"])
    assert "no_trading" in joined
    assert "no_paper_micro_live_or_live" in joined
    assert "no_credentials" in joined
    assert "no_gate_movement" in joined
    assert "no_steps_beyond_the_single_enumerated_grant" in joined


def test_decision_options_are_the_closed_three():
    p = pk.generate_approval_packet(_created_arbitrage())
    assert tuple(p["decision_options"]) == (
        "APPROVE_AS_SCOPED", "DENY", "REQUEST_CHANGES")


def test_packet_id_is_deterministic():
    a = pk.generate_approval_packet(_created_arbitrage())
    b = pk.generate_approval_packet(_created_arbitrage())
    assert a == b
    c = pk.generate_approval_packet(_created_crypto_d1())
    assert a["packet_id"] != c["packet_id"]


# --------------------------------------------------------------------------- #
# refusals: rejected/maybe/invalid never reach a signature request
# --------------------------------------------------------------------------- #
def test_refused_adapter_record_is_refused():
    refused = ad.adapt_intake_decision(
        it.intake_strategy_idea("auto trade everything with my api key"))
    p = pk.generate_approval_packet(refused)
    assert p["verdict"] == pk.VERDICT_PACKET_REFUSED
    assert p["covered_proposal"] is None
    assert p["approval_grants_exactly"] == []
    assert "no_created_proposal_to_packet" in p["blockers"]


def test_missing_adapter_record_is_refused():
    p = pk.generate_approval_packet(None)
    assert p["verdict"] == pk.VERDICT_PACKET_REFUSED
    assert "adapter_record_missing_or_not_a_dict" in p["blockers"]


def test_tampered_adapter_record_is_refused():
    record = _created_arbitrage()
    record["enqueued_by_adapter"] = True  # breaks the adapter validator
    p = pk.generate_approval_packet(record)
    assert p["verdict"] == pk.VERDICT_PACKET_REFUSED
    assert "adapter_record_invalid" in p["blockers"]
    assert any(b.startswith("adapter_error:") for b in p["blockers"])


def test_chain_end_to_end_rejected_idea_never_reaches_packet():
    for bad_idea in ("place orders on binance for me",
                     "use my exchange account api key",
                     "guaranteed profit, cannot lose"):
        decision = it.intake_strategy_idea(bad_idea)
        record = ad.adapt_intake_decision(decision)
        p = pk.generate_approval_packet(record)
        assert p["verdict"] == pk.VERDICT_PACKET_REFUSED, bad_idea
        assert p["approval_grants_exactly"] == []


# --------------------------------------------------------------------------- #
# posture: in-memory only, nothing runs, gates untouched
# --------------------------------------------------------------------------- #
def test_packet_is_inert_on_all_paths():
    packets = [
        pk.generate_approval_packet(_created_arbitrage()),
        pk.generate_approval_packet(None),
    ]
    for p in packets:
        assert p["packet_is_in_memory_only"] is True
        assert p["human_review_required"] is True
        assert p["next_required_action"] == "HUMAN_APPROVED_BATCH_APPROVAL_DESIGN"
        for key in (
            "executes", "writes_files", "writes_queue", "writes_ledger",
            "runs_research", "runs_scanner", "runs_simulation", "runs_backtest",
            "runs_optimization", "starts_scheduler", "fetches_data", "calls_api",
            "connects_broker", "connects_exchange", "uses_real_money",
            "uses_network", "uses_credentials", "contains_order_logic",
            "authorizes_paper_execution", "authorizes_micro_live",
            "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
        ):
            assert p[key] is False, key
        assert p["paper_trading_gate_locked"] is True
        assert p["micro_live_gate_locked"] is True
        assert p["live_gate_locked"] is True
    assert packets[0]["roadmap_link_id"] == "L2_lane_specific_approval_packet_generator"
    assert packets[0]["roadmap_seq"] == 2


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_generated_and_refused():
    assert pk.validate_approval_packet(
        pk.generate_approval_packet(_created_arbitrage()))["valid"] is True
    assert pk.validate_approval_packet(
        pk.generate_approval_packet(None))["valid"] is True


def test_validate_rejects_signed_packet():
    p = pk.generate_approval_packet(_created_arbitrage())
    p["signed"] = True
    v = pk.validate_approval_packet(p)
    assert v["valid"] is False
    assert "packet_claims_to_be_signed" in v["errors"]
    p2 = pk.generate_approval_packet(_created_arbitrage())
    p2["human_signature"] = "forged"
    v2 = pk.validate_approval_packet(p2)
    assert v2["valid"] is False
    assert "packet_carries_a_signature" in v2["errors"]
    p3 = pk.generate_approval_packet(_created_arbitrage())
    p3["human_decision"] = "APPROVE_AS_SCOPED"
    v3 = pk.validate_approval_packet(p3)
    assert v3["valid"] is False
    assert "packet_carries_a_decision" in v3["errors"]


def test_validate_rejects_multi_grant_or_diverged_grant():
    p = pk.generate_approval_packet(_created_arbitrage())
    p["approval_grants_exactly"].append("BUILD_SOMETHING_ELSE")
    v = pk.validate_approval_packet(p)
    assert v["valid"] is False
    assert "grant_not_exactly_one_command" in v["errors"]
    p2 = pk.generate_approval_packet(_created_arbitrage())
    p2["approval_grants_exactly"] = ["BUILD_SOMETHING_ELSE"]
    v2 = pk.validate_approval_packet(p2)
    assert v2["valid"] is False
    assert "grant_diverges_from_proposal_command" in v2["errors"]


def test_validate_rejects_refused_packet_that_grants():
    p = pk.generate_approval_packet(None)
    p["approval_grants_exactly"] = ["BUILD_SOMETHING"]
    v = pk.validate_approval_packet(p)
    assert v["valid"] is False
    assert "refused_packet_grants_something" in v["errors"]


def test_validate_rejects_tampered_decision_options():
    p = pk.generate_approval_packet(_created_arbitrage())
    p["decision_options"] = ["APPROVE_AS_SCOPED", "AUTO_APPROVE"]
    v = pk.validate_approval_packet(p)
    assert v["valid"] is False
    assert "decision_options_tampered" in v["errors"]


def test_validate_rejects_weakened_does_not_grant():
    p = pk.generate_approval_packet(_created_arbitrage())
    p["approval_does_not_grant"] = [
        n for n in p["approval_does_not_grant"] if "no_trading" not in n]
    v = pk.validate_approval_packet(p)
    assert v["valid"] is False
    assert any("does_not_grant_missing:no_trading" in e for e in v["errors"])


def test_validate_rejects_authorization_claim():
    p = pk.generate_approval_packet(_created_arbitrage())
    p["packet_is_a_request_not_an_authorization"] = False
    v = pk.validate_approval_packet(p)
    assert v["valid"] is False
    assert "packet_claims_to_authorize" in v["errors"]
    p2 = pk.generate_approval_packet(_created_arbitrage())
    p2["generated_packet_activates_nothing"] = False
    v2 = pk.validate_approval_packet(p2)
    assert v2["valid"] is False
    assert "packet_claims_to_activate" in v2["errors"]


def test_validate_rejects_missing_lane_constraints():
    p = pk.generate_approval_packet(_created_arbitrage())
    p["lane_constraints"] = []
    v = pk.validate_approval_packet(p)
    assert v["valid"] is False
    assert "generated_packet_without_lane_constraints" in v["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    p = pk.generate_approval_packet(_created_arbitrage())
    p["paper_trading_gate_locked"] = False
    v = pk.validate_approval_packet(p)
    assert v["valid"] is False
    assert any("gate_not_locked:paper_trading_gate_locked" in e for e in v["errors"])
    p2 = pk.generate_approval_packet(_created_arbitrage())
    p2["writes_ledger"] = True
    v2 = pk.validate_approval_packet(p2)
    assert v2["valid"] is False
    assert any("capability_not_false:writes_ledger" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_generated_and_refused():
    md = pk.render_approval_packet_markdown(
        pk.generate_approval_packet(_created_arbitrage()))
    assert md.startswith("# SPARTA Strategy Idea Approval Packet (UNSIGNED REQUEST)")
    assert "grants EXACTLY" in md
    assert "does NOT grant" in md
    assert "LOCKED" in md
    md2 = pk.render_approval_packet_markdown(pk.generate_approval_packet(None))
    assert "refused; no signature request exists" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_label():
    assert pk.get_strategy_idea_approval_packet_label() == pk.PACKET_LABEL
    assert "READ-ONLY" in pk.PACKET_LABEL
    assert pk.PACKET_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in pk.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_subprocess_or_credential_modules():
    with open(pk.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets", "aiohttp",
              "schedule", "apscheduler"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)
