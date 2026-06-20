"""Candidate #22 -- external_signum_trend_radar_gc_long_short_v1
-- REAL-CANDLE ENTRY-SIGNAL LABELS (PURE, READ-ONLY, RESEARCH ONLY).

Produces deterministic per-asset ENTRY-SIGNAL labels from the locally-staged, SHA-pinned
Signum Trend Radar GC dataset, AFTER the human duplicate-marketRank resolution. It is
chain-gated on the dataset validation reaching VALID or VALID_VIA_TIEBREAKER; it orders the
50 assets by the human tie-breaker (marketRank asc, marketCap desc, symbol asc) and labels
each asset's latest CLOSED daily candle with the FROZEN C22 entry predicates:

  * LONG_ENTRY  -- close crosses up through the upper gc band
                   (latest.c > latest.gc.upper AND prev.c <= prev.gc.upper);
  * HEDGE_SHORT -- gc.trend == "Red" AND close crosses down through the gc filter
                   (latest.c < latest.gc.filter AND prev.c >= prev.gc.filter);
  * BEAR_SHORT  -- BTC in downtrend AND gc.trend == "Red" AND latest.high >= 0.98*filter
                   AND latest.c < filter;
  * NONE        -- no entry signal on the latest closed candle.

The single numeric constant (the bear high-reaches-filter multiple, 0.98) is single-sourced
from the frozen detector spec; nothing is invented. These are ENTRY-SIGNAL labels on one
closed-candle snapshot: position EXITS, NAV sizing, and the ticker-collision guard are
EXECUTION-stage concerns (no holdings, no pair price in a single snapshot) and are out of
label scope by design.

It performs NO file/network I/O (the runner reads the file + writes the gitignored
artifact), fetches NO data, MUTATES the dataset NOTHING, invents NO marketRank, runs NO
replay, optimizes NOTHING, advances NOTHING. Every dangerous capability is pinned False.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_candidate_spec_contract as _s22  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_detector_spec_dry_run_contract as _dr22  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_dataset_validation_contract as _dv  # noqa: E501

LB22_SCHEMA_VERSION = 1
LB22_MODE = "RESEARCH_ONLY"
LB22_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _s22.CANDIDATE_ID
CANDIDATE_TOKEN = _s22.CANDIDATE_TOKEN
CANDIDATE_FAMILY = _s22.CANDIDATE_FAMILY
CANDIDATE_NAME = _s22.CANDIDATE_NAME

# single-sourced from the frozen detector spec (NOT redefined).
BEAR_HIGH_MULT = _dr22.BEAR_HIGH_MULT                # 0.98
DATASET_PATH = _dv.DATASET_PATH
DATASET_SHA256 = _dv.DATASET_SHA256

BTC_SYMBOL = "BINANCE:BTCUSDT"

# the gitignored artifact the runner writes (under the per-candidate data dir).
ARTIFACT_DIR = "data/external_signum_trend_radar_gc/detector_labels"
ARTIFACT_BASENAME = "c22_gc_real_candle_entry_labels"

SIGNAL_LONG = "LONG_ENTRY"
SIGNAL_HEDGE = "HEDGE_SHORT"
SIGNAL_BEAR = "BEAR_SHORT"
SIGNAL_NONE = "NONE"
SIGNAL_SKIP = "SKIP"

VERDICT_LABELS_PRODUCED = "C22_REAL_CANDLE_ENTRY_LABELS_PRODUCED_FOR_HUMAN_REVIEW"
VERDICT_LABELS_BLOCKED = "C22_REAL_CANDLE_LABELS_BLOCKED"
NEXT_ACTION_AFTER_LABELS = (
    "HUMAN_DECISION_C22_REVIEW_REAL_CANDLE_LABELS_OR_REJECT")

# pinned SHA256 of the canonical labels artifact (set after first deterministic generation).
LABELS_ARTIFACT_SHA256 = (
    "bc434aebe056fd72670735442e58926f9df483cbbbf820308b153c36d12a8947")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "performs_file_io", "performs_network_io",
    "runs_replay", "runs_backtest", "computes_pnl", "optimizes_parameters",
    "tunes_parameters", "reparameterizes", "fetches_data", "stages_data",
    "mutates_data", "repairs_market_rank", "invents_ranks", "invents_rule_values",
    "auto_commits", "auto_pushes", "modifies_scheduler", "installs_scheduler",
    "sends_notifications", "sends_email", "calls_api", "uses_network", "uses_credentials",
    "uses_api_keys", "connects_signum", "uses_mcp", "accesses_hyperliquid",
    "connects_broker", "connects_exchange", "sends_trades", "edits_bots",
    "sets_trading_pair", "creates_claude_routines", "uses_real_money", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "unlocks_downstream_gate", "advances_without_human_approval",
    "modifies_c22_rules", "starts_c23", "reopens_c21", "crosses_into_forbidden_gate",
)


def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _candle(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    ohlc = raw.get("ohlc") or {}
    gc = raw.get("gc") or {}
    return {"o": ohlc.get("o"), "h": ohlc.get("h"), "l": ohlc.get("l"),
            "c": ohlc.get("c"), "trend": gc.get("trend"), "upper": gc.get("upper"),
            "filter": gc.get("filter"), "date": raw.get("date")}


def extract_label_rows(parsed: dict) -> dict[str, Any]:
    """PURE. Per-symbol latest+previous closed candle + rank/cap/ref from a parsed dataset.
    No I/O."""
    out: dict[str, Any] = {}
    for r in list((parsed or {}).get("results") or []):
        if not isinstance(r, dict):
            continue
        ind = r.get("indicators") or {}
        data = ind.get("data") or []
        latest = _candle(data[-1]) if len(data) >= 1 else None
        prev = _candle(data[-2]) if len(data) >= 2 else None
        out[r.get("symbol")] = {
            "symbol": r.get("symbol"), "market_rank": r.get("marketRank"),
            "market_cap": r.get("marketCap"), "cmc_ref": ind.get("cmcRefPriceUsd"),
            "latest": latest, "prev": prev,
            "latest_date": latest.get("date") if latest else None}
    return out


def _classify_signal(row: dict, btc_downtrend: bool) -> tuple:
    """PURE. The FROZEN C22 entry predicates on one asset's latest closed candle.
    Returns (signal, reasons, skip_reason)."""
    latest = row.get("latest")
    prev = row.get("prev")
    needed_latest = ("c", "h", "trend", "upper", "filter")
    if (not latest or not prev
            or any(latest.get(k) is None for k in needed_latest)
            or prev.get("c") is None or prev.get("upper") is None
            or prev.get("filter") is None):
        return SIGNAL_NONE, [], "missing_indicator_data"

    c, h = latest["c"], latest["h"]
    upper, filt, trend = latest["upper"], latest["filter"], latest["trend"]
    pc, pupper, pfilter = prev["c"], prev["upper"], prev["filter"]

    if c > upper and pc <= pupper:
        return SIGNAL_LONG, ["crossover_up_through_upper_gc_band"], None
    if trend == "Red" and c < filt and pc >= pfilter:
        return SIGNAL_HEDGE, ["red_cross_down_through_gc_filter"], None
    if (btc_downtrend and trend == "Red" and h >= BEAR_HIGH_MULT * filt
            and c < filt):
        return SIGNAL_BEAR, ["bear_btc_downtrend_high_reaches_filter_close_below"], None
    return SIGNAL_NONE, [], None


def build_labels(parsed: dict, sha256: str) -> dict[str, Any]:
    """Assemble the C22 real-candle entry-signal labels. Pure; no I/O. Chain-gated on the
    dataset validation reaching VALID / VALID_VIA_TIEBREAKER; orders assets by the human
    tie-breaker; labels each asset's latest closed candle. Deterministic for fixed input."""
    facts = _dv.extract_dataset_facts(parsed)
    validation = _dv.build_dataset_validation(facts, sha256)
    gate_ok = (validation["verdict"] in (_dv.VERDICT_VALID,
                                         _dv.VERDICT_VALID_VIA_TIEBREAKER)
               and validation["proceed_to_labels"] is True)

    rows = extract_label_rows(parsed)
    duplicate_ranks = set(facts.get("duplicate_market_ranks") or [])

    order_rows = [{"symbol": s, "market_rank": v.get("market_rank"),
                   "market_cap": v.get("market_cap")} for s, v in rows.items()]
    ordered = _dv.apply_market_rank_tiebreaker(order_rows)

    btc = rows.get(BTC_SYMBOL)
    btc_latest = btc.get("latest") if btc else None
    btc_present = bool(btc_latest and btc_latest.get("c") is not None
                       and btc_latest.get("filter") is not None)
    btc_downtrend = bool(btc_present and btc_latest["c"] < btc_latest["filter"])

    labels: list = []
    counts = {SIGNAL_LONG: 0, SIGNAL_HEDGE: 0, SIGNAL_BEAR: 0,
              SIGNAL_NONE: 0, SIGNAL_SKIP: 0}
    if gate_ok:
        for i, oref in enumerate(ordered):
            row = rows.get(oref["symbol"]) or {}
            signal, reasons, skip = _classify_signal(row, btc_downtrend)
            rank = row.get("market_rank")
            labels.append({
                "order_index": i, "symbol": oref["symbol"],
                "market_rank_raw": rank, "market_cap": row.get("market_cap"),
                "tie_broken": rank in duplicate_ranks,
                "latest_date": row.get("latest_date"),
                "signal": signal, "reasons": reasons, "skip_reason": skip})
            if skip:
                counts[SIGNAL_SKIP] += 1
            else:
                counts[signal] += 1

    labels_payload = {
        "candidate_id": CANDIDATE_ID,
        "dataset_path": DATASET_PATH,
        "dataset_sha256": DATASET_SHA256,
        "market_rank_tiebreaker": list(_dv.MARKET_RANK_TIEBREAKER),
        "btc_symbol": BTC_SYMBOL, "btc_present": btc_present,
        "btc_downtrend": btc_downtrend,
        "label_counts": counts, "labels": labels}

    blockers: list = []
    if not gate_ok:
        blockers.append("dataset_validation_not_valid:" + str(validation["verdict"]))

    record: dict[str, Any] = {
        "schema_version": LB22_SCHEMA_VERSION, "mode": LB22_MODE, "lane": LB22_LANE,
        "candidate_id": CANDIDATE_ID, "candidate_token": CANDIDATE_TOKEN,
        "candidate_family": CANDIDATE_FAMILY, "candidate_name": CANDIDATE_NAME,
        "is_real_candle_labels_only": True,
        "label": (
            "Candidate #22 real-candle entry-signal labels (READ-ONLY, RESEARCH ONLY). "
            "Per-asset LONG_ENTRY / HEDGE_SHORT / BEAR_SHORT / NONE on the latest closed "
            "daily candle, ordered by the human marketRank tie-breaker, single-sourcing the "
            "bear high-multiple from the frozen detector. Dataset not mutated; no rank "
            "invented; exits/sizing/collision are execution-stage and out of label scope. "
            "Runs no replay; advances nothing."),
        # chain provenance
        "dataset_validation_verdict": validation["verdict"],
        "dataset_validation_valid": _dv.validate_dataset_validation(validation)["valid"],
        "spec_commit": _dv.SPEC_COMMIT,
        "chain_gated_on_validation": gate_ok,
        "bear_high_multiple_single_sourced": BEAR_HIGH_MULT,
        # the labels
        "verdict": VERDICT_LABELS_PRODUCED if gate_ok else VERDICT_LABELS_BLOCKED,
        "blockers": blockers,
        "btc_present": btc_present, "btc_downtrend": btc_downtrend,
        "label_counts": counts,
        "labels_produced": len(labels),
        "labels": labels,
        "labels_payload": labels_payload,
        "market_rank_tiebreaker": list(_dv.MARKET_RANK_TIEBREAKER),
        "tie_broken_order_symbols": [o["symbol"] for o in ordered],
        # provenance + no-mutation guarantees
        "dataset_mutated": False, "repaired_market_rank": False, "invented_ranks": False,
        "raw_market_rank_preserved": True,
        # artifact metadata (runner writes to this gitignored path)
        "artifact_dir": ARTIFACT_DIR,
        "artifact_basename": ARTIFACT_BASENAME,
        "artifact_gitignored": True,
        "labels_artifact_sha256_pinned": LABELS_ARTIFACT_SHA256,
        # downstream gates locked; only the labels-review gate is next
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True, "advances_nothing": True,
        "next_required_action": NEXT_ACTION_AFTER_LABELS,
        "human_review_required": True,
        "current_loop_stage": "real_candle_labels",
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_file_io": True, "no_network_io": True,
        "no_replay": True, "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_data_fetch": True, "no_stage_data": True, "no_mutate_dataset": True,
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


def validate_labels(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, labels-only, chain-gated on a
    valid dataset validation (VALID / VALID_VIA_TIEBREAKER), 50 labels in tie-broken order,
    counts summing to the label total, the bear multiple single-sourced from the frozen
    detector, the dataset NOT mutated + NO rank invented, downstream gates locked + advances
    nothing, and every capability flag False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != LB22_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_real_candle_labels_only") is not True:
        failures.append("not_labels_only")
    if r.get("verdict") not in (VERDICT_LABELS_PRODUCED, VERDICT_LABELS_BLOCKED):
        failures.append("bad_verdict")

    # chain gate
    if r.get("spec_commit") != _dv.SPEC_COMMIT:
        failures.append("spec_commit_not_pinned")
    if r.get("bear_high_multiple_single_sourced") != BEAR_HIGH_MULT:
        failures.append("bear_multiple_not_single_sourced")

    produced = r.get("verdict") == VERDICT_LABELS_PRODUCED
    if produced:
        if r.get("chain_gated_on_validation") is not True:
            failures.append("not_chain_gated")
        if r.get("dataset_validation_verdict") not in (
                _dv.VERDICT_VALID, _dv.VERDICT_VALID_VIA_TIEBREAKER):
            failures.append("dataset_validation_not_valid")
        if r.get("dataset_validation_valid") is not True:
            failures.append("dataset_validation_record_invalid")
        labels = r.get("labels") or []
        if len(labels) != _dv.EXPECTED_ROW_COUNT:
            failures.append("labels_count_not_50")
        if r.get("labels_produced") != len(labels):
            failures.append("labels_produced_mismatch")
        # order_index is a strict 0..n-1 sequence
        if [lab.get("order_index") for lab in labels] != list(range(len(labels))):
            failures.append("order_index_not_sequential")
        # symbols unique (strict total order)
        if len({lab.get("symbol") for lab in labels}) != len(labels):
            failures.append("labels_symbols_not_unique")
        # counts sum to total
        counts = r.get("label_counts") or {}
        if sum(counts.values()) != len(labels):
            failures.append("counts_do_not_sum_to_total")
        # every signal is in the closed set
        for lab in labels:
            if lab.get("signal") not in (SIGNAL_LONG, SIGNAL_HEDGE, SIGNAL_BEAR,
                                         SIGNAL_NONE):
                failures.append("label_signal_outside_closed_set")
                break
        if list(r.get("market_rank_tiebreaker") or []) != list(
                _dv.MARKET_RANK_TIEBREAKER):
            failures.append("tiebreaker_tampered")

    # no-mutation invariants
    for k in ("dataset_mutated", "repaired_market_rank", "invented_ranks"):
        if r.get(k) is not False:
            failures.append("must_not_%s" % k)
    if r.get("raw_market_rank_preserved") is not True:
        failures.append("raw_rank_not_preserved")

    # artifact gitignored + sha pinned
    if not str(r.get("artifact_dir", "")).startswith("data/external_signum_trend_radar_gc"):
        failures.append("artifact_dir_wrong")
    if r.get("artifact_gitignored") is not True:
        failures.append("artifact_not_gitignored")
    if r.get("labels_artifact_sha256_pinned") != LABELS_ARTIFACT_SHA256:
        failures.append("labels_sha_pin_tampered")

    # downstream locked + advances nothing
    for gate in ("replay_gate_locked", "paper_trading_gate_locked", "live_gate_locked"):
        if r.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")
    if r.get("next_required_action") != NEXT_ACTION_AFTER_LABELS:
        failures.append("next_action_not_labels_review")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_file_io", "no_network_io", "no_replay", "no_pnl",
                "no_optimization", "no_data_fetch", "no_mutate_dataset",
                "no_repair_market_rank", "no_invent_ranks", "no_commit", "no_push",
                "no_signum_connection", "no_mcp", "no_hyperliquid", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_modify_c22_rules",
                "no_start_c23", "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
