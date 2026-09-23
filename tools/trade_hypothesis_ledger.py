"""Forward-tested hypothesis ledger over the operator's PAPER trade journal.

Phase 1 of the self-improving trading learning loop. Posture (non-negotiable):
  * Research / observation only. No broker, no orders, no execution path.
  * The journal (trades.db) is opened read-only through the learning report's
    ``load_journal_ro`` (sqlite URI mode=ro). Nothing external is touched.
  * Every rule SUGGESTION emitted by ``tools/trade_journal_learning_report.py``
    becomes a HYPOTHESIS here. Its in-sample evidence is frozen at
    registration and it is then scored ONLY on trades that close strictly
    after ``registered_as_of`` — out-of-sample by construction.
  * Promotion / rejection uses pre-registered thresholds. A CONFIRMED status
    is a recommendation for the operator to consider in the paper bot by
    hand. Nothing is applied automatically, anywhere.

Files written (all inside SPARTA_BRAIN):
  data/trade_hypothesis_ledger.json
  reports/trade_learning/hypothesis_ledger.md
  reports/trade_learning/hypothesis_history.jsonl   (one line per run)

Usage:
    .venv\\Scripts\\python tools\\trade_hypothesis_ledger.py

Standard library only. Deterministic for fixed input (bootstrap seed 42).
"""
from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.trade_journal_adapter import (  # noqa: E402  (reuse, never modify)
    _REL_TRADES_DB,
    _coerce_float,
    _parse_dt,
    external_root,
)
from tools.trade_journal_learning_report import (  # noqa: E402  (reuse, never modify)
    BANNER,
    _alignment,
    _days_between,
    _pnl,
    _signal_key,
    _weekday,
    build_learning_report,
    load_journal_ro,
)

LEDGER_PATH = _REPO_ROOT / "data" / "trade_hypothesis_ledger.json"
REPORT_DIR = _REPO_ROOT / "reports" / "trade_learning"
MD_NAME = "hypothesis_ledger.md"
HISTORY_NAME = "hypothesis_history.jsonl"

SCHEMA_VERSION = 1
STATUSES = ("PROPOSED", "SHADOW", "CONFIRMED", "APPLIED", "REJECTED", "RETIRED")
# APPLIED (Phase 4): the operator applied the rule in the paper bot. The counterfactual
# scoring stops (the rule now shapes the trades themselves); instead the ledger tracks the
# realized journal expectancy AFTER applied_as_of against the baseline frozen at apply time.
APPLIED_MIN_N = 20
APPLIED_REGRESSION_R = 0.2   # flag when post-apply mean R < baseline - 0.2R with n >= APPLIED_MIN_N

# Trades opened before the partial-bar fix came from a bot reading a
# still-forming candle; the operator retired that record from evidence
# (obsidian-trade-logger/reports/observation_mode/system_b_benchmark_gate.md and
# system_b_strategy_retirement_20260919.json). Kept in sync with
# EVIDENCE_VALID_FROM in trade_journal_learning_report.py.
EVIDENCE_VALID_FROM = "2026-09-15"

# An applied rule needs SOMETHING to be judged against at n >= APPLIED_MIN_N.
# When the only available baseline would be retired evidence, we refuse to
# compute one and fall back to this absolute floor instead. Pre-registered
# 2026-09-21, BEFORE the post-fix evidence existed, per
# reports/trade_learning/spec_killswitch_and_ledger_baseline_2026-09-21.md:
# rollback is recommended if mean R < 0.0 at n >= APPLIED_MIN_N. A positive
# mean does NOT declare the rule working - it only means no rollback.
ROLLBACK_ABS_MEAN_R = 0.0

# Why an applied rule has (or lacks) an admissible baseline. These are distinct:
# a legacy record froze a NUMBER from retired trades, while a new apply may
# simply not have enough post-fix trades yet. Both fall back to the absolute
# rollback rule, but only the first is a correctness problem.
BASELINE_EMPIRICAL = "EMPIRICAL_POST_FIX"
BASELINE_RETIRED = "NOT_EVALUABLE_RETIRED_EVIDENCE"
BASELINE_INSUFFICIENT = "NOT_EVALUABLE_INSUFFICIENT_POST_FIX_SAMPLE"
BASELINE_NOT_EVALUABLE = (BASELINE_RETIRED, BASELINE_INSUFFICIENT)

DEFAULT_THRESHOLDS = {
    "min_forward_signals": 20,
    "min_p_positive": 0.90,
    "max_p_positive_reject": 0.50,
}
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 42
BOOTSTRAP_MIN_N = 5

STOP_CAP_R = -1.5           # enforce_hard_stop: kill at -1.5R
PARTIAL_TRIGGER_R = 2.0     # partial_tp_or_trail_2R: take half at 2R
PARTIAL_FRACTION = 0.5

# ── "unblock" hypotheses (2026-09-23) ────────────────────────────────────────
# The kinds above are scored on trades the bot TOOK. A gate that blocks an entry
# leaves no trade to score, so the loop could never learn whether a block was
# right. The bot keeps its own hindsight ledger of blocked entries
# (reports/observation_mode/missed_opportunity_outcomes.jsonl, resolved weekly
# by scripts/resolve_ledger_outcomes.py with a 3 x ATR hypothetical stop and a
# 1R target). An "unblock__<COUNTED_REASON>" hypothesis is scored on those rows:
# delta_R = the R the blocked entry would have made, so a CONFIRMED read means
# "allowing these entries would have helped" and REJECTED means the gate was
# right. Read-only; rows are only consumed once resolved, and only when their
# signal date is strictly after registration.
UNBLOCK_PREFIX = "unblock__"
_REL_MISSED_OUTCOMES = ("reports", "observation_mode", "missed_opportunity_outcomes.jsonl")
UNBLOCK_HYP_STOP_ATR_MULT = 3.0   # mirrors resolve_ledger_outcomes.HYP_STOP_ATR_MULT
UNBLOCK_RESOLVED = ("GOOD_BLOCK", "BAD_BLOCK", "NEUTRAL_BLOCK")

