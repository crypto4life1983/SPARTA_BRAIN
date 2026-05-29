"""Dry-run-default Telegram NOTIFIER for the weekly RS s21 broker-free paper process.

Lives OUTSIDE the harness package on purpose: the harness package
(weekly_rs_s21_forward_paper_harness/) has a hard no-network / no-key contract enforced by
tests/test_safety_guards.py (no os.environ, no urllib, etc.). This notifier necessarily reads a
Telegram token, so it must NOT sit inside that package. It consumes the harness's read-only status
aggregator and never reaches into harness mechanic code.

SAFETY MODEL (none may be weakened):
- DRY-RUN BY DEFAULT. A real send requires BOTH dry_run=False AND enable_send=True AND a configured
  secret, routed through the single existing transport boundary (tools/brain_telegram_notify).
- Secret resolution chain (first hit wins): (1) environment vars (SPARTA_TELEGRAM_TOKEN+CHAT_ID, or
  TELEGRAM_TOKEN+CHAT_ID), (2) the paper-specific gitignored local_secrets/weekly_rs_paper_telegram.json,
  (3) the existing SPARTA Telegram config loaded via tools/brain_telegram_notify.load_telegram_config()
  (which itself reads env + data/telegram_config.json + config/telegram_config.json + the external
  obsidian-trade-logger live_config.json). Tokens are NEVER printed, logged, returned to callers, or
  placed in a message body. local_secrets/ stays gitignored.
- Every message carries the DIAGNOSTIC_ONLY footer and is scrubbed: a Telegram-bot-token-shaped string
  in any message BLOCKS the send (SecretLeakBlocked).
- This module NEVER runs a cycle, fetches/refreshes data, or connects a broker.

DIAGNOSTIC_ONLY -- FRC NEVER_GRANTED -- Live BLOCKED_AT_6_GATES -- Trading PAUSED.
"""

import importlib.util as _ilu
import json as _json
import os as _os
import pathlib as _pathlib
import re as _re

from paper_trading.weekly_rs_s21_forward_paper_harness import status as _status

REPO_ROOT = _pathlib.Path(__file__).resolve().parents[1]
LOCAL_SECRET_PATH = REPO_ROOT / "local_secrets" / "weekly_rs_paper_telegram.json"
DEFAULT_STATE_PATH = _status.RUNS_DIR / "notify_state.json"

FOOTER = "[DIAGNOSTIC_ONLY · broker-free · FRC NEVER_GRANTED · no execution]"
# Telegram bot-token shape: <digits>:<>=30 base64-ish chars. Block if present in any outgoing text.
_SECRET_SHAPE = _re.compile(r"\b\d{6,12}:[A-Za-z0-9_-]{30,}\b")

EVENTS = ("ready", "stale", "cycle_complete", "killswitch", "refresh_failed", "push_commit")


class SecretLeakBlocked(RuntimeError):
    pass


# ---- secrets (token NEVER returned/printed) ----------------------------- #

def _resolve_secret():
    """Internal only. Returns (token, chat_id, source_label) by trying, in order: env vars, the paper
    local_secrets file, then the existing SPARTA Telegram config (via the existing transport loader).
    Callers MUST NOT log/return the token; it is handed directly to the transport on a real send.
    source_label is a coarse category only -- it never embeds a path that could include a token."""
    env = _os.environ
    token = env.get("SPARTA_TELEGRAM_TOKEN") or env.get("TELEGRAM_TOKEN")
    chat_id = env.get("SPARTA_TELEGRAM_CHAT_ID") or env.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        return token, chat_id, "environment"
    if LOCAL_SECRET_PATH.exists():
        try:
            data = _json.loads(LOCAL_SECRET_PATH.read_text(encoding="utf-8"))
            t = data.get("token") or data.get("bot_token")
            c = data.get("chat_id")
            if t and c:
                return t, c, "local_secrets"
        except Exception:
            pass
    # Fallback: existing SPARTA Telegram config via the existing transport's loader (lazy import).
    try:
        spec = _ilu.spec_from_file_location(
            "_brain_telegram_notify_resolver", str(REPO_ROOT / "tools" / "brain_telegram_notify.py"))
        mod = _ilu.module_from_spec(spec); spec.loader.exec_module(mod)
        cfg = mod.load_telegram_config()
        t = cfg.get("token"); c = cfg.get("chat_id"); src = cfg.get("source") or ""
        if t and c:
            if src == "environment":
                return t, c, "environment"
            if "live_config.json" in str(src):
                return t, c, "sparta_existing:external_live_config"
            return t, c, "sparta_existing:local_config"
    except Exception:
        pass
    return None, None, None


def secret_status():
    """PUBLIC: presence only. NEVER returns the token or chat_id."""
    token, chat_id, source = _resolve_secret()
    return {"configured": bool(token and chat_id), "source": source}


def _scrub(text):
    if _SECRET_SHAPE.search(text or ""):
        raise SecretLeakBlocked("secret-shaped token detected in message; send blocked")
    return text


# ---- message templates (A-F) -------------------------------------------- #

def msg_ready(s):
    return _scrub("\n".join([
        "SPARTA Weekly RS s21 - Paper",
        "READY: new weekly anchor available (%s)" % (s.get("next_expected_anchor") or "next bar"),
        "Last cycle: #%s @ %s" % (s.get("last_cycle_number"), s.get("last_anchor_date")),
        "Action: operator may authorize the next broker-free dry cycle. Nothing runs automatically.",
        FOOTER]))


