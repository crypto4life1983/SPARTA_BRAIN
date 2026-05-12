"""Isolated experimental strategy discovery namespace."""

from .lifecycle import ALLOWED_STATUSES, can_transition, transition_strategy
from .registry import build_strategy_library, normalize_strategy_record

EXPERIMENTAL_MARKER = "EXPERIMENTAL"

