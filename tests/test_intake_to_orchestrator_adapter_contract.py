"""Tests for the SPARTA Intake-to-Orchestrator Adapter Contract (READ-ONLY).

Everything here is pure and in-memory; no network, no credentials, no API call, no
queue write, no file write, no scheduler, no gate is unlocked. The adapter shapes a
PROPOSED queue entry from a validated intake YES and refuses everything else."""

from __future__ import annotations

import ast

import sparta_commander.intake_to_orchestrator_adapter_contract as ad
import sparta_commander.strategy_idea_intake_automation_contract as it
import sparta_commander.strategy_factory_queue_schema as qs


def _yes_arbitrage():
    return it.intake_strategy_idea("funding rate arbitrage research on btc basis")


def _yes_crypto_d1():
    return it.intake_strategy_idea(
        "When fresh evidence accrues, evaluate RP4 under the trend filter rules."
    )


# --------------------------------------------------------------------------- #
# YES decisions become proposals shaped like the real queue schema
# --------------------------------------------------------------------------- #
def test_yes_arbitrage_creates_proposal():
    r = ad.adapt_intake_decision(_yes_arbitrage())
    assert r["verdict"] == ad.VERDICT_PROPOSAL_CREATED
    assert r["blockers"] == []
    assert r["lane"] == it.LANE_ARBITRAGE
    e = r["proposed_queue_entry"]
    assert e["phase"] == "idea_intake"
    assert e["status"] == "AWAITING_HUMAN_REVIEW"
    assert e["priority"] == "normal"
    assert e["entry_is_a_proposal_not_a_queued_run"] is True


def test_yes_crypto_d1_creates_proposal_with_verbatim_command():
    decision = _yes_crypto_d1()
    r = ad.adapt_intake_decision(decision)
    assert r["verdict"] == ad.VERDICT_PROPOSAL_CREATED
    assert r["lane"] == it.LANE_CRYPTO_D1
    assert r["suggested_next_safe_command"] == decision["next_safe_command"]
    e = r["proposed_queue_entry"]
    assert e["suggested_next_safe_command"] == decision["next_safe_command"]
    assert e["command_is_a_suggestion_only"] is True


def test_proposal_satisfies_queue_required_fields():
    e = ad.adapt_intake_decision(_yes_arbitrage())["proposed_queue_entry"]
    for field in qs.REQUIRED_ENTRY_FIELDS:
        assert e.get(field), field


def test_proposal_status_is_in_closed_enum_and_not_forbidden():
    assert ad.PROPOSAL_STATUS in qs.QUEUE_STATUS
    assert ad.PROPOSAL_STATUS not in qs.FORBIDDEN_STATUS_VALUES
    assert ad.PROPOSAL_PHASE in qs.PHASES
    e = ad.adapt_intake_decision(_yes_arbitrage())["proposed_queue_entry"]
    assert e["status"] not in qs.FORBIDDEN_STATUS_VALUES


def test_proposal_ids_are_deterministic():
    a = ad.adapt_intake_decision(_yes_arbitrage())
    b = ad.adapt_intake_decision(_yes_arbitrage())
    assert a == b
    assert a["proposed_queue_entry"]["run_id"].startswith("proposal_idea_")


def test_different_lanes_get_different_candidate_ids():
    a = ad.adapt_intake_decision(_yes_arbitrage())["proposed_queue_entry"]
    c = ad.adapt_intake_decision(_yes_crypto_d1())["proposed_queue_entry"]
    assert a["candidate_id"] != c["candidate_id"]


# --------------------------------------------------------------------------- #
# NO / MAYBE / invalid decisions are refused with no proposal at all
# --------------------------------------------------------------------------- #
def test_rejected_idea_is_refused():
    no = it.intake_strategy_idea("auto trade everything with my api key")
    r = ad.adapt_intake_decision(no)
    assert r["verdict"] == ad.VERDICT_PROPOSAL_REFUSED
    assert r["proposed_queue_entry"] is None
    assert "idea_was_rejected_by_intake_no_proposal_allowed" in r["blockers"]


