"""Candidate #22 -- external_signum_trend_radar_gc_long_short_v1
-- MULTI-WINDOW REAL-CANDLE ENTRY-SIGNAL LABELS (PURE, READ-ONLY, RESEARCH ONLY, SPEC + IMPL).

Human-approved remediation (token
HUMAN_APPROVED_C22_MULTI_WINDOW_LABEL_BUILD_REMEDIATION_SPEC_AND_IMPLEMENTATION_ONLY):
the minimum ADDITIVE tooling to apply the already-approved, UNCHANGED C22 labeling logic
INDEPENDENTLY across the 20 reviewed frozen windows 2026-06-20 .. 2026-07-09.

Why this exists: the original single-window labels contract
(external_signum_trend_radar_gc_long_short_v1_real_candle_labels_contract) is SHA-pinned to
the single 06-20 bootstrap dataset (its dataset-validation gate requires
sha256 == the pinned DATASET_SHA256), so it CANNOT be reused verbatim across the other 19
windows. This contract therefore reuses the FROZEN CLASSIFICATION CORE verbatim -- the same
imported functions and constants, no reinterpretation:
  * _lb._classify_signal        (the frozen LONG/HEDGE/BEAR/NONE + skip predicates)
  * _lb.extract_label_rows      (latest+previous CLOSED-candle extraction)
  * _lb.BEAR_HIGH_MULT          (0.98, single-sourced from the frozen detector spec)
  * _lb.BTC_SYMBOL / BTC-context logic (btc downtrend from BTC's own latest closed candle)
  * _dv.apply_market_rank_tiebreaker (human tie-break ordering; invents no rank)
  * _dv.extract_dataset_facts   (structural + rank-uniqueness facts)
It applies them PER WINDOW exactly as build_labels does in its gate-open branch, binding each
window's OWN source path/date/SHA256, and computes a deterministic aggregate manifest SHA.

This contract AUTHORIZES NOTHING TO RUN. It builds NO real artifact, performs NO file/network
I/O, runs NO replay, optimizes NOTHING, and advances NOTHING. The actual 20-window build is a
SEPARATE human gate (see NEXT_GATE_TOKEN). build_authorized/replay_authorized/
optimization_authorized/activation_authorized/paper_live_authorized/execution_authorized are
all False. The single-window contract, its runner, and the historical 06-20 artifact are
PRESERVED and untouched.
"""
from __future__ import annotations

import datetime as _dt
import hashlib as _hashlib
import json as _json
from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_contract as _lb  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_dataset_validation_contract as _dv  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_detector_spec_dry_run_contract as _dr22  # noqa: E501

MWL22_SCHEMA_VERSION = 1
MWL22_MODE = "RESEARCH_ONLY"
MWL22_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _lb.CANDIDATE_ID

# ---- the reviewed frozen window range (inclusive, contiguous, 20 windows) ------------------
WINDOW_START = "2026-06-20"
WINDOW_END = "2026-07-09"
EXPECTED_WINDOWS = 20
LABELS_PER_WINDOW = _dv.EXPECTED_ROW_COUNT          # 50
TOTAL_LABELS = EXPECTED_WINDOWS * LABELS_PER_WINDOW  # 1000


def _daterange(start: str, end: str) -> tuple:
    a = _dt.date.fromisoformat(start)
    b = _dt.date.fromisoformat(end)
    out = []
    d = a
    while d <= b:
        out.append(d.isoformat())
        d += _dt.timedelta(days=1)
    return tuple(out)


EXPECTED_DATES = _daterange(WINDOW_START, WINDOW_END)   # 20 ISO dates

# ---- frozen semantics reused verbatim from the single-window source of truth ---------------
BEAR_HIGH_MULT = _lb.BEAR_HIGH_MULT                 # 0.98 (single-sourced from detector spec)
BTC_SYMBOL = _lb.BTC_SYMBOL
SIGNAL_LONG = _lb.SIGNAL_LONG
SIGNAL_HEDGE = _lb.SIGNAL_HEDGE
SIGNAL_BEAR = _lb.SIGNAL_BEAR
SIGNAL_NONE = _lb.SIGNAL_NONE
SIGNAL_SKIP = _lb.SIGNAL_SKIP
MARKET_RANK_TIEBREAKER = tuple(_dv.MARKET_RANK_TIEBREAKER)
# expose the exact frozen functions (identity-reused; NOT reimplemented)
classify_signal = _lb._classify_signal
extract_label_rows = _lb.extract_label_rows
apply_market_rank_tiebreaker = _dv.apply_market_rank_tiebreaker
extract_dataset_facts = _dv.extract_dataset_facts

