"""T1-T16 test suite for the s9 RSI-2 aggregator module.

Renames forbidden. Each top-level TestCase class is prefixed Tnn_ so the
build orchestrator can map result rows to T-IDs.
"""
from __future__ import annotations

import builtins
import dataclasses
import sys
import unittest
from pathlib import Path
from typing import Mapping

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import (
    load_all,
)
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal import (
    SignalEvent,
    compute_signals_all,
)
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator import (
    CostTier,
    ExitReason,
    SimulationResult,
    TradeRecord,
    simulate,
)
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator import (
    A10_CAP_BINDING_EVENTS_MAX,
    A1_MIN_CLOSED_TRADES,
    A2_SHARPE_PROXY_MIN,
    A3_EXPECTANCY_MIN,
    A4_TRADE_CURVE_MAXDD_PCT_MAX,
    A5_PER_MARKET_WR_GAP_MIN_COUNT,
    A5_PORTFOLIO_WR_GAP_PP_MIN,
    A7_EFFECTIVE_INDEPENDENT_BETS_MIN,
    AGateResults,
    AggregationResult,
    AggregatorError,
    AggregatorInputError,
    AggregatorOosBlockedError,
    AggregatorParameterOverrideError,
    AggregatorProvenanceDriftError,
    CostStressRow,
    DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION,
    DR_STRESS_TIERS_REQUIRED,
    IN_SAMPLE_WINDOW,
    K10_AVG_PAIRWISE_DEPENDENCE_MAX,
    K11_CAP_BINDING_EVENTS_MAX,
    KCriteriaResults,
    PerSymbolStats,
    PerTradeStats,
    PortfolioStats,
    VerdictReason,
    aggregate,
)


# Shared fixture cached at module-import scope.
_DATA = load_all()
_SIG = compute_signals_all(_DATA)
_SIMS = {tier.name: simulate(_DATA, _SIG, cost_tier=tier)
         for tier in (CostTier.S0, CostTier.S1, CostTier.S2, CostTier.S3)}
_SAFETY = {f"C{i}": True for i in range(1, 9)}


class T01_SchemaAndCostStressRows(unittest.TestCase):
    def test_schema(self):
        r = aggregate(_DATA, _SIMS, _SAFETY)
        self.assertIsInstance(r, AggregationResult)
        self.assertEqual(set(r.cost_stress_matrix.keys()),
                         set(DR_STRESS_TIERS_REQUIRED))
        for tier, row in r.cost_stress_matrix.items():
            self.assertIsInstance(row, CostStressRow)
            self.assertEqual(row.tier, tier)
        self.assertIsInstance(r.verdict, VerdictReason)
        self.assertEqual(r.in_sample_window, IN_SAMPLE_WINDOW)


class T02_AllDatesInSample(unittest.TestCase):
    def test_aggregation_dates_in_is(self):
        r = aggregate(_DATA, _SIMS, _SAFETY)
        for pts in r.per_trade_stats:
            self.assertGreaterEqual(pts.trade_entry_date, IN_SAMPLE_WINDOW[0])
            self.assertLessEqual(pts.trade_exit_date, IN_SAMPLE_WINDOW[1])


class T03_TotalNetPnlEqualsSumOfTradeRecords(unittest.TestCase):
    def test_per_tier_net_pnl_equals_simulator_sum(self):
        r = aggregate(_DATA, _SIMS, _SAFETY)
        for tier in ("S0", "S1", "S2", "S3"):
            sim_total = sum(rec.net_pnl_dollars
                            for rec in _SIMS[tier].trade_records)
            self.assertAlmostEqual(
                r.cost_stress_matrix[tier].total_net_pnl_dollars,
                sim_total, places=6,
                msg=f"tier {tier} sum mismatch",
            )


