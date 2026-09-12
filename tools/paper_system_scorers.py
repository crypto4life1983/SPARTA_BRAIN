"""Phase 2 of the SPARTA self-improving trading loop: READ-ONLY paper-system scorers.

Posture (non-negotiable):
  * Research / observation only. No broker, no orders, no execution path, no keys.
  * The external project ``obsidian-trade-logger`` is READ ONLY here: its report /
    state files are opened for reading and nothing under it is ever written.
  * The only files written live under ``C:\\SPARTA_BRAIN\\reports\\trade_learning\\``.
  * Nothing here invents a gate. Each scorer maps the line's OWN pre-registered
    window and gates (cited in ``criteria_file``) onto one status vocabulary:
        SHADOW | CONFIRMED | REJECTED | BLOCKED | NO_DATA
    CONFIRMED / REJECTED are reads of a paper window, never a live-readiness
    claim and never a strategy approval.

Status rules (design doc ``reports/trade_learning/self_improving_loop_design_2026-09-11.md``):
  * NO_DATA   - the line's files are missing / unreadable.
  * BLOCKED   - the tracker itself says PAUSE / halted, or its data is stale by its
                own staleness threshold.
  * CONFIRMED - own window satisfied AND every own (non-manual) gate PASS AND sign POSITIVE.
  * REJECTED  - own window satisfied AND (sign NEGATIVE OR any hard own gate FAIL).
  * SHADOW    - everything else (window open, gate not evaluable, sign flat, ...).

Usage:
    .venv\\Scripts\\python tools\\paper_system_scorers.py [--as-of YYYY-MM-DD]

Pure core: ``score_<line>(inputs, as_of)`` and ``decide(...)`` are deterministic for
fixed input (no clocks, no randomness, sorted keys everywhere). Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.trade_journal_adapter import external_root  # noqa: E402  (reuse, never modify)

# ── constants ───────────────────────────────────────────────────────────────

BANNER = (
    "READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · "
    "NO STRATEGY APPROVAL · NO BROKER / NO ORDER"
)
FORBIDDEN_WORDS = ("validated", "ready", "approved", "profitable strategy", "deploy")
_FORBIDDEN_RE = re.compile(
    r"\b(validated|ready|approved|profitable strategy|deploy\w*)\b", re.IGNORECASE
)

REPORT_DIR = _REPO_ROOT / "reports" / "trade_learning"
SCORECARD_JSON = "paper_systems_scorecard.json"
SCORECARD_MD = "paper_systems_scorecard.md"
HISTORY_JSONL = "paper_systems_history.jsonl"

STATUS_SHADOW = "SHADOW"
STATUS_CONFIRMED = "CONFIRMED"
STATUS_REJECTED = "REJECTED"
STATUS_BLOCKED = "BLOCKED"
STATUS_NO_DATA = "NO_DATA"
STATUSES = (STATUS_SHADOW, STATUS_CONFIRMED, STATUS_REJECTED, STATUS_BLOCKED, STATUS_NO_DATA)

SIGN_POSITIVE, SIGN_NEGATIVE, SIGN_FLAT, SIGN_NONE = "POSITIVE", "NEGATIVE", "FLAT", "NONE"

GATE_PASS = "PASS"
GATE_FAIL = "FAIL"
GATE_PENDING = "PENDING"            # window still accruing; value is evolving
GATE_NOT_EVALUABLE = "NOT_EVALUABLE"  # the line's own gate needs data the tracker does not emit
GATE_MANUAL = "MANUAL"              # human sign-off gate; outside any automated read

LINE_FUNDING_CARRY = "funding_carry_paper"
LINE_NQ_ORB = "nq_orb_paper"
LINE_GC_ICT = "gc_ict_paper"
LINE_FROZEN_STACK = "frozen_stack_paper_forward"
LINE_S21 = "s21_weekly_rs_paper"
LINES = (LINE_FUNDING_CARRY, LINE_NQ_ORB, LINE_GC_ICT, LINE_FROZEN_STACK, LINE_S21)

RECORD_KEYS = (
    "line", "source_files", "launched", "as_of", "days_elapsed", "window", "sample",
    "sign", "headline_metrics", "own_gates", "status", "reason", "recommendation",
    "criteria_file",
)

# Each tracker's OWN staleness threshold (hours). Cited, not invented:
#   funding carry : funding_carry_phase7_paper_plan.md section 7 (CRITICAL > 48 h)
#   NQ ORB        : nq_paper_tracker/alerts.py DATA_STALE_HOURS = 48
#   GC ICT        : gc_paper_tracker/pipeline.py  stale_hours > 48 -> WATCH DATA_STALE
STALE_HOURS_TRACKER = 48.0

# Frozen-stack out-of-sample split (corrected 2026-09-12). The external 1m cache had stopped
# at 2026-03-31, so the bot could not see any bar after that date; refreshing it on 2026-09-11
# produced rows with entry dates from 2026-04 onward. Those entries were never available to the
# bot while its parameters were locked, so they are genuine OUT-OF-SAMPLE evidence even though
# they are not "forward from today". Rows at or before the old ceiling are backfill and are
# reported separately, never scored. This is a data ceiling, not a registration date: it is
# disclosed as such wherever the line is reported.
FROZEN_STACK_FORWARD_SPLIT = "2026-03-31"
FROZEN_STACK_SPLIT_BASIS = ("previous external 1m-cache ceiling; entries after it were "
                            "unavailable to the bot under its locked parameters")
# The "60-90 day clean paper run" in the source doc means days of the bot actually RUNNING
# forward, not calendar days spanned by data it back-filled in one pass. The cache was
# refreshed on 2026-09-11 and the first run over it was 2026-09-12, so the clean-run clock
# starts there. Out-of-sample ROWS are still identified by FROZEN_STACK_FORWARD_SPLIT.
FROZEN_STACK_OPERATION_START = "2026-09-12"

# A paper line whose operator closure decision is recorded stops being an open question: the
# scorer reports the recorded closure instead of re-deriving a live status, so a closed line
# never reappears in the daily human queue.
CLOSURE_DECISION_GLOBS = ("CLOSURE_DECISION_*.md",)

# Frozen stack own thresholds (read from analytics/final_stack_operational_validation.py and
# reports/final_frozen_architecture.md section 8 / 9 in the external project).
FROZEN_STACK_DD_ENVELOPE_PCT = -10.0
FROZEN_STACK_D4_REPRO_MIN_PCT = 90.0
FROZEN_STACK_BURN_IN_DAYS = 30
FROZEN_STACK_CLEAN_RUN_DAYS = "60-90"   # section 9 states a range, not one number
FROZEN_STACK_CLEAN_RUN_DAYS_CONSERVATIVE = 90

# s21 manifest constants are read from the harness manifest at load time (never copied here).
S21_REL_STATE = ("paper_trading", "weekly_rs_s21_forward_paper_harness", "runs", "cycles_v2",
                 "harness_state.json")
S21_LEGACY_NOTE = ("legacy runs/dry_cycle_001/002 are NOT valid evidence "
                   "(brain_memory/projects/trading_bot/lessons.md LESSON_S21_PAPER_001/002)")

OBS_ONLY = "Observation only: no rule change, no strategy approval, no live-readiness claim."


# ── small helpers ────────────────────────────────────────────────────────────

def _parse_date(v: Any) -> date | None:
    if v is None:
        return None
    if isinstance(v, date):
        return v
    s = str(v).strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(s[:10])
        except ValueError:
            return None


def _days_between(start: Any, end: Any) -> int | None:
    a, b = _parse_date(start), _parse_date(end)
    if a is None or b is None:
        return None
    return (b - a).days


def _num(v: Any, default: float | None = None) -> float | None:
    if v is None or v == "":
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _bool(v: Any) -> bool | None:
    """Trackers emit bools, or the strings 'True' / 'False'. Never trust truthiness of a str."""
    if isinstance(v, bool):
        return v
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in ("true", "1", "yes"):
        return True
    if s in ("false", "0", "no"):
        return False
    return None


def _round(v: Any, nd: int = 4) -> float | None:
    f = _num(v)
    return None if f is None else round(f, nd)


def sign_of(pnl: Any) -> str:
    f = _num(pnl)
    if f is None:
        return SIGN_NONE
    if f > 0:
        return SIGN_POSITIVE
    if f < 0:
        return SIGN_NEGATIVE
    return SIGN_FLAT


def gate(name: str, threshold: Any, value: Any, status: str, hard: bool = True,
         note: str = "") -> dict[str, Any]:
    g = {"name": name, "threshold": threshold, "value": value, "status": status, "hard": hard}
    if note:
        g["note"] = note
    return g


def _cmp_gate(name: str, threshold: Any, value: float | None, ok: bool | None, hard: bool = True,
              pending: bool = False, note: str = "") -> dict[str, Any]:
    if value is None or ok is None:
        return gate(name, threshold, value, GATE_NOT_EVALUABLE, hard, note or "value missing")
    if pending and not ok:
        return gate(name, threshold, value, GATE_PENDING, hard, note)
    return gate(name, threshold, value, GATE_PASS if ok else GATE_FAIL, hard, note)


def forbidden_words_found(text: str) -> list[str]:
    return sorted({m.group(0).lower() for m in _FORBIDDEN_RE.finditer(text or "")})


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _read_csv(path: Path) -> list[dict[str, str]] | None:
    try:
        with path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))
    except (OSError, ValueError):
        return None


# ── the one decision function ────────────────────────────────────────────────

def decide(window_satisfied: bool, sign: str, gates: list[dict[str, Any]],
           blocked_reason: str = "", no_data_reason: str = "",
           window_desc: str = "") -> tuple[str, str]:
    """Map (window, sign, own gates, tracker state) -> (status, reason). Pure."""
    if no_data_reason:
        return STATUS_NO_DATA, no_data_reason
    if blocked_reason:
        return STATUS_BLOCKED, blocked_reason
    scored = [g for g in gates if g["status"] != GATE_MANUAL]
    hard_fail = [g["name"] for g in scored if g["hard"] and g["status"] == GATE_FAIL]
    if window_satisfied:
        if sign == SIGN_NEGATIVE or hard_fail:
            parts = [f"own window satisfied ({window_desc})" if window_desc else "own window satisfied"]
            if sign == SIGN_NEGATIVE:
                parts.append("sign NEGATIVE")
            if hard_fail:
                parts.append("hard gate FAIL: " + ", ".join(hard_fail))
            return STATUS_REJECTED, "; ".join(parts)
        unresolved = [f"{g['name']}={g['status']}" for g in scored if g["status"] != GATE_PASS]
        if sign == SIGN_POSITIVE and not unresolved:
            return STATUS_CONFIRMED, (f"own window satisfied ({window_desc}); sign POSITIVE; "
                                      f"all {len(scored)} own gates PASS")
        bits = [f"own window satisfied ({window_desc})" if window_desc else "own window satisfied"]
        if sign != SIGN_POSITIVE:
            bits.append(f"sign {sign}")
        if unresolved:
            bits.append("unresolved own gates: " + ", ".join(unresolved))
        return STATUS_SHADOW, "; ".join(bits)
    tail = f" ({window_desc})" if window_desc else ""
    extra = ("; hard gate FAIL so far: " + ", ".join(hard_fail)) if hard_fail else ""
    return STATUS_SHADOW, f"own window not yet satisfied{tail}{extra}"


def _record(**kw: Any) -> dict[str, Any]:
    rec = {k: kw.get(k) for k in RECORD_KEYS}
    rec["source_files"] = sorted(str(p) for p in (rec["source_files"] or []))
    rec["own_gates"] = list(rec["own_gates"] or [])
    rec["headline_metrics"] = dict(rec["headline_metrics"] or {})
    rec.setdefault("window", {"kind": None, "end_or_min_n": None, "satisfied": False})
    rec.setdefault("sample", {})
    if rec["sign"] is None:
        rec["sign"] = SIGN_NONE
    if rec["recommendation"] is None:
        rec["recommendation"] = OBS_ONLY
    return rec


def _tracker_status_from_alerts(alerts: list[dict[str, Any]] | None) -> str:
    sev = {str(a.get("severity")) for a in (alerts or [])}
    if "CRITICAL" in sev:
        return "PAUSE"
    if "WATCH" in sev:
        return "WATCH"
    return "ON-TRACK"


def _blocked_reason(tracker_status: str | None, stale_hours: float | None,
                    alerts: list[dict[str, Any]] | None) -> str:
    if tracker_status and str(tracker_status).upper().replace(" ", "-") == "PAUSE":
        codes = ",".join(sorted(str(a.get("code")) for a in (alerts or [])
                                if a.get("severity") == "CRITICAL")) or "n/a"
        return f"tracker status PAUSE (CRITICAL alerts: {codes})"
    if stale_hours is not None and stale_hours > STALE_HOURS_TRACKER:
        return f"tracker data stale: {stale_hours:.1f} h > {STALE_HOURS_TRACKER:.0f} h (own threshold)"
    return ""


# ── 1. funding carry paper ───────────────────────────────────────────────────

FC_CRITERIA = "obsidian-trade-logger/reports/funding_carry_phase7_paper_plan.md (section 7 alerts, section 8 graduation criteria)"
FC_WINDOW_DAYS = 90                 # section 8 item 1
FC_PHASE6B_WORST_OOS_DD_PCT = -0.89  # section 8 item 3 (Phase 6B worst-OOS drawdown)
FC_DD_ACCEPTABLE_MULT = 3.0          # "a 3x deterioration would still be acceptable"
FC_DD_UNACCEPTABLE_MULT = 10.0       # "a 10x deterioration would not"
FC_CAGR_TOLERANCE = 0.30             # section 8 item 2 (+/- 30% of the same-period Phase-6B estimate)
FC_PHASE6B_FULL_SAMPLE_CAGR_PCT = 8.08  # funding_carry_phase6b_execution_refinement.md table (reference only)
_FC_DATA_OUTAGE_CODES = ("DATA_STALE", "DATA_MISSING")


def score_funding_carry(inputs: dict[str, Any], as_of: str) -> dict[str, Any]:
    """inputs: {latest: dict|None, alerts_rows: list[dict]|None, phase8_report_present: bool|None,
                source_files: list[str]}"""
    latest = inputs.get("latest")
    src = inputs.get("source_files") or []
    if not latest:
        st, rs = decide(False, SIGN_NONE, [], no_data_reason="latest.json missing or unreadable")
        return _record(line=LINE_FUNDING_CARRY, source_files=src, launched=None, as_of=as_of,
                       days_elapsed=None, sign=SIGN_NONE, own_gates=[], status=st, reason=rs,
                       criteria_file=FC_CRITERIA)
    ts = latest.get("tracker_state") or {}
    si = latest.get("since_inception") or {}
    fresh = latest.get("data_freshness") or {}
    alerts_active = latest.get("alerts_active") or []
    launched = (_parse_date(ts.get("launch_date_utc")) or date(2026, 5, 13)).isoformat()
    days = _days_between(launched, as_of)
    days_tracker = int(_num(ts.get("days_since_launch"), days or 0) or 0)
    initial = _num(ts.get("initial_capital"), 10_000.0)
    equity = _num(si.get("final_equity_usd"), _num(ts.get("paper_equity")))
    net_pnl = None if equity is None or initial is None else equity - initial
    max_dd_pct = _num(si.get("max_drawdown_pct"))
    stale_h = _num(fresh.get("stale_hours"))
    tracker_status = latest.get("status") or _tracker_status_from_alerts(alerts_active)

    ann_ret = None
    if equity and initial and days_tracker > 0:
        ann_ret = (equity / initial) ** (365.0 / days_tracker) - 1.0

    # gate 1: >= 90 calendar days without a CRITICAL alert that was not a known data outage
    rows = inputs.get("alerts_rows")
    if rows is None:
        non_outage_crit = sum(1 for a in alerts_active if a.get("severity") == "CRITICAL"
                              and not str(a.get("code", "")).startswith(_FC_DATA_OUTAGE_CODES))
        g1_note = "alerts.csv not supplied; counted ACTIVE non-outage CRITICAL alerts only"
    else:
        non_outage_crit = 0
        for r in rows:
            if str(r.get("severity")) != "CRITICAL":
                continue
            d = _parse_date(r.get("report_date_utc"))
            if d is not None and d.isoformat() < launched:
                continue
            if str(r.get("code", "")).startswith(_FC_DATA_OUTAGE_CODES):
                continue
            non_outage_crit += 1
        g1_note = "counted CRITICAL rows in alerts.csv since launch, excluding DATA_STALE*/DATA_MISSING* outage codes"
    window_ok = days_tracker >= FC_WINDOW_DAYS
    g1 = _cmp_gate("g1_90d_without_non_outage_critical",
                   f">= {FC_WINDOW_DAYS} days and 0 non-outage CRITICAL",
                   float(non_outage_crit), window_ok and non_outage_crit == 0,
                   pending=not window_ok, note=g1_note)
    # gate 2: realized CAGR within +/-30% of the same-period Phase-6B simulator estimate
    g2 = gate("g2_realized_cagr_within_30pct_of_phase6b_same_period",
              f"+/- {int(FC_CAGR_TOLERANCE * 100)}% of same-period Phase-6B estimate",
              _round(ann_ret, 5), GATE_NOT_EVALUABLE, True,
              "the tracker does not emit a same-period Phase-6B simulator estimate; the full-sample "
              f"Phase-6B OOS CAGR (+{FC_PHASE6B_FULL_SAMPLE_CAGR_PCT}%) is shown in headline_metrics for "
              "reference only and is NOT the plan's gate quantity")
    # gate 3: max drawdown not materially worse than 3x the Phase-6B worst-OOS drawdown (-0.89%)
    dd_ok_thr = FC_PHASE6B_WORST_OOS_DD_PCT * FC_DD_ACCEPTABLE_MULT / 100.0
    dd_bad_thr = FC_PHASE6B_WORST_OOS_DD_PCT * FC_DD_UNACCEPTABLE_MULT / 100.0
    if max_dd_pct is None:
        g3 = gate("g3_max_dd_vs_phase6b_worst_oos", f">= {dd_ok_thr:.4f} (3x of -0.89%)", None,
                  GATE_NOT_EVALUABLE, True, "max_drawdown_pct missing")
    elif max_dd_pct >= dd_ok_thr:
        g3 = gate("g3_max_dd_vs_phase6b_worst_oos", f">= {dd_ok_thr:.4f} (3x of -0.89%)",
                  _round(max_dd_pct, 6), GATE_PASS, True)
    elif max_dd_pct <= dd_bad_thr:
        g3 = gate("g3_max_dd_vs_phase6b_worst_oos", f">= {dd_ok_thr:.4f} (3x of -0.89%)",
                  _round(max_dd_pct, 6), GATE_FAIL, True, "worse than 10x the Phase-6B worst-OOS drawdown")
    else:
        g3 = gate("g3_max_dd_vs_phase6b_worst_oos", f">= {dd_ok_thr:.4f} (3x of -0.89%)",
                  _round(max_dd_pct, 6), GATE_NOT_EVALUABLE, True,
                  "between 3x and 10x of the Phase-6B worst-OOS drawdown: the plan leaves this to review")
    p8 = inputs.get("phase8_report_present")
    g4 = gate("g4_phase8_basis_aware_completed_and_reviewed", "report present and reviewed by a human",
              p8, GATE_MANUAL, True, "reviewed-by-human is not machine-readable")
    g5 = gate("g5_explicit_human_sign_off", "written go-live note", None, GATE_MANUAL, True,
              "outside any automated read")
    gates = [g1, g2, g3, g4, g5]

    sign = sign_of(net_pnl)
    window = {"kind": "calendar_days_since_launch", "end_or_min_n": FC_WINDOW_DAYS,
              "satisfied": bool(window_ok)}
    wdesc = f"{days_tracker}/{FC_WINDOW_DAYS} days"
    blocked = _blocked_reason(tracker_status, stale_h, alerts_active)
    status, reason = decide(window["satisfied"], sign, gates, blocked_reason=blocked, window_desc=wdesc)
    metrics = {
        "tracker_status": tracker_status,
        "strategy_label": latest.get("strategy_label"),
        "report_date": (_parse_date(latest.get("report_date_utc")) or date.min).isoformat(),
        "report_age_days": _days_between(latest.get("report_date_utc"), as_of),
        "initial_capital_usd": initial,
        "final_equity_usd": _round(equity, 2),
        "net_pnl_usd": _round(net_pnl, 2),
        "funding_pnl_total_usd": _round(si.get("funding_pnl_total_usd"), 2),
        "basis_pnl_total_usd": _round(si.get("basis_pnl_total_usd"), 2),
        "total_simulated_costs_usd": _round(si.get("total_simulated_costs_usd"), 2),
        "cost_consumption_pct": _round(si.get("cost_consumption_pct"), 4),
        "max_drawdown_pct": _round(max_dd_pct, 6),
        "n_position_changes": si.get("n_position_changes"),
        "realized_annualized_return": _round(ann_ret, 5),
        "phase6b_full_sample_oos_cagr_pct_reference_only": FC_PHASE6B_FULL_SAMPLE_CAGR_PCT,
        "stale_hours": _round(stale_h, 1),
        "active_alert_codes": sorted(str(a.get("code")) for a in alerts_active),
    }
    rec_text = _recommendation_text(LINE_FUNDING_CARRY, status, reason, "plan section 8: 'If any of these is unmet, paper tracking continues without going live.'")
    return _record(line=LINE_FUNDING_CARRY, source_files=src, launched=launched, as_of=as_of,
                   days_elapsed=days, window=window,
                   sample={"n_days": days_tracker, "n_position_changes": si.get("n_position_changes")},
                   sign=sign, headline_metrics=metrics, own_gates=gates, status=status,
                   reason=reason, recommendation=rec_text, criteria_file=FC_CRITERIA)


# ── 2 + 3. NQ ORB / GC ICT paper (same graduation shape, each with its own doc) ─

NQ_CRITERIA = "obsidian-trade-logger/reports/nq_phase12_paper_plan.md (section 5 graduation criteria; section 4 alert thresholds; nq_paper_tracker/alerts.py)"
GC_CRITERIA = "obsidian-trade-logger/reports/observation_mode/gc_ict_observation_rules.md (review milestones + graduation criteria; gc_paper_tracker/spec.py LAUNCH_DATE)"


def _recorded_closure(inputs: dict[str, Any]) -> dict[str, Any] | None:
    """An operator closure decision recorded next to the tracker, if any.

    A line the operator has closed is no longer an open question: it must not be
    re-derived from a stale tracker, and it must not reappear in the daily human
    queue. Returns {"path": str, "text": str} or None."""
    for path_str in (inputs.get("closure_files") or []):
        try:
            text = Path(path_str).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if text.strip():
            return {"path": path_str, "text": text}
    return None


def _closed_record(line: str, criteria: str, inputs: dict[str, Any], as_of: str,
                   closure: dict[str, Any]) -> dict[str, Any]:
    first = next((ln.strip() for ln in closure["text"].splitlines()
                  if ln.strip().startswith("**Decision")), "").strip("* ")
    return _record(line=line, source_files=(inputs.get("source_files") or []) + [closure["path"]],
                   launched=None, as_of=as_of, days_elapsed=None,
                   window={"kind": "closed_by_operator", "end_or_min_n": None, "satisfied": True},
                   sample={}, sign=SIGN_NONE, headline_metrics={}, own_gates=[],
                   status=STATUS_REJECTED,
                   reason=f"closed by recorded operator decision ({Path(closure['path']).name})"
                          + (f": {first}" if first else ""),
                   recommendation="Closed on record. No further action; the line is not re-scored.",
                   criteria_file=criteria)


def _score_futures_tracker(line: str, criteria: str, inputs: dict[str, Any], as_of: str,
                           default_launch: str, extra_note: str = "") -> dict[str, Any]:
    closure = _recorded_closure(inputs)
    if closure:
        return _closed_record(line, criteria, inputs, as_of, closure)
    latest = inputs.get("latest")
    src = inputs.get("source_files") or []
    if not latest:
        st, rs = decide(False, SIGN_NONE, [], no_data_reason="latest.json missing or unreadable")
        return _record(line=line, source_files=src, launched=None, as_of=as_of, days_elapsed=None,
                       sign=SIGN_NONE, own_gates=[], status=st, reason=rs, criteria_file=criteria)
    ts = latest.get("tracker_state") or {}
    si = latest.get("since_inception") or {}
    g = latest.get("graduation_progress") or {}
    fresh = latest.get("data_freshness") or {}
    alerts_active = latest.get("alerts_active") or []
    tracker_status = latest.get("status") or _tracker_status_from_alerts(alerts_active)
    launched = (_parse_date(ts.get("launch_date_utc") or ts.get("launch_date"))
                or _parse_date(default_launch)).isoformat()
    days = _days_between(launched, as_of)
    stale_h = _num(fresh.get("stale_hours"))

    days_done = int(_num(g.get("trading_days_complete"), _num(ts.get("trading_days_since_launch"), 0)) or 0)
    days_req = int(_num(g.get("trading_days_required"), 60) or 60)
    n_trades = int(_num(g.get("trades_complete"), _num(si.get("n_trades_fired"), 0)) or 0)
    trades_req = int(_num(g.get("trades_required"), 40) or 40)
    n_long = int(_num(g.get("n_long"), _num(si.get("n_long"), 0)) or 0)
    n_short = int(_num(g.get("n_short"), _num(si.get("n_short"), 0)) or 0)
    ls_req = int(_num(g.get("long_short_min_each_required"), 10) or 10)
    pnl = _num(g.get("realized_pnl_usd"), _num(si.get("net_pnl_usd")))
    max_dd = _num(g.get("max_drawdown_pct"), _num(si.get("max_drawdown_pct")))
    worst_day = _num(g.get("worst_day_pct"))
    n_crit = int(_num(g.get("active_critical_alerts"),
                      sum(1 for a in alerts_active if a.get("severity") == "CRITICAL")) or 0)
    window_ok = days_done >= days_req and n_trades >= trades_req

    dd_within = _bool(g.get("max_drawdown_within_15pct"))
    if dd_within is None and max_dd is not None:
        dd_within = max_dd > -0.15
    wd_within = _bool(g.get("worst_day_within_5pct"))
    if wd_within is None and worst_day is not None:
        wd_within = worst_day > -0.05

    gates = [
        _cmp_gate("c1_trading_days", f">= {days_req}", float(days_done), days_done >= days_req,
                  pending=True),
        _cmp_gate("c2_fired_trades", f">= {trades_req}", float(n_trades), n_trades >= trades_req,
                  pending=True),
        _cmp_gate("c3_realized_pnl_positive", "> 0 after locked costs", _round(pnl, 2),
                  None if pnl is None else pnl > 0, pending=not window_ok),
        _cmp_gate("c4_max_drawdown_within_15pct", "> -15% for the entire window", _round(max_dd, 6),
                  dd_within),
        _cmp_gate("c5_worst_day_within_5pct", "> -5% of initial capital", _round(worst_day, 6),
                  wd_within),
        _cmp_gate("c6_long_and_short_min_each", f">= {ls_req} long AND >= {ls_req} short",
                  f"L{n_long}/S{n_short}", n_long >= ls_req and n_short >= ls_req,
                  pending=not window_ok),
        _cmp_gate("c7_no_unresolved_critical_alerts", "== 0", float(n_crit), n_crit == 0),
        gate("c8_explicit_human_go_live_sign_off", "written go-live note", None, GATE_MANUAL, True,
             "outside any automated read"),
    ]
    sign = sign_of(pnl)
    window = {"kind": "trading_days_AND_fired_trades",
              "end_or_min_n": {"trading_days": days_req, "fired_trades": trades_req},
              "satisfied": bool(window_ok)}
    wdesc = f"{days_done}/{days_req} days, {n_trades}/{trades_req} trades"
    blocked = _blocked_reason(tracker_status, stale_h, alerts_active)
    status, reason = decide(window["satisfied"], sign, gates, blocked_reason=blocked, window_desc=wdesc)
    if extra_note and status == STATUS_SHADOW:
        reason = f"{reason}; {extra_note}"
    metrics = {
        "tracker_status": tracker_status,
        "strategy_label": latest.get("strategy_label"),
        "report_date": (_parse_date(latest.get("report_date_utc")) or date.min).isoformat(),
        "report_age_days": _days_between(latest.get("report_date_utc"), as_of),
        "instrument": ts.get("instrument"),
        "initial_capital_usd": _num(ts.get("initial_capital_usd")),
        "paper_equity_usd": _round(ts.get("paper_equity_usd"), 2),
        "net_pnl_usd": _round(pnl, 2),
        "n_trades_fired": n_trades, "n_long": n_long, "n_short": n_short,
        "max_drawdown_pct": _round(max_dd, 6),
        "worst_day_pct": _round(worst_day, 6),
        "total_costs_usd": _round(si.get("total_costs_usd"), 2),
        "spec_hash_match": ts.get("launch_spec_hash") == ts.get("current_spec_hash"),
        "stale_hours": _round(stale_h, 1),
        "active_alert_codes": sorted(str(a.get("code")) for a in alerts_active),
    }
    if "win_rate" in si:
        metrics["win_rate"] = _round(si.get("win_rate"), 3)
    if "avg_r" in si:
        metrics["avg_r"] = _round(si.get("avg_r"), 3)
    if "n_skipped_size_zero" in si:
        metrics["n_skipped_size_zero"] = si.get("n_skipped_size_zero")
    plan_quote = ("own plan: 'If any mandatory criterion is unmet, paper tracking either continues "
                  "or is restarted -- live capital is NOT considered.'")
    rec_text = _recommendation_text(line, status, reason, plan_quote)
    return _record(line=line, source_files=src, launched=launched, as_of=as_of, days_elapsed=days,
                   window=window, sample={"n_trades": n_trades, "n_days": days_done}, sign=sign,
                   headline_metrics=metrics, own_gates=gates, status=status, reason=reason,
                   recommendation=rec_text, criteria_file=criteria)


def score_nq_orb(inputs: dict[str, Any], as_of: str) -> dict[str, Any]:
    """inputs: {latest: dict|None, source_files: list[str]}"""
    return _score_futures_tracker(LINE_NQ_ORB, NQ_CRITERIA, inputs, as_of, "2026-05-13")


def score_gc_ict(inputs: dict[str, Any], as_of: str) -> dict[str, Any]:
    """inputs: {latest: dict|None, source_files: list[str]}"""
    return _score_futures_tracker(
        LINE_GC_ICT, GC_CRITERIA, inputs, as_of, "2026-06-14",
        extra_note="thin line: own rules doc expects ~2 years to reach 40 fired trades")


# ── 4. frozen stack paper bot (forward rows only) ────────────────────────────

FS_CRITERIA = ("obsidian-trade-logger/reports/final_frozen_architecture.md (section 8 alert table, section 9 "
               "checklist '60-90 day clean paper run') + analytics/final_stack_operational_validation.py "
               "(BURN_IN_DAYS=30, ALERT_DD_ENVELOPE_BREACH_PCT=-10, ALERT_D4_REPRODUCIBILITY_PCT=90)")
FS_EXECUTED_ENGINES = ("baseline_breakout", "v2_bb_snapback")


def score_frozen_stack(inputs: dict[str, Any], as_of: str) -> dict[str, Any]:
    """inputs: {state: dict|None, trades_rows: list[dict]|None, validation: dict|None,
                forward_split: str, source_files: list[str]}"""
    state = inputs.get("state")
    rows = inputs.get("trades_rows")
    src = inputs.get("source_files") or []
    split = str(inputs.get("forward_split") or FROZEN_STACK_FORWARD_SPLIT)
    if state is None and rows is None:
        st, rs = decide(False, SIGN_NONE, [], no_data_reason="final_stack_paper_state.json and final_stack_paper_trades.csv missing or unreadable")
        return _record(line=LINE_FROZEN_STACK, source_files=src, launched=split, as_of=as_of,
                       days_elapsed=_days_between(split, as_of), sign=SIGN_NONE, own_gates=[],
                       status=st, reason=rs, criteria_file=FS_CRITERIA)
    rows = rows or []
    fwd = [r for r in rows if str(r.get("entry_time", ""))[:10] > split]
    back = [r for r in rows if str(r.get("entry_time", ""))[:10] <= split]
    fwd_exec = [r for r in fwd if r.get("engine") in FS_EXECUTED_ENGINES]
    fwd_skipped = [r for r in fwd if r.get("engine") == "skipped_by_d4"]
    sum_r = sum(_num(r.get("net_r"), 0.0) or 0.0 for r in fwd_exec)
    n_fwd = len(fwd_exec)
    # Out-of-sample span (evidence) vs clean-run days (the line's own gate clock).
    oos_span_days = _days_between(split, as_of) or 0
    days = _days_between(str(inputs.get("operation_start") or FROZEN_STACK_OPERATION_START),
                         as_of) or 0

    def _engine_summary(subset: list[dict[str, str]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for eng in sorted({str(r.get("engine")) for r in subset}):
            sub = [r for r in subset if r.get("engine") == eng]
            out[eng] = {"n": len(sub),
                        "sum_net_r": round(sum(_num(r.get("net_r"), 0.0) or 0.0 for r in sub), 4)}
        return out

    validation = inputs.get("validation") or {}
    head = validation.get("headline") or {}
    d4_pct = _num(head.get("d4_agreement_pct"))
    state_status = (state or {}).get("status")
    load_errors = (state or {}).get("load_errors") or {}

    window_ok = n_fwd > 0 and days >= FROZEN_STACK_CLEAN_RUN_DAYS_CONSERVATIVE
    gates = [
        gate("f1_clean_paper_run_days", f"{FROZEN_STACK_CLEAN_RUN_DAYS} days (section 9 states a range; "
             f"{FROZEN_STACK_CLEAN_RUN_DAYS_CONSERVATIVE} used as the conservative read)",
             float(days), GATE_PASS if window_ok else GATE_PENDING, True,
             f"days of clean forward RUNNING since {FROZEN_STACK_OPERATION_START}; the "
             f"{oos_span_days}-day span back to the {split} data ceiling is out-of-sample "
             "evidence, not run time; burn-in 30 days suppresses alerts before that"),
        gate("f2_paper_equity_dd_within_envelope", f"> {FROZEN_STACK_DD_ENVELOPE_PCT}%", None,
             GATE_NOT_EVALUABLE, True,
             "trades CSV carries net_r only; equity-% drawdown comes from the operational validator, "
             "which reads full history (backfill included), not forward-only"),
        _cmp_gate("f3_d4_reproducibility", f">= {FROZEN_STACK_D4_REPRO_MIN_PCT}%", d4_pct,
                  None if d4_pct is None else d4_pct >= FROZEN_STACK_D4_REPRO_MIN_PCT,
                  note="validator read over full history (not forward-only); shown as the line's own gate value"),
        gate("f4_rolling_90d_avg_r_non_negative", ">= 0 with n >= 5 (warning-level in own table)",
             _round(sum_r / n_fwd, 4) if n_fwd else None,
             (GATE_PASS if sum_r / n_fwd >= 0 else GATE_FAIL) if n_fwd >= 5 else GATE_PENDING,
             False, "forward executed rows only"),
    ]
    sign = sign_of(sum_r) if n_fwd else SIGN_NONE
    window = {"kind": "forward_clean_paper_run_days",
              "end_or_min_n": f"{FROZEN_STACK_CLEAN_RUN_DAYS} days (conservative {FROZEN_STACK_CLEAN_RUN_DAYS_CONSERVATIVE}) from {split}",
              "satisfied": bool(window_ok)}
    blocked = ""
    if state is not None and str(state_status).upper() not in ("OK", ""):
        blocked = f"paper bot state status {state_status!r}"
    elif load_errors:
        blocked = f"paper bot state reports load_errors for {sorted(load_errors)}"
    wdesc = (f"{n_fwd} out-of-sample executed rows after the {split} data ceiling "
             f"({oos_span_days}-day span), {days} days of clean forward running since "
             f"{FROZEN_STACK_OPERATION_START}")
    status, reason = decide(window["satisfied"], sign, gates, blocked_reason=blocked, window_desc=wdesc)
    if status == STATUS_SHADOW and n_fwd == 0:
        reason = (f"0 forward rows with entry_time > {split} (forward window not started; "
                  f"{len(back)} backfill rows excluded from scoring)")
    metrics = {
        "forward_split": split,
        "state_status": state_status,
        "state_generated_at": (state or {}).get("generated_at"),
        "state_age_days": _days_between((state or {}).get("generated_at"), as_of),
        "appended_rows_last_run": (state or {}).get("appended_rows"),
        "candidate_rows_last_run": (state or {}).get("candidate_rows"),
        "forward_n_executed": n_fwd,
        "forward_n_skipped_by_d4": len(fwd_skipped),
        "forward_sum_net_r": round(sum_r, 4),
        "forward_by_engine": _engine_summary(fwd),
        "backfill_not_scored": {
            "n_rows": len(back),
            "last_entry_time": max((str(r.get("entry_time", "")) for r in back), default=None),
            "by_engine": _engine_summary(back),
        },
        "validator_global_verdict": head.get("global_verdict"),
        "validator_d4_agreement_pct": d4_pct,
        "stack_label": ((state or {}).get("frozen_parameters") or {}).get("FROZEN_STACK_LABEL"),
    }
    rec_text = _recommendation_text(LINE_FROZEN_STACK, status, reason,
                                    "own doc section 9: forward paper evidence accrues; nothing is tuned")
    return _record(line=LINE_FROZEN_STACK, source_files=src, launched=split, as_of=as_of,
                   days_elapsed=days, window=window,
                   sample={"n_trades": n_fwd, "n_days": days, "n_backfill_rows_excluded": len(back)},
                   sign=sign, headline_metrics=metrics, own_gates=gates, status=status,
                   reason=reason, recommendation=rec_text, criteria_file=FS_CRITERIA)


# ── 5. s21 weekly RS forward paper harness ───────────────────────────────────

S21_CRITERIA = ("paper_trading/weekly_rs_s21_forward_paper_harness/manifest.py (gate_thresholds) + "
                "OPERATIONS_CHECKLIST.md section 8 (12-week >= 15 closed, 24-week >= 35 closed) + "
                "cycle_runner.evaluate_gates")


def _s21_weeks(state: dict[str, Any], R: int) -> float:
    if state.get("first_asof_index") is None or state.get("last_asof_index") is None:
        return 0.0
    return (float(state["last_asof_index"]) - float(state["first_asof_index"])) / float(R) + 1.0


def score_s21(inputs: dict[str, Any], as_of: str) -> dict[str, Any]:
    """inputs: {state: dict|None, gate_eval: dict|None (cycle_runner.evaluate_gates output),
                thresholds: dict (manifest gate_thresholds), rebalance_days: int,
                start_cash: float, manifest_status: dict, state_path: str, source_files: list[str]}"""
    state = inputs.get("state")
    src = inputs.get("source_files") or []
    T = inputs.get("thresholds") or {}
    min12 = int(_num(T.get("gate_12wk_min_closed_trades"), 15) or 15)
    min24 = int(_num(T.get("gate_24wk_min_closed_trades"), 35) or 35)
    window = {"kind": "weeks_AND_closed_trades",
              "end_or_min_n": {"12wk": {"weeks": 12, "min_closed_trades": min12},
                               "24wk": {"weeks": 24, "min_closed_trades": min24}},
              "satisfied": False}
    if not state:
        rs = (f"no harness_state.json under runs/cycles_v2/ ({inputs.get('state_path') or 'path unknown'}); "
              f"{S21_LEGACY_NOTE}; manifest paper_state="
              f"{(inputs.get('manifest_status') or {}).get('paper_state')}")
        st, rs = decide(False, SIGN_NONE, [], no_data_reason=rs)
        return _record(line=LINE_S21, source_files=src, launched=None, as_of=as_of, days_elapsed=None,
                       window=window, sample={"n_trades": 0}, sign=SIGN_NONE, own_gates=[], status=st,
                       reason=rs, criteria_file=S21_CRITERIA,
                       headline_metrics={"manifest_status": inputs.get("manifest_status") or {}})
    R = int(_num(inputs.get("rebalance_days"), 5) or 5)
    start_cash = _num(inputs.get("start_cash"), 100_000.0)
    closed = int(_num(state.get("closed_trades_total"), 0) or 0)
    weeks = _s21_weeks(state, R)
    ge = inputs.get("gate_eval") or {}
    checks = ge.get("checks") or {}
    last = (state.get("equity_path") or [{}])[-1]
    cost_drag = _num(checks.get("annualized_cost_drag"), _num(last.get("annualized_cost_drag")))
    max_dd = _num(checks.get("max_drawdown"), _num((state.get("drawdown") or {}).get("max_dd")))
    halted = bool(checks.get("halted", state.get("halted", False)))
    drift = bool(checks.get("mechanic_drift", False))
    equity_after = _num(state.get("last_equity_after"))
    pnl = None if equity_after is None or start_cash is None else equity_after - start_cash
    launched = state.get("first_asof_date") or state.get("first_cycle_utc") or state.get("created_utc")
    launched = (_parse_date(launched) or date.min).isoformat() if launched else None

    def _milestone(name: str, horizon: int, min_trades: int) -> dict[str, Any]:
        g = (ge.get("gates") or {}).get(name)
        if g and g.get("status") in ("PASS", "FAIL", "NOT_YET_EVALUABLE"):
            status = {"PASS": GATE_PASS, "FAIL": GATE_FAIL, "NOT_YET_EVALUABLE": GATE_PENDING}[g["status"]]
            return gate(f"m_{name}_milestone", f">= {horizon} weeks AND >= {min_trades} closed trades",
                        f"{weeks:.1f} wk / {closed} closed", status, True, str(g.get("reason", "")))
        reached = weeks >= horizon and closed >= min_trades
        if not reached:
            return gate(f"m_{name}_milestone", f">= {horizon} weeks AND >= {min_trades} closed trades",
                        f"{weeks:.1f} wk / {closed} closed", GATE_PENDING, True, "not yet evaluable (own logic replicated)")
        fails = []
        if halted:
            fails.append("KILLSWITCH_HALTED")
        if cost_drag is not None and cost_drag > _num(T.get("annualized_cost_drag_max"), 0.05):
            fails.append("COST_DRAG_GT_MAX")
        if max_dd is not None and max_dd >= _num(T.get("drawdown_kill"), 0.30):
            fails.append("MAX_DRAWDOWN_GE_KILL")
        if drift:
            fails.append("MECHANIC_DRIFT")
        return gate(f"m_{name}_milestone", f">= {horizon} weeks AND >= {min_trades} closed trades",
                    f"{weeks:.1f} wk / {closed} closed", GATE_FAIL if fails else GATE_PASS, True,
                    ",".join(fails) or "sample and horizon reached; assessments hold (replicated)")

    m12 = _milestone("12wk", 12, min12)
    m24 = _milestone("24wk", 24, min24)
    gates = [
        m12, m24,
        _cmp_gate("k_not_halted", "halted == False", 0.0 if not halted else 1.0, not halted),
        _cmp_gate("k_annualized_cost_drag", f"<= {_num(T.get('annualized_cost_drag_max'), 0.05)}",
                  _round(cost_drag, 5), None if cost_drag is None else cost_drag <= _num(T.get("annualized_cost_drag_max"), 0.05)),
        _cmp_gate("k_max_drawdown_below_kill", f"< {_num(T.get('drawdown_kill'), 0.30)}",
                  _round(max_dd, 5), None if max_dd is None else max_dd < _num(T.get("drawdown_kill"), 0.30)),
        _cmp_gate("k_no_mechanic_drift", "drift == False", 0.0 if not drift else 1.0, not drift),
    ]
    window["satisfied"] = m12["status"] in (GATE_PASS, GATE_FAIL)
    sign = sign_of(pnl)
    blocked = "harness kill-switch halted" if halted else ""
    wdesc = f"{weeks:.1f}/12 weeks, {closed}/{min12} closed trades (12wk milestone)"
    status, reason = decide(window["satisfied"], sign, gates, blocked_reason=blocked, window_desc=wdesc)
    metrics = {
        "closed_trades_total": closed, "weeks_elapsed": round(weeks, 2),
        "cycles_completed": state.get("cycles_completed"),
        "last_equity_after": _round(equity_after, 2), "start_cash_usd": start_cash,
        "net_pnl_usd": _round(pnl, 2), "annualized_cost_drag": _round(cost_drag, 5),
        "max_drawdown": _round(max_dd, 5), "halted": halted, "mechanic_drift": drift,
        "gate_eval_source": "cycle_runner.evaluate_gates" if ge else "replicated from manifest thresholds",
        "manifest_status": inputs.get("manifest_status") or {},
        "disclosure": ge.get("disclosure"),
    }
    rec_text = _recommendation_text(LINE_S21, status, reason,
                                    "own checklist section 8: a 12/24-week read is one more diagnostic data point only")
    return _record(line=LINE_S21, source_files=src, launched=launched, as_of=as_of,
                   days_elapsed=_days_between(launched, as_of) if launched else None, window=window,
                   sample={"n_trades": closed, "n_weeks": round(weeks, 2)}, sign=sign,
                   headline_metrics=metrics, own_gates=gates, status=status, reason=reason,
                   recommendation=rec_text, criteria_file=S21_CRITERIA)


# ── recommendation text (plain, observation-only) ───────────────────────────

def _recommendation_text(line: str, status: str, reason: str, own_doc_quote: str) -> str:
    if status == STATUS_CONFIRMED:
        body = (f"The pre-registered window for {line} resolved with sign POSITIVE and its own gates held. "
                "Record the window read in the trading decision record. This is a paper-window read, not a "
                "live decision: the line's remaining human sign-off gates stay open and live stays blocked.")
    elif status == STATUS_REJECTED:
        body = (f"The pre-registered window for {line} resolved without meeting its own criteria ({reason}). "
                "Record the window read as resolved-negative in the trading decision record; the operator "
                "chooses between continue-tracking (with this read logged) or restart with a new fixed launch "
                "date. No mid-window strategy edit, no re-tuning, no rescue.")
    elif status == STATUS_BLOCKED:
        body = (f"{line} cannot be read today ({reason}). Fix the data / tracker condition first; the window "
                "clock is the tracker's own, nothing is reset here.")
    elif status == STATUS_NO_DATA:
        body = f"{line} has no scoreable evidence yet ({reason}). Nothing to act on."
    else:
        body = f"{line} stays in SHADOW ({reason}). Keep tracking; nothing to act on."
    return f"{body} {own_doc_quote} {OBS_ONLY}"


# ── loaders (read-only) ─────────────────────────────────────────────────────

def load_funding_carry_inputs(ext_root: Path) -> dict[str, Any]:
    d = ext_root / "reports" / "paper_funding_carry"
    latest_p, alerts_p = d / "latest.json", d / "alerts.csv"
    p8 = ext_root / "reports" / "funding_carry_phase8_basis_aware.md"
    latest = _read_json(latest_p) if latest_p.exists() else None
    return {"latest": latest,
            "alerts_rows": _read_csv(alerts_p) if alerts_p.exists() else None,
            "phase8_report_present": p8.exists(),
            "source_files": [str(p) for p in (latest_p, alerts_p) if p.exists()]}


def load_nq_orb_inputs(ext_root: Path) -> dict[str, Any]:
    d = ext_root / "reports" / "nq_paper_orb"
    latest_p = d / "latest.json"
    srcs = [p for p in (latest_p, d / "latest.md", d / "trades.csv", d / "equity_curve.csv") if p.exists()]
    return {"latest": _read_json(latest_p) if latest_p.exists() else None,
            "source_files": [str(p) for p in srcs],
            "closure_files": _closure_files(d)}


def load_gc_ict_inputs(ext_root: Path) -> dict[str, Any]:
    d = ext_root / "reports" / "gc_paper_ict"
    latest_p = d / "latest.json"
    srcs = [p for p in (latest_p, d / "latest.md", d / "alerts.csv") if p.exists()]
    return {"latest": _read_json(latest_p) if latest_p.exists() else None,
            "source_files": [str(p) for p in srcs],
            "closure_files": _closure_files(d)}


def _closure_files(d: Path) -> list[str]:
    """Operator closure decisions recorded in a tracker's report folder."""
    out: list[str] = []
    for pattern in CLOSURE_DECISION_GLOBS:
        try:
            out.extend(sorted(str(p) for p in d.glob(pattern)))
        except Exception:
            pass
    return out


