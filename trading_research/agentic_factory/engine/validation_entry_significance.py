"""Reusable entry-significance integration layer (Factory-D5).

Wraps the existing engine/signal_significance.py so any future *frozen* strategy
can produce a STANDARD entry-significance report through the validation factory.
It runs the same-count random-entry permutation test across a fixed horizon set
and maps the per-horizon verdicts to one conservative entry-edge disposition.

This is the Factory-D1 ladder module E (entry_significance): "real entries vs
same-count random-in-regime; optional vs raw-signal baseline; fixed horizons, NO
horizon shopping." It enforces the FIXED horizon set so a caller cannot fish for
the one horizon that happens to look significant.

OFFLINE / INERT: Python standard library only (typing) plus the sibling factory
modules. It opens no network connection, spawns no child process, fetches no
data, runs no shell or version-control call, reads no CSV / real market data, and
does NO dynamic code loading -- bars and signal indices are passed in by the
caller. It never mutates a strategy's frozen parameters and writes nothing.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from engine import validation_reports
from engine import signal_significance


# Final entry-edge dispositions (distinct from the per-horizon labels in
# signal_significance: EDGE_LIKELY / INCONCLUSIVE / NO_EDGE / NO_RESULT).
ENTRY_EDGE_SUPPORTED = "ENTRY_EDGE_SUPPORTED"
ENTRY_EDGE_INCONCLUSIVE = "ENTRY_EDGE_INCONCLUSIVE"
ENTRY_EDGE_NOT_SUPPORTED = "ENTRY_EDGE_NOT_SUPPORTED"

DEFAULT_HORIZONS: Tuple[int, ...] = (5, 10, 20, 40)


def normalize_signal_indices(
    signal_indices: Sequence[Any], max_index: Optional[int] = None
) -> List[int]:
    """Sort + de-duplicate a list of integer signal indices.

    Rejects non-int values (bool is refused even though it subclasses int),
    negative indices, and -- when `max_index` is given -- any index past the end.
    Returns a sorted list of unique indices.
    """
    out: set = set()
    for x in signal_indices:
        if isinstance(x, bool) or not isinstance(x, int):
            raise ValueError(f"signal index must be a non-bool int, got {x!r}")
        if x < 0:
            raise ValueError(f"signal index must be non-negative, got {x}")
        if max_index is not None and x > max_index:
            raise ValueError(f"signal index {x} exceeds max_index {max_index}")
        out.add(x)
    return sorted(out)


def run_entry_significance(
    bars: Sequence[Any],
    signal_indices: Sequence[int],
    *,
    horizons: Sequence[int] = DEFAULT_HORIZONS,
    n_iter: int = 5000,
    seed: int = 0,
    label: str = "IS",
    baseline_signal_indices: Optional[Sequence[int]] = None,
) -> Dict[str, Any]:
    """Run the same-count random-entry significance test across fixed horizons.

    Window hygiene (IS vs OOS) is the CALLER's responsibility; this module only
    measures forward-return significance and never inspects file paths. The
    random baseline is drawn inside signal_significance with exactly as many
    entries as the real signal produced (same-count), fully seeded.

    If `baseline_signal_indices` is supplied (e.g. raw-breakout entries to compare
    a retest-hold entry against), a light forward-return mean comparison is added
    per horizon -- it does NOT change the verdict, it is descriptive context.

    Returns a structured dict keyed by horizon under "results".
    """
    max_index = (len(bars) - 1) if len(bars) else None
    idx = normalize_signal_indices(signal_indices, max_index=max_index)

    results: Dict[str, Any] = {}
    for h in horizons:
        results[str(int(h))] = signal_significance.summarize_significance(
            bars, idx, int(h), n_iter=n_iter, seed=seed
        )

    baseline_comparison: Optional[Dict[str, Any]] = None
    if baseline_signal_indices is not None:
        alt = normalize_signal_indices(baseline_signal_indices, max_index=max_index)
        baseline_comparison = {}
        for h in horizons:
            real_fr = signal_significance.forward_returns(bars, idx, int(h))
            alt_fr = signal_significance.forward_returns(bars, alt, int(h))
            baseline_comparison[str(int(h))] = {
                "real_count": len(real_fr),
                "real_mean": (sum(real_fr) / len(real_fr)) if real_fr else 0.0,
                "alt_count": len(alt_fr),
                "alt_mean": (sum(alt_fr) / len(alt_fr)) if alt_fr else 0.0,
            }

    return {
        "label": label,
        "horizons": [int(h) for h in horizons],
        "n_iter": int(n_iter),
        "seed": int(seed),
        "signal_count": len(idx),
        "results": results,
        "baseline_comparison": baseline_comparison,
    }


def derive_entry_verdict(
    results: Dict[str, Any], min_supported_horizons: int = 1
) -> str:
    """Map per-horizon significance verdicts to one conservative entry verdict.

    Accepts either the full run_entry_significance() output (it reads the
    "results" sub-dict) or a bare {horizon: summary} mapping.

    Conservative rule:
      * SUPPORTED  -- at least `min_supported_horizons` valid horizons are
        EDGE_LIKELY AND NO valid horizon is NO_EDGE (no severe contradiction).
      * NOT_SUPPORTED -- every valid horizon is NO_EDGE.
      * INCONCLUSIVE -- anything else, including no valid (non-NO_RESULT) horizon.

    A horizon whose verdict is NO_RESULT (too few signals / too short) is treated
    as "no information" and excluded from the tally rather than counted against.
    """
    by_h = results.get("results", results)
    verdicts = [
        (v or {}).get("verdict") for v in by_h.values() if isinstance(v, dict)
    ]
    valid = [v for v in verdicts if v not in (None, signal_significance.NO_RESULT)]
    if not valid:
        return ENTRY_EDGE_INCONCLUSIVE

    supported = sum(1 for v in valid if v == signal_significance.EDGE_LIKELY)
    no_edge = sum(1 for v in valid if v == signal_significance.NO_EDGE)

    if supported >= min_supported_horizons and no_edge == 0:
        return ENTRY_EDGE_SUPPORTED
    if all(v == signal_significance.NO_EDGE for v in valid):
        return ENTRY_EDGE_NOT_SUPPORTED
    return ENTRY_EDGE_INCONCLUSIVE


def build_entry_significance_report(
    *,
    branch_id: str,
    title: str,
    results: Dict[str, Any],
    verdict: Optional[str] = None,
    min_supported_horizons: int = 1,
    module_id: str = "entry_significance",
    source_commits: Optional[Dict[str, Any]] = None,
    input_files: Optional[List[str]] = None,
    data_window: Optional[Dict[str, Any]] = None,
    frozen_parameters: Optional[Dict[str, Any]] = None,
    status: str = "COMPLETE",
    caveats: Optional[List[Any]] = None,
    next_allowed_step: str = "sequence_risk",
    forbidden_actions: Optional[List[Any]] = None,
    notes: Optional[List[Any]] = None,
    created_utc: str = "",
) -> Dict[str, Any]:
    """Assemble a Factory-D2-schema entry-significance report.

    The verdict defaults to derive_entry_verdict(results) but the caller may
    override it. The fixed horizon set / n_iter / seed are frozen into
    frozen_parameters so the run is reproducible from the report. Writes nothing.
    """
    v = verdict or derive_entry_verdict(results, min_supported_horizons)

    metrics = {
        "label": results.get("label"),
        "horizons": results.get("horizons"),
        "n_iter": results.get("n_iter"),
        "seed": results.get("seed"),
        "signal_count": results.get("signal_count"),
        "by_horizon": results.get("results"),
        "baseline_comparison": results.get("baseline_comparison"),
    }

    frozen = dict(frozen_parameters or {})
    frozen.setdefault("horizons", list(results.get("horizons", [])))
    frozen.setdefault("n_iter", results.get("n_iter"))
    frozen.setdefault("seed", results.get("seed"))
    frozen.setdefault("min_supported_horizons", min_supported_horizons)

    default_forbidden = [
        "no_horizon_shopping", "no_optimization", "no_parameter_sweeps",
        "no_data_fetch", "no_paper_or_live", "no_execution_or_api",
    ]
    return validation_reports.make_report(
        branch_id=branch_id,
        module_id=module_id,
        title=title,
        status=status,
        verdict=v,
        created_utc=created_utc,
        source_commits=dict(source_commits or {}),
        input_files=list(input_files or []),
        data_window=dict(data_window or {}),
        frozen_parameters=frozen,
        metrics=metrics,
        caveats=list(caveats or []),
        next_allowed_step=next_allowed_step,
        forbidden_actions=list(forbidden_actions or default_forbidden),
        notes=list(notes or []),
    )
