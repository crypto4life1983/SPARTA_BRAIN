"""Regression: app.py once defined `_HOOK_PATTERNS` twice (a dict for the
learning-insights pattern detector and a list for product hook selection).
The list shadowed the dict, so `/api/learning/insights` raised
AttributeError ('list' object has no attribute 'items') since 2026-04-30.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app as _app  # noqa: E402


def test_hook_pattern_tables_are_distinct_types():
    assert isinstance(_app._HOOK_PATTERNS, dict)
    assert isinstance(_app._PRODUCT_HOOK_PATTERNS, list)


def test_detect_hook_patterns_returns_keys():
    keys = _app._detect_hook_patterns("Stop doing this with your money?")
    assert "stop_doing" in keys
    assert "question" in keys
    assert _app._detect_hook_patterns("") == []


def test_learning_insights_endpoint_does_not_crash():
    payload = _app.api_learning_insights()
    assert isinstance(payload, dict)
    assert "top_thresh" in payload or len(payload) > 0
