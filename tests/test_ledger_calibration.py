"""tools/ledger_calibration.py: accrual math, the never-at-current-rate case, in-sample sign
mapping / agreement, and no forbidden words in the rendered markdown."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import ledger_calibration as lc  # noqa: E402
from tools.trade_hypothesis_ledger import forbidden_words_found  # noqa: E402


def _hyp(sid, kind, registered, status="SHADOW", n=0, mean=None, evidence=None, history=None, applied=None):
    h = dict(id=sid, kind=kind, status=status, registered_as_of=registered,
             registered_evidence=evidence or {}, rule=f"rule {sid}", params={},
             forward=dict(n_signals=n, delta_R_mean=mean, delta_R_sum=None, bootstrap_p_positive=None),
             history=history or [dict(as_of=registered, status="SHADOW", note="registered")])
    if applied:
        h["applied"] = applied
    return h


def _ledger(*hyps):
    return {"hypotheses": {h["id"]: h for h in hyps}}


def test_accrual_rate_and_projection_math():
    h = _hyp("a", "unblock", "2026-09-20", n=6, mean=0.1, evidence={"mean_hyp_R": 0.5})
    rep = lc.build(_ledger(h), [], "2026-10-20", None)
    r = rep["rows"][0]
    assert r["days_since_registration"] == 30
    assert r["accrual_per_30d"] == 6.0                       # 6 signals in 30 days
    assert r["projected_days_to_floor"] == "70"              # (20-6)/6*30 = 70
    assert lc.projected_days_to_floor(25, 3.0) == "reached"


def test_never_at_current_rate_is_named_in_totals():
    h = _hyp("stuck", "block_where", "2026-09-23", n=0, evidence={"short_mean_R": -0.02})
    rep = lc.build(_ledger(h), [], "2026-10-20", None)
    assert rep["rows"][0]["projected_days_to_floor"] == "never at current rate"
    assert rep["totals"]["never_reach_floor_at_current_rate"] == ["stuck"]
    assert rep["totals"]["share_with_forward_evidence"] == 0.0


def test_in_sample_sign_mapping_and_agreement():
    block = _hyp("b", "block", "2026-09-11", n=3, mean=0.2, evidence={"avg_R": -0.3})      # -avg_R = + ; fwd + -> agree
    dshort = _hyp("d", "block_where", "2026-09-23", n=2, mean=-0.4, evidence={"short_mean_R": -0.02})  # + vs - -> disagree
    cap = _hyp("c", "stop_cap", "2026-09-11", n=0, evidence={"total_excess_loss_R": 6.0})     # no forward data
    ext = _hyp("e", "extend_timeout", "2026-10-10", n=1, mean=-1.0, evidence={"n_resolved": 0, "sum_delta_R": 0.0})
    p2 = _hyp("p", "partial_2R", "2026-09-11", n=2, mean=0.3, evidence={"mean_MFE_R": 3.0, "mean_realized_R": 1.8})
    rep = lc.build(_ledger(block, dshort, cap, ext, p2), [], "2026-10-20", None)
    rows = {r["id"]: r for r in rep["rows"]}
    assert rows["b"]["in_sample_sign"] == "+" and rows["b"]["sign_agreement"] == "agree"
    assert rows["d"]["in_sample_sign"] == "+" and rows["d"]["sign_agreement"] == "disagree"
    assert rows["c"]["in_sample_sign"] == "+" and rows["c"]["sign_agreement"] == "no forward data"
    assert rows["e"]["in_sample_sign"] is None and rows["e"]["sign_agreement"] == "no in-sample sign"
    assert rows["p"]["in_sample_sign"] == "+" and rows["p"]["in_sample_sign_source"] == "mean_MFE_R - mean_realized_R"
    assert rep["totals"]["sign_agreement_counts"]["agree"] == 2
    assert rep["totals"]["sign_agreement_counts"]["disagree"] == 1


def test_days_to_verdict_priors_and_no_forbidden_words(tmp_path):
    applied = _hyp("ap", "block", "2026-09-11", status="APPLIED", n=0, evidence={"avg_R": -0.3},
                   history=[dict(as_of="2026-09-11", status="SHADOW"), dict(as_of="2026-09-15", status="APPLIED")],
                   applied=dict(applied_as_of="2026-09-15", n_after=12, mean_R_after=-0.55, regression_flag=False))
    rej = _hyp("rj", "unblock", "2026-09-01", n=20, mean=-0.5, evidence={"mean_hyp_R": -0.1})
    hist = [dict(as_of="2026-10-01", status_changes=[dict(id="rj", to="REJECTED")])]
    priors = {"ap": {"prior_delta_R_mean": 0.12, "stable": True}}
    rep = lc.build(_ledger(applied, rej), hist, "2026-10-20", priors)
    rows = {r["id"]: r for r in rep["rows"]}
    assert rows["ap"]["days_to_verdict"] == 4 and rows["ap"]["applied_n_after"] == 12
    # APPLIED rows accrue on post-apply closes from the apply date: 12 in 35 days -> 10.29 per 30d
    assert rows["ap"]["forward_n"] == 12 and rows["ap"]["forward_n_source"].startswith("applied.n_after")
    assert rows["ap"]["accrual_per_30d"] == 10.29 and rows["ap"]["projected_days_to_floor"] == "23"
    assert rows["ap"]["sign_agreement"] == "disagree"       # in-sample + vs post-apply mean -0.55
    assert rows["rj"]["days_to_verdict"] == 30 and rows["rj"]["projected_days_to_floor"] == "reached"
    assert rows["ap"]["replay_prior_delta_R_mean"] == 0.12 and rows["rj"]["replay_prior_delta_R_mean"] is None
    assert rep["totals"]["replay_priors_file"] == "present"
    md = lc.render_markdown(rep)
    assert lc.BANNER in md and "never at current rate" in md
    assert forbidden_words_found(md) == []
    # the CLI round-trips through files and says when the priors file is absent
    ledger_p = tmp_path / "l.json"
    ledger_p.write_text(json.dumps(_ledger(applied, rej)), encoding="utf-8")
    hist_p = tmp_path / "h.jsonl"
    hist_p.write_text("\n".join(json.dumps(x) for x in hist), encoding="utf-8")
    out_md, out_json = tmp_path / "o.md", tmp_path / "o.json"
    assert lc.main(["--as-of", "2026-10-20", "--ledger", str(ledger_p), "--history", str(hist_p),
                    "--priors", str(tmp_path / "missing.json"), "--out-md", str(out_md), "--out-json", str(out_json)]) == 0
    assert "absent" in out_md.read_text(encoding="utf-8")
    assert json.loads(out_json.read_text(encoding="utf-8"))["totals"]["replay_priors_file"] == "absent"
