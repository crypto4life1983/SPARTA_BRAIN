"""Tests for the Factory-D9 minimal safe validation-factory CLI.

Covers list-modules / describe / version / synthetic-smoke dispatch and exit
codes, the safe-module synthetic report write, refusal of a missing output dir,
refusal of describe-only (real-data) modules, the absence of any paper/live/deploy
command, the help-text safety banner, an offline-source token scan, and a
no-real-data source scan.

Synthetic temp dirs only. No real NQ/ES CSVs are read; no strategy is backtested;
no real in-sample / out-of-sample data is used.
"""

import json
import os

from engine import validation_cli as CLI
from engine import validation_reports as VR


# 1 -- list-modules exits 0 and includes the key ladder modules.
def test_list_modules_exit0_includes_key(capsys):
    rc = CLI.main(["list-modules"])
    out = capsys.readouterr().out
    assert rc == 0
    for m in ("report_schema", "sequence_risk", "friction", "final_decision"):
        assert m in out


# 2 -- describe of a known module exits 0 and prints its required inputs.
def test_describe_known_exit0(capsys):
    rc = CLI.main(["describe", "--module", "friction"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "module: friction" in out
    assert "required inputs:" in out


# 3 -- describe of an unknown module exits nonzero.
def test_describe_unknown_nonzero():
    assert CLI.main(["describe", "--module", "does_not_exist"]) != 0
    # missing --module is also a usage error.
    assert CLI.main(["describe"]) != 0


# 4 -- version exits 0 and prints a non-empty version string.
def test_version_exit0(capsys):
    rc = CLI.main(["version"])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.strip()


# 5 -- an unsupported command exits nonzero.
def test_unsupported_command_nonzero():
    assert CLI.main(["frobnicate"]) != 0
    assert CLI.main([]) != 0


# 6 -- synthetic-smoke writes a schema-valid report.json/report.md to a temp dir.
def test_synthetic_smoke_writes_reports(tmp_path):
    dest = str(tmp_path / "out")
    rc = CLI.main(["synthetic-smoke", "--module", "friction", "--output-dir", dest])
    assert rc == 0
    json_path = os.path.join(dest, "report.json")
    md_path = os.path.join(dest, "report.md")
    assert os.path.isfile(json_path)
    assert os.path.isfile(md_path)
    with open(json_path, "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    assert VR.validate_report(loaded) == []
    assert loaded["module_id"] == "friction_stress"


# 7 -- synthetic-smoke refuses a missing / empty output dir and writes nothing.
def test_synthetic_smoke_missing_output_dir_refused(tmp_path):
    assert CLI.main(["synthetic-smoke", "--module", "friction"]) != 0
    assert CLI.main(["synthetic-smoke", "--module", "friction", "--output-dir", ""]) != 0
    # nothing was created under the temp dir.
    assert list(tmp_path.iterdir()) == []


# 8 -- the CLI source reads no real market data (no CSV/data-loading references).
def test_module_reads_no_real_data():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_cli.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    for token in [".csv", "data_offline", "load_daily_bars", "load_yearly_csvs", "open("]:
        assert token not in text, f"CLI references real-data token: {token}"


# 9 -- CLI source is offline/inert (no network/exec/dynamic-import/VC tokens).
def test_module_source_is_offline_inert():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_cli.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "subprocess", "socket", "urllib", "requests", "httpx", "aiohttp",
        "websockets", "ccxt", "binance", "bybit", "alpaca", "ib_insync",
        "broker", "api_key", "os.system", "exec(", "eval(",
        "importlib", "__import__", "git",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in CLI source: {hits}"


# 10 -- the CLI supports no paper / live / deploy commands.
def test_no_paper_live_deploy_commands():
    for cmd in ("paper", "live", "deploy", "trade", "broker", "order"):
        assert CLI.main([cmd]) != 0, f"command unexpectedly accepted: {cmd}"


# 11 -- the help banner states the no-optimization / no-paper-live posture.
def test_help_mentions_no_optimization_no_paper_live(capsys):
    rc = CLI.main(["--help"])
    out = capsys.readouterr().out.lower()
    assert rc == 0
    assert "no optimization" in out
    assert "no paper/live" in out


# 12 -- a describe-only (real-strategy/data) module is refused for synthetic-smoke,
#       proving the smoke path never fabricates a real backtest. Temp dir only.
def test_real_data_module_refused_for_smoke(tmp_path):
    dest = str(tmp_path / "out")
    assert CLI.main(["synthetic-smoke", "--module", "is_baseline", "--output-dir", dest]) != 0
    assert CLI.main(["synthetic-smoke", "--module", "oos_run", "--output-dir", dest]) != 0
    # refusal wrote nothing.
    assert not os.path.exists(dest)
