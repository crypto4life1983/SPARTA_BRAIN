"""Tests for the /journal route — SPARTA Trade Intelligence Journal v1.

Coverage:
- GET /journal returns 200.
- Page renders required identifiers: title, READ ONLY, Trading PAUSED,
  BLOCKED_AT_6_GATES.
- Page has no <form> tag and no POST method.
- Page contains no live-trading / broker action words or buttons.
- When the adapter returns a MISSING payload, the page renders MISSING
  instead of fabricated values.
- When the adapter raises, the route still returns 200 with an ERROR
  banner and fail-closed posture.

Style mirrors tests/test_app_command_route.py and
tests/test_app_shadow_validator_route.py: pytest.importorskip on fastapi,
lazy TestClient import inside each test body to keep httpx out of the
runtime safety scan.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


pytest.importorskip("fastapi")

_REPO_ROOT = Path(__file__).resolve().parents[1]


# --- basic route renders ----------------------------------------------------

def test_journal_route_returns_200():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/journal")
    assert r.status_code == 200


def test_journal_route_renders_title_and_posture_pills():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/journal")
    body = r.text
    assert "SPARTA Trade Intelligence Journal" in body
    assert "READ ONLY" in body
    assert "Trading PAUSED" in body
    assert "BLOCKED_AT_6_GATES" in body


def test_journal_route_has_required_sections():
    """All eleven structural sections must render so the operator sees a
    consistent layout whether data is present or MISSING."""
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/journal")
    body = r.text
    for needle in (
        "Data status",
        "Summary",
        "Evidence Quality",
        "Unified gate strip",
        "Strategy scorecard",
        "Symbol performance",
        "Daily P&amp;L correlation",
        "Monte Carlo summary",
        "Risk of ruin",
        "Weekday performance",
        "Month performance",
        "Missing data",
    ):
        assert needle in body, f"missing section: {needle}"


# --- read-only contract ----------------------------------------------------

def test_journal_route_has_no_form_or_post():
    """No <form>, no method=POST — read-only HTML only."""
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/journal")
    body_lower = r.text.lower()
    assert "<form" not in body_lower, "rendered HTML must contain no <form>"
    assert 'method="post"' not in body_lower
    assert "method='post'" not in body_lower


def test_journal_route_405_on_non_get_verbs():
    """POST/PUT/PATCH/DELETE on /journal must return 405."""
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    for verb in ("post", "put", "patch", "delete"):
        method = getattr(client, verb)
        r = method("/journal")
        assert r.status_code == 405, (
            f"{verb.upper()} /journal returned {r.status_code}, expected 405"
        )


def test_journal_route_has_no_action_words_or_buttons():
    """Page must not contain trading-action language as visible buttons or
    interactive controls. We scan the rendered body for forbidden words in
    contexts that imply user-triggerable actions."""
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/journal")
    body = r.text
    body_lower = body.lower()

    # Hard ban: any <button> or onclick handler. The page is GET-only.
    assert "<button" not in body_lower, "rendered page must not contain <button>"
    assert "onclick=" not in body_lower, "rendered page must not contain onclick="

    # Forbidden action phrases / buttons that imply trading or live ops.
    forbidden_phrases = (
        "place order",
        "start bot",
        "stop bot",
        "broker connect",
        "connect broker",
        "execute trade",
        "live trade",
        "go live",
        "submit order",
        "buy now",
        "sell now",
    )
    for phrase in forbidden_phrases:
        assert phrase not in body_lower, (
            f"rendered page contains forbidden phrase: {phrase!r}"
        )

    # Whole-word ban on the lone action verbs Buy / Sell / Execute. We
    # allow the substring inside surrounding words (best_strategy, etc.)
    # but not as a standalone token.
    for token in ("buy", "sell", "execute"):
        if re.search(rf"\b{token}\b", body_lower):
            raise AssertionError(
                f"rendered page contains standalone action verb: {token!r}"
            )


# --- MISSING fail-closed ---------------------------------------------------

def test_journal_route_renders_missing_when_adapter_empty(monkeypatch):
    """If the adapter returns a fully-MISSING payload, the page must render
    MISSING markers instead of fabricated values."""
    import app as app_module
    from fastapi.testclient import TestClient
    from tools import trade_journal_adapter as _tja

    def _fake_load_payload():
        # Reuse the adapter's own empty-payload shape so we test against
        # the schema the route actually expects.
        return _tja._empty_payload(status="MISSING")

    monkeypatch.setattr(_tja, "load_payload", _fake_load_payload)

    client = TestClient(app_module.app)
    r = client.get("/journal")
    assert r.status_code == 200
    body = r.text
    # Status pill on the data-status section.
    assert "MISSING" in body
    # Specific empty-state markers from the template.
    assert "MISSING: no strategy scorecard rows." in body
    assert "MISSING: no per-symbol metrics." in body
    # No fabricated numeric values: the placeholder dash must appear.
    assert "&mdash;" in body or "—" in body


def test_journal_scorecard_uses_live_db_over_stale_si_report(
    monkeypatch, tmp_path
):
    """Regression: when the on-disk SI report shows 0 closed trades for
    D2/F2/G but the live trades.db rows contain closed trades for those
    strategies, the /journal scorecard table must show the live DB counts
    (not the stale 0s), and a stale-SI warning must surface in the
    Missing data & warnings section.
    """
    import app as app_module
    from fastapi.testclient import TestClient
    from tools import trade_journal_adapter as _tja

    fake_si = {
        "generated_at": "2026-05-04T21:46:51.562257+00:00",
        "per_strategy": {
            "D2": {
                "total_trades": 2, "open_trades": 2, "closed_trades": 0,
                "win_rate": "INSUFFICIENT_DATA",
                "expectancy_R": "INSUFFICIENT_DATA",
                "profit_factor": "INSUFFICIENT_DATA",
                "long_performance": "INSUFFICIENT_DATA",
                "short_performance": "INSUFFICIENT_DATA",
                "best_symbol": None, "worst_symbol": None,
                "confidence": 20, "confidence_label": "LOW",
                "data_quality": "LOW",
            },
            "F2": {
                "total_trades": 2, "open_trades": 2, "closed_trades": 0,
                "win_rate": "INSUFFICIENT_DATA",
                "expectancy_R": "INSUFFICIENT_DATA",
                "profit_factor": "INSUFFICIENT_DATA",
                "long_performance": "INSUFFICIENT_DATA",
                "short_performance": "INSUFFICIENT_DATA",
                "best_symbol": None, "worst_symbol": None,
                "confidence": 20, "confidence_label": "LOW",
                "data_quality": "LOW",
            },
            "G": {
                "total_trades": 1, "open_trades": 1, "closed_trades": 0,
                "win_rate": "INSUFFICIENT_DATA",
                "expectancy_R": "INSUFFICIENT_DATA",
                "profit_factor": "INSUFFICIENT_DATA",
                "long_performance": "INSUFFICIENT_DATA",
                "short_performance": "INSUFFICIENT_DATA",
                "best_symbol": None, "worst_symbol": None,
                "confidence": 20, "confidence_label": "LOW",
                "data_quality": "LOW",
            },
        },
        "per_symbol": {
            "XRPUSDT": {
                "best_strategy": None, "worst_strategy": None,
                "total_exposure_attempts": 5,
                "blocked_attempts": 0, "open_lock": True,
            },
        },
        "global": {},
    }

    # Live trade rows: D2 has 2 closed, F2 has 2 closed, G has 2 closed
    # (1 timeout + 1 loss) + 1 open. Mirrors the real shape of the live DB.
    def _row(rid, strat, outcome, close_date, pnl_r, pnl_usd):
        return {
            "id": rid, "exchange": "kraken", "symbol": "XRPUSDT",
            "strategy": strat, "direction": "short" if strat in ("D2", "F2") else "long",
            "entry": 1.0, "sl": 1.05, "size_usd": 100.0,
            "open_date": "2026-04-28",
            "close_date": close_date,
            "outcome": outcome, "pnl_r": pnl_r, "pnl_usd": pnl_usd,
            "max_favorable_R": None, "max_adverse_R": None,
        }
    fake_rows = [
        _row(13, "D2", "LOSS", "2026-05-15", -1.357, -27.14),
        _row(15, "D2", "LOSS", "2026-05-15", -1.415, -28.31),
        _row(14, "F2", "LOSS", "2026-05-15", -1.357, -27.14),
        _row(16, "F2", "LOSS", "2026-05-15", -1.415, -28.31),
        _row(17, "G",  "TIMEOUT", "2026-05-19",  0.126,   2.51),
        _row(25, "G",  "LOSS",    "2026-05-23", -0.439,  -8.77),
        _row(99, "G",  None,      None,          None,    None),  # open
    ]

    # Fixture filesystem: a real tmp_path with a zero-byte trades.db so the
    # adapter's `db_path.exists()` check passes and staleness compares
    # against a real (fresh) mtime. The actual SQLite read is monkeypatched.
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "trades.db").write_bytes(b"")

    monkeypatch.setattr(_tja, "external_root", lambda: tmp_path)

    real_safe_load = _tja._safe_load_json

    def fake_safe_load_json(path):
        s = str(path).replace("\\", "/")
        if s.endswith("strategy_intelligence_report.json"):
            return dict(fake_si)
        # All other JSON loads (sp_report, gate state files) → MISSING.
        return None

    monkeypatch.setattr(_tja, "_safe_load_json", fake_safe_load_json)
    monkeypatch.setattr(
        _tja, "_read_trades_ro", lambda _db_path: (list(fake_rows), None),
    )

    client = TestClient(app_module.app)
    r = client.get("/journal")
    assert r.status_code == 200
    body = r.text

    # Each scorecard row begins with <td>{strategy}</td><td>{closed_trades}</td>.
    # The whitespace between cells depends on Jinja whitespace; allow any.
    for strat, expected_closed in (("D2", 2), ("F2", 2), ("G", 2)):
        m = re.search(rf"<td>{strat}</td>\s*<td>(\d+)</td>", body)
        assert m is not None, (
            f"could not locate scorecard row for {strat!r} in rendered HTML"
        )
        actual = int(m.group(1))
        assert actual == expected_closed, (
            f"scorecard for {strat!r} shows closed={actual}, expected "
            f"{expected_closed}. If actual==0, the stale SI snapshot is "
            f"still overriding live DB rows — the precedence fix regressed."
        )

    # Stale warning must surface in the Missing data & warnings section.
    assert "strategy_intelligence_report_stale" in body, (
        "expected the SI-stale warning string to appear in the rendered page"
    )

    # And the live DB must be flagged as the authoritative data source.
    assert "trades_db" in body, (
        "expected the data-status section to indicate trades_db as the source"
    )

    # Restore _safe_load_json so other monkeypatched tests see the original
    # behaviour. (monkeypatch fixture does this automatically on teardown.)
    _ = real_safe_load


def test_journal_evidence_quality_observation_only_with_seven_closed(
    monkeypatch, tmp_path
):
    """With 7 closed trades the Evidence Quality section must:

      * render the OBSERVATION_ONLY final-state label,
      * mark Monte Carlo, Risk of Ruin, and Daily Correlation as BLOCKED
        with the documented label strings,
      * mark per-strategy minimum sample size as
        INSUFFICIENT_FOR_STRATEGY_CONFIDENCE,
      * keep the existing stale-SI warning rendering when the SI snapshot
        is older than the trades.db mtime.
    """
    import app as app_module
    from fastapi.testclient import TestClient
    from tools import trade_journal_adapter as _tja

    # Stale SI snapshot — same shape as the production file.
    fake_si = {
        "generated_at": "2026-05-04T21:46:51.562257+00:00",
        "per_strategy": {
            "D2": {"closed_trades": 0, "total_trades": 2, "open_trades": 2},
            "F2": {"closed_trades": 0, "total_trades": 2, "open_trades": 2},
            "G":  {"closed_trades": 0, "total_trades": 1, "open_trades": 1},
        },
        "per_symbol": {},
        "global": {},
    }

    def _row(rid, strat, outcome, close_date, pnl_r, pnl_usd, symbol="XRPUSDT"):
        return {
            "id": rid, "exchange": "kraken", "symbol": symbol,
            "strategy": strat,
            "direction": "short" if strat in ("D2", "F2") else "long",
            "entry": 1.0, "sl": 1.05, "size_usd": 100.0,
            "open_date": "2026-04-28",
            "close_date": close_date,
            "outcome": outcome, "pnl_r": pnl_r, "pnl_usd": pnl_usd,
            "max_favorable_R": None, "max_adverse_R": None,
        }

    # Exactly 7 closed trades, matching the live DB shape on 2026-05-27.
    fake_rows = [
        _row(13, "D2", "LOSS",    "2026-05-15", -1.357, -27.14),
        _row(15, "D2", "LOSS",    "2026-05-15", -1.415, -28.31),
        _row(14, "F2", "LOSS",    "2026-05-15", -1.357, -27.14),
        _row(16, "F2", "LOSS",    "2026-05-15", -1.415, -28.31),
        _row(18, "D",  "LOSS",    "2026-05-18", -1.082, -21.65, symbol="BNBUSDT"),
        _row(17, "G",  "TIMEOUT", "2026-05-19",  0.126,   2.51),
        _row(25, "G",  "LOSS",    "2026-05-23", -0.439,  -8.77),
        # An open trade so the per-strategy fallback still surfaces D and G
        # as active without contributing to the closed count.
        _row(99, "G",  None, None, None, None),
    ]

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "trades.db").write_bytes(b"")

    monkeypatch.setattr(_tja, "external_root", lambda: tmp_path)
    monkeypatch.setattr(
        _tja,
        "_safe_load_json",
        lambda path: (
            dict(fake_si)
            if str(path).replace("\\", "/").endswith(
                "strategy_intelligence_report.json"
            )
            else None
        ),
    )
    monkeypatch.setattr(
        _tja, "_read_trades_ro", lambda _db_path: (list(fake_rows), None),
    )

    client = TestClient(app_module.app)
    r = client.get("/journal")
    assert r.status_code == 200
    body = r.text

    # Section header must render.
    assert "Evidence Quality" in body

    # Final state must be OBSERVATION_ONLY (7 closed < 30 + multiple blocking checks).
    assert "OBSERVATION_ONLY" in body, (
        "expected Evidence Quality final state to render as OBSERVATION_ONLY"
    )

    # Documented blocking-label strings must surface.
    for needle in (
        "INSUFFICIENT_FOR_STRATEGY_CONFIDENCE",
        "MONTE_CARLO_BLOCKED_N_LT_10",
        "RISK_OF_RUIN_BLOCKED_N_LT_10",
        "DAILY_CORRELATION_BLOCKED_N_DAYS_LT_5",
    ):
        assert needle in body, f"expected blocking label {needle!r} in HTML"

    # Stale-SI warning must still render alongside the new section.
    assert "strategy_intelligence_report_stale" in body, (
        "stale SI warning must still appear in the rendered page"
    )

    # No new <button>, <form>, or onclick handlers introduced by the
    # Evidence Quality block.
    body_lower = body.lower()
    assert "<form" not in body_lower
    assert "<button" not in body_lower
    assert "onclick=" not in body_lower
    assert 'method="post"' not in body_lower


def test_journal_evidence_quality_renders_when_payload_empty(monkeypatch):
    """The Evidence Quality section must still render (with MISSING) when
    the adapter returns the empty payload — never crash on a missing
    `evidence_quality` field."""
    import app as app_module
    from fastapi.testclient import TestClient
    from tools import trade_journal_adapter as _tja

    monkeypatch.setattr(
        _tja, "load_payload", lambda: _tja._empty_payload(status="MISSING"),
    )
    client = TestClient(app_module.app)
    r = client.get("/journal")
    assert r.status_code == 200
    body = r.text
    assert "Evidence Quality" in body
    # The empty-payload default surfaces MISSING for evidence_quality.
    assert "evidence quality not computed" in body


def test_journal_route_renders_error_when_adapter_raises(monkeypatch):
    """If the adapter raises, the route must still return 200 and render
    an ERROR banner. Fail-closed: no fabricated data."""
    import app as app_module
    from fastapi.testclient import TestClient
    from tools import trade_journal_adapter as _tja

    def _boom():
        raise RuntimeError("simulated adapter failure for test")

    monkeypatch.setattr(_tja, "load_payload", _boom)

    client = TestClient(app_module.app)
    r = client.get("/journal")
    assert r.status_code == 200
    body = r.text
    assert "ERROR" in body
    # The error message itself should surface in the warnings list so the
    # operator can see WHY the page is in ERROR state.
    assert "simulated adapter failure for test" in body
    # Even in ERROR state the safety pills must still be visible.
    assert "READ ONLY" in body
    assert "Trading PAUSED" in body
    assert "BLOCKED_AT_6_GATES" in body
    # Fail-closed banner copy.
    assert "Fail-closed" in body or "fail-closed" in body
