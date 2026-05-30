"""Synthetic end-to-end validation-factory smoke demo (Factory-D10).

Wires every factory ladder module together on FAKE in-memory data to prove the
plumbing connects safely -- it is a connectivity demo, NOT a research result. It
fabricates bars, fabricates trades through a fake strategy callable, and walks the
whole ladder: in-sample baseline -> out-of-sample protocol + one-shot run ->
entry significance -> sequence risk -> regime -> walk-forward -> friction -> final
decision, writing each module's standard report into its own sub-folder.

It proves nothing about any real strategy. Every number here is synthetic. The
final readiness it derives is therefore a conservative research-tier disposition
only; this demo can never lift a candidate to any operational tier.

OFFLINE / INERT: Python standard library only (os, datetime, typing) plus the
sibling factory modules. It opens no connection, spawns no child process, fetches
no data, runs no shell or version-control call, reads no real market data, imports
no real strategy, and does NO dynamic code loading. The only files it writes are
report.json / report.md, and ONLY beneath the explicit output_dir it is given.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Sequence

from engine import validation_reports
from engine import validation_is_runner
from engine import validation_oos_runner
from engine import validation_entry_significance
from engine import validation_sequence_risk
from engine import validation_regime
from engine import validation_walk_forward
from engine import validation_friction
from engine import validation_decision


# A clearly-fake, valid-looking pre-registered protocol id (not a real hash).
SYNTHETIC_PROTOCOL_COMMIT = "SYNTHETIC_PROTOCOL_COMMIT_0000001"
SYNTHETIC_ENGINE_COMMIT = "SYNTHETIC_ENGINE_COMMIT_0000001"
# Fixed, obviously-synthetic timestamp so repeated runs are byte-stable.
SYNTH_UTC = "2099-01-01T00:00:00+00:00"

IS_YEARS: List[int] = list(range(2013, 2023))
OOS_YEARS: List[int] = [2023, 2024, 2025]
_BARS_PER_YEAR = 30
_TRADE_STEP = 5
# A net-positive, well-spread R pattern (avg 0.25R/trade) so the synthetic chain
# exercises the healthy branch of each verdict map deterministically.
_R_CYCLE = (0.5, 0.3, -0.2, 0.6, 0.4, -0.1, 0.5, 0.3)

# The sub-folders / module ids the smoke produces, in ladder order.
EXPECTED_MODULES: List[str] = [
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


def _make_bars_for_years(years: Sequence[int]) -> List[Dict[str, Any]]:
    """Build simple in-memory OHLCV bars (with an ATR proxy) across `years`."""
    bars: List[Dict[str, Any]] = []
    g = 0
    for year in years:
        for i in range(_BARS_PER_YEAR):
            month = 1 + (i // 3)        # 1..10
            day = 1 + (i % 27)          # 1..27 (always a valid date)
            close = 100.0 + 0.1 * g + (g % 5) * 0.05
            bars.append({
                "timestamp": datetime(int(year), month, day),
                "open": close,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000.0,
                "atr20": 1.0 + float(g % 3),   # cycles 1/2/3 -> low/mid/high regimes
            })
            g += 1
    return bars


def make_synthetic_bars() -> Dict[str, List[Dict[str, Any]]]:
    """Return fake IS (2013-2022) and OOS (2023-2025) bars, in memory only."""
    return {
        "is": _make_bars_for_years(IS_YEARS),
        "oos": _make_bars_for_years(OOS_YEARS),
    }


def synthetic_strategy_runner(bars: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """A FAKE, deterministic strategy callable: emits one trade every few bars.

    It contains no real entry/exit logic and reads no files -- it only maps bar
    positions to a fixed R pattern so the runner plumbing can be exercised. Given
    the same bars it always returns identical trades.
    """
    trades: List[Dict[str, Any]] = []
    k = 0
    for i in range(0, len(bars), _TRADE_STEP):
        bar = bars[i]
        trades.append({
            "r_multiple": _R_CYCLE[k % len(_R_CYCLE)],
            "entry_index": i,
            "exit_index": min(i + _TRADE_STEP, len(bars) - 1),
            "year": int(bar["timestamp"].year),
            "entry_date": bar["timestamp"].date().isoformat(),
        })
        k += 1
    return trades


def make_synthetic_trades() -> Dict[str, List[Dict[str, Any]]]:
    """Return the fake IS and OOS trade lists the synthetic runner produces."""
    bars = make_synthetic_bars()
    return {
        "is": synthetic_strategy_runner(bars["is"]),
        "oos": synthetic_strategy_runner(bars["oos"]),
    }


def _verdict_from_total(total_r: float, positive: str, negative: str) -> str:
    return positive if float(total_r) > 0 else negative


def run_synthetic_validation_smoke(output_dir: str) -> Dict[str, Any]:
    """Run the whole ladder on synthetic data and write one report per module.

    Returns a manifest dict: the module list, the written report paths, the
    per-module verdicts, and the derived (conservative) research decision +
    readiness level. Refuses an empty output_dir; writes nothing outside it.
    """
    if not output_dir or not str(output_dir).strip():
        raise ValueError("run_synthetic_validation_smoke requires a non-empty output_dir")

    bars = make_synthetic_bars()
    is_bars, oos_bars = bars["is"], bars["oos"]

    paths: Dict[str, Dict[str, str]] = {}
    verdicts: Dict[str, str] = {}

    def _emit(name: str, report: Dict[str, Any]) -> None:
        paths[name] = validation_reports.write_report(
            report, os.path.join(output_dir, name)
        )

    # 1 -- in-sample baseline.
    is_run = validation_is_runner.run_is_baseline(
        synthetic_strategy_runner, is_bars, metadata={"is_years": IS_YEARS}
    )
    is_metrics = is_run["metrics"]
    is_trades = is_run["trades"]
    verdicts["is_baseline"] = _verdict_from_total(
        is_metrics["total_r"], "IS_CONTINUE", "IS_FAIL"
    )
    _emit("is_baseline", validation_is_runner.build_is_report(
        branch_id="SYNTH",
        module_id="is_baseline",
        title="Synthetic IS baseline (demo)",
        verdict=verdicts["is_baseline"],
        metrics=is_metrics,
        input_files=["synthetic_is_2013_2022.jsonl"],
        data_window={"is_years": IS_YEARS},
        frozen_parameters={"strategy": "synthetic_demo", "trade_step": _TRADE_STEP},
        source_commits={"engine": SYNTHETIC_ENGINE_COMMIT},
        created_utc=SYNTH_UTC,
    ))

    # 2 -- pre-registered out-of-sample protocol (a registration, not a verdict).
    verdicts["oos_protocol"] = "PROTOCOL_REGISTERED"
    _emit("oos_protocol", validation_oos_runner.build_oos_protocol_report(
        branch_id="SYNTH",
        title="Synthetic OOS protocol (demo)",
        criteria={"min_total_r": 0.0, "note": "synthetic pass/watch/fail criteria"},
        protocol_rules=["one_shot", "no_peek_before_commit"],
        input_files=["synthetic_oos_2023_2025.jsonl"],
        data_window={"oos_years": OOS_YEARS},
        source_commits={"engine": SYNTHETIC_ENGINE_COMMIT},
        created_utc=SYNTH_UTC,
    ))

    # 3 -- one-shot OOS run, bound to the (fake) protocol commit.
    oos_run = validation_oos_runner.run_oos_baseline(
        synthetic_strategy_runner, oos_bars, metadata={
            "protocol_commit": SYNTHETIC_PROTOCOL_COMMIT,
            "oos_years": OOS_YEARS,
            "input_files": ["synthetic_oos_2023_2025.jsonl"],
        },
    )
    oos_metrics = oos_run["metrics"]
    verdicts["oos_run"] = _verdict_from_total(oos_metrics["total_r"], "PASS", "FAIL")
    _emit("oos_run", validation_oos_runner.build_oos_result_report(
        branch_id="SYNTH",
        title="Synthetic OOS one-shot run (demo)",
        verdict=verdicts["oos_run"],
        metrics=oos_metrics,
        protocol_commit=SYNTHETIC_PROTOCOL_COMMIT,
        input_files=["synthetic_oos_2023_2025.jsonl"],
        data_window={"oos_years": OOS_YEARS},
        created_utc=SYNTH_UTC,
    ))

    # 4 -- entry significance over a small fixed horizon set (fast, seeded).
    signal_indices = [t["entry_index"] for t in is_trades]
    es_results = validation_entry_significance.run_entry_significance(
        is_bars, signal_indices, horizons=(5, 10), n_iter=100, seed=0, label="IS",
    )
    verdicts["entry_significance"] = validation_entry_significance.derive_entry_verdict(
        es_results
    )
    _emit("entry_significance", validation_entry_significance.build_entry_significance_report(
        branch_id="SYNTH",
        title="Synthetic entry significance (demo)",
        results=es_results,
        input_files=["synthetic_is_2013_2022.jsonl"],
        data_window={"is_years": IS_YEARS},
        created_utc=SYNTH_UTC,
    ))

    # 5 -- sequence risk on the IS trade R-multiples.
    seq_summary = validation_sequence_risk.run_sequence_risk(
        is_trades, n_iter=200, seed=0
    )
    verdicts["sequence_risk"] = seq_summary["verdict"]
    _emit("sequence_risk", validation_sequence_risk.build_sequence_risk_report(
        branch_id="SYNTH",
        title="Synthetic sequence risk (demo)",
        summary=seq_summary,
        input_files=["synthetic_is_2013_2022.jsonl"],
        data_window={"is_years": IS_YEARS},
        created_utc=SYNTH_UTC,
    ))

    # 6 -- regime breakdown: classify IS bars, tag trades by entry regime.
    regimes = validation_regime.classify_volatility_regimes(is_bars)
    tagged = validation_regime.tag_trades_by_entry_regime(is_trades, regimes)
    regime_summary = validation_regime.summarize_by_regime(tagged)
    verdicts["regime"] = validation_regime.derive_regime_verdict(regime_summary)
    _emit("regime", validation_regime.build_regime_report(
        branch_id="SYNTH",
        title="Synthetic regime breakdown (demo)",
        summary=regime_summary,
        input_files=["synthetic_is_2013_2022.jsonl"],
        data_window={"is_years": IS_YEARS},
        created_utc=SYNTH_UTC,
    ))

    # 7 -- walk-forward stability across the IS years.
    wf_summary = validation_walk_forward.summarize_rolling_windows(
        is_trades, IS_YEARS[0], IS_YEARS[-1], 3
    )
    verdicts["walk_forward"] = validation_walk_forward.derive_walk_forward_verdict(
        wf_summary
    )
    _emit("walk_forward", validation_walk_forward.build_walk_forward_report(
        branch_id="SYNTH",
        title="Synthetic walk-forward (demo)",
        summary=wf_summary,
        input_files=["synthetic_is_2013_2022.jsonl"],
        data_window={"is_years": IS_YEARS},
        created_utc=SYNTH_UTC,
    ))

    # 8 -- friction / cost stress on the IS trade R-multiples.
    fr_summary = validation_friction.friction_scenarios(
        [t["r_multiple"] for t in is_trades]
    )
    verdicts["friction"] = validation_friction.derive_friction_verdict(fr_summary)
    _emit("friction", validation_friction.build_friction_report(
        branch_id="SYNTH",
        title="Synthetic friction stress (demo)",
        summary=fr_summary,
        input_files=["synthetic_is_2013_2022.jsonl"],
        data_window={"is_years": IS_YEARS},
        created_utc=SYNTH_UTC,
    ))

    # 9 -- final decision / readiness orchestration. The decision layer keys OOS
    #      under "oos"; the protocol registration is not a pass/fail input.
    decision_verdicts = {
        "is_baseline": verdicts["is_baseline"],
        "oos": verdicts["oos_run"],
        "entry_significance": verdicts["entry_significance"],
        "sequence_risk": verdicts["sequence_risk"],
        "regime": verdicts["regime"],
        "walk_forward": verdicts["walk_forward"],
        "friction": verdicts["friction"],
    }
    decision_report = validation_decision.build_decision_report(
        branch_id="SYNTH",
        title="Synthetic final decision (demo)",
        verdicts=decision_verdicts,
        created_utc=SYNTH_UTC,
    )
    verdicts["final_decision"] = decision_report["verdict"]
    _emit("final_decision", decision_report)

    return {
        "synthetic": True,
        "output_dir": output_dir,
        "modules": list(EXPECTED_MODULES),
        "paths": paths,
        "verdicts": verdicts,
        "research_decision": decision_report["metrics"]["research_decision"],
        "readiness_level": decision_report["metrics"]["readiness_level"],
    }