class T04_A1ClosedTradesMatchesPortfolio(unittest.TestCase):
    def test_a1_count_consistent(self):
        r = aggregate(_DATA, _SIMS, _SAFETY)
        per_sym_sum = sum(
            r.per_symbol_stats[sym].trades_count
            for sym in ("SPY", "TLT", "GLD", "USO")
        )
        self.assertEqual(r.portfolio_stats.total_closed_trades, per_sym_sum)
        self.assertEqual(per_sym_sum, _SIMS["S1"].num_closed_trades_total)


class T05_A4ThresholdConstantIsFifty(unittest.TestCase):
    def test_a4_constant_value(self):
        self.assertEqual(A4_TRADE_CURVE_MAXDD_PCT_MAX, 50.0)
        r = aggregate(_DATA, _SIMS, _SAFETY)
        # The a_gate evaluation must compare against the constant.
        observed_dd = r.portfolio_stats.trade_curve_max_drawdown_pct_vs_starting_cash
        expected_a4 = observed_dd <= A4_TRADE_CURVE_MAXDD_PCT_MAX
        self.assertEqual(r.a_gate_results.A4_trade_curve_maxdd_at_or_below_max,
                         expected_a4)


class T06_AggregatorInputError_BadLoaded(unittest.TestCase):
    def test_non_mapping_loaded(self):
        with self.assertRaises(AggregatorInputError):
            aggregate(None, _SIMS, _SAFETY)
        with self.assertRaises(AggregatorInputError):
            aggregate("not a mapping", _SIMS, _SAFETY)

    def test_wrong_loaded_keys(self):
        bad = {"SPY": _DATA["SPY"], "FOO": _DATA["TLT"]}
        with self.assertRaises(AggregatorInputError):
            aggregate(bad, _SIMS, _SAFETY)


class T07_AggregatorInputError_BadSimulationResults(unittest.TestCase):
    def test_missing_tier(self):
        bad = {"S0": _SIMS["S0"], "S1": _SIMS["S1"]}  # missing S2/S3
        with self.assertRaises(AggregatorInputError):
            aggregate(_DATA, bad, _SAFETY)

    def test_non_mapping(self):
        with self.assertRaises(AggregatorInputError):
            aggregate(_DATA, None, _SAFETY)

    def test_bad_safety_keys(self):
        bad = {f"C{i}": True for i in range(1, 5)}  # only C1-C4
        with self.assertRaises(AggregatorInputError):
            aggregate(_DATA, _SIMS, bad)


class T08_OosInjectionRefusal(unittest.TestCase):
    def test_oos_dated_trade_record_raises(self):
        s1 = _SIMS["S1"]
        # Build a synthetic SimulationResult with one OOS-dated TradeRecord.
        bad_record = TradeRecord(
            symbol="SPY", trade_id="SPY_FAKE", direction="long",
            entry_trigger_date="2023-06-14",
            entry_fill_date="2023-06-15",
            entry_fill_price=400.0,
            entry_slippage_dollars=0.02,
            shares=2,
            exit_trigger_date="2023-06-15",
            exit_fill_date="2023-06-16",
            exit_fill_price=400.5,
            exit_slippage_dollars=0.02,
            exit_reason=ExitReason.RSI_EXIT_TRIGGER,
            commission_dollars=0.0,
            gross_pnl_dollars=1.0,
            net_pnl_dollars=0.96,
            hold_days=1,
        )
        bad_sim = dataclasses.replace(
            s1,
            trade_records=tuple(list(s1.trade_records) + [bad_record]),
        )
        bad_map = dict(_SIMS)
        bad_map["S1"] = bad_sim
        with self.assertRaises(AggregatorOosBlockedError):
            aggregate(_DATA, bad_map, _SAFETY)