# ---- canonical multi-window artifact naming (tied to the DATE RANGE, never "today") --------
ARTIFACT_DIR = _lb.ARTIFACT_DIR   # data/external_signum_trend_radar_gc/detector_labels
MW_ARTIFACT_BASENAME = "c22_gc_real_candle_entry_labels_multiwindow"
MW_ARTIFACT_FILENAME = "%s_%s_%s.json" % (MW_ARTIFACT_BASENAME, WINDOW_START, WINDOW_END)
# the PRESERVED historical single-window artifact (do not overwrite / confuse with this).
SINGLE_WINDOW_ARTIFACT_FILENAME = "c22_gc_real_candle_entry_labels_2026-06-20.json"

VERDICT_MANIFEST_READY = "C22_MULTI_WINDOW_LABEL_MANIFEST_READY_BUILD_GATED"
VERDICT_MANIFEST_BLOCKED = "C22_MULTI_WINDOW_LABEL_MANIFEST_BLOCKED"

# ---- lifecycle: REUSE the existing canonical C22 token; do NOT invent a parallel one -------
# The remediation changed only the IMPLEMENTATION (single-window -> multi-window), not the
# lifecycle stage. The canonical gate that authorizes building the C22 real-candle labels is
# already registered; the multi-window build is that same build, so it is governed by the
# same token. After the build, review is governed by the existing review token.
NEXT_GATE_TOKEN = _dv.NEXT_ACTION_VALID             # HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT
NEXT_ACTION_AFTER_LABELS = _lb.NEXT_ACTION_AFTER_LABELS  # HUMAN_DECISION_C22_REVIEW_REAL_CANDLE_LABELS_OR_REJECT

# ---- explicit named authorization flags (all False; execution is a separate human gate) ----
BUILD_AUTHORIZED = False
REPLAY_AUTHORIZED = False
OPTIMIZATION_AUTHORIZED = False
ACTIVATION_AUTHORIZED = False
PAPER_LIVE_AUTHORIZED = False
EXECUTION_AUTHORIZED = False

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "performs_file_io", "performs_network_io",
    "runs_replay", "runs_backtest", "computes_pnl", "optimizes_parameters",
    "tunes_parameters", "reparameterizes", "changes_thresholds", "changes_classification",
    "fetches_data", "pickups_data", "reduces_data", "stages_data", "mutates_data",
    "alters_source", "repairs_market_rank", "invents_ranks", "restores_ranks_51_100",
    "reconstructs_top100", "auto_commits", "auto_pushes", "modifies_scheduler",
    "installs_scheduler", "calls_api", "uses_network", "uses_credentials", "uses_api_keys",
    "connects_signum", "uses_mcp", "accesses_hyperliquid", "connects_broker",
    "connects_exchange", "sends_trades", "edits_bots", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "activates_candidate", "promotes_gate", "unlocks_downstream_gate",
    "advances_without_human_approval", "modifies_c22_rules", "modifies_single_window_contract",
    "overwrites_single_window_artifact", "starts_c23", "reopens_c21",
    "crosses_into_forbidden_gate",
)