# Substring check, same semantics as the learning report (so "already" also
# trips "ready": keep such words out of the render).
FORBIDDEN_WORDS = ("validated", "ready", "approved", "profitable strategy", "deploy")

POSTURE = {
    "mode": "READ_ONLY_OBSERVATION",
    "broker": "NONE",
    "orders": "NONE",
    "journal_writes": "NONE",
    "external_project_modified": False,
    "rules_applied": False,
    "confirmed_means": "recommendation for the operator; nothing applied automatically",
}


# ── small helpers ───────────────────────────────────────────────────────────

def _r(x: float | None, nd: int = 4) -> float | None:
    return None if x is None else round(float(x), nd)


def _close_day(row: dict[str, Any]) -> date | None:
    dt = _parse_dt(row.get("close_date"))
    return None if dt is None else dt.date()


def _sig_str(row: dict[str, Any]) -> str:
    return "|".join(_signal_key(row))


def new_ledger(as_of: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "banner": BANNER,
        "posture": dict(POSTURE),
        "created_as_of": as_of,
        "last_updated_as_of": as_of,
        "default_thresholds": dict(DEFAULT_THRESHOLDS),
        "hypotheses": {},
    }


def load_ledger(path: Path = LEDGER_PATH) -> dict[str, Any]:
    if not path.exists():
        return new_ledger()
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("hypotheses", {})
    data.setdefault("default_thresholds", dict(DEFAULT_THRESHOLDS))
    return data


def save_ledger(ledger: dict[str, Any], path: Path = LEDGER_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2, sort_keys=True), encoding="utf-8")


# ── suggestion id → hypothesis kind ─────────────────────────────────────────

def kind_for_id(sid: str) -> tuple[str, dict[str, Any]]:
    """Map a learning-report suggestion id to (kind, params). Unknown → 'unknown'."""
    sid = str(sid)
    if sid.startswith("block_") and "_in_" in sid:
        direction, regime = sid[len("block_"):].split("_in_", 1)
        direction, regime = direction.lower(), regime.upper()
        probe = {"regime_at_open": regime, "direction": direction}
        return "block", {"direction": direction, "regime": regime,
                         "alignment": _alignment(probe)}
    if sid.startswith("review_pause_"):
        return "block", {"strategy": sid[len("review_pause_"):]}
    if sid == "enforce_hard_stop":
        return "stop_cap", {"cap_R": STOP_CAP_R}
    if sid == "partial_tp_or_trail_2R":
        return "partial_2R", {"trigger_R": PARTIAL_TRIGGER_R, "fraction": PARTIAL_FRACTION}
    if sid.startswith("flag_"):
        wd = sid[len("flag_"):]
        if wd.startswith("weekday_"):
            wd = wd[len("weekday_"):]
        return "flag", {"weekday": wd}
    if sid.startswith("blockwhere__"):
        # generic cell block emitted by tools/trade_rule_search.py:
        # blockwhere__<field>=<value>__<field>=<value>  (fields: strategy, direction,
        # regime_at_open, exchange, weekday, hold_bucket)
        where: dict[str, str] = {}
        for part in sid[len("blockwhere__"):].split("__"):
            if "=" in part:
                k, v = part.split("=", 1)
                where[k] = v
        return ("block_where", {"where": where}) if where else ("unknown", {})
    if sid.startswith(UNBLOCK_PREFIX):
        reason = sid[len(UNBLOCK_PREFIX):].strip().upper()
        return ("unblock", {"counted_reason": reason}) if reason else ("unknown", {})
    return "unknown", {}


# ── missed-opportunity outcomes (blocked entries, resolved with hindsight) ───

def missed_outcomes_path(ext_root: Path | None = None) -> Path:
    root = Path(ext_root) if ext_root is not None else external_root()
    return root.joinpath(*_REL_MISSED_OUTCOMES)


def load_missed_outcomes(path: Path | None = None) -> list[dict[str, Any]]:
    """Read the bot's resolved blocked-entry ledger. Read-only; a missing or
    unreadable file is an empty list, never an error (the ledger still runs)."""
    p = path if path is not None else missed_outcomes_path()
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return []
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def outcome_r(row: dict[str, Any]) -> float | None:
    """Hypothetical R of a blocked entry at its classification horizon: the
    direction-adjusted close return divided by the hypothetical risk
    (UNBLOCK_HYP_STOP_ATR_MULT x ATR / entry). Mirrors the bot's own
    build_missed_opportunity_report._r_multiple so both reports agree."""
    h = row.get("classification_horizon")
    if h is None:
        return None
    dar = _coerce_float(row.get(f"dir_adjusted_return_{h}"))
    atr = _coerce_float(row.get("atr"))
    entry = _coerce_float(row.get("entry_candidate"))
    if dar is None or atr is None or entry is None or entry <= 0:
        return None
    risk_frac = UNBLOCK_HYP_STOP_ATR_MULT * atr / entry
    if risk_frac <= 0:
        return None
    return dar / risk_frac


def _outcome_day(row: dict[str, Any]) -> date | None:
    ts = str(row.get("ts_utc") or "")[:10]
    try:
        return date.fromisoformat(ts)
    except ValueError:
        return None