class T09_ParameterOverrideRefusal(unittest.TestCase):
    def test_unknown_kwarg_window(self):
        with self.assertRaises(AggregatorParameterOverrideError):
            aggregate(_DATA, _SIMS, _SAFETY,
                      window=("2024-01-01", "2025-12-31"))

    def test_unknown_kwarg_threshold(self):
        with self.assertRaises(AggregatorParameterOverrideError):
            aggregate(_DATA, _SIMS, _SAFETY,
                      a2_sharpe_proxy_min=0.5)

    def test_unknown_kwarg_filter(self):
        with self.assertRaises(AggregatorParameterOverrideError):
            aggregate(_DATA, _SIMS, _SAFETY, enable_short=True)


class T10_DataclassFieldNameStructuralInvariants(unittest.TestCase):
    FORBIDDEN_FRAGMENTS = (
        "donchian", "atr", "wilder",
        "pyramid", "unit_index",
        "entry_short", "exit_short", "short_position", "borrow",
        "stop_distance", "stop_price",
        "live_trading", "broker_session", "order_send",
        "place_order", "submit_order", "review_queue",
        "idea_memory", "strategy_lab",
    )
    EXPECTED_PORTFOLIO_FIELDS = (
        "total_closed_trades", "total_net_pnl_dollars",
        "total_gross_pnl_dollars", "mean_trade_net_pnl_dollars",
        "stdev_trade_net_pnl_dollars",
        "sharpe_proxy_per_trade", "expectancy_per_trade_dollars",
        "portfolio_win_rate", "portfolio_pl_ratio",
        "portfolio_implied_breakeven_win_rate",
        "portfolio_win_rate_gap_to_breakeven_pp",
        "trade_curve_cumulative_pnl_dollars",
        "trade_curve_high_water_mark_dollars",
        "trade_curve_max_drawdown_dollars",
        "trade_curve_max_drawdown_pct_vs_starting_cash",
        "cap_binding_events_count",
    )
    EXPECTED_PER_TRADE_FIELDS = (
        "symbol", "trade_id", "trade_pnl_dollars",
        "trade_entry_date", "trade_exit_date",
        "trade_duration_days", "trade_direction",
        "trade_exit_reason", "trade_is_win",
    )

    def _names(self, cls):
        return tuple(f.name for f in dataclasses.fields(cls))

    def test_per_trade_no_forbidden(self):
        names = self._names(PerTradeStats)
        for frag in self.FORBIDDEN_FRAGMENTS:
            for n in names:
                self.assertNotIn(frag.lower(), n.lower(),
                    f"forbidden fragment {frag!r} in PerTradeStats field {n}")

    def test_per_trade_expected_present(self):
        names = set(self._names(PerTradeStats))
        for n in self.EXPECTED_PER_TRADE_FIELDS:
            self.assertIn(n, names)

    def test_portfolio_no_forbidden(self):
        names = self._names(PortfolioStats)
        for frag in self.FORBIDDEN_FRAGMENTS:
            for n in names:
                self.assertNotIn(frag.lower(), n.lower())

    def test_portfolio_expected_present(self):
        names = set(self._names(PortfolioStats))
        for n in self.EXPECTED_PORTFOLIO_FIELDS:
            self.assertIn(n, names)

    def test_aggregation_result_attestations(self):
        names = set(self._names(AggregationResult))
        self.assertIn("oos_aggregation_intentionally_omitted", names)
        self.assertIn("post_oos_aggregation_intentionally_omitted", names)
        self.assertIn("live_action_intentionally_blocked", names)
        self.assertIn("downstream_research_promotion_intentionally_blocked", names)

    def test_verdict_is_in_closed_enum(self):
        r = aggregate(_DATA, _SIMS, _SAFETY)
        valid = {
            VerdictReason.PARKED_PROVENANCE_BROKEN,
            VerdictReason.REJECT_FAST,
            VerdictReason.PARKED_SAFETY_FAILED,
            VerdictReason.PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS,
            VerdictReason.PARKED_FAILED_AT_INSUFFICIENT_SAMPLE,
            VerdictReason.PARKED_CAP_BINDING,
            VerdictReason.PARKED_SAFE_BUT_NOT_MONEY_PROVEN,
            VerdictReason.ELIGIBLE_FOR_OOS,
        }
        self.assertIn(r.verdict, valid)


