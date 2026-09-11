"""Read-only daily frozen-stack evidence cycle for SPARTA Brain.

This orchestrator runs the paper-only frozen stack, refreshes validation
and read-only intelligence reports, and appends a local evidence snapshot.
It never touches live execution or trading logic.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .daily_profit_brain_runner import refresh_daily_profit_brain
from .frozen_stack_regime_intelligence import refresh_frozen_stack_market_regime_intelligence
from .memory import DATA_DIR, ROOT, write_json
from .reports import build_report, generate_daily_report
from .commander import dashboard_summary

EXTERNAL_ROOT = Path(r"C:\Users\mahmo\obsidian-trade-logger")
EXTERNAL_SCRIPT = EXTERNAL_ROOT / "scripts" / "frozen_stack_paper_bot.py"
EXTERNAL_VALIDATION_MODULE = "analytics.final_stack_operational_validation"

OUT_JSON = ROOT / "reports" / "frozen_stack_daily_evidence_cycle.json"
OUT_MD = ROOT / "reports" / "frozen_stack_daily_evidence_cycle.md"
SNAPSHOT_PATH = DATA_DIR / "frozen_stack_daily_evidence_cycle.jsonl"
LOG_ROOT = ROOT / "logs" / "frozen_stack_daily_evidence_cycle"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=False))
        handle.write("\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except Exception:
                continue
            if isinstance(item, dict):
                rows.append(item)
    except Exception:
        return []
    return rows


def _write_step_log(step_dir: Path, step_name: str, payload: dict[str, Any]) -> Path:
    step_dir.mkdir(parents=True, exist_ok=True)
    path = step_dir / f"{step_name}.json"
    write_json(path, payload)
    return path


def _run_subprocess(command: list[str], cwd: Path, log_dir: Path, step_name: str) -> dict[str, Any]:
    log_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True)
    result = {
        "step": step_name,
        "command": command,
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout": proc.stdout[-8000:],
        "stderr": proc.stderr[-8000:],
        "status": "OK" if proc.returncode == 0 else "FAILED",
    }
    if proc.returncode != 0 and "ModuleNotFoundError: No module named 'pandas'" in proc.stderr:
        result["status"] = "MISSING_DEPENDENCY"
        result["missing_dependency"] = "pandas"
    _write_step_log(log_dir, step_name, result)
    return result


def _paper_bot_step(
    external_root: Path = EXTERNAL_ROOT,
    step_dir: Path | None = None,
    runner: Callable[[list[str], Path, Path, str], dict[str, Any]] = _run_subprocess,
) -> dict[str, Any]:
    step_dir = step_dir or (LOG_ROOT / utc_now().replace(":", "-"))
    if not EXTERNAL_SCRIPT.exists():
        result = {
            "step": "paper_bot",
            "status": "MISSING_REPORT",
            "error": "frozen_stack_paper_bot.py not found",
            "paper_only": True,
            "no_live_execution": True,
        }
        _write_step_log(step_dir, "paper_bot", result)
        return result
    command = [sys.executable, str(EXTERNAL_SCRIPT)]
    result = runner(command, external_root, step_dir, "paper_bot")
    result["paper_only"] = True
    result["no_live_execution"] = True
    return result


FRESHNESS_SYMBOLS = ("BTCUSDT", "ETHUSDT", "XRPUSDT")
FRESHNESS_MAX_AGE_DAYS = 45  # monthly zips: a healthy cache is at most ~one month behind


def _data_freshness_step(
    external_root: Path = EXTERNAL_ROOT,
    step_dir: Path | None = None,
    today: datetime | None = None,
) -> dict[str, Any]:
    """Read-only check that the paper bot's Binance 15m cache is not stale.

    The frozen stack loads monthly zips from ``data/binance_cache/<SYMBOL>/YYYY-MM.zip``.
    Between 2026-03 and 2026-09 that cache silently stopped at March while the paper
    bot kept reporting OK with zero appended rows. This step names the last cached
    month per symbol and flags STALE_DATA when the newest month is older than
    FRESHNESS_MAX_AGE_DAYS, so the cycle can never again call dormant data "OK".
    """
    step_dir = step_dir or (LOG_ROOT / utc_now().replace(":", "-"))
    now = today or datetime.now(timezone.utc)
    cache_root = external_root / "data" / "binance_cache"
    per_symbol: dict[str, Any] = {}
    ages: list[int] = []
    # The paper bot's daily loader aggregates the 1m cache (<SYMBOL>_1m/); the 15m cache
    # (<SYMBOL>/) feeds older backtests. Check both; the 1m one is the one that matters.
    cache_keys = [f"{s}_1m" for s in FRESHNESS_SYMBOLS] + list(FRESHNESS_SYMBOLS)
    for symbol in cache_keys:
        months = sorted(
            p.stem for p in (cache_root / symbol).glob("????-??.zip")
        ) if (cache_root / symbol).exists() else []
        if not months:
            per_symbol[symbol] = {"last_month": None, "age_days": None, "status": "MISSING"}
            continue
        year, month = (int(x) for x in months[-1].split("-"))
        # last bar of a monthly zip = last day of that month
        if month == 12:
            month_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            month_end = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        age = (now - month_end).days
        ages.append(age)
        per_symbol[symbol] = {
            "last_month": months[-1],
            "age_days": age,
            "status": "OK" if age <= FRESHNESS_MAX_AGE_DAYS else "STALE_DATA",
        }
    missing_1m = [k for k, v in per_symbol.items() if k.endswith("_1m") and v["status"] == "MISSING"]
    if not ages:
        status = "MISSING"
    elif missing_1m or max(ages) > FRESHNESS_MAX_AGE_DAYS:
        status = "STALE_DATA"  # a missing 1m cache means the paper bot cannot see the market
    else:
        status = "OK"
    result = {
        "step": "data_freshness",
        "status": status,
        "cache_root": str(cache_root),
        "max_age_days_allowed": FRESHNESS_MAX_AGE_DAYS,
        "oldest_symbol_age_days": max(ages) if ages else None,
        "per_symbol": per_symbol,
        "read_only": True,
    }
    _write_step_log(step_dir, "data_freshness", result)
    return result


def _validation_step(
    external_root: Path = EXTERNAL_ROOT,
    step_dir: Path | None = None,
    runner: Callable[[list[str], Path, Path, str], dict[str, Any]] = _run_subprocess,
) -> dict[str, Any]:
    step_dir = step_dir or (LOG_ROOT / utc_now().replace(":", "-"))
    command = [
        sys.executable,
        "-c",
        (
            "from analytics.final_stack_operational_validation import generate_report; "
            "import json; "
            "rep = generate_report(paper_trade_source='data/final_stack_paper_trades.csv'); "
            "print(json.dumps({'global_verdict': rep.get('headline', {}).get('global_verdict'), 'n_paper_trades': rep.get('n_paper_trades')}))"
        ),
    ]
    if not (external_root / "analytics" / "final_stack_operational_validation.py").exists():
        result = {
            "step": "validation",
            "status": "MISSING_REPORT",
            "error": "final_stack_operational_validation.py not found",
        }
        _write_step_log(step_dir, "validation", result)
        return result
    result = runner(command, external_root, step_dir, "validation")
    return result


def _refresh_commander_summary(output_dir: Path | None = None) -> dict[str, Any]:
    report = generate_daily_report()
    summary = build_report()
    return {
        "step": "commander_summary",
        "status": "OK",
        "generated_report": report,
        "summary": summary,
        "output_path": str(output_dir or DATA_DIR),
    }


def _refresh_profit_brain(output_dir: Path | None = None, memory_dir: Path | None = None) -> dict[str, Any]:
    report = refresh_daily_profit_brain(output_dir=output_dir, memory_dir=memory_dir)
    return {
        "step": "profit_brain_refresh",
        "status": "OK",
        "reports": report.get("reports", {}),
        "snapshot_path": report.get("snapshot_path"),
        "gate_status": (report.get("decision_gate") or {}).get("gate_status"),
    }


def _refresh_frozen_stack_intelligence(
    external_validation_report: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    report = refresh_frozen_stack_market_regime_intelligence(
        validation_report_path=external_validation_report,
        output_dir=output_dir,
    )
    return {
        "step": "frozen_stack_intelligence",
        "status": "OK" if report.get("read_only") else "FAILED",
        "market_regime": report.get("market_regime", {}),
        "deployment_readiness": report.get("deployment_readiness", {}),
        "confidence_context": report.get("confidence_context", {}),
        "why_not_ready_reasons": report.get("why_not_ready_reasons", []),
        "validation_summary": report.get("validation_summary", {}),
        "outputs": report.get("outputs", {}),
    }


def _build_snapshot(steps: dict[str, Any], commander: dict[str, Any], profit_brain: dict[str, Any], intelligence: dict[str, Any]) -> dict[str, Any]:
    profit_brief = (profit_brain.get("generated_report") or {}).get("daily_profit_brief") or {}
    learning_status = (profit_brain.get("generated_report") or {}).get("summary", {}).get("status")
    intelligence_data = intelligence or {}
    return {
        "timestamp": utc_now(),
        "paper_bot_status": steps.get("paper_bot", {}).get("status"),
        "data_freshness_status": steps.get("data_freshness", {}).get("status", "UNKNOWN"),
        "data_oldest_symbol_age_days": steps.get("data_freshness", {}).get("oldest_symbol_age_days"),
        "validation_status": steps.get("validation", {}).get("status"),
        "frozen_stack_regime": intelligence_data.get("market_regime", {}).get("label", "INSUFFICIENT_DATA"),
        "deployment_readiness": intelligence_data.get("deployment_readiness", {}).get("status", "INSUFFICIENT_DATA"),
        "confidence_context_score": intelligence_data.get("confidence_context", {}).get("adjusted_confidence"),
        "profit_brain_gate_status": profit_brain.get("gate_status", "INSUFFICIENT_DATA"),
        "profit_brain_confidence_score": profit_brief.get("confidence_score"),
        "profit_brain_data_quality_score": profit_brief.get("data_quality_score"),
        "commander_overall_status": (commander.get("generated_report") or {}).get("overall_status", "unknown"),
        "learning_status": learning_status or "INSUFFICIENT_DATA",
        "why_not_ready_reasons": intelligence_data.get("why_not_ready_reasons") or [],
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Frozen-Stack Daily Evidence Cycle",
        "",
        f"- Generated: {report.get('generated_at')}",
        f"- Overall status: {report.get('overall_status')}",
        f"- Read-only: {report.get('read_only')}",
        "",
        "## Step Results",
    ]
    for step in report.get("steps") or []:
        lines.append(f"- {step.get('step')}: {step.get('status')}")
    lines.extend(
        [
            "",
            "## Snapshot",
        ]
    )
    snapshot = report.get("snapshot") or {}
    for key in [
        "paper_bot_status",
        "data_freshness_status",
        "data_oldest_symbol_age_days",
        "validation_status",
        "frozen_stack_regime",
        "deployment_readiness",
        "confidence_context_score",
        "profit_brain_gate_status",
        "profit_brain_confidence_score",
        "profit_brain_data_quality_score",
        "commander_overall_status",
        "learning_status",
    ]:
        lines.append(f"- {key}: {snapshot.get(key)}")
    reasons = snapshot.get("why_not_ready_reasons") or []
    if reasons:
        lines.append("")
        lines.append("## Why Not Ready")
        lines.extend(f"- {reason}" for reason in reasons)
    return "\n".join(lines) + "\n"


def run_frozen_stack_daily_evidence_cycle(
    external_root: Path = EXTERNAL_ROOT,
    reports_dir: Path | None = None,
    memory_dir: Path | None = None,
    log_root: Path | None = None,
    subprocess_runner: Callable[[list[str], Path, Path, str], dict[str, Any]] = _run_subprocess,
) -> dict[str, Any]:
    reports_dir = reports_dir or ROOT / "reports"
    memory_dir = memory_dir or DATA_DIR
    log_root = log_root or LOG_ROOT
    cycle_id = utc_now().replace(":", "-")
    step_dir = log_root / cycle_id

    step_results: list[dict[str, Any]] = []
    paper_bot = _paper_bot_step(external_root=external_root, step_dir=step_dir, runner=subprocess_runner)
    step_results.append(paper_bot)

    data_freshness = _data_freshness_step(external_root=external_root, step_dir=step_dir)
    step_results.append(data_freshness)

    validation = _validation_step(external_root=external_root, step_dir=step_dir, runner=subprocess_runner)
    step_results.append(validation)

    intelligence = _refresh_frozen_stack_intelligence(
        external_validation_report=external_root / "reports" / "final_stack_operational_validation.json",
        output_dir=reports_dir,
    )
    _write_step_log(step_dir, "frozen_stack_intelligence", intelligence)
    step_results.append(intelligence)

    profit_brain = _refresh_profit_brain(output_dir=reports_dir, memory_dir=memory_dir)
    _write_step_log(step_dir, "profit_brain_refresh", profit_brain)
    step_results.append(profit_brain)

    commander = _refresh_commander_summary(output_dir=reports_dir)
    _write_step_log(step_dir, "commander_summary", commander)
    step_results.append(commander)

    snapshot = _build_snapshot(
        {"paper_bot": paper_bot, "data_freshness": data_freshness, "validation": validation},
        commander,
        profit_brain,
        intelligence,
    )
    _append_jsonl(SNAPSHOT_PATH, snapshot)

    overall_status = "OK"
    if any(step.get("status") in {"FAILED", "MISSING_REPORT", "MISSING_DEPENDENCY", "STALE_DATA"} for step in step_results):
        overall_status = "PARTIAL"

    report = {
        "schema": "sparta_commander.frozen_stack_daily_evidence_cycle.v1",
        "generated_at": utc_now(),
        "read_only": True,
        "overall_status": overall_status,
        "steps": step_results,
        "snapshot": snapshot,
        "snapshot_path": str(SNAPSHOT_PATH),
        "log_root": str(step_dir),
        "reports": {
            "frozen_stack_market_regime_intelligence": str(reports_dir / "frozen_stack_market_regime_intelligence.json"),
            "frozen_stack_market_regime_intelligence_md": str(reports_dir / "frozen_stack_market_regime_intelligence.md"),
            "sparta_profit_brain": str(reports_dir / "sparta_profit_brain.json"),
            "sparta_profit_brain_md": str(reports_dir / "sparta_profit_brain.md"),
            "sparta_commander_report": str(DATA_DIR / "sparta_commander_report.json"),
        },
        "generated_reports": [
            str(reports_dir / "frozen_stack_market_regime_intelligence.json"),
            str(reports_dir / "frozen_stack_market_regime_intelligence.md"),
            str(reports_dir / "sparta_profit_brain.json"),
            str(reports_dir / "sparta_profit_brain.md"),
            str(DATA_DIR / "sparta_commander_report.json"),
            str(OUT_JSON),
            str(OUT_MD),
        ],
        "no_live_execution": True,
        "no_strategy_changes": True,
        "no_parameter_changes": True,
    }
    write_json(OUT_JSON, report)
    OUT_MD.write_text(_render_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    result = run_frozen_stack_daily_evidence_cycle()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
