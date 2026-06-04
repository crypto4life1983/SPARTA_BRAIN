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
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

import app as app_module  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DANGER_FLAGS = app_module._JARVIS_SFI_DANGER_FLAGS


# --- temp-artifact helpers -------------------------------------------------

def _tmp_dir():
    d = app_module.BASE / "storage" / "jarvis" / "__sfi_panel_test__"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _rel(path):
    return str(path.relative_to(app_module.BASE)).replace("\\", "/")


def _point(monkeypatch, *, preview=None, report=None, proposal=None,
           write_preview=True, write_report=True, write_proposal=True):
    """Write the requested artifacts to a temp dir and repoint the reader's
    rel-path constants at them. Anything not written is repointed at a
    guaranteed-missing path so the reader sees state 'missing'."""
    d = _tmp_dir()
    missing = d / "__never_exists__.json"

    def _set(attr, payload, do_write, name):
        if do_write:
            p = d / name
            p.write_text(payload, encoding="utf-8")
            monkeypatch.setattr(app_module, attr, _rel(p))
        else:
            monkeypatch.setattr(app_module, attr, _rel(missing))

    _set("_JARVIS_SFI_PREVIEW_REL",
         preview if isinstance(preview, str) else json.dumps(preview or {}),
         write_preview, "preview.json")
    _set("_JARVIS_SFI_REPORT_REL",
         report if isinstance(report, str) else json.dumps(report or {}),
         write_report, "report.json")
    _set("_JARVIS_SFI_PROPOSAL_REL",
         proposal if isinstance(proposal, str) else json.dumps(proposal or {}),
         write_proposal, "proposal.json")
    return d


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