def label_window(parsed: dict, sha256: str, run_date: str) -> dict[str, Any]:
    """PURE. Apply the FROZEN single-window classification core to ONE window, binding this
    window's own source date + SHA256. This is byte-for-byte the same computation build_labels
    performs in its gate-open branch (same imported functions/constants), with no shared
    mutable state across windows. Returns {labels(50 when structurally valid), counts,
    btc_present, btc_downtrend}."""
    facts = extract_dataset_facts(parsed)
    rows = extract_label_rows(parsed)
    duplicate_ranks = set(facts.get("duplicate_market_ranks") or [])
    order_rows = [{"symbol": s, "market_rank": v.get("market_rank"),
                   "market_cap": v.get("market_cap")} for s, v in rows.items()]
    ordered = apply_market_rank_tiebreaker(order_rows)
    btc = rows.get(BTC_SYMBOL)
    btc_latest = btc.get("latest") if btc else None
    btc_present = bool(btc_latest and btc_latest.get("c") is not None
                       and btc_latest.get("filter") is not None)
    btc_downtrend = bool(btc_present and btc_latest["c"] < btc_latest["filter"])
    counts = {SIGNAL_LONG: 0, SIGNAL_HEDGE: 0, SIGNAL_BEAR: 0, SIGNAL_NONE: 0, SIGNAL_SKIP: 0}
    labels: list = []
    for i, oref in enumerate(ordered):
        row = rows.get(oref["symbol"]) or {}
        signal, reasons, skip = classify_signal(row, btc_downtrend)
        rank = row.get("market_rank")
        labels.append({
            "source_date": run_date, "source_sha256": sha256,
            "order_index": i, "symbol": oref["symbol"],
            "market_rank_raw": rank, "market_cap": row.get("market_cap"),
            "tie_broken": rank in duplicate_ranks,
            "latest_date": row.get("latest_date"),
            "btc_present": btc_present, "btc_downtrend": btc_downtrend,
            "signal": signal, "reasons": list(reasons), "skip_reason": skip})
        counts[SIGNAL_SKIP if skip else signal] += 1
    return {"labels": labels, "label_counts": counts,
            "btc_present": btc_present, "btc_downtrend": btc_downtrend}


def _structural_window_ok(facts: dict) -> dict[str, Any]:
    """Reuses the SAME structural field-checks the single-window dataset validation applies
    (minus the single-file sha256 pin, since each window binds its own SHA), plus the
    strict-total-order tie-break requirement. Returns {ok, checks}."""
    checks = {
        "row_count_50": facts.get("row_count") == LABELS_PER_WINDOW,
        "all_detector_gc": facts.get("all_detector_gc") is True,
        "indicators_data_present": facts.get("rows_missing_indicators_data") == 0,
        "latest_and_previous_candles_present":
            facts.get("latest_and_previous_candles_present") is True,
        "gc_trend_upper_filter_present": facts.get("gc_trend_upper_filter_present") is True,
        "cmc_ref_price_usd_present": facts.get("cmc_ref_price_usd_present") is True,
        "market_rank_present_numeric": facts.get("market_rank_present_numeric") is True,
        "tiebreaker_total_order": facts.get("tiebreaker_total_order") is True,
    }
    return {"ok": all(checks.values()), "checks": checks}


def _manifest_sha(window_records: list) -> str:
    """Deterministic aggregate manifest SHA over the ORDERED per-window (date|sha|rows)."""
    canon = "\n".join("%s|%s|%d" % (w["run_date"], w["sha256"], w["row_count"])
                      for w in window_records).encode("utf-8")
    return _hashlib.sha256(canon).hexdigest()


