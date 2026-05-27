"""Read-only snapshot exporter for the SPARTA Trade Intelligence Journal.

Writes a timestamped JSON + Markdown pair into `reports/`:

    reports/journal_snapshot_<UTC_TIMESTAMP>.json
    reports/journal_snapshot_<UTC_TIMESTAMP>.md

Safety contract (mirrors `tools/trade_journal_adapter.py`):

  * No writes outside `C:\\SPARTA_BRAIN\\reports` (the configured --reports-dir).
  * No broker / API / order / scheduler / execution code on any path.
  * The external trading project is touched only through the adapter, which
    opens `trades.db` with SQLite URI `mode=ro`.
  * No fabricated values — the snapshot only echoes the adapter's payload
    with a header banner and human-readable formatting.
  * Status labels in the rendered MD say READ ONLY, OBSERVATION ONLY,
    NO LIVE READINESS CLAIM, NO STRATEGY APPROVAL, and
    NO BROKER / NO ORDER / NO OPTIMIZATION verbatim.

CLI:
    python tools/export_journal_snapshot.py
    python tools/export_journal_snapshot.py --reports-dir <dir>

Programmatic:
    from tools.export_journal_snapshot import export_snapshot
    json_path, md_path = export_snapshot(reports_dir)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Project root must be importable when invoked as a script.
_BASE = Path(__file__).resolve().parents[1]
if str(_BASE) not in sys.path:
    sys.path.insert(0, str(_BASE))

from tools.trade_journal_adapter import load_payload  # noqa: E402


_DEFAULT_REPORTS_DIR = _BASE / "reports"
_FILE_PREFIX = "journal_snapshot_"

_HEADER_BANNER = (
    "READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · "
    "NO STRATEGY APPROVAL · NO BROKER / NO ORDER / NO OPTIMIZATION"
)


# ── helpers ─────────────────────────────────────────────────────────────────

def _utc_filename_stamp(now_utc: datetime) -> str:
    return now_utc.strftime("%Y%m%dT%H%M%SZ")


def _fmt(value: Any, dash: str = "—") -> str:
    if value is None or value == "":
        return dash
    return str(value)


def _md_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "_no rows_\n"
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = "\n".join("| " + " | ".join(_fmt(c) for c in r) + " |" for r in rows)
    return "\n".join([head, sep, body]) + "\n"


def _section_header(title: str, status: str | None) -> str:
    if status:
        return f"## {title} — {status}"
    return f"## {title}"


# ── markdown renderer ───────────────────────────────────────────────────────

def render_markdown(payload: dict[str, Any], now_utc: datetime) -> str:
    lines: list[str] = []

    # --- top header + banner ---------------------------------------------
    lines.append("# SPARTA Trade Intelligence Journal — Snapshot")
    lines.append("")
    lines.append(f"**Generated (UTC):** {now_utc.isoformat()}")
    lines.append(f"**Adapter status:** {payload.get('status', 'UNKNOWN')}")
    summary = payload.get("summary") or {}
    lines.append(f"**Data source:** {summary.get('source', 'unknown')}")
    lines.append(f"**External root:** `{payload.get('external_root', '')}`")
    lines.append("")
    lines.append(f"> {_HEADER_BANNER}")
    lines.append("")

    # --- posture ----------------------------------------------------------
    posture = payload.get("posture") or {}
    lines.append("## Posture")
    lines.append("")
    lines.append(_md_table(
        ["Field", "Value"],
        sorted(([k, v] for k, v in posture.items()), key=lambda r: r[0]),
    ))

    # --- summary ----------------------------------------------------------
    lines.append("## Summary")
    lines.append("")
    lines.append(_md_table(
        ["Metric", "Value"],
        [
            ["Trades total",  summary.get("trade_count")],
            ["Closed",        summary.get("closed_trade_count")],
            ["Open",          summary.get("open_trade_count")],
            ["Strategies",    summary.get("strategy_count")],
            ["Symbols",       summary.get("symbol_count")],
            ["Data source",   summary.get("source")],
        ],
    ))

    # --- evidence quality -------------------------------------------------
    eq = payload.get("evidence_quality") or {}
    lines.append(_section_header("Evidence Quality", eq.get("final_state", "MISSING")))
    lines.append("")
    for r in (eq.get("final_state_reason") or []):
        lines.append(f"- {r}")
    if eq.get("final_state_reason"):
        lines.append("")
    lines.append(_md_table(
        ["Check", "Label", "Status", "Detail"],
        [
            [c.get("name"), c.get("label"), c.get("status"), c.get("detail")]
            for c in (eq.get("checks") or [])
        ],
    ))
    thr = eq.get("thresholds") or {}
    if thr:
        lines.append(
            f"_Thresholds: per-strategy min closed = {thr.get('per_strategy_min_closed')}; "
            f"Monte Carlo min closed = {thr.get('monte_carlo_min_trades')}; "
            f"Risk-of-ruin min closed = {thr.get('risk_of_ruin_min_trades')}; "
            f"Daily correlation min unique close-days = {thr.get('daily_correlation_min_days')}; "
            f"Observation-only ceiling = {thr.get('observation_total_closed')} total closed trades._"
        )
        lines.append("")

    # --- strategy scorecard ----------------------------------------------
    lines.append("## Strategy Scorecard")
    lines.append("")
    lines.append(_md_table(
        ["Strategy", "Closed", "Win rate", "Expectancy R",
         "Profit factor", "Data quality"],
        [
            [
                row.get("strategy"), row.get("closed_trades"),
                row.get("win_rate"), row.get("expectancy_R"),
                row.get("profit_factor"), row.get("data_quality"),
            ]
            for row in (payload.get("scorecards") or [])
        ],
    ))

    # --- symbol performance ----------------------------------------------
    lines.append("## Symbol Performance")
    lines.append("")
    lines.append(_md_table(
        ["Symbol", "Best strategy", "Worst strategy",
         "Exposure attempts", "Blocked attempts", "Open lock"],
        [
            [
                row.get("symbol"), row.get("best_strategy"),
                row.get("worst_strategy"), row.get("total_exposure_attempts"),
                row.get("blocked_attempts"),
                "yes" if row.get("open_lock") else "no",
            ]
            for row in (payload.get("symbol_metrics") or [])
        ],
    ))

    # --- daily correlation -----------------------------------------------
    corr = payload.get("daily_pnl_correlation") or {}
    lines.append(_section_header("Daily P&L Correlation",
                                 corr.get("status", "MISSING")))
    lines.append("")
    if corr.get("status") == "OK":
        strats = corr.get("strategies") or []
        matrix_rows = []
        for row in (corr.get("matrix") or []):
            matrix_rows.append(
                [row.get("strategy"),
                 *[_fmt(v) for v in (row.get("values") or [])]]
            )
        lines.append(_md_table(["", *strats], matrix_rows))
        lines.append(f"_unique close-days: {corr.get('day_count')}_")
    else:
        lines.append(f"_reason: {corr.get('reason', '—')}_")
    lines.append("")

    # --- monte carlo ------------------------------------------------------
    mc = payload.get("monte_carlo_summary") or {}
    lines.append(_section_header("Monte Carlo Summary",
                                 mc.get("status", "MISSING")))
    lines.append("")
    if mc.get("status") == "OK":
        lines.append(_md_table(
            ["Metric", "p5", "p50", "p95"],
            [
                ["Final equity (R)",
                 mc.get("final_R_p5"), mc.get("final_R_p50"), mc.get("final_R_p95")],
                ["Max drawdown (R)",
                 mc.get("max_dd_R_p5"), mc.get("max_dd_R_p50"), mc.get("max_dd_R_p95")],
            ],
        ))
        lines.append(
            f"_runs={mc.get('runs')}, trade_count={mc.get('trade_count')}, "
            f"method={mc.get('method')}_"
        )
    else:
        lines.append(f"_reason: {mc.get('reason', '—')}_")
    lines.append("")

    # --- risk of ruin -----------------------------------------------------
    ror = payload.get("risk_of_ruin") or {}
    lines.append(_section_header("Risk of Ruin", ror.get("status", "MISSING")))
    lines.append("")
    if ror.get("status") == "OK":
        lines.append(f"- **Risk of ruin:** {ror.get('risk_of_ruin_pct')}%")
        lines.append(f"- Method: {ror.get('method')}")
        lines.append(
            f"- Runs: {ror.get('runs')}, path length: {ror.get('path_length')}"
        )
        lines.append(
            f"- Risk per trade: {ror.get('risk_pct_per_trade')}%, "
            f"ruin drawdown: {ror.get('ruin_drawdown_pct')}%"
        )
        lines.append(f"- Trades sampled: {ror.get('trade_count')}")
    else:
        lines.append(f"_reason: {ror.get('reason', '—')}_")
    lines.append("")

    # --- weekday performance ---------------------------------------------
    wd = payload.get("weekday_performance") or {}
    lines.append(_section_header("Weekday Performance",
                                 wd.get("status", "MISSING")))
    lines.append("")
    if wd.get("status") == "OK":
        lines.append(_md_table(
            ["Weekday", "Trades", "Avg R", "Win rate", "Sum R"],
            [
                [r.get("label"), r.get("trades"), r.get("avg_R"),
                 r.get("win_rate"), r.get("sum_R")]
                for r in (wd.get("rows") or [])
            ],
        ))
    else:
        lines.append(f"_reason: {wd.get('reason', '—')}_")
    lines.append("")

    # --- month performance -----------------------------------------------
    m = payload.get("month_performance") or {}
    lines.append(_section_header("Month Performance",
                                 m.get("status", "MISSING")))
    lines.append("")
    if m.get("status") == "OK":
        lines.append(_md_table(
            ["Month", "Trades", "Avg R", "Win rate", "Sum R"],
            [
                [r.get("label"), r.get("trades"), r.get("avg_R"),
                 r.get("win_rate"), r.get("sum_R")]
                for r in (m.get("rows") or [])
            ],
        ))
    else:
        lines.append(f"_reason: {m.get('reason', '—')}_")
    lines.append("")

    # --- unified gate strip ----------------------------------------------
    gates = payload.get("gates") or []
    lines.append("## Unified Gate Strip")
    lines.append("")
    lines.append(_md_table(
        ["Gate", "Status", "Detail"],
        [[g.get("name"), g.get("status"), g.get("detail")] for g in gates],
    ))

    # --- missing & errors ------------------------------------------------
    missing = payload.get("missing") or []
    errors = payload.get("errors") or []
    lines.append("## Missing Data & Warnings")
    lines.append("")
    if not missing and not errors:
        lines.append("_no missing-data flags or errors reported_")
    if missing:
        lines.append("**Missing inputs:**")
        for entry in missing:
            lines.append(f"- {entry}")
    if errors:
        lines.append("")
        lines.append("**Errors (fail-closed; nothing fabricated):**")
        for entry in errors:
            lines.append(f"- {entry}")

    # --- footer banner ---------------------------------------------------
    lines.append("")
    lines.append("---")
    lines.append(f"_{_HEADER_BANNER}_")
    lines.append("")
    lines.append(
        "_End of snapshot. Read-only export. No execution surface. "
        "No broker connection. No order placement. No strategy logic change._"
    )

    return "\n".join(lines) + "\n"


# ── core ────────────────────────────────────────────────────────────────────

def export_snapshot(
    reports_dir: Path,
    payload: dict[str, Any] | None = None,
    now_utc: datetime | None = None,
) -> tuple[Path, Path]:
    """Write the JSON + MD snapshot pair into `reports_dir`.

    Returns `(json_path, md_path)`. Never writes outside `reports_dir`.
    `payload` defaults to a freshly loaded adapter payload; `now_utc`
    defaults to `datetime.now(timezone.utc)`.
    """
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    if payload is None:
        payload = load_payload()
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    # Add snapshot-level metadata without mutating the caller's dict.
    snapshot = dict(payload)
    snapshot["snapshot_generated_at_utc"] = now_utc.isoformat()
    snapshot["snapshot_banner"] = _HEADER_BANNER

    stamp = _utc_filename_stamp(now_utc)
    json_path = reports_dir / f"{_FILE_PREFIX}{stamp}.json"
    md_path = reports_dir / f"{_FILE_PREFIX}{stamp}.md"

    json_path.write_text(
        json.dumps(snapshot, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )
    md_path.write_text(render_markdown(snapshot, now_utc), encoding="utf-8")
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only snapshot exporter for the SPARTA Trade Intelligence "
            "Journal. Writes a timestamped JSON + Markdown pair."
        ),
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=_DEFAULT_REPORTS_DIR,
        help=f"Output directory (default: {_DEFAULT_REPORTS_DIR})",
    )
    args = parser.parse_args(argv)
    json_path, md_path = export_snapshot(args.reports_dir)
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
