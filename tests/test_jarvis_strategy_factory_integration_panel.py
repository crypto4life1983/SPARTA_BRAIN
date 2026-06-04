"""JARVIS Strategy Factory Dynamic Feed Panel v1 — read-only preview tests.

Covers the additive ``/api/jarvis/status`` key ``strategy_factory_integration``
and its backend reader ``_jarvis_strategy_factory_integration``, which surfaces
the committed research-only integration bundle artifacts:

- anchor ``reports/strategy_factory_integration_v1_build/dashboard_feed_preview.json``
- sibling ``report.json`` (decision memo verdict + next action)
- sibling ``registry_update_proposal.json`` (proposal status)

Invariants enforced:
- the status aggregate exposes ``strategy_factory_integration`` and stays
  read-only,
- the reader fails closed on a missing / corrupt / non-object preview
  (never raises, never writes),
- ``preview_only`` is ALWAYS True and ``applied_to_dashboard`` ALWAYS False in
  the response, regardless of disk state,
- any ACTIVE/STRONG/PASS verdict is clamped to WATCH with a warning,
- an artifact claiming it was applied / written / mutated is an anomaly
  (pinned safe + commander_color RED), never trusted,
- a present preview with a missing sibling still renders safely
  (UNKNOWN fields, no crash),
- the dashboard template carries the panel + preview-only / non-authorization
  wording and adds no execution / broker / order control.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

import app as app_module  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DANGER_FLAGS = app_module._JARVIS_SFI_DANGER_FLAGS

# All temp artifacts live under one disposable root inside the gitignored
# storage/ tree. An autouse fixture wipes it around every test so nothing
# leaks into the repo or between tests.
_TEST_ROOT = app_module.BASE / "storage" / "jarvis" / "__sfi_panel_test__"

# Fixed basenames the reader derives from the chosen build folder. v2 selects a
# build FOLDER (discovered or fixed fallback); it never reads loose paths.
_PREVIEW_NAME = "dashboard_feed_preview.json"
_REPORT_NAME = "report.json"
_PROPOSAL_NAME = "registry_update_proposal.json"


@pytest.fixture(autouse=True)
def _clean_test_root():
    shutil.rmtree(_TEST_ROOT, ignore_errors=True)
    _TEST_ROOT.mkdir(parents=True, exist_ok=True)
    yield
    shutil.rmtree(_TEST_ROOT, ignore_errors=True)


# --- temp-artifact helpers -------------------------------------------------

def _rel(path):
    return str(Path(path).relative_to(app_module.BASE)).replace("\\", "/")


def _unique_dir(prefix):
    return Path(tempfile.mkdtemp(prefix=prefix, dir=_TEST_ROOT))


def _dump(payload):
    return payload if isinstance(payload, str) else json.dumps(payload or {})


def _write_build(dirpath, *, preview=None, report=None, proposal=None,
                 write_preview=True, write_report=True, write_proposal=True):
    """Write the fixed-basename artifacts into a build folder. Anything not
    written is simply absent, so the reader sees that sibling as missing."""
    dirpath = Path(dirpath)
    dirpath.mkdir(parents=True, exist_ok=True)
    if write_preview:
        (dirpath / _PREVIEW_NAME).write_text(_dump(preview), encoding="utf-8")
    if write_report:
        (dirpath / _REPORT_NAME).write_text(_dump(report), encoding="utf-8")
    if write_proposal:
        (dirpath / _PROPOSAL_NAME).write_text(_dump(proposal), encoding="utf-8")
    return dirpath


def _point(monkeypatch, *, preview=None, report=None, proposal=None,
           write_preview=True, write_report=True, write_proposal=True):
    """Fixed-fallback setup: write artifacts into a temp build folder, aim the
    fixed-fallback constant ``_JARVIS_SFI_DIR_REL`` at it, and point the
    discovery root at an isolated EMPTY dir so discovery returns ``None`` and
    the reader falls back to that folder. Returns the build dir."""
    build = _write_build(_unique_dir("build_"),
                         preview=preview, report=report, proposal=proposal,
                         write_preview=write_preview,
                         write_report=write_report,
                         write_proposal=write_proposal)
    empty_root = _unique_dir("emptyroot_")
    monkeypatch.setattr(app_module, "_JARVIS_SFI_DIR_REL", _rel(build))
    monkeypatch.setattr(app_module, "_JARVIS_SFI_REPORTS_ROOT_REL",
                        _rel(empty_root))
    return build


def _setup_discovery(monkeypatch, *, fallback_present=False):
    """Aim discovery at a fresh empty reports root and the fixed fallback at a
    separate temp folder (empty unless ``fallback_present``). Returns
    ``(root, fallback_dir)``. Build folders are added under ``root`` per test."""
    root = _unique_dir("reports_")
    fb = _unique_dir("fallback_")
    if fallback_present:
        _write_build(
            fb,
            preview=_good_preview(entry={"module_name": "fixed_fallback_v1",
                                         "status": "WATCH"}),
            report=_good_report(), proposal=_good_proposal())
    monkeypatch.setattr(app_module, "_JARVIS_SFI_REPORTS_ROOT_REL", _rel(root))
    monkeypatch.setattr(app_module, "_JARVIS_SFI_DIR_REL", _rel(fb))
    return root, fb


def _build_name(token):
    return f"strategy_factory_integration_{token}_build"


def _good_preview(**over):
    pv = {
        "layer": "strategy_factory_integration_v1",
        "entry": {"module_name": "strategy_factory_integration_v1",
                  "status": "WATCH / research-only dry-run"},
        "preview_only": True,
        "applied_to_dashboard": False,
        "dashboard_write_performed": False,
        "non_authorization_statement":
            "Research-only synthetic dry-run; authorizes no paper/live/broker/"
            "exchange/order/fetch and promotes nothing above WATCH.",
        "safety_flags": {f: False for f in _DANGER_FLAGS},
    }
    pv.update(over)
    return pv


def _good_report(**over):
    rep = {
        "verdict_ceiling": "WATCH",
        "decision_memo": {"verdict": "WATCH"},
        "next_action": "Operator review of the dry-run decision memo.",
    }
    rep.update(over)
    return rep


def _good_proposal(**over):
    prop = {
        "proposal_only": True,
        "applied": False,
        "registry_mutation_performed": False,
        "proposed_candidate": {"status": "WATCH"},
    }
    prop.update(over)
    return prop


# --- status wiring ---------------------------------------------------------

def test_status_exposes_strategy_factory_integration():
    status = app_module.api_jarvis_status()
    assert "strategy_factory_integration" in status
    sfi = status["strategy_factory_integration"]
    assert isinstance(sfi, dict)
    assert sfi["read_only"] is True
    assert sfi["preview_only"] is True
    assert sfi["applied_to_dashboard"] is False
    assert sfi["verdict_ceiling"] == "WATCH"


# --- fail-closed reader ----------------------------------------------------

def test_missing_preview_fails_closed(monkeypatch):
    _point(monkeypatch, write_preview=False)
    out = app_module._jarvis_strategy_factory_integration()
    assert out["state"] == "missing"
    assert out["read_only"] is True
    assert out["preview_only"] is True
    assert out["applied_to_dashboard"] is False
    assert out["latest_verdict"] == "UNKNOWN"
    assert out["registry_proposal_status"] == "UNKNOWN"
    assert out["safety_anomaly"] is False


def test_corrupt_preview_fails_closed(monkeypatch):
    _point(monkeypatch, preview="{ not valid json ")
    out = app_module._jarvis_strategy_factory_integration()
    assert out["state"] == "invalid"
    assert out["preview_only"] is True
    assert out["applied_to_dashboard"] is False
    assert "detail" in out


def test_non_object_preview_fails_closed(monkeypatch):
    _point(monkeypatch, preview=json.dumps([1, 2, 3]))
    out = app_module._jarvis_strategy_factory_integration()
    assert out["state"] == "invalid"
    assert out["preview_only"] is True
    assert out["applied_to_dashboard"] is False


# --- valid surface ---------------------------------------------------------

def test_valid_preview_surfaces_fields(monkeypatch):
    _point(monkeypatch, preview=_good_preview(),
           report=_good_report(), proposal=_good_proposal())
    out = app_module._jarvis_strategy_factory_integration()
    assert out["state"] == "ready"
    assert out["bundle"] == "strategy_factory_integration_v1"
    assert out["preview_only"] is True
    assert out["applied_to_dashboard"] is False
    assert out["verdict_ceiling"] == "WATCH"
    assert out["latest_verdict"] == "WATCH"
    assert out["registry_proposal_status"] == "WATCH"
    assert out["registry_proposal_applied"] is False
    assert out["next_action"] == "Operator review of the dry-run decision memo."
    assert isinstance(out["non_authorization_statement"], str)
    assert out["safety_anomaly"] is False
    assert out["commander_color"] == "GREEN"
    locks = out["safety_locks"]
    assert locks["research_only"] is True
    for flag in _DANGER_FLAGS:
        assert locks[flag] is False


# --- verdict clamp ---------------------------------------------------------

@pytest.mark.parametrize("forbidden", ["ACTIVE", "STRONG", "PASS"])
def test_forbidden_report_verdict_clamped_to_watch(monkeypatch, forbidden):
    _point(monkeypatch, preview=_good_preview(),
           report=_good_report(decision_memo={"verdict": forbidden}),
           proposal=_good_proposal())
    out = app_module._jarvis_strategy_factory_integration()
    assert out["latest_verdict"] == "WATCH"
    assert any("forbidden" in w.lower() for w in out["warnings"])


@pytest.mark.parametrize("forbidden", ["ACTIVE", "STRONG", "PASS"])
def test_forbidden_proposal_status_clamped_to_watch(monkeypatch, forbidden):
    _point(monkeypatch, preview=_good_preview(), report=_good_report(),
           proposal=_good_proposal(
               proposed_candidate={"status": forbidden}))
    out = app_module._jarvis_strategy_factory_integration()
    assert out["registry_proposal_status"] == "WATCH"


def test_forbidden_token_in_preview_status_is_clamped(monkeypatch):
    _point(monkeypatch,
           preview=_good_preview(entry={"module_name": "x",
                                         "status": "ACTIVE now"}),
           report=_good_report(), proposal=_good_proposal())
    out = app_module._jarvis_strategy_factory_integration()
    assert "ACTIVE" not in out["status"].upper().replace("RESEARCH", "")
    assert out["status"] == "WATCH / research-only (clamped)"
    assert any("forbidden verdict" in w.lower() for w in out["warnings"])


# --- anomaly pinning -------------------------------------------------------

@pytest.mark.parametrize("claim", [
    {"applied_to_dashboard": True},
    {"dashboard_write_performed": True},
    {"preview_only": False},
])
def test_preview_applied_claim_is_anomaly(monkeypatch, claim):
    _point(monkeypatch, preview=_good_preview(**claim),
           report=_good_report(), proposal=_good_proposal())
    out = app_module._jarvis_strategy_factory_integration()
    assert out["safety_anomaly"] is True
    assert out["commander_color"] == "RED"
    assert out["preview_only"] is True
    assert out["applied_to_dashboard"] is False


@pytest.mark.parametrize("bad_flag", _DANGER_FLAGS)
def test_true_danger_flag_on_disk_is_anomaly(monkeypatch, bad_flag):
    flags = {f: False for f in _DANGER_FLAGS}
    flags[bad_flag] = True
    _point(monkeypatch, preview=_good_preview(safety_flags=flags),
           report=_good_report(), proposal=_good_proposal())
    out = app_module._jarvis_strategy_factory_integration()
    assert out["safety_anomaly"] is True
    assert out["commander_color"] == "RED"
    assert out["safety_locks"][bad_flag] is False


@pytest.mark.parametrize("claim", [
    {"applied": True},
    {"proposal_only": False},
    {"registry_mutation_performed": True},
])
def test_proposal_applied_claim_is_anomaly(monkeypatch, claim):
    _point(monkeypatch, preview=_good_preview(), report=_good_report(),
           proposal=_good_proposal(**claim))
    out = app_module._jarvis_strategy_factory_integration()
    assert out["safety_anomaly"] is True
    assert out["commander_color"] == "RED"
    assert out["registry_proposal_applied"] is False


# --- sibling-missing graceful render ---------------------------------------

def test_preview_present_siblings_missing_renders_safe(monkeypatch):
    _point(monkeypatch, preview=_good_preview(),
           write_report=False, write_proposal=False)
    out = app_module._jarvis_strategy_factory_integration()
    assert out["state"] == "ready"
    assert out["latest_verdict"] == "UNKNOWN"
    assert out["next_action"] is None
    assert out["registry_proposal_status"] == "UNKNOWN"
    assert out["safety_anomaly"] is False
    assert any("report.json" in w for w in out["warnings"])
    assert any("registry_update_proposal.json" in w for w in out["warnings"])


# --- reader writes nothing -------------------------------------------------

def test_reader_performs_no_write(monkeypatch):
    d = _point(monkeypatch, preview=_good_preview(),
               report=_good_report(), proposal=_good_proposal())
    before = {p.name: p.read_bytes() for p in d.iterdir() if p.is_file()}
    names_before = set(before)
    app_module._jarvis_strategy_factory_integration()
    after = {p.name: p.read_bytes() for p in d.iterdir() if p.is_file()}
    assert set(after) == names_before  # no new file created
    for name, data in before.items():
        assert after[name] == data  # no existing file mutated


# --- template: panel present, wording, no controls -------------------------

def test_template_has_integration_panel():
    body = (_REPO_ROOT / "templates" / "jarvis.html").read_text(
        encoding="utf-8")
    assert "pStrategyFactoryIntegration" in body
    assert "strategy_factory_integration" in body
    assert "Strategy Factory Integration Feed" in body


def test_template_has_preview_and_non_authorization_wording():
    low = (_REPO_ROOT / "templates" / "jarvis.html").read_text(
        encoding="utf-8").lower()
    assert "preview only" in low
    assert "non-authorization" in low
    assert "not applied to dashboard" in low
    assert "no registry mutation" in low


def test_template_stays_control_free():
    low = (_REPO_ROOT / "templates" / "jarvis.html").read_text(
        encoding="utf-8").lower()
    for tok in ("<button", "<form", "onclick", 'method="post"',
                "/api/jarvis/refresh", "/api/jarvis/apply"):
        assert tok not in low


# --- v2 latest-artifact discovery ------------------------------------------

def test_discovery_picks_highest_version(monkeypatch):
    root, _ = _setup_discovery(monkeypatch)
    _write_build(root / _build_name("v1"), preview=_good_preview(),
                 report=_good_report(), proposal=_good_proposal())
    _write_build(root / _build_name("v2"), preview=_good_preview(),
                 report=_good_report(), proposal=_good_proposal())
    out = app_module._jarvis_strategy_factory_integration()
    assert out["state"] == "ready"
    assert out["source_selection"] == "latest_discovered"
    assert out["source_dir"].endswith(_build_name("v2"))


def test_discovery_mtime_breaks_tie_over_name(monkeypatch):
    # Same (absent) version -> mtime is the tiebreak BEFORE lexical name. The
    # lexically-smaller name carries the NEWER mtime; it must still win, proving
    # mtime outranks the name key.
    root, _ = _setup_discovery(monkeypatch)
    older = _write_build(root / _build_name("zzz"), preview=_good_preview(),
                         report=_good_report(), proposal=_good_proposal())
    newer = _write_build(root / _build_name("aaa"), preview=_good_preview(),
                         report=_good_report(), proposal=_good_proposal())
    os.utime(older / _PREVIEW_NAME, (1_000_000, 1_000_000))
    os.utime(newer / _PREVIEW_NAME, (2_000_000, 2_000_000))
    out = app_module._jarvis_strategy_factory_integration()
    assert out["source_selection"] == "latest_discovered"
    assert out["source_dir"].endswith(_build_name("aaa"))


def test_discovery_ignores_unsafe_folder_names(monkeypatch):
    # A higher-"version" folder whose name fails the allowlist (uppercase, no
    # _build suffix) must be ignored even though it sorts higher numerically.
    root, _ = _setup_discovery(monkeypatch)
    _write_build(root / _build_name("v1"), preview=_good_preview(),
                 report=_good_report(), proposal=_good_proposal())
    _write_build(root / "strategy_factory_integration_v9_NOPE",
                 preview=_good_preview(), report=_good_report(),
                 proposal=_good_proposal())
    _write_build(root / "random_other_folder", preview=_good_preview())
    out = app_module._jarvis_strategy_factory_integration()
    assert out["source_selection"] == "latest_discovered"
    assert out["source_dir"].endswith(_build_name("v1"))


def test_discovery_skips_corrupt_and_anchorless_folders(monkeypatch):
    # A higher-version folder with a corrupt anchor, and another with NO anchor
    # at all, are both skipped; the valid lower-version folder wins.
    root, _ = _setup_discovery(monkeypatch)
    _write_build(root / _build_name("v3"), preview="{ not json ")
    # v2: a real folder but no anchor file present at all.
    (root / _build_name("v2")).mkdir(parents=True, exist_ok=True)
    _write_build(root / _build_name("v1"), preview=_good_preview(),
                 report=_good_report(), proposal=_good_proposal())
    out = app_module._jarvis_strategy_factory_integration()
    assert out["source_selection"] == "latest_discovered"
    assert out["source_dir"].endswith(_build_name("v1"))


def test_discovery_does_not_recurse(monkeypatch):
    # A valid higher-version folder nested one level down must NOT be found;
    # only the top-level folder is selected.
    root, _ = _setup_discovery(monkeypatch)
    _write_build(root / _build_name("v1"), preview=_good_preview(),
                 report=_good_report(), proposal=_good_proposal())
    _write_build(root / "sub" / _build_name("v9"), preview=_good_preview(),
                 report=_good_report(), proposal=_good_proposal())
    out = app_module._jarvis_strategy_factory_integration()
    assert out["source_selection"] == "latest_discovered"
    assert out["source_dir"].endswith(_build_name("v1"))


def test_discovery_falls_back_to_fixed_when_root_empty(monkeypatch):
    _setup_discovery(monkeypatch, fallback_present=True)
    out = app_module._jarvis_strategy_factory_integration()
    assert out["state"] == "ready"
    assert out["source_selection"] == "fixed_fallback"
    assert out["bundle"] == "fixed_fallback_v1"


def test_discovery_missing_everywhere_fails_closed(monkeypatch):
    # Empty root AND empty fallback folder -> the preview anchor is missing in
    # the fallback, so the reader fails closed with safe defaults.
    _setup_discovery(monkeypatch, fallback_present=False)
    out = app_module._jarvis_strategy_factory_integration()
    assert out["state"] == "missing"
    assert out["source_selection"] == "fixed_fallback"
    assert out["preview_only"] is True
    assert out["applied_to_dashboard"] is False
    assert out["safety_anomaly"] is False


def test_discovery_symlink_escape_ignored(monkeypatch, tmp_path):
    # A build-named symlink that points OUTSIDE reports/ must never be selected.
    # On Windows symlink creation often needs privilege; skip cleanly if so.
    root, _ = _setup_discovery(monkeypatch)
    outside = tmp_path / "outside_build"
    _write_build(outside, preview=_good_preview(entry={
        "module_name": "evil_escaped_v9", "status": "WATCH"}),
        report=_good_report(), proposal=_good_proposal())
    link = root / _build_name("v9")
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted on this platform")
    _write_build(root / _build_name("v1"), preview=_good_preview(),
                 report=_good_report(), proposal=_good_proposal())
    out = app_module._jarvis_strategy_factory_integration()
    assert out["source_selection"] == "latest_discovered"
    assert out["source_dir"].endswith(_build_name("v1"))
    assert out["bundle"] != "evil_escaped_v9"


def test_discovered_forbidden_verdict_still_clamps(monkeypatch):
    root, _ = _setup_discovery(monkeypatch)
    _write_build(root / _build_name("v2"), preview=_good_preview(),
                 report=_good_report(decision_memo={"verdict": "ACTIVE"}),
                 proposal=_good_proposal())
    out = app_module._jarvis_strategy_factory_integration()
    assert out["source_selection"] == "latest_discovered"
    assert out["latest_verdict"] == "WATCH"
    assert any("forbidden" in w.lower() for w in out["warnings"])


def test_discovery_reader_writes_nothing_and_no_lock(monkeypatch):
    root, _ = _setup_discovery(monkeypatch)
    build = _write_build(root / _build_name("v1"), preview=_good_preview(),
                         report=_good_report(), proposal=_good_proposal())
    lock_path = app_module.BASE / "storage" / "locks" / "sparta_writer.lock.json"
    lock_before = lock_path.read_bytes() if lock_path.exists() else None

    def _snapshot():
        return {p: p.read_bytes() for p in _TEST_ROOT.rglob("*") if p.is_file()}

    before = _snapshot()
    app_module._jarvis_strategy_factory_integration()
    after = _snapshot()
    assert set(after) == set(before)
    for p, data in before.items():
        assert after[p] == data
    # the reader must not have created or mutated the writer lock
    lock_after = lock_path.read_bytes() if lock_path.exists() else None
    assert lock_after == lock_before
    # and it created no anchor folder of its own under the discovery root
    assert build.exists()


def test_api_status_surfaces_source_fields():
    sfi = app_module.api_jarvis_status()["strategy_factory_integration"]
    assert "source_dir" in sfi
    assert "source_selection" in sfi
    assert sfi["source_selection"] in (
        "latest_discovered", "fixed_fallback", "none")


def test_template_has_reading_row():
    body = (_REPO_ROOT / "templates" / "jarvis.html").read_text(
        encoding="utf-8")
    assert "'Reading'" in body
    assert "source_dir" in body
    assert "source_selection" in body
