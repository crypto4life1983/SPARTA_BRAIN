"""SPARTA Arbitrage Factory V1 - SCANNER (READ-ONLY, ALERTS/REPORTS ONLY).

The first real scanner, built under the frozen seq-1 spec and gated on the
WHOLE lane chain (seq 0-5 lane review must be ACCEPTED). One approved run =
one report. Blocked or refused runs write NOTHING.

What a run does:
  1. Re-derives the lane chain and refuses unless the lane review is ACCEPTED.
  2. Builds a staging manifest from data/arbitrage_factory_v1/staged/ and
     validates it with the prep-rules contract; refuses if any kind is
     missing, any field is unsafe, or any data is stale and unacknowledged.
  3. Computes GROSS edge candidates purely from staged data (funding carry,
     spot-perp basis), then charges the seq-3 fee/slippage model in full.
  4. Classifies via the seq-3 thresholds and emits seq-4 alert records --
     every record is validated by the seq-4 schema validator before the run
     may complete; an invalid alert refuses the whole run.
  5. write=False (default): returns the report in memory, writes nothing.
     write=True (a separately human-approved run): writes ONE json+md pair
     under reports/arbitrage_factory_v1/, exclusive-create, never overwrite.

Never: orders, trade instructions, network, credentials, accounts, schedules,
loops, gate movement. Alerts carry the mandatory research-only disclaimer.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any

from sparta_commander.arbitrage_lane_review_contract import (
    VERDICT_LANE_REVIEW_ACCEPTED,
    build_arbitrage_lane_review,
)
from sparta_commander.arbitrage_staged_data_preparation_rules_contract import (
    VERDICT_MANIFEST_ACCEPTED,
    validate_staging_manifest,
)
from sparta_commander.arbitrage_fee_slippage_model_contract import (
    classify_net_edge,
    estimate_net_edge_bps,
)
from sparta_commander.arbitrage_alert_report_schema_contract import (
    MANDATORY_DISCLAIMER,
    REPORTS_ROOT,
    validate_alert_record,
)

SCANNER_SCHEMA_VERSION = "arbitrage_scanner.v1"
SCANNER_LABEL = "SPARTA Arbitrage Factory V1 Scanner (READ-ONLY, ALERTS ONLY)"
SCANNER_MODE = "RESEARCH_ONLY"

VERDICT_SCAN_COMPLETED = "ARBITRAGE_SCAN_COMPLETED_REPORT_READY"
VERDICT_SCAN_REFUSED = "ARBITRAGE_SCAN_REFUSED_NOTHING_WRITTEN"

NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_SCAN_REPORT"

STAGED_DIR = "data/arbitrage_factory_v1/staged"
_KIND_BY_PREFIX = {"funding": "funding_rates", "basis": "spot_perp_basis",
                   "quotes": "cross_exchange_quotes", "fees": "fee_schedule",
                   "depth": "liquidity_depth"}
# Conservative cost floors (bps) when a symbol-matched staged number is absent.
_FLOOR_SPREAD_BPS = 2.0
_FLOOR_SLIPPAGE_BPS = 1.5
_FLOOR_WITHDRAWAL_BPS = 0.5


def _now_utc() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _parse_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    return lines[0].split(","), [l.split(",") for l in lines[1:]]


def _refuse(report: dict[str, Any], reason: str) -> dict[str, Any]:
    report["verdict"] = VERDICT_SCAN_REFUSED
    report["blockers"].append(reason)
    report["alerts"] = []
    report["report_written"] = False
    return report


def run_arbitrage_scan(repo_root: Any = ".", write: bool = False) -> dict[str, Any]:
    """Run ONE scan. Refuse-by-default; blocked runs write nothing.
    write=True requires its own explicit human approval per the seq-1 spec."""
    now = _now_utc()
    report: dict[str, Any] = {
        "schema_version": SCANNER_SCHEMA_VERSION,
        "label": SCANNER_LABEL,
        "mode": SCANNER_MODE,
        "lane": "arbitrage_factory_v1",
        "run_timestamp_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": None,
        "blockers": [],
        "alerts": [],
        "alerts_are_research_only_not_trade_signals": True,
        "disclaimer": MANDATORY_DISCLAIMER,
        "report_written": False,
        "report_paths": [],
        "executes": False, "contains_order_logic": False, "uses_network": False,
        "uses_credentials": False, "starts_scheduler": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }

    # Gate 1: the whole lane chain must review ACCEPTED.
    if build_arbitrage_lane_review().get("verdict") != VERDICT_LANE_REVIEW_ACCEPTED:
        return _refuse(report, "lane_review_not_accepted")

    # Gate 2: staged manifest must validate ACCEPTED and be complete.
    staged = Path(repo_root) / STAGED_DIR
    if not staged.is_dir():
        return _refuse(report, "staged_folder_missing")
    entries, tables = [], {}
    for path in sorted(staged.glob("*.csv")):
        kind = _KIND_BY_PREFIX.get(path.name.split("_")[0])
        header, rows = _parse_rows(path)
        entry: dict[str, Any] = {"filename": path.name, "kind": kind,
                                 "columns": header}
        if kind != "fee_schedule":
            if not rows:
                return _refuse(report, "empty_staged_file:" + path.name)
            ts = [r[0] for r in rows]
            entry["first_timestamp_utc"], entry["last_timestamp_utc"] = min(ts), max(ts)
        entries.append(entry)
        tables[kind] = (header, rows)
    manifest = {"prepared_as_of_utc": report["run_timestamp_utc"],
                "entries": entries}
    m = validate_staging_manifest(manifest)
    if m.get("verdict") != VERDICT_MANIFEST_ACCEPTED:
        return _refuse(report, "manifest_refused:" + json.dumps(m.get("entry_errors") or m.get("errors")))
    if not m.get("manifest_complete_for_all_kinds"):
        return _refuse(report, "missing_kinds:" + ",".join(m.get("missing_kinds", [])))

    # Shared staged cost inputs (taker fee from staged kraken schedule, as the
    # conservative venue proxy; depth spread for BTC).
    fee_header, fee_rows = tables["fee_schedule"]
    taker_by_symbol = {r[fee_header.index("symbol")]:
                       float(r[fee_header.index("taker_fee_pct")]) * 10000
                       for r in fee_rows}
    d_header, d_rows = tables["liquidity_depth"]
    btc_spread = max(float(d_rows[-1][d_header.index("spread_bps")]), _FLOOR_SPREAD_BPS)

    def _staleness(kind: str) -> int:
        last = next(e["last_timestamp_utc"] for e in entries if e["kind"] == kind)
        parsed = _dt.datetime.fromisoformat(last.replace("Z", "+00:00"))
        return max((now - parsed).days, 0)

    candidates = []
    # Candidate 1: BTC funding carry (F1) from staged funding history.
    f_header, f_rows = tables["funding_rates"]
    latest_rate = float(f_rows[-1][f_header.index("funding_rate_8h")])
    candidates.append({
        "alert_id": "alert_btc_funding_carry_" + now.strftime("%Y%m%d%H%M%S"),
        "family_id": "ARB_F1_spot_perp_funding_basis", "symbol": "BTC",
        "venues": ["binance"], "gross_edge_bps": abs(latest_rate) * 10000,
        "taker_fee_bps": taker_by_symbol.get("BTC", 40.0),
        "spread_cost_bps": btc_spread, "slippage_bps": _FLOOR_SLIPPAGE_BPS,
        "funding_adjustment_bps": 0.0,
        "withdrawal_amortization_bps": _FLOOR_WITHDRAWAL_BPS,
        "staleness_kind": "funding_rates",
        "summary": "BTC funding carry candidate from staged funding history; "
                   "net edge shown after the full conservative cost stack",
    })
    # Candidate 2: ETH spot-perp basis (F1/F2) from the staged same-instant pair.
    b_header, b_rows = tables["spot_perp_basis"]
    basis_pct = float(b_rows[-1][b_header.index("basis_pct")])
    candidates.append({
        "alert_id": "alert_eth_basis_" + now.strftime("%Y%m%d%H%M%S"),
        "family_id": "ARB_F2_cross_exchange_basis_monitoring", "symbol": "ETH",
        "venues": ["bybit"], "gross_edge_bps": abs(basis_pct) * 100,
        "taker_fee_bps": taker_by_symbol.get("ETH", 40.0),
        "spread_cost_bps": _FLOOR_SPREAD_BPS, "slippage_bps": _FLOOR_SLIPPAGE_BPS,
        "funding_adjustment_bps": abs(latest_rate) * 10000,
        "withdrawal_amortization_bps": _FLOOR_WITHDRAWAL_BPS,
        "staleness_kind": "spot_perp_basis",
        "summary": "ETH spot-perp basis candidate from staged same-instant "
                   "pair; net edge shown after the full conservative cost stack",
    })

    for c in candidates:
        inputs = {k: c[k] for k in ("gross_edge_bps", "taker_fee_bps",
                                    "spread_cost_bps", "slippage_bps",
                                    "funding_adjustment_bps",
                                    "withdrawal_amortization_bps")}
        est = estimate_net_edge_bps(inputs)
        if not est["computable"]:
            return _refuse(report, "cost_model_refused:" + ";".join(est["errors"]))
        net = est["net_edge_bps"]
        alert = {
            "alert_id": c["alert_id"],
            "timestamp_utc": report["run_timestamp_utc"],
            "family_id": c["family_id"], "symbol": c["symbol"],
            "venues": c["venues"],
            "gross_edge_bps": round(c["gross_edge_bps"], 4),
            "taker_fee_bps": c["taker_fee_bps"],
            "spread_cost_bps": c["spread_cost_bps"],
            "slippage_bps": c["slippage_bps"],
            "funding_adjustment_bps": round(c["funding_adjustment_bps"], 4),
            "withdrawal_amortization_bps": c["withdrawal_amortization_bps"],
            "net_edge_bps": round(net, 4), "verdict": classify_net_edge(net),
            "data_staleness_days": _staleness(c["staleness_kind"]),
            "evidence_label": "[evidence: staged csvs " + report["run_timestamp_utc"] + "]",
            "summary": c["summary"],
            "alert_is_research_only_not_a_trade_signal": True,
            "human_action_needed": True, "disclaimer": MANDATORY_DISCLAIMER,
        }
        # recompute exact net from rounded components so the schema check holds
        alert["net_edge_bps"] = round(
            alert["gross_edge_bps"] - 2 * alert["taker_fee_bps"]
            - alert["spread_cost_bps"] - alert["slippage_bps"]
            - alert["funding_adjustment_bps"]
            - alert["withdrawal_amortization_bps"], 10)
        alert["verdict"] = classify_net_edge(alert["net_edge_bps"])
        check = validate_alert_record(alert)
        if not check["acceptable"]:
            return _refuse(report, "alert_failed_schema:" + ";".join(check["errors"]))
        report["alerts"].append(alert)

    report["verdict"] = VERDICT_SCAN_COMPLETED
    if write:
        out_dir = Path(repo_root) / REPORTS_ROOT
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = "arbitrage_scan_" + now.strftime("%Y%m%dT%H%M%SZ")
        jpath, mpath = out_dir / (stem + ".json"), out_dir / (stem + ".md")
        with open(jpath, "x", encoding="utf-8") as fh:  # never overwrite
            json.dump(report, fh, indent=2)
        lines = ["# SPARTA Arbitrage Research Scan (ALERTS ONLY)", "",
                 "- " + MANDATORY_DISCLAIMER, ""]
        for a in report["alerts"]:
            lines += [f"## [{a['verdict']}] {a['alert_id']}",
                      f"- {a['summary']}",
                      f"- gross {a['gross_edge_bps']} bps -> net {a['net_edge_bps']} bps "
                      f"(taker x2 {a['taker_fee_bps']}, spread {a['spread_cost_bps']}, "
                      f"slippage {a['slippage_bps']}, funding {a['funding_adjustment_bps']}, "
                      f"withdrawal {a['withdrawal_amortization_bps']})", ""]
        with open(mpath, "x", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        report["report_written"] = True
        report["report_paths"] = [str(jpath), str(mpath)]
    return report
