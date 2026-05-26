"""T1-T16 test suite for the s7 D1 cross-asset yfinance proxy result aggregator.

Run from repo root with stdlib unittest:
    python tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/test_aggregator.py

Plan anchor:
  docs/s7_d1_cross_asset_donchian_step_07_result_aggregation_specification_plan.md
  sha256 fc0f0dcd34b75055405fc1ba2bbbf4a60e57e2bb1a692feb86999c31e3108983
"""
from __future__ import annotations

import builtins
import dataclasses
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import (  # noqa: E402
    load_all,
)
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_signal import (  # noqa: E402
    compute_signals_all,
)
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_simulator import (  # noqa: E402
    CostTier,
    ExitReason,
    SimulationResult,
    TradeGroup,
    TradeUnit,
    simulate,
)
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_aggregator import (  # noqa: E402
    AGateResults,
    AggregationResult,
    AggregatorError,
    AggregatorInputError,
    AggregatorOosBlockedError,
    AggregatorParameterOverrideError,
    AggregatorProvenanceDriftError,
    CostStressRow,
    DR_STRESS_TIERS_REQUIRED,
    IN_SAMPLE_WINDOW,
    KCriteriaResults,
    PerSymbolStats,
    PerTradeStats,
    PortfolioStats,
    VerdictReason,
    aggregate,
)

AGG_PKG = "external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_aggregator"


# Cached real-data fixture so 4-tier simulation runs only once across tests.
_REAL_FIXTURE = None


def _real_fixture():
    global _REAL_FIXTURE
    if _REAL_FIXTURE is None:
        loaded = load_all()
        sigs = compute_signals_all(loaded)
        sims = {t.value: simulate(loaded, sigs, cost_tier=t)
                for t in (CostTier.S0, CostTier.S1, CostTier.S2, CostTier.S3)}
        safety = {f"C{i}": True for i in range(1, 9)}
        _REAL_FIXTURE = (loaded, sims, safety)
    return _REAL_FIXTURE


def _synth_unit(symbol, group_id, idx, trigger_date, fill_date, fill_price,
                shares, stop_price, exit_date, exit_price, exit_reason,
                n_entry, gross, net):
    return TradeUnit(
        symbol=symbol,
        trade_group_id=group_id,
        unit_index=idx,
        entry_trigger_date=trigger_date,
        entry_fill_date=fill_date,
        entry_fill_price=fill_price,
        entry_slippage_dollars=0.0,
        n_entry_dollars=n_entry,
        shares=shares,
        stop_price_at_entry=stop_price,
        exit_date=exit_date,
        exit_fill_price=exit_price,
        exit_slippage_dollars=0.0,
        exit_reason=exit_reason,
        commission_dollars=0.0,
        gross_pnl_dollars=gross,
        net_pnl_dollars=net,
    )


def _synth_group(symbol, group_id, direction, n_entry, open_date, close_date,
                 unit_pnls, close_reason):
    """Build a TradeGroup with len(unit_pnls) units; each unit has the given net PnL."""
    units = []
    for i, pnl in enumerate(unit_pnls):
        units.append(_synth_unit(
            symbol=symbol, group_id=group_id, idx=i,
            trigger_date=open_date, fill_date=open_date, fill_price=100.0,
            shares=10, stop_price=99.0, exit_date=close_date,
            exit_price=100.0 + pnl / 10.0, exit_reason=close_reason,
            n_entry=n_entry, gross=pnl, net=pnl,
        ))
    total_gross = sum(u.gross_pnl_dollars for u in units)
    total_net = sum(u.net_pnl_dollars for u in units)
    return TradeGroup(
        symbol=symbol,
        trade_group_id=group_id,
        direction=direction,
        n_entry_dollars=n_entry,
        trigger_date_unit_0=open_date,
        units=tuple(units),
        group_open_date=open_date,
        group_close_date=close_date,
        group_gross_pnl_dollars=total_gross,
        group_net_pnl_dollars=total_net,
        group_unit_count=len(units),
        group_close_reason=close_reason,
    )