def load_frozen_stack_inputs(ext_root: Path) -> dict[str, Any]:
    state_p = ext_root / "data" / "final_stack_paper_state.json"
    trades_p = ext_root / "data" / "final_stack_paper_trades.csv"
    val_p = ext_root / "reports" / "final_stack_operational_validation.json"
    return {"state": _read_json(state_p) if state_p.exists() else None,
            "trades_rows": _read_csv(trades_p) if trades_p.exists() else None,
            "validation": _read_json(val_p) if val_p.exists() else None,
            "forward_split": FROZEN_STACK_FORWARD_SPLIT,
            "source_files": [str(p) for p in (state_p, trades_p, val_p) if p.exists()]}


def load_s21_inputs(sparta_root: Path) -> dict[str, Any]:
    state_p = sparta_root.joinpath(*S21_REL_STATE)
    manifest_p = state_p.parents[2] / "manifest.py"
    thresholds: dict[str, Any] = {}
    manifest_status: dict[str, Any] = {}
    R, start_cash = 5, 100_000.0
    try:
        if str(sparta_root) not in sys.path:
            sys.path.insert(0, str(sparta_root))
        from paper_trading.weekly_rs_s21_forward_paper_harness.manifest import MANIFEST  # noqa: E402
        thresholds = dict(MANIFEST.get("gate_thresholds") or {})
        manifest_status = dict(MANIFEST.get("status") or {})
        R = int(MANIFEST["locked_mechanic"]["rebalance_cadence_R_days"])
        start_cash = float(MANIFEST["locked_mechanic"]["start_cash_usd"])
    except Exception as exc:  # noqa: BLE001 -- manifest unreadable is reported, never fatal
        manifest_status = {"manifest_import_error": f"{type(exc).__name__}: {exc}"}
    state = _read_json(state_p) if state_p.exists() else None
    gate_eval = None
    if state is not None:
        try:
            from paper_trading.weekly_rs_s21_forward_paper_harness import cycle_runner  # noqa: E402
            gate_eval = cycle_runner.evaluate_gates(state)
        except Exception as exc:  # noqa: BLE001
            manifest_status["evaluate_gates_error"] = f"{type(exc).__name__}: {exc}"
    return {"state": state, "gate_eval": gate_eval, "thresholds": thresholds, "rebalance_days": R,
            "start_cash": start_cash, "manifest_status": manifest_status, "state_path": str(state_p),
            "source_files": [str(p) for p in (state_p, manifest_p) if p.exists()]}


