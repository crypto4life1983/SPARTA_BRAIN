"""Tests for tools/frozen_shard_resolver.py.

The resolver exists because `regime_shadow_fresh_data_update.py` merges the
per-period frozen shards into one continuous shard and renames the old ones
to `<name>.superseded.<UTC>`, which broke the hardcoded shard names in the
Phase 4Q/4S regime tools.

Every test builds its own frozen-inputs directory under tmp_path; no file in
data/frozen_regime_inputs/ is read or written here.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from frozen_shard_resolver import (  # noqa: E402
    FrozenShardResolutionError,
    resolve_frozen_csv,
)


def _touch(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("timestamp,close\n2021-01-01,29000.0\n", encoding="utf-8")
    return p


def test_exact_match_is_returned_unchanged(tmp_path: Path) -> None:
    """While the legacy shard is still on disk, nothing changes."""
    d = tmp_path / "frozen"
    legacy = _touch(d / "btcusdt_1d_2020-01-01_2022-12-31.csv")
    _touch(d / "btcusdt_1d_2020-01-01_2026-09-18.csv")

    assert resolve_frozen_csv(legacy) == str(legacy)


def test_superseded_shard_falls_back_to_live_shard(tmp_path: Path) -> None:
    d = tmp_path / "frozen"
    live = _touch(d / "btcusdt_1d_2020-01-01_2026-09-18.csv")
    _touch(d / "btcusdt_1d_2020-01-01_2022-12-31.csv.superseded.20260520T233812Z")

    missing = d / "btcusdt_1d_2020-01-01_2022-12-31.csv"
    assert resolve_frozen_csv(missing) == str(live)


def test_does_not_cross_assets(tmp_path: Path) -> None:
    """An ETH request never resolves to the BTC shard."""
    d = tmp_path / "frozen"
    _touch(d / "btcusdt_1d_2020-01-01_2026-09-18.csv")
    eth_live = _touch(d / "ethusdt_1d_2020-01-01_2026-09-18.csv")

    resolved = resolve_frozen_csv(d / "ethusdt_1d_2020-01-01_2022-12-31.csv")
    assert resolved == str(eth_live)


def test_does_not_cross_timeframes(tmp_path: Path) -> None:
    d = tmp_path / "frozen"
    _touch(d / "btcusdt_1h_2020-01-01_2026-09-18.csv")

    with pytest.raises(FrozenShardResolutionError):
        resolve_frozen_csv(d / "btcusdt_1d_2020-01-01_2022-12-31.csv")


def test_superseded_files_are_never_selected(tmp_path: Path) -> None:
    d = tmp_path / "frozen"
    _touch(d / "btcusdt_1d_2020-01-01_2022-12-31.csv.superseded.20260520T233812Z")

    with pytest.raises(FrozenShardResolutionError):
        resolve_frozen_csv(d / "btcusdt_1d_2020-01-01_2022-12-31.csv")


def test_sample_files_are_ignored(tmp_path: Path) -> None:
    """`_SAMPLE_SYNTHETIC_*` must never stand in for real evidence."""
    d = tmp_path / "frozen"
    _touch(d / "_SAMPLE_SYNTHETIC_btcusdt_1d.csv")

    with pytest.raises(FrozenShardResolutionError):
        resolve_frozen_csv(d / "btcusdt_1d_2020-01-01_2022-12-31.csv")


def test_ambiguous_live_shards_refuse_to_guess(tmp_path: Path) -> None:
    d = tmp_path / "frozen"
    _touch(d / "btcusdt_1d_2020-01-01_2026-09-18.csv")
    _touch(d / "btcusdt_1d_2020-01-01_2026-09-19.csv")

    with pytest.raises(FrozenShardResolutionError) as exc:
        resolve_frozen_csv(d / "btcusdt_1d_2020-01-01_2022-12-31.csv")
    assert "refusing to guess" in str(exc.value)


def test_unrecognised_filename_is_rejected(tmp_path: Path) -> None:
    d = tmp_path / "frozen"
    d.mkdir(parents=True, exist_ok=True)

    with pytest.raises(FrozenShardResolutionError):
        resolve_frozen_csv(d / "not_a_shard_name.csv")


def test_missing_directory_is_reported(tmp_path: Path) -> None:
    with pytest.raises(FrozenShardResolutionError):
        resolve_frozen_csv(
            tmp_path / "nope" / "btcusdt_1d_2020-01-01_2022-12-31.csv"
        )


def test_repo_relative_path_resolves_against_repo_root() -> None:
    """The real repo-relative name the Phase 4Q tools pass must resolve."""
    resolved = resolve_frozen_csv(
        "data/frozen_regime_inputs/btcusdt_1d_2020-01-01_2022-12-31.csv"
    )
    assert Path(resolved).exists()
    assert Path(resolved).name.startswith("btcusdt_1d_")
    assert ".superseded." not in Path(resolved).name
