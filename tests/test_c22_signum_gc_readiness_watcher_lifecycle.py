"""Tests for the lifecycle-aware C22 readiness watcher + ASCII-safe tracker output.

Covers: original count-based behavior when the collection review is NOT yet consumed;
suppression of the consumed review token once C22 is in the label-evidence HOLD; evidence
extension counting; anti-tamper; and cp1252-safe tracker rendering. No real dataset scan.
"""
import sparta_commander.c22_signum_gc_collection_readiness_watcher_contract as rw
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as trk

TOKEN = "HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW"


def _facts(n):
    return [{"filename": "gc_crypto_trendradar_daily_2026%02d%02d.json" % (6 if i <= 11 else 7, i),
             "date": "2026-06-%02d" % (19 + i) if (19 + i) <= 30 else "2026-07-%02d" % (19 + i - 30),
             "valid": True} for i in range(1, n + 1)]


# ---- original (not-consumed) behavior preserved -----------------------------

def test_under_20_not_consumed_keeps_collecting():
    r = rw.build_readiness(_facts(19))          # default review_consumed=False
    assert r["status"] == rw.STATUS_NOT_READY
    assert r["ready"] is False and r["suggested_next_token"] is None
    assert rw.validate_readiness(r)["valid"] is True


def test_exactly_20_not_consumed_surfaces_review_token():
    r = rw.build_readiness(_facts(20))          # default review_consumed=False (backward compat)
    assert r["status"] == rw.STATUS_READY
    assert r["ready"] is True
    assert r["suggested_next_token"] == TOKEN
    assert rw.validate_readiness(r)["valid"] is True


# ---- consumed lifecycle: token never resurfaces -----------------------------

def test_consumed_20plus_does_not_resurface_token():
    for n in (20, 23, 30):
        r = rw.build_readiness(_facts(n), review_consumed=True,
                               label_review_decision=rw.LABEL_REVIEW_DECISION)
        assert r["status"] == rw.STATUS_COLLECTING_EXTENSION
        assert r["ready"] is False
        assert r["suggested_next_token"] is None
        assert r["collection_review_consumed"] is True
        assert r["label_review_decision"] == "HOLD_FOR_MORE_C22_LABEL_EVIDENCE"
        assert r["extension_windows"] == max(0, n - rw.REQUIRED_WINDOWS)
        assert r["replay_locked"] is True
        assert rw.validate_readiness(r)["valid"] is True


def test_consumed_extension_grows_with_new_windows():
    a = rw.build_readiness(_facts(21), review_consumed=True)
    b = rw.build_readiness(_facts(24), review_consumed=True)
    assert a["extension_windows"] == 1 and b["extension_windows"] == 4
    # no auto-labeling / auto-replay signal in either
    assert a["suggested_next_token"] is None and b["suggested_next_token"] is None
    assert a["runs_labels"] is False and a["runs_replay"] is False


def test_default_flag_omitted_preserves_original_contract():
    # omitting the flag entirely must behave exactly like the pre-remediation watcher
    r = rw.build_readiness(_facts(20))
    assert r["collection_review_consumed"] is False
    assert r["status"] == rw.STATUS_READY and r["suggested_next_token"] == TOKEN


# ---- anti-tamper -----------------------------------------------------------

def test_validator_rejects_consumed_record_that_surfaces_token():
    r = rw.build_readiness(_facts(22), review_consumed=True)
    r["suggested_next_token"] = TOKEN            # forbidden once consumed
    assert rw.validate_readiness(r)["valid"] is False


def test_validator_rejects_consumed_record_marked_ready():
    r = rw.build_readiness(_facts(22), review_consumed=True)
    r["ready"] = True
    assert rw.validate_readiness(r)["valid"] is False


def test_no_numeric_sufficiency_threshold_invented():
    # the contract exposes only the original 20-window collection threshold; no new numeric
    # thresholds for non-downtrend / LONG / HEDGE / BEAR sufficiency exist.
    assert rw.REQUIRED_WINDOWS == 20
    names = [n for n in dir(rw) if n.isupper()]
    for n in names:
        assert "SUFFICIENT" not in n and "MIN_LONG" not in n and "MIN_BEAR" not in n \
            and "MIN_HEDGE" not in n and "NON_DOWNTREND" not in n


# ---- output compatibility ---------------------------------------------------

def test_tracker_markdown_is_cp1252_safe_and_json_semantics_unchanged():
    s = trk.build_collection_status(["gc_crypto_trendradar_daily.json"])
    md = trk.render_collection_section_markdown(s)
    md.encode("cp1252")                          # must not raise on cp1252 terminals
    assert "✅" not in md                     # no emoji
    assert "C22 Signum GC data-collection tracker" in md and "1 / 20" in md
    # JSON-facing status semantics unchanged
    assert s["collected_windows"] == 1 and s["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