def score_all(as_of: str, ext_root: Path | None = None, sparta_root: Path | None = None) -> list[dict[str, Any]]:
    ext = Path(ext_root) if ext_root is not None else external_root()
    sp = Path(sparta_root) if sparta_root is not None else _REPO_ROOT
    return [
        score_funding_carry(load_funding_carry_inputs(ext), as_of),
        score_nq_orb(load_nq_orb_inputs(ext), as_of),
        score_gc_ict(load_gc_ict_inputs(ext), as_of),
        score_frozen_stack(load_frozen_stack_inputs(ext), as_of),
        score_s21(load_s21_inputs(sp), as_of),
    ]


# ── rendering ───────────────────────────────────────────────────────────────

def _fmt(v: Any) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:,.4f}".rstrip("0").rstrip(".") if abs(v) < 1e6 else f"{v:,.0f}"
    if isinstance(v, (dict, list)):
        return json.dumps(v, sort_keys=True)
    return str(v)


def render_markdown(records: list[dict[str, Any]], as_of: str) -> str:
    L = [f"# Paper systems scorecard -- {as_of}", "", f"**{BANNER}**", "",
         "Each line is scored against ITS OWN pre-registered window and gates (cited per line). "
         "Status vocabulary: SHADOW / CONFIRMED / REJECTED / BLOCKED / NO_DATA. A CONFIRMED or REJECTED "
         "read closes a paper window and nothing else. " + OBS_ONLY, "",
         "| line | status | sign | window | sample | reason |", "|---|---|---|---|---|---|"]
    for r in records:
        w = r["window"]
        wtxt = f"{w.get('kind')} {'satisfied' if w.get('satisfied') else 'open'}"
        L.append(f"| {r['line']} | **{r['status']}** | {r['sign']} | {wtxt} | {_fmt(r['sample'])} | {r['reason']} |")
    for r in records:
        L += ["", f"## {r['line']} -- {r['status']}", "",
              f"- Criteria file: `{r['criteria_file']}`",
              f"- Launched: {r['launched'] or '-'} · as_of {r['as_of']} · days elapsed {_fmt(r['days_elapsed'])}",
              f"- Window: {_fmt(r['window'])}",
              f"- Sign: {r['sign']} · sample {_fmt(r['sample'])}",
              f"- Reason: {r['reason']}",
              f"- Recommendation: {r['recommendation']}", ""]
        if r["own_gates"]:
            L += ["| own gate | threshold | value | status | hard | note |", "|---|---|---|---|---|---|"]
            for g in r["own_gates"]:
                L.append(f"| {g['name']} | {_fmt(g['threshold'])} | {_fmt(g['value'])} | {g['status']} | "
                         f"{'yes' if g['hard'] else 'no'} | {g.get('note', '')} |")
        else:
            L.append("(no own gates evaluated)")
        L += ["", "Headline metrics:", "", "```json", json.dumps(r["headline_metrics"], indent=1, sort_keys=True), "```",
              "", "Source files (read-only):"]
        L += [f"- `{p}`" for p in r["source_files"]] or ["- (none found)"]
    L += ["", "---", BANNER, ""]
    return "\n".join(L)


