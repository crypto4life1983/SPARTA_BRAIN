"""2026-10-26: block_where cells may name several values (block when the field is any of them),
plus the operator registration helper that writes such a hypothesis as SHADOW."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import trade_hypothesis_ledger as thl  # noqa: E402
from tools import replay_prior as rp  # noqa: E402


def test_sid_with_pipe_parses_to_a_list_and_round_trips():
    kind, params = thl.kind_for_id("blockwhere__volume_bucket=low|normal")
    assert kind == "block_where"
    assert params["where"] == {"volume_bucket": ["low", "normal"]}
    assert thl.where_sid(params["where"]) == "blockwhere__volume_bucket=low|normal"
    # single values are unchanged
    assert thl.kind_for_id("blockwhere__hold_bucket=short")[1]["where"] == {"hold_bucket": "short"}


def test_where_matches_single_and_list():
    assert thl.where_matches("short", "short")
    assert not thl.where_matches("long", "short")
    assert thl.where_matches("low", ["low", "normal"])
    assert not thl.where_matches("high", ["low", "normal"])


def test_evaluate_block_where_with_list_blocks_any_listed_value():
    hyp = {"params": {"where": {"direction": ["long", "short"], "strategy": "D"}}}
    t = {"direction": "long", "strategy": "D", "pnl_r": -1.0, "outcome": "LOSS"}
    assert thl.evaluate_block_where(hyp, t) == 1.0
    t2 = {"direction": "long", "strategy": "F", "pnl_r": -1.0, "outcome": "LOSS"}
    assert thl.evaluate_block_where(hyp, t2) is None


def test_register_block_where_writes_shadow_once():
    ledger = thl.new_ledger()
    ev = {"source": "replay_2026-10-20", "n_blocked": 1490, "mean_R_blocked": 0.023}
    sid = thl.register_block_where(ledger, {"volume_bucket": ["low", "normal"]}, "2026-10-26", ev,
                                   label="REPLAY_PRIOR_ONLY", note="operator go")
    assert sid == "blockwhere__volume_bucket=low|normal"
    h = ledger["hypotheses"][sid]
    assert h["status"] == "SHADOW" and h["kind"] == "block_where"
    assert h["params"]["where"] == {"volume_bucket": ["low", "normal"]}
    assert h["registered_evidence"] == ev and h["registered_label"] == "REPLAY_PRIOR_ONLY"
    assert h["forward"]["n_rows"] == 0 and h["thresholds"]["min_forward_signals"] == 20
    assert "operator go" in h["history"][0]["note"]
    # second call is a no-op
    assert thl.register_block_where(ledger, {"volume_bucket": ["low", "normal"]}, "2026-10-27", ev, "X") is None
    assert h["registered_as_of"] == "2026-10-26"


def test_replay_prior_for_list_cell_sums_minus_R_of_listed_buckets():
    hyp = {"kind": "block_where", "params": {"where": {"volume_bucket": ["low", "normal"]}}}
    taken = [
        {"date": "2025-01-05", "features": {"volume_bucket": "low"}, "res_base": {"R": -1.0}},
        {"date": "2025-02-05", "features": {"volume_bucket": "normal"}, "res_base": {"R": -0.5}},
        {"date": "2025-03-05", "features": {"volume_bucket": "high"}, "res_base": {"R": 2.0}},
    ]
    pr = rp.prior_for(hyp, taken, [], [])
    assert pr["n"] == 2 and pr["sum"] == 1.5
    assert pr["prior_delta_R_mean"] == 0.75
