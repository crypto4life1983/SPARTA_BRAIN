"""Out-of-sample protocol + run ENFORCEMENT layer (Factory-D4).

Enforces the one-shot OOS discipline planned in
reports/factory_d1_reusable_validation_runner_plan/ (committed 93b5299), built on
the report schema/writer of engine/validation_reports.py (Factory-D2) and the
metric helpers of engine/validation_is_runner.py (Factory-D3).

This module enforces SEQUENCING and WINDOW HYGIENE -- it is NOT a strategy
evaluator, NOT an optimizer, and NOT a version-control client. It refuses to run
an OOS pass unless a pre-registered protocol commit hash is supplied, refuses any
in-sample (2013-2022) file or bar inside an OOS window, and refuses 2026 unless
explicitly allowed.

OFFLINE / INERT: Python standard library only (os, typing) plus the sibling
factory modules. It opens no network connection, spawns no child process,
fetches no data, runs no shell or version-control call, and does NO dynamic code
loading -- the strategy is passed in as a plain callable. It never mutates a
strategy's frozen parameters and decides NO pass/fail verdict on its own (the
caller supplies the verdict).
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional, Set

from engine import validation_reports
from engine.validation_is_runner import compute_is_metrics, _normalize_summary


# The sealed in-sample years -- forbidden inside an OOS window.
IS_YEARS: Set[str] = {str(y) for y in range(2013, 2023)}
# The authorized out-of-sample years.
DEFAULT_OOS_YEARS: Set[int] = {2023, 2024, 2025}
# Sentinel strings that must never count as a real, committed protocol.
_UNBOUND_TOKENS = {"", "uncommitted", "draft", "none", "todo", "pending"}


def assert_oos_protocol_bound(
    protocol_commit: Any, protocol_path: Optional[str] = None
) -> None:
    """Require a real, pre-registered protocol commit before any OOS run.

    Rejects a missing / empty / placeholder ("UNCOMMITTED", "DRAFT", ...) value.
    If `protocol_path` is given, it must point at a report.json / report.md that
    exists on disk. Performs NO version-control call -- the caller is responsible
    for having actually committed the protocol; this only refuses obvious
    placeholders.
    """
    if not isinstance(protocol_commit, str) or protocol_commit.strip().lower() in _UNBOUND_TOKENS:
        raise ValueError(
            "OOS run refused: a non-empty pre-registered protocol_commit is "
            f"required (got {protocol_commit!r})"
        )
    if protocol_path is not None:
        base = os.path.basename(protocol_path)
        if base not in ("report.json", "report.md"):
            raise ValueError(
                "protocol_path must be a report.json/report.md, got "
                f"{base!r}"
            )
        if not os.path.isfile(protocol_path):
            raise ValueError(f"protocol_path does not exist: {protocol_path}")


def _path_year_tokens(path: str) -> Set[str]:
    base = os.path.basename(path)
    return {y for y in (IS_YEARS | {"2023", "2024", "2025", "2026"}) if y in base}


def assert_oos_only_paths(
    paths: List[str], window_label: str = "OOS", allow_2026: bool = False
) -> None:
    """Refuse in-sample (2013-2022) files inside an OOS window (path-level seal).

    Accepts 2023/2024/2025. Refuses 2026 unless `allow_2026` is explicitly True.
    A path carrying no recognizable year token is left alone (cannot be judged).
    Raises ValueError naming the offending path(s); returns None when clean.
    """
    if str(window_label).upper() != "OOS":
        return
    bad_is: List[str] = []
    bad_2026: List[str] = []
    for p in paths:
        toks = _path_year_tokens(p)
        if toks & IS_YEARS:
            bad_is.append(p)
        elif "2026" in toks and not allow_2026:
            bad_2026.append(p)
    if bad_is:
        raise ValueError(
            "OOS window refuses in-sample (2013-2022) files: " + ", ".join(bad_is)
        )
    if bad_2026:
        raise ValueError(
            "OOS window refuses 2026 files unless explicitly allowed: "
            + ", ".join(bad_2026)
        )


def assert_bars_in_oos_range(
    bars: List[Dict[str, Any]], allowed_years: Optional[Set[int]] = None
) -> None:
    """Refuse any bar whose calendar year is not in the allowed OOS set.

    Raises ValueError listing the out-of-range years; returns None when clean.
    """
    allowed = {int(y) for y in (allowed_years if allowed_years is not None else DEFAULT_OOS_YEARS)}
    seen_bad = sorted(
        {b["timestamp"].year for b in bars if b["timestamp"].year not in allowed}
    )
    if seen_bad:
        raise ValueError(
            "bars fall outside the allowed OOS years "
            f"{sorted(allowed)}: out-of-range years {seen_bad}"
        )


def _metrics_from_result(result: Any):
    """Normalize a runner result (trade list OR summary dict) -> (metrics, trades).

    Reuses the Factory-D3 helpers so IS and OOS report identical metric shapes.
    """
    if isinstance(result, list):
        return compute_is_metrics(result), result
    if isinstance(result, dict):
        if isinstance(result.get("trades"), list):
            return compute_is_metrics(result["trades"]), result["trades"]
        return _normalize_summary(result), []
    raise TypeError(
        "strategy_runner must return a list of trades or a summary dict, "
        f"got {type(result).__name__}"
    )


def run_oos_baseline(
    strategy_runner: Callable[[List[Dict[str, Any]]], Any],
    bars: List[Dict[str, Any]],
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """Run a frozen strategy callable on OOS bars -- ONLY if protocol-bound.

    `metadata` MUST carry "protocol_commit" (a real pre-registered hash); it MAY
    carry "oos_years" (default {2023,2024,2025}), "input_files" (re-checked
    against the path seal), and "allow_2026". The strategy is a plain callable,
    never loaded from a string, so no dynamic code execution happens here, and no
    parameter is mutated.

    Returns {"metrics": <standard metric dict>, "trades": <list>, "raw": <result>}.
    """
    if not isinstance(metadata, dict):
        raise TypeError("metadata dict with a 'protocol_commit' is required")

    assert_oos_protocol_bound(
        metadata.get("protocol_commit"), metadata.get("protocol_path")
    )

    oos_years = metadata.get("oos_years")
    allowed = {int(y) for y in (oos_years if oos_years else DEFAULT_OOS_YEARS)}

    input_files = metadata.get("input_files")
    if input_files:
        assert_oos_only_paths(
            input_files, "OOS", allow_2026=bool(metadata.get("allow_2026", False))
        )

    assert_bars_in_oos_range(bars, allowed)

    result = strategy_runner(bars)
    metrics, trades = _metrics_from_result(result)
    return {"metrics": metrics, "trades": trades, "raw": result}


def build_oos_protocol_report(
    *,
    branch_id: str,
    title: str,
    criteria: Dict[str, Any],
    module_id: str = "oos_protocol",
    protocol_rules: Optional[List[Any]] = None,
    source_commits: Optional[Dict[str, Any]] = None,
    input_files: Optional[List[str]] = None,
    data_window: Optional[Dict[str, Any]] = None,
    frozen_parameters: Optional[Dict[str, Any]] = None,
    status: str = "COMPLETE",
    verdict: str = "PROTOCOL_REGISTERED",
    caveats: Optional[List[Any]] = None,
    next_allowed_step: str = "oos_run",
    forbidden_actions: Optional[List[Any]] = None,
    notes: Optional[List[Any]] = None,
    created_utc: str = "",
) -> Dict[str, Any]:
    """Assemble a PRE-REGISTERED OOS protocol report (no strategy is run).

    The pass/watch/fail `criteria` and `protocol_rules` are frozen into the
    report's frozen_parameters so they are pinned by the commit that records this
    report -- that commit's hash becomes the `protocol_commit` later required by
    run_oos_baseline. Writes nothing.
    """
    frozen = dict(frozen_parameters or {})
    frozen["pass_watch_fail_criteria"] = dict(criteria)
    frozen["protocol_rules"] = list(protocol_rules or [])

    default_forbidden = [
        "no_oos_peek_before_commit", "no_optimization",
        "no_parameter_change", "no_data_fetch",
    ]
    return validation_reports.make_report(
        branch_id=branch_id,
        module_id=module_id,
        title=title,
        status=status,
        verdict=verdict,
        created_utc=created_utc,
        source_commits=dict(source_commits or {}),
        input_files=list(input_files or []),
        data_window=dict(data_window or {}),
        frozen_parameters=frozen,
        metrics={},
        caveats=list(caveats or []),
        next_allowed_step=next_allowed_step,
        forbidden_actions=list(forbidden_actions or default_forbidden),
        notes=list(notes or []),
    )


def build_oos_result_report(
    *,
    branch_id: str,
    title: str,
    verdict: str,
    metrics: Dict[str, Any],
    protocol_commit: str,
    module_id: str = "oos_run",
    source_commits: Optional[Dict[str, Any]] = None,
    input_files: Optional[List[str]] = None,
    data_window: Optional[Dict[str, Any]] = None,
    frozen_parameters: Optional[Dict[str, Any]] = None,
    status: str = "COMPLETE",
    caveats: Optional[List[Any]] = None,
    next_allowed_step: str = "entry_significance",
    forbidden_actions: Optional[List[Any]] = None,
    notes: Optional[List[Any]] = None,
    created_utc: str = "",
) -> Dict[str, Any]:
    """Assemble a one-shot OOS RESULT report bound to its protocol commit.

    Re-asserts the protocol binding, then records `protocol_commit` in
    source_commits. The verdict / caveats are SUPPLIED BY THE CALLER -- this
    module never decides pass/fail itself. Writes nothing.
    """
    assert_oos_protocol_bound(protocol_commit)

    commits = dict(source_commits or {})
    commits["protocol_commit"] = protocol_commit

    default_forbidden = [
        "no_oos_reuse", "no_optimization", "no_parameter_sweeps",
        "no_data_fetch", "no_paper_or_live", "no_execution_or_api",
    ]
    return validation_reports.make_report(
        branch_id=branch_id,
        module_id=module_id,
        title=title,
        status=status,
        verdict=verdict,
        created_utc=created_utc,
        source_commits=commits,
        input_files=list(input_files or []),
        data_window=dict(data_window or {}),
        frozen_parameters=dict(frozen_parameters or {}),
        metrics=dict(metrics),
        caveats=list(caveats or []),
        next_allowed_step=next_allowed_step,
        forbidden_actions=list(forbidden_actions or default_forbidden),
        notes=list(notes or []),
    )
