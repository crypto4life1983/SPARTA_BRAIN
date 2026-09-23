"""Resolve a frozen-regime-input CSV path to the shard that is live on disk.

Why this exists
---------------
`tools/regime_shadow_fresh_data_update.py` merges every
`{asset}_1d_{start}_{end}.csv` shard in `data/frozen_regime_inputs/` into a
single continuous `{asset}_1d_{earliest}_{latest}.csv` and renames the old
shards to `<name>.superseded.<UTC>` (preserved, never deleted). Its own
docstring names the `*.csv` auto-detect glob as the intended consumer
pattern.

Several tools were written before that merge step existed and hardcode the
pre-merge shard names (e.g. `btcusdt_1d_2020-01-01_2022-12-31.csv`). After
the first merge ran those names stopped resolving and the tools raised
`RegimeIntelligenceError: csv not found`.

This resolver closes that gap without changing what data a window sees:

* an exact on-disk match always wins, so nothing changes while the legacy
  shard is present;
* otherwise the single live shard for the same asset + timeframe is used.

Substituting the merged shard is evidence-neutral because the merge is a
date-keyed union of the same rows: every date in each superseded btc/eth/sol
shard is present in the corresponding live shard with an identical close.
Callers still slice by the window's own `lo`/`hi` dates, so a window keeps
resolving to the same rows it did before the merge.

Read-only: this module never writes, renames or deletes anything.
"""
from __future__ import annotations

import re
from pathlib import Path

FROZEN_DIR_NAME = "data/frozen_regime_inputs"
SUPERSEDED_MARKER = ".superseded."

# `{asset}_{timeframe}_{start}_{end}.csv`
_SHARD_RE = re.compile(
    r"^(?P<asset>[A-Za-z0-9]+)_(?P<timeframe>[A-Za-z0-9]+)_"
    r"(?P<start>\d{4}-\d{2}-\d{2})_(?P<end>\d{4}-\d{2}-\d{2})\.csv$"
)


class FrozenShardResolutionError(RuntimeError):
    """Raised when no live shard can stand in for the requested path."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _live_shards(frozen_dir: Path, asset: str, timeframe: str) -> list[Path]:
    """Live (non-superseded) shards for one asset + timeframe."""
    out = []
    for p in sorted(frozen_dir.glob(f"{asset}_{timeframe}_*.csv")):
        if SUPERSEDED_MARKER in p.name:
            continue
        if p.name.startswith("_"):  # `_SAMPLE_SYNTHETIC_*` and friends
            continue
        if _SHARD_RE.match(p.name):
            out.append(p)
    return out


def resolve_frozen_csv(path: str | Path) -> str:
    """Return `path` if it exists, else the live shard that superseded it.

    `path` may be absolute or repo-relative (e.g.
    `data/frozen_regime_inputs/btcusdt_1d_2020-01-01_2022-12-31.csv`).
    The return value is always a string path, so callers can hand it
    straight to `sparta_regime_intelligence.csv_loader.load_frozen_csv`.
    """
    p = Path(path)
    candidate = p if p.is_absolute() else _repo_root() / p
    if candidate.exists():
        return str(path)

    m = _SHARD_RE.match(candidate.name)
    if m is None:
        raise FrozenShardResolutionError(
            f"not a recognised frozen shard filename: {candidate.name}"
        )

    frozen_dir = candidate.parent
    if not frozen_dir.is_dir():
        raise FrozenShardResolutionError(
            f"frozen inputs directory not found: {frozen_dir}"
        )

    live = _live_shards(frozen_dir, m.group("asset"), m.group("timeframe"))
    if len(live) == 1:
        return str(live[0])
    if not live:
        raise FrozenShardResolutionError(
            f"no live shard for {m.group('asset')}_{m.group('timeframe')} "
            f"in {frozen_dir} (requested {candidate.name})"
        )
    raise FrozenShardResolutionError(
        f"{len(live)} live shards for {m.group('asset')}_{m.group('timeframe')} "
        f"in {frozen_dir}; refusing to guess: "
        f"{sorted(x.name for x in live)}"
    )