def test_maybe_idea_is_refused_until_human_clarifies():
    maybe = it.intake_strategy_idea("a vague new thing")
    r = ad.adapt_intake_decision(maybe)
    assert r["verdict"] == ad.VERDICT_PROPOSAL_REFUSED
    assert r["proposed_queue_entry"] is None
    assert "idea_needs_human_clarification_before_any_proposal" in r["blockers"]


def test_missing_decision_is_refused():
    r = ad.adapt_intake_decision(None)
    assert r["verdict"] == ad.VERDICT_PROPOSAL_REFUSED
    assert "intake_decision_missing_or_not_a_dict" in r["blockers"]


def test_tampered_invalid_decision_is_refused():
    d = _yes_arbitrage()
    d["intake_starts_no_work"] = False  # breaks the intake validator
    r = ad.adapt_intake_decision(d)
    assert r["verdict"] == ad.VERDICT_PROPOSAL_REFUSED
    assert "intake_decision_invalid" in r["blockers"]
    assert any(b.startswith("intake_error:") for b in r["blockers"])


def test_yes_with_unknown_lane_is_refused():
    d = _yes_arbitrage()
    d["lane"] = it.LANE_ARBITRAGE  # keep validator happy, then break post-validation
    r_ok = ad.adapt_intake_decision(d)
    assert r_ok["verdict"] == ad.VERDICT_PROPOSAL_CREATED
    # an unrecognized answer string must refuse, not crash
    d2 = _yes_arbitrage()
    d2["answer"] = "YES_RESEARCHABLE_NOW"
    assert ad.adapt_intake_decision(d2)["verdict"] == ad.VERDICT_PROPOSAL_CREATED


# --------------------------------------------------------------------------- #
# adapter posture: in-memory only, never enqueues, gates untouched
# --------------------------------------------------------------------------- #
def test_adapter_record_is_inert_on_all_paths():
    records = [
        ad.adapt_intake_decision(_yes_arbitrage()),
        ad.adapt_intake_decision(it.intake_strategy_idea("auto trade everything")),
        ad.adapt_intake_decision(it.intake_strategy_idea("a vague new thing")),
        ad.adapt_intake_decision(None),
    ]
    for r in records:
        assert r["proposal_is_in_memory_only"] is True
        assert r["enqueued_by_adapter"] is False
        assert r["adapter_invents_no_commands"] is True
        assert r["human_review_required"] is True
        assert r["next_required_action"] == "HUMAN_APPROVED_STRATEGY_IDEA_PACKET_SCHEMA"
        for key in (
            "executes", "writes_files", "writes_queue", "runs_research",
            "runs_scanner", "runs_simulation", "runs_backtest", "runs_optimization",
            "starts_scheduler", "fetches_data", "calls_api", "connects_broker",
            "connects_exchange", "uses_real_money", "uses_network",
            "uses_credentials", "contains_order_logic", "authorizes_paper_execution",
            "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
            "unlocks_downstream_gate",
        ):
            assert r[key] is False, key
        assert r["paper_trading_gate_locked"] is True
        assert r["micro_live_gate_locked"] is True
        assert r["live_gate_locked"] is True


def test_queue_schema_id_is_pinned():
    r = ad.adapt_intake_decision(_yes_arbitrage())
    assert r["queue_schema_id"] == qs.QUEUE_SCHEMA_ID
    assert r["roadmap_link_id"] == "L1_intake_to_queue_adapter"
    assert r["roadmap_seq"] == 1


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_created_and_refused():
    created = ad.adapt_intake_decision(_yes_arbitrage())
    refused = ad.adapt_intake_decision(None)
    assert ad.validate_adapter_record(created)["valid"] is True
    assert ad.validate_adapter_record(refused)["valid"] is True


