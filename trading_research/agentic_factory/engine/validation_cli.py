"""Minimal safe command interface for the validation factory (Factory-D9).

A thin, static wrapper so future strategy branches can discover and demonstrate
the standard validation modules consistently. It does FOUR things only:

  * list-modules     -- name the supported ladder modules.
  * describe         -- print a module's purpose + required inputs (no execution).
  * synthetic-smoke  -- write ONE demo report from in-memory synthetic data, for
                        the safe summary/report modules only.
  * version          -- print the CLI version string.

It deliberately does NOT load strategies from arbitrary names, run a real
backtest, touch real in-sample / out-of-sample data, optimize, sweep parameters,
fetch data, or expose any paper / live / deploy command. Modules that need a real
strategy or real market data are describe-only here; there is no fake execution.

OFFLINE / INERT: Python standard library only (sys, typing) plus the in-repo
validation modules it wraps. It opens no network connection, spawns no child
process, fetches no data, runs no shell or version-control call, reads no real
market data, and does NO dynamic code loading. The only files it ever writes are
report.json / report.md, and ONLY into the explicit --output-dir a caller passes
to synthetic-smoke.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

from engine import validation_reports
from engine import validation_sequence_risk
from engine import validation_regime
from engine import validation_walk_forward
from engine import validation_friction
from engine import validation_decision


CLI_VERSION = "sparta-validation-factory-cli 0.9.0 (research-only, offline)"

# Fixed timestamp for the synthetic demos so repeated smokes are deterministic.
_DEMO_UTC = "2026-05-30T00:00:00+00:00"

# Ladder modules the CLI knows about (Factory-D1 order).
SUPPORTED_MODULES: List[str] = [
    "report_schema",
    "is_baseline",
    "oos_protocol",
    "oos_run",
    "entry_significance",
    "sequence_risk",
    "regime",
    "walk_forward",
    "friction",
    "final_decision",
]

# Modules that can be demonstrated safely with synthetic in-memory data. The rest
# need a real strategy or real IS/OOS market data and are describe-only here.
SMOKE_SUPPORTED = {
    "report_schema",
    "sequence_risk",
    "regime",
    "walk_forward",
    "friction",
    "final_decision",
}

# module -> (short description, required real inputs).
MODULE_INFO: Dict[str, Tuple[str, str]] = {
    "report_schema": (
        "Standard validation report schema + writer.",
        "none (schema demo only)",
    ),
    "is_baseline": (
        "In-sample baseline metrics gate.",
        "real in-sample bars -- describe only, no execution here",
    ),
    "oos_protocol": (
        "One-shot out-of-sample protocol guard.",
        "frozen in-sample spec + an out-of-sample window -- describe only",
    ),
    "oos_run": (
        "One-shot out-of-sample evaluation.",
        "frozen strategy + out-of-sample bars -- describe only",
    ),
    "entry_significance": (
        "Entry-edge statistical significance vs a null model.",
        "already-produced trades + a null model -- describe only",
    ),
    "sequence_risk": (
        "Trade-order shuffle + bootstrap sequence-risk battery.",
        "a list of R-multiples (or trade dicts)",
    ),
    "regime": (
        "Per-regime concentration breakdown.",
        "regime-tagged trades",
    ),
    "walk_forward": (
        "Rolling-window stability across years.",
        "year-tagged trades + a year range + a window size",
    ),
    "friction": (
        "Per-trade cost / slippage stress ladder.",
        "a list of R-multiples",
    ),
    "final_decision": (
        "Readiness + research-decision orchestration.",
        "a per-module verdict dict (+ optional context metrics)",
    ),
}


def _print_help() -> None:
    print("SPARTA validation factory CLI -- research-only, offline.")
    print("")
    print("Usage: validation_cli <command> [options]")
    print("")
    print("Commands:")
    print("  list-modules                  list the supported validation modules")
    print("  describe --module M           show a module's purpose + required inputs")
    print("  synthetic-smoke --module M --output-dir DIR")
    print("                                write a synthetic-data demo report (safe modules only)")
    print("  version                       print the CLI version string")
    print("")
    print("Safety: no optimization, no parameter sweeps, no data fetch, no paper/live,")
    print("        no execution or external API. Synthetic/demo data only.")


def _get_opt(args: Sequence[str], name: str) -> Optional[str]:
    """Return the value of a `--name VALUE` or `--name=VALUE` option, else None."""
    for i, a in enumerate(args):
        if a == name:
            if i + 1 < len(args):
                return args[i + 1]
            return None
        if a.startswith(name + "="):
            return a.split("=", 1)[1]
    return None


def _cmd_list_modules() -> int:
    for m in SUPPORTED_MODULES:
        print(m)
    return 0


def _cmd_describe(args: Sequence[str]) -> int:
    module = _get_opt(args, "--module")
    if not module:
        print("error: describe requires --module MODULE", file=sys.stderr)
        return 2
    if module not in MODULE_INFO:
        print(f"error: unknown module: {module}", file=sys.stderr)
        return 2
    desc, inputs = MODULE_INFO[module]
    if module in SMOKE_SUPPORTED:
        smoke = "yes (synthetic in-memory demo)"
    else:
        smoke = "no (describe only; needs a real strategy/data)"
    print(f"module: {module}")
    print(f"description: {desc}")
    print(f"required inputs: {inputs}")
    print(f"synthetic-smoke available: {smoke}")
    return 0


def _build_demo_report(module: str) -> Dict[str, Any]:
    """Assemble ONE validation report for a safe module from synthetic data."""
    if module == "report_schema":
        return validation_reports.make_report(
            branch_id="DEMO",
            module_id="report_schema",
            title="Synthetic report-schema demo",
            status="COMPLETE",
            verdict="SCHEMA_DEMO_OK",
            created_utc=_DEMO_UTC,
            next_allowed_step="human_review",
            notes=["synthetic demo only; no strategy, no data"],
        )
    if module == "sequence_risk":
        summary = validation_sequence_risk.run_sequence_risk(
            [1.0, -1.0, 2.0, -1.0, 1.5, -0.5, 0.8, -0.7, 1.2, -0.6],
            n_iter=200,
            seed=0,
        )
        return validation_sequence_risk.build_sequence_risk_report(
            branch_id="DEMO",
            title="Synthetic sequence-risk demo",
            summary=summary,
            created_utc=_DEMO_UTC,
        )
    if module == "regime":
        trades = [
            {"regime": "low", "r_multiple": 1.0},
            {"regime": "low", "r_multiple": -0.5},
            {"regime": "mid", "r_multiple": 0.8},
            {"regime": "high", "r_multiple": -1.0},
            {"regime": "high", "r_multiple": 1.5},
        ]
        summary = validation_regime.summarize_by_regime(trades)
        return validation_regime.build_regime_report(
            branch_id="DEMO",
            title="Synthetic regime demo",
            summary=summary,
            created_utc=_DEMO_UTC,
        )
    if module == "walk_forward":
        trades = [{"year": y, "r_multiple": 1.0} for y in range(2013, 2023)]
        summary = validation_walk_forward.summarize_rolling_windows(
            trades, 2013, 2022, 3
        )
        return validation_walk_forward.build_walk_forward_report(
            branch_id="DEMO",
            title="Synthetic walk-forward demo",
            summary=summary,
            created_utc=_DEMO_UTC,
        )
    if module == "friction":
        summary = validation_friction.friction_scenarios([1.0, 1.0, -0.5, 0.5])
        return validation_friction.build_friction_report(
            branch_id="DEMO",
            title="Synthetic friction demo",
            summary=summary,
            created_utc=_DEMO_UTC,
        )
    if module == "final_decision":
        verdicts = {
            "is_baseline": "IS_CONTINUE",
            "oos": "PASS",
            "entry_significance": "ENTRY_EDGE_SUPPORTED",
            "sequence_risk": "SEQUENCE_RISK_ACCEPTABLE",
            "regime": "REGIME_RISK_ACCEPTABLE",
            "walk_forward": "WALK_FORWARD_STABLE",
            "friction": "FRICTION_ROBUST",
        }
        return validation_decision.build_decision_report(
            branch_id="DEMO",
            title="Synthetic final-decision demo",
            verdicts=verdicts,
            created_utc=_DEMO_UTC,
        )
    raise ValueError(f"no synthetic demo for module: {module}")


def _cmd_synthetic_smoke(args: Sequence[str]) -> int:
    module = _get_opt(args, "--module")
    output_dir = _get_opt(args, "--output-dir")
    if not module:
        print("error: synthetic-smoke requires --module MODULE", file=sys.stderr)
        return 2
    if module not in MODULE_INFO:
        print(f"error: unknown module: {module}", file=sys.stderr)
        return 2
    if module not in SMOKE_SUPPORTED:
        print(
            f"error: module '{module}' needs a real strategy/data; it is "
            "describe-only, no synthetic smoke",
            file=sys.stderr,
        )
        return 2
    if not output_dir or not output_dir.strip():
        print(
            "error: synthetic-smoke requires --output-dir DIR", file=sys.stderr
        )
        return 2
    report = _build_demo_report(module)
    paths = validation_reports.write_report(report, output_dir)
    print(f"wrote {paths['report_json']}")
    print(f"wrote {paths['report_md']}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Parse a single command and dispatch. Returns a process exit code."""
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        _print_help()
        return 2
    cmd, rest = args[0], args[1:]
    if cmd in ("-h", "--help", "help"):
        _print_help()
        return 0
    if cmd == "version":
        print(CLI_VERSION)
        return 0
    if cmd == "list-modules":
        return _cmd_list_modules()
    if cmd == "describe":
        return _cmd_describe(rest)
    if cmd == "synthetic-smoke":
        return _cmd_synthetic_smoke(rest)
    print(f"error: unsupported command: {cmd}", file=sys.stderr)
    _print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