def render_closure_recommendation(rec: dict[str, Any]) -> str:
    w = rec["window"]
    L = [f"# Closure recommendation -- {rec['line']} -- {rec['as_of']}", "", f"**{BANNER}**", "",
         f"Status: **{rec['status']}**", f"Sign: {rec['sign']}",
         f"Window: {_fmt(w)}", f"Sample: {_fmt(rec['sample'])}",
         f"Launched: {rec['launched'] or '-'} · days elapsed {_fmt(rec['days_elapsed'])}",
         f"Criteria file: `{rec['criteria_file']}`", "",
         "## Why the window resolved", "", rec["reason"], "",
         "## Own gates at resolution", "",
         "| own gate | threshold | value | status | hard |", "|---|---|---|---|---|"]
    for g in rec["own_gates"]:
        L.append(f"| {g['name']} | {_fmt(g['threshold'])} | {_fmt(g['value'])} | {g['status']} | {'yes' if g['hard'] else 'no'} |")
    L += ["", "## Recommendation (observation only)", "", rec["recommendation"], "",
          "## Headline metrics", "", "```json", json.dumps(rec["headline_metrics"], indent=1, sort_keys=True), "```",
          "", "Source files (read-only):"] + [f"- `{p}`" for p in rec["source_files"]]
    L += ["", "---", "This file is written once when the line's own window first resolves and is never rewritten. "
          "It changes no rule, sends no order, and grants nothing.", BANNER, ""]
    return "\n".join(L)


