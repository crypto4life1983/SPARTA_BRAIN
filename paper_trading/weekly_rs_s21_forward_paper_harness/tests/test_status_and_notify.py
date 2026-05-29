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


# === enablement BUILD — explicit safety guarantees =========================== #

def test_real_send_path_reachable_only_via_explicit_enable(monkeypatch):
    """Guarantee #3: _real_send is invoked ONLY when BOTH dry_run=False AND enable_send=True AND a
    secret is configured. All other combinations leave it untouched."""
    monkeypatch.setattr(notify, "_resolve_secret", lambda: ("000000:tok", "999", "test"))
    calls = []
    monkeypatch.setattr(notify, "_real_send", lambda text, t, c: (calls.append((text, t, c)), True)[1])

    body = "SPARTA Weekly RS s21 - Paper\nhello\n" + notify.FOOTER
    # (a) dry-run default -> not called
    r1 = notify.notify(body)
    assert r1["sent"] is False and len(calls) == 0
    # (b) enable_send=False -> not called
    r2 = notify.notify(body, dry_run=False, enable_send=False)
    assert r2["sent"] is False and len(calls) == 0
    # (c) dry_run=True still wins even if enable_send=True -> not called
    r3 = notify.notify(body, dry_run=True, enable_send=True)
    assert r3["sent"] is False and len(calls) == 0
    # (d) only when both flags are flipped AND secret present -> called exactly once
    r4 = notify.notify(body, dry_run=False, enable_send=True)
    assert r4["sent"] is True and len(calls) == 1
    assert calls[0][0] == body  # exact text we passed (post-scrub)


def test_real_send_skipped_when_no_secret(monkeypatch):
    monkeypatch.setattr(notify, "_resolve_secret", lambda: (None, None, None))
    sentinel = []
    monkeypatch.setattr(notify, "_real_send", lambda *a, **k: sentinel.append(1))
    r = notify.notify("body\n" + notify.FOOTER, dry_run=False, enable_send=True)
    assert r["sent"] is False and r["dry_run"] is True
    assert sentinel == []
    assert "no secret configured" in r.get("reason", "")


def test_telegram_failure_has_no_side_effects(monkeypatch, tmp_path):
    """Guarantee #6: a Telegram-API failure (transport returns False) must NOT run a cycle, modify
    any harness ledger file, or touch sealed artifacts. We snapshot the cycle 002 files before/after."""
    import hashlib
    cycle_dir = status.RUNS_DIR / "dry_cycle_002"
    files = ["paper_orders.jsonl", "paper_trades_closed.jsonl", "killswitch_status.json",
            "paper_weekly_report_002.md"]
    def snap():
        out = {}
        for f in files:
            p = cycle_dir / f
            out[f] = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        return out
    before_files = snap()
    before_runs = sorted(d.name for d in status.RUNS_DIR.iterdir() if d.is_dir())

    monkeypatch.setattr(notify, "_resolve_secret", lambda: ("000000:tok", "999", "test"))
    monkeypatch.setattr(notify, "_real_send", lambda *a, **k: False)  # simulate Telegram failure

    r = notify.notify("body\n" + notify.FOOTER, dry_run=False, enable_send=True)
    assert r["sent"] is False  # graceful failure, no exception

    after_files = snap()
    after_runs = sorted(d.name for d in status.RUNS_DIR.iterdir() if d.is_dir())
    assert before_files == after_files, "Telegram failure must not modify harness ledger files"
    assert before_runs == after_runs, "Telegram failure must not create/remove run dirs"


def test_notifier_references_no_dangerous_harness_functions():
    """Guarantee #7: the notifier source must NOT reference any broker/live/Strategy-Lab/FRC/cycle
    runner symbol. Structural scan of the notify.py source."""
    import inspect
    src = inspect.getsource(notify)
    for fn in ("run_weekly_paper_cycle", "connect_broker", "place_live_order",
              "paper_trade_via_broker", "submit_to_strategy_lab", "request_frc",
              "fetch_market_data"):
        assert fn not in src, "notifier source references forbidden symbol %r" % fn


