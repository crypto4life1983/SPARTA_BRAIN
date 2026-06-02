"""Tests for tools/crypto_d1_kraken_normalize.py.

Synthetic fixtures only. No real Kraken data, no network, no credentials.
Every write test points ``--repo-root`` at a pytest ``tmp_path`` so the real
``data/crypto_d1_research/`` tree is never created or touched.
"""
from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import crypto_d1_kraken_normalize as norm  # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_kraken_normalize.py"

# The 35 required Crypto-D1 per-dataset manifest fields (mirrors the spec
# enforced by tools/crypto_d1_dataset_manifest_check.py).
REQUIRED_MANIFEST_FIELDS = (
    "dataset_id", "dataset_version", "created_at", "created_by",
    "research_lane", "market_type", "assets", "symbols", "quote_currency",
    "timeframe", "time_start", "time_end", "timezone", "bar_boundary",
    "data_frequency", "source_type", "source_name", "source_location",
    "data_contract_version", "protocol_version", "checksum_policy",
    "row_count_expected", "row_count_actual", "missing_day_policy",
    "duplicate_policy", "partial_day_policy", "zero_volume_policy",
    "outlier_policy", "normalization_policy", "fee_slippage_assumption_reference",
    "freeze_status", "QA_status", "allowed_use", "forbidden_use", "notes",
)

_FIXED_NOW = datetime(2026, 6, 2, 12, 0, 0, tzinfo=timezone.utc)


# --- fixture helpers -------------------------------------------------------


def _unix(d) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())


def _write_raw(path: Path, rows) -> None:
    """rows: iterable of (date, open, high, low, close, volume, count)."""
    lines = []
    for d, o, h, lo, c, v, tc in rows:
        parts = [str(_unix(d)), str(o), str(h), str(lo), str(c), str(v)]
        if tc is not None:
            parts.append(str(tc))
        lines.append(",".join(parts))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _full_rows():
    return [
        (d, 100.0, 110.0, 90.0, 105.0, 1000.0, 42)
        for d in norm._all_dates_in_range()
    ]


@pytest.fixture
def raw_full(tmp_path):
    """A complete, valid raw dir covering the whole range for all 3 assets."""
    raw = tmp_path / "kraken_raw"
    raw.mkdir()
    rows = _full_rows()
    _write_raw(raw / "XBTUSD_1440.csv", rows)
    _write_raw(raw / "ETHUSD_1440.csv", rows)
    _write_raw(raw / "SOLUSD_1440.csv", rows)
    return raw


# Noisy filenames that mimic the full Kraken dump and must all be ignored.
_NOISE_FILENAMES = (
    "XBTUSD_1.csv", "XBTUSD_5.csv", "XBTUSD_60.csv", "XBTUSD_240.csv",
    "XBTUSD1_1440.csv", "XBTUSDC_1440.csv", "XXBTZUSD_1440.csv",
    "ETHUSD_1.csv", "ETHUSD_60.csv", "ETHUSD1_1440.csv", "ETHUSDC_1440.csv",
    "XETHZUSD_1440.csv", "SOLUSD_1.csv", "SOLUSD_240.csv", "SOLUSDC_1440.csv",
    "DOGEUSD_1440.csv", "README.txt",
)


@pytest.fixture
def raw_full_noisy(tmp_path):
    """A full-dump-style raw dir: the 3 exact daily files surrounded by many
    other intervals / quote / name variants that must all be ignored."""
    raw = tmp_path / "kraken_dump"
    raw.mkdir()
    rows = _full_rows()
    _write_raw(raw / "XBTUSD_1440.csv", rows)
    _write_raw(raw / "ETHUSD_1440.csv", rows)
    _write_raw(raw / "SOLUSD_1440.csv", rows)
    # garbage rows in the noise files; they should never be parsed
    for name in _NOISE_FILENAMES:
        (raw / name).write_text("not,real,data\n", encoding="utf-8")
    return raw


def _minimal_raw(tmp_path, btc_rows=None):
    """A tiny valid raw dir; BTC rows can be overridden to probe errors."""
    from datetime import date

    raw = tmp_path / "kraken_raw_min"
    raw.mkdir()
    one = [(date(2021, 6, 17), 100.0, 110.0, 90.0, 105.0, 1000.0, 42)]
    _write_raw(raw / "XBTUSD_1440.csv", btc_rows if btc_rows is not None else one)
    _write_raw(raw / "ETHUSD_1440.csv", one)
    _write_raw(raw / "SOLUSD_1440.csv", one)
    return raw


# --- safety: no dangerous imports / calls in the tool source ---------------