# ── persistence (only under reports/trade_learning) ─────────────────────────

def _prior_resolved(history_path: Path, line: str, status: str) -> bool:
    if not history_path.exists():
        return False
    try:
        for raw in history_path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            row = json.loads(raw)
            if (row.get("lines") or {}).get(line, {}).get("status") == status:
                return True
    except (OSError, ValueError):
        return False
    return False


def write_closure_recommendations(records: list[dict[str, Any]], report_dir: Path,
                                  history_path: Path | None = None) -> list[Path]:
    """Write closure_recommendation_<line>_<as_of>.md the FIRST time a line is CONFIRMED or REJECTED.
    Idempotent: never rewrites an existing file; never writes again for a (line, status) pair
    that the history already records."""
    written: list[Path] = []
    hist = history_path if history_path is not None else report_dir / HISTORY_JSONL
    for rec in records:
        if rec["status"] not in (STATUS_CONFIRMED, STATUS_REJECTED):
            continue
        path = report_dir / f"closure_recommendation_{rec['line']}_{rec['as_of']}.md"
        if path.exists() or _prior_resolved(hist, rec["line"], rec["status"]):
            continue
        text = render_closure_recommendation(rec)
        report_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written


def history_line(records: list[dict[str, Any]], as_of: str, generated_at: str = "") -> dict[str, Any]:
    line = {"as_of": as_of,
            "lines": {r["line"]: {"status": r["status"], "sign": r["sign"], "reason": r["reason"],
                                  "window_satisfied": bool(r["window"].get("satisfied"))}
                      for r in records}}
    if generated_at:
        line["generated_at"] = generated_at
    return line