def msg_stale(s):
    src = s.get("data_source") or {}
    return _scrub("\n".join([
        "SPARTA Weekly RS s21 - Paper",
        "NO-TRADE (STALE): %s" % s.get("next_cycle_reason", "no new anchor"),
        "Active source %s last bar %s. No cycle created. This is expected behavior, not an error." % (
            src.get("key"), src.get("last_date")),
        FOOTER]))


def msg_cycle_complete(s):
    return _scrub("\n".join([
        "SPARTA Weekly RS s21 - Paper",
        "Cycle #%s complete @ %s" % (s.get("last_cycle_number"), s.get("last_anchor_date")),
        "Equity: %s  -  Holdings (<=8): %s" % (s.get("latest_equity_usd"), ", ".join(s.get("current_holdings") or [])),
        "Verdict: %s  -  Kill-switch: %s" % (s.get("last_cycle_verdict"), s.get("killswitch_status")),
        FOOTER]))


def msg_killswitch(s):
    halt = s.get("killswitch_halt")
    tail = "HALT - paper test stopped; no auto-resume." if halt else "Review required; not auto-halted."
    return _scrub("\n".join([
        "SPARTA Weekly RS s21 - Paper",
        "KILL-SWITCH %s: %s" % (s.get("killswitch_status"), ", ".join(s.get("killswitch_reasons") or []) or "(none)"),
        "Cycle #%s @ %s. %s" % (s.get("last_cycle_number"), s.get("last_anchor_date"), tail),
        FOOTER]))


def msg_refresh_failed(source_key, last_date, short_reason):
    return _scrub("\n".join([
        "SPARTA Weekly RS s21 - Paper",
        "DATA REFRESH FAILED: %s" % short_reason,
        "Active source unchanged (%s, last %s). Sealed baseline untouched. No cycle run." % (source_key, last_date),
        FOOTER]))


def msg_push_commit(summary, short_hash):
    return _scrub("\n".join([
        "SPARTA Weekly RS s21 - Paper",
        "Repo update: %s  (HEAD %s)" % (summary, short_hash),
        FOOTER]))


# ---- anti-spam state ---------------------------------------------------- #

def load_state(path=DEFAULT_STATE_PATH):
    p = _pathlib.Path(path)
    if not p.exists():
        return {}
    try:
        d = _json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def save_state(state, path=DEFAULT_STATE_PATH):
    p = _pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return str(p)


def compute_events(s, state):
    """Diff current status `s` vs prior `state`; return [(event, text)] newly fired. PURE: no send, no
    state write, no cycle, no fetch. refresh_failed / push_commit are operator-passed, not derived here."""
    fired = []
    n = s.get("last_cycle_number")
    anchor = s.get("last_anchor_date")
    if n is not None and state.get("last_cycle_completed") != n:
        fired.append(("cycle_complete", msg_cycle_complete(s)))
        if s.get("killswitch_halt") or s.get("killswitch_status") in ("WARN", "REVIEW", "TRIGGERED"):
            fired.append(("killswitch", msg_killswitch(s)))
    if s.get("next_cycle") == "READY":
        if state.get("ready_anchor") != s.get("next_expected_anchor"):
            fired.append(("ready", msg_ready(s)))
    else:
        if state.get("stale_anchor") != anchor:
            fired.append(("stale", msg_stale(s)))
    return fired


# ---- send (dry-run default; real send behind explicit enable) ----------- #

def _real_send(text, token, chat_id):
    """Route a real send through the single existing transport boundary, loaded by file path so we do not
    depend on `tools` being importable. Only reached when explicitly enabled. Token passed straight to the
    transport, never logged here."""
    spec = _ilu.spec_from_file_location("_brain_telegram_notify", str(REPO_ROOT / "tools" / "brain_telegram_notify.py"))
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return bool(mod.send_telegram_message(text, token=token, chat_id=chat_id))


def notify(text, *, dry_run=True, enable_send=False):
    """DRY-RUN by default: returns the text, sends nothing. A real send needs dry_run=False AND
    enable_send=True AND a configured secret. Token is read internally and never returned."""
    text = _scrub(text)
    if dry_run or not enable_send:
        return {"sent": False, "dry_run": True, "text": text, "reason": "dry-run default"}
    token, chat_id, source = _resolve_secret()
    if not (token and chat_id):
        return {"sent": False, "dry_run": True, "text": text, "reason": "no secret configured; send skipped"}
    ok = _real_send(text, token, chat_id)
    return {"sent": ok, "dry_run": False, "text": text, "source": source}


def run_check(*, dry_run=True, enable_send=False, persist_state=False,
              state_path=DEFAULT_STATE_PATH, data_source=None, runs_dir=None):
    """Read status, compute newly-fired events, (dry-run) emit them, optionally persist anti-spam state.
    READ-ONLY w.r.t. the paper process: never runs a cycle, fetches, refreshes, or connects a broker."""
    s = _status.paper_status(data_source=data_source, runs_dir=runs_dir or _status.RUNS_DIR)
    state = load_state(state_path)
    fired = compute_events(s, state)
    results = [{"event": ev, **notify(txt, dry_run=dry_run, enable_send=enable_send)} for ev, txt in fired]
    if s.get("last_cycle_number") is not None:
        state["last_cycle_completed"] = s["last_cycle_number"]
    if s.get("next_cycle") == "READY":
        state["ready_anchor"] = s.get("next_expected_anchor")
    else:
        state["stale_anchor"] = s.get("last_anchor_date")
    if persist_state:
        save_state(state, state_path)
    return {"status": s, "fired": [r["event"] for r in results], "results": results,
            "secret": secret_status(), "dry_run": bool(dry_run or not enable_send), "state_persisted": bool(persist_state)}