def _synth_sim(tier, slip_scalar, comm_scalar, trade_groups, starting_cash=100000.0):
    return SimulationResult(
        starting_cash=starting_cash,
        final_cash_balance=starting_cash + sum(g.group_net_pnl_dollars for g in trade_groups),
        cost_tier=tier,
        cost_tier_slippage_scalar=slip_scalar,
        cost_tier_commission_scalar=comm_scalar,
        trade_groups=tuple(trade_groups),
        trade_groups_per_symbol={s: sum(1 for g in trade_groups if g.symbol == s)
                                  for s in ("SPY", "TLT", "GLD", "USO")},
        num_closed_units_total=sum(g.group_unit_count for g in trade_groups),
        num_closed_units_per_symbol={s: sum(g.group_unit_count for g in trade_groups if g.symbol == s)
                                      for s in ("SPY", "TLT", "GLD", "USO")},
        daily_equity_ledger=(),
        max_drawdown_pct_observed=0.0,
        k4_fired=False,
        in_sample_window=IN_SAMPLE_WINDOW,
        first_signal_date_processed="2014-03-24",
        last_signal_date_processed="2022-12-30",
        entry_skip_log=(),
        oos_simulation_intentionally_omitted=True,
        post_oos_simulation_intentionally_omitted=True,
    )


class T01_ImportsOnlyAllowedModules(unittest.TestCase):
    """T1: aggregator.py imports stdlib only (no external network/vendor SDK)."""

    def test_imports(self):
        src = (REPO_ROOT
               / "external_research_hunter"
               / "s7_d1_cross_asset_donchian_yfinance_proxy_aggregator"
               / "aggregator.py").read_text(encoding="utf-8")
        forbidden = [
            "import yfinance", "import databento", "import requests",
            "import urllib.", "from urllib", "import http.client",
            "import socket", "import curl_cffi", "import aiohttp",
            "import httpx", "import grpc",
            "import strategy_lab", "import sparta_commander",
            "import broker", "import interactive_brokers", "import alpaca",
            "import ibapi", "import quantconnect", "import lean",
        ]
        for line in src.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for f in forbidden:
                self.assertNotIn(f, stripped, f"forbidden import: {f}")


class T02_EveryDateInInSampleWindow(unittest.TestCase):
    """T2: every per_trade and per_symbol and portfolio computation
    operates over IS dates only (verified by inspecting per_trade_stats dates)."""

    def test_dates(self):
        loaded, sims, safety = _real_fixture()
        r = aggregate(loaded, sims, safety)
        for pt in r.per_trade_stats:
            self.assertGreaterEqual(pt.trade_open_date, IN_SAMPLE_WINDOW[0])
            self.assertLessEqual(pt.trade_close_date, IN_SAMPLE_WINDOW[1])


class T03_OosInjectionBlocked(unittest.TestCase):
    """T3: synthetic SimulationResult with a TradeGroup whose close_date is OOS;
    aggregate raises AggregatorOosBlockedError."""

    def test_oos_block(self):
        loaded, sims, safety = _real_fixture()
        # Build a clone of the S1 sim with an OOS-dated TradeGroup injected
        s1 = sims["S1"]
        bad_group = _synth_group(
            symbol="SPY", group_id="tg_bad", direction="long",
            n_entry=2.0, open_date="2024-06-15", close_date="2024-06-20",
            unit_pnls=[100.0], close_reason=ExitReason.DONCHIAN_20_EXIT,
        )
        bad_sim = dataclasses.replace(
            s1, trade_groups=tuple(list(s1.trade_groups) + [bad_group]),
        )
        bad_sims = dict(sims)
        bad_sims["S1"] = bad_sim
        with self.assertRaises(AggregatorOosBlockedError):
            aggregate(loaded, bad_sims, safety)


class T04_NoLiveTradingCodePath(unittest.TestCase):
    """T4: aggregate accepts only the three positional args; extra kwargs raise."""

    def test_extra_kwargs(self):
        loaded, sims, safety = _real_fixture()
        with self.assertRaises(AggregatorParameterOverrideError):
            aggregate(loaded, sims, safety, broker="alpaca")
        with self.assertRaises(AggregatorParameterOverrideError):
            aggregate(loaded, sims, safety, enable_oos=True)


class T05_NoBrokerageOrStrategyLabImportInAggregatorSource(unittest.TestCase):
    """T5: static grep for brokerage / Strategy Lab / review_queue tokens (outside FORBIDDEN_TOKEN_EXCLUSION lines)."""

    def test_grep(self):
        src = (REPO_ROOT
               / "external_research_hunter"
               / "s7_d1_cross_asset_donchian_yfinance_proxy_aggregator"
               / "aggregator.py").read_text(encoding="utf-8")
        for tok in ("brokerage", "alpaca", "interactive_brokers", "ibkr",
                    "Strategy Lab", "strategy_lab", "review_queue", "idea_memory",
                    "order_send", "place_order", "submit_order"):
            for ln_no, line in enumerate(src.splitlines(), start=1):
                if tok in line:
                    stripped = line.strip()
                    if stripped.startswith("#") and "FORBIDDEN_TOKEN_EXCLUSION" in line:
                        continue
                    self.fail(f"forbidden token {tok!r} in aggregator.py line {ln_no}: {line.strip()[:160]}")