def _register_manual_entry() -> None:
    """One-shot /guide registration. Never allowed to break the scorecard."""
    try:
        import database as db  # local sparta.db; unrelated to trades.db
        db.upsert_manual_entry(
            "paper_system_scorers",
            module_name="Paper System Scorers",
            category="Trading",
            status="live",
            short_description=(
                "Read-only scorers for the five paper lines (funding carry, NQ ORB, GC ICT, frozen "
                "stack forward, s21 weekly RS); each mapped to its OWN pre-registered window/gates."
            ),
            how_it_works=(
                "Reads each tracker's latest report/state file read-only, cites the line's own "
                "criteria file, evaluates its own gates, and maps the result to SHADOW / CONFIRMED / "
                "REJECTED / BLOCKED / NO_DATA. When a window first resolves it writes a one-time "
                "closure recommendation (observation only)."
            ),
            when_to_use=(
                "Daily after the paper trackers run. Observation only: no broker, no orders, no "
                "rule changes, no live-readiness claim."
            ),
            user_action=(
                "Run `.venv\\Scripts\\python tools\\paper_system_scorers.py`; read "
                "reports/trade_learning/paper_systems_scorecard.md (history in paper_systems_history.jsonl)."
            ),
            sort_order=97,
        )
    except Exception as exc:  # noqa: BLE001 -- registration must never break the report
        print(f"[manual-entry] skipped: {type(exc).__name__}: {exc}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Read-only paper-system scorers (Phase 2).")
    p.add_argument("--as-of", default=None, help="YYYY-MM-DD (default: local operator date)")
    p.add_argument("--report-dir", default=str(REPORT_DIR))
    args = p.parse_args(argv)
    as_of = args.as_of or datetime.now().strftime("%Y-%m-%d")
    report_dir = Path(args.report_dir)

    records = score_all(as_of)
    md = render_markdown(records, as_of)
    bad = forbidden_words_found(md)
    if bad:
        print(f"WARNING forbidden words in render: {bad}")

    report_dir.mkdir(parents=True, exist_ok=True)
    payload = {"banner": BANNER, "as_of": as_of, "generated_at": datetime.now().isoformat(timespec="seconds"),
               "records": records}
    (report_dir / SCORECARD_JSON).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (report_dir / SCORECARD_MD).write_text(md, encoding="utf-8")
    hist = report_dir / HISTORY_JSONL
    closures = write_closure_recommendations(records, report_dir, hist)  # before the history append
    with hist.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(history_line(records, as_of, payload["generated_at"]), sort_keys=True) + "\n")

    _register_manual_entry()
    print(BANNER)
    print(f"wrote {report_dir / SCORECARD_JSON}, {SCORECARD_MD}, {HISTORY_JSONL} (+1 line)")
    for c in closures:
        print(f"closure recommendation written: {c}")
    for r in records:
        print(f"  {r['line']:28s} {r['status']:10s} sign={r['sign']:8s} {r['reason']}")
    return 0


__all__ = [
    "score_funding_carry", "score_nq_orb", "score_gc_ict", "score_frozen_stack", "score_s21",
    "score_all", "decide", "sign_of", "render_markdown", "render_closure_recommendation",
    "write_closure_recommendations", "history_line", "forbidden_words_found", "BANNER",
    "FORBIDDEN_WORDS", "STATUSES", "RECORD_KEYS", "LINES",
]

if __name__ == "__main__":
    sys.exit(main())
