"""Global test isolation for the External Research / Review Queue layer.

Permanent guarantee: no test (fixture data, mock findings, adapter calls,
default-path helpers) can ever read or write the REAL Phase 14B report or
the REAL Phase 14C review queue. Every test gets its own temp report dir.

This redirects ONLY the runtime path override (`_TEST_REPORT_DIR`). The
canonical exported path constants (QUEUE_JSON, PHASE14B_REPORT_JSON, ...)
are deliberately left untouched so the safety verifier's
report-path-under-reports check still sees the real paths and PASSES.
"""

import pytest

from sparta_commander import external_finding_review as _efr
from sparta_commander import external_finding_verification_plan as _efvp
from sparta_commander import external_finding_static_inspection as _efsi
from sparta_commander import external_finding_reimpl_spec as _efrs
from sparta_commander import external_finding_paper_sim_scaffold as _efps
from sparta_commander import external_finding_prereg_plan as _efpp
from sparta_commander import external_finding_prerun_checklist as _efpc
from sparta_commander import external_finding_paper_sim_run as _efpr
from sparta_commander import external_finding_prereg_plan_v2 as _efp2
from sparta_commander import external_finding_prerun_checklist_v2 as _efc2
from sparta_commander import external_finding_paper_sim_run_v2 as _efr2
from sparta_commander import external_finding_closure_report as _efcl
from sparta_commander import nq_mnq_or_prereg as _nqp
from sparta_commander import nq_mnq_or_data_requirements as _nqd
from sparta_commander import nq_mnq_or_data_contract_discovery as _nqdisc
from sparta_commander import nq_mnq_or_folder_staging_report as _nqstg
from sparta_commander import crypto_regime_prereg as _crp
from sparta_commander import crypto_regime_data_contract_discovery as _crpd
from sparta_commander import crypto_regime_folder_staging_report as _crps
from sparta_commander import stat_arb_pair_prereg as _sap
from sparta_commander import stat_arb_pair_data_requirements as _sad
from sparta_commander import copy_research_charter as _crc
from sparta_commander import copy_research_source_registry as _crsr
from sparta_commander import copy_research_observer as _cro
from sparta_commander import copy_research_hypothesis_builder as _crhb
from sparta_commander import external_strategy_discovery_d01 as _esd
from sparta_commander import (
    external_strategy_discovery_d02_seed_intake as _esd2)
from sparta_commander import (
    crypto_regime_data_contract_discovery_rerun as _crpr)
from sparta_commander import crypto_regime_sealed_prereg as _crsp
from sparta_commander import crypto_regime_prerun_checklist as _crpc
from sparta_commander import crypto_regime_phase05_paper_run as _crp5
from sparta_commander import crypto_regime_closure_report as _crcl
from sparta_commander import market_permission_gate as _mpg
from sparta_commander import strategy_evidence_card as _sec
from sparta_commander import strategy_factory_charter as _sfc
from sparta_commander import strategy_factory_source_registry as _sfsr
from sparta_commander import strategy_factory_idea_intake as _sfii
from sparta_commander import strategy_factory_hypothesis_spec as _sfhs
from sparta_commander import strategy_factory_backtest_readiness as _sfbr
from sparta_commander import strategy_factory_data_contract_gate as _sfdcg
from sparta_commander import strategy_factory_template_registry as _sftreg
from sparta_commander import strategy_factory_cost_slippage_registry as _sfcost
from sparta_commander import strategy_factory_phase5_block_idea_draft as _sfblock
from sparta_commander import strategy_factory_phase5_offline_backtest_run as _sfp5
from sparta_commander import external_research_hunter as _erh


# Many tests — and the artifact-drift guard at the bottom of this file —
# resolve project paths relative to the current working directory
# ("strategy_lab/strategies/...", "data/frozen_regime_inputs/...",
# "brain_memory/projects/trading_bot/decisions.md"). Invoked from tests/
# those paths miss: ~60 tests fail with FileNotFoundError, the safety
# layer rejects the resulting tests/strategy_lab/data/... paths, and the
# drift guard silently no-ops because its glob root does not exist.
#
# Pin the working directory to the repo root for the whole session so the
# suite behaves identically however pytest was invoked. Session-scoped and
# defined before the drift guard, so it is in effect when that snapshots.
@pytest.fixture(scope="session", autouse=True)
def _run_from_repo_root():
    import os
    import pathlib

    repo_root = pathlib.Path(__file__).resolve().parents[1]
    previous = os.getcwd()
    os.chdir(repo_root)
    try:
        yield repo_root
    finally:
        os.chdir(previous)


@pytest.fixture(autouse=True)
def _isolate_external_report_paths(tmp_path, monkeypatch):
    iso = tmp_path / "_iso_reports"
    iso.mkdir(parents=True, exist_ok=True)
    # monkeypatch auto-reverts after each test; per-test temp dir = full
    # isolation. Explicit path args still win (these helpers resolve an
    # explicit arg before consulting the override).
    monkeypatch.setattr(_efr, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_erh, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_efvp, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_efsi, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_efrs, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_efps, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_efpp, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_efpc, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_efpr, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_efp2, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_efc2, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_efr2, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_efcl, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_nqp, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_nqd, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_nqdisc, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_nqstg, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_crp, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_crpd, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_crps, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sap, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sad, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_crc, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_crsr, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_cro, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_crhb, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_esd, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_esd2, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_crpr, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_crsp, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_crpc, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_crp5, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_crcl, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_mpg, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sec, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sfc, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sfsr, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sfii, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sfhs, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sfbr, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sfdcg, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sftreg, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sfcost, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sfblock, "_TEST_REPORT_DIR", iso, raising=True)
    monkeypatch.setattr(_sfp5, "_TEST_REPORT_DIR", iso, raising=True)
    yield


# --- Strategy Lab artifact-drift recurrence guard (Option B) ---------------
# Smallest safe, TEST-TIME-ONLY tripwire: detect (and fail loudly) if any
# test run causes a producer (e.g. strategy_lab/robustness_audit.py) to
# write F5 cointegration generated artifacts into the REAL Strategy Lab
# path. It NEVER deletes/moves/modifies anything and changes NO production
# behaviour — it only snapshots the offending glob once per session and
# asserts it did not grow, so the 2026-05-15-style stale-drift cannot
# silently recur. (Pre-existing baseline files, if any, are tolerated;
# only NEW ones created during the session trip the guard.)
@pytest.fixture(scope="session", autouse=True)
def _guard_no_new_f5_cointegration_artifacts():
    import pathlib

    bt = pathlib.Path("strategy_lab/data/backtests")

    def _snapshot() -> set:
        if not bt.is_dir():
            return set()
        return {
            p.name for p in
            (list(bt.glob("*f5*")) + list(bt.glob("btc_eth_cointegration*")))
        }

    before = _snapshot()
    yield
    after = _snapshot()
    created = sorted(after - before)
    assert created == [], (
        "Strategy Lab artifact-drift recurrence: a test run wrote new F5 "
        "cointegration artifacts into strategy_lab/data/backtests "
        f"(producer not test-isolated): {created}. Isolate the producer's "
        "output to a tmp path; do not commit/keep these generated files."
    )
