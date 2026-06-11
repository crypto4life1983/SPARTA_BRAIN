"""SPARTA NY-Session FVG+CHOCH REPLAY RUNNER - DRY RUN (RESEARCH ONLY).

The first executable research piece in the auto-research lane: a deterministic
replay of ACCEPTED detector labels against PROVIDED in-memory candles only.
Net-after-costs always; gross-only pass claims impossible; every rejection
auditable. No network, no fetch, no orders, no scoring, no promotion, no loop.

Deterministic simulation rules (long; short is the mirror):
  - entry triggers when a candle's low touches the proposed entry price
  - pre-entry: a candle touching the stop without touching entry rejects the
    replay as STOP_BEFORE_ENTRY; touching both is conservatively an
    entry-then-immediate-stop loss
  - post-entry, per candle, conservative order: stop checked BEFORE target
  - breakeven: only after a candle CLOSES beyond entry + 1R (the modeled
    structure confirmation) AND the request enables it; stop then moves to
    entry
  - neither stop nor target by replay_end_time: honest timeout exit at the
    last in-window close
  - costs: fees + spread + slippage (bps of entry notional) converted to R
    and charged before net_r_after_costs
"""

from __future__ import annotations

import datetime as _dt
from typing import Any

from sparta_commander.ny_session_fvg_choch_replay_spec import (
    CANDIDATE_ID,
    REPLAY_OUTPUT_FIELDS,
    REPLAY_STATUSES,
    VERDICT_RP_READY,
    build_ny_fvg_choch_replay_spec,
    validate_ny_fvg_choch_replay_spec,
    validate_replay_output_record,
)

RR_SCHEMA_VERSION = "ny_session_fvg_choch_replay_runner_dry_run.v1"
RR_LABEL = ("SPARTA NY-Session FVG+CHOCH Replay Runner Dry Run "
            "(RESEARCH ONLY, FIXTURE CANDLES ONLY)")
RR_MODE = "RESEARCH_ONLY"
NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_DRY_RUN_REPLAY_RESULTS"

_FORBIDDEN_KEY_TOKENS = ("order", "api_key", "credential", "wallet",
                         "account", "login", "fetch_url", "live_authorized",
                         "paper_authorized", "scorer_patch")
_COSTS = ("fees_bps", "spread_bps", "slippage_bps")


def get_replay_runner_dry_run_label() -> str:
    return RR_LABEL


def _ts(value: Any) -> _dt.datetime | None:
    try:
        return _dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _base_record(label: Any) -> dict[str, Any]:
    record: dict[str, Any] = {f: None for f in REPLAY_OUTPUT_FIELDS}
    record["candidate_id"] = CANDIDATE_ID
    record["runner_authorizes_nothing"] = True
    if isinstance(label, dict):
        for key in ("setup_id", "symbol", "session_date", "direction"):
            record[key] = label.get(key)
    return record


def _reject(record: dict[str, Any], status: str, reason: str) -> dict[str, Any]:
    record["replay_status"] = status
    record["rejection_reason"] = reason
    record["audit_notes"] = "rejected replay kept on record: " + reason
    return record