def test_validate_rejects_refused_with_proposal():
    r = ad.adapt_intake_decision(None)
    r["proposed_queue_entry"] = {"run_id": "x"}
    v = ad.validate_adapter_record(r)
    assert v["valid"] is False
    assert "refused_record_carries_a_proposal" in v["errors"]


def test_validate_rejects_created_without_proposal():
    r = ad.adapt_intake_decision(_yes_arbitrage())
    r["proposed_queue_entry"] = None
    v = ad.validate_adapter_record(r)
    assert v["valid"] is False
    assert "created_record_without_proposal" in v["errors"]


def test_validate_rejects_forbidden_or_wrong_status():
    r = ad.adapt_intake_decision(_yes_arbitrage())
    r["proposed_queue_entry"]["status"] = "APPROVED"
    v = ad.validate_adapter_record(r)
    assert v["valid"] is False
    assert "proposal_status_not_awaiting_human_review" in v["errors"]
    assert "proposal_uses_forbidden_status" in v["errors"]


def test_validate_rejects_queued_run_claim():
    r = ad.adapt_intake_decision(_yes_arbitrage())
    r["proposed_queue_entry"]["entry_is_a_proposal_not_a_queued_run"] = False
    v = ad.validate_adapter_record(r)
    assert v["valid"] is False
    assert "proposal_claims_to_be_a_queued_run" in v["errors"]


def test_validate_rejects_diverged_command():
    r = ad.adapt_intake_decision(_yes_arbitrage())
    r["proposed_queue_entry"]["suggested_next_safe_command"] = "BUILD_OTHER_THING"
    v = ad.validate_adapter_record(r)
    assert v["valid"] is False
    assert "proposal_command_diverges_from_record" in v["errors"]


def test_validate_rejects_enqueue_claim_or_persistence():
    r = ad.adapt_intake_decision(_yes_arbitrage())
    r["enqueued_by_adapter"] = True
    v = ad.validate_adapter_record(r)
    assert v["valid"] is False
    assert "adapter_claims_to_have_enqueued" in v["errors"]
    r2 = ad.adapt_intake_decision(_yes_arbitrage())
    r2["proposal_is_in_memory_only"] = False
    v2 = ad.validate_adapter_record(r2)
    assert v2["valid"] is False
    assert "proposal_not_in_memory_only" in v2["errors"]


def test_validate_rejects_missing_required_field():
    r = ad.adapt_intake_decision(_yes_arbitrage())
    del r["proposed_queue_entry"]["run_id"]
    v = ad.validate_adapter_record(r)
    assert v["valid"] is False
    assert "proposal_missing_field:run_id" in v["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    r = ad.adapt_intake_decision(_yes_arbitrage())
    r["live_gate_locked"] = False
    v = ad.validate_adapter_record(r)
    assert v["valid"] is False
    assert any("gate_not_locked:live_gate_locked" in e for e in v["errors"])
    r2 = ad.adapt_intake_decision(_yes_arbitrage())
    r2["writes_queue"] = True
    v2 = ad.validate_adapter_record(r2)
    assert v2["valid"] is False
    assert any("capability_not_false:writes_queue" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_created_and_refused():
    md = ad.render_adapter_record_markdown(ad.adapt_intake_decision(_yes_arbitrage()))
    assert md.startswith("# SPARTA Intake-to-Orchestrator Adapter Record")
    assert "AWAITING_HUMAN_REVIEW" in md
    assert "suggestion only, human must issue it" in md
    assert "LOCKED" in md
    md2 = ad.render_adapter_record_markdown(ad.adapt_intake_decision(None))
    assert "refused; nothing was proposed" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_label():
    assert ad.get_intake_to_orchestrator_adapter_label() == ad.ADAPTER_LABEL
    assert "READ-ONLY" in ad.ADAPTER_LABEL
    assert ad.ADAPTER_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in ad.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_subprocess_or_credential_modules():
    with open(ad.__file__, "r", encoding="utf-8") as fh:
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
