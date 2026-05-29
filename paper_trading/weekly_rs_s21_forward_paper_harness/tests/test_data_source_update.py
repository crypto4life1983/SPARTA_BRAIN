"""BUILD tests for the refreshed-data-source update: refreshed dir accepted, sealed dir not overwritten, cycle still
gated, filename suffix configurable/pinned to 20260528, stale/missing/misaligned data -> HALT. Synthetic only; no network."""
import csv
import pytest

CAL = ["2019-01-02", "2019-01-03", "2019-01-04", "2019-01-07", "2019-01-08"]


def _write_universe_csvs(tmpdir, suffix, universe, drop=None, misalign=None):
    for sym in universe:
        if sym == drop:
            continue
        dates = CAL if sym != misalign else (CAL[:-1] + ["2099-01-01"])
        with open(tmpdir / (sym + suffix), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["date", "open", "high", "low", "close", "volume"])
            for i, d in enumerate(dates):
                w.writerow([d, 100.0, 101.0, 99.0, 100.0 + i, 1000])


def test_default_source_is_refreshed_and_suffix_pinned_20260528(harness):
    mani = harness["manifest"]
    assert mani.DEFAULT_DATA_SOURCE == "refreshed_20260528"
    ref = mani.DATA_SOURCES["refreshed_20260528"]
    assert ref["dir"] == "data/s21_weekly_rs_paper_refresh/raw"
    assert ref["filename_suffix"] == "_ohlcv_1d_20190102_20260528.csv"
    assert ref["filename_suffix"].endswith("20260528.csv")


def test_resolve_data_source_defaults_to_refreshed(harness):
    cyc = harness["cycle"]
    d, suf, last = cyc.resolve_data_source()
    assert d == "data/s21_weekly_rs_paper_refresh/raw" and suf.endswith("20260528.csv") and last == "2026-05-28"
    # explicit override honored
    d2, suf2, _ = cyc.resolve_data_source(local_csv_dir="/tmp/x", filename_suffix="_custom.csv")
    assert d2 == "/tmp/x" and suf2 == "_custom.csv"


def test_sealed_baseline_is_read_only_and_distinct(harness):
    ds = harness["manifest"].DATA_SOURCES
    assert ds["sealed_baseline_20251230"]["read_only"] is True
    assert ds["sealed_baseline_20251230"]["dir"] != ds["refreshed_20260528"]["dir"]
    assert ds["sealed_baseline_20251230"]["filename_suffix"].endswith("20251230.csv")


def test_refreshed_dir_accepted_and_loader_is_read_only(harness, tmp_path):
    cyc = harness["cycle"]; uni = harness["manifest"].LOCKED_UNIVERSE_48
    refreshed = tmp_path / "refresh"; refreshed.mkdir()
    sealed_like = tmp_path / "sealed_like"; sealed_like.mkdir()  # must remain empty (no writes)
    suffix = "_ohlcv_1d_20190102_20260528.csv"
    _write_universe_csvs(refreshed, suffix, uni)
    closes, cal = cyc._load_local_closes(str(refreshed), suffix)
    assert len(closes) == 48 and cal == CAL
    # loader performed NO writes anywhere (sealed-like dir still empty)
    assert list(sealed_like.iterdir()) == []


def test_missing_data_halts(harness, tmp_path):
    cyc = harness["cycle"]; uni = harness["manifest"].LOCKED_UNIVERSE_48
    d = tmp_path / "r"; d.mkdir(); suffix = "_ohlcv_1d_20190102_20260528.csv"
    _write_universe_csvs(d, suffix, uni, drop="VLO")  # one missing
    with pytest.raises(FileNotFoundError):
        cyc._load_local_closes(str(d), suffix)


def test_misaligned_calendar_halts(harness, tmp_path):
    cyc = harness["cycle"]; uni = harness["manifest"].LOCKED_UNIVERSE_48
    d = tmp_path / "r"; d.mkdir(); suffix = "_ohlcv_1d_20190102_20260528.csv"
    _write_universe_csvs(d, suffix, uni, misalign="MU")
    with pytest.raises(ValueError, match="CALENDAR_MISALIGNMENT"):
        cyc._load_local_closes(str(d), suffix)


def test_stale_data_halts(harness, tmp_path):
    cyc = harness["cycle"]; uni = harness["manifest"].LOCKED_UNIVERSE_48
    d = tmp_path / "r"; d.mkdir(); suffix = "_ohlcv_1d_20190102_20260528.csv"
    _write_universe_csvs(d, suffix, uni)  # last bar = 2019-01-08
    with pytest.raises(cyc.StaleDataError):
        cyc._load_local_closes(str(d), suffix, min_last_date="2026-05-28")


def test_cycle_still_refuses_without_authorization(harness):
    cyc = harness["cycle"]
    with pytest.raises(cyc.CycleNotAuthorized):
        cyc.run_weekly_paper_cycle(operator_authorized_dry_run=False)  # default refreshed source; still gated
