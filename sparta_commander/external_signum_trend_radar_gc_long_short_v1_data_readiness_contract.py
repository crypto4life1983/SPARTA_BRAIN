"""Candidate #22 -- external_signum_trend_radar_gc_long_short_v1
-- REAL-CANDLE DATA-READINESS REVIEW (PURE, RESEARCH ONLY).

Determines, deterministically and read-only, whether a frozen local dataset suitable for
C22 REAL-CANDLE LABEL generation EXISTS. Chain-gated on the frozen C22 detector dry-run
(C22_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW, pinned commit cfad8ab7).

HONEST CONCLUSION -- DATA_NOT_READY. The C22 detector, faithful to the frozen spec,
consumes the SIGNUM "Trend Radar" daily `gc` DETECTOR output: per asset, per CLOSED daily
candle, it needs the PROVIDER-SUPPLIED indicator fields gc.trend ("Green"/"Red"/"Grey"),
gc.upper (the upper GC band) and gc.filter (the centre line), plus the asset-row fields
breakoutDate and a unique numeric market_rank, plus a pair price + cmcRefPriceUsd for the
ticker-collision guard, plus the bot HOLDINGS / NAV context. These are a PROPRIETARY
provider indicator, NOT standard OHLCV.

No frozen local dataset supplies them:
  * the committed crypto datasets (crypto_basis_funding_research, crypto_d1_spot, etc.)
    are OHLCV + funding only -- they carry NO gc.trend / gc.upper / gc.filter bands, NO
    breakoutDate, NO market_rank, NO Trend-Radar row structure;
  * the gc bands cannot be DERIVED from raw OHLCV here -- the spec treats them as
    provider-supplied and does NOT define the Trend-Radar `gc` indicator formula;
    computing them would INVENT rules (forbidden);
  * they cannot be FETCHED -- the Signum / MCP / Hyperliquid integration is hard-locked.

Therefore this review STOPS at DATA_NOT_READY: it produces NO labels, NO artifacts, and
NOTHING to SHA-pin. It declares EXACTLY the frozen, operator-staged Trend-Radar gc-detector
dataset that would be required (path + source + retrieval-UTC + SHA256 + >=50 line items +
the gc fields + breakoutDate + unique numeric market_rank + per-asset closed daily candles
+ the holdings/NAV snapshot context) before a separate, freshly-authorised labels run.

It builds NO labels, runs NO detector on real data, fetches NO data, connects to NOTHING
(no Signum / MCP / Hyperliquid / API / credentials), edits NO bot, sends NO email/trade,
and touches NO replay / paper / live / broker / order / scheduler surface. Every capability
flag is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_detector_spec_dry_run_contract as _dr  # noqa: E501

DRD22_SCHEMA_VERSION = 1
DRD22_MODE = "RESEARCH_ONLY"
DRD22_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _dr.CANDIDATE_ID                 # "C22"
CANDIDATE_TOKEN = _dr.CANDIDATE_TOKEN
CANDIDATE_FAMILY = _dr.CANDIDATE_FAMILY
CANDIDATE_NAME = _dr.CANDIDATE_NAME

# pinned committed detector dry-run this readiness review is chain-gated on.
DETECTOR_DRY_RUN_COMMIT = "cfad8ab7b4c5b9a2435658985950c6efc17497fe"
EXPECTED_DETECTOR_VERDICT = "C22_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"

VERDICT_DATA_NOT_READY = "DATA_NOT_READY"
# the verdict that a FUTURE, separately-authorised review could reach once an operator
# stages a real Trend-Radar gc-detector dataset (declared here, NOT produced now).
VERDICT_WOULD_BE_READY = "FROZEN_AND_READY_FOR_RESEARCH_ONLY_C22_TREND_RADAR_LABELS"

GATE_SEQUENCE = tuple(_dr.GATE_SEQUENCE)
NEXT_HUMAN_ACTION = (
    "HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET_THEN_REAUTHORISE_C22_LABELS")

# --- the EXACT data fields the C22 detector requires (from the frozen spec) ---
REQUIRED_DATA_FIELDS = {
    "per_trend_radar_row": ("symbol", "market_rank (unique numeric)", "breakoutDate",
                            "pair_price_usd", "cmcRefPriceUsd"),
    "per_closed_daily_candle": ("ohlc.h", "ohlc.c", "gc.trend (Green/Red/Grey)",
                                "gc.upper (upper GC band)", "gc.filter (centre line)"),
    "run_context": ("bot HOLDINGS (symbol/side/usd_notional + short collateral/uPnL/"
                    "size_base)", "NAV snapshot", "trading_account == perpetual"),
    "minimum_line_items": _dr.MIN_LINE_ITEMS,   # 50
    "all_assets_non_stablecoin": True,
}

# --- the frozen local datasets that EXIST, and why none are suitable ----------
SURVEYED_LOCAL_DATASETS = (
    {"path": "data/crypto_basis_funding_research/raw",
     "contents": "BTC/ETH/SOL daily spot/perp OHLCV + funding",
     "supplies_trend_radar_gc_fields": False,
     "reason": "OHLCV + funding only; no gc.trend/gc.upper/gc.filter, no breakoutDate, "
               "no market_rank, no Trend-Radar row structure"},
    {"path": "data/crypto_d1_spot",
     "contents": "daily crypto spot OHLCV",
     "supplies_trend_radar_gc_fields": False,
     "reason": "OHLCV only; no provider gc-detector indicator fields"},
    {"path": "data/mechanically_neutral_spot_perp_basis_funding_carry_c20 / "
             "low_turnover_same_asset_spot_perp_funding_carry_c21",
     "contents": "C20/C21 gitignored label artifacts over the spot/perp/funding data",
     "supplies_trend_radar_gc_fields": False,
     "reason": "carry-study artifacts; unrelated to the Trend-Radar gc detector"},
)

# --- the reasons the data is not ready (none of which can be worked around) ---
DATA_NOT_READY_REASONS = (
    "the C22 detector requires the SIGNUM Trend-Radar daily 'gc' detector output "
    "(gc.trend / gc.upper / gc.filter bands + breakoutDate + unique numeric market_rank "
    "per asset per closed daily candle) -- a PROPRIETARY provider indicator, not OHLCV",
    "NO frozen local dataset supplies these fields (the committed crypto datasets are "
    "OHLCV + funding only)",
    "the gc bands cannot be DERIVED from raw OHLCV: the frozen spec treats them as "
    "provider-supplied and does not define the Trend-Radar 'gc' indicator formula -- "
    "computing them would INVENT rules, which is forbidden",
    "the data cannot be FETCHED: the Signum / MCP / Hyperliquid integration is "
    "hard-locked (no connection, no API keys, no credentials)",
)

# --- what an operator must stage before a future, separately-authorised run ---
REQUIRED_OPERATOR_STAGED_DATASET = {
    "must_be": "a FROZEN, deterministic local Trend-Radar gc-detector daily export",
    "provenance_required": ("local path", "source/provider", "retrieval_utc",
                            "recomputable SHA256 per file", "attestation"),
    "must_contain_fields": REQUIRED_DATA_FIELDS["per_trend_radar_row"]
    + REQUIRED_DATA_FIELDS["per_closed_daily_candle"],
    "minimum_line_items": _dr.MIN_LINE_ITEMS,
    "must_be_non_stablecoin_assets": True,
    "then": ("a SEPARATE, freshly human-authorised C22 real-candle labels run that "
             "SHA-pins the frozen dataset before reading it"),
    "sparta_fetches_nothing": True,
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "produces_labels", "runs_detector_on_real_candles",
    "runs_labels", "runs_replay", "computes_pnl", "optimizes_parameters",
    "tunes_parameters", "edits_rules", "derives_provider_indicator", "invents_indicator",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data", "auto_commits",
    "auto_pushes", "modifies_scheduler", "installs_scheduler", "sends_notifications",
    "sends_email", "calls_api", "uses_network", "uses_credentials", "uses_api_keys",
    "connects_signum", "uses_mcp", "accesses_hyperliquid", "connects_broker",
    "connects_exchange", "sends_trades", "edits_bots", "sets_trading_pair",
    "converts_funds", "creates_claude_routines", "uses_real_money", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "claims_data_ready", "claims_profitability",
    "crosses_into_forbidden_gate",
)


def get_c22_data_readiness_label() -> str:
    return (
        "Candidate #22 external_signum_trend_radar_gc_long_short_v1 real-candle "
        "DATA-READINESS review (READ-ONLY, RESEARCH ONLY). VERDICT = DATA_NOT_READY: the "
        "C22 detector needs the proprietary Signum Trend-Radar daily 'gc' detector fields "
        "(gc.trend / gc.upper / gc.filter + breakoutDate + unique numeric market_rank per "
        "asset per closed candle), which NO frozen local dataset supplies, which cannot be "
        "DERIVED from OHLCV without inventing the indicator, and which cannot be FETCHED "
        "(Signum / MCP / Hyperliquid hard-locked). NO labels produced, NO artifacts, "
        "NOTHING SHA-pinned. Declares the frozen operator-staged Trend-Radar dataset "
        "required before a separately-authorised labels run. Executes nothing.")


def get_c22_data_readiness_next_action() -> str:
    return NEXT_HUMAN_ACTION


def _deepish_tuple_of_dicts(t: tuple) -> list:
    return [dict(d) for d in t]


def build_c22_data_readiness() -> dict[str, Any]:
    """Assemble the frozen C22 real-candle data-readiness review record. Pure; no I/O.
    Chain-gated on the frozen detector dry-run. Concludes DATA_NOT_READY; produces no
    labels and no artifacts."""
    dr = _dr.build_c22_detector_dry_run()
    dr_valid = _dr.validate_c22_detector_dry_run(dr)["valid"]
    dr_verdict = dr.get("verdict")

    blockers: list = []
    if not dr_valid:
        blockers.append("c22_detector_dry_run_invalid")
    if dr_verdict != EXPECTED_DETECTOR_VERDICT:
        blockers.append("c22_detector_dry_run_not_frozen")

    # the deterministic data survey: no surveyed dataset supplies the gc fields.
    any_suitable = any(d["supplies_trend_radar_gc_fields"]
                       for d in SURVEYED_LOCAL_DATASETS)

    record: dict[str, Any] = {
        "schema_version": DRD22_SCHEMA_VERSION, "mode": DRD22_MODE, "lane": DRD22_LANE,
        "label": get_c22_data_readiness_label(),
        "candidate_id": CANDIDATE_ID, "candidate_token": CANDIDATE_TOKEN,
        "candidate_family": CANDIDATE_FAMILY, "candidate_name": CANDIDATE_NAME,
        "is_data_readiness_review_only": True,
        "blockers": blockers,
        # the honest verdict
        "readiness_verdict": (VERDICT_DATA_NOT_READY if not blockers
                              else "C22_DATA_READINESS_BLOCKED"),
        "data_ready": False,
        "labels_produced": False,
        "artifacts_produced": [],
        "any_sha_pinned_artifacts": False,
        # chain provenance (gated on the frozen detector dry-run)
        "detector_dry_run_valid": dr_valid,
        "detector_dry_run_verdict": dr_verdict,
        "chain_gated_on_c22_detector_dry_run": not blockers,
        "detector_dry_run_commit": DETECTOR_DRY_RUN_COMMIT,
        # frozen spec rules preserved (this review changes no rule)
        "preserves_frozen_c22_spec_rules": True,
        "edits_no_rules": True,
        "invents_no_indicator": True,
        # the required data + the survey + why not ready
        "required_data_fields": {
            "per_trend_radar_row": list(REQUIRED_DATA_FIELDS["per_trend_radar_row"]),
            "per_closed_daily_candle":
                list(REQUIRED_DATA_FIELDS["per_closed_daily_candle"]),
            "run_context": list(REQUIRED_DATA_FIELDS["run_context"]),
            "minimum_line_items": REQUIRED_DATA_FIELDS["minimum_line_items"],
            "all_assets_non_stablecoin":
                REQUIRED_DATA_FIELDS["all_assets_non_stablecoin"]},
        "surveyed_local_datasets": _deepish_tuple_of_dicts(SURVEYED_LOCAL_DATASETS),
        "any_local_dataset_supplies_trend_radar_gc_fields": any_suitable,
        "data_not_ready_reasons": list(DATA_NOT_READY_REASONS),
        "required_operator_staged_dataset": {
            **{k: (list(v) if isinstance(v, tuple) else v)
               for k, v in REQUIRED_OPERATOR_STAGED_DATASET.items()}},
        # posture: nothing fetched / connected / produced
        "uses_frozen_local_data_only": True,
        "no_data_fetch": True,
        "no_signum_connection": True,
        "no_mcp": True,
        "no_hyperliquid": True,
        "gc_bands_cannot_be_derived_from_ohlcv_without_inventing": True,
        "human_review_required": True,
        "current_loop_stage": "real_candle_labels_data_readiness",
        "next_required_action": NEXT_HUMAN_ACTION,
        "advances_nothing": True,
        "does_not_produce_labels_review_contract": True,
        # downstream gates locked
        "labels_gate_locked_until_data_ready": True,
        "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build_labels": True, "no_write": True, "no_execute": True,
        "no_real_candle_detection": True, "no_replay": True, "no_pnl": True,
        "no_optimization": True, "no_tuning": True, "no_edit_rules": True,
        "no_invent_indicator": True, "no_derive_provider_indicator": True,
        "no_data_fetch": True, "no_real_data_access": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_scheduler_change": True,
        "no_scheduler_install": True, "no_signum_connection": True, "no_mcp": True,
        "no_hyperliquid": True, "no_api_keys": True, "no_credentials": True,
        "no_send_email": True, "no_bot_edits": True, "no_set_trading_pair": True,
        "no_convert_funds": True, "no_claude_routines": True, "no_send_trades": True,
        "no_broker": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True, "no_claim_data_ready": True,
        "no_downstream_gate_unlock": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c22_data_readiness(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the review is research-only,
    readiness-review-only, chain-gated on the frozen detector dry-run (verdict + pinned
    commit), HONESTLY concludes DATA_NOT_READY (data_ready False, no labels, no artifacts,
    nothing SHA-pinned) because no surveyed local dataset supplies the Trend-Radar gc
    fields and they can be neither derived nor fetched, preserves the frozen spec rules
    (invents no indicator), declares the required operator-staged dataset, advances
    nothing, keeps downstream gates locked, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != DRD22_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_data_readiness_review_only") is not True:
        failures.append("not_readiness_review_only")
    if record.get("blockers"):
        failures.append("has_blockers")

    # the honest DATA_NOT_READY verdict -- cannot be flipped to ready
    if record.get("readiness_verdict") != VERDICT_DATA_NOT_READY:
        failures.append("verdict_not_data_not_ready")
    if record.get("data_ready") is not False:
        failures.append("must_not_claim_data_ready")
    if record.get("labels_produced") is not False:
        failures.append("must_not_produce_labels")
    if record.get("artifacts_produced") != []:
        failures.append("must_produce_no_artifacts")
    if record.get("any_sha_pinned_artifacts") is not False:
        failures.append("must_have_no_sha_pinned_artifacts")
    if record.get("does_not_produce_labels_review_contract") is not True:
        failures.append("must_not_produce_labels_review_contract")

    # chain gate on the frozen detector dry-run
    if record.get("detector_dry_run_valid") is not True:
        failures.append("detector_dry_run_not_valid")
    if record.get("detector_dry_run_verdict") != EXPECTED_DETECTOR_VERDICT:
        failures.append("detector_dry_run_not_frozen")
    if record.get("chain_gated_on_c22_detector_dry_run") is not True:
        failures.append("not_chain_gated")
    if record.get("detector_dry_run_commit") != DETECTOR_DRY_RUN_COMMIT:
        failures.append("detector_commit_not_pinned")

    # rules preserved; no indicator invented
    if record.get("preserves_frozen_c22_spec_rules") is not True:
        failures.append("rules_not_preserved")
    if record.get("edits_no_rules") is not True:
        failures.append("must_not_edit_rules")
    if record.get("invents_no_indicator") is not True:
        failures.append("must_not_invent_indicator")
    if record.get("gc_bands_cannot_be_derived_from_ohlcv_without_inventing") is not True:
        failures.append("derive_claim_missing")

    # the survey honestly shows no suitable dataset
    if record.get("any_local_dataset_supplies_trend_radar_gc_fields") is not False:
        failures.append("survey_falsely_claims_suitable_dataset")
    surveyed = record.get("surveyed_local_datasets") or []
    if not surveyed:
        failures.append("survey_empty")
    for d in surveyed:
        if d.get("supplies_trend_radar_gc_fields") is not False:
            failures.append("surveyed_dataset_falsely_suitable_%s" % d.get("path"))
    if len(record.get("data_not_ready_reasons") or []) < 4:
        failures.append("insufficient_not_ready_reasons")

    # required data fields + operator-staged dataset declared
    rdf = record.get("required_data_fields") or {}
    pcd = rdf.get("per_closed_daily_candle") or []
    if not any("gc.upper" in x for x in pcd) or not any("gc.filter" in x for x in pcd):
        failures.append("required_gc_band_fields_missing")
    if rdf.get("minimum_line_items") != 50:
        failures.append("min_line_items_not_50")
    req = record.get("required_operator_staged_dataset") or {}
    if "provenance_required" not in req or not req.get("provenance_required"):
        failures.append("operator_provenance_not_declared")
    if req.get("sparta_fetches_nothing") is not True:
        failures.append("must_state_sparta_fetches_nothing")

    # posture: no fetch / connection
    for k in ("uses_frozen_local_data_only", "no_data_fetch", "no_signum_connection",
              "no_mcp", "no_hyperliquid"):
        if record.get(k) is not True:
            failures.append("posture_off_%s" % k)

    # advances nothing; downstream locked
    if record.get("next_required_action") != NEXT_HUMAN_ACTION:
        failures.append("next_action_wrong")
    if record.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")
    for gate in ("labels_gate_locked_until_data_ready", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build_labels", "no_real_candle_detection", "no_replay",
                "no_data_fetch", "no_edit_rules", "no_invent_indicator",
                "no_derive_provider_indicator", "no_signum_connection", "no_mcp",
                "no_hyperliquid", "no_api_keys", "no_credentials", "no_send_email",
                "no_bot_edits", "no_send_trades", "no_paper_trading", "no_live_trading",
                "no_commit", "no_push", "no_claim_data_ready"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
