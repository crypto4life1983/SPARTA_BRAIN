"""Tests for the Candidate #22 Signum GC export/save automation feasibility PROPOSAL.

Proves the proposal is PROPOSAL-ONLY and SAFE: it compares all three options (official
export/API, browser/UI automation, semi-auto reminder + manual download); recommends the
semi-auto option for adoption now (credential-free, no browser, safest), marks the official
option as a read-only human-gated follow-up, and rejects browser automation; implements
nothing; performs no Signum login / fetch / browser automation / API / MCP / network; stores
no credentials/cookies/tokens/passwords/session files; preserves C22
HOLD_FOR_MORE_FROZEN_DATA_WINDOWS with replay locked; and the module source contains no live
login/fetch/browser/network call tokens."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.c22_signum_gc_export_save_automation_feasibility_proposal_contract as fp  # noqa: E501

_P = fp.build_feasibility_proposal()
_OPTS = {o["id"]: o for o in _P["options"]}


# ---- proposal builds + validates -------------------------------------------

def test_proposal_builds_and_validates():
    assert _P["mode"] == "RESEARCH_ONLY"
    assert _P["is_proposal_only"] is True
    assert _P["implements_nothing"] is True
    assert _P["verdict"] == (
        "C22_EXPORT_SAVE_AUTOMATION_FEASIBILITY_PROPOSAL_READY_FOR_REVIEW")
    assert fp.validate_feasibility_proposal(_P)["valid"] is True


# ---- all three options compared --------------------------------------------

def test_three_options_compared():
    assert set(_OPTS) == {"official_export_or_api", "browser_ui_automation",
                          "semi_auto_reminder_manual_download"}
    for o in _OPTS.values():
        for axis in ("requires_credentials", "needs_browser_automation",
                     "tos_or_account_risk", "brittleness", "safety_rank",
                     "recommendation_role", "pros", "cons"):
            assert axis in o, (o["id"], axis)


# ---- recommendation: adopt semi-auto, investigate official, reject browser --

def test_recommendation_semi_auto_now():
    assert _P["recommended_primary"] == "semi_auto_reminder_manual_download"
    sa = _OPTS["semi_auto_reminder_manual_download"]
    assert sa["recommendation_role"] == "adopt_now"
    assert sa["requires_credentials"] is False
    assert sa["needs_browser_automation"] is False
    assert sa["safety_rank"] == 1


def test_official_is_read_only_human_gated_followup():
    assert _P["investigate_next"] == "official_export_or_api"
    assert _P["investigate_next_is_read_only_human_gated"] is True
    off = _OPTS["official_export_or_api"]
    assert off["recommendation_role"] == "investigate_next_read_only_human_gated"
    assert off["availability_unknown_must_verify_read_only"] is True


def test_browser_automation_not_recommended():
    assert _P["not_recommended"] == "browser_ui_automation"
    br = _OPTS["browser_ui_automation"]
    assert br["recommendation_role"] == "not_recommended"
    assert br["needs_browser_automation"] is True
    assert br["tos_or_account_risk"] == "high"
    assert br["safety_rank"] == 3


# ---- proposal implements / accesses / stores nothing -----------------------

def test_no_implementation_no_live_access_no_credentials():
    for flag in ("implements_export_automation", "performs_signum_login", "fetches_data",
                 "performs_network_io", "performs_browser_automation", "calls_api",
                 "uses_mcp", "opens_browser", "stores_credentials", "stores_cookies",
                 "stores_tokens", "stores_passwords", "stores_session_files",
                 "uses_api_keys", "connects_signum"):
        assert _P[flag] is False, flag
    for flag in fp._CAPABILITY_FLAGS_FALSE:
        assert _P[flag] is False, flag
        assert fp.validate_feasibility_proposal({**_P, flag: True})["valid"] is False
    for key, val in _P["scope_locks"].items():
        assert val is True, key


# ---- C22 state preserved ---------------------------------------------------

def test_c22_state_preserved():
    assert _P["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert _P["replay_locked"] is True
    assert _P["advances_nothing"] is True
    assert _P["next_required_action"] == (
        "HUMAN_DECISION_C22_EXPORT_SAVE_AUTOMATION_METHOD_OR_HOLD")


# ---- anti-tamper: cannot flip the recommendation to browser/official --------

def test_tamper_recommendation_rejected():
    bad = {**_P, "recommended_primary": "browser_ui_automation"}
    assert fp.validate_feasibility_proposal(bad)["valid"] is False


# ---- module purity + no live login/fetch/browser/network tokens ------------

def test_module_purity_no_live_access_tokens():
    src = Path(fp.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "requests.", "httpx",
                 "selenium", "playwright", "webdriver", "get_trendradar",
                 "socket.connect", ".login(", "json.load"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "json", "hashlib", "pathlib", "numpy", "pandas", "selenium",
              "playwright"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
