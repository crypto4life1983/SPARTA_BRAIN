"""Minimal integrity + anti-tamper tests for the Dux transcript evidence record.

PORTABLE: the committed suite validates the pinned provenance constants WITHOUT requiring the
git-ignored external transcript to exist. Optional strict verification against the real file is
skipped when the file is absent (clean checkout)."""
import hashlib

import pytest

import sparta_commander.dux_small_cap_short_family_transcript_evidence_contract as e


def test_1_provenance_pinned_portable_no_file_needed():
    # validates the pinned constants + storage status; reads NO external file
    r = e.build_dux_transcript_evidence()
    assert r["source_path"] == "manual_inputs/steven_dux_chart_fanatics_small_cap_short_transcript.txt"
    assert r["source_bytes"] == 58317
    assert r["source_sha256"] == "aa16a0e01f6bd3aeed521c81a88ad653890d350bf629a138ead842ae91380511"
    assert r["source_storage_status"] == "EXTERNAL_MANUAL_INPUT_NOT_BUNDLED_IN_COMMIT"
    assert r["transcript_is_bundled"] is False
    assert r["transcript_available_on_every_checkout"] is False
    assert r["repository_contains_source_bytes"] is False
    assert e.validate_dux_transcript_evidence(r)["valid"] is True
    # tamper with path / bytes / hash / storage status / bundled flags -> rejected
    for k, v in (("source_path", "other/path.txt"), ("source_sha256", "0" * 64),
                 ("source_bytes", 12345), ("source_storage_status", "BUNDLED"),
                 ("transcript_is_bundled", True),
                 ("transcript_available_on_every_checkout", True),
                 ("repository_contains_source_bytes", True)):
        bad = e.build_dux_transcript_evidence(); bad[k] = v
        assert e.validate_dux_transcript_evidence(bad)["valid"] is False, k


def test_1b_optional_strict_verification_against_real_transcript_if_present():
    res = e.verify_external_source(require_present=True)   # default path = repo transcript
    if res["present"] is False:
        pytest.skip("external transcript not present on this checkout (portable)")
    assert res["ok"] is True and res["matches"] is True
    assert res["actual_bytes"] == 58317
    assert res["actual_sha256"] == "aa16a0e01f6bd3aeed521c81a88ad653890d350bf629a138ead842ae91380511"


def test_1c_absent_source_ok_when_not_required(tmp_path):
    res = e.verify_external_source(path=str(tmp_path / "nope.txt"), require_present=False)
    assert res["present"] is False and res["ok"] is True
    assert res["reason"] == "external_source_not_present_ok_not_required"


def test_1d_absent_source_fails_when_required(tmp_path):
    res = e.verify_external_source(path=str(tmp_path / "nope.txt"), require_present=True)
    assert res["present"] is False and res["ok"] is False
    assert res["reason"] == "external_source_required_but_absent"


def test_1e_wrong_content_fails_in_both_modes(tmp_path):
    p = tmp_path / "wrong.txt"
    p.write_bytes(b"not the transcript")
    for req in (False, True):
        res = e.verify_external_source(path=str(p), require_present=req)
        assert res["present"] is True and res["ok"] is False and res["matches"] is False
        assert res["reason"] == "external_source_mismatch"


def test_2_three_playbooks_separate():
    r = e.build_dux_transcript_evidence()
    assert set(r["playbooks"]) == {"gap_up_short", "bounce_short", "first_red_day"}
    assert r["playbooks_combined"] is False
    bad = e.build_dux_transcript_evidence(); bad["combines_playbooks"] = True
    assert e.validate_dux_transcript_evidence(bad)["valid"] is False