class T06_Determinism(unittest.TestCase):
    """T6: aggregate twice produces field-equal AggregationResult."""

    def test_determinism(self):
        loaded, sims, safety = _real_fixture()
        r1 = aggregate(loaded, sims, safety)
        r2 = aggregate(loaded, sims, safety)
        self.assertEqual(r1.verdict, r2.verdict)
        self.assertEqual(r1.portfolio_stats, r2.portfolio_stats)
        self.assertEqual(r1.k_criteria_results, r2.k_criteria_results)
        self.assertEqual(r1.a_gate_results, r2.a_gate_results)
        self.assertEqual(r1.per_trade_stats, r2.per_trade_stats)
        self.assertEqual(r1.cost_stress_matrix, r2.cost_stress_matrix)


class T07_ParameterOverrideRejected(unittest.TestCase):
    """T7: lookback= / window= / enable_oos= kwargs raise."""

    def test_unknown_kwarg(self):
        loaded, sims, safety = _real_fixture()
        with self.assertRaises(AggregatorParameterOverrideError):
            aggregate(loaded, sims, safety, lookback=50)
        with self.assertRaises(AggregatorParameterOverrideError):
            aggregate(loaded, sims, safety, window=("1999-01-01", "2099-12-31"))


class T08_NoVendorOrNetworkImports(unittest.TestCase):
    """T8: aggregator.py contains no Databento / yfinance / network import."""

    def test_grep(self):
        src = (REPO_ROOT
               / "external_research_hunter"
               / "s7_d1_cross_asset_donchian_yfinance_proxy_aggregator"
               / "aggregator.py").read_text(encoding="utf-8")
        for tok in ("yfinance", "databento", "yahoo_finance", "DATABENTO_API_KEY",
                    "requests.get", "urllib.request", "socket.connect"):
            for ln_no, line in enumerate(src.splitlines(), start=1):
                if tok in line:
                    stripped = line.strip()
                    if stripped.startswith("#") and "FORBIDDEN_TOKEN_EXCLUSION" in line:
                        continue
                    self.fail(f"forbidden vendor/network token {tok!r} in line {ln_no}: {line.strip()[:160]}")


class T09_NoProductionRefs(unittest.TestCase):
    """T9: no scheduler / autopilot / FRC-gate / live trading references."""

    def test_grep(self):
        src = (REPO_ROOT
               / "external_research_hunter"
               / "s7_d1_cross_asset_donchian_yfinance_proxy_aggregator"
               / "aggregator.py").read_text(encoding="utf-8")
        for tok in ("scheduler", "autopilot", "frc_gate",
                    "live trading", "live_trading", "production_signal",
                    "paper_broker", "paper_trade"):
            for ln_no, line in enumerate(src.splitlines(), start=1):
                if tok in line:
                    stripped = line.strip()
                    if stripped.startswith("#") and "FORBIDDEN_TOKEN_EXCLUSION" in line:
                        continue
                    self.fail(f"forbidden production token {tok!r} in line {ln_no}: {line.strip()[:160]}")


class T10_CostStressMatrixRequiresFourTiers(unittest.TestCase):
    """T10: missing any of S0/S1/S2/S3 raises AggregatorInputError."""

    def test_missing_tier(self):
        loaded, sims, safety = _real_fixture()
        partial_sims = {k: v for k, v in sims.items() if k != "S2"}
        with self.assertRaises(AggregatorInputError):
            aggregate(loaded, partial_sims, safety)


class T11_K8SealedParentDriftVerdict(unittest.TestCase):
    """T11: in-memory tamper of a LoadedSymbol.csv_sha256 -> verdict
    PARKED_PROVENANCE_BROKEN (K8 fires)."""

    def test_k8_drift(self):
        loaded, sims, safety = _real_fixture()
        # Build a tampered loaded with one symbol having a wrong sha256
        tampered = dict(loaded)
        spy = tampered["SPY"]
        tampered_spy = dataclasses.replace(spy, csv_sha256="0" * 64)
        tampered["SPY"] = tampered_spy
        r = aggregate(tampered, sims, safety)
        self.assertEqual(r.verdict, VerdictReason.PARKED_PROVENANCE_BROKEN)
        self.assertTrue(r.k_criteria_results.K8_sealed_parent_drift)


