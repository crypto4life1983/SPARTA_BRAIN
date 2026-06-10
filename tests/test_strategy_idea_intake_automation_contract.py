"""Tests for the SPARTA Strategy Idea Intake Automation Contract (READ-ONLY).

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no file write, no gate is unlocked. The intake triages ideas to
YES/NO/MAYBE deterministically and never starts work itself."""

from __future__ import annotations

import ast

import sparta_commander.strategy_idea_intake_automation_contract as it


# --------------------------------------------------------------------------- #
# YES: arbitrage-lane ideas route with a next safe command
# --------------------------------------------------------------------------- #
def test_arbitrage_idea_is_yes_routed_to_arbitrage_lane():
    d = it.intake_strategy_idea(
        "Monitor the funding rate and spot-perp basis on BTC and alert when the "
        "fee-adjusted carry is positive."
    )
    assert d["answer"] == it.ANSWER_YES
    assert d["lane"] == it.LANE_ARBITRAGE
    assert d["next_safe_command"] == "BUILD_ARBITRAGE_DATA_CONTRACT_READ_ONLY"
    assert d["next_safe_command_is_a_suggestion_only"] is True
    assert any("alerts_and_reports_only" in r for r in d["reasons"])


def test_cross_exchange_idea_is_yes():
    d = it.intake_strategy_idea(
        {"title": "Cross-exchange spread watch",
         "description": "track the price difference between venues for ETH"}
    )
    assert d["answer"] == it.ANSWER_YES
    assert d["lane"] == it.LANE_ARBITRAGE


# --------------------------------------------------------------------------- #
# YES: crypto-d1 fresh-evidence ideas route with the frozen-rulebook command
# --------------------------------------------------------------------------- #
def test_crypto_d1_fresh_evidence_idea_is_yes_with_frozen_bars():
    d = it.intake_strategy_idea(
        "When fresh evidence accrues, evaluate RP4 under the trend filter rules."
    )
    assert d["answer"] == it.ANSWER_YES
    assert d["lane"] == it.LANE_CRYPTO_D1
    assert "AWAIT_FRESH_EVIDENCE_ACCRUAL" in d["next_safe_command"]
    assert any("thread_is_closed" in r for r in d["reasons"])
    assert any("frozen_block_190_bars" in r for r in d["reasons"])


# --------------------------------------------------------------------------- #
# NO: execution / credentials / private data / hype / tainted windows
# --------------------------------------------------------------------------- #
def test_execution_idea_is_rejected():
    d = it.intake_strategy_idea(
        "Build a bot to auto-trade the funding arbitrage and place orders on binance."
    )
    assert d["answer"] == it.ANSWER_NO
    assert d["lane"] is None
    assert d["next_safe_command"] is None
    assert any("requires_order_execution" in r for r in d["reasons"])


def test_structured_needs_execution_flag_rejects():
    d = it.intake_strategy_idea(
        {"title": "basis research", "description": "study the basis",
         "needs_execution": True}
    )
    assert d["answer"] == it.ANSWER_NO
    assert any("requires_order_execution" in r for r in d["reasons"])


def test_credentials_idea_is_rejected():
    d = it.intake_strategy_idea(
        "Connect my exchange account with the api key and track my balance."
    )
    assert d["answer"] == it.ANSWER_NO
    assert any("requires_exchange_credentials" in r for r in d["reasons"])


def test_hype_idea_is_rejected():
    d = it.intake_strategy_idea("A guaranteed profit strategy that cannot lose.")
    assert d["answer"] == it.ANSWER_NO
    assert any("auto_rejected" in r for r in d["reasons"])


def test_private_data_idea_is_rejected():
    d = it.intake_strategy_idea("Use a paid signal group's private feed for entries.")
    assert d["answer"] == it.ANSWER_NO
    assert any("private_or_authenticated_data" in r for r in d["reasons"])


def test_tainted_window_remining_is_rejected():
    d = it.intake_strategy_idea(
        "Let's tweak rp6 parameters and re-run the old windows to make it win."
    )
    assert d["answer"] == it.ANSWER_NO
    assert any("repeats_the_overfit" in r for r in d["reasons"])


def test_hard_no_beats_lane_match():
    # Even a perfect arbitrage keyword match is rejected when execution is requested.
    d = it.intake_strategy_idea(
        "Spot-perp funding arbitrage that will execute trades automatically."
    )
    assert d["answer"] == it.ANSWER_NO


# --------------------------------------------------------------------------- #
# MAYBE: vague, cross-lane, or genuinely new ideas
# --------------------------------------------------------------------------- #
def test_empty_idea_is_maybe():
    d = it.intake_strategy_idea("")
    assert d["answer"] == it.ANSWER_MAYBE
    assert d["clarifications"]


def test_unrelated_new_idea_is_maybe_new_lane():
    d = it.intake_strategy_idea(
        "Research seasonal patterns in agricultural commodity prices."
    )
    assert d["answer"] == it.ANSWER_MAYBE
    assert d["lane"] == it.LANE_NEW_REQUIRED
    assert "RESEARCH_READINESS_CONTRACT" in d["next_safe_command"]
    assert any("research/alerts only" in c for c in d["clarifications"])


