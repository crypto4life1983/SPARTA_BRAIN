"""Tests for the /command route — SPARTA Trading Command Center v1.

Authorized by: docs/sparta_command_center_first_build_plan.md (commit 970452c)
Plan section 10 defines the required coverage; this module implements it.

Coverage:
- GET /command returns 200 with at least one B006_* lifecycle row
- B006_002 renders (real on-disk state)
- Phase ladder rows render
- Page contains no <form> and no method="POST"
- Non-GET verbs return 405
- SEAL_DRIFT flag fires when a sidecar pin disagrees with the file body
- Route does not write to any artifact under reports/external_research_hunter/
- Posture invariants strip renders (Trading PAUSED / etc.)
- MISSING flag fires when no artifacts are present (fail-closed, no fabrication)
- No external network call is made while rendering the route
- Static scan: the /command block in app.py has no forbidden tokens
"""
from __future__ import annotations

import hashlib
import json
import re
import socket
import sys
from pathlib import Path

import pytest


pytest.importorskip("fastapi")
# NOTE: TestClient (which pulls in httpx) is imported lazily inside each
# test body, mirroring tests/test_app_shadow_validator_route.py. Keeping
# httpx out of module-level imports preserves the Phase 5B safety scan
# `test_no_third_party_network_or_broker_in_runtime_imports`.

_REPO_ROOT = Path(__file__).resolve().parents[1]


# --- route renders --------------------------------------------------------

def test_command_route_returns_200():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/command")
    assert r.status_code == 200


def test_command_route_renders_b006_002():
    """Real on-disk B006_002 lifecycle must surface, including its REJECT_FAST
    sealed verdict (sealed in archived commit a2ca6f7-precursor history)."""
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/command")
    body = r.text
    assert "B006_002" in body
    assert "REJECT_FAST" in body


def test_command_route_renders_phase_ladder():
    """All 9 phases (0-8) and their canonical labels must render."""
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/command")
    body = r.text
    assert "Phase ladder (0-8)" in body
    for phase_label in (
        "Selection / diagnostic plan",
        "Spec DRAFT",
        "Spec SEAL",
        "Runner",
        "Execution guard build report",
        "Operator execution preparation",
        "Operator QC",
        "Result sealing report",
        "Archival memo",
    ):
        assert phase_label in body, f"missing phase label: {phase_label}"


def test_command_route_renders_posture_invariants():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/command")
    body = r.text
    assert "Trading PAUSED" in body
    assert "BLOCKED_AT_6_GATES" in body
    assert "FRC NEVER_GRANTED" in body
    assert "no_strategy_optimization_authorized = True" in body


# --- read-only contract --------------------------------------------------

def test_command_route_html_has_no_form_or_post():
    """No <form>, no method="POST" — read-only HTML only."""
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/command")
    body_lower = r.text.lower()
    assert "<form" not in body_lower
    assert 'method="post"' not in body_lower
    assert "method='post'" not in body_lower


def test_command_route_405_on_non_get_verbs():
    """POST/PUT/PATCH/DELETE on /command must return 405 Method Not Allowed."""
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    for verb in ("post", "put", "patch", "delete"):
        method = getattr(client, verb)
        r = method("/command")
        assert r.status_code == 405, (
            f"{verb.upper()} /command returned {r.status_code}, expected 405"
        )


def test_command_route_does_not_write_to_reports():
    """Pre/post mtime + sha256 of a sample B006_002 artifact must be
    byte-identical after the request handler runs."""
    sample = (
        _REPO_ROOT
        / "reports"
        / "external_research_hunter"
        / "b006_002_archival_memo.md"
    )
    if not sample.exists():
        pytest.skip(f"sample artifact not on disk: {sample}")

    before_mtime = sample.stat().st_mtime_ns
    before_sha = hashlib.sha256(sample.read_bytes()).hexdigest()

    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/command")
    assert r.status_code == 200

    after_mtime = sample.stat().st_mtime_ns
    after_sha = hashlib.sha256(sample.read_bytes()).hexdigest()
    assert before_mtime == after_mtime, "sample artifact mtime changed"
    assert before_sha == after_sha, "sample artifact sha256 changed"