def build_multi_window_manifest(window_inputs: Any) -> dict[str, Any]:
    """PURE. Validate the 20 supplied windows and assemble the multi-window label manifest +
    aggregate labels. `window_inputs` = list of dicts {source_path, run_date, row_count,
    sha256, parsed}. FAILS CLOSED (verdict BLOCKED + blockers) on any missing/duplicate date,
    gap, invalid window, wrong row count, or count mismatch. Builds NO file; authorizes
    nothing."""
    blockers: list = []
    wins = list(window_inputs or [])
    # order by run_date deterministically
    wins_sorted = sorted(wins, key=lambda w: str(w.get("run_date")))
    dates = [str(w.get("run_date")) for w in wins_sorted]

    if len(wins_sorted) != EXPECTED_WINDOWS:
        blockers.append("expected_%d_windows_got_%d" % (EXPECTED_WINDOWS, len(wins_sorted)))
    if len(set(dates)) != len(dates):
        blockers.append("duplicate_window_dates")
    if tuple(dates) != EXPECTED_DATES:
        blockers.append("dates_not_exactly_expected_contiguous_range")

    per_window: list = []
    agg_labels: list = []
    agg_counts = {SIGNAL_LONG: 0, SIGNAL_HEDGE: 0, SIGNAL_BEAR: 0,
                  SIGNAL_NONE: 0, SIGNAL_SKIP: 0}
    for w in wins_sorted:
        parsed = w.get("parsed") or {}
        sha = str(w.get("sha256"))
        rd = str(w.get("run_date"))
        facts = extract_dataset_facts(parsed)
        struct = _structural_window_ok(facts)
        # rows in the parsed content must all carry this window's runDate (no mixed-date)
        row_dates = {r.get("runDate") for r in parsed.get("results", []) if isinstance(r, dict)}
        single_date = (len(row_dates) == 1 and next(iter(row_dates)) == rd)
        window_ok = struct["ok"] and single_date and facts.get("row_count") == LABELS_PER_WINDOW
        if not window_ok:
            blockers.append("invalid_window:%s" % rd)
        built = label_window(parsed, sha, rd) if window_ok else {
            "labels": [], "label_counts": dict(agg_counts),
            "btc_present": False, "btc_downtrend": False}
        if window_ok and len(built["labels"]) != LABELS_PER_WINDOW:
            blockers.append("window_%s_did_not_produce_%d_labels" % (rd, LABELS_PER_WINDOW))
        for k, v in built["label_counts"].items():
            agg_counts[k] = agg_counts.get(k, 0) + v
        agg_labels.extend(built["labels"])
        per_window.append({
            "run_date": rd, "source_path": w.get("source_path"),
            "sha256": sha, "row_count": facts.get("row_count"),
            "structurally_valid": window_ok, "structural_checks": struct["checks"],
            "btc_present": built["btc_present"], "btc_downtrend": built["btc_downtrend"],
            "label_counts": built["label_counts"]})

    if not blockers and len(agg_labels) != TOTAL_LABELS:
        blockers.append("aggregate_label_count_%d_ne_%d" % (len(agg_labels), TOTAL_LABELS))

    manifest_sha = _manifest_sha(
        [{"run_date": p["run_date"], "sha256": p["sha256"],
          "row_count": p["row_count"] or 0} for p in per_window])

    record: dict[str, Any] = {
        "schema_version": MWL22_SCHEMA_VERSION, "mode": MWL22_MODE, "lane": MWL22_LANE,
        "candidate_id": CANDIDATE_ID,
        "window_start": WINDOW_START, "window_end": WINDOW_END,
        "expected_windows": EXPECTED_WINDOWS, "labels_per_window": LABELS_PER_WINDOW,
        "total_labels_expected": TOTAL_LABELS,
        "expected_dates": list(EXPECTED_DATES),
        "is_multi_window_spec_and_impl_only": True,
        "reuses_single_window_core": True,
        "single_window_source_contract":
            "external_signum_trend_radar_gc_long_short_v1_real_candle_labels_contract",
        "single_window_artifact_preserved": SINGLE_WINDOW_ARTIFACT_FILENAME,
        "bear_high_multiple_single_sourced": BEAR_HIGH_MULT,
        "market_rank_tiebreaker": list(MARKET_RANK_TIEBREAKER),
        "per_window": per_window,
        "aggregate_manifest_sha256": manifest_sha,
        "aggregate_label_counts": agg_counts,
        "aggregate_labels_built": len(agg_labels),
        "verdict": (VERDICT_MANIFEST_READY if not blockers else VERDICT_MANIFEST_BLOCKED),
        "blockers": blockers,
        # canonical artifact naming + collision prevention
        "artifact_dir": ARTIFACT_DIR,
        "mw_artifact_filename": MW_ARTIFACT_FILENAME,
        "never_date_tagged_today": True,
        "never_overwrites_single_window_artifact": True,
        # explicit authorization flags (execution is a SEPARATE human gate)
        "build_authorized": BUILD_AUTHORIZED, "replay_authorized": REPLAY_AUTHORIZED,
        "optimization_authorized": OPTIMIZATION_AUTHORIZED,
        "activation_authorized": ACTIVATION_AUTHORIZED,
        "paper_live_authorized": PAPER_LIVE_AUTHORIZED,
        "execution_authorized": EXECUTION_AUTHORIZED,
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True, "advances_nothing": True,
        "next_gate_token": NEXT_GATE_TOKEN,
        "next_action_after_labels": NEXT_ACTION_AFTER_LABELS,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    return record, agg_labels


def build_aggregate_payload(record: dict, agg_labels: list) -> dict[str, Any]:
    """PURE. The canonical multi-window artifact payload a FUTURE authorized build would write.
    Returned for determinism testing on synthetic inputs; this function writes NOTHING."""
    return {
        "candidate_id": CANDIDATE_ID,
        "window_start": WINDOW_START, "window_end": WINDOW_END,
        "expected_dates": list(EXPECTED_DATES),
        "aggregate_manifest_sha256": record["aggregate_manifest_sha256"],
        "market_rank_tiebreaker": list(MARKET_RANK_TIEBREAKER),
        "bear_high_multiple_single_sourced": BEAR_HIGH_MULT,
        "per_window": [{k: p[k] for k in ("run_date", "source_path", "sha256",
                                          "row_count", "btc_present", "btc_downtrend",
                                          "label_counts")}
                       for p in record["per_window"]],
        "aggregate_label_counts": record["aggregate_label_counts"],
        "labels": agg_labels}


def canonical_payload_bytes(payload: dict) -> bytes:
    """Byte-stable serialization the aggregate artifact SHA would be pinned over (matches the
    single-window runner's convention: indent=2, sort_keys, trailing newline)."""
    return (_json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def validate_multi_window(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, spec+impl-only, reuses the frozen
    core, all named authorization flags + capability flags are False, downstream gates locked,
    the canonical artifact is date-range-named (never today-tagged) and never overwrites the
    single-window artifact, and (for a READY manifest) exactly 20 contiguous windows / 50 per
    window / 1000 aggregate with no blockers."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record
    if r.get("mode") != MWL22_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_multi_window_spec_and_impl_only") is not True:
        failures.append("not_spec_impl_only")
    if r.get("reuses_single_window_core") is not True:
        failures.append("must_reuse_single_window_core")
    if r.get("bear_high_multiple_single_sourced") != _dr22.BEAR_HIGH_MULT:
        failures.append("bear_mult_drifted")
    if tuple(r.get("market_rank_tiebreaker") or ()) != tuple(_dv.MARKET_RANK_TIEBREAKER):
        failures.append("tiebreaker_drifted")
    if tuple(r.get("expected_dates") or ()) != EXPECTED_DATES:
        failures.append("expected_dates_wrong")
    # named authorization flags all False
    for k in ("build_authorized", "replay_authorized", "optimization_authorized",
              "activation_authorized", "paper_live_authorized", "execution_authorized"):
        if r.get(k) is not False:
            failures.append("authorization_flag_true:%s" % k)
    for k in ("replay_gate_locked", "paper_trading_gate_locked", "live_gate_locked",
              "advances_nothing", "never_date_tagged_today",
              "never_overwrites_single_window_artifact"):
        if r.get(k) is not True:
            failures.append("safety_flag_wrong:%s" % k)
    # canonical naming: date-range, not today; distinct from single-window artifact
    if r.get("mw_artifact_filename") != MW_ARTIFACT_FILENAME:
        failures.append("mw_artifact_name_wrong")
    if WINDOW_START not in str(r.get("mw_artifact_filename")) or \
            WINDOW_END not in str(r.get("mw_artifact_filename")):
        failures.append("mw_artifact_name_not_date_range_bound")
    if r.get("mw_artifact_filename") == SINGLE_WINDOW_ARTIFACT_FILENAME:
        failures.append("mw_artifact_collides_with_single_window")
    if r.get("next_gate_token") != _dv.NEXT_ACTION_VALID:
        failures.append("next_gate_token_not_canonical_reused")
    # READY-manifest structural guarantees
    if r.get("verdict") == VERDICT_MANIFEST_READY:
        if r.get("blockers"):
            failures.append("ready_with_blockers")
        if len(r.get("per_window") or []) != EXPECTED_WINDOWS:
            failures.append("ready_not_20_windows")
        if r.get("aggregate_labels_built") != TOTAL_LABELS:
            failures.append("ready_not_1000_labels")
        if not all(p.get("structurally_valid") is True and p.get("row_count") == LABELS_PER_WINDOW
                   for p in r.get("per_window") or []):
            failures.append("ready_window_not_valid_or_not_50")
        if [p["run_date"] for p in r.get("per_window")] != list(EXPECTED_DATES):
            failures.append("ready_dates_not_contiguous_expected")
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true:%s" % flag)
    return {"valid": not failures, "failures": failures}
