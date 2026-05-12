from __future__ import annotations

from pathlib import Path

import strategy_lab.safety as safety


def test_strategy_lab_sources_do_not_include_forbidden_integration_words():
    root = Path("strategy_lab")
    assert root.exists()
    forbidden_patterns = [
        "broker",
        "place_order",
        "submit_order",
        "execute_order",
        "live execution",
        "exchange write",
    ]
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for pattern in forbidden_patterns:
            assert pattern not in text, f"Forbidden pattern {pattern!r} found in {path}"


def test_strategy_lab_approved_roots_are_inside_lab():
    lab_root = Path("strategy_lab").resolve()
    for root in safety.APPROVED_OUTPUT_ROOTS:
        resolved = root.resolve()
        assert lab_root in resolved.parents or resolved == lab_root or resolved.parent == lab_root


def test_strategy_lab_safety_rejects_outside_paths():
    outside = Path("C:/Users")
    assert safety.is_approved_path(Path("strategy_lab") / "reports")
    assert not safety.is_approved_path(outside)

