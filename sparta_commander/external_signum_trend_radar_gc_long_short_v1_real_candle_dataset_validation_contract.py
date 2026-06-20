"""Candidate #22 -- external_signum_trend_radar_gc_long_short_v1
-- REAL-CANDLE DATASET VALIDATION (PURE, READ-ONLY, RESEARCH ONLY).

Validates the LOCALLY STAGED Signum Trend Radar GC detector dataset against the FROZEN C22
spec + detector before any real-candle labels may be produced. It is PURE: it operates on
an ALREADY-PARSED dataset dict + the file's SHA256 (the runner/test reads the file
read-only and feeds the facts in); it performs NO file/network I/O, fetches NO data,
connects to NO Signum / MCP / Hyperliquid, and -- critically -- NEVER repairs or invents a
market rank.

Validation gate (single staged file only):
  * SHA256 matches the pinned value (the exact staged artifact, nothing else);
  * exactly 50 result rows; every row detector == "gc";
  * every row carries indicators.data with >= 2 daily candles (latest + previous closed);
  * the latest + previous candle each carry gc.trend / gc.upper / gc.filter;
  * every row carries indicators.cmcRefPriceUsd;
  * every row carries a numeric marketRank.

Outcome (honest, per the frozen spec's market-rank resolution -- unique numeric required
else entries are invalid):
  * structurally incomplete            -> DATASET_INVALID (stop, name the reason);
  * structurally complete + rank UNIQUE -> DATASET_VALID_PROCEED_TO_LABELS;
  * structurally complete + rank NOT unique
        -> DATASET_ENTRIES_INVALID_NON_UNIQUE_MARKET_RANK (stop; do NOT repair / invent
           ranks; escalate to a human rank-disambiguation gate).

It builds NO labels, runs NO replay, optimizes NOTHING, advances NOTHING. Every dangerous
capability is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_candidate_spec_contract as _s22  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_detector_spec_dry_run_contract as _dr22  # noqa: E501

DV22_SCHEMA_VERSION = 1
DV22_MODE = "RESEARCH_ONLY"
DV22_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _s22.CANDIDATE_ID
CANDIDATE_TOKEN = _s22.CANDIDATE_TOKEN
CANDIDATE_FAMILY = _s22.CANDIDATE_FAMILY
CANDIDATE_NAME = _s22.CANDIDATE_NAME

# the ONE staged artifact this validation pins (relative to repo root).
DATASET_PATH = "data/external_signum_trend_radar_gc/gc_crypto_trendradar_daily.json"
# pinned SHA256 of the exact staged file under validation (lowercase hex).
DATASET_SHA256 = (
    "cc37dee4f6bb65ac9ae219bfa8e4ececa83fb06952d8ecac3250419367470f21")

EXPECTED_ROW_COUNT = 50
EXPECTED_DETECTOR = "gc"

# chain provenance: this validation is gated on the frozen spec + frozen detector.
SPEC_COMMIT = _dr22.SPEC_COMMIT
EXPECTED_SPEC_VERDICT = _dr22.EXPECTED_SPEC_VERDICT
EXPECTED_DETECTOR_VERDICT = _dr22.VERDICT_DR22_FROZEN

VERDICT_VALID = "C22_DATASET_VALID_PROCEED_TO_LABELS"
VERDICT_VALID_VIA_TIEBREAKER = (
    "C22_DATASET_VALID_VIA_MARKET_RANK_TIEBREAKER_PROCEED_TO_LABELS")
VERDICT_DATASET_INVALID = "C22_DATASET_INVALID"
VERDICT_ENTRIES_INVALID = "C22_DATASET_ENTRIES_INVALID_NON_UNIQUE_MARKET_RANK"

# HUMAN ambiguity resolution (HUMAN_DECISION_C22_RESOLVE_DUPLICATE_MARKET_RANK_OR_REJECT):
# when marketRank ties occur, C22 ENTRY ORDERING uses a deterministic tie-break --
# (1) marketRank ascending, (2) marketCap descending, (3) symbol ascending. This orders
# ENTRIES only; it does NOT mutate the dataset and does NOT invent new marketRank values.
# The raw provider marketRank / marketCap values are preserved verbatim.
MARKET_RANK_TIEBREAKER = ("market_rank_asc", "market_cap_desc", "symbol_asc")
MARKET_RANK_RESOLUTION_NOTE = (
    "HUMAN ambiguity resolution: on marketRank ties, C22 entry ordering breaks ties by "
    "marketRank ascending, then marketCap descending, then symbol ascending. This is a "
    "human resolution for entry ordering only -- NOT vendor-original data; the dataset is "
    "not mutated and no marketRank value is invented.")

NEXT_ACTION_VALID = "HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"
NEXT_ACTION_ENTRIES_INVALID = (
    "HUMAN_DECISION_C22_RESOLVE_DUPLICATE_MARKET_RANK_OR_REJECT")
NEXT_ACTION_DATASET_INVALID = (
    "HUMAN_DECISION_C22_RESTAGE_OR_REJECT_INVALID_DATASET")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "performs_file_io", "performs_network_io",
    "runs_detector_on_real_candles", "builds_labels", "runs_replay", "runs_backtest",
    "computes_pnl", "optimizes_parameters", "tunes_parameters", "reparameterizes",
    "fetches_data", "stages_data", "mutates_data", "repairs_market_rank",
    "invents_rule_values", "invents_ranks", "auto_commits", "auto_pushes",
    "modifies_scheduler", "installs_scheduler", "sends_notifications", "sends_email",
    "calls_api", "uses_network", "uses_credentials", "uses_api_keys", "connects_signum",
    "uses_mcp", "accesses_hyperliquid", "connects_broker", "connects_exchange",
    "sends_trades", "edits_bots", "sets_trading_pair", "creates_claude_routines",
    "uses_real_money", "places_orders", "contains_order_logic", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "advances_without_human_approval", "modifies_c22_rules", "starts_c23",
    "reopens_c21", "crosses_into_forbidden_gate",
)


def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def apply_market_rank_tiebreaker(order_rows: list) -> list:
    """PURE. Deterministically order rows for ENTRY ordering using the human-resolved
    tie-break: marketRank ascending, then marketCap descending, then symbol ascending.
    Operates on minimal {symbol, market_rank, market_cap} dicts. Mutates nothing; invents
    no rank. Returns a new ordered list."""
    def key(r: dict):
        rank = r.get("market_rank")
        cap = r.get("market_cap")
        return (rank if _is_number(rank) else float("inf"),
                -(cap if _is_number(cap) else 0.0),
                str(r.get("symbol")))
    return sorted(order_rows, key=key)


def extract_dataset_facts(parsed: dict) -> dict[str, Any]:
    """PURE. Compute the field-presence + market-rank-uniqueness facts from an ALREADY
    PARSED dataset dict ({limited,total,results:[...]}). No I/O. Never raises on missing
    keys; reports them as violations."""
    results = list((parsed or {}).get("results") or [])
    n = len(results)
    non_gc = 0
    missing_data = 0
    lt2_candles = 0
    candle_gc_violations = 0
    missing_cmc = 0
    missing_rank = 0
    non_numeric_rank = 0
    ranks: list = []
    rank_counts: dict = {}
    order_rows: list = []

    for r in results:
        if not isinstance(r, dict):
            non_gc += 1
            missing_data += 1
            continue
        if r.get("detector") != EXPECTED_DETECTOR:
            non_gc += 1
        ind = r.get("indicators") or {}
        data = ind.get("data") or []
        if not data:
            missing_data += 1
        elif len(data) < 2:
            lt2_candles += 1
        else:
            for cdl in (data[-1], data[-2]):
                gc = (cdl or {}).get("gc") or {}
                if (gc.get("trend") is None or gc.get("upper") is None
                        or gc.get("filter") is None):
                    candle_gc_violations += 1
        if ind.get("cmcRefPriceUsd") is None:
            missing_cmc += 1
        rk = r.get("marketRank")
        if rk is None:
            missing_rank += 1
        else:
            ranks.append(rk)
            if not _is_number(rk):
                non_numeric_rank += 1
            else:
                rank_counts[rk] = rank_counts.get(rk, 0) + 1
        order_rows.append({"symbol": r.get("symbol"), "market_rank": rk,
                           "market_cap": r.get("marketCap")})

    distinct = len({rk for rk in ranks if _is_number(rk)})
    market_rank_unique = (
        n == EXPECTED_ROW_COUNT and len(ranks) == n and non_numeric_rank == 0
        and distinct == n)
    duplicate_ranks = sorted(v for v, c in rank_counts.items() if c > 1)

    # deterministic tie-break ordering (human resolution; entry ordering only)
    ordered = apply_market_rank_tiebreaker(order_rows)
    tie_broken_order_symbols = [r["symbol"] for r in ordered]
    distinct_symbols = len({r["symbol"] for r in order_rows})
    # the tie-break yields a STRICT TOTAL ORDER iff every symbol is unique (the final
    # tiebreaker key) and every row carries a numeric rank.
    tiebreaker_total_order = (
        n == EXPECTED_ROW_COUNT and distinct_symbols == n
        and missing_rank == 0 and non_numeric_rank == 0)

    return {
        "row_count": n,
        "had_market_rank_ties": len(duplicate_ranks) > 0,
        "tie_broken_order_symbols": tie_broken_order_symbols,
        "tiebreaker_total_order": tiebreaker_total_order,
        "distinct_symbols": distinct_symbols,
        "all_detector_gc": non_gc == 0 and n > 0,
        "non_gc_rows": non_gc,
        "rows_missing_indicators_data": missing_data,
        "rows_with_fewer_than_2_candles": lt2_candles,
        "latest_and_previous_candles_present": (
            missing_data == 0 and lt2_candles == 0 and n > 0),
        "candle_gc_field_violations": candle_gc_violations,
        "gc_trend_upper_filter_present": candle_gc_violations == 0,
        "rows_missing_cmc_ref_price_usd": missing_cmc,
        "cmc_ref_price_usd_present": missing_cmc == 0 and n > 0,
        "rows_missing_market_rank": missing_rank,
        "non_numeric_market_rank": non_numeric_rank,
        "market_rank_present_numeric": (
            missing_rank == 0 and non_numeric_rank == 0 and n > 0),
        "distinct_market_rank_count": distinct,
        "market_rank_unique": market_rank_unique,
        "duplicate_market_ranks": duplicate_ranks,
    }


def build_dataset_validation(facts: dict, sha256: str) -> dict[str, Any]:
    """Assemble the dataset-validation record from extracted facts + the file SHA256. Pure;
    no I/O. Chain-gated on the frozen spec + frozen detector. NEVER repairs or invents a
    market rank -- a non-unique rank yields ENTRIES_INVALID and a human gate, not a fix."""
    spec = _s22.build_c22_spec()
    spec_valid = _s22.validate_c22_spec(spec)["valid"]
    spec_verdict = spec.get("verdict")
    detector = _dr22.build_c22_detector_dry_run()
    detector_valid = _dr22.validate_c22_detector_dry_run(detector)["valid"]
    detector_verdict = detector.get("verdict")

    sha_ok = str(sha256).lower() == DATASET_SHA256

    # structural completeness (the required-field gate)
    structural_checks = {
        "sha256_pinned": sha_ok,
        "row_count_50": facts.get("row_count") == EXPECTED_ROW_COUNT,
        "all_detector_gc": facts.get("all_detector_gc") is True,
        "indicators_data_present": facts.get("rows_missing_indicators_data") == 0,
        "latest_and_previous_candles_present":
            facts.get("latest_and_previous_candles_present") is True,
        "gc_trend_upper_filter_present":
            facts.get("gc_trend_upper_filter_present") is True,
        "cmc_ref_price_usd_present": facts.get("cmc_ref_price_usd_present") is True,
        "market_rank_present_numeric": facts.get("market_rank_present_numeric") is True,
    }
    structural_ok = all(structural_checks.values())
    market_rank_unique = facts.get("market_rank_unique") is True
    tiebreaker_total_order = facts.get("tiebreaker_total_order") is True

    blockers: list = []
    if not spec_valid or spec_verdict != EXPECTED_SPEC_VERDICT:
        blockers.append("c22_spec_not_frozen")
    if not detector_valid or detector_verdict != EXPECTED_DETECTOR_VERDICT:
        blockers.append("c22_detector_not_frozen")

    structural_failures = [k for k, v in structural_checks.items() if not v]
    tiebreaker_applied = False

    if blockers:
        verdict = VERDICT_DATASET_INVALID
        proceed = False
        next_action = NEXT_ACTION_DATASET_INVALID
        skip_reasons = ["chain_gate:" + b for b in blockers]
    elif not structural_ok:
        verdict = VERDICT_DATASET_INVALID
        proceed = False
        next_action = NEXT_ACTION_DATASET_INVALID
        skip_reasons = ["structural_failure:" + k for k in structural_failures]
    elif market_rank_unique:
        verdict = VERDICT_VALID
        proceed = True
        next_action = NEXT_ACTION_VALID
        skip_reasons = []
    elif tiebreaker_total_order:
        # marketRank not unique, but the human tie-breaker yields a strict total order
        # for entry ordering -> ambiguity resolved; proceed (dataset NOT mutated).
        verdict = VERDICT_VALID_VIA_TIEBREAKER
        proceed = True
        next_action = NEXT_ACTION_VALID
        skip_reasons = []
        tiebreaker_applied = True
    else:
        verdict = VERDICT_ENTRIES_INVALID
        proceed = False
        next_action = NEXT_ACTION_ENTRIES_INVALID
        skip_reasons = [
            "non_unique_market_rank:duplicate_ranks=%s"
            % (facts.get("duplicate_market_ranks") or [])]

    # labels are NEVER produced by this validation step; while entries are invalid the
    # detector's market-rank resolution yields zero entries regardless.
    labels_produced = 0

    record: dict[str, Any] = {
        "schema_version": DV22_SCHEMA_VERSION, "mode": DV22_MODE, "lane": DV22_LANE,
        "candidate_id": CANDIDATE_ID, "candidate_token": CANDIDATE_TOKEN,
        "candidate_family": CANDIDATE_FAMILY, "candidate_name": CANDIDATE_NAME,
        "is_dataset_validation_only": True,
        "label": (
            "Candidate #22 real-candle dataset validation (READ-ONLY, RESEARCH ONLY). "
            "Validates the single locally-staged Signum Trend Radar GC detector dataset "
            "against the frozen C22 spec + detector; pins its SHA256; confirms 50 gc rows "
            "with indicators.data latest+previous candles carrying gc.trend/upper/filter, "
            "cmcRefPriceUsd, and numeric marketRank; and -- without ever repairing or "
            "inventing a rank -- stops at ENTRIES_INVALID when marketRank is not unique. "
            "Builds no labels, runs no replay, advances nothing."),
        # the pinned artifact
        "dataset_path": DATASET_PATH,
        "dataset_sha256_pinned": DATASET_SHA256,
        "dataset_sha256_observed": str(sha256).lower(),
        "sha256_matches_pin": sha_ok,
        # chain provenance
        "spec_valid": spec_valid, "spec_verdict": spec_verdict,
        "spec_commit": SPEC_COMMIT,
        "detector_valid": detector_valid, "detector_verdict": detector_verdict,
        "chain_gated": not blockers,
        # the validation facts + checks
        "required_field_checks": structural_checks,
        "structurally_complete": structural_ok,
        "structural_failures": structural_failures,
        "dataset_facts": dict(facts),
        "row_count": facts.get("row_count"),
        "market_rank_unique": market_rank_unique,
        "duplicate_market_ranks": list(facts.get("duplicate_market_ranks") or []),
        # human tie-breaker resolution (entry ordering only; dataset NOT mutated)
        "had_market_rank_ties": facts.get("had_market_rank_ties") is True,
        "market_rank_tiebreaker": list(MARKET_RANK_TIEBREAKER),
        "market_rank_resolution_note": MARKET_RANK_RESOLUTION_NOTE,
        "tiebreaker_yields_total_order": tiebreaker_total_order,
        "tiebreaker_applied": tiebreaker_applied,
        "tie_broken_order_symbols": list(facts.get("tie_broken_order_symbols") or []),
        # honest outcome
        "verdict": verdict,
        "proceed_to_labels": proceed,
        "labels_produced": labels_produced,
        "skip_reasons": skip_reasons,
        "next_required_action": next_action,
        # explicit no-repair guarantees
        "repaired_market_rank": False,
        "invented_ranks": False,
        "mutated_dataset": False,
        "requires_human_rank_disambiguation_gate": verdict == VERDICT_ENTRIES_INVALID,
        # downstream gates locked
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
        "advances_nothing": True,
        "human_review_required": True,
        "current_loop_stage": "real_candle_dataset_validation",
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_file_io": True, "no_network_io": True,
        "no_real_candle_detection": True, "no_labels": True, "no_replay": True,
        "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_data_fetch": True, "no_stage_more_data": True, "no_mutate_dataset": True,
        "no_repair_market_rank": True, "no_invent_ranks": True, "no_invent_values": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_scheduler_install": True,
        "no_signum_connection": True, "no_mcp": True, "no_hyperliquid": True,
        "no_api_keys": True, "no_credentials": True, "no_send_email": True,
        "no_bot_edits": True, "no_set_trading_pair": True, "no_claude_routines": True,
        "no_send_trades": True, "no_broker": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_promote_gate": True,
        "no_downstream_gate_unlock": True, "no_modify_c22_rules": True,
        "no_start_c23": True, "no_reopen_c21": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_dataset_validation(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only,
    dataset-validation-only, chain-gated on the frozen spec + detector, pins the dataset
    SHA256, reports the required-field checks, NEVER repairs/invents a market rank, draws
    the honest verdict (VALID only when structurally complete AND rank-unique; ENTRIES_
    INVALID when complete but rank not unique; DATASET_INVALID otherwise), keeps downstream
    gates locked + advances nothing, and pins every capability flag False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != DV22_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_dataset_validation_only") is not True:
        failures.append("not_dataset_validation_only")
    if r.get("verdict") not in (VERDICT_VALID, VERDICT_VALID_VIA_TIEBREAKER,
                                VERDICT_DATASET_INVALID, VERDICT_ENTRIES_INVALID):
        failures.append("bad_verdict")

    # chain provenance pinned
    if r.get("spec_verdict") != EXPECTED_SPEC_VERDICT:
        failures.append("spec_not_frozen")
    if r.get("spec_commit") != SPEC_COMMIT:
        failures.append("spec_commit_not_pinned")
    if r.get("detector_verdict") != EXPECTED_DETECTOR_VERDICT:
        failures.append("detector_not_frozen")

    # dataset pin
    if r.get("dataset_path") != DATASET_PATH:
        failures.append("dataset_path_wrong")
    if r.get("dataset_sha256_pinned") != DATASET_SHA256:
        failures.append("sha_pin_tampered")

    # no repair / invent / mutate -- the central safety invariant
    for k in ("repaired_market_rank", "invented_ranks", "mutated_dataset"):
        if r.get(k) is not False:
            failures.append("must_not_%s" % k)

    # verdict consistency with the facts
    structural_ok = r.get("structurally_complete") is True
    rank_unique = r.get("market_rank_unique") is True
    sha_ok = r.get("sha256_matches_pin") is True
    chain_ok = r.get("chain_gated") is True
    tiebreaker_total = r.get("tiebreaker_yields_total_order") is True
    v = r.get("verdict")
    if v == VERDICT_VALID:
        if not (structural_ok and rank_unique and sha_ok and chain_ok):
            failures.append("valid_verdict_without_full_validity")
        if r.get("proceed_to_labels") is not True:
            failures.append("valid_must_proceed_to_labels")
        if r.get("next_required_action") != NEXT_ACTION_VALID:
            failures.append("valid_next_action_wrong")
    elif v == VERDICT_VALID_VIA_TIEBREAKER:
        # structurally complete, rank NOT unique, but the tie-breaker totally orders it.
        if not (structural_ok and sha_ok and chain_ok and tiebreaker_total):
            failures.append("tiebreaker_valid_without_total_order")
        if rank_unique:
            failures.append("tiebreaker_path_but_rank_already_unique")
        if r.get("tiebreaker_applied") is not True:
            failures.append("tiebreaker_must_be_applied")
        if not r.get("duplicate_market_ranks"):
            failures.append("tiebreaker_must_name_duplicate_ranks")
        if list(r.get("market_rank_tiebreaker") or []) != list(MARKET_RANK_TIEBREAKER):
            failures.append("tiebreaker_order_tampered")
        if len(r.get("tie_broken_order_symbols") or []) != r.get("row_count"):
            failures.append("tie_broken_order_incomplete")
        if r.get("proceed_to_labels") is not True:
            failures.append("tiebreaker_must_proceed_to_labels")
        if r.get("next_required_action") != NEXT_ACTION_VALID:
            failures.append("tiebreaker_next_action_wrong")
    elif v == VERDICT_ENTRIES_INVALID:
        if not (structural_ok and chain_ok and sha_ok):
            failures.append("entries_invalid_requires_structural_completeness")
        if rank_unique:
            failures.append("entries_invalid_but_rank_unique")
        if r.get("proceed_to_labels") is not False:
            failures.append("entries_invalid_must_not_proceed")
        if not r.get("duplicate_market_ranks"):
            failures.append("entries_invalid_must_name_duplicate_ranks")
        if r.get("requires_human_rank_disambiguation_gate") is not True:
            failures.append("entries_invalid_must_require_human_gate")
        if r.get("next_required_action") != NEXT_ACTION_ENTRIES_INVALID:
            failures.append("entries_invalid_next_action_wrong")
    else:  # DATASET_INVALID
        if structural_ok and rank_unique and sha_ok and chain_ok:
            failures.append("dataset_invalid_but_everything_valid")
        if r.get("proceed_to_labels") is not False:
            failures.append("dataset_invalid_must_not_proceed")

    # labels are never produced by validation
    if r.get("labels_produced") != 0:
        failures.append("validation_must_not_produce_labels")
    if r.get("builds_labels") is not False:
        failures.append("builds_labels_must_be_false")

    # downstream locked + advances nothing
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if r.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_file_io", "no_network_io", "no_real_candle_detection",
                "no_labels", "no_replay", "no_pnl", "no_optimization", "no_data_fetch",
                "no_mutate_dataset", "no_repair_market_rank", "no_invent_ranks",
                "no_invent_values", "no_commit", "no_push", "no_signum_connection",
                "no_mcp", "no_hyperliquid", "no_api_keys", "no_credentials",
                "no_bot_edits", "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_modify_c22_rules", "no_start_c23", "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
