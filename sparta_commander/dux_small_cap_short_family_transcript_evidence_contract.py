"""Steven Dux small-cap short family -- TRANSCRIPT EVIDENCE RECORD (PURE, READ-ONLY,
EVIDENCE-ONLY; NOT A STRATEGY CANDIDATE).

Human-approved build token: HUMAN_APPROVED_BUILD_DUX_FAMILY_TRANSCRIPT_EVIDENCE_RECORD_ONLY.
Classification: TRANSCRIPT_EVIDENCE_ONLY_NOT_A_STRATEGY_CANDIDATE.

A durable, hash-pinned record of what the verified Dux transcript actually establishes -- the
three playbooks kept strictly separate, the per-ticker case studies (explicit fact vs
interpretation vs transcription/instrument uncertainty vs missing chart visual vs unverified
claim), the numerical priors (all TRADER_REPORTED_NON_EVIDENCE), and the genuine-vs-non
contradiction classification. It computes nothing, creates no candidate, and does not activate
or amend the committed Bounce Short V1 spec. The validator pins source provenance (byte size +
SHA-256) and rejects any tamper toward candidate / proven / executable / data-fetching status.
"""
from __future__ import annotations

from typing import Any

DXE_SCHEMA_VERSION = 1
DXE_MODE = "RESEARCH_ONLY"
DXE_CLASSIFICATION = "TRANSCRIPT_EVIDENCE_ONLY_NOT_A_STRATEGY_CANDIDATE"
RECORD_ID = "DUX_SMALL_CAP_SHORT_FAMILY_TRANSCRIPT_EVIDENCE"
APPROVAL_TOKEN = "HUMAN_APPROVED_BUILD_DUX_FAMILY_TRANSCRIPT_EVIDENCE_RECORD_ONLY"

# --- pinned source provenance (validator rejects a different path / hash / byte size) -------
# The transcript is an EXTERNAL manual input: it is git-ignored (.gitignore: manual_inputs/),
# NOT tracked, and NOT bundled in any commit. The provenance below is pinned as constants so
# the committed suite validates portably WITHOUT the file existing on a clean checkout.
SOURCE_PATH = "manual_inputs/steven_dux_chart_fanatics_small_cap_short_transcript.txt"
SOURCE_BYTES = 58317
SOURCE_SHA256 = "aa16a0e01f6bd3aeed521c81a88ad653890d350bf629a138ead842ae91380511"
SOURCE_STORAGE_STATUS = "EXTERNAL_MANUAL_INPUT_NOT_BUNDLED_IN_COMMIT"

import os as _os  # noqa: E402  (used only by the OPTIONAL local verifier below)
_REPO_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))


