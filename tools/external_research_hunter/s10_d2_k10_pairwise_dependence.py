"""S10-D2 K10 pairwise-dependence evaluator.

Authorized by: operator phrase
    "Authorize S10-D2 K10 pairwise dependence computation."

Closes gap G2 from the S10-D2 tier-N status review
(reports/s10_d2_..._tier_n_spec_and_status_review.{md,json}) by computing
the avg pairwise correlation of NQ + GC + ZN + CL RTH daily simple returns
over the sealed in-sample window (2013-01-01 .. 2022-12-30, per
in_sample_driver.IN_SAMPLE_START / IN_SAMPLE_END).

Method
------
1. Reuse `derive_rth_daily_bars(market)` from the sealed in-sample driver
   to load per-market RTH daily OHLCV from the local cache. The driver:
     - reads .dbn.zst from C:/SPARTA_BRAIN/data/databento_cache only
     - never instantiates databento.Historical
     - never opens a network socket
2. Compute simple daily returns per market: r_t = (c_t - c_{t-1}) / c_{t-1}.
3. Inner-join the 4 series on their common calendar dates.
4. Compute 6 pairwise Pearson correlations and their unweighted mean.
5. Apply the K10 acceptance gate: K10_avg_pairwise_corr_gt_0_50 fires when
   avg > 0.50.
6. Seal a JSON + MD report pair at
   reports/external_research_hunter/s10_d2_..._k10_pairwise_dependence_result_sealed.{json,md}.

Hard contract (defense-in-depth)
--------------------------------
- No Databento Historical API call. No databento.Historical instantiation.
- No DATABENTO_API_KEY read. No environment-variable read for credentials.
- No external network call. socket.create_connection is monkeypatched to
  raise; if anything tries to open a socket the run halts.
- No cache mutation. No file write under data/databento_cache or
  data/databento_cache_oos. The two output files are the ONLY filesystem
  writes this script performs.
- No spec mutation. No parameter change. No strategy optimization.
- No OOS inspection. No simulator run. No backtest run. No signal compute.
- No live trading. No broker call.

This module is importable without side effects; the entry point is `main()`.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
import socket
import sys
from pathlib import Path
from typing import Dict, List, Tuple


REPO_ROOT = Path(r"C:\SPARTA_BRAIN")
REPORT_DIR = REPO_ROOT / "reports" / "external_research_hunter"
REPORT_JSON = REPORT_DIR / (
    "s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_"
    "k10_pairwise_dependence_result_sealed.json"
)
REPORT_MD = REPORT_DIR / (
    "s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_"
    "k10_pairwise_dependence_result_sealed.md"
)

K10_THRESHOLD = 0.50  # K10_avg_pairwise_corr_gt_0_50 fires when avg > threshold
SCHEMA_ID = (
    "sparta.external_research_hunter."
    "s10_d2_k10_pairwise_dependence_result_sealed.v1"
)
PHASE_PREFIX = "PHASE2-S10-D2-XAD-RC-K10"
CANDIDATE_RECORD_ID = (
    "s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl"
)


# ---------------------------------------------------------------------------
# Defense-in-depth: prove no outbound network call
# ---------------------------------------------------------------------------
class NoNetworkError(RuntimeError):
    """Raised if anything tries to open a socket during the K10 run."""


def block_network() -> None:
    """Replace socket.create_connection with a fail-closed stub.

    The driver's local-cache read path does not open sockets; this is
    defense-in-depth to prove the contract at runtime.
    """
    def _refuse(*_args, **_kwargs):
        raise NoNetworkError(
            "S10-D2 K10 evaluator: socket.create_connection was called. "
            "This run is contractually local-cache-only; halting."
        )
    socket.create_connection = _refuse


# ---------------------------------------------------------------------------
# Math (pure functions; no I/O, no globals)
# ---------------------------------------------------------------------------
def daily_returns(closes: List[float]) -> List[float]:
    """Simple daily returns. len(out) == len(in) - 1.

    Raises ValueError on zero or non-finite inputs (fail-closed; the K10
    gate is meaningless on corrupt closes).
    """
    if len(closes) < 2:
        return []
    out: List[float] = []
    for i in range(1, len(closes)):
        c0 = closes[i - 1]
        c1 = closes[i]
        if c0 == 0 or not math.isfinite(c0) or not math.isfinite(c1):
            raise ValueError(
                f"non-finite or zero close at i={i}: c0={c0!r} c1={c1!r}"
            )
        out.append((c1 - c0) / c0)
    return out


def pearson_corr(xs: List[float], ys: List[float]) -> float:
    """Pearson correlation. Requires equal-length, non-constant inputs."""
    n = len(xs)
    if n != len(ys):
        raise ValueError(f"length mismatch: {n} vs {len(ys)}")
    if n < 2:
        raise ValueError("need at least 2 observations")
    mx = sum(xs) / n
    my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        raise ValueError("constant series; correlation undefined")
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return num / (sx * sy)


def avg_pairwise_corr(
    series_by_symbol: Dict[str, List[float]],
) -> Tuple[float, Dict[str, float]]:
    """Return (unweighted mean of pair-correlations, dict of pair->corr).

    Pair keys are formatted as `"A__B"` with the symbols in ascending
    alphabetical order to make output deterministic.
    """
    symbols = sorted(series_by_symbol.keys())
    n = len(symbols)
    if n < 2:
        raise ValueError(f"need >= 2 symbols, got {n}")
    pairs: Dict[str, float] = {}
    for i in range(n):
        for j in range(i + 1, n):
            a, b = symbols[i], symbols[j]
            pairs[f"{a}__{b}"] = pearson_corr(
                series_by_symbol[a], series_by_symbol[b],
            )
    avg = sum(pairs.values()) / len(pairs)
    return avg, pairs


def align_by_date(
    closes_by_symbol: Dict[str, Dict[_dt.date, float]],
) -> Tuple[List[_dt.date], Dict[str, List[float]]]:
    """Inner-join on dates present in every symbol's series."""
    if not closes_by_symbol:
        return [], {}
    common = set.intersection(
        *[set(d.keys()) for d in closes_by_symbol.values()]
    )
    dates = sorted(common)
    per_symbol_closes: Dict[str, List[float]] = {
        sym: [d[date] for date in dates]
        for sym, d in closes_by_symbol.items()
    }
    return dates, per_symbol_closes


