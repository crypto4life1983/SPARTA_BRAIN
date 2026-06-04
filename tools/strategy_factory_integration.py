"""SPARTA Strategy Factory v1 Integration Bundle -- Research-Only Dry-Run (BUILD ONLY).

Read-only, local-only, stdlib-only. This module joins the existing read-only
Strategy Factory layers and the reconciled Crypto-D1 N=20 deeper-validation helper
into ONE descriptive dry-run bundle. The chain it composes is:

    queue -> orchestrator -> runner-output adapter -> deeper-validation helper
    -> validation report -> decision memo -> registry update PROPOSAL
    -> dashboard feed PREVIEW -> next action

It is NOT paper trading, NOT live trading, and NOT broker/exchange integration. It:

  * reads the factory queue/orchestrator/safety/registry surfaces READ-ONLY (it
    mutates none of them);
  * feeds the deeper-validation helper SYNTHETIC bars only -- it reads NO frozen
    dataset and runs NO real backtest over frozen data;
  * emits a registry update *proposal* (proposal_only=true, applied=false) and a
    dashboard feed *preview* (preview_only=true, applied_to_dashboard=false) --
    it imports no dashboard/DB module and performs no registry/dashboard write;
  * executes no subprocess, opens no network, touches no credentials, places no
    order, and authorizes no paper/live/broker/exchange/fetch;
  * keeps N fixed at 20; the {18,20,22} neighborhood stays a labeled stability
    SENSITIVITY (winner never re-selected);
  * caps every verdict at WATCH. The decision memo can only ever emit WATCH,
    FAIL, or INSUFFICIENT_EVIDENCE -- never PASS/ACTIVE/STRONG. Even all-green
    synthetic evidence resolves to WATCH because this is research-only and not
    real-data validation.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import crypto_d1_backtest_runner as cbr            # noqa: E402  (Bar + constants)
import crypto_d1_deeper_validation as dv            # noqa: E402  (analysis helper)
import strategy_factory_queue as sfq                # noqa: E402  (read-only)
import strategy_factory_orchestrator as sfo         # noqa: E402  (read-only)
import strategy_factory_safety as sfs               # noqa: E402  (read-only)
import strategy_report_registry as srr              # noqa: E402  (read-only)

# --- Identity --------------------------------------------------------------
SCHEMA_VERSION = 1
LAYER = "strategy_factory_integration_v1"
CONFIG_NAME = "strategy_factory_integration_v1"
PRIMARY_LOOKBACK = dv.PRIMARY_LOOKBACK              # 20 (single source: helper)
VERDICT_CEILING = "WATCH"
ALLOWED_MEMO_VERDICTS = ("WATCH", "FAIL", "INSUFFICIENT_EVIDENCE")
FORBIDDEN_VERDICTS = frozenset({"ACTIVE", "STRONG", "PASS"})

# Single confined writer target (opt-in only).
_BUILD_OUT_RELDIR = Path("reports") / "strategy_factory_integration_v1_build"

# Dashboard manual-entry field names replicated locally so this module needs NO
# dashboard/DB import. (Mirrors the dashboard's accepted upsert fields.)
_DASHBOARD_ENTRY_FIELDS = (
    "module_key", "module_name", "category", "status", "short_description",
    "how_it_works", "when_to_use", "user_action", "sort_order",
)

SAFETY_FLAGS = {
    "research_only": True,
    "paper_live_authorized": False,
    "broker_path_enabled": False,
    "exchange_path_enabled": False,
    "order_path_enabled": False,
    "fetch_live_data_enabled": False,
    "dataset_mutation_allowed": False,
    "queue_mutation_allowed": False,
    "registry_mutation_allowed": False,
    "dashboard_mutation_allowed": False,
    "active_strong_promoted": False,
    "bundle_23_started": False,
    "execution_authorized": False,
}

NON_AUTHORIZATION = (
    "Research-only dry-run INTEGRATION layer. Composes read-only factory views "
    "over synthetic bars and emits descriptive artifacts plus a registry "
    "proposal and a dashboard preview. It runs no backtest over frozen data, "
    "executes no queue task, mutates no queue/registry/dashboard/dataset, and "
    "authorizes no paper/live/broker/exchange/order/fetch action. It promotes "
    "no lane to ACTIVE/STRONG and emits no PASS. Verdict ceiling stays WATCH; "
    "Crypto-D1 stays WATCH/MIXED and NOT_READY_FOR_REAL_DATA. A positive "
    "synthetic view is not a trading authorization."
)


# ===========================================================================
# Synthetic fixtures -- deterministic, NEVER touch real research data.
# ===========================================================================
def _synthetic_bars(symbol, closes, start=cbr.V002_OOS_START):
    d0 = datetime.strptime(start, "%Y-%m-%d")
    out = []
    for i, c in enumerate(closes):
        ts = (d0 + timedelta(days=i)).strftime("%Y-%m-%d")
        out.append(cbr.Bar(timestamp=ts, open=c, high=c, low=c, close=float(c),
                           volume=1.0, symbol=symbol, source="synthetic",
                           quote_currency="USD"))
    return out


def _trending_closes(n, base, step, wobble):
    out, price = [], base
    for i in range(n):
        price += step + (wobble if i % 2 == 0 else -wobble)
        out.append(price)
    return out


def synthetic_per_asset(n=240):
    """Helper-shaped synthetic per-asset OOS bars (BTC/ETH/SOL). No file I/O."""
    return [
        {"asset": "BTC", "bars": _synthetic_bars("BTCUSDT", _trending_closes(n, 100, 1.0, 3.0))},
        {"asset": "ETH", "bars": _synthetic_bars("ETHUSDT", _trending_closes(n, 50, 0.5, 2.0))},
        {"asset": "SOL", "bars": _synthetic_bars("SOLUSDT", _trending_closes(n, 20, 0.3, 1.5))},
    ]


def synthetic_runner_output(n=240):
    """A synthetic, runner-RESULT-shaped payload (NOT from a real backtest).

    Each asset carries the OOS bars the runner would have sliced plus a metrics
    dict shaped like ``cbr._simulate_equity``'s return, computed over the SAME
    synthetic bars. Used to exercise the adapter seam. Reads no frozen data."""
    out = {}
    for item in synthetic_per_asset(n):
        bars = item["bars"]
        pos, err = cbr.momentum_continuation(bars, PRIMARY_LOOKBACK)
        metrics = None
        if err is None:
            metrics = cbr._simulate_equity(
                pos, bars, fee_bps=dv.BASELINE_ROUND_TRIP_BPS / 2.0, slip_bps=0.0,
                start_equity=cbr.DEFAULT_START_EQUITY, spread_bps=0.0,
            )
        out[item["asset"]] = {"bars": bars, "runner_metrics": metrics}
    return out


# ===========================================================================
# Runner-output adapter -- the seam where real runner OOS slices would plug in.
# ===========================================================================
def adapt_runner_output_to_per_asset(runner_output):
    """Convert runner-shaped output into the deeper-validation helper's per_asset
    input ``[{"asset": str, "bars": [cbr.Bar, ...]}]``.

    Accepts either the helper-shaped list already, or a runner-result-shaped dict
    ``{asset: {"bars": [...], "runner_metrics": {...}}}``. Reads NO frozen data;
    constructs nothing from disk. This is the explicit, future-approved seam for
    real runner OOS slices -- here it is fed synthetic bars only."""
    if isinstance(runner_output, list):
        return runner_output
    out = []
    for asset in sorted(runner_output):
        out.append({"asset": asset, "bars": runner_output[asset]["bars"]})
    return out


# ===========================================================================
# Decision memo -- verdict capped at WATCH (never PASS/ACTIVE/STRONG).
# ===========================================================================
def _derive_decision(validation_report):
    secs = validation_report["validation_sections"]
    cons = secs["3_per_asset_consistency"]
    tct = secs["4_trade_count_and_turnover"]
    fee_secs = secs["5_fee_slippage_stress"]
    out_secs = secs["6_outlier_sensitivity"]
    reg_secs = secs["7_regime_sensitivity"]
    nb_secs = secs["9_small_parameter_neighborhood_sensitivity"]

    checks = {
        "all_assets_positive": bool(cons.get("all_positive", False)),
        "meets_family_floor": bool(tct.get("meets_family_floor", False)),
        "per_asset_floor_all_clear": bool(tct.get("per_asset")) and all(
            a.get("clears_per_asset_floor", False)
            for a in tct.get("per_asset", {}).values()),
        "fee_stress_survived": bool(fee_secs) and all(
            f.get("baseline_total_return", 0.0) > 0.0 and all(
                lvl.get("survives_positive", False)
                for lvl in f.get("stress_levels", {}).values())
            for f in fee_secs.values()),
        "not_outlier_dependent": bool(out_secs) and not any(
            o.get("edge_outlier_dependent", False) for o in out_secs.values()),
        "not_single_regime": bool(reg_secs) and not any(
            r.get("confined_to_single_regime", True) for r in reg_secs.values()),
        "neighborhood_sensitivity_not_optimization": bool(nb_secs) and all(
            nb.get("is_sensitivity_not_optimization", False)
            and nb.get("winner_reselected") is False
            for nb in nb_secs.values()),
    }

    insufficient = bool(validation_report.get("insufficient_history_notes"))
    has_trades = bool(tct.get("per_asset"))

    if insufficient or not has_trades:
        verdict = "INSUFFICIENT_EVIDENCE"
    elif checks["meets_family_floor"] and checks["per_asset_floor_all_clear"]:
        # Even all-green synthetic evidence is capped at WATCH on purpose:
        # this is research-only and NOT real-data validation.
        verdict = "WATCH"
    else:
        verdict = "FAIL"

    if verdict not in ALLOWED_MEMO_VERDICTS or verdict in FORBIDDEN_VERDICTS:
        raise RuntimeError(f"verdict ceiling violated: {verdict!r}")

    evidence = {"WATCH": "MIXED", "FAIL": "NONE",
                "INSUFFICIENT_EVIDENCE": "WEAK"}[verdict]
    return verdict, evidence, checks


def _rationale(verdict, checks):
    if verdict == "WATCH":
        return ("Synthetic dry-run read is WATCH: descriptive views cleared the "
                "research trade floors, but this is not real-data validation. No "
                "further step without separate operator approval.")
    if verdict == "FAIL":
        return ("Synthetic dry-run did not clear the per-asset/family research "
                "trade floors; recorded as FAIL pending a future real-data "
                "review.")
    return ("Synthetic series produced no qualifying trades; evidence is "
            "insufficient. Supply more history before any read.")


def _next_action(verdict):
    return ("Await separate operator approval to (a) wire real runner OOS slices "
            "into the adapter for true validation and (b) decide whether to apply "
            "the registry proposal. No further step is authorized now. Verdict "
            f"stays capped at WATCH (current synthetic read: {verdict}).")


# ===========================================================================
# Registry update PROPOSAL (proposal_only -- never applied here).
# ===========================================================================
def _registry_update_proposal(verdict, evidence):
    status = {"WATCH": "WATCH", "FAIL": "FAILED",
              "INSUFFICIENT_EVIDENCE": "WATCH"}[verdict]
    if status in FORBIDDEN_VERDICTS:
        raise RuntimeError(f"proposed status violates ceiling: {status!r}")
    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER,
        "proposal_only": True,
        "applied": False,
        "registry_mutation_performed": False,
        "verdict_ceiling": VERDICT_CEILING,
        "human_approval_required_to_apply": True,
        "proposed_candidate": {
            "candidate_id": "crypto_d1_momentum_n20",
            "title": "Crypto-D1 Momentum N=20 (research-only)",
            "lane": "crypto_d1_momentum_n20",
            "market": "crypto",
            "timeframe": "1d",
            "hypothesis": "Daily momentum continuation on BTC/ETH/SOL at N=20.",
            "status": status,
            "evidence_level": evidence,
            "primary_lookback": PRIMARY_LOOKBACK,
            "neighborhood_lookbacks": list(dv.NEIGHBORHOOD_LOOKBACKS),
            "neighborhood_is_sensitivity_not_optimization": True,
            "winner_reselected": False,
            "source_reports": [
                "reports/strategy_factory_integration_v1_build/report.json"],
            "next_action": _next_action(verdict),
            "allowed_next_steps": [
                "operator_review",
                "wire_real_runner_oos_slices_after_approval",
            ],
            "forbidden_next_steps": [
                "promote_active", "promote_strong", "mark_pass",
                "paper", "live", "broker", "exchange", "order", "fetch",
            ],
        },
        "safety_flags": dict(SAFETY_FLAGS),
        "non_authorization_statement": NON_AUTHORIZATION,
    }


# ===========================================================================
# Dashboard feed PREVIEW (preview_only -- no dashboard import, no DB write).
# ===========================================================================
def _dashboard_feed_preview(verdict):
    entry = {
        "module_key": "strategy_factory_integration_v1",
        "module_name": "Strategy Factory v1 Integration (Dry-Run)",
        "category": "Strategy Factory",
        "status": f"{verdict} / research-only",
        "short_description": (
            "Research-only dry-run that joins the queue, orchestrator, safety, "
            "and registry views with the Crypto-D1 N=20 deeper-validation "
            "sections into one synthetic bundle."),
        "how_it_works": (
            "Composes existing read-only factory layers over synthetic bars and "
            "emits a report, a decision memo, a registry update proposal, and "
            "this preview. It runs nothing and changes nothing."),
        "when_to_use": (
            "To inspect how the Crypto-D1 N=20 research chain would connect end "
            "to end before any future real-data step."),
        "user_action": (
            "Review the bundle artifacts; separate operator approval is required "
            "before any further step."),
        "sort_order": 950,
    }
    assert set(entry) <= set(_DASHBOARD_ENTRY_FIELDS)
    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER,
        "preview_only": True,
        "applied_to_dashboard": False,
        "dashboard_write_performed": False,
        "target_table": "system_manual_entries",
        "entry": entry,
        "safety_flags": dict(SAFETY_FLAGS),
        "non_authorization_statement": NON_AUTHORIZATION,
    }


# ===========================================================================
# Assembler -- the full integration bundle (no execution).
# ===========================================================================
def build_integration_bundle(base, runner_output=None,
                             start_equity=cbr.DEFAULT_START_EQUITY):
    """Compose the read-only factory views + synthetic deeper-validation into one
    dry-run bundle. Reads the factory configs READ-ONLY; feeds the helper
    SYNTHETIC bars only; mutates nothing; executes nothing."""
    base = Path(base)
    queue = sfq.build(base)
    orchestrator = sfo.build_dry_run_plan(base)
    safety = sfs.build(base)
    registry = srr.build_registry(base)

    per_asset = adapt_runner_output_to_per_asset(
        runner_output if runner_output is not None else synthetic_runner_output())
    validation_report = dv.build_deeper_validation_report(
        per_asset, start_equity=start_equity)

    verdict, evidence, checks = _derive_decision(validation_report)
    decision = {
        "verdict": verdict,
        "verdict_ceiling": VERDICT_CEILING,
        "allowed_verdicts": list(ALLOWED_MEMO_VERDICTS),
        "evidence_level": evidence,
        "checks": checks,
        "rationale": _rationale(verdict, checks),
        "promotion_blocked": True,
        "reason_capped_at_watch": (
            "Research-only synthetic dry-run; not real-data validation. No "
            "promotion tier above WATCH is reachable from this dry-run."),
    }
    proposal = _registry_update_proposal(verdict, evidence)
    preview = _dashboard_feed_preview(verdict)

    # Self-screen the human-facing free text against the contract's forbidden
    # trading terms (the proposal's forbidden_next_steps list is intentionally
    # excluded -- it NAMES the forbidden steps in order to forbid them).
    human_text = " ".join([
        decision["rationale"], decision["reason_capped_at_watch"],
        _next_action(verdict),
        preview["entry"]["short_description"], preview["entry"]["how_it_works"],
        preview["entry"]["when_to_use"], preview["entry"]["user_action"],
    ])
    forbidden_scan = sfs.screen_text(human_text, sfs.REQUIRED_FORBIDDEN_TERMS)

    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER,
        "config_mode": CONFIG_NAME,
        "read_only": True,
        "dry_run": True,
        "executes_backtest": False,
        "executes_anything": False,
        "uses_synthetic_data_only": True,
        "reads_frozen_dataset": False,
        "primary_lookback": PRIMARY_LOOKBACK,
        "verdict_ceiling": VERDICT_CEILING,
        "chain": [
            "queue", "orchestrator", "runner_output_adapter", "deeper_validation",
            "validation_report", "decision_memo", "registry_update_proposal",
            "dashboard_feed_preview", "next_action",
        ],
        "queue_summary": {k: queue.get(k) for k in (
            "layer", "item_count", "valid_item_count", "blocked_item_count")},
        "orchestrator_summary": {k: orchestrator.get(k) for k in (
            "layer", "dry_run", "executes_anything", "execution_halted",
            "task_count")},
        "safety_summary": {k: safety.get(k) for k in ("layer", "valid", "safe")},
        "registry_summary": {k: registry.get(k) for k in (
            "layer", "strategy_count")},
        "validation_report": validation_report,
        "decision_memo": decision,
        "registry_update_proposal": proposal,
        "dashboard_feed_preview": preview,
        "next_action": _next_action(verdict),
        "forbidden_term_scan_on_human_text": forbidden_scan,
        "safety_flags": dict(SAFETY_FLAGS),
        "non_authorization_statement": NON_AUTHORIZATION,
    }


def show_plan():
    """Read-only descriptor of this integration bundle (no execution)."""
    return {
        "config_name": CONFIG_NAME,
        "layer": LAYER,
        "purpose": (
            "Research-only dry-run integration of the Strategy Factory chain "
            "over synthetic Crypto-D1 N=20 evidence. Runs nothing; verdict "
            "ceiling WATCH."),
        "primary_lookback": PRIMARY_LOOKBACK,
        "verdict_ceiling": VERDICT_CEILING,
        "allowed_memo_verdicts": list(ALLOWED_MEMO_VERDICTS),
        "chain": [
            "queue", "orchestrator", "runner_output_adapter", "deeper_validation",
            "validation_report", "decision_memo", "registry_update_proposal",
            "dashboard_feed_preview", "next_action",
        ],
        "outputs": [
            "report.json", "report.md", "decision_memo.md",
            "registry_update_proposal.json", "dashboard_feed_preview.json",
        ],
        "uses_synthetic_data_only": True,
        "reads_frozen_dataset": False,
        "build_only": True,
        "executes_backtest": False,
        "safety_flags": dict(SAFETY_FLAGS),
        "non_authorization_statement": NON_AUTHORIZATION,
    }


# ===========================================================================
# Deterministic serialization + markdown + opt-in confined writer + CLI.
# ===========================================================================
def to_stable_json(obj) -> str:
    """Deterministic, sorted-key JSON (factory convention)."""
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False,
                      default=str) + "\n"


def render_markdown(bundle) -> str:
    d = bundle["decision_memo"]
    lines = [
        "# Strategy Factory v1 Integration Bundle -- Research-Only Dry-Run",
        "",
        f"- layer: `{bundle['layer']}`",
        f"- **dry_run: {bundle['dry_run']}  |  executes_anything: "
        f"{bundle['executes_anything']}  |  executes_backtest: "
        f"{bundle['executes_backtest']}**",
        f"- uses_synthetic_data_only: {bundle['uses_synthetic_data_only']}  |  "
        f"reads_frozen_dataset: {bundle['reads_frozen_dataset']}",
        f"- primary_lookback: {bundle['primary_lookback']}  |  verdict_ceiling: "
        f"{bundle['verdict_ceiling']}",
        "",
        "## Chain",
        "",
        " -> ".join(bundle["chain"]),
        "",
        "## Inputs (read-only)",
        "",
        f"- queue: {bundle['queue_summary']}",
        f"- orchestrator: {bundle['orchestrator_summary']}",
        f"- safety: {bundle['safety_summary']}",
        f"- registry: {bundle['registry_summary']}",
        "",
        "## Decision",
        "",
        f"- **verdict: {d['verdict']}** (allowed: {d['allowed_verdicts']})",
        f"- evidence_level: {d['evidence_level']}",
        f"- promotion_blocked: {d['promotion_blocked']}",
        f"- rationale: {d['rationale']}",
        "",
        "### Checks",
        "",
    ]
    for k, v in sorted(d["checks"].items()):
        lines.append(f"- {k}: {v}")
    lines += [
        "",
        "## Proposals / previews (not applied)",
        "",
        f"- registry_update_proposal: proposal_only="
        f"{bundle['registry_update_proposal']['proposal_only']}, applied="
        f"{bundle['registry_update_proposal']['applied']}",
        f"- dashboard_feed_preview: preview_only="
        f"{bundle['dashboard_feed_preview']['preview_only']}, "
        f"applied_to_dashboard="
        f"{bundle['dashboard_feed_preview']['applied_to_dashboard']}",
        "",
        f"## Next action\n\n{bundle['next_action']}",
        "",
        "## Non-authorization",
        "",
        bundle["non_authorization_statement"],
        "",
    ]
    return "\n".join(lines)


def render_decision_memo(bundle) -> str:
    d = bundle["decision_memo"]
    lines = [
        "# Crypto-D1 N=20 Integration Dry-Run -- Decision Memo (research-only)",
        "",
        f"- **verdict: {d['verdict']}**  (ceiling: {d['verdict_ceiling']}; "
        f"allowed: {', '.join(d['allowed_verdicts'])})",
        f"- evidence_level: {d['evidence_level']}",
        f"- promotion_blocked: {d['promotion_blocked']}",
        "",
        "## Why this verdict",
        "",
        d["rationale"],
        "",
        d["reason_capped_at_watch"],
        "",
        "## Checks (descriptive, from the deeper-validation views)",
        "",
    ]
    for k, v in sorted(d["checks"].items()):
        lines.append(f"- {k}: {v}")
    lines += [
        "",
        "## Next action",
        "",
        bundle["next_action"],
        "",
        "## Non-authorization",
        "",
        bundle["non_authorization_statement"],
        "",
    ]
    return "\n".join(lines)


def write_bundle(base, bundle) -> list:
    """Opt-in writer. Writes the five artifacts ONLY under the single build
    folder reports/strategy_factory_integration_v1_build/. Returns repo-relative
    paths. Performs no registry/dashboard/dataset write."""
    base = Path(base)
    out_dir = base / _BUILD_OUT_RELDIR
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(to_stable_json(bundle), encoding="utf-8")
    (out_dir / "report.md").write_text(render_markdown(bundle), encoding="utf-8")
    (out_dir / "decision_memo.md").write_text(
        render_decision_memo(bundle), encoding="utf-8")
    (out_dir / "registry_update_proposal.json").write_text(
        to_stable_json(bundle["registry_update_proposal"]), encoding="utf-8")
    (out_dir / "dashboard_feed_preview.json").write_text(
        to_stable_json(bundle["dashboard_feed_preview"]), encoding="utf-8")
    names = ("report.json", "report.md", "decision_memo.md",
             "registry_update_proposal.json", "dashboard_feed_preview.json")
    return [(out_dir / n).relative_to(base).as_posix() for n in names]


def main(argv=None) -> int:
    """Read-only CLI: builds the dry-run bundle and prints it. Runs no backtest,
    reads no frozen dataset, mutates nothing, returns 0."""
    parser = argparse.ArgumentParser(
        description="Strategy Factory v1 research-only dry-run integration "
                    "bundle (BUILD ONLY; runs no backtest, executes nothing).")
    parser.add_argument("--base", default=None, help="repo root (default: cwd)")
    parser.add_argument("--write", action="store_true",
                        help="ALSO write the five artifacts under "
                             "reports/strategy_factory_integration_v1_build/")
    args = parser.parse_args(argv)
    base = Path(args.base) if args.base else Path(".")
    bundle = build_integration_bundle(base)
    if args.write:
        written = write_bundle(base, bundle)
        sys.stderr.write("wrote: " + ", ".join(written) + "\n")
    sys.stdout.write(to_stable_json(bundle))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