def verify_external_source(path: str | None = None, require_present: bool = False) -> dict:
    """OPTIONAL local helper (the only I/O in this module; NOT called by build/validate).
    Verifies the external transcript against the pinned size + SHA-256 when present.
    - present + match          -> ok=True.
    - present + size/hash diff  -> ok=False (fails in BOTH modes).
    - absent + require_present=False -> ok=True, present=False (portable: does not fail).
    - absent + require_present=True  -> ok=False (fails clearly).
    Never mutates the file."""
    import hashlib
    p = path if path is not None else _os.path.join(_REPO_ROOT, SOURCE_PATH)
    if not _os.path.isfile(p):
        return {"present": False, "matches": None,
                "ok": (not require_present),
                "reason": ("external_source_not_present_ok_not_required" if not require_present
                           else "external_source_required_but_absent")}
    raw = open(p, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    matches = (len(raw) == SOURCE_BYTES and sha == SOURCE_SHA256)
    return {"present": True, "matches": matches, "ok": matches,
            "actual_bytes": len(raw), "actual_sha256": sha,
            "reason": ("external_source_verified" if matches else "external_source_mismatch")}

# --- three playbooks -- kept strictly separate (no combined stats/entries/ratios/horizons) --
PLAYBOOKS = {
    "gap_up_short": "current-day demand exhaustion; morning gap >100%, push 20-35%, "
                    "enter on first weakness after ~1h consolidation; win ~75%+, ~50-70/yr",
    "bounce_short": "historical trapped supply vs weaker current demand; ~2-month flat after a "
                    "prior high-volume spike, gap back into the resistance band; win 80-85%, ~30/yr",
    "first_red_day": "multi-day dollar-volume exhaustion; >=3 consecutive higher-volume green "
                     "days (3-day >=300% / 2-day >=1000%); 1/4 starter + following-day entry; "
                     "win up to 90%, ~5-10/yr",
}

# --- per-ticker case studies (transcript-grounded; separated by evidence kind) --------------
CASE_STUDIES = (
    {"ticker": "GME", "playbook": "bounce_short",
     "explicit_fact": "volume estimate ~10:1; opened and instantly crashed ~50%",
     "interpretation": "cited as the high-ratio bounce-short archetype",
     "transcription_uncertainty": None,
     "missing_visual": "no date/price chart; 'very early in the days' undated",
     "unverified_claim": "~$1.5M made in ~15 minutes"},
    {"ticker": "BYND", "playbook": "first_red_day",
     "explicit_fact": "described as a 'natural/standard' first red day this year; 'almost "
                      "fitted the range'",
     "interpretation": "used as the canonical first-red-day example",
     "transcription_uncertainty": "'BD chart beyond me' = Beyond Meat / BYND",
     "missing_visual": "exact entries/dates absent",
     "unverified_claim": "~$7M trade (could have pushed 12-13M; size cost ~5-6% extra)"},
    {"ticker": "DWAC", "playbook": "first_red_day",
     "explicit_fact": "two-session exception; two-day variant requires ~1,000% range",
     "interpretation": "example of the 2-day range exception",
     "transcription_uncertainty": None,
     "missing_visual": "no dates/prices; visual only",
     "unverified_claim": "trader states he made 'the DWAC trade' (amount unspecified)"},
    {"ticker": "CRCL", "playbook": "first_red_day",
     "explicit_fact": "IPO variant; IPO initial market cap ~$300-500M associated with a "
                      "~$30B dollar-exhaustion block",
     "interpretation": "example that IPO dollar-blocks scale far higher",
     "transcription_uncertainty": "figures garbled ('3 500 millions'); treat as UNCERTAIN",
     "missing_visual": "no chart; block figure approximate",
     "unverified_claim": "~$30B exhaustion block (non-evidence, uncertain)"},
    {"ticker": "BIRD", "playbook": "gap_up_short_avoidance",
     "explicit_fact": "~70M premarket shares; >50M premarket => not tradable via gap-up short; "
                      "next-day gap-down volume dry-up is the short opportunity",
     "interpretation": "example of a CROWDED gap-up to AVOID same-day",
     "transcription_uncertainty": None,
     "missing_visual": "exact levels/dates absent",
     "unverified_claim": None},
    {"ticker": "EIQ", "playbook": "gap_up_short_low_float_variation",
     "explicit_fact": "spike $3 -> 9 -> top ~12 -> fade; ~30M traded; ~700k float; "
                      ">15x float rotation not ideal; low-float => wait for 50%-drop-then-bounce",
     "interpretation": "ultra-low-float gap-up variation",
     "transcription_uncertainty": "TICKER SYMBOL UNCERTAIN -- transcript says 'EIQ' (operator "
                                  "referenced 'EEIQ/EIQ'); exact symbol unresolved",
     "missing_visual": "no dated chart",
     "unverified_claim": None},
    {"ticker": "SILVER", "playbook": "first_red_day",
     "explicit_fact": "first-red-day illustration; remaining-reward rule (avoid when >~50% of "
                      "the entire run already erased); entire gain from ~$50; short ~92-93 'doable'",
     "interpretation": "classic first-red-day pattern used as illustration",
     "transcription_uncertainty": "INSTRUMENT IDENTITY UNCERTAIN -- 'silver' only; SLV ETF vs "
                                  "silver futures vs a silver-named equity unresolved",
     "missing_visual": "no dated chart; $50/92-93 imply a high-priced instrument",
     "unverified_claim": "trader 'got scarred', missed the clean entry (self-reported)"},
    {"ticker": "AMC", "playbook": None,
     "explicit_fact": "mentioned ONLY as a hyped exception (~2-3x/yr) alongside GME",
     "interpretation": "hyped-runner exception, not a worked setup",
     "transcription_uncertainty": None,
     "missing_visual": "no setup shown",
     "unverified_claim": None},
)

# --- additional evidence points -------------------------------------------------------------
GREEN_DAY_DEFINITION_NOTE = (
    "'green day' in First Red Day likely means positive close-to-close performance rather than "
    "candle-body color, but this is UNRESOLVED and must not be silently frozen")
GREEN_DAY_DEFINITION_RESOLVED = False

REMAINING_REWARD_RULE = (
    "a First Red Day entry may be unattractive when more than ~50% of the entire run has "
    "already been erased (TRADER_REPORTED_NON_EVIDENCE)")

INITIAL_MARKET_CAP_HEURISTIC = "estimated_initial_market_cap ~= current_market_cap / price_multiple"
INITIAL_MARKET_CAP_HEURISTIC_UNSAFE_FOR_SPARTA = True
INITIAL_MARKET_CAP_HEURISTIC_UNSAFE_REASON = (
    "fails when point-in-time shares outstanding change via dilution, offerings, warrants, "
    "reverse splits or corporate actions; SPARTA must require point-in-time shares outstanding")
REQUIRES_POINT_IN_TIME_SHARES_OUTSTANDING = True

PRIOR_CHART_REGIME_FEATURE = ("long_term_downtrend_beaten_down", "flat_base", "other_or_unknown")
PRIOR_CHART_REGIME_PREDICTIVE_RANKING_ASSERTED = False

DIRECT_GAP_BOUNCE_LIGHT_PREMARKET_VOLUME = "approx_3M_to_5M"   # non-evidence, direct-gap only

FOLLOWING_SESSION_FIRST_RED_DAY = {
    "following_green_or_strong_session": "do_not_short_in_the_illustrated_process",
    "following_red_or_weak_session": "may_qualify",
    "entry_stage_relationships_resolved": False,
}

# --- contradiction classification -----------------------------------------------------------
GENUINE_OR_UNRESOLVED_CONTRADICTIONS = (
    "projected_volume_multiplier_x5_vs_x10",
    "direct_gap_vs_intraday_ramp_win_rate_contradiction",
    "preferred_market_cap_below_100M_vs_hard_rejection_above_200M",
    "no_size_limit_vs_admitted_market_impact_slippage",
    "exact_first_red_day_starter_and_main_entry_sequence",
)
NON_CONTRADICTORY_DISTINCTIONS = (
    "dwac_two_day_first_red_day_exception_vs_two_month_bounce_revisit",
    "raw_volume_vs_later_dollar_volume_clarification",
    "quarter_size_starter_vs_later_main_entry_not_proven_mutually_exclusive",
    "total_spike_day_volume_vs_resistance_band_volume_refinement",
)

# --- numerical priors -- ALL TRADER_REPORTED_NON_EVIDENCE -----------------------------------
NUMERICAL_PRIORS = {
    "price_min": ">$3",
    "initial_market_cap": "1-100M (gap-up reject >200M / <100M; first-red-day <200M)",
    "float": "1-50M (bands 1-2M / 2-5M / 5-10M / 10-20M)",
    "premarket_attention_volume": ">50M",
    "projected_volume_multiplier": "x5 to x10",
    "gap_and_push": "gap-up >100%; push 20-35%; bounce open plummet 15-20%",
    "float_rotation_warning": ">15x not ideal",
    "dollar_block": "bounce >=150M; first-red-day scales by init-cap; IPO(CRCL) ~30B",
    "trapped_supply_ratio": "1:1 / 2:1 / seen 10:1",
    "frequency": "gap-up 50-70/yr; bounce ~30/yr; first-red-day 5-10/yr; GME/AMC 2-3/yr",
    "win_rate": "gap-up 75%+; bounce 80-85%; first-red-day up to 90%",
    "fade": "gap-up ~26%; bounce ~50% (ramp) / ~75% (direct-gap variant)",
    "risk_and_rr": "avg risk ~7%; R/R ~1:3.5",
    "participation": "<=10% float, <=1% volume, <=30% of cap/float",
    "size": "gap-up/bounce max ~1-1.2M avg 200-300k; first-red-day millions/billions",
}

RELATION_TO_BOUNCE_SHORT_V1 = {
    "bounce_short_v1_is_one_narrow_branch": True,
    "mandatory_amendment_identified": False,
    "activates_or_expands_bounce_short_v1": False,
    "missing_layers": ("visual_chart_details", "proprietary_statistics",
                       "short_borrow_information", "execution_layers"),
}

_CAPABILITY_FLAGS_FALSE = (
    "is_candidate", "creates_candidate", "assigns_candidate_number", "modifies_bounce_short_v1",
    "runs_event_study", "runs_backtest", "runs_replay", "creates_labels", "fetches_data",
    "creates_scanner", "paper_trades", "live_trades", "connects_broker", "purchases_locates",
    "changes_queue", "changes_gate", "changes_lifecycle", "auto_commits", "auto_pushes",
    "treats_claims_as_evidence", "combines_playbooks",
    "accepts_initial_market_cap_heuristic_as_truth", "activates_bounce_short_v1",
    "crosses_into_forbidden_gate",
)


def build_dux_transcript_evidence() -> dict[str, Any]:
    """PURE. Assemble the hash-pinned transcript evidence record. No I/O; authorizes/advances
    nothing."""
    record: dict[str, Any] = {
        "schema_version": DXE_SCHEMA_VERSION, "mode": DXE_MODE,
        "classification": DXE_CLASSIFICATION, "record_id": RECORD_ID,
        "approved_via": APPROVAL_TOKEN,
        "is_transcript_evidence_only": True, "is_candidate": False, "is_proposal": False,
        # provenance (pinned constants; portable -- does NOT require the file to exist)
        "source_path": SOURCE_PATH, "source_bytes": SOURCE_BYTES, "source_sha256": SOURCE_SHA256,
        "source_storage_status": SOURCE_STORAGE_STATUS,
        "transcript_modified": False,
        "transcript_is_bundled": False,
        "transcript_available_on_every_checkout": False,
        "repository_contains_source_bytes": False,
        # playbooks (separate)
        "playbooks": dict(PLAYBOOKS), "playbooks_combined": False,
        # case studies
        "case_studies": [dict(c) for c in CASE_STUDIES],
        # additional evidence points
        "green_day_definition_note": GREEN_DAY_DEFINITION_NOTE,
        "green_day_definition_resolved": GREEN_DAY_DEFINITION_RESOLVED,
        "remaining_reward_rule": REMAINING_REWARD_RULE,
        "remaining_reward_rule_is_evidence": False,
        "initial_market_cap_heuristic": INITIAL_MARKET_CAP_HEURISTIC,
        "initial_market_cap_heuristic_unsafe_for_sparta": INITIAL_MARKET_CAP_HEURISTIC_UNSAFE_FOR_SPARTA,
        "initial_market_cap_heuristic_unsafe_reason": INITIAL_MARKET_CAP_HEURISTIC_UNSAFE_REASON,
        "requires_point_in_time_shares_outstanding": REQUIRES_POINT_IN_TIME_SHARES_OUTSTANDING,
        "accepts_initial_market_cap_heuristic_as_truth": False,
        "prior_chart_regime_feature": list(PRIOR_CHART_REGIME_FEATURE),
        "prior_chart_regime_predictive_ranking_asserted": PRIOR_CHART_REGIME_PREDICTIVE_RANKING_ASSERTED,
        "direct_gap_bounce_light_premarket_volume": DIRECT_GAP_BOUNCE_LIGHT_PREMARKET_VOLUME,
        "following_session_first_red_day": dict(FOLLOWING_SESSION_FIRST_RED_DAY),
        # contradictions
        "genuine_or_unresolved_contradictions": list(GENUINE_OR_UNRESOLVED_CONTRADICTIONS),
        "non_contradictory_distinctions": list(NON_CONTRADICTORY_DISTINCTIONS),
        # numerical priors (non-evidence)
        "numerical_priors": dict(NUMERICAL_PRIORS),
        "numerical_priors_status": "TRADER_REPORTED_NON_EVIDENCE",
        "claims_are_non_evidence": True,
        # relation to V1
        "relation_to_bounce_short_v1": {
            k: (list(v) if isinstance(v, tuple) else v)
            for k, v in RELATION_TO_BOUNCE_SHORT_V1.items()},
        # posture
        "advances_nothing": True, "human_review_required": True,
        "next_gate": "NONE_EVIDENCE_ONLY_FUTURE_WORK_REQUIRES_NEW_HUMAN_APPROVAL",
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_candidate": True, "no_modify_bounce_short_v1": True, "no_activate_bounce_short_v1": True,
        "no_event_study": True, "no_backtest": True, "no_replay": True, "no_labels": True,
        "no_data_fetch": True, "no_scanner": True, "no_paper_trades": True, "no_live_trades": True,
        "no_broker": True, "no_locate_purchase": True, "no_change_queue": True,
        "no_change_gate": True, "no_change_lifecycle": True, "no_auto_commit": True,
        "no_auto_push": True, "no_treat_claims_as_evidence": True, "no_combine_playbooks": True,
        "no_accept_market_cap_heuristic_as_truth": True, "no_modify_transcript": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_dux_transcript_evidence(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid ONLY when research/evidence-only; source byte size + SHA-256
    match the pinned values; the three playbooks are present and not combined; case studies are
    transcript-evidence only (incl. EIQ symbol + silver instrument uncertainty); trader claims
    and numerical priors are non-evidence; the green-day definition is unresolved; the
    initial-market-cap heuristic is unsafe/not-accepted-as-truth; genuine vs non-contradiction
    sets are exact; Bounce Short V1 is neither modified nor activated; and every capability flag
    is False."""
    f: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record
    if r.get("mode") != DXE_MODE:
        f.append("mode_not_research_only")
    if r.get("classification") != DXE_CLASSIFICATION:
        f.append("classification_wrong")
    if r.get("is_transcript_evidence_only") is not True:
        f.append("not_evidence_only")
    if r.get("is_candidate") is not False or r.get("is_proposal") is not False:
        f.append("must_not_be_candidate_or_proposal")
    # provenance pinned (path + bytes + hash + external/not-bundled status)
    if r.get("source_path") != SOURCE_PATH:
        f.append("source_path_mismatch")
    if r.get("source_bytes") != SOURCE_BYTES:
        f.append("source_bytes_mismatch")
    if r.get("source_sha256") != SOURCE_SHA256:
        f.append("source_sha256_mismatch")
    if r.get("source_storage_status") != SOURCE_STORAGE_STATUS:
        f.append("source_storage_status_mismatch")
    if r.get("transcript_modified") is not False:
        f.append("transcript_must_not_be_modified")
    # external / not-bundled invariants -- all must remain False
    if r.get("transcript_is_bundled") is not False:
        f.append("transcript_must_not_be_bundled")
    if r.get("transcript_available_on_every_checkout") is not False:
        f.append("transcript_must_not_be_claimed_available_on_every_checkout")
    if r.get("repository_contains_source_bytes") is not False:
        f.append("repository_must_not_claim_source_bytes")
    # playbooks separate
    for pb in ("gap_up_short", "bounce_short", "first_red_day"):
        if pb not in (r.get("playbooks") or {}):
            f.append("missing_playbook:%s" % pb)
    if r.get("playbooks_combined") is not False or r.get("combines_playbooks") is not False:
        f.append("playbooks_must_not_be_combined")
    # case studies present incl. required uncertainties
    cs = {c.get("ticker"): c for c in (r.get("case_studies") or [])}
    for tk in ("GME", "BYND", "DWAC", "CRCL", "BIRD", "EIQ", "SILVER", "AMC"):
        if tk not in cs:
            f.append("missing_case_study:%s" % tk)
    if "EIQ" in cs and "UNCERTAIN" not in str(cs["EIQ"].get("transcription_uncertainty") or "").upper():
        f.append("eiq_symbol_uncertainty_missing")
    if "SILVER" in cs and "UNCERTAIN" not in str(cs["SILVER"].get("transcription_uncertainty") or "").upper():
        f.append("silver_instrument_uncertainty_missing")
    # non-evidence
    if r.get("claims_are_non_evidence") is not True or r.get("treats_claims_as_evidence") is not False:
        f.append("claims_must_be_non_evidence")
    if r.get("numerical_priors_status") != "TRADER_REPORTED_NON_EVIDENCE":
        f.append("priors_must_be_non_evidence")
    if r.get("remaining_reward_rule_is_evidence") is not False:
        f.append("remaining_reward_rule_must_be_non_evidence")
    # green-day unresolved
    if r.get("green_day_definition_resolved") is not False:
        f.append("green_day_definition_must_be_unresolved")
    # initial-market-cap heuristic unsafe / not truth / requires PIT shares
    if r.get("initial_market_cap_heuristic_unsafe_for_sparta") is not True:
        f.append("market_cap_heuristic_must_be_unsafe")
    if r.get("accepts_initial_market_cap_heuristic_as_truth") is not False:
        f.append("market_cap_heuristic_must_not_be_accepted_as_truth")
    if r.get("requires_point_in_time_shares_outstanding") is not True:
        f.append("must_require_point_in_time_shares_outstanding")
    # prior-chart-regime: no predictive ranking
    if r.get("prior_chart_regime_predictive_ranking_asserted") is not False:
        f.append("no_prior_chart_regime_ranking_may_be_asserted")
    # contradiction classification exact
    if tuple(r.get("genuine_or_unresolved_contradictions") or ()) != GENUINE_OR_UNRESOLVED_CONTRADICTIONS:
        f.append("genuine_contradictions_tampered")
    if tuple(r.get("non_contradictory_distinctions") or ()) != NON_CONTRADICTORY_DISTINCTIONS:
        f.append("non_contradiction_set_tampered")
    # relation to V1: not modified / not activated
    rel = r.get("relation_to_bounce_short_v1") or {}
    if rel.get("activates_or_expands_bounce_short_v1") is not False:
        f.append("must_not_activate_or_expand_v1")
    if rel.get("bounce_short_v1_is_one_narrow_branch") is not True:
        f.append("must_state_v1_is_one_branch")
    if r.get("modifies_bounce_short_v1") is not False or r.get("activates_bounce_short_v1") is not False:
        f.append("must_not_modify_or_activate_v1")
    if r.get("advances_nothing") is not True:
        f.append("must_advance_nothing")
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            f.append("capability_flag_true:%s" % flag)
    return {"valid": not f, "failures": f}
