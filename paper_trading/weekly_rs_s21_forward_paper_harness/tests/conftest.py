import pathlib, sys
import pytest


@pytest.fixture(autouse=True)
def _env_guards(monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "invalid"); monkeypatch.setenv("HTTPS_PROXY", "invalid")
    monkeypatch.delenv("TIINGO_API_KEY", raising=False)
    yield


@pytest.fixture
def harness():
    p = pathlib.Path(__file__).resolve()
    repo_root = next(par for par in p.parents if (par / "paper_trading").is_dir())
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    import importlib
    base = "paper_trading.weekly_rs_s21_forward_paper_harness."
    return {m: importlib.import_module(base + m) for m in
            ("manifest", "safety", "signal", "portfolio", "paper_book", "paper_logging", "killswitch", "report", "cycle")}


@pytest.fixture
def synthetic_prices():
    n = 320
    rates = {"A": 0.0012, "B": 0.0010, "C": 0.0008, "D": 0.0006, "E": 0.0004, "F": 0.0002, "G": 0.0000, "H": -0.0002, "I": -0.0004, "J": -0.0006}
    out = {}
    for s, r in rates.items():
        px = 100.0; ser = []
        for _ in range(n):
            ser.append(round(px, 6)); px *= (1.0 + r)
        out[s] = ser
    return out
