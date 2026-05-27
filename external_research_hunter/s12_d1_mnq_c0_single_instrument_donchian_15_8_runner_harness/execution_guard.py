"""S12-D1 execution_guard: runtime invariant enforcement.

ExecutionGuard objects encapsulate the sealed-spec invariants and
raise RuntimeError on violation. The drivers instantiate a guard
at construction and call its check methods before each strategy step.

P3 BUILD authors this module; the guard is NOT invoked at BUILD
(no driver runs). Future P6/P10/P10.5 phases will exercise it.

No fetch. No Databento. No network. No order submission. No
brokerage connection. Read-only against CONFIG.
"""
from __future__ import annotations

from typing import Optional

from . import runner_main


class GuardViolation(RuntimeError):
    """Raised when any sealed-spec invariant is violated at runtime."""


class ExecutionGuard:
    """Enforces sealed-spec invariants at runtime.

    Instantiated by the IS and OOS drivers. Each `assert_*` method
    raises GuardViolation on violation. Methods that simply check a
    boolean predicate return that bool (no side effect).

    Tracks per-market unit count to enforce `max_units_per_market = 1`
    (no-pyramid invariant) across position lifecycle events.
    """

    def __init__(self):
        self._config = dict(runner_main.CONFIG)
        # Mutable bookkeeping (per-market unit count)
        self._units_open: dict = {}  # symbol -> int

    # ---- Static / class-level invariants ----

    def assert_donchian_15_8_locked(self) -> None:
        if self._config["donchian_entry_period_N"] != 15:
            raise GuardViolation(
                "Donchian-N is not 15 (LOCKED at PLAN; no retreat to 55)"
            )
        if self._config["donchian_exit_period_M"] != 8:
            raise GuardViolation(
                "Donchian-M is not 8 (LOCKED at PLAN; no retreat to 20)"
            )

    def assert_atr_20_2n_locked(self) -> None:
        if self._config["atr_period"] != 20:
            raise GuardViolation("ATR period is not 20")
        if self._config["atr_kind"] != "wilder":
            raise GuardViolation("ATR kind is not 'wilder'")
        if self._config["stop_multiple_n"] != 2.0:
            raise GuardViolation("ATR stop multiplier is not 2.0")

    def assert_per_trade_risk_1pct(self) -> None:
        if self._config["portfolio_risk_per_trade_pct"] != 1.0:
            raise GuardViolation(
                f"per-trade risk is {self._config['portfolio_risk_per_trade_pct']!r}, "
                "not 1.0%"
            )

    def assert_start_cash_100k(self) -> None:
        if self._config["starting_cash_mnq_equivalent_usd"] != 100_000.0:
            raise GuardViolation(
                f"START_CASH is {self._config['starting_cash_mnq_equivalent_usd']!r}, "
                "not $100,000 (DA4=B)"
            )

    def assert_universe_single_instrument_mnq_c0(self) -> None:
        u = tuple(self._config["universe"])
        if u != ("MNQ.c.0",):
            raise GuardViolation(
                f"Universe is {u!r}; expected ('MNQ.c.0',) "
                "(single_instrument_universe_NO_widening_post_seal)"
            )

    def assert_no_pyramid_invariant_held(self) -> None:
        if self._config["no_pyramid"] is not True:
            raise GuardViolation("no_pyramid invariant False at runtime")
        if self._config["max_units_per_market"] != 1:
            raise GuardViolation(
                "max_units_per_market != 1 (no-pyramid violation)"
            )

    def assert_k4_threshold_50pct(self) -> None:
        if self._config["k4_max_drawdown_fraction"] != 0.50:
            raise GuardViolation("K4 max-drawdown fraction is not 0.50")
        if self._config["k4_max_drawdown_abs_usd"] != 50_000.0:
            raise GuardViolation("K4 max-drawdown absolute is not $50,000")

    def assert_warmup_220(self) -> None:
        if self._config["warmup_days"] != 220:
            raise GuardViolation("WARMUP_DAYS is not 220")

    # ---- Dynamic / per-step invariants ----

    def assert_warmup_passed(self, day_index: int) -> None:
        """Raise GuardViolation if day_index is within warmup period.

        Per `no_warmup_order_submission` invariant: NO order may be
        submitted within the first WARMUP_DAYS days.
        """
        warmup = int(self._config["warmup_days"])
        if day_index < warmup:
            raise GuardViolation(
                f"Order attempted at day_index={day_index} which is within "
                f"WARMUP_DAYS={warmup} (no_warmup_order_submission)"
            )

    def attempt_open_unit(self, symbol: str) -> None:
        """Register an attempt to open a new unit on `symbol`.

        Raises GuardViolation if doing so would exceed
        `max_units_per_market = 1` (no-pyramid).
        """
        current = self._units_open.get(symbol, 0)
        new_count = current + 1
        max_units = int(self._config["max_units_per_market"])
        if new_count > max_units:
            raise GuardViolation(
                f"attempt_open_unit on {symbol!r} would yield "
                f"{new_count} units > max_units_per_market={max_units} "
                "(no-pyramid invariant violation)"
            )
        self._units_open[symbol] = new_count

    def register_close_unit(self, symbol: str) -> None:
        """Decrement unit count when a position closes."""
        current = self._units_open.get(symbol, 0)
        if current <= 0:
            raise GuardViolation(
                f"register_close_unit on {symbol!r} with no open units"
            )
        self._units_open[symbol] = current - 1

    def open_units(self, symbol: str) -> int:
        return self._units_open.get(symbol, 0)

    # ---- Negative-action invariants (always raise on call) ----

    def assert_no_live_mode(self) -> None:
        """Sentinel: live-mode invocation MUST raise.

        Future runner code is required to NEVER call SetLiveMode /
        SetBrokerageModel / DeployAlgorithm. This method exists so unit
        tests can verify the guard's stance.
        """
        raise GuardViolation(
            "live mode is BLOCKED_AT_6_GATES (permanent); "
            "no_live_trading invariant"
        )

    def assert_no_brokerage_connection(self) -> None:
        raise GuardViolation(
            "brokerage connection is BLOCKED; no_brokerage_connection invariant"
        )

    def assert_no_databento_runtime_call(self) -> None:
        raise GuardViolation(
            "Databento runtime call is BLOCKED; no_databento_at_runtime invariant"
        )

    def assert_no_strategy_lab_invocation(self) -> None:
        raise GuardViolation(
            "Strategy Lab invocation is BLOCKED; no_strategy_lab_promotion invariant"
        )

    # ---- Composite check ----

    def assert_all_static_invariants_held(self) -> None:
        """Run all static (non-stateful) invariant checks; raise on any failure.

        Called by drivers at construction time. Does NOT call the
        negative-action sentinels (those are designed to raise when called).
        """
        self.assert_donchian_15_8_locked()
        self.assert_atr_20_2n_locked()
        self.assert_per_trade_risk_1pct()
        self.assert_start_cash_100k()
        self.assert_universe_single_instrument_mnq_c0()
        self.assert_no_pyramid_invariant_held()
        self.assert_k4_threshold_50pct()
        self.assert_warmup_220()