def test_no_dangerous_imports_or_calls():
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))
    banned_roots = {
        "urllib", "requests", "socket", "http", "ftplib", "subprocess",
        "ccxt", "krakenex", "krakenapi", "dotenv", "websocket", "aiohttp",
        "httpx", "smtplib", "telnetlib", "os", "pickle",
    }
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported_roots.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_roots.add(node.module.split(".")[0])
    leaked = imported_roots & banned_roots
    assert not leaked, f"tool imports banned modules: {sorted(leaked)}"

    banned_attrs = {
        "system", "popen", "getenv", "environ", "Popen", "run", "call",
        "check_output", "spawn", "fork", "urlopen",
    }
    banned_names = {"eval", "exec", "__import__", "compile"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in banned_attrs:
            raise AssertionError(f"tool uses banned attribute: .{node.attr}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in banned_names, (
                f"tool calls banned builtin: {node.func.id}"
            )


# --- mapping + parsing -----------------------------------------------------


def test_classify_xbt_maps_to_btc():
    assert norm.classify_raw_file(Path("XBTUSD_1440.csv")) == "BTC"
    assert norm.classify_raw_file(Path("ethusd_1440.csv")) == "ETH"
    assert norm.classify_raw_file(Path("SOLUSD_1440.csv")) == "SOL"
    assert norm.classify_raw_file(Path("DOGEUSD_1440.csv")) is None


def test_classify_rejects_non_exact_variants():
    # Lower intervals, alternate quotes, and alternate venue names are NOT the
    # approved daily file and must be ignored (return None).
    for variant in (
        "XBTUSD_1.csv", "XBTUSD_5.csv", "XBTUSD_60.csv", "XBTUSD_240.csv",
        "XBTUSD1_1440.csv", "XBTUSDC_1440.csv", "XXBTZUSD_1440.csv",
        "ETHUSD1_1440.csv", "ETHUSDC_1440.csv", "XETHZUSD_1440.csv",
        "SOLUSD_240.csv", "SOLUSDC_1440.csv",
    ):
        assert norm.classify_raw_file(Path(variant)) is None, variant


# --- exact-filename selection against a noisy full dump --------------------


def test_full_dump_selects_only_exact_daily_files(raw_full_noisy):
    # (1) Full dump with noisy variants still selects only the exact _1440 files.
    result = norm.normalize(raw_full_noisy)
    assert {r[6] for r in result["rows"]} == {"BTC", "ETH", "SOL"}
    assert result["per_asset"]["BTC"]["raw_file"] == "XBTUSD_1440.csv"
    assert result["per_asset"]["ETH"]["raw_file"] == "ETHUSD_1440.csv"
    assert result["per_asset"]["SOL"]["raw_file"] == "SOLUSD_1440.csv"


def test_eth_variant_does_not_collide(tmp_path):
    # (2) ETHUSD1_1440.csv must not collide with ETHUSD_1440.csv.
    from datetime import date

    raw = tmp_path / "eth_variant"
    raw.mkdir()
    one = [(date(2021, 6, 17), 100, 110, 90, 105, 1000, 42)]
    _write_raw(raw / "XBTUSD_1440.csv", one)
    _write_raw(raw / "ETHUSD_1440.csv", one)
    _write_raw(raw / "SOLUSD_1440.csv", one)
    (raw / "ETHUSD1_1440.csv").write_text("not,real,data\n", encoding="utf-8")
    result = norm.normalize(raw)  # must NOT raise a duplicate error
    assert result["per_asset"]["ETH"]["raw_file"] == "ETHUSD_1440.csv"


def test_btc_quote_variant_does_not_collide(tmp_path):
    # (3) XBTUSDC_1440.csv must not collide with XBTUSD_1440.csv.
    from datetime import date

    raw = tmp_path / "btc_variant"
    raw.mkdir()
    one = [(date(2021, 6, 17), 100, 110, 90, 105, 1000, 42)]
    _write_raw(raw / "XBTUSD_1440.csv", one)
    _write_raw(raw / "ETHUSD_1440.csv", one)
    _write_raw(raw / "SOLUSD_1440.csv", one)
    (raw / "XBTUSDC_1440.csv").write_text("not,real,data\n", encoding="utf-8")
    result = norm.normalize(raw)  # must NOT raise a duplicate error
    assert result["per_asset"]["BTC"]["raw_file"] == "XBTUSD_1440.csv"


def test_missing_exact_file_fails_even_with_variants(tmp_path):
    # (4) Missing the exact daily file fails even when variants are present.
    from datetime import date

    raw = tmp_path / "missing_exact"
    raw.mkdir()
    one = [(date(2021, 6, 17), 100, 110, 90, 105, 1000, 42)]
    _write_raw(raw / "XBTUSD_1440.csv", one)
    _write_raw(raw / "SOLUSD_1440.csv", one)
    # only an ETH *variant* exists, not the exact ETHUSD_1440.csv
    (raw / "ETHUSD1_1440.csv").write_text("not,real,data\n", encoding="utf-8")
    with pytest.raises(norm.KrakenNormalizeError, match="missing required"):
        norm.normalize(raw)


def test_duplicate_exact_filename_in_subfolders_fails(tmp_path):
    # (5) Same exact filename in two different subfolders is a hard error.
    from datetime import date

    raw = tmp_path / "dup_folders"
    sub_a = raw / "a"
    sub_b = raw / "b"
    sub_a.mkdir(parents=True)
    sub_b.mkdir(parents=True)
    one = [(date(2021, 6, 17), 100, 110, 90, 105, 1000, 42)]
    _write_raw(sub_a / "XBTUSD_1440.csv", one)
    _write_raw(sub_b / "XBTUSD_1440.csv", one)
    _write_raw(raw / "ETHUSD_1440.csv", one)
    _write_raw(raw / "SOLUSD_1440.csv", one)
    with pytest.raises(norm.KrakenNormalizeError, match="duplicate exact daily file"):
        norm.normalize(raw)


def test_dry_run_with_noisy_folder_reports_expected_counts(raw_full_noisy):
    # (6) Dry-run over a noisy folder succeeds and reports 1659/asset, 4977 total.
    result = norm.normalize(raw_full_noisy)
    assert result["row_count_expected_per_asset"] == 1659
    assert result["per_asset"]["BTC"]["row_count"] == 1659
    assert result["per_asset"]["ETH"]["row_count"] == 1659
    assert result["per_asset"]["SOL"]["row_count"] == 1659
    assert result["row_count_total"] == 4977


def test_header_row_is_skipped(tmp_path):
    from datetime import date

    raw = tmp_path / "kraken_raw"
    raw.mkdir()
    body = "time,open,high,low,close,volume,count\n" + ",".join(
        [str(_unix(date(2021, 6, 17))), "100", "110", "90", "105", "1000", "42"]
    ) + "\n"
    (raw / "XBTUSD_1440.csv").write_text(body, encoding="utf-8")
    _write_raw(
        raw / "ETHUSD_1440.csv",
        [(date(2021, 6, 17), 100, 110, 90, 105, 1000, 42)],
    )
    _write_raw(
        raw / "SOLUSD_1440.csv",
        [(date(2021, 6, 17), 100, 110, 90, 105, 1000, 42)],
    )
    result = norm.normalize(raw)
    assert result["per_asset"]["BTC"]["row_count"] == 1


# --- timestamp + range + schema -------------------------------------------


def test_timestamp_conversion_is_iso_bar_open(tmp_path):
    result = norm.normalize(_minimal_raw(tmp_path))
    btc = [r for r in result["rows"] if r[6] == "BTC"]
    assert btc[0][0] == "2021-06-17T00:00:00Z"


def test_range_filter_excludes_out_of_range(tmp_path):
    from datetime import date

    rows = [
        (date(2020, 1, 1), 100, 110, 90, 105, 1000, 42),   # before range
        (date(2021, 6, 17), 100, 110, 90, 105, 1000, 42),  # in range
        (date(2026, 6, 1), 100, 110, 90, 105, 1000, 42),   # after range
    ]
    result = norm.normalize(_minimal_raw(tmp_path, btc_rows=rows))
    btc = [r for r in result["rows"] if r[6] == "BTC"]
    assert len(btc) == 1
    assert btc[0][0] == "2021-06-17T00:00:00Z"


def test_exact_csv_header_and_constant():
    assert norm.CSV_HEADER == (
        "timestamp", "open", "high", "low", "close", "volume",
        "symbol", "source", "quote_currency", "trade_count",
    )


def test_csv_text_first_line_matches_header(tmp_path):
    result = norm.normalize(_minimal_raw(tmp_path))
    first_line = result["csv_text"].splitlines()[0]
    assert first_line == (
        "timestamp,open,high,low,close,volume,symbol,source,"
        "quote_currency,trade_count"
    )


def test_one_combined_file_holds_all_three_assets(raw_full):
    result = norm.normalize(raw_full)
    symbols = {r[6] for r in result["rows"]}
    assert symbols == {"BTC", "ETH", "SOL"}


def test_expected_counts(raw_full):
    result = norm.normalize(raw_full)
    assert result["row_count_expected_per_asset"] == 1659
    assert result["per_asset"]["BTC"]["row_count"] == 1659
    assert result["per_asset"]["ETH"]["row_count"] == 1659
    assert result["per_asset"]["SOL"]["row_count"] == 1659
    assert result["row_count_total"] == 4977


# --- integrity errors ------------------------------------------------------


def test_duplicate_timestamp_rejected(tmp_path):
    from datetime import date

    dup = [
        (date(2021, 6, 17), 100, 110, 90, 105, 1000, 42),
        (date(2021, 6, 17), 101, 111, 91, 106, 1001, 43),
    ]
    with pytest.raises(norm.KrakenNormalizeError, match="duplicate"):
        norm.normalize(_minimal_raw(tmp_path, btc_rows=dup))


def test_ohlc_inconsistency_rejected(tmp_path):
    from datetime import date

    bad = [(date(2021, 6, 17), 100, 104, 90, 105, 1000, 42)]  # high < close
    with pytest.raises(norm.KrakenNormalizeError, match="high"):
        norm.normalize(_minimal_raw(tmp_path, btc_rows=bad))


def test_negative_volume_rejected(tmp_path):
    from datetime import date

    bad = [(date(2021, 6, 17), 100, 110, 90, 105, -5, 42)]
    with pytest.raises(norm.KrakenNormalizeError, match="volume"):
        norm.normalize(_minimal_raw(tmp_path, btc_rows=bad))


def test_negative_trade_count_rejected(tmp_path):
    from datetime import date

    bad = [(date(2021, 6, 17), 100, 110, 90, 105, 1000, -1)]
    with pytest.raises(norm.KrakenNormalizeError, match="trade_count"):
        norm.normalize(_minimal_raw(tmp_path, btc_rows=bad))


def test_missing_asset_file_rejected(tmp_path):
    raw = tmp_path / "incomplete"
    raw.mkdir()
    from datetime import date

    _write_raw(
        raw / "XBTUSD_1440.csv",
        [(date(2021, 6, 17), 100, 110, 90, 105, 1000, 42)],
    )
    with pytest.raises(norm.KrakenNormalizeError, match="missing required"):
        norm.normalize(raw)


# --- dry-run / write gating ------------------------------------------------


def _out_dir(repo_root: Path) -> Path:
    return repo_root / norm.DATASET_REL


def test_dry_run_writes_nothing(raw_full, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    rc = norm.main(["--raw-dir", str(raw_full), "--repo-root", str(repo)])
    assert rc == 0
    assert not _out_dir(repo).exists()


def test_write_required_to_materialize(raw_full, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    # default (dry-run): nothing on disk
    norm.main(["--raw-dir", str(raw_full), "--repo-root", str(repo)])
    assert not _out_dir(repo).exists()
    # with --write: the dataset files appear
    rc = norm.main(
        ["--raw-dir", str(raw_full), "--repo-root", str(repo), "--write"]
    )
    assert rc == 0
    out = _out_dir(repo)
    assert (out / norm.DATA_FILE).exists()
    assert (out / norm.MANIFEST_FILE).exists()
    assert (out / norm.FEES_FILE).exists()


def test_write_produces_single_combined_csv(raw_full, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    norm.main(
        ["--raw-dir", str(raw_full), "--repo-root", str(repo), "--write"]
    )
    out = _out_dir(repo)
    csvs = sorted(p.name for p in out.glob("*.csv"))
    assert csvs == [norm.DATA_FILE]


def test_no_qa_report_created(raw_full, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    norm.main(
        ["--raw-dir", str(raw_full), "--repo-root", str(repo),
         "--write", "--freeze"]
    )
    out = _out_dir(repo)
    assert not (out / "qa_report.json").exists()


def test_freeze_requires_write(raw_full, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    result = norm.normalize(raw_full)
    with pytest.raises(norm.KrakenNormalizeError, match="requires --write"):
        norm.materialize(
            result, repo_root=repo, write=False, freeze=True, now=_FIXED_NOW
        )


# --- write-jail ------------------------------------------------------------


def test_write_jail_blocks_escape(tmp_path):
    out = tmp_path / "data" / "crypto_d1_research" / norm.DATASET_ID / "V001"
    out.mkdir(parents=True)
    # a normal name resolves inside
    inside = norm._jail_target(out, norm.DATA_FILE)
    assert inside.parent == out.resolve()
    # an escaping name is refused
    with pytest.raises(norm.KrakenNormalizeError, match="outside"):
        norm._jail_target(out, "../../../evil.csv")


# --- sidecars: manifest + fees ---------------------------------------------


def test_manifest_has_all_required_fields(raw_full, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    result = norm.normalize(raw_full)
    plan = norm.materialize(
        result, repo_root=repo, write=False, freeze=False, now=_FIXED_NOW
    )
    manifest = plan["manifest"]
    for field in REQUIRED_MANIFEST_FIELDS:
        assert field in manifest, f"manifest missing required field: {field}"


def test_manifest_qa_status_is_draft_and_counts(raw_full, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    result = norm.normalize(raw_full)
    plan = norm.materialize(
        result, repo_root=repo, write=False, freeze=False, now=_FIXED_NOW
    )
    m = plan["manifest"]
    assert m["QA_status"] == "QA_DRAFT"
    assert m["created_by"] == norm.OPERATOR_LABEL
    assert m["row_count_expected"] == 4977
    assert m["row_count_actual"] == 4977
    assert m["data_contract_version"] == "crypto_d1_data_contract_v1"
    assert m["protocol_version"] == "crypto_d1_protocol_v1"


def test_freeze_status_reflects_freeze_flag(raw_full, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    result = norm.normalize(raw_full)
    drafted = norm.materialize(
        result, repo_root=repo, write=True, freeze=False, now=_FIXED_NOW
    )
    assert drafted["manifest"]["freeze_status"] == "DRAFT"

    repo2 = tmp_path / "repo2"
    repo2.mkdir()
    frozen = norm.materialize(
        result, repo_root=repo2, write=True, freeze=True, now=_FIXED_NOW
    )
    assert frozen["manifest"]["freeze_status"] == "FROZEN"


def test_fees_sentinel(raw_full, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    result = norm.normalize(raw_full)
    plan = norm.materialize(
        result, repo_root=repo, write=False, freeze=False, now=_FIXED_NOW
    )
    fees = plan["fees"]
    assert fees["status"] == norm.SENTINEL
    assert fees["taker_fee_bps"] == norm.SENTINEL
    assert fees["slippage_bps"] == norm.SENTINEL


# --- freeze artifacts ------------------------------------------------------


def test_checksums_file_is_correct(raw_full, tmp_path):
    import hashlib

    repo = tmp_path / "repo"
    repo.mkdir()
    norm.main(
        ["--raw-dir", str(raw_full), "--repo-root", str(repo),
         "--write", "--freeze"]
    )
    out = _out_dir(repo)
    checks = (out / norm.CHECKSUMS_FILE).read_text(encoding="utf-8")
    entries = [ln for ln in checks.splitlines() if ln.strip()]
    assert len(entries) == 3  # csv + manifest + fees
    for line in entries:
        digest, name = line.split("  ", 1)
        actual = hashlib.sha256((out / name).read_bytes()).hexdigest()
        assert digest == actual, f"checksum mismatch for {name}"


def test_freeze_record_content(raw_full, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    norm.main(
        ["--raw-dir", str(raw_full), "--repo-root", str(repo),
         "--write", "--freeze"]
    )
    out = _out_dir(repo)
    record = json.loads((out / norm.FREEZE_RECORD_FILE).read_text("utf-8"))
    assert record["operator"] == norm.OPERATOR_LABEL
    assert "kraken_tos_evidence_reference" in record
    assert "Kraken" in record["kraken_tos_evidence_reference"]
    assert record["freeze_timestamp"]
    assert record["data_contract_version"] == "crypto_d1_data_contract_v1"
    assert record["protocol_version"] == "crypto_d1_protocol_v1"


# --- determinism -----------------------------------------------------------


def test_normalize_is_deterministic(raw_full):
    a = norm.normalize(raw_full)
    b = norm.normalize(raw_full)
    assert a["csv_text"] == b["csv_text"]


def test_materialized_files_are_deterministic_given_fixed_now(raw_full, tmp_path):
    repo1 = tmp_path / "r1"
    repo1.mkdir()
    repo2 = tmp_path / "r2"
    repo2.mkdir()
    result = norm.normalize(raw_full)
    norm.materialize(
        result, repo_root=repo1, write=True, freeze=True, now=_FIXED_NOW
    )
    norm.materialize(
        result, repo_root=repo2, write=True, freeze=True, now=_FIXED_NOW
    )
    for name in (norm.DATA_FILE, norm.MANIFEST_FILE, norm.FEES_FILE,
                 norm.CHECKSUMS_FILE, norm.FREEZE_RECORD_FILE):
        b1 = (_out_dir(repo1) / name).read_bytes()
        b2 = (_out_dir(repo2) / name).read_bytes()
        assert b1 == b2, f"non-deterministic output: {name}"
