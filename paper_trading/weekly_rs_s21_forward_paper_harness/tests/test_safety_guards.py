import re, pathlib
import pytest


def test_broker_live_fetch_frc_refusals(harness):
    s = harness["safety"]
    for fn in (s.connect_broker, s.place_live_order, s.paper_trade_via_broker, s.submit_to_strategy_lab, s.request_frc, s.fetch_market_data):
        with pytest.raises(s.SafetyViolation):
            fn()


def test_assert_safe_environment(harness):
    s = harness["safety"]
    assert s.assert_safe_environment(live_mode=False, broker=None) is True
    with pytest.raises(s.SafetyViolation):
        s.assert_safe_environment(live_mode=True)
    with pytest.raises(s.SafetyViolation):
        s.assert_safe_environment(broker=object())


def test_no_api_key_access(harness):
    s = harness["safety"]
    assert s.assert_no_api_key_access({"PATH": "x"}) is True
    with pytest.raises(s.SafetyViolation):
        s.assert_no_api_key_access({"TIINGO_API_KEY": "x"})


def test_cycle_refuses_without_authorization(harness):
    c = harness["cycle"]
    with pytest.raises(c.CycleNotAuthorized):
        c.run_weekly_paper_cycle("/nonexistent", 200, operator_authorized_dry_run=False)


def test_source_has_no_network_or_key_access(harness):
    pkgdir = pathlib.Path(harness["manifest"].__file__).resolve().parent
    forbidden = ["import requests", "from requests", "import urllib", "import socket", "import http", "from http", "import tiingo", "from tiingo", "os.environ", "getenv", "urlopen", "boto3", "requests.get", "requests.post"]
    for py in pkgdir.glob("*.py"):
        src = py.read_text(encoding="utf-8")
        for tok in forbidden:
            assert tok not in src, "forbidden token %r in %s" % (tok, py.name)
