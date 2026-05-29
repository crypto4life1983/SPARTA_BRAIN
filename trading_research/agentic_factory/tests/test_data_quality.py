"""Tests for the offline data-quality scanner. Local CSV only, no network."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import data_quality  # noqa: E402


_HEADER = "ts_event,open,high,low,close,volume,symbol\n"


def _write(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(body)
    return str(p)


def _bar(ts, o=100.0, h=101.0, lo=99.0, c=100.5):
    return f"{ts},{o},{h},{lo},{c},10,NQ\n"


def test_valid_csv_basic_fields(tmp_path):
    body = _HEADER + _bar("2023-12-26 14:30:00+00:00") + _bar("2023-12-26 14:45:00+00:00")
    path = _write(tmp_path, "ok.csv", body)
    rep = data_quality.scan_csv(path)

    assert rep["row_count"] == 2
    assert rep["required_columns_present"] is True
    assert rep["missing_columns"] == []
    assert rep["timezone_aware"] is True
    assert rep["first_timestamp"].startswith("2023-12-26T14:30:00")
    assert rep["last_timestamp"].startswith("2023-12-26T14:45:00")
    assert rep["distinct_dates"] == 1


def test_missing_timestamp_column(tmp_path):
    body = "open,high,low,close,volume,symbol\n100,101,99,100.5,10,NQ\n"
    path = _write(tmp_path, "no_ts.csv", body)
    rep = data_quality.scan_csv(path)  # default ts col 'ts_event' absent

    assert rep["required_columns_present"] is False
    assert "ts_event" in rep["missing_columns"]
    assert rep["verdict"] == data_quality.UNUSABLE
    assert rep["readiness"]["serious_research"] is False


def test_duplicate_timestamp_detection(tmp_path):
    ts = "2023-12-26 14:30:00+00:00"
    body = _HEADER + _bar(ts) + _bar(ts)  # same timestamp twice
    path = _write(tmp_path, "dupe.csv", body)
    rep = data_quality.scan_csv(path)

    assert rep["duplicate_timestamps"] == 1


def test_bad_ohlc_row_detection(tmp_path):
    good = _bar("2023-12-26 14:30:00+00:00")
    # high (90) below low (99) -> invalid
    bad = _bar("2023-12-26 14:31:00+00:00", o=100.0, h=90.0, lo=99.0, c=95.0)
    # non-numeric close -> invalid
    bad2 = "2023-12-26 14:32:00+00:00,100,101,99,abc,10,NQ\n"
    path = _write(tmp_path, "bad_ohlc.csv", _HEADER + good + bad + bad2)
    rep = data_quality.scan_csv(path)

    assert rep["invalid_ohlc_rows"] == 2


def test_too_small_dataset_needs_more_data(tmp_path):
    body = _HEADER + _bar("2023-12-26 14:30:00+00:00") + _bar("2023-12-26 15:00:00+00:00")
    path = _write(tmp_path, "tiny.csv", body)
    rep = data_quality.scan_csv(path)

    assert rep["readiness"]["serious_research"] is False
    assert rep["readiness"]["profitability_conclusion"] is False
    assert rep["verdict"] == data_quality.NEEDS_MORE_DATA
    # One eligible session is still enough for plumbing/smoke.
    assert rep["readiness"]["plumbing_test"] is True
    assert rep["readiness"]["smoke_test"] is True