def test_sparta_existing_config_fallback_labelled_coarsely(monkeypatch, tmp_path):
    """Guarantee: the SPARTA existing-config fallback works AND the source label is a coarse category
    (never a file path that might embed a token)."""
    fake_token = "111111:" + ("B" * 35)  # synthetic, not real
    fake_chat = "55555"

    # Build a fake brain_telegram_notify shim that returns the fake config.
    shim = tmp_path / "tools" / "brain_telegram_notify.py"
    shim.parent.mkdir(parents=True, exist_ok=True)
    shim.write_text(
        "def load_telegram_config():\n"
        "    return {'token': %r, 'chat_id': %r, 'source': r'C:\\\\Users\\\\x\\\\obsidian-trade-logger\\\\config\\\\live_config.json'}\n"
        % (fake_token, fake_chat), encoding="utf-8")

    monkeypatch.setattr(notify, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(notify, "LOCAL_SECRET_PATH", tmp_path / "local_secrets" / "absent.json")

    ss = notify.secret_status()
    assert ss["configured"] is True
    assert ss["source"] == "sparta_existing:external_live_config"
    # token and chat MUST NOT appear in the public return
    assert fake_token not in repr(ss) and fake_chat not in repr(ss)
    # path components MUST NOT appear in the source label
    assert "live_config.json" not in ss["source"] or ss["source"] == "sparta_existing:external_live_config"
    assert "\\" not in ss["source"] and "/" not in ss["source"].split(":")[-1]


def test_env_priority_beats_files(monkeypatch, tmp_path):
    """Env-var token must win over any file-based source."""
    monkeypatch.setenv("SPARTA_TELEGRAM_TOKEN", "999999:" + "C" * 35)
    monkeypatch.setenv("SPARTA_TELEGRAM_CHAT_ID", "1")
    # Make file sources also "available" (they should be ignored).
    shim = tmp_path / "tools" / "brain_telegram_notify.py"
    shim.parent.mkdir(parents=True, exist_ok=True)
    shim.write_text(
        "def load_telegram_config():\n"
        "    return {'token': 'xxx', 'chat_id': 'yyy', 'source': 'config/telegram_config.json'}\n",
        encoding="utf-8")
    monkeypatch.setattr(notify, "REPO_ROOT", tmp_path)
    ss = notify.secret_status()
    assert ss["configured"] is True and ss["source"] == "environment"


def test_resolver_returns_none_when_nothing_configured(monkeypatch, tmp_path):
    """With env cleared (autouse), local_secrets absent, and no tools/brain_telegram_notify.py present,
    the resolver must return (None, None, None) -- never crash, never expose anything."""
    monkeypatch.setattr(notify, "REPO_ROOT", tmp_path)  # tools/ doesn't exist here
    monkeypatch.setattr(notify, "LOCAL_SECRET_PATH", tmp_path / "local_secrets" / "absent.json")
    t, c, s = notify._resolve_secret()
    assert (t, c, s) == (None, None, None)
    ss = notify.secret_status()
    assert ss == {"configured": False, "source": None}


def test_dry_run_and_enable_send_false_both_send_nothing_even_with_real_secret(monkeypatch):
    """Belt-and-braces version of guarantees #1 + #2 with a real (but fake) secret present."""
    monkeypatch.setattr(notify, "_resolve_secret", lambda: ("777777:" + "D" * 35, "42", "test"))
    monkeypatch.setattr(notify, "_real_send",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not send")))
    out = notify.run_check()  # defaults
    assert out["dry_run"] is True
    assert all(r["sent"] is False for r in out["results"])
    out2 = notify.notify("body\n" + notify.FOOTER, dry_run=False, enable_send=False)
    assert out2["sent"] is False