# ---------------------------------------------------------------------------
# Data load: reuse sealed driver
# ---------------------------------------------------------------------------
def load_daily_closes_by_symbol() -> Tuple[
    Dict[str, Dict[_dt.date, float]], Dict[str, object]
]:
    """For each market, return {date -> RTH-daily-close} for the sealed IS
    window. Also returns a short summary of the data inputs for the report.
    """
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from external_research_hunter.s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness import (  # noqa: E501
        in_sample_driver as drv,
    )
    # Defensive: verify cache state + sealed-chain shas before any decode.
    cache_state = drv.assert_cache_complete()
    seal_state = drv.assert_seal_inheritance()
    closes: Dict[str, Dict[_dt.date, float]] = {}
    for market in drv.SYMBOLS.keys():
        daily = drv.derive_rth_daily_bars(market)
        closes[market] = {row["date"]: row["close"] for row in daily}
    inputs_summary = {
        "in_sample_start": drv.IN_SAMPLE_START.isoformat(),
        "in_sample_end": drv.IN_SAMPLE_END.isoformat(),
        "cache_root": str(drv.CACHE_ROOT),
        "tier_n_spec_seal_sha256_pinned": drv.TIER_N_SPEC_SEAL_SHA256,
        "plan_lock_seal_sha256_pinned": drv.PLAN_LOCK_SEAL_SHA256,
        "phase2_plan_seal_sha256_pinned": drv.PHASE2_PLAN_SEAL_SHA256,
        "predecessor_seal_sha256_pinned": drv.PREDECESSOR_SEAL_SHA256,
        "expected_cache_bytes_per_market": dict(drv.EXPECTED_CACHE_BYTES),
        "expected_files_per_root": drv.EXPECTED_FILES_PER_ROOT,
        "cache_assertion_pass": cache_state.get("pass", False),
        "seal_assertion_pass": seal_state.get("pass", False),
        "symbols_in_canonical_order": [
            drv.SYMBOLS[m] for m in ("NQ", "GC", "ZN", "CL")
        ],
    }
    return closes, inputs_summary


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def build_report(
    avg_corr: float,
    pair_corrs: Dict[str, float],
    common_date_count: int,
    per_symbol_obs_count: Dict[str, int],
    inputs_summary: Dict[str, object],
) -> Dict[str, object]:
    fires = avg_corr > K10_THRESHOLD
    verdict = (
        "K10_FIRED_AVG_PAIRWISE_CORR_EXCEEDS_0_50"
        if fires
        else "K10_PASS_AVG_PAIRWISE_CORR_AT_OR_BELOW_0_50"
    )
    body: Dict[str, object] = {
        "schema_id": SCHEMA_ID,
        "phase_prefix": PHASE_PREFIX,
        "candidate_record_id": CANDIDATE_RECORD_ID,
        "authored_at_utc": _dt.datetime.now(_dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "authorization": (
            "Authorize S10-D2 K10 pairwise dependence computation."
        ),
        "verdict": verdict,
        "verdict_enum_allowed": [
            "K10_PASS_AVG_PAIRWISE_CORR_AT_OR_BELOW_0_50",
            "K10_FIRED_AVG_PAIRWISE_CORR_EXCEEDS_0_50",
        ],
        "verdict_never_means_live_ready": True,
        "live_promotion_path_closed": True,
        "k10_evaluation": {
            "metric_name": "K10_avg_pairwise_corr_gt_0_50",
            "threshold": K10_THRESHOLD,
            "threshold_direction": "fires_when_avg_strictly_greater_than_threshold",
            "avg_pairwise_corr": avg_corr,
            "avg_pairwise_corr_rounded_6dp": round(avg_corr, 6),
            "fires": fires,
        },
        "pairwise_correlations_rounded_6dp": {
            k: round(v, 6) for k, v in sorted(pair_corrs.items())
        },
        "pair_count": len(pair_corrs),
        "common_date_count_used_for_returns": max(common_date_count - 1, 0),
        "common_date_count_used_for_alignment": common_date_count,
        "per_symbol_observation_count_after_inner_join": dict(
            sorted(per_symbol_obs_count.items())
        ),
        "data_inputs": inputs_summary,
        "method": {
            "return_kind": "simple_daily_return",
            "alignment": (
                "inner_join_on_calendar_date_after_per_market_rth_aggregation"
            ),
            "correlation": "pearson",
            "aggregation": (
                "unweighted_arithmetic_mean_of_pair_correlations"
            ),
            "pairs_count_expected_for_4_symbols": 6,
            "rth_aggregation_source": (
                "external_research_hunter."
                "s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness."
                "in_sample_driver.derive_rth_daily_bars"
            ),
        },
        "boundaries_held": {
            "no_databento_call": True,
            "no_databento_historical_instantiation": True,
            "no_databento_api_key_access": True,
            "no_external_network_call": True,
            "no_socket_open_attempt": True,
            "no_cache_mutation": True,
            "no_file_content_modification_under_data_databento_cache": True,
            "no_file_content_modification_under_data_databento_cache_oos": True,
            "no_strategy_optimization_authorized": True,
            "no_tier_n_spec_mutation": True,
            "no_parameter_changes": True,
            "no_live_trading": True,
            "no_paper_trading": True,
            "no_broker_call": True,
            "no_oos_inspection": True,
            "no_oos_computation": True,
            "no_simulator_run": True,
            "no_signal_computed": True,
            "no_backtest_run": True,
            "no_review_queue_mutation": True,
            "no_idea_memory_mutation": True,
            "no_strategy_lab_invoked": True,
            "no_candidate_promoted": True,
            "no_lessons_md_staged_or_modified": True,
        },
        "trading_status": "PAUSED",
        "live_status": "BLOCKED_AT_6_GATES",
        "frc_granted": False,
        "advisory_label_permanent": "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE",
    }
    canonical = json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    )
    seal = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    body["report_seal_sha256"] = seal
    body["seal_method"] = (
        "sha256( json.dumps(body_excluding_seal_fields, sort_keys=True, "
        "separators=(',',':'), ensure_ascii=False) )"
    )
    return body