class T12_K9SampleSizeVerdict(unittest.TestCase):
    """T12: synthesize a result with < 100 trades across all tiers; verify
    one of the verdict paths fires (REJECT_FAST takes priority over K9
    if DR rules fire; the synthetic here avoids DR fires by keeping all
    tiers identical so cost-stress is flat)."""

    def test_k9(self):
        loaded, sims, safety = _real_fixture()
        # Build a synthetic four-tier sim with only 10 trades each, all small positive,
        # cost-stress is flat (S0==S1==S2==S3 PnL).
        groups = [_synth_group(
            symbol=("SPY", "TLT", "GLD", "USO")[i % 4],
            group_id=f"tg_{i:04d}", direction="long",
            n_entry=2.0,
            open_date=f"2015-{(i % 12) + 1:02d}-15",
            close_date=f"2015-{(i % 12) + 1:02d}-20",
            unit_pnls=[100.0], close_reason=ExitReason.DONCHIAN_20_EXIT,
        ) for i in range(10)]
        synth_sims = {
            "S0": _synth_sim("S0", 0.0, 0.0, groups),
            "S1": _synth_sim("S1", 1.0, 1.0, groups),
            "S2": _synth_sim("S2", 3.0, 1.5, groups),
            "S3": _synth_sim("S3", 5.0, 2.0, groups),
        }
        r = aggregate(loaded, synth_sims, safety)
        self.assertTrue(r.k_criteria_results.K9_closed_trades_below_100)
        # Without DR fires, K9 dominates -> PARKED_FAILED_AT_INSUFFICIENT_SAMPLE.
        self.assertEqual(r.verdict, VerdictReason.PARKED_FAILED_AT_INSUFFICIENT_SAMPLE)


class T13_AllAPassEligibleForOos(unittest.TestCase):
    """T13: synthesize a four-tier matrix where all A1-A10 pass and no K fires;
    verdict is ELIGIBLE_FOR_OOS. Uses real loaded for pairwise dependence
    (which is real-data-driven and confirmed PASS at A7 in smoke test)."""

    def test_eligible(self):
        loaded, _sims, safety = _real_fixture()
        # Build >=100 trades distributed across 4 symbols, with positive expectancy,
        # win rate well above breakeven, and identical across tiers (no DR fire).
        # Mix of wins and losses so P/L ratio and WR-gap both look healthy.
        groups = []
        per_sym_groups = {s: 30 for s in ("SPY", "TLT", "GLD", "USO")}  # 120 trades total
        for sym in ("SPY", "TLT", "GLD", "USO"):
            for i in range(per_sym_groups[sym]):
                # 60% wins of $200, 40% losses of $50  => P/L=4, WR=0.6, IBWR=0.2
                # Win-rate-gap = (0.6 - 0.2) * 100 = +40 pp
                is_win = (i % 5) < 3   # 3/5 = 60% wins
                pnl = 200.0 if is_win else -50.0
                groups.append(_synth_group(
                    symbol=sym, group_id=f"tg_{sym}_{i:04d}",
                    direction="long", n_entry=1.0,
                    open_date=f"2016-{((i % 12) + 1):02d}-15",
                    close_date=f"2016-{((i % 12) + 1):02d}-20",
                    unit_pnls=[pnl],
                    close_reason=ExitReason.DONCHIAN_20_EXIT,
                ))
        synth_sims = {
            "S0": _synth_sim("S0", 0.0, 0.0, groups),
            "S1": _synth_sim("S1", 1.0, 1.0, groups),
            "S2": _synth_sim("S2", 3.0, 1.5, groups),
            "S3": _synth_sim("S3", 5.0, 2.0, groups),
        }
        # Use real loaded for pairwise dependence (real-data avg pair dep is ~0.04 -> A7 PASS)
        r = aggregate(loaded, synth_sims, safety)
        # Sanity-check the expected sub-results
        self.assertFalse(r.k_criteria_results.K9_closed_trades_below_100,
                         f"K9 unexpectedly fires; total={r.portfolio_stats.total_closed_trades}")
        self.assertFalse(r.k_criteria_results.K12_dr_fires,
                         f"K12 unexpectedly fires; DR={r.dr_rule_fires}")
        self.assertEqual(r.verdict, VerdictReason.ELIGIBLE_FOR_OOS,
                         f"got {r.verdict.value} explanation: {r.verdict_explanation}")


