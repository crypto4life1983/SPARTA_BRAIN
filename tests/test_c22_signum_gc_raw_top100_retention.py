"""Tests for the additive raw top-100 immutable retention in the C22 import path.

All fixtures are synthetic in-memory windows written to temporary directories; no real window
is imported and the canonical dataset/checkpoint is never touched.
"""
import hashlib
import json

import tools.c22_signum_gc_local_export_importer_once as runner


def _cndl(c, upper, filt, trend="Green", h=None, date="2026-06-28"):
    h = c + 1 if h is None else h
    return {"ohlc": {"o": c, "h": h, "l": c - 1, "c": c},
            "gc": {"trend": trend, "upper": upper, "filter": filt}, "date": date}


def _row(symbol, rank, rd):
    return {"detector": "gc", "assetClass": "crypto", "runDate": rd, "symbol": symbol,
            "marketRank": rank, "marketCap": 1e9,
            "indicators": {"cmcRefPriceUsd": 100.0,
                           "data": [_cndl(100, 110, 90, date=rd), _cndl(100, 110, 90, date=rd)]}}


def _window(rd, n):
    rows = [_row("BINANCE:BTCUSDT", 1, rd)] + [_row("SYM%03d" % i, i, rd) for i in range(2, n + 1)]
    return {"limited": False, "total": n, "results": rows}


def _patch(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"; dest = tmp_path / "dest"
    inbox.mkdir(); dest.mkdir()
    monkeypatch.setattr(runner, "INBOX", inbox)
    monkeypatch.setattr(runner, "DEST", dest)
    monkeypatch.setattr(runner, "QUARANTINE_DIR", inbox / "_quarantine")
    monkeypatch.setattr(runner, "REDUCTION_LOG_DIR", dest / "_reductions")
    return inbox, dest


def _raw_dir(dest):
    return dest / runner.RAW_TOP100_DIRNAME


def test_top100_creates_immutable_raw_plus_canonical_top50(tmp_path, monkeypatch):
    inbox, dest = _patch(tmp_path, monkeypatch)
    rd = "2026-06-28"
    blob = json.dumps(_window(rd, 100), separators=(",", ":")).encode("utf-8")
    src = inbox / "gc_crypto_trendradar_daily_top100.json"
    src.write_bytes(blob)
    res = runner.import_one(src, set(), today=rd)

    assert res["imported"] is True and res["reduced"] is True
    assert res["source_type"] == runner.SOURCE_TYPE_REDUCED
    assert res["raw_top100_retained"] is True and res["raw_top100_row_count"] == 100
    # canonical top-50 written, 50 rows, and its SHA is independent of the raw SHA
    canon = dest / "gc_crypto_trendradar_daily_20260628.json"
    assert canon.is_file()
    canon_obj = json.loads(canon.read_text(encoding="utf-8"))
    assert canon_obj["total"] == 50 and len(canon_obj["results"]) == 50
    canon_sha = hashlib.sha256(canon.read_bytes()).hexdigest()
    # raw archive is byte-identical to the ORIGINAL vendor bytes
    raw_path = _raw_dir(dest) / "gc_crypto_trendradar_daily_20260628_raw_top100.json"
    assert raw_path.is_file()
    assert raw_path.read_bytes() == blob
    raw_sha = hashlib.sha256(blob).hexdigest()
    assert res["raw_top100_sha256"] == raw_sha
    assert raw_sha != canon_sha                       # independent evidence


def test_provenance_differentiates_reduced_and_records_raw(tmp_path, monkeypatch):
    inbox, dest = _patch(tmp_path, monkeypatch)
    rd = "2026-06-28"
    blob = json.dumps(_window(rd, 100), separators=(",", ":")).encode("utf-8")
    src = inbox / "gc_crypto_trendradar_daily_top100.json"; src.write_bytes(blob)
    res = runner.import_one(src, set(), today=rd)
    assert res["imported"] is True
    prov_files = sorted((dest / "_reductions").glob("reduction_*.json"))
    assert len(prov_files) == 1
    prov = json.loads(prov_files[0].read_text(encoding="utf-8"))
    assert prov["source_type"] == runner.SOURCE_TYPE_REDUCED
    assert prov["raw_top100_retained"] is True
    assert prov["raw_top100_source_type"] == runner.SOURCE_TYPE_RAW_RETAINED
    assert prov["raw_top100_sha256"] == hashlib.sha256(blob).hexdigest()
    assert prov["raw_top100_row_count"] == 100
    assert prov["canonical_total"] == 50


def test_native_top50_creates_no_raw_archive(tmp_path, monkeypatch):
    inbox, dest = _patch(tmp_path, monkeypatch)
    rd = "2026-06-24"
    blob = json.dumps(_window(rd, 50), separators=(",", ":")).encode("utf-8")
    src = inbox / "gc_crypto_trendradar_daily_native.json"; src.write_bytes(blob)
    res = runner.import_one(src, set(), today=rd)
    assert res["imported"] is True
    assert res["source_type"] == runner.SOURCE_TYPE_NATIVE
    assert "raw_top100_retained" not in res            # native never retains a raw archive
    assert not _raw_dir(dest).exists() or not any(_raw_dir(dest).iterdir())


def test_raw_collision_refuses_without_overwrite(tmp_path, monkeypatch):
    inbox, dest = _patch(tmp_path, monkeypatch)
    _raw_dir(dest).mkdir(parents=True)
    existing = _raw_dir(dest) / "gc_crypto_trendradar_daily_20260628_raw_top100.json"
    existing.write_bytes(b"preexisting")
    try:
        runner._write_raw_top100(b"newbytes", "2026-06-28", 100)
        assert False, "expected collision refusal"
    except RuntimeError as e:
        assert "refuse_overwrite_raw_top100" in str(e)
    assert existing.read_bytes() == b"preexisting"     # immutable: not overwritten


def test_future_dated_top100_produces_no_raw_archive(tmp_path, monkeypatch):
    inbox, dest = _patch(tmp_path, monkeypatch)
    rd = "2026-06-28"
    blob = json.dumps(_window(rd, 100), separators=(",", ":")).encode("utf-8")
    src = inbox / "gc_crypto_trendradar_daily_future.json"; src.write_bytes(blob)
    res = runner.import_one(src, set(), today="2026-06-27")   # window is tomorrow -> quarantine
    assert res["imported"] is False
    assert not _raw_dir(dest).exists() or not any(_raw_dir(dest).iterdir())


def test_invalid_top100_produces_no_raw_archive(tmp_path, monkeypatch):
    inbox, dest = _patch(tmp_path, monkeypatch)
    rd = "2026-06-28"
    w = _window(rd, 100); w["results"][10]["detector"] = "tr"   # a bad row -> INVALID
    blob = json.dumps(w, separators=(",", ":")).encode("utf-8")
    src = inbox / "gc_crypto_trendradar_daily_bad.json"; src.write_bytes(blob)
    res = runner.import_one(src, set(), today=rd)
    assert res["imported"] is False
    assert not _raw_dir(dest).exists() or not any(_raw_dir(dest).iterdir())