def test_3_ticker_case_studies_are_transcript_evidence_only():
    r = e.build_dux_transcript_evidence()
    tickers = {c["ticker"] for c in r["case_studies"]}
    assert {"GME", "BYND", "DWAC", "CRCL", "BIRD", "EIQ", "SILVER", "AMC"} <= tickers
    cs = {c["ticker"]: c for c in r["case_studies"]}
    assert "UNCERTAIN" in cs["EIQ"]["transcription_uncertainty"].upper()
    assert "UNCERTAIN" in cs["SILVER"]["transcription_uncertainty"].upper()
    for c in r["case_studies"]:
        assert set(c) >= {"explicit_fact", "interpretation", "transcription_uncertainty",
                          "missing_visual", "unverified_claim"}


def test_4_trader_claims_and_numbers_non_evidence():
    r = e.build_dux_transcript_evidence()
    assert r["claims_are_non_evidence"] is True
    assert r["treats_claims_as_evidence"] is False
    assert r["numerical_priors_status"] == "TRADER_REPORTED_NON_EVIDENCE"
    assert r["remaining_reward_rule_is_evidence"] is False


def test_5_green_day_definition_unresolved():
    r = e.build_dux_transcript_evidence()
    assert r["green_day_definition_resolved"] is False
    bad = e.build_dux_transcript_evidence(); bad["green_day_definition_resolved"] = True
    assert e.validate_dux_transcript_evidence(bad)["valid"] is False


def test_6_initial_market_cap_heuristic_not_point_in_time_truth():
    r = e.build_dux_transcript_evidence()
    assert r["initial_market_cap_heuristic_unsafe_for_sparta"] is True
    assert r["accepts_initial_market_cap_heuristic_as_truth"] is False
    assert r["requires_point_in_time_shares_outstanding"] is True
    bad = e.build_dux_transcript_evidence(); bad["accepts_initial_market_cap_heuristic_as_truth"] = True
    assert e.validate_dux_transcript_evidence(bad)["valid"] is False


def test_7_genuine_vs_non_contradictions_classified_separately():
    r = e.build_dux_transcript_evidence()
    g = r["genuine_or_unresolved_contradictions"]
    n = r["non_contradictory_distinctions"]
    assert "projected_volume_multiplier_x5_vs_x10" in g
    assert "direct_gap_vs_intraday_ramp_win_rate_contradiction" in g
    assert "dwac_two_day_first_red_day_exception_vs_two_month_bounce_revisit" in n
    assert "total_spike_day_volume_vs_resistance_band_volume_refinement" in n
    assert set(g).isdisjoint(set(n))


def test_8_bounce_short_v1_not_modified_or_activated():
    r = e.build_dux_transcript_evidence()
    rel = r["relation_to_bounce_short_v1"]
    assert rel["bounce_short_v1_is_one_narrow_branch"] is True
    assert rel["mandatory_amendment_identified"] is False
    assert rel["activates_or_expands_bounce_short_v1"] is False
    assert r["modifies_bounce_short_v1"] is False and r["activates_bounce_short_v1"] is False


def test_9_all_operational_capabilities_false():
    r = e.build_dux_transcript_evidence()
    for flag in e._CAPABILITY_FLAGS_FALSE:
        assert r[flag] is False, flag
    for flag in ("is_candidate", "creates_candidate", "assigns_candidate_number",
                 "modifies_bounce_short_v1", "runs_event_study", "runs_backtest", "runs_replay",
                 "creates_labels", "fetches_data", "creates_scanner", "paper_trades",
                 "live_trades", "connects_broker", "purchases_locates", "changes_queue",
                 "changes_gate", "changes_lifecycle", "auto_commits", "auto_pushes"):
        assert r[flag] is False


def test_10_tamper_to_candidate_proven_executable_or_datafetch_rejected():
    for k, v in (("is_candidate", True), ("paper_trades", True), ("fetches_data", True),
                 ("treats_claims_as_evidence", True), ("classification", "STRATEGY_CANDIDATE")):
        r = e.build_dux_transcript_evidence(); r[k] = v
        assert e.validate_dux_transcript_evidence(r)["valid"] is False, k