class T14_DR2FireRejectFast(unittest.TestCase):
    """T14: synthesize cost-stress where S2 is half of S1 (and S0/S1 both positive);
    DR2 fires; K12 fires; verdict REJECT_FAST."""

    def test_dr2(self):
        loaded, _, safety = _real_fixture()
        # Build a baseline S1 with 100 trades of +$200; S0 +$300; S2 +$50 (much less than half);
        # S3 +$50 (also less than half).
        def make_groups(pnl_each, n=120):
            return [_synth_group(
                symbol=("SPY","TLT","GLD","USO")[i % 4],
                group_id=f"g_{i:04d}", direction="long", n_entry=1.0,
                open_date=f"2017-{((i % 12) + 1):02d}-15",
                close_date=f"2017-{((i % 12) + 1):02d}-20",
                unit_pnls=[pnl_each], close_reason=ExitReason.DONCHIAN_20_EXIT,
            ) for i in range(n)]
        synth_sims = {
            "S0": _synth_sim("S0", 0.0, 0.0, make_groups(300.0)),
            "S1": _synth_sim("S1", 1.0, 1.0, make_groups(200.0)),
            "S2": _synth_sim("S2", 3.0, 1.5, make_groups(50.0)),   # 50 / 200 = 25% < 50% threshold
            "S3": _synth_sim("S3", 5.0, 2.0, make_groups(50.0)),
        }
        r = aggregate(loaded, synth_sims, safety)
        self.assertTrue(r.dr_rule_fires["DR2_S2_or_S3_degrades_materially"])
        self.assertTrue(r.k_criteria_results.K12_dr_fires)
        self.assertEqual(r.verdict, VerdictReason.REJECT_FAST)


class T15_DR3FireRejectFast(unittest.TestCase):
    """T15: synthesize cost-stress where S0 positive but S2 non-positive (DR3 fires)."""

    def test_dr3(self):
        loaded, _, safety = _real_fixture()
        def make_groups(pnl_each, n=120):
            return [_synth_group(
                symbol=("SPY","TLT","GLD","USO")[i % 4],
                group_id=f"g_{i:04d}", direction="long", n_entry=1.0,
                open_date=f"2018-{((i % 12) + 1):02d}-15",
                close_date=f"2018-{((i % 12) + 1):02d}-20",
                unit_pnls=[pnl_each], close_reason=ExitReason.DONCHIAN_20_EXIT,
            ) for i in range(n)]
        # S0 positive, S1 positive AND > 50% of S0 (avoid DR2/DR5), S2 non-positive (DR3 fires).
        synth_sims = {
            "S0": _synth_sim("S0", 0.0, 0.0, make_groups(300.0)),    # 36000 net
            "S1": _synth_sim("S1", 1.0, 1.0, make_groups(250.0)),    # 30000 net (83% of S0)
            "S2": _synth_sim("S2", 3.0, 1.5, make_groups(0.0)),      # 0 net <= 0 -> DR3 fires
            "S3": _synth_sim("S3", 5.0, 2.0, make_groups(200.0)),    # positive
        }
        # Note: S2 at 0 also satisfies DR2 (0 < 50% of 30000). Both DR2 and DR3 fire.
        r = aggregate(loaded, synth_sims, safety)
        self.assertTrue(r.dr_rule_fires["DR3_zero_cost_only_survival"])
        self.assertTrue(r.k_criteria_results.K12_dr_fires)
        self.assertEqual(r.verdict, VerdictReason.REJECT_FAST)


class T16_DR5FireRejectFast(unittest.TestCase):
    """T16: synthesize cost-stress where S0 positive AND S1 non-positive (DR5 fires)."""

    def test_dr5(self):
        loaded, _, safety = _real_fixture()
        def make_groups(pnl_each, n=120):
            return [_synth_group(
                symbol=("SPY","TLT","GLD","USO")[i % 4],
                group_id=f"g_{i:04d}", direction="long", n_entry=1.0,
                open_date=f"2019-{((i % 12) + 1):02d}-15",
                close_date=f"2019-{((i % 12) + 1):02d}-20",
                unit_pnls=[pnl_each], close_reason=ExitReason.DONCHIAN_20_EXIT,
            ) for i in range(n)]
        synth_sims = {
            "S0": _synth_sim("S0", 0.0, 0.0, make_groups(300.0)),
            "S1": _synth_sim("S1", 1.0, 1.0, make_groups(-100.0)),   # negative -> DR5 fires
            "S2": _synth_sim("S2", 3.0, 1.5, make_groups(-150.0)),
            "S3": _synth_sim("S3", 5.0, 2.0, make_groups(-200.0)),
        }
        r = aggregate(loaded, synth_sims, safety)
        self.assertTrue(r.dr_rule_fires["DR5_S0_to_S1_edge_negative"])
        self.assertTrue(r.dr_rule_fires["DR3_zero_cost_only_survival"])
        self.assertTrue(r.k_criteria_results.K12_dr_fires)
        self.assertEqual(r.verdict, VerdictReason.REJECT_FAST)


if __name__ == "__main__":
    unittest.main(verbosity=2)
