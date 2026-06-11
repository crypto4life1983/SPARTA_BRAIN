"""Tests for the SPARTA Arbitrage Factory V1 Data-Contract Chain Results Review.

Everything here is pure and in-memory; no network, no credentials, no API call, no
exchange connection, no staged-file read, no persistence, no scanner, no scheduler,
no gate is unlocked. Acceptance means chain coherence only -- never a seq 3
authorization."""

from __future__ import annotations

import ast

import sparta_commander.arbitrage_data_contract as dc
import sparta_commander.arbitrage_factory_v1_data_contract_results_review as rv
import sparta_commander.arbitrage_factory_v1_research_readiness_contract as ar
import sparta_commander.arbitrage_scanner_spec_contract as sp


def _chain():
    readiness = ar.build_arbitrage_factory_v1_readiness()
    spec = sp.record_arbitrage_scanner_spec(readiness)
    contract = dc.record_arbitrage_data_contract(spec)
    return readiness, spec, contract


# --------------------------------------------------------------------------- #
# the coherent chain is ACCEPTED with a full passing checklist
# --------------------------------------------------------------------------- #
def test_real_chain_review_is_accepted():
    r = rv.build_data_contract_results_review()
    assert r["verdict"] == rv.VERDICT_REVIEW_ACCEPTED
    assert r["blockers"] == []
    assert r["lane"] == "arbitrage_factory_v1"
    assert r["reviews_batch_step"] == 5
    assert r["covered_batch_id"] == "batch_aeb83ad9d637"
    assert r["next_required_action"] == "HUMAN_APPROVED_FEE_SLIPPAGE_MODEL"


def test_all_eight_checks_pass_on_the_real_chain():
    r = rv.build_data_contract_results_review()
    assert set(r["checklist_results"]) == set(rv.REVIEW_CHECKLIST)
    assert all(r["checklist_results"][name] is True
               for name in rv.REVIEW_CHECKLIST)
    assert len(rv.REVIEW_CHECKLIST) == 8


def test_seq_verdicts_are_recorded():
    r = rv.build_data_contract_results_review()
    assert r["seq_verdicts"] == {
        "seq0_readiness": ar.VERDICT_READINESS_READY,
        "seq1_scanner_spec": sp.VERDICT_SPEC_READY,
        "seq2_data_contract": dc.VERDICT_DATA_CONTRACT_READY,
    }


def test_acceptance_is_coherence_only_never_seq3_authorization():
    r = rv.build_data_contract_results_review()
    assert r["acceptance_means_chain_coherence_only"] is True
    assert r["acceptance_is_not_seq3_authorization"] is True
    assert r["seq3_requires_its_own_human_approval"] is True


def test_review_is_deterministic():
    assert (rv.build_data_contract_results_review()
            == rv.build_data_contract_results_review())


def test_review_chain_matches_build_on_real_objects():
    readiness, spec, contract = _chain()
    assert rv.review_chain(readiness, spec, contract) == (
        rv.build_data_contract_results_review())


# --------------------------------------------------------------------------- #
# broken chains are BLOCKED with named failed checks
# --------------------------------------------------------------------------- #
def test_missing_objects_block():
    r = rv.review_chain(None, None, None)
    assert r["verdict"] == rv.VERDICT_REVIEW_BLOCKED
    assert "chain_objects_missing_or_not_dicts" in r["blockers"]


def test_tampered_data_contract_blocks_review():
    readiness, spec, contract = _chain()
    contract["fetches_data"] = True  # breaks the seq 2 validator
    r = rv.review_chain(readiness, spec, contract)
    assert r["verdict"] == rv.VERDICT_REVIEW_BLOCKED
    assert "check_failed:seq2_data_contract_ready_and_valid" in r["blockers"]


def test_tampered_readiness_blocks_review():
    readiness, spec, contract = _chain()
    readiness["execution_capability_exists"] = True
    r = rv.review_chain(readiness, spec, contract)
    assert r["verdict"] == rv.VERDICT_REVIEW_BLOCKED
    assert "check_failed:seq0_readiness_ready_and_valid" in r["blockers"]


def test_blocked_chain_objects_block_review():
    readiness = ar.build_arbitrage_factory_v1_readiness()
    blocked_spec = sp.record_arbitrage_scanner_spec(None)
    blocked_contract = dc.record_arbitrage_data_contract(blocked_spec)
    r = rv.review_chain(readiness, blocked_spec, blocked_contract)
    assert r["verdict"] == rv.VERDICT_REVIEW_BLOCKED
    assert "check_failed:seq1_scanner_spec_ready_and_valid" in r["blockers"]


