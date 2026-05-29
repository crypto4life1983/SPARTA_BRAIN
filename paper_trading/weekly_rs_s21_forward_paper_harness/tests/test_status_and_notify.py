"""Safety + dry-run tests for the weekly RS s21 paper status aggregator and notifier.

Synthetic / unit only. NO network (conftest sets HTTP(S)_PROXY=invalid), NO real Telegram send, NO cycle,
NO fetch, NO broker. Asserts: dry-run default, token never returned, secret-shape scrub, no send without
explicit enable, DIAGNOSTIC_ONLY footer on every template, READY/STALE logic, anti-spam, read-only behavior.
"""

import importlib
import pathlib
import sys

import pytest

REPO_ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "paper_trading").is_dir())
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
_BASE = "paper_trading.weekly_rs_s21_forward_paper_harness."
status = importlib.import_module(_BASE + "status")
notify = importlib.import_module("paper_trading.weekly_rs_s21_paper_notify")

# A clearly-fake, non-real token-shaped string used ONLY to prove the scrub blocks it.
_FAKE_TOKEN_SHAPED = "000000:" + ("A" * 35)


@pytest.fixture(autouse=True)
def _clear_telegram_env(monkeypatch):
    for k in ("SPARTA_TELEGRAM_TOKEN", "TELEGRAM_TOKEN", "SPARTA_TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_ID"):
        monkeypatch.delenv(k, raising=False)
    yield


def test_paper_status_reads_latest_cycle():
    s = status.paper_status()
    assert s["last_cycle_number"] is not None and s["last_cycle_number"] >= 2
    assert s["last_anchor_date"] == "2026-05-28"
    assert len(s["current_holdings"]) == 8
    # governance invariants are always surfaced
    assert s["frc_status"] == "NEVER_GRANTED"
    assert s["live_status"] == "BLOCKED_AT_6_GATES"
    assert s["trading_status"] == "PAUSED"
    assert s["no_broker"] and s["no_live_trading"] and s["no_fetch"]
    assert s["governance_banner"][0] == "DIAGNOSTIC_ONLY"


def test_readiness_logic():
    assert status.readiness("2026-05-28", "2026-05-28")[0] == "STALE"
    assert status.readiness("2026-05-28", "2026-06-04")[0] == "READY"
    assert status.readiness(None, "2026-06-04")[0] == "READY"
    assert status.readiness(None, None)[0] == "STALE"


def test_every_template_has_footer_and_diag():
    s = status.paper_status()
    msgs = [
        notify.msg_ready(s), notify.msg_stale(s), notify.msg_cycle_complete(s), notify.msg_killswitch(s),
        notify.msg_refresh_failed("refreshed_20260528", "2026-05-28", "HTTP 500"),
        notify.msg_push_commit("pushed master", "abc1234"),
    ]
    for m in msgs:
        assert notify.FOOTER in m
        assert "DIAGNOSTIC_ONLY" in m


def test_secret_status_never_returns_token(monkeypatch):
    monkeypatch.setenv("SPARTA_TELEGRAM_TOKEN", _FAKE_TOKEN_SHAPED)
    monkeypatch.setenv("SPARTA_TELEGRAM_CHAT_ID", "12345")
    ss = notify.secret_status()
    assert set(ss.keys()) == {"configured", "source"}
    assert ss["configured"] is True and ss["source"] == "environment"
    # the raw token must NOT appear anywhere in the public return
    assert _FAKE_TOKEN_SHAPED not in repr(ss)


def test_secret_shape_blocks_send():
    with pytest.raises(notify.SecretLeakBlocked):
        notify.notify("here is a leaked token %s in the body" % _FAKE_TOKEN_SHAPED, dry_run=True)


def test_notify_dry_run_sends_nothing():
    r = notify.notify("SPARTA Weekly RS s21 - Paper\nhello\n%s" % notify.FOOTER, dry_run=True)
    assert r["sent"] is False and r["dry_run"] is True


def test_no_real_send_without_enable(monkeypatch):
    # Even with a (fake) secret present, enable_send=False must never send.
    monkeypatch.setattr(notify, "_resolve_secret", lambda: ("000000:tok", "999", "environment"))
    # guard: if anything tried to actually send, fail loudly
    monkeypatch.setattr(notify, "_real_send", lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not send")))
    r = notify.notify("SPARTA Weekly RS s21 - Paper\nbody\n%s" % notify.FOOTER, dry_run=False, enable_send=False)
    assert r["sent"] is False and r["dry_run"] is True


def test_run_check_default_is_dry_and_read_only(tmp_path):
    runs_before = sorted(p.name for p in status.RUNS_DIR.iterdir()) if status.RUNS_DIR.exists() else []
    out = notify.run_check(state_path=tmp_path / "notify_state.json")
    assert out["dry_run"] is True
    assert all(r["sent"] is False for r in out["results"])
    # default run_check must not persist state and must not create/alter run dirs
    assert (tmp_path / "notify_state.json").exists() is False
    runs_after = sorted(p.name for p in status.RUNS_DIR.iterdir()) if status.RUNS_DIR.exists() else []
    assert runs_before == runs_after


def test_anti_spam_suppresses_repeat(tmp_path):
    sp = tmp_path / "notify_state.json"
    first = notify.run_check(state_path=sp, persist_state=True, dry_run=True)
    assert "cycle_complete" in first["fired"]
    assert sp.exists()
    second = notify.run_check(state_path=sp, persist_state=True, dry_run=True)
    assert "cycle_complete" not in second["fired"]


def test_run_check_never_imports_a_cycle_runner():
    # Structural guard: the notifier path must not expose / call the gated cycle runner.
    assert not hasattr(notify, "run_weekly_paper_cycle")
    assert not hasattr(status, "run_weekly_paper_cycle")