def test_cross_lane_idea_is_maybe():
    d = it.intake_strategy_idea(
        "Use the resume policy trend filter to time spot-perp basis arbitrage entries."
    )
    assert d["answer"] == it.ANSWER_MAYBE
    assert d["lane"] is None
    assert any("pick one" in c or "belong" in c for c in d["clarifications"])


# --------------------------------------------------------------------------- #
# determinism and posture
# --------------------------------------------------------------------------- #
def test_intake_is_deterministic():
    idea = "alert on the pair spread between btc and eth"
    assert it.intake_strategy_idea(idea) == it.intake_strategy_idea(idea)


def test_intake_is_case_insensitive():
    a = it.intake_strategy_idea("FUNDING RATE ARBITRAGE RESEARCH")
    b = it.intake_strategy_idea("funding rate arbitrage research")
    assert a["answer"] == b["answer"] == it.ANSWER_YES


def test_every_decision_is_inert_and_human_gated():
    for idea in ("funding basis research", "auto trade everything", "something vague"):
        d = it.intake_strategy_idea(idea)
        assert d["human_review_required"] is True
        assert d["intake_starts_no_work"] is True
        assert d["next_required_action"] == "HUMAN_REVIEW_OF_INTAKE_DECISION"
        for key in (
            "executes", "writes_files", "runs_research", "runs_scanner",
            "runs_simulation", "runs_backtest", "runs_optimization", "fetches_data",
            "calls_api", "connects_broker", "connects_exchange", "uses_real_money",
            "uses_network", "uses_credentials", "contains_order_logic",
            "authorizes_paper_execution", "authorizes_micro_live",
            "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
        ):
            assert d[key] is False, (idea, key)
        assert d["paper_trading_gate_locked"] is True
        assert d["micro_live_gate_locked"] is True
        assert d["live_gate_locked"] is True


def test_non_string_non_dict_input_is_maybe_not_crash():
    d = it.intake_strategy_idea(12345)
    assert d["answer"] == it.ANSWER_MAYBE


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_all_answer_types():
    yes = it.intake_strategy_idea("funding rate arbitrage research")
    no = it.intake_strategy_idea("auto trade everything with my api key")
    maybe = it.intake_strategy_idea("a vague new thing")
    assert it.validate_intake_decision(yes)["valid"] is True
    assert it.validate_intake_decision(no)["valid"] is True
    assert it.validate_intake_decision(maybe)["valid"] is True


def test_validate_rejects_yes_without_lane_or_command():
    d = it.intake_strategy_idea("funding rate arbitrage research")
    d["lane"] = None
    v = it.validate_intake_decision(d)
    assert v["valid"] is False
    assert "yes_without_existing_lane" in v["errors"]
    d2 = it.intake_strategy_idea("funding rate arbitrage research")
    d2["next_safe_command"] = None
    v2 = it.validate_intake_decision(d2)
    assert v2["valid"] is False
    assert "yes_without_next_safe_command" in v2["errors"]


def test_validate_rejects_command_on_rejected_idea():
    d = it.intake_strategy_idea("auto trade everything")
    d["next_safe_command"] = "BUILD_SOMETHING"
    v = it.validate_intake_decision(d)
    assert v["valid"] is False
    assert "rejected_idea_carries_a_command" in v["errors"]


def test_validate_rejects_maybe_without_clarifications():
    d = it.intake_strategy_idea("a vague new thing")
    d["clarifications"] = []
    v = it.validate_intake_decision(d)
    assert v["valid"] is False
    assert "maybe_without_clarifications" in v["errors"]


def test_validate_rejects_work_starting_intake():
    d = it.intake_strategy_idea("funding rate arbitrage research")
    d["intake_starts_no_work"] = False
    v = it.validate_intake_decision(d)
    assert v["valid"] is False
    assert "intake_claims_to_start_work" in v["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    d = it.intake_strategy_idea("funding rate arbitrage research")
    d["micro_live_gate_locked"] = False
    v = it.validate_intake_decision(d)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])
    d2 = it.intake_strategy_idea("funding rate arbitrage research")
    d2["contains_order_logic"] = True
    v2 = it.validate_intake_decision(d2)
    assert v2["valid"] is False
    assert any("capability_not_false:contains_order_logic" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = it.render_intake_decision_markdown(
        it.intake_strategy_idea("funding rate arbitrage research")
    )
    assert md.startswith("# SPARTA Strategy Idea Intake Decision")
    assert "YES_RESEARCHABLE_NOW" in md
    assert "suggestion only, human must issue" in md
    assert "LOCKED" in md


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_label():
    assert it.get_strategy_idea_intake_label() == it.INTAKE_LABEL
    assert "READ-ONLY" in it.INTAKE_LABEL
    assert it.INTAKE_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in it.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_subprocess_or_credential_modules():
    with open(it.__file__, "r", encoding="utf-8") as fh:
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
