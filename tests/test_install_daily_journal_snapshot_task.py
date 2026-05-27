"""Tests for the daily-journal-snapshot scheduler PowerShell scripts.

Pure static text checks. Pytest does NOT register a Windows scheduled
task, does NOT invoke PowerShell, and does NOT touch the live Task
Scheduler. We only assert that the two .ps1 files contain the required
shape and contain nothing that resembles a trading-execution surface.

Covers:
  tools/install_daily_journal_snapshot_task.ps1
  tools/verify_daily_journal_snapshot_task.ps1
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


_REPO_ROOT = Path(__file__).resolve().parents[1]
_INSTALL_PS1 = _REPO_ROOT / "tools" / "install_daily_journal_snapshot_task.ps1"
_VERIFY_PS1 = _REPO_ROOT / "tools" / "verify_daily_journal_snapshot_task.ps1"

# Whole-word, case-insensitive bans. Whole-word matters because the
# Windows ScheduledTasks API uses parameter names like ExecutionTimeLimit
# that legitimately contain "Execution" as a substring; we don't want to
# trip on those, only on standalone trading language.
#
# Notes on words we intentionally do NOT ban here:
#   * "execute" — the ScheduledTaskAction object has a literal
#     `-Execute <path>` parameter, and `Format-List Execute, ...` is the
#     idiomatic way for the verifier to print it. Trading-execution
#     intent is already caught by the more specific bans below (broker,
#     order, exchange names, live trading, obsidian-trade-logger path).
_FORBIDDEN_WORDS = (
    "broker",
    "order",
    "optimize",
    "optimization",
    "fetch",
    "binance",
    "kraken",
    "coinbase",
    "metatrader",
    "quantconnect",
    "buy",
    "sell",
)

# Multi-word / path phrases that imply touching the external trading repo
# or live trading. These are substring matches because they are unique
# enough not to collide with scheduler API tokens.
#
# Note: the literal string "trades.db" is intentionally NOT in this list.
# The .ps1 safety comments legitimately reference it to *disavow* writes
# (e.g., "No write to trades.db; the adapter opens it with mode=ro"); a
# substring ban would punish that documentation. The actual operational
# guardrail is the absence of `obsidian-trade-logger` and of any Set-
# Content / Out-File / Add-Content directed at the external repo.
_FORBIDDEN_PHRASES = (
    "live trading",
    "live trade",
    "place order",
    "submit order",
    "obsidian-trade-logger",
    "start bot",
)


# --- helpers ---------------------------------------------------------------

def _read(path: Path) -> str:
    assert path.exists(), f"required file is missing: {path}"
    return path.read_text(encoding="utf-8")


def _strip_disavowal_lines(text: str) -> str:
    """Remove lines that DOCUMENT what the script doesn't do.

    The .ps1 files legitimately contain phrases like "NO BROKER" and
    "No live trading" inside:

      * PowerShell comment lines (`# ...`)
      * Safety-banner output lines (`Write-Output "Safety: ..."` or
        `Write-Host "Safety: ..."`)
      * The `-Description '...'` argument on Register-ScheduledTask

    Those are disavowals, not operational references. Stripping them
    before the forbidden-token scan lets the test focus on actual
    operational PowerShell, which must be clean."""
    out = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if re.match(
            r'^\s*Write-(Output|Host)\s+["\']Safety:', line
        ):
            continue
        if "-Description" in line:
            continue
        out.append(line)
    return "\n".join(out)


def _assert_no_forbidden_tokens(text: str, label: str) -> None:
    """Assert no forbidden whole-words and no forbidden phrases are in the
    *operational* portion of the script (disavowal lines stripped first)."""
    operational = _strip_disavowal_lines(text)
    lowered = operational.lower()
    for phrase in _FORBIDDEN_PHRASES:
        assert phrase not in lowered, (
            f"{label}: forbidden phrase {phrase!r} appears in operational script"
        )
    for word in _FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            raise AssertionError(
                f"{label}: forbidden whole-word {word!r} appears in "
                f"operational script (after stripping comments and "
                f"safety-banner output lines)"
            )


# --- install_daily_journal_snapshot_task.ps1 ------------------------------

def test_install_script_exists():
    assert _INSTALL_PS1.exists(), f"missing installer: {_INSTALL_PS1}"


def test_install_script_has_required_task_name():
    text = _read(_INSTALL_PS1)
    assert "'SPARTA Daily Journal Snapshot'" in text, (
        "installer must register a task named exactly "
        "'SPARTA Daily Journal Snapshot'"
    )


def test_install_script_has_python_path_and_exporter():
    text = _read(_INSTALL_PS1)
    assert r"C:\SPARTA_BRAIN\.venv\Scripts\python.exe" in text or \
        ".venv\\Scripts\\python.exe" in text, (
            "installer must reference the venv python interpreter"
        )
    assert "export_journal_snapshot.py" in text, (
        "installer must reference tools/export_journal_snapshot.py"
    )


def test_install_script_uses_required_trigger_time():
    text = _read(_INSTALL_PS1)
    assert "-Daily -At '01:10'" in text or '-Daily -At "01:10"' in text, (
        "installer must use Daily -At '01:10' trigger"
    )


def test_install_script_uses_required_working_directory():
    text = _read(_INSTALL_PS1)
    assert r"C:\SPARTA_BRAIN" in text, (
        "installer must reference the project root C:\\SPARTA_BRAIN"
    )
    # The WorkingDirectory parameter must be wired to the project root.
    assert "-WorkingDirectory" in text


def test_install_script_has_no_trading_keywords():
    _assert_no_forbidden_tokens(_read(_INSTALL_PS1), "install_daily_journal_snapshot_task.ps1")


def test_install_script_has_no_external_trading_repo_path():
    text = _read(_INSTALL_PS1).lower()
    assert "obsidian-trade-logger" not in text, (
        "installer must NOT reference the external trading repo path"
    )
    # Also assert no write redirection targeting that root.
    assert "users\\mahmo\\obsidian" not in text, (
        "installer must NOT path into the external trading repo"
    )


def test_install_script_declares_read_only_safety_banner():
    text = _read(_INSTALL_PS1)
    # The header comment block must declare the safety posture so an
    # operator reading the file sees the contract before they run it.
    assert "READ_ONLY" in text or "READ ONLY" in text
    assert "NO_BROKER" in text or "NO BROKER" in text
    assert "NO_ORDER" in text or "NO ORDER" in text
    assert "NO_OPTIMIZATION" in text or "NO OPTIMIZATION" in text


def test_install_script_replaces_existing_task_idempotently():
    """The installer must Unregister-ScheduledTask any same-named task
    before Register-ScheduledTask, so repeated runs leave exactly one
    task."""
    text = _read(_INSTALL_PS1)
    assert "Unregister-ScheduledTask" in text
    assert "Register-ScheduledTask" in text


# --- verify_daily_journal_snapshot_task.ps1 -------------------------------

def test_verify_script_exists():
    assert _VERIFY_PS1.exists(), f"missing verifier: {_VERIFY_PS1}"


def test_verify_script_inspects_required_task_name():
    text = _read(_VERIFY_PS1)
    # Accept either single- or double-quoted string assignment.
    assert (
        "'SPARTA Daily Journal Snapshot'" in text
        or '"SPARTA Daily Journal Snapshot"' in text
    ), "verifier must target the task name 'SPARTA Daily Journal Snapshot'"


def test_verify_script_prints_required_fields():
    """The verifier must surface every field the operator asked for:
    existence, action command + args, working directory, trigger time,
    last run time, and last task result.

    The check is behavioural — we look for access to the right API
    objects/fields rather than for specific Write-Output / Format-List
    string literals, so implementation rewrites stay compatible."""
    text = _read(_VERIFY_PS1)

    # Must call the read-only inspectors.
    assert "Get-ScheduledTask " in text or "Get-ScheduledTask\n" in text or "Get-ScheduledTask -" in text, (
        "verifier must call Get-ScheduledTask to find the task"
    )
    assert "Get-ScheduledTaskInfo" in text, (
        "verifier must call Get-ScheduledTaskInfo for last-run + result"
    )

    # Must reference the action subobject and the fields the spec lists.
    assert ".Actions" in text, "verifier must surface task .Actions"
    assert "Execute" in text, "verifier must surface action Execute"
    assert "Arguments" in text, "verifier must surface action Arguments"
    assert "WorkingDirectory" in text, "verifier must surface WorkingDirectory"

    # Must reference triggers somehow (either named field or Format-List *).
    assert ".Triggers" in text, "verifier must surface task .Triggers"

    # Must surface last-run + last-result.
    assert "LastRunTime" in text, "verifier must surface LastRunTime"
    assert "LastTaskResult" in text, "verifier must surface LastTaskResult"


def test_verify_script_has_no_register_or_modify_calls():
    """The verifier must be strictly read-only. No Register/Unregister/
    Start/Stop/Set-ScheduledTask calls allowed."""
    text = _read(_VERIFY_PS1)
    for cmdlet in (
        "Register-ScheduledTask",
        "Unregister-ScheduledTask",
        "Start-ScheduledTask",
        "Stop-ScheduledTask",
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
    ):
        assert cmdlet not in text, (
            f"verify script must not call {cmdlet} (read-only contract)"
        )


def test_verify_script_has_no_trading_keywords():
    _assert_no_forbidden_tokens(_read(_VERIFY_PS1), "verify_daily_journal_snapshot_task.ps1")


def test_verify_script_has_no_external_trading_repo_path():
    text = _read(_VERIFY_PS1).lower()
    assert "obsidian-trade-logger" not in text
    assert "users\\mahmo\\obsidian" not in text


# --- cross-file consistency -----------------------------------------------

def test_install_and_verify_target_same_task_name():
    """Two scripts, one task. The name string must be identical, regardless
    of whether the .ps1 uses single- or double-quoted string assignment."""
    inst = _read(_INSTALL_PS1)
    verify = _read(_VERIFY_PS1)
    pattern = re.compile(r"""\$TaskName\s*=\s*['"]([^'"]+)['"]""")
    m_inst = pattern.search(inst)
    m_verify = pattern.search(verify)
    assert m_inst is not None, "installer must define $TaskName"
    assert m_verify is not None, "verifier must define $TaskName"
    assert m_inst.group(1) == m_verify.group(1) == "SPARTA Daily Journal Snapshot"
