from __future__ import annotations

from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent
APPROVED_OUTPUT_ROOTS = (
    LAB_ROOT / "reports",
    LAB_ROOT / "data",
    LAB_ROOT / "logs",
)


def is_approved_path(path: str | Path) -> bool:
    candidate = Path(path).resolve()
    return any(candidate == root.resolve() or root.resolve() in candidate.parents for root in APPROVED_OUTPUT_ROOTS)


def assert_approved_path(path: str | Path) -> Path:
    candidate = Path(path).resolve()
    if not is_approved_path(candidate):
        raise ValueError(f"Path is not approved: {candidate}")
    return candidate

