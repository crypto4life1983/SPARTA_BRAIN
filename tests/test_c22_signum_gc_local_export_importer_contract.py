"""Tests for the Candidate #22 Signum GC local export importer (contract + tool).

Proves: a valid export imports (IMPORT_OK) with a runDate-derived destination filename; a
second file for the same date is DUPLICATE_WINDOW (no overwrite); structurally invalid files
(wrong detector, wrong assetClass, missing gc fields, <50 rows, missing marketRank/
cmcRefPriceUsd) are INVALID and not imported; the JSON contents are never mutated (byte
copy); the tool writes only into the dataset folder via tmp dirs (never the real one); the
imported file is SHA-reported; and the contract/tool carry no network/API/Signum/MCP/
trading/scheduler tokens. C22 stays HOLD_FOR_MORE_FROZEN_DATA_WINDOWS."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import sparta_commander.c22_signum_gc_local_export_importer_contract as imp
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as trk
import tools.c22_signum_gc_local_export_importer_once as runner


# ---- fixtures: a minimal-but-complete valid parsed export ------------------

def _candle(c, h, trend="Green", upper=10.0, filt=8.0, date="2026-06-21"):
    return {"ohlc": {"o": c, "h": h, "l": c - 1, "c": c},
            "gc": {"lower": filt - 1, "trend": trend, "upper": upper, "filter": filt},
            "date": date, "volume": 1000.0}


def _row(symbol, rank, run_date="2026-06-21"):
    return {"symbol": symbol, "marketRank": rank, "marketCap": 1e9 / rank,
            "detector": "gc", "assetClass": "crypto", "runDate": run_date,
            "indicators": {"cmcRefPriceUsd": 5.0,
                           "data": [_candle(5.0, 5.5), _candle(6.0, 6.5)]}}


def _valid_parsed(run_date="2026-06-21", total=50, n=3):
    return {"limited": False, "total": total,
            "results": [_row("SYM%d" % i, i, run_date) for i in range(1, n + 1)]}


# ---- valid import ----------------------------------------------------------

def test_valid_import_decision():
    d = imp.build_import_decision(_valid_parsed("2026-06-21"), already_collected_dates=set())
    assert d["verdict"] == imp.VERDICT_IMPORT_OK
    assert d["structurally_valid"] is True
    assert d["run_date"] == "2026-06-21"
    assert d["destination_filename"] == "gc_crypto_trendradar_daily_20260621.json"
    assert d["should_import"] is True
    assert imp.validate_import_decision(d)["valid"] is True


# ---- duplicate window (date already collected) -----------------------------

def test_duplicate_window_decision():
    d = imp.build_import_decision(_valid_parsed("2026-06-20"),
                                  already_collected_dates={"2026-06-20"})
    assert d["verdict"] == imp.VERDICT_DUPLICATE
    assert d["should_import"] is False
    assert imp.validate_import_decision(d)["valid"] is True


# ---- invalid: wrong detector / assetClass / missing fields / <50 -----------

def test_wrong_detector_is_invalid():
    p = _valid_parsed()
    p["results"][0]["detector"] = "tr"
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID
    assert "all_detector_gc" in d["reasons"]
    assert d["should_import"] is False


def test_wrong_asset_class_is_invalid():
    p = _valid_parsed()
    p["results"][1]["assetClass"] = "equity"
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID
    assert "all_asset_class_crypto" in d["reasons"]


def test_missing_gc_fields_is_invalid():
    p = _valid_parsed()
    p["results"][0]["indicators"]["data"][-1]["gc"].pop("filter")
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID
    assert "gc_trend_upper_filter_present" in d["reasons"]


def test_too_few_rows_is_invalid():
    p = _valid_parsed(total=10, n=2)   # total < 50 and only 2 rows
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID
    assert "has_50_rows" in d["reasons"]


def test_missing_market_rank_and_cmc_is_invalid():
    p = _valid_parsed()
    p["results"][0].pop("marketRank")
    p["results"][1]["indicators"].pop("cmcRefPriceUsd")
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID
    assert "market_rank_present" in d["reasons"]
    assert "cmc_ref_price_usd_present" in d["reasons"]


def test_mixed_run_dates_is_invalid():
    p = _valid_parsed()
    p["results"][0]["runDate"] = "2026-06-21"
    p["results"][1]["runDate"] = "2026-06-22"
    d = imp.build_import_decision(p, set())
    assert d["verdict"] == imp.VERDICT_INVALID


# ---- tool: real byte copy into a tmp dataset dir, never overwrites ---------

def test_tool_imports_and_never_overwrites(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    dest = tmp_path / "dest"
    inbox.mkdir()
    dest.mkdir()
    monkeypatch.setattr(runner, "INBOX", inbox)
    monkeypatch.setattr(runner, "DEST", dest)

    blob = json.dumps(_valid_parsed("2026-06-21")).encode("utf-8")
    src = inbox / "gc_crypto_trendradar_daily_anything.json"
    src.write_bytes(blob)

    res1 = runner.import_one(src, runner._already_collected_dates())
    assert res1["imported"] is True
    out = dest / "gc_crypto_trendradar_daily_20260621.json"
    assert out.is_file()
    # byte-identical copy (JSON never mutated)
    assert out.read_bytes() == blob
    assert res1["sha256"] == hashlib.sha256(blob).hexdigest()

    # a second file for the SAME date must NOT overwrite -> DUPLICATE
    src2 = inbox / "gc_crypto_trendradar_daily_copy.json"
    src2.write_bytes(json.dumps(_valid_parsed("2026-06-21")).encode("utf-8"))
    res2 = runner.import_one(src2, runner._already_collected_dates())
    assert res2["imported"] is False
    assert res2["verdict"] == imp.VERDICT_DUPLICATE
    assert out.read_bytes() == blob   # original untouched


def test_tool_empty_inbox(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "INBOX", tmp_path / "missing_inbox")
    assert runner.main() == 0


# ---- future-dated guard: data-integrity hardening (clock-anomalous exports) -

def test_is_future_dated_helper():
    assert imp.is_future_dated("2026-06-26", "2026-06-25") is True
    assert imp.is_future_dated("2026-06-25", "2026-06-25") is False   # same day OK
    assert imp.is_future_dated("2026-06-24", "2026-06-25") is False   # past OK
    assert imp.is_future_dated(None, "2026-06-25") is False
    assert imp.is_future_dated("garbage", "2026-06-25") is False      # unparseable -> False


def test_same_day_import_is_ok_with_today():
    today = "2026-06-25"
    d = imp.build_import_decision(_valid_parsed("2026-06-25"), set(), today=today)
    assert d["verdict"] == imp.VERDICT_IMPORT_OK
    assert d["is_future_dated"] is False
    assert d["should_import"] is True
    assert imp.validate_import_decision(d)["valid"] is True


def test_duplicate_still_noop_with_today():
    today = "2026-06-25"
    d = imp.build_import_decision(_valid_parsed("2026-06-20"), {"2026-06-20"}, today=today)
    assert d["verdict"] == imp.VERDICT_DUPLICATE
    assert d["should_import"] is False
    assert imp.validate_import_decision(d)["valid"] is True


def test_future_dated_is_rejected_not_imported():
    today = "2026-06-25"
    d = imp.build_import_decision(_valid_parsed("2026-06-26"), set(), today=today)
    assert d["verdict"] == imp.VERDICT_FUTURE_DATED
    assert d["is_future_dated"] is True
    assert d["should_import"] is False
    assert "future_dated_run_date:2026-06-26_after_local_date:2026-06-25" in d["reasons"]
    assert imp.validate_import_decision(d)["valid"] is True
    # tamper: a future-dated export may NOT be relabeled IMPORT_OK
    bad = {**d, "verdict": imp.VERDICT_IMPORT_OK, "should_import": True}
    assert imp.validate_import_decision(bad)["valid"] is False


def test_tool_quarantines_future_dated_and_count_does_not_advance(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    dest = tmp_path / "dest"
    inbox.mkdir()
    dest.mkdir()
    monkeypatch.setattr(runner, "INBOX", inbox)
    monkeypatch.setattr(runner, "DEST", dest)
    monkeypatch.setattr(runner, "QUARANTINE_DIR", inbox / "_quarantine")
    today = "2026-06-25"

    # (5) a valid SAME-DAY file still imports normally
    good = inbox / "gc_crypto_trendradar_daily_good.json"
    good.write_bytes(json.dumps(_valid_parsed("2026-06-25")).encode("utf-8"))
    rg = runner.import_one(good, runner._already_collected_dates(), today=today)
    assert rg["imported"] is True
    assert (dest / "gc_crypto_trendradar_daily_20260625.json").is_file()

    # a FUTURE-dated file is quarantined, never imported
    fut = inbox / "gc_crypto_trendradar_daily_future.json"
    blob = json.dumps(_valid_parsed("2026-06-26")).encode("utf-8")
    fut.write_bytes(blob)
    rf = runner.import_one(fut, runner._already_collected_dates(), today=today)
    assert rf["imported"] is False
    assert rf["verdict"] == imp.VERDICT_FUTURE_DATED
    assert rf["quarantined"] is True

    # (4) dataset did NOT gain the future window; count/latest date unchanged
    assert not (dest / "gc_crypto_trendradar_daily_20260626.json").exists()
    collected = sorted(trk._date_from_filename(p.name) for p in dest.glob(trk.EXPORT_GLOB))
    assert collected == ["2026-06-25"]   # only the same-day import; 2026-06-26 absent

    # original moved OUT of the inbox top-level (not left to re-import, not deleted)
    assert not fut.exists()
    qroot = inbox / "_quarantine" / "2026-06-26"
    qfiles = list(qroot.glob("*"))
    payloads = [p for p in qfiles if p.name.endswith(".json") and ".note." not in p.name]
    notes = [p for p in qfiles if p.name.endswith(".note.json")]
    assert payloads and notes
    # (4-cont) quarantined payload preserved byte-for-byte (moved, not mutated/deleted)
    assert payloads[0].read_bytes() == blob
    # quarantine note carries reason, timestamp, source, destination, size, SHA-256
    note = json.loads(notes[0].read_text(encoding="utf-8"))
    assert note["sha256"] == hashlib.sha256(blob).hexdigest()
    assert note["size_bytes"] == len(blob)
    assert note["status"] == "QUARANTINED_NOT_DELETED"
    assert note["local_machine_date"] == today
    assert note["source_path"] and note["destination_path"] and note["quarantined_at"]


def test_quarantine_is_invisible_to_scanners_and_under_gitignored_inbox(tmp_path, monkeypatch):
    """(5) git/artifact safety: quarantine lives INSIDE the gitignored inbox dir and its files
    do NOT match the EXPORT_GLOB, so no importer/tracker scan re-imports a quarantined file and
    nothing lands in the tracked dataset."""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    monkeypatch.setattr(runner, "INBOX", inbox)
    monkeypatch.setattr(runner, "DEST", tmp_path / "dest")
    monkeypatch.setattr(runner, "QUARANTINE_DIR", inbox / "_quarantine")
    # production inbox path is the gitignored data dir, and quarantine nests under it
    assert imp.INBOX_DIR == "data/external_signum_trend_radar_gc_inbox"
    assert runner.QUARANTINE_DIR.parent == inbox

    fut = inbox / "gc_crypto_trendradar_daily_future.json"
    fut.write_bytes(json.dumps(_valid_parsed("2026-06-26")).encode("utf-8"))
    runner.import_one(fut, set(), today="2026-06-25")

    # a non-recursive EXPORT_GLOB over the inbox finds NO quarantined payload
    assert list(inbox.glob(trk.EXPORT_GLOB)) == []
    payloads = list((inbox / "_quarantine" / "2026-06-26").glob("*"))
    assert payloads, "expected quarantined files to exist in the subfolder"
    for p in payloads:
        assert not p.name.startswith(trk.EXPORT_PREFIX)   # off the EXPORT_GLOB prefix


# ---- same-day shape/size anomaly guard (full-dump / pretty-printed exports) -

def test_check_shape_anomaly_helper():
    p = _valid_parsed("2026-06-25")
    # canonical minified daily export -> clean
    assert imp.check_shape_anomaly(p, 62442, 62338)["anomalous"] is False
    assert imp.check_shape_anomaly(p)["anomalous"] is False
    # pretty-printed (raw bloated, MINIFIED payload normal) -> NOT anomalous, only warned
    pp = imp.check_shape_anomaly(p, 113530, 62348)   # the 06-20 / 06-26 shape
    assert pp["anomalous"] is False
    assert pp["warnings"]
    # real extra content (minified payload beyond the content ceiling) -> anomalous
    assert imp.check_shape_anomaly(p, 200000, 199000)["anomalous"] is True
    # extra top-level key (full/raw dump) -> anomalous via content-shape
    assert imp.check_shape_anomaly({**p, "debugDump": {"all": True}})["anomalous"] is True


def test_normal_minified_same_day_imports_with_sizes():
    d = imp.build_import_decision(_valid_parsed("2026-06-25"), set(), today="2026-06-25",
                                  raw_bytes=62442, compact_bytes=62338)   # ratio ~1.00
    assert d["verdict"] == imp.VERDICT_IMPORT_OK
    assert d["is_anomalous_shape"] is False
    assert d["should_import"] is True
    assert imp.validate_import_decision(d)["valid"] is True


def test_pretty_printed_alone_imports_with_warning():
    # the 06-20/06-26 shape: ~113 KB raw but content-equivalent ~62 KB minified -> IMPORTS
    d = imp.build_import_decision(_valid_parsed("2026-06-25"), set(), today="2026-06-25",
                                  raw_bytes=113530, compact_bytes=62348)   # ratio ~1.82
    assert d["verdict"] == imp.VERDICT_IMPORT_OK
    assert d["is_anomalous_shape"] is False
    assert d["should_import"] is True
    assert d["shape_warnings"]   # formatting is flagged as a non-blocking warning
    assert imp.validate_import_decision(d)["valid"] is True


def test_oversized_minified_content_is_anomalous():
    # real extra content: the MINIFIED payload is far above the normal ~62 KB
    d = imp.build_import_decision(_valid_parsed("2026-06-25"), set(), today="2026-06-25",
                                  raw_bytes=190000, compact_bytes=185000)
    assert d["verdict"] == imp.VERDICT_ANOMALOUS
    assert any("minified_content_exceeds_ceiling" in x for x in d["anomaly_reasons"])
    assert imp.validate_import_decision(d)["valid"] is True
    bad = {**d, "verdict": imp.VERDICT_IMPORT_OK, "should_import": True}
    assert imp.validate_import_decision(bad)["valid"] is False


def test_full_dump_shape_is_anomalous():
    # extra top-level key + far too many rows = a full/raw dump, not a daily window
    p = _valid_parsed("2026-06-25", total=500, n=70)
    p["debugDump"] = {"everything": True}
    d = imp.build_import_decision(p, set(), today="2026-06-25",
                                  raw_bytes=80000, compact_bytes=79000)
    assert d["verdict"] == imp.VERDICT_ANOMALOUS
    assert any("unexpected_top_level_keys" in x for x in d["anomaly_reasons"])
    assert any("results" in x or "total" in x for x in d["anomaly_reasons"])


def test_tool_pretty_printed_imports_with_warning(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    dest = tmp_path / "dest"
    inbox.mkdir()
    dest.mkdir()
    monkeypatch.setattr(runner, "INBOX", inbox)
    monkeypatch.setattr(runner, "DEST", dest)
    monkeypatch.setattr(runner, "QUARANTINE_DIR", inbox / "_quarantine")

    compact = json.dumps(_valid_parsed("2026-06-24"), separators=(",", ":"))
    pretty = json.dumps(_valid_parsed("2026-06-24"), indent=2)
    assert len(pretty) / len(compact) > imp.PRETTY_PRINT_WARN_RATIO   # really pretty-printed
    src = inbox / "gc_crypto_trendradar_daily_pp.json"
    src.write_bytes(pretty.encode("utf-8"))
    res = runner.import_one(src, runner._already_collected_dates(), today="2026-06-25")
    # pretty-printing alone does NOT block import; it is imported WITH a warning
    assert res["imported"] is True
    assert res["verdict"] == imp.VERDICT_IMPORT_OK
    assert res["shape_warnings"]
    assert (dest / "gc_crypto_trendradar_daily_20260624.json").is_file()


def test_tool_quarantines_true_full_dump_and_count_does_not_advance(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    dest = tmp_path / "dest"
    inbox.mkdir()
    dest.mkdir()
    monkeypatch.setattr(runner, "INBOX", inbox)
    monkeypatch.setattr(runner, "DEST", dest)
    monkeypatch.setattr(runner, "QUARANTINE_DIR", inbox / "_quarantine")
    today = "2026-06-25"

    # a normal MINIFIED same-day export imports normally
    good = inbox / "gc_crypto_trendradar_daily_good.json"
    good.write_bytes(json.dumps(_valid_parsed("2026-06-25"), separators=(",", ":")).encode())
    assert runner.import_one(good, runner._already_collected_dates(),
                             today=today)["imported"] is True

    # a TRUE full/raw dump (extra top-level key) is quarantined, never imported
    dump = dict(_valid_parsed("2026-06-25"))
    dump["debugDump"] = {"all": True}
    blob = json.dumps(dump, separators=(",", ":")).encode("utf-8")   # minified, real extra key
    bad = inbox / "gc_crypto_trendradar_daily_dump.json"
    bad.write_bytes(blob)
    rb = runner.import_one(bad, runner._already_collected_dates(), today=today)
    assert rb["imported"] is False
    assert rb["verdict"] == imp.VERDICT_ANOMALOUS
    assert rb["quarantined"] is True

    # C22 count/latest do NOT advance from the dump (only the good import counts)
    collected = sorted(trk._date_from_filename(p.name) for p in dest.glob(trk.EXPORT_GLOB))
    assert collected == ["2026-06-25"]

    # dump moved OUT of the inbox top-level (not re-importable, not deleted)
    assert not bad.exists()
    assert "gc_crypto_trendradar_daily_dump.json" not in [p.name for p in inbox.glob(trk.EXPORT_GLOB)]
    qfiles = list((inbox / "_quarantine" / "2026-06-25").glob("*"))
    payloads = [p for p in qfiles if p.name.endswith(".json") and ".note." not in p.name]
    notes = [p for p in qfiles if p.name.endswith(".note.json")]
    assert payloads and notes
    assert payloads[0].read_bytes() == blob
    for p in payloads:
        assert not p.name.startswith(trk.EXPORT_PREFIX)   # invisible to EXPORT_GLOB scans
    note = json.loads(notes[0].read_text(encoding="utf-8"))
    assert note["sha256"] == hashlib.sha256(blob).hexdigest()
    assert "anomalous" in note["quarantine_reason"]
    assert note["status"] == "QUARANTINED_NOT_DELETED"


def test_duplicate_normal_file_still_noop_with_sizes():
    # a normal, in-band duplicate must remain a harmless no-op (not flagged anomalous)
    d = imp.build_import_decision(_valid_parsed("2026-06-20"), {"2026-06-20"},
                                  today="2026-06-25", raw_bytes=62442, compact_bytes=62338)
    assert d["verdict"] == imp.VERDICT_DUPLICATE
    assert d["is_anomalous_shape"] is False
    assert d["should_import"] is False
    assert imp.validate_import_decision(d)["valid"] is True


# ---- Signum top-100 -> top-50 canonicalization / reduction -----------------

def test_is_reducible_top100_helper():
    assert imp.is_reducible_top100(_valid_parsed("2026-06-28", total=100, n=100)) is True
    assert imp.is_reducible_top100(_valid_parsed("2026-06-28", total=50, n=50)) is False
    # extra top-level key -> not reducible (full/raw dump, handled by the anomaly path)
    p = _valid_parsed("2026-06-28", total=100, n=100); p["debugDump"] = {"x": 1}
    assert imp.is_reducible_top100(p) is False
    # count mismatch -> not reducible
    assert imp.is_reducible_top100(_valid_parsed("2026-06-28", total=100, n=50)) is False


def test_derive_canonical_top50_first_50_preserving_order():
    p = _valid_parsed("2026-06-28", total=100, n=100)
    d = imp.derive_canonical_top50(p)
    assert sorted(d.keys()) == ["limited", "results", "total"]   # no extra metadata
    assert d["total"] == 50 and len(d["results"]) == 50
    assert d["results"] == p["results"][:50]                     # FIRST 50, order preserved
    assert len(p["results"]) == 100                              # input not mutated


def test_reducible_decision_same_day():
    d = imp.build_import_decision(_valid_parsed("2026-06-28", total=100, n=100), set(),
                                  today="2026-06-28", raw_bytes=130000, compact_bytes=70000)
    assert d["verdict"] == imp.VERDICT_REDUCIBLE
    assert d["is_reducible_top100"] is True
    assert d["should_import"] is False and d["should_reduce_and_import"] is True
    assert d["reducer"] == "first_50_vendor_instruction"
    assert imp.validate_import_decision(d)["valid"] is True
    # tamper: a reducible export may NOT be relabeled IMPORT_OK (raw 100 rows must not import)
    bad = {**d, "verdict": imp.VERDICT_IMPORT_OK, "should_import": True}
    assert imp.validate_import_decision(bad)["valid"] is False


def test_future_dated_100row_does_not_reduce_early():
    d = imp.build_import_decision(_valid_parsed("2026-06-28", total=100, n=100), set(),
                                  today="2026-06-27", raw_bytes=130000, compact_bytes=70000)
    assert d["verdict"] == imp.VERDICT_FUTURE_DATED   # future date beats reduction
    assert d["should_import"] is False


def test_malformed_100row_rejects_not_reduces():
    # a bad row -> structurally INVALID, never reduced
    p = _valid_parsed("2026-06-28", total=100, n=100); p["results"][80]["detector"] = "tr"
    d = imp.build_import_decision(p, set(), today="2026-06-28",
                                  raw_bytes=130000, compact_bytes=70000)
    assert d["verdict"] == imp.VERDICT_INVALID
    # extra top-level key (full/raw dump) -> ANOMALOUS, never reduced
    p2 = _valid_parsed("2026-06-28", total=100, n=100); p2["debugDump"] = {"x": 1}
    d2 = imp.build_import_decision(p2, set(), today="2026-06-28",
                                   raw_bytes=130000, compact_bytes=70000)
    assert d2["verdict"] == imp.VERDICT_ANOMALOUS


def test_tool_reduces_top100_and_imports_canonical_top50(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    dest = tmp_path / "dest"
    inbox.mkdir()
    dest.mkdir()
    monkeypatch.setattr(runner, "INBOX", inbox)
    monkeypatch.setattr(runner, "DEST", dest)
    monkeypatch.setattr(runner, "QUARANTINE_DIR", inbox / "_quarantine")
    monkeypatch.setattr(runner, "REDUCTION_LOG_DIR", dest / "_reductions")
    today = "2026-06-28"

    src = inbox / "gc_crypto_trendradar_daily_top100.json"
    src.write_bytes(json.dumps(_valid_parsed("2026-06-28", total=100, n=100),
                               separators=(",", ":")).encode("utf-8"))
    res = runner.import_one(src, runner._already_collected_dates(), today=today)
    assert res["imported"] is True
    assert res["verdict"] == imp.VERDICT_REDUCIBLE
    assert res["reduced"] is True and res["reducer"] == "first_50_vendor_instruction"

    # (5) derived active window: canonical shape, total=50, 50 first rows
    out = dest / "gc_crypto_trendradar_daily_20260628.json"
    assert out.is_file()
    canon = json.loads(out.read_bytes().decode("utf-8"))
    assert sorted(canon.keys()) == ["limited", "results", "total"]
    assert canon["total"] == 50 and len(canon["results"]) == 50
    src_rows = json.loads(src.read_bytes().decode("utf-8"))["results"][:50]
    assert canon["results"] == src_rows               # first 50, order preserved

    # (8) count/latest advanced only via the reduced window
    collected = sorted(trk._date_from_filename(p.name) for p in dest.glob(trk.EXPORT_GLOB))
    assert collected == ["2026-06-28"]

    # (6) provenance sidecar in the ignored subfolder, off EXPORT_GLOB
    prov = list((dest / "_reductions").glob("*.json"))
    assert prov, "expected a reduction provenance sidecar"
    note = json.loads(prov[0].read_text(encoding="utf-8"))
    assert note["reducer"] == "first_50_vendor_instruction"
    assert note["original_total"] == 100 and note["original_results"] == 100
    assert note["canonical_total"] == 50
    assert note["original_sha256"] and note["canonical_sha256"]
    assert note["original_filename"] == "gc_crypto_trendradar_daily_top100.json"
    assert "first 50 rows" in note["vendor_instruction_quote"].lower()
    # the window scan sees ONLY the canonical file, never the provenance sidecar
    assert list(dest.glob(trk.EXPORT_GLOB)) == [out]
    for p in prov:
        assert not p.name.startswith(trk.EXPORT_PREFIX)


def test_tool_reduced_window_duplicate_is_noop(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    dest = tmp_path / "dest"
    inbox.mkdir()
    dest.mkdir()
    monkeypatch.setattr(runner, "INBOX", inbox)
    monkeypatch.setattr(runner, "DEST", dest)
    monkeypatch.setattr(runner, "QUARANTINE_DIR", inbox / "_quarantine")
    monkeypatch.setattr(runner, "REDUCTION_LOG_DIR", dest / "_reductions")
    today = "2026-06-28"
    blob = json.dumps(_valid_parsed("2026-06-28", total=100, n=100),
                      separators=(",", ":")).encode("utf-8")

    s1 = inbox / "gc_crypto_trendradar_daily_a.json"
    s1.write_bytes(blob)
    assert runner.import_one(s1, runner._already_collected_dates(),
                             today=today)["imported"] is True
    # a second reducible file for the SAME date -> derived window is a DUPLICATE no-op
    s2 = inbox / "gc_crypto_trendradar_daily_b.json"
    s2.write_bytes(blob)
    r2 = runner.import_one(s2, runner._already_collected_dates(), today=today)
    assert r2["imported"] is False
    assert r2["verdict"] == imp.VERDICT_DUPLICATE
    assert len(list(dest.glob(trk.EXPORT_GLOB))) == 1   # still exactly one window


# ---- tracker compatibility: imported filename is counted as a window -------

def test_imported_filename_is_tracked_window():
    # the importer's destination filename is exactly what the tracker counts as a window
    fname = imp.derive_destination_filename("2026-06-21")
    assert trk._date_from_filename(fname) == "2026-06-21"
    status = trk.build_collection_status(
        ["gc_crypto_trendradar_daily.json", fname])
    assert status["collected_windows"] == 2   # bootstrap (06-20) + imported (06-21)


# ---- no network / API / Signum / trading / scheduler tokens ----------------

_FORBIDDEN_TOKENS = (
    "import requests", "from requests", "import ccxt", "from ccxt", "urlopen",
    "import socket", "schtasks", "Register-ScheduledTask", "ScheduledTaskTrigger",
    "BackgroundScheduler", "place_order", "create_order", "api.binance", "MetaTrader",
    "get_trendradar", "import websockets",
)


def test_no_network_api_trading_scheduler_tokens():
    for mod in (imp, runner):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        for tok in _FORBIDDEN_TOKENS:
            assert tok not in src, "%s: %s" % (Path(mod.__file__).name, tok)


# ---- capability flags + module purity (the pure contract) ------------------

def test_capability_flags_and_state():
    d = imp.build_import_decision(_valid_parsed(), set())
    assert d["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert d["replay_locked"] is True
    for flag in imp._CAPABILITY_FLAGS_FALSE:
        assert d[flag] is False, flag
    for key, val in d["scope_locks"].items():
        assert val is True, key


def test_contract_module_purity():
    src = Path(imp.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen",
                 "json.load", "read_text", "read_bytes", "glob("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