def _outcome_rows_for(reason: str, outcomes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [o for o in outcomes
            if str(o.get("counted_reason") or "").upper() == reason
            and o.get("classification") in UNBLOCK_RESOLVED]


def unblock_evidence(reason: str, outcomes: list[dict[str, Any]],
                     up_to: str | None = None) -> dict[str, Any]:
    """Frozen in-sample summary of a gate's resolved blocks (signal day <= up_to)."""
    rows = _outcome_rows_for(reason, outcomes)
    if up_to:
        lim = date.fromisoformat(up_to)
        rows = [o for o in rows if (_outcome_day(o) or lim) <= lim]
    rs = [r for r in (outcome_r(o) for o in rows) if r is not None]
    cls: dict[str, int] = defaultdict(int)
    for o in rows:
        cls[str(o.get("classification"))] += 1
    return {"n_resolved_blocks": len(rows), "good_blocks": cls.get("GOOD_BLOCK", 0),
            "bad_blocks": cls.get("BAD_BLOCK", 0), "neutral_blocks": cls.get("NEUTRAL_BLOCK", 0),
            "net_hyp_R": _r(sum(rs)) if rs else 0.0,
            "mean_hyp_R": _r(sum(rs) / len(rs)) if rs else None,
            "source": "/".join(_REL_MISSED_OUTCOMES)}


def register_unblock(ledger: dict[str, Any], reason: str, as_of: str,
                     outcomes: list[dict[str, Any]], note: str = "") -> str | None:
    """Register unblock__<REASON> as SHADOW with the gate's hindsight record up to
    as_of frozen as in-sample evidence. Existing ids are left untouched. Returns
    the id when newly registered, else None."""
    reason = reason.strip().upper()
    sid = f"{UNBLOCK_PREFIX}{reason}"
    hyps = ledger.setdefault("hypotheses", {})
    if not reason or sid in hyps:
        return None
    hyps[sid] = {
        "id": sid,
        "rule": (f"allow entries the paper bot currently blocks with reason {reason}; "
                 "scored on the bot's resolved blocked-entry ledger, delta_R = hypothetical "
                 "R of the blocked entry (3 x ATR stop, 1R target)"),
        "kind": "unblock",
        "params": {"counted_reason": reason},
        "registered_as_of": as_of,
        "registered_evidence": unblock_evidence(reason, outcomes, up_to=as_of),
        "registered_label": "HINDSIGHT_BLOCK_LEDGER",
        "status": "SHADOW",
        "forward": {
            "n_signals": 0, "n_rows": 0, "delta_R_sum": 0.0, "delta_R_mean": None,
            "wins": 0, "losses": 0, "bootstrap_p_positive": None, "last_eval_as_of": None,
            "trade_ids_evaluated": [], "signal_keys_evaluated": [], "samples": [],
        },
        "thresholds": dict(ledger.get("default_thresholds", DEFAULT_THRESHOLDS)),
        "history": [{"as_of": as_of, "status": "SHADOW",
                     "note": "registered by operator from the blocked-entry ledger; "
                             "hindsight record to date frozen as in-sample evidence"
                             + (f"; {note}" if note else "")}],
    }
    ledger["created_as_of"] = ledger.get("created_as_of") or as_of
    return sid


def _forward_unblock_candidates(hyp: dict[str, Any],
                                outcomes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Resolved blocked entries for this gate whose signal day is strictly after
    registration and that have not been scored yet."""
    reg = date.fromisoformat(hyp["registered_as_of"])
    done = set(hyp["forward"].get("signal_keys_evaluated", []))
    reason = str(hyp.get("params", {}).get("counted_reason") or "").upper()
    out: list[dict[str, Any]] = []
    for o in _outcome_rows_for(reason, outcomes):
        d = _outcome_day(o)
        if d is None or d <= reg:
            continue
        key = str(o.get("candidate_id") or f"{o.get('ts_utc')}|{o.get('symbol')}|{o.get('strategy_id')}")
        if key in done:
            continue
        out.append(o)
    return sorted(out, key=lambda o: (str(o.get("ts_utc")), str(o.get("symbol")), str(o.get("strategy_id"))))


# ── registration ────────────────────────────────────────────────────────────

def register_from_report(report: dict[str, Any], as_of: str, ledger: dict[str, Any]) -> list[str]:
    """Every suggestion id not yet in the ledger becomes a hypothesis (SHADOW,
    or PROPOSED when the kind is unknown). Existing ids are left untouched:
    evidence stays frozen at first registration. Never deletes. Returns the
    newly registered ids (sorted)."""
    hyps = ledger.setdefault("hypotheses", {})
    added: list[str] = []
    for s in sorted(report.get("suggestions", []), key=lambda x: str(x.get("id"))):
        sid = str(s.get("id"))
        if not sid or sid in hyps:
            continue
        kind, params = kind_for_id(sid)
        status = "PROPOSED" if kind == "unknown" else "SHADOW"
        hyps[sid] = {
            "id": sid,
            "rule": s.get("rule"),
            "kind": kind,
            "params": params,
            "registered_as_of": as_of,
            "registered_evidence": json.loads(json.dumps(s.get("evidence", {}))),
            "registered_label": s.get("label"),
            "status": status,
            "forward": {
                "n_signals": 0,
                "n_rows": 0,
                "delta_R_sum": 0.0,
                "delta_R_mean": None,
                "wins": 0,
                "losses": 0,
                "bootstrap_p_positive": None,
                "last_eval_as_of": None,
                "trade_ids_evaluated": [],
                "signal_keys_evaluated": [],
                "samples": [],
            },
            "thresholds": dict(ledger.get("default_thresholds", DEFAULT_THRESHOLDS)),
            "history": [{
                "as_of": as_of,
                "status": status,
                "note": ("registered from learning report; in-sample evidence frozen"
                         if kind != "unknown" else
                         "registered with unknown kind; not evaluated"),
            }],
        }
        added.append(sid)
    if added:
        ledger["created_as_of"] = ledger.get("created_as_of") or as_of
    return added


# ── counterfactual evaluators (pure) ────────────────────────────────────────
# Each returns delta_R = R(rule) - R(realized), or None when the rule does not
# apply to this trade. Only closed trades with a numeric pnl_r are scored.

def evaluate_block(hyp: dict[str, Any], trade: dict[str, Any]) -> float | None:
    v = _pnl(trade)
    if v is None:
        return None
    p = hyp.get("params", {})
    if "strategy" in p:
        if str(trade.get("strategy") or "") != str(p["strategy"]):
            return None
    else:
        if str(trade.get("direction") or "").lower() != str(p.get("direction", "")).lower():
            return None
        if str(trade.get("regime_at_open") or "").upper() != str(p.get("regime", "")).upper():
            return None
    return -v


def evaluate_stop_cap(hyp: dict[str, Any], trade: dict[str, Any]) -> float | None:
    v = _pnl(trade)
    if v is None:
        return None
    cap = float(hyp.get("params", {}).get("cap_R", STOP_CAP_R))
    if v >= cap:
        return None
    return cap - v


def evaluate_partial_2R(
    hyp: dict[str, Any], trade: dict[str, Any], excursion: dict[str, Any] | None
) -> float | None:
    """Approximation (documented judgment call): half taken at 2R (=1.0R on
    the full position), the other half runs with a breakeven stop and is
    approximated as 0.5*max(pnl_r, 0). rule_R = 1.0 + 0.5*max(pnl_r, 0)."""
    v = _pnl(trade)
    if v is None or not excursion:
        return None
    mfe = _coerce_float(excursion.get("max_favorable_R"))
    p = hyp.get("params", {})
    trigger = float(p.get("trigger_R", PARTIAL_TRIGGER_R))
    frac = float(p.get("fraction", PARTIAL_FRACTION))
    if mfe is None or mfe < trigger:
        return None
    rule_r = frac * trigger + (1.0 - frac) * max(v, 0.0)
    return rule_r - v


def evaluate_flag(hyp: dict[str, Any], trade: dict[str, Any]) -> float | None:
    v = _pnl(trade)
    if v is None:
        return None
    if _weekday(trade) != hyp.get("params", {}).get("weekday"):
        return None
    return -v


def trade_field(trade: dict[str, Any], field: str) -> str | None:
    """Derived/normalised trade attributes used by generic cell rules."""
    if field == "weekday":
        return _weekday(trade)
    if field == "hold_bucket":
        d = _days_between(trade.get("open_date"), trade.get("close_date"))
        if d is None:
            return None
        return "short" if d <= 5 else ("mid" if d <= 12 else "long")
    v = trade.get(field)
    if v is None:
        return None
    v = str(v)
    return v.upper() if field == "regime_at_open" else (v.lower() if field in ("direction", "exchange") else v)


def evaluate_block_where(hyp: dict[str, Any], trade: dict[str, Any]) -> float | None:
    """Block the entry when every field in params['where'] matches the trade."""
    v = _pnl(trade)
    if v is None:
        return None
    where = hyp.get("params", {}).get("where", {})
    if not where:
        return None
    for field, want in where.items():
        got = trade_field(trade, field)
        if got is None or str(got) != str(want):
            return None
    return -v


def evaluate_hypothesis(
    hyp: dict[str, Any], trade: dict[str, Any], excursion: dict[str, Any] | None = None
) -> float | None:
    kind = hyp.get("kind")
    if kind == "block":
        return evaluate_block(hyp, trade)
    if kind == "block_where":
        return evaluate_block_where(hyp, trade)
    if kind == "stop_cap":
        return evaluate_stop_cap(hyp, trade)
    if kind == "partial_2R":
        return evaluate_partial_2R(hyp, trade, excursion)
    if kind == "flag":
        return evaluate_flag(hyp, trade)
    return None


# ── Phase 4: applied-rule tracking ──────────────────────────────────────────

def _dedup_best_signals(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[tuple[str, str, str], dict[str, Any]] = {}
    for t in trades:
        v = _pnl(t)
        if v is None:
            continue
        k = _signal_key(t)
        if k not in best or v > float(_pnl(best[k])):
            best[k] = t
    return list(best.values())


def mark_applied(ledger: dict[str, Any], sid: str, as_of: str, trades: list[dict[str, Any]],
                 note: str = "") -> dict[str, Any]:
    """Operator applied hypothesis `sid` in the paper bot on `as_of`. Freezes the journal
    baseline (dedup-best mean R of everything closed on/before as_of) and switches the
    hypothesis to APPLIED. Counterfactual forward stats are kept as they were."""
    hyp = ledger["hypotheses"][sid]
    # The baseline may only be built from trades that are still admissible as
    # evidence, i.e. opened on/after the partial-bar fix. Anything earlier is
    # retired, and scoring valid forward evidence against a retired baseline
    # produces a rollback verdict that says nothing about the rule.
    cutoff = date.fromisoformat(as_of)
    before = [
        float(_pnl(t)) for t in _dedup_best_signals(trades)
        if (_close_day(t) is not None and _close_day(t) <= cutoff
            and str(t.get("open_date") or "") >= EVIDENCE_VALID_FROM)
    ]
    usable = len(before) >= APPLIED_MIN_N
    hyp["applied"] = {
        "applied_as_of": as_of,
        "note": note,
        "baseline_n": len(before),
        "baseline_mean_R": _r(sum(before) / len(before)) if usable else None,
        "baseline_status": BASELINE_EMPIRICAL if usable else BASELINE_INSUFFICIENT,
        "baseline_valid_from": EVIDENCE_VALID_FROM,
        "rollback_rule": (
            f"mean R < baseline - {APPLIED_REGRESSION_R}R at n >= {APPLIED_MIN_N}"
            if usable else
            f"mean R < {ROLLBACK_ABS_MEAN_R}R at n >= {APPLIED_MIN_N} "
            f"(absolute; no admissible baseline)"
        ),
        "n_after": 0,
        "mean_R_after": None,
        "p_after_ge_baseline": None,
        "regression_flag": False,
        "last_eval_as_of": None,
    }
    hyp["history"].append({"as_of": as_of, "status": "APPLIED",
                           "note": f"{hyp.get('status')} -> APPLIED: {note or 'applied in paper bot'}"})
    hyp["status"] = "APPLIED"
    return hyp


def _baseline_status(ap: dict[str, Any]) -> str:
    """Effective baseline status, derived for records written before this field
    existed.

    A record applied before EVIDENCE_VALID_FROM froze its baseline from trades
    that are now retired, whatever number it stored. Deriving the status here
    annotates those records WITHOUT rewriting the pre-registered values they
    carry - re-dating them and nulling the baseline is a separate, separately
    approved migration (spec step 4, still pending)."""
    stored = ap.get("baseline_status")
    if stored:
        return str(stored)
    applied_as_of = str(ap.get("applied_as_of") or "")
    if ap.get("baseline_mean_R") is not None and applied_as_of and applied_as_of < EVIDENCE_VALID_FROM:
        # A number frozen from trades that are now retired: the correctness problem.
        return BASELINE_RETIRED
    if ap.get("baseline_mean_R") is None:
        return BASELINE_INSUFFICIENT
    return BASELINE_EMPIRICAL


def _update_applied(hyp: dict[str, Any], trades: list[dict[str, Any]], as_of: str) -> None:
    ap = hyp.get("applied") or {}
    since = date.fromisoformat(ap["applied_as_of"])
    after = [float(_pnl(t)) for t in _dedup_best_signals(trades)
             if (_close_day(t) is not None and _close_day(t) > since)]
    ap["n_after"] = len(after)
    ap["mean_R_after"] = _r(sum(after) / len(after)) if after else None
    base = ap.get("baseline_mean_R")
    if after and base is not None:
        shifted = [x - float(base) for x in after]
        ap["p_after_ge_baseline"] = bootstrap_p_positive(shifted)
        ap["regression_flag"] = bool(
            len(after) >= APPLIED_MIN_N and (sum(after) / len(after)) < float(base) - APPLIED_REGRESSION_R
        )
    elif after:
        # No admissible baseline: judge against the pre-registered absolute
        # floor instead. p_after_ge_baseline stays None - there is no baseline
        # to be "ge" than, and inventing one is the failure this avoids.
        ap["regression_flag"] = bool(
            len(after) >= APPLIED_MIN_N
            and (sum(after) / len(after)) < ROLLBACK_ABS_MEAN_R
        )
    # Annotate (never overwrite) the baseline's provenance so both renderers
    # can say whether the rollback rule in force rests on admissible evidence.
    ap["baseline_status"] = _baseline_status(ap)
    ap["baseline_is_retired_evidence"] = ap["baseline_status"] == BASELINE_RETIRED
    ap["last_eval_as_of"] = as_of
    hyp["applied"] = ap


# ── forward evaluation ──────────────────────────────────────────────────────

def bootstrap_p_positive(
    deltas: list[float], n_boot: int = BOOTSTRAP_N, seed: int = BOOTSTRAP_SEED
) -> float | None:
    """Fraction of bootstrap resamples (with replacement) whose mean > 0.
    None when fewer than BOOTSTRAP_MIN_N observations. Deterministic."""
    n = len(deltas)
    if n < BOOTSTRAP_MIN_N:
        return None
    rng = random.Random(seed)
    hits = 0
    for _ in range(n_boot):
        s = 0.0
        for _ in range(n):
            s += deltas[rng.randrange(n)]
        if s / n > 0:
            hits += 1
    return hits / n_boot


def _decide_status(current: str, fwd: dict[str, Any], th: dict[str, Any]) -> str:
    n = fwd["n_signals"]
    p = fwd["bootstrap_p_positive"]
    min_n = int(th.get("min_forward_signals", DEFAULT_THRESHOLDS["min_forward_signals"]))
    if n >= min_n and p is not None:
        if p >= float(th.get("min_p_positive", DEFAULT_THRESHOLDS["min_p_positive"])):
            return "CONFIRMED"
        if p <= float(th.get("max_p_positive_reject", DEFAULT_THRESHOLDS["max_p_positive_reject"])):
            return "REJECTED"
    return "SHADOW"


def _forward_candidates(
    hyp: dict[str, Any], trades: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    """Closed trades with close_date strictly after registered_as_of, not yet
    evaluated, grouped by signal key (mirrored exchange rows collapse)."""
    reg = date.fromisoformat(hyp["registered_as_of"])
    fwd = hyp["forward"]
    done_ids = set(fwd.get("trade_ids_evaluated", []))
    done_sigs = set(fwd.get("signal_keys_evaluated", []))
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for t in trades:
        if t.get("close_date") in (None, "") or _pnl(t) is None:
            continue
        cd = _close_day(t)
        if cd is None or cd <= reg:
            continue
        if t.get("id") in done_ids:
            continue
        sig = _sig_str(t)
        if sig in done_sigs:
            continue
        groups[sig].append(t)
    return groups


def update_forward(
    ledger: dict[str, Any],
    trades: list[dict[str, Any]],
    excursions: dict[int, dict[str, Any]] | None,
    as_of: str,
    outcomes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Score every SHADOW/CONFIRMED hypothesis on new forward signals, then
    apply its pre-registered thresholds. Deterministic. Returns a summary.
    `outcomes` (the bot's resolved blocked-entry rows) feeds "unblock" kinds;
    every other kind is scored on `trades` exactly as before."""
    excursions = excursions or {}
    outcomes = outcomes or []
    summary: dict[str, Any] = {"as_of": as_of, "evaluated": {}, "status_changes": []}
    for sid in sorted(ledger.get("hypotheses", {})):
        hyp = ledger["hypotheses"][sid]
        if hyp.get("status") == "APPLIED":
            _update_applied(hyp, trades, as_of)
            ap = hyp["applied"]
            summary["evaluated"][sid] = {"applied": True, "n_after": ap["n_after"],
                                         "mean_R_after": ap["mean_R_after"],
                                         "regression_flag": ap["regression_flag"], "status": "APPLIED"}
            continue
        if hyp.get("status") not in ("SHADOW", "CONFIRMED"):
            continue
        fwd = hyp["forward"]
        new_n = 0
        if hyp.get("kind") == "unblock":
            groups: dict[str, list[dict[str, Any]]] = {}
            for o in _forward_unblock_candidates(hyp, outcomes):
                delta = outcome_r(o)
                if delta is None:
                    continue  # unresolved return: re-scanned on later runs
                key = str(o.get("candidate_id") or f"{o.get('ts_utc')}|{o.get('symbol')}|{o.get('strategy_id')}")
                fwd["samples"].append({
                    "signal": key,
                    "trade_id": None,
                    "row_ids": [],
                    "close_date": str(o.get("ts_utc") or "")[:10],
                    "pnl_r": None,
                    "delta_R": _r(delta),
                    "symbol": o.get("symbol"),
                    "strategy": o.get("strategy_id"),
                    "classification": o.get("classification"),
                })
                fwd["signal_keys_evaluated"].append(key)
                fwd["n_rows"] += 1
                new_n += 1
        else:
            groups = _forward_candidates(hyp, trades)
        for sig in sorted(groups):
            rows = groups[sig]
            # dedup_best: the best-R row represents the signal (tie → lowest id)
            best = max(rows, key=lambda r: (_pnl(r), -int(r.get("id") or 0)))
            ex = excursions.get(best.get("id"))
            delta = evaluate_hypothesis(hyp, best, ex)
            if delta is None:
                continue  # rule does not apply (yet); re-scanned on later runs
            fwd["samples"].append({
                "signal": sig,
                "trade_id": best.get("id"),
                "row_ids": sorted(int(r.get("id")) for r in rows if r.get("id") is not None),
                "close_date": best.get("close_date"),
                "pnl_r": _r(_pnl(best)),
                "delta_R": _r(delta),
            })
            fwd["trade_ids_evaluated"].extend(
                int(r.get("id")) for r in rows if r.get("id") is not None
            )
            fwd["signal_keys_evaluated"].append(sig)
            fwd["n_rows"] += len(rows)
            new_n += 1
        fwd["trade_ids_evaluated"] = sorted(set(fwd["trade_ids_evaluated"]))
        fwd["signal_keys_evaluated"] = sorted(set(fwd["signal_keys_evaluated"]))
        deltas = [float(s["delta_R"]) for s in fwd["samples"]]
        fwd["n_signals"] = len(deltas)
        fwd["delta_R_sum"] = _r(sum(deltas)) if deltas else 0.0
        fwd["delta_R_mean"] = _r(sum(deltas) / len(deltas)) if deltas else None
        fwd["wins"] = sum(1 for d in deltas if d > 0)
        fwd["losses"] = sum(1 for d in deltas if d < 0)
        fwd["bootstrap_p_positive"] = bootstrap_p_positive(deltas)
        fwd["last_eval_as_of"] = as_of

        new_status = _decide_status(hyp["status"], fwd, hyp.get("thresholds", DEFAULT_THRESHOLDS))
        if new_status != hyp["status"]:
            note = (f"{hyp['status']} -> {new_status}: forward n={fwd['n_signals']} "
                    f"mean_delta_R={fwd['delta_R_mean']} p_positive={fwd['bootstrap_p_positive']}")
            hyp["history"].append({"as_of": as_of, "status": new_status, "note": note})
            summary["status_changes"].append({"id": sid, "from": hyp["status"], "to": new_status})
            hyp["status"] = new_status
        summary["evaluated"][sid] = {"new_signals": new_n, "n_signals": fwd["n_signals"],
                                     "status": hyp["status"]}
    ledger["last_updated_as_of"] = as_of
    return summary


# ── markdown ────────────────────────────────────────────────────────────────

def _fmt(v: Any) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def _evidence_line(ev: dict[str, Any]) -> str:
    parts = []
    for k in sorted(ev):
        v = ev[k]
        if isinstance(v, list):
            v = "[" + ",".join(str(x) for x in v[:5]) + "]"
        parts.append(f"{k}={_fmt(v)}")
    return " ".join(parts) or "-"


def _next_threshold(hyp: dict[str, Any]) -> str:
    st = hyp["status"]
    fwd = hyp["forward"]
    th = hyp.get("thresholds", DEFAULT_THRESHOLDS)
    min_n = th["min_forward_signals"]
    if st == "APPLIED":
        ap = hyp.get("applied") or {}
        n_after = ap.get("n_after") or 0
        rule = ap.get("rollback_rule")
        if not rule:
            rule = (
                f"mean R < {ROLLBACK_ABS_MEAN_R}R at n >= {APPLIED_MIN_N}"
                if ap.get("baseline_mean_R") is None else
                f"mean R < baseline - {APPLIED_REGRESSION_R}R at n >= {APPLIED_MIN_N}"
            )
        warn = " ⚠ baseline is RETIRED evidence" if _baseline_status(ap) == BASELINE_RETIRED else ""
        if n_after < APPLIED_MIN_N:
            return f"rollback check at n>={APPLIED_MIN_N} (have {n_after}): {rule}{warn}"
        return f"{rule}{warn}"
    if st == "PROPOSED":
        return "unknown kind: not evaluated"
    if st in ("REJECTED", "RETIRED"):
        return "terminal"
    n = fwd["n_signals"]
    if n < min_n:
        return f"need {min_n} forward signals (have {n})"
    return (f"p_positive {_fmt(fwd['bootstrap_p_positive'])}: confirm >= {th['min_p_positive']}, "
            f"reject <= {th['max_p_positive_reject']}")


def render_markdown(ledger: dict[str, Any]) -> str:
    hyps = ledger.get("hypotheses", {})
    counts: dict[str, int] = defaultdict(int)
    for h in hyps.values():
        counts[h["status"]] += 1
    L = [
        f"# Trade Hypothesis Ledger — {ledger.get('last_updated_as_of') or '-'}",
        "",
        f"**{BANNER}**",
        "",
        "Every rule suggestion from the learning report is registered here as a "
        "hypothesis. Its in-sample evidence is frozen at registration; it is then "
        "scored only on PAPER trades that close strictly after that date "
        "(out-of-sample by construction), via a counterfactual delta_R = "
        "R(rule) − R(realized) per deduplicated signal. Mirrored exchange rows "
        "collapse to one signal (best-R row). Thresholds are pre-registered: "
        f"CONFIRMED needs n >= {DEFAULT_THRESHOLDS['min_forward_signals']} forward signals and "
        f"bootstrap p_positive >= {DEFAULT_THRESHOLDS['min_p_positive']}; REJECTED needs the same n "
        f"and p_positive <= {DEFAULT_THRESHOLDS['max_p_positive_reject']}; otherwise SHADOW.",
        "",
        "Status counts: " + (", ".join(f"{s} {counts[s]}" for s in STATUSES if counts[s]) or "none"),
        "",
        "| id | status | kind | registered | in-sample evidence (frozen) | fwd n (rows) | "
        "mean ΔR | sum ΔR | p_positive | next threshold |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for sid in sorted(hyps):
        h = hyps[sid]
        f = h["forward"]
        L.append(
            f"| {sid} | **{h['status']}** | {h['kind']} | {h['registered_as_of']} | "
            f"{_evidence_line(h.get('registered_evidence', {}))} | "
            f"{f['n_signals']} ({f['n_rows']}) | {_fmt(f['delta_R_mean'])} | "
            f"{_fmt(f['delta_R_sum'])} | {_fmt(f['bootstrap_p_positive'])} | {_next_threshold(h)} |"
        )
    if not hyps:
        L.append("| - | - | - | - | no hypotheses registered | - | - | - | - | - |")
    L += [
        "",
        "## Rules",
        "",
    ]
    for sid in sorted(hyps):
        h = hyps[sid]
        last = h["history"][-1] if h.get("history") else {}
        L.append(f"- **{sid}** — {h.get('rule')} · params {json.dumps(h.get('params', {}), sort_keys=True)} "
                 f"· last change {last.get('as_of', '-')}: {last.get('note', '-')}")
    if not hyps:
        L.append("- none")
    L += [
        "",
        "## What a CONFIRMED rule means",
        "",
        "CONFIRMED means the forward counterfactual evidence crossed the pre-registered "
        "thresholds on trades that closed after the hypothesis was registered. It is a "
        "recommendation for the operator to consider applying, by hand, in the PAPER bot "
        "after reading the numbers. Nothing is applied automatically: this tool has no "
        "broker, no order path, never writes to the journal and never changes the bot. "
        "CONFIRMED is not a claim about live trading. Every hypothesis keeps being "
        "re-scored as more paper trades close and can fall back to SHADOW or move to "
        "REJECTED. Counterfactual deltas are approximations (see the partial_2R note in "
        "the module docstring) and small samples are noisy even past the thresholds.",
        "",
        f"_{BANNER}_",
        "",
    ]
    return "\n".join(L)


def forbidden_words_found(text: str) -> list[str]:
    low = text.lower()
    return [w for w in FORBIDDEN_WORDS if w in low]


# ── one full cycle (pure I/O wrapper used by main() and the report hook) ────

def run_cycle(
    report: dict[str, Any],
    trades: list[dict[str, Any]],
    excursions: dict[int, dict[str, Any]] | None,
    as_of: str,
    ledger_path: Path = LEDGER_PATH,
    report_dir: Path = REPORT_DIR,
    outcomes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """`outcomes=None` loads the bot's blocked-entry ledger from the external
    project (read-only, empty when absent); pass a list to control it in tests."""
    ledger = load_ledger(ledger_path)
    if ledger.get("created_as_of") is None:
        ledger["created_as_of"] = as_of
    added = register_from_report(report, as_of, ledger)
    if outcomes is None:
        outcomes = load_missed_outcomes()
    summary = update_forward(ledger, trades, excursions, as_of, outcomes=outcomes)
    save_ledger(ledger, ledger_path)

    md = render_markdown(ledger)
    bad = forbidden_words_found(md)
    if bad:
        print(f"WARNING forbidden words in render: {bad}")
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / MD_NAME).write_text(md, encoding="utf-8")

    by_status: dict[str, int] = defaultdict(int)
    for h in ledger["hypotheses"].values():
        by_status[h["status"]] += 1
    line = {
        "as_of": as_of,
        "n_hypotheses": len(ledger["hypotheses"]),
        "registered": added,
        "by_status": dict(sorted(by_status.items())),
        "forward_n": {sid: h["forward"]["n_signals"] for sid, h in sorted(ledger["hypotheses"].items())},
        "status_changes": summary["status_changes"],
    }
    with (report_dir / HISTORY_NAME).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, sort_keys=True) + "\n")
    ledger["_last_run"] = line
    return ledger


def _register_manual_entry() -> None:
    """One-shot /guide registration. Never allowed to break the run."""
    try:
        import database as db  # local sparta.db; unrelated to trades.db
        db.upsert_manual_entry(
            "trade_hypothesis_ledger",
            module_name="Trade Hypothesis Ledger (forward test)",
            category="Trading",
            status="live",
            short_description=(
                "Registers every learning-report rule suggestion as a hypothesis and "
                "scores it forward on paper trades that close after registration; "
                "promotes/rejects by pre-registered thresholds. Observation only."
            ),
            how_it_works=(
                "Reads trades.db read-only, freezes each suggestion's in-sample evidence, "
                "computes counterfactual delta_R per deduplicated forward signal (block / "
                "stop cap -1.5R / partial 2R / weekday flag), bootstraps p_positive "
                "(2000 resamples, seed 42) and sets SHADOW / CONFIRMED / REJECTED. "
                f"An APPLIED rule's baseline is built only from trades opened on/after "
                f"the {EVIDENCE_VALID_FROM} partial-bar fix; with fewer than "
                f"{APPLIED_MIN_N} such closes it stores no baseline and falls back to "
                f"the pre-registered absolute rollback rule (mean R < "
                f"{ROLLBACK_ABS_MEAN_R}R at n >= {APPLIED_MIN_N}). A baseline frozen "
                "before that date is marked RETIRED in the report rather than silently "
                "rewritten. 'unblock__<REASON>' hypotheses (2026-09-23) learn from entries "
                "the bot did NOT take: they are scored on the bot's resolved blocked-entry "
                "ledger (reports/observation_mode/missed_opportunity_outcomes.jsonl), "
                "delta_R = hypothetical R of the blocked entry, so CONFIRMED means the gate "
                "is costing money and REJECTED means it is earning its keep. Register with "
                "--register-unblock REASON."
            ),
            when_to_use=(
                "Daily, after the learning report. CONFIRMED = a recommendation for the "
                "operator to consider in the paper bot; nothing is applied automatically."
            ),
            user_action=(
                "Run `.venv\\Scripts\\python tools\\trade_hypothesis_ledger.py`; read "
                "reports/trade_learning/hypothesis_ledger.md (ledger at "
                "data/trade_hypothesis_ledger.json)."
            ),
            sort_order=97,
        )
    except Exception as exc:  # noqa: BLE001 - registration is best-effort
        print(f"[manual-entry] skipped: {type(exc).__name__}: {exc}")


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Hypothesis ledger (observation only)")
    ap.add_argument("--mark-applied", nargs="*", default=None,
                    help="hypothesis ids the operator applied in the paper bot (Phase 4)")
    ap.add_argument("--applied-as-of", default=None, help="YYYY-MM-DD the rule went live in the paper bot")
    ap.add_argument("--note", default="", help="free text, e.g. the bot commit hash")
    ap.add_argument("--register-unblock", nargs="*", default=None, metavar="COUNTED_REASON",
                    help="register unblock__<REASON> hypotheses scored on the bot's resolved "
                         "blocked-entry ledger (e.g. TREND_UP_BLOCKS_SHORT)")
    args = ap.parse_args(argv)
    db_path = external_root().joinpath(*_REL_TRADES_DB)
    if not db_path.exists():
        print(f"trades.db not found: {db_path}")
        return 1
    as_of = datetime.now().strftime("%Y-%m-%d")  # local operator date
    trades, excursions = load_journal_ro(db_path)
    if args.register_unblock:
        ledger = load_ledger()
        outcomes = load_missed_outcomes()
        for reason in args.register_unblock:
            sid = register_unblock(ledger, reason, as_of, outcomes, note=args.note)
            if sid:
                ev = ledger["hypotheses"][sid]["registered_evidence"]
                print(f"REGISTERED {sid} as of {as_of}: frozen evidence {ev}")
            else:
                print(f"already registered or empty reason: {reason}")
        save_ledger(ledger)
    if args.mark_applied:
        ledger = load_ledger()
        when = args.applied_as_of or as_of
        for sid in args.mark_applied:
            if sid not in ledger.get("hypotheses", {}):
                print(f"unknown hypothesis: {sid}")
                return 2
            mark_applied(ledger, sid, when, trades, note=args.note)
            print(f"APPLIED {sid} as of {when}")
        save_ledger(ledger)
    rep = build_learning_report(trades, excursions, as_of)
    ledger = run_cycle(rep, trades, excursions, as_of)
    _register_manual_entry()
    last = ledger["_last_run"]
    print(BANNER)
    print(f"wrote {LEDGER_PATH}, {REPORT_DIR / MD_NAME}, {HISTORY_NAME} (+1 line)")
    print(f"hypotheses {last['n_hypotheses']} · registered now {last['registered']} · "
          f"by_status {last['by_status']} · forward_n {last['forward_n']} · "
          f"status_changes {last['status_changes']}")
    return 0


__all__ = [
    "new_ledger", "load_ledger", "save_ledger", "kind_for_id", "register_from_report",
    "evaluate_block", "evaluate_stop_cap", "evaluate_partial_2R", "evaluate_flag",
    "evaluate_hypothesis", "bootstrap_p_positive", "update_forward", "render_markdown",
    "forbidden_words_found", "run_cycle", "DEFAULT_THRESHOLDS", "FORBIDDEN_WORDS",
    "load_missed_outcomes", "outcome_r", "unblock_evidence", "register_unblock",
]

if __name__ == "__main__":
    sys.exit(main())
