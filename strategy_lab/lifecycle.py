from __future__ import annotations

ALLOWED_STATUSES = (
    "IDEA",
    "IN_RESEARCH",
    "BACKTESTED",
    "ROBUST",
    "PAPER_TESTING",
    "WATCHLIST",
    "REJECTED",
    "EXPIRED",
)

_TRANSITIONS = {
    "IDEA": {"IN_RESEARCH"},
    "IN_RESEARCH": {"BACKTESTED"},
    "BACKTESTED": {"ROBUST"},
    "ROBUST": {"PAPER_TESTING"},
    "PAPER_TESTING": {"WATCHLIST"},
}

_ALWAYS_ALLOWED = {"REJECTED", "EXPIRED"}
_FORBIDDEN = {"LIVE"}


def normalize_status(status: str | None) -> str:
    value = str(status or "IDEA").upper()
    if value not in ALLOWED_STATUSES and value not in _FORBIDDEN:
        raise ValueError(f"Unknown status: {status!r}")
    return value


def can_transition(current: str | None, target: str | None) -> bool:
    current_status = normalize_status(current)
    target_status = normalize_status(target)
    if target_status in _FORBIDDEN:
        return False
    if target_status in _ALWAYS_ALLOWED:
        return True
    if current_status == target_status:
        return True
    return target_status in _TRANSITIONS.get(current_status, set())


def transition_strategy(current: str | None, target: str | None) -> str:
    if not can_transition(current, target):
        raise ValueError(f"Transition not allowed: {current!r} -> {target!r}")
    return normalize_status(target)

