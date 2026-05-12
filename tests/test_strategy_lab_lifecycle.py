from __future__ import annotations

import pytest

from strategy_lab.lifecycle import ALLOWED_STATUSES, can_transition, transition_strategy


def test_lifecycle_allows_only_documented_forward_transitions():
    assert "LIVE" not in ALLOWED_STATUSES
    assert can_transition("IDEA", "IN_RESEARCH")
    assert can_transition("IN_RESEARCH", "BACKTESTED")
    assert can_transition("BACKTESTED", "ROBUST")
    assert can_transition("ROBUST", "PAPER_TESTING")
    assert can_transition("PAPER_TESTING", "WATCHLIST")


def test_lifecycle_allows_reject_and_expire_from_any_state():
    for state in ALLOWED_STATUSES:
        assert can_transition(state, "REJECTED")
        assert can_transition(state, "EXPIRED")


def test_lifecycle_blocks_live():
    for state in ALLOWED_STATUSES:
        assert not can_transition(state, "LIVE")
        with pytest.raises(ValueError):
            transition_strategy(state, "LIVE")


def test_lifecycle_rejects_invalid_jump():
    assert not can_transition("IDEA", "ROBUST")
    with pytest.raises(ValueError):
        transition_strategy("IDEA", "ROBUST")