class T11_Determinism(unittest.TestCase):
    def test_same_input_same_output(self):
        r1 = aggregate(_DATA, _SIMS, _SAFETY)
        r2 = aggregate(_DATA, _SIMS, _SAFETY)
        self.assertEqual(r1.verdict, r2.verdict)
        self.assertEqual(r1.portfolio_stats.total_net_pnl_dollars,
                         r2.portfolio_stats.total_net_pnl_dollars)
        self.assertEqual(r1.avg_pairwise_dependence_measure,
                         r2.avg_pairwise_dependence_measure)
        self.assertEqual(r1.effective_independent_bets,
                         r2.effective_independent_bets)
        self.assertEqual(len(r1.per_trade_stats), len(r2.per_trade_stats))
        for a, b in zip(r1.per_trade_stats, r2.per_trade_stats):
            self.assertEqual(a, b)


class T12_NoFileIoAtImport(unittest.TestCase):
    def test_no_io_at_import(self):
        AGG_PKG = ("external_research_hunter."
                   "s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator")
        keys_to_drop = [k for k in list(sys.modules) if AGG_PKG in k]
        saved = {k: sys.modules[k] for k in keys_to_drop}
        for k in keys_to_drop:
            del sys.modules[k]
        captured_open = []
        captured_read = []
        real_open = builtins.open
        real_read = Path.read_bytes

        def _po(*a, **kw):
            if a:
                captured_open.append(a[0])
            return real_open(*a, **kw)

        def _pr(self):
            captured_read.append(str(self))
            return real_read(self)

        builtins.open = _po
        Path.read_bytes = _pr
        try:
            import importlib
            importlib.import_module(AGG_PKG)
        finally:
            builtins.open = real_open
            Path.read_bytes = real_read
            for k, v in saved.items():
                sys.modules[k] = v
        suspect_open = [
            p for p in captured_open
            if isinstance(p, (str, Path))
            and not str(p).endswith((".py", ".pyc"))
        ]
        suspect_read = [
            p for p in captured_read
            if not p.endswith((".py", ".pyc"))
        ]
        self.assertEqual(suspect_open, [])
        self.assertEqual(suspect_read, [])


class T13_ForbiddenTokenGrep(unittest.TestCase):
    TOKENS_THAT_MUST_NOT_APPEAR_IN_AGGREGATOR = (
        "yfinance", "yahoo_finance", "databento", "DATABENTO_API_KEY",
        "Strategy Lab", "review_queue", "idea_memory",
        "live_trading", "brokerage",
        "alpaca", "ibapi", "ib_insync", "tradestation",
        "place_order", "submit_order", "cancel_order", "modify_order",
        "Donchian", "ATR(", "wilder_atr",
        "pyramid_unit", "pyramid_step",
        "STOP_HIT", "STOP_DISTANCE_N_MULTIPLE", "DONCHIAN_20_EXIT",
        "entry_short_triggered", "exit_short_triggered",
        "short_position", "borrow_cost", "borrow_rate",
        "simulate_oos", "compute_oos", "aggregate_oos",
        "post_oos_simulation",
        "force_oos", "skip_oos", "disable_oos_check",
    )

    def setUp(self):
        path = (REPO_ROOT / "external_research_hunter"
                / "s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator"
                / "aggregator.py")
        self.lines = path.read_text(encoding="utf-8").splitlines()
        self.excluded = set()
        for i, line in enumerate(self.lines, start=1):
            if "FORBIDDEN_TOKEN_EXCLUSION" in line:
                self.excluded.add(i)
                self.excluded.add(i + 1)
                self.excluded.add(i + 2)

    def test_no_forbidden_tokens(self):
        for tok in self.TOKENS_THAT_MUST_NOT_APPEAR_IN_AGGREGATOR:
            hits = []
            for i, line in enumerate(self.lines, start=1):
                if tok in line and i not in self.excluded:
                    hits.append((i, line.strip()[:160]))
            self.assertEqual(hits, [],
                f"forbidden token {tok!r} found in aggregator.py: {hits}")


