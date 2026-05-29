"""Deterministic, offline strategy-parameter proposer.

OFFLINE / DETERMINISTIC: no AI API calls, no network, no randomness beyond a
seeded generator. Given a search space it enumerates NQ ORB parameter
variants in a stable, reproducible order so a run is fully repeatable.

This is the "AI proposes strategy" step of the loop, implemented as a safe,
local grid search rather than any external model call.
"""

from __future__ import annotations

import itertools
import random
from typing import List, Dict, Any


def base_params() -> Dict[str, Any]:
    """Default NQ ORB params (mirrors config\\factory_config.yaml)."""
    return {
        "opening_range_minutes": 15,
        "target_r_multiple": 2.0,
        "session_start": "09:30",
        "session_end": "16:00",
        "stop_mode": "opposite_range",
        "one_trade_per_day": True,
    }


def propose_variants(
    search_opening_range_minutes: List[int] | None = None,
    search_target_r_multiple: List[float] | None = None,
    seed: int = 23,
) -> List[Dict[str, Any]]:
    """Enumerate parameter variants deterministically.

    The full grid is built, then shuffled with a *seeded* generator so the
    ordering is stable across runs (reproducible, not truly random).
    """
    or_minutes = search_opening_range_minutes or [5, 10, 15, 30]
    target_rs = search_target_r_multiple or [1.5, 2.0, 3.0]

    grid = list(itertools.product(or_minutes, target_rs))
    rng = random.Random(seed)
    rng.shuffle(grid)

    variants: List[Dict[str, Any]] = []
    for orm, tr in grid:
        params = base_params()
        params["opening_range_minutes"] = int(orm)
        params["target_r_multiple"] = float(tr)
        variants.append(params)
    return variants


def next_proposal(history: List[Dict[str, Any]] | None = None, seed: int = 23) -> Dict[str, Any]:
    """Return the next untried variant given a history of tried param dicts.

    History items are param dicts previously proposed. Returns the first
    variant from the deterministic ordering not already present in history.
    Falls back to base_params() when the grid is exhausted.
    """
    history = history or []

    def _key(p: Dict[str, Any]):
        return (p.get("opening_range_minutes"), p.get("target_r_multiple"))

    tried = {_key(p) for p in history}
    for variant in propose_variants(seed=seed):
        if _key(variant) not in tried:
            return variant
    return base_params()