def test_mismatched_chain_fails_rebuild_identity_check():
    readiness, spec, contract = _chain()
    # a "valid-looking" contract that was not derived from this spec chain
    foreign = dc.record_arbitrage_data_contract(spec)
    foreign["staged_dataset_specs"]["funding_rates"]["file_pattern"] = (
        dc.STAGING_ROOT + "funding_renamed_{symbol}_{venue}.csv")
    r = rv.review_chain(readiness, spec, foreign)
    assert r["verdict"] == rv.VERDICT_REVIEW_BLOCKED
    assert any("explicit_gating_identical_to_standalone_rebuild" in b
               or "seq2_data_contract_ready_and_valid" in b
               for b in r["blockers"])


# --------------------------------------------------------------------------- #
# posture
# --------------------------------------------------------------------------- #
def test_review_is_inert_on_all_paths():
    reviews = [
        rv.build_data_contract_results_review(),
        rv.review_chain(None, None, None),
    ]
    for r in reviews:
        assert r["review_reads_no_staged_files"] is True
        assert r["review_persists_nothing"] is True
        assert r["human_review_required"] is True
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
            assert r[key] is False, key
        assert r["paper_trading_gate_locked"] is True
        assert r["micro_live_gate_locked"] is True
        assert r["live_gate_locked"] is True


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_accepted_and_blocked():
    assert rv.validate_data_contract_results_review(
        rv.build_data_contract_results_review())["valid"] is True
    assert rv.validate_data_contract_results_review(
        rv.review_chain(None, None, None))["valid"] is True


def test_validate_rejects_accepted_with_failed_check():
    r = rv.build_data_contract_results_review()
    r["checklist_results"]["capabilities_all_false_across_chain"] = False
    v = rv.validate_data_contract_results_review(r)
    assert v["valid"] is False
    assert "accepted_with_failed_check" in v["errors"]


def test_validate_rejects_accepted_with_partial_checklist():
    r = rv.build_data_contract_results_review()
    del r["checklist_results"]["tampered_upstream_refuses_downstream"]
    v = rv.validate_data_contract_results_review(r)
    assert v["valid"] is False
    assert "accepted_without_full_checklist" in v["errors"]


def test_validate_rejects_authorization_claims():
    r = rv.build_data_contract_results_review()
    r["acceptance_is_not_seq3_authorization"] = False
    v = rv.validate_data_contract_results_review(r)
    assert v["valid"] is False
    assert "acceptance_claims_authorization" in v["errors"]
    r2 = rv.build_data_contract_results_review()
    r2["seq3_requires_its_own_human_approval"] = False
    v2 = rv.validate_data_contract_results_review(r2)
    assert v2["valid"] is False
    assert "seq3_approval_dropped" in v2["errors"]


def test_validate_rejects_tampered_checklist_or_batch_identity():
    r = rv.build_data_contract_results_review()
    r["checklist"] = r["checklist"][:3]
    v = rv.validate_data_contract_results_review(r)
    assert v["valid"] is False
    assert "checklist_tampered" in v["errors"]
    r2 = rv.build_data_contract_results_review()
    r2["covered_batch_id"] = "batch_other"
    v2 = rv.validate_data_contract_results_review(r2)
    assert v2["valid"] is False
    assert "wrong_batch_id" in v2["errors"]


def test_validate_rejects_persistence_or_staged_read_claims():
    r = rv.build_data_contract_results_review()
    r["review_persists_nothing"] = False
    v = rv.validate_data_contract_results_review(r)
    assert v["valid"] is False
    assert "review_persists" in v["errors"]
    r2 = rv.build_data_contract_results_review()
    r2["review_reads_no_staged_files"] = False
    v2 = rv.validate_data_contract_results_review(r2)
    assert v2["valid"] is False
    assert "review_reads_staged_files" in v2["errors"]


def test_validate_rejects_unlocked_gate_or_capability():
    r = rv.build_data_contract_results_review()
    r["live_gate_locked"] = False
    v = rv.validate_data_contract_results_review(r)
    assert v["valid"] is False
    assert any("gate_not_locked:live_gate_locked" in e for e in v["errors"])
    r2 = rv.build_data_contract_results_review()
    r2["runs_scanner"] = True
    v2 = rv.validate_data_contract_results_review(r2)
    assert v2["valid"] is False
    assert any("capability_not_false:runs_scanner" in e for e in v2["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_accepted_and_blocked():
    md = rv.render_data_contract_results_review_markdown(
        rv.build_data_contract_results_review())
    assert md.startswith(
        "# SPARTA Arbitrage Factory V1 Data-Contract Chain Results Review")
    assert "chain coherence ONLY" in md
    assert "[PASS]" in md and "[FAIL]" not in md
    assert "LOCKED" in md
    md2 = rv.render_data_contract_results_review_markdown(
        rv.review_chain(None, None, None))
    assert "review does not accept the chain" in md2


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_review_label():
    assert rv.get_data_contract_results_review_label() == rv.REVIEW_LABEL
    assert "READ-ONLY" in rv.REVIEW_LABEL
    assert "REVIEW ONLY" in rv.REVIEW_LABEL
    assert rv.REVIEW_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rv.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_exchange_or_credential_modules():
    with open(rv.__file__, "r", encoding="utf-8") as fh:
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