class T14_ForbiddenImportGrep(unittest.TestCase):
    FORBIDDEN_IMPORTS = (
        "import yfinance", "import databento", "import requests",
        "import urllib.", "from urllib", "import http.client",
        "import socket", "import curl_cffi", "import aiohttp",
        "import httpx", "import grpc", "import pyarrow.flight",
        "import strategy_lab", "import sparta_commander",
        "import spartacus", "import hydra_video", "import app",
        "import sparta_brain",
        "import broker", "import interactive_brokers", "import alpaca",
        "import tradestation", "import ibapi", "import binance",
        "import oanda", "import ib_insync",
        "import quantconnect", "import lean", "import qcalgorithm",
        "import pandas", "import numpy", "from pandas", "from numpy",
    )

    def test_no_forbidden_imports(self):
        path = (REPO_ROOT / "external_research_hunter"
                / "s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator"
                / "aggregator.py")
        text = path.read_text(encoding="utf-8")
        for f in self.FORBIDDEN_IMPORTS:
            for ln_no, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                self.assertNotIn(f, stripped,
                    f"forbidden import {f!r} at line {ln_no}: {stripped}")


class T15_PublicApiSurface(unittest.TestCase):
    EXPECTED = sorted([
        "A10_CAP_BINDING_EVENTS_MAX",
        "A1_MIN_CLOSED_TRADES",
        "A2_SHARPE_PROXY_MIN",
        "A3_EXPECTANCY_MIN",
        "A4_TRADE_CURVE_MAXDD_PCT_MAX",
        "A5_PER_MARKET_WR_GAP_MIN_COUNT",
        "A5_PORTFOLIO_WR_GAP_PP_MIN",
        "A7_EFFECTIVE_INDEPENDENT_BETS_MIN",
        "AGateResults",
        "AggregationResult",
        "AggregatorError",
        "AggregatorInputError",
        "AggregatorOosBlockedError",
        "AggregatorParameterOverrideError",
        "AggregatorProvenanceDriftError",
        "CostStressRow",
        "DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION",
        "DR_STRESS_TIERS_REQUIRED",
        "IN_SAMPLE_WINDOW",
        "K10_AVG_PAIRWISE_DEPENDENCE_MAX",
        "K11_CAP_BINDING_EVENTS_MAX",
        "KCriteriaResults",
        "PerSymbolStats",
        "PerTradeStats",
        "PortfolioStats",
        "VerdictReason",
        "aggregate",
    ])

    def test_all_matches(self):
        import importlib
        mod = importlib.import_module(
            "external_research_hunter."
            "s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator"
        )
        observed = sorted(getattr(mod, "__all__", ()))
        self.assertEqual(observed, self.EXPECTED)


class T16_NoSideEffectImportsOfForbiddenModules(unittest.TestCase):
    FORBIDDEN_PRESENCE = (
        "yfinance", "databento", "requests", "urllib3",
        "http.client", "socket",
        "alpaca", "ibapi", "ib_insync", "tradestation", "binance",
        "oanda", "quantconnect", "lean", "qcalgorithm",
        "pandas", "numpy",
    )

    def test_aggregate_does_not_import_forbidden(self):
        before = set(sys.modules.keys())
        _ = aggregate(_DATA, _SIMS, _SAFETY)
        after = set(sys.modules.keys())
        added = after - before
        for f in self.FORBIDDEN_PRESENCE:
            for k in added:
                self.assertNotIn(f, k,
                    f"forbidden module {f!r} imported as side effect via key {k!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