def run_replay_dry_run(label: Any, request: Any) -> dict[str, Any]:
    """ONE deterministic dry-run replay. Pure; fixture candles only."""
    record = _base_record(label)

    spec = build_ny_fvg_choch_replay_spec()
    if (not validate_ny_fvg_choch_replay_spec(spec).get("valid")
            or spec.get("verdict") != VERDICT_RP_READY):
        return _reject(record, "REPLAY_REJECTED_INVALID_LABEL",
                       "replay_spec_not_ready")
    if not isinstance(label, dict) or label.get(
            "detector_status") != "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW":
        return _reject(record, "REPLAY_REJECTED_INVALID_LABEL",
                       "detector_label_missing_or_not_accepted")
    if not isinstance(request, dict):
        return _reject(record, "REPLAY_REJECTED_INVALID_LABEL",
                       "request_not_a_dict")
    for key in list(request) + list(label):
        lowered = str(key).lower()
        for token in _FORBIDDEN_KEY_TOKENS:
            if token in lowered:
                return _reject(record, "REPLAY_REJECTED_FORBIDDEN_CAPABILITY",
                               "forbidden_field:" + str(key))
    for cost in _COSTS:
        raw = request.get(cost)
        if not isinstance(raw, (int, float)) or isinstance(raw, bool) or raw < 0:
            return _reject(record, "REPLAY_REJECTED_COSTS_UNDEFINED",
                           "cost_missing_or_invalid:" + cost)

    candles = request.get("candles")
    if not isinstance(candles, list) or not candles:
        return _reject(record, "REPLAY_REJECTED_MISSING_CANDLES",
                       "candles_missing_or_empty")
    for c in candles:
        if not isinstance(c, dict) or _ts(c.get("timestamp_utc")) is None or not all(
                isinstance(c.get(k), (int, float)) and not isinstance(c.get(k), bool)
                for k in ("high", "low", "close")):
            return _reject(record, "REPLAY_REJECTED_MISSING_CANDLES",
                           "candle_incomplete")

    direction = label.get("direction")
    entry = label.get("proposed_entry_price")
    stop = label.get("proposed_stop_price")
    target = label.get("proposed_target_4r_price")
    if direction not in ("long", "short") or not all(
            isinstance(x, (int, float)) and not isinstance(x, bool)
            for x in (entry, stop, target)):
        return _reject(record, "REPLAY_REJECTED_INVALID_LABEL",
                       "label_prices_or_direction_invalid")
    risk = abs(float(entry) - float(stop))
    if risk <= 0:
        return _reject(record, "REPLAY_REJECTED_INVALID_LABEL", "zero_risk")
    sign = 1.0 if direction == "long" else -1.0

    start = _ts(request.get("replay_start_time"))
    end = _ts(request.get("replay_end_time"))
    window = [c for c in candles
              if (start is None or _ts(c["timestamp_utc"]) >= start)
              and (end is None or _ts(c["timestamp_utc"]) <= end)]
    if not window:
        return _reject(record, "REPLAY_REJECTED_MISSING_CANDLES",
                       "no_candles_inside_replay_window")

    def touched_entry(c):  # price reaches the entry level
        return c["low"] <= entry if direction == "long" else c["high"] >= entry

    def touched(level, c):  # adverse/favorable level touch
        return c["low"] <= level if direction == "long" else c["high"] >= level

    entered = False
    current_stop = float(stop)
    breakeven_on = request.get("breakeven_enabled") is True
    record.update({"entry_price": float(entry), "stop_price": float(stop),
                   "target_4r_price": float(target),
                   "breakeven_triggered": False, "entry_triggered": False})
    mae = mfe = 0.0
    exit_price = exit_reason = exit_time = None

    for c in window:
        if not entered:
            stop_touch = (c["low"] <= stop if direction == "long"
                          else c["high"] >= stop)
            if stop_touch and not touched_entry(c):
                return _reject(record, "REPLAY_REJECTED_STOP_BEFORE_ENTRY",
                               "stop_level_traded_before_entry")
            if touched_entry(c):
                entered = True
                record["entry_triggered"] = True
                record["entry_time"] = c["timestamp_utc"]
                if stop_touch:  # same-candle ambiguity: conservative loss
                    exit_price, exit_reason = float(stop), "stop_hit_same_candle"
                    exit_time = c["timestamp_utc"]
                    break
            continue
        adverse_r = sign * (entry - (c["low"] if direction == "long"
                                     else c["high"])) / risk
        favorable_r = sign * ((c["high"] if direction == "long"
                               else c["low"]) - entry) / risk
        mae, mfe = max(mae, adverse_r), max(mfe, favorable_r)
        stop_touch = (c["low"] <= current_stop if direction == "long"
                      else c["high"] >= current_stop)
        if stop_touch:  # conservative: stop before target
            exit_price = float(current_stop)
            exit_reason = ("breakeven_stop_hit"
                           if record["breakeven_triggered"] else "stop_hit")
            exit_time = c["timestamp_utc"]
            break
        target_touch = (c["high"] >= target if direction == "long"
                        else c["low"] <= target)
        if target_touch:
            exit_price, exit_reason = float(target), "target_4r_hit"
            exit_time = c["timestamp_utc"]
            break
        # modeled structure confirmation: close beyond entry + 1R
        if breakeven_on and not record["breakeven_triggered"] and sign * (
                c["close"] - entry) >= risk:
            record["breakeven_triggered"] = True
            record["breakeven_time"] = c["timestamp_utc"]
            current_stop = float(entry)

    if not entered:
        return _reject(record, "REPLAY_REJECTED_NO_ENTRY",
                       "entry_level_never_traded_in_window")
    if exit_price is None:  # honest timeout exit
        last = window[-1]
        exit_price, exit_reason = float(last["close"]), "timeout_end_of_window"
        exit_time = last["timestamp_utc"]

    gross_r = sign * (exit_price - float(entry)) / risk
    cost_r = (sum(float(request[c]) for c in _COSTS) / 10000.0) * float(entry) / risk
    record.update({
        "exit_price": exit_price, "exit_reason": exit_reason,
        "exit_time": exit_time, "gross_r": round(gross_r, 6),
        "net_r_after_costs": round(gross_r - cost_r, 6),
        "gross_pnl_model": round(sign * (exit_price - float(entry)), 6),
        "net_pnl_model_after_costs": round(
            sign * (exit_price - float(entry))
            - (sum(float(request[c]) for c in _COSTS) / 10000.0) * float(entry), 6),
        "max_adverse_excursion_r": round(mae, 6),
        "max_favorable_excursion_r": round(mfe, 6),
        "replay_status": "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW",
        "rejection_reason": None,
        "audit_notes": "dry run on fixture candles; net charged "
                       + str(sum(float(request[c]) for c in _COSTS)) + " bps",
    })
    assert record["replay_status"] in REPLAY_STATUSES
    check = validate_replay_output_record(record)
    if not check["acceptable"]:
        return _reject(record, "REPLAY_REJECTED_INVALID_LABEL",
                       "output_failed_replay_spec:" + ";".join(check["errors"]))
    return record
