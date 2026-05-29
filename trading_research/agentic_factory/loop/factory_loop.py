"""Local TraderDev-style orchestration loop.

OFFLINE / LOCAL-ONLY: wires the pieces together using local files only.

    proposer  ->  offline backtester  ->  metrics  ->  report  ->  decision

- Reads config from a local YAML file (optional; falls back to defaults).
- Reads market data from a local offline CSV only.
- Writes inert report files (json + md) into the local reports/ folder.

No network, no broker, no order placement, no signal to any live system,
no scheduler. Run it by hand when you want a research pass.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Make the sibling 'engine' package importable when run directly.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_MODULE_ROOT = os.path.dirname(_THIS_DIR)
if _MODULE_ROOT not in sys.path:
    sys.path.insert(0, _MODULE_ROOT)

from engine import backtester, metrics, decision, proposer  # noqa: E402


def _load_config(config_path: str) -> Dict[str, Any]:
    """Load YAML config if present and PyYAML is available; else defaults."""
    defaults = {
        "data": {"offline_csv": "data_offline/nq_orb_sample.csv", "timestamp_column": "timestamp"},
        "strategy": proposer.base_params(),
        "decision": decision.default_thresholds(),
        "reports": {"output_dir": "reports"},
    }
    if not os.path.exists(config_path):
        return defaults
    try:
        import yaml  # type: ignore
    except Exception:
        return defaults
    with open(config_path, "r", encoding="utf-8") as fh:
        loaded = yaml.safe_load(fh) or {}
    # Shallow-merge top-level keys onto defaults.
    merged = dict(defaults)
    merged.update(loaded)
    return merged


def _resolve(path: str) -> str:
    """Resolve a path relative to the module root if it is not absolute."""
    if os.path.isabs(path):
        return path
    return os.path.join(_MODULE_ROOT, path)


def run_once(
    config_path: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run a single propose -> backtest -> metrics -> report -> decide pass."""
    if config_path is None:
        config_path = os.path.join(_MODULE_ROOT, "config", "factory_config.yaml")
    cfg = _load_config(config_path)

    if params is None:
        # Start from base defaults, then overlay the config strategy block so
        # session_start, session_end, opening_range_minutes, etc. come from
        # factory_config.yaml rather than hard-coded defaults.
        params = proposer.base_params()
        params.update(cfg.get("strategy", {}) or {})

    csv_rel = cfg.get("data", {}).get("offline_csv", "data_offline/nq_orb_sample.csv")
    ts_col = cfg.get("data", {}).get("timestamp_column", "timestamp")
    csv_path = _resolve(csv_rel)

    if not os.path.exists(csv_path):
        return {
            "status": "no_data",
            "message": f"Offline CSV not found at {csv_path}. Drop a file in data_offline/.",
            "params": params,
        }

    bt = backtester.run_backtest(csv_path, params, timestamp_column=ts_col)
    summary = metrics.summarize(bt["r_multiples"])
    verdict = decision.decide(summary, cfg.get("decision"))

    result = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "strategy": "nq_orb",
        "params": params,
        "metrics": summary,
        "decision": verdict,
        "trade_count": int(summary.get("trade_count", 0)),
    }
    _write_report(cfg, result)
    return result


def _write_report(cfg: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Write inert json + md report files into the local reports folder."""
    out_dir = _resolve(cfg.get("reports", {}).get("output_dir", "reports"))
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(out_dir, f"nq_orb_run_{stamp}.json")
    md_path = os.path.join(out_dir, f"nq_orb_run_{stamp}.md")

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)

    m = result["metrics"]
    lines = [
        f"# NQ ORB run — {result['timestamp']}",
        "",
        f"- decision: **{result['decision']['decision']}**",
        f"- reasons: {result['decision']['reasons']}",
        "",
        "## Params",
        f"- opening_range_minutes: {result['params'].get('opening_range_minutes')}",
        f"- target_r_multiple: {result['params'].get('target_r_multiple')}",
        "",
        "## Metrics",
        f"- trade_count: {m['trade_count']:.0f}",
        f"- win_rate: {m['win_rate']:.3f}",
        f"- profit_factor: {m['profit_factor']:.3f}",
        f"- expectancy_r: {m['expectancy_r']:.3f}",
        f"- max_drawdown_pct: {m['max_drawdown_pct']:.2f}",
        f"- sharpe_like: {m['sharpe_like']:.3f}",
        "",
    ]
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    out = run_once()
    print(json.dumps(out, indent=2))