# --- fixture-backed flag tests -------------------------------------------

def _write_min_lifecycle(reports_dir: Path, lifecycle_id: str = "B006_900",
                        pin_matches: bool = True):
    """Create a minimal fixture lifecycle with a spec DRAFT + json sidecar.
    If pin_matches=False, the sidecar's artifact_sha256 is wrong on purpose
    (to trigger SEAL_DRIFT)."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    lid_lc = lifecycle_id.lower()
    md_path = reports_dir / f"{lid_lc}_spy_test_spec_DRAFT.md"
    json_path = reports_dir / f"{lid_lc}_spy_test_spec_DRAFT.json"
    md_body = b"# Fixture spec DRAFT\n\nfixture body for command-center tests.\n"
    md_path.write_bytes(md_body)
    real_md_sha = hashlib.sha256(md_body).hexdigest()
    if pin_matches:
        pin = real_md_sha
    else:
        # Same length / hex; deliberately different from the real md sha.
        pin = "0" * 64
    sidecar = {
        "candidate_description": "Fixture lifecycle for SPARTA Command Center v1 tests",
        "artifact_sha256": pin,
    }
    json_path.write_text(json.dumps(sidecar, indent=2), encoding="utf-8")
    return md_path, json_path


def test_command_route_flags_seal_drift(tmp_path, monkeypatch):
    """When a sidecar pins a sha that disagrees with the file body, the
    rendered row must contain the literal token SEAL_DRIFT."""
    fixture_dir = tmp_path / "external_research_hunter"
    _write_min_lifecycle(fixture_dir, "B006_900", pin_matches=False)

    import app as app_module
    monkeypatch.setattr(app_module, "_COMMAND_REPORTS_DIR", fixture_dir)
    # Decisions file: point at a non-existent path so next_authorize stays "".
    monkeypatch.setattr(
        app_module, "_COMMAND_DECISIONS_FILE", tmp_path / "no_decisions.md",
    )
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/command")
    assert r.status_code == 200
    body = r.text
    assert "B006_900" in body
    assert "SEAL_DRIFT" in body


def test_command_route_flags_ok_when_sidecar_pin_matches(tmp_path, monkeypatch):
    """Complement to SEAL_DRIFT: when the sidecar pin matches the file body,
    the row renders OK."""
    fixture_dir = tmp_path / "external_research_hunter"
    _write_min_lifecycle(fixture_dir, "B006_901", pin_matches=True)

    import app as app_module
    monkeypatch.setattr(app_module, "_COMMAND_REPORTS_DIR", fixture_dir)
    monkeypatch.setattr(
        app_module, "_COMMAND_DECISIONS_FILE", tmp_path / "no_decisions.md",
    )
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/command")
    assert r.status_code == 200
    body = r.text
    assert "B006_901" in body
    # The OK status must render at least once for the matched-pin artifact.
    assert "cc-status-OK" in body


def test_command_route_fails_closed_on_empty_dir(tmp_path, monkeypatch):
    """Empty (but existing) reports dir: page must render the MISSING
    empty-state message, NOT a fabricated row."""
    empty_dir = tmp_path / "external_research_hunter"
    empty_dir.mkdir()

    import app as app_module
    monkeypatch.setattr(app_module, "_COMMAND_REPORTS_DIR", empty_dir)
    monkeypatch.setattr(
        app_module, "_COMMAND_DECISIONS_FILE", tmp_path / "no_decisions.md",
    )
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/command")
    assert r.status_code == 200
    body = r.text
    assert "MISSING" in body
    assert "no B006_* lifecycle artifacts found on disk" in body


def test_command_route_fails_closed_on_missing_dir(tmp_path, monkeypatch):
    """Non-existent reports dir: page must render the directory-missing
    empty-state message."""
    missing_dir = tmp_path / "does_not_exist" / "external_research_hunter"
    assert not missing_dir.exists()

    import app as app_module
    monkeypatch.setattr(app_module, "_COMMAND_REPORTS_DIR", missing_dir)
    monkeypatch.setattr(
        app_module, "_COMMAND_DECISIONS_FILE", tmp_path / "no_decisions.md",
    )
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/command")
    assert r.status_code == 200
    body = r.text
    assert "MISSING" in body
    assert "directory not found" in body


# --- network-isolation safety ---------------------------------------------

def test_command_route_makes_no_external_network_call(monkeypatch):
    """Render /command with socket.create_connection patched to raise; the
    request must still succeed, proving no outbound network call happens."""
    def _refuse(*args, **kwargs):
        raise RuntimeError(
            "test_command_route_makes_no_external_network_call: "
            "socket.create_connection was called from /command handler"
        )
    monkeypatch.setattr(socket, "create_connection", _refuse)

    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/command")
    assert r.status_code == 200


# --- static scan: forbidden tokens in the /command block of app.py -------

def test_app_command_block_has_no_forbidden_tokens():
    """The /command block in app.py must contain no broker / execution /
    fetch / optimize / paper-trade tokens (plan §8)."""
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    # Block B in app.py is bounded by these two unique-to-Block-B markers.
    # The lifespan upsert comment uses different wording so it cannot match.
    start = src.find("# Hard contract for this entire block:")
    end = src.find("# === END SPARTA Trading Command Center")
    assert start != -1, "command-center block header not found in app.py"
    assert end != -1, "command-center block footer not found in app.py"
    block = src[start:end]
    # Strip line comments so the contract prose ("No fetch. No optimize.")
    # in the block header doesn't trip the substring scan.
    code_only = re.sub(r"(?m)#.*$", "", block).lower()
    forbidden = (
        "place_order", "submit_order", "send_order", "route_order",
        "execute_order", "execute_trade", "place_trade",
        "open_position", "close_position", "modify_position",
        "send_telegram", "notify_telegram", "post_to_webhook",
        "import broker", "from broker",
        "import databento", "from databento",
        "requests.post", "requests.put", "urllib.request",
        "subprocess.run", "subprocess.popen", "os.system",
        ".write_text(", ".write_bytes(", "shutil.copy", "shutil.move",
    )
    for tok in forbidden:
        assert tok not in code_only, f"forbidden token in /command block: {tok}"


def test_app_command_block_route_is_get_only():
    """The /command block must declare exactly one route, and it must be GET."""
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    # Block B in app.py is bounded by these two unique-to-Block-B markers.
    # The lifespan upsert comment uses different wording so it cannot match.
    start = src.find("# Hard contract for this entire block:")
    end = src.find("# === END SPARTA Trading Command Center")
    block = src[start:end]
    # Strip line comments so the rollback note ("comment out the
    # @app.get(...) decorator below") doesn't trip the count.
    code_only = re.sub(r"(?m)#.*$", "", block)
    # Must have exactly one @app.get and zero @app.post/put/patch/delete.
    assert code_only.count('@app.get("/command"') == 1
    assert code_only.count("@app.post") == 0
    assert code_only.count("@app.put") == 0
    assert code_only.count("@app.patch") == 0
    assert code_only.count("@app.delete") == 0


def test_app_command_block_template_has_no_form_or_input():
    """The command.html template must contain no <form>, <input>, or
    mutating button affordance (plan §8)."""
    tpl = (_REPO_ROOT / "templates" / "command.html").read_text(encoding="utf-8")
    lower = tpl.lower()
    assert "<form" not in lower
    assert "<input" not in lower
    assert "<textarea" not in lower
    # We allow <button> only if it has no mutating handler. v1 template has
    # zero <button> elements; assert that too.
    assert "<button" not in lower
    # No fetch/POST in any inline JS (the template should have no JS at all).
    assert "fetch(" not in lower
    assert "xmlhttprequest" not in lower
    assert "method:\"post\"" not in lower
    assert "method: 'post'" not in lower