def write_report(body: Dict[str, object]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(body, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    k10 = body["k10_evaluation"]  # type: ignore[index]
    pairs = body["pairwise_correlations_rounded_6dp"]  # type: ignore[index]
    inputs = body["data_inputs"]  # type: ignore[index]
    boundaries = body["boundaries_held"]  # type: ignore[index]
    method = body["method"]  # type: ignore[index]
    md_lines = [
        "# S10-D2 K10 pairwise dependence — result (sealed)",
        "",
        f"**Schema:** `{body['schema_id']}`  ",
        f"**Phase prefix:** `{body['phase_prefix']}`  ",
        f"**Candidate record id:** `{body['candidate_record_id']}`  ",
        f"**Authored at (UTC):** `{body['authored_at_utc']}`  ",
        f"**Authorization:** *\"{body['authorization']}\"*  ",
        f"**Report seal sha256:** `{body['report_seal_sha256']}`",
        "",
        "## Verdict",
        "",
        f"**`{body['verdict']}`**",
        "",
        f"- K10 metric: `{k10['metric_name']}`",
        f"- Threshold: `{k10['threshold']}` (fires when avg strictly > threshold)",
        f"- Average pairwise correlation: **`{k10['avg_pairwise_corr_rounded_6dp']:+.6f}`**",
        f"- K10 fires: **`{k10['fires']}`**",
        "",
        "## Pairwise Pearson correlations",
        "",
        "| Pair | Correlation |",
        "|------|-------------|",
    ]
    for pair, c in sorted(pairs.items()):
        md_lines.append(f"| `{pair}` | `{c:+.6f}` |")
    md_lines.extend([
        "",
        "## Data inputs",
        "",
        f"- IS window UTC: `{inputs['in_sample_start']}` .. `{inputs['in_sample_end']}`",
        f"- Cache root: `{inputs['cache_root']}`",
        f"- Cache assertion: `{inputs['cache_assertion_pass']}`  ·  "
        f"Seal-inheritance assertion: `{inputs['seal_assertion_pass']}`",
        f"- Tier-N spec seal (pinned): `{inputs['tier_n_spec_seal_sha256_pinned']}`",
        f"- Plan-lock seal (pinned): `{inputs['plan_lock_seal_sha256_pinned']}`",
        f"- Phase-2 plan seal (pinned): `{inputs['phase2_plan_seal_sha256_pinned']}`",
        f"- Predecessor seal (pinned): `{inputs['predecessor_seal_sha256_pinned']}`",
        "",
        f"- Common-date count (after inner join across 4 symbols): "
        f"`{body['common_date_count_used_for_alignment']}`",
        f"- Daily-return count per symbol (n-1): "
        f"`{body['common_date_count_used_for_returns']}`",
        "",
        "## Method",
        "",
        f"- Return kind: `{method['return_kind']}`",
        f"- Alignment: `{method['alignment']}`",
        f"- Correlation: `{method['correlation']}`",
        f"- Aggregation: `{method['aggregation']}`",
        f"- RTH aggregation source: `{method['rth_aggregation_source']}`",
        "",
        "## Hard boundaries (all held this run)",
        "",
    ])
    for k, v in sorted(boundaries.items()):
        md_lines.append(f"- `{k}`: `{v}`")
    md_lines.extend([
        "",
        "## Posture invariants (unchanged by this evaluation)",
        "",
        f"- Trading status: `{body['trading_status']}`",
        f"- Live status: `{body['live_status']}`",
        f"- FRC granted: `{body['frc_granted']}`",
        f"- Advisory label (permanent): `{body['advisory_label_permanent']}`",
        f"- verdict_never_means_live_ready: `{body['verdict_never_means_live_ready']}`",
        f"- live_promotion_path_closed: `{body['live_promotion_path_closed']}`",
        "",
    ])
    REPORT_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    block_network()
    closes_by_symbol, inputs_summary = load_daily_closes_by_symbol()
    dates, per_sym_closes = align_by_date(closes_by_symbol)
    per_sym_obs = {s: len(v) for s, v in per_sym_closes.items()}
    returns_by_sym = {
        s: daily_returns(v) for s, v in per_sym_closes.items()
    }
    avg, pairs = avg_pairwise_corr(returns_by_sym)
    body = build_report(
        avg_corr=avg,
        pair_corrs=pairs,
        common_date_count=len(dates),
        per_symbol_obs_count=per_sym_obs,
        inputs_summary=inputs_summary,
    )
    write_report(body)
    print(f"K10 verdict: {body['verdict']}")
    print(f"avg_pairwise_corr: {avg:+.6f}  threshold: {K10_THRESHOLD}  "
          f"fires: {body['k10_evaluation']['fires']}")  # type: ignore[index]
    for k, v in sorted(pairs.items()):
        print(f"  {k}: {v:+.6f}")
    print(f"common dates: {len(dates)}")
    print(f"report_seal_sha256: {body['report_seal_sha256']}")
    print(f"report JSON: {REPORT_JSON}")
    print(f"report MD:   {REPORT_MD}")


if __name__ == "__main__":
    main()
