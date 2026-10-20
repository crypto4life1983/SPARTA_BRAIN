"""tools/trade_features.py: entry-bar buckets for the rule search."""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\SPARTA_BRAIN")
from tools import trade_features as tf  # noqa: E402


def test_buckets_from_the_new_fields():
    rec = dict(candle_body_strength=0.9, atr_expansion=1.3, volume_ratio=2.0, range_position=0.1,
               ema20_dist_atr=1.5, ema200_dist_atr=-0.2)
    f = tf.features_from_record(rec)
    assert f == {"body_bucket": "full", "atr_expansion_bucket": "expanding", "volume_bucket": "high",
                 "range_pos_bucket": "bottom", "ema20_dist_bucket": "far_above", "ema200_side": "below"}


def test_buckets_fall_back_to_the_legacy_fields():
    rec = dict(candle_body_strength=0.44, atr_at_entry=0.0057, atr_avg_at_entry=0.0064,
               entry_price=0.09253, ema20_at_entry=0.0997, ema200_at_entry=0.0934)
    f = tf.features_from_record(rec)
    assert f["body_bucket"] == "mid"
    assert f["atr_expansion_bucket"] == "contracting"          # 0.0057/0.0064 = 0.89
    assert f["ema20_dist_bucket"] == "far_below"               # (0.0925-0.0997)/0.0057 = -1.26
    assert f["ema200_side"] == "below"
    assert f["volume_bucket"] is None and f["range_pos_bucket"] is None


def test_edges_are_inclusive_the_documented_way():
    assert tf.features_from_record({"candle_body_strength": 0.805})["body_bucket"] == "full"
    assert tf.features_from_record({"candle_body_strength": 0.8049})["body_bucket"] == "strong"
    assert tf.features_from_record({"atr_expansion": 1.1})["atr_expansion_bucket"] == "expanding"
    assert tf.features_from_record({"range_position": 0.85})["range_pos_bucket"] == "top"
    assert tf.features_from_record({"range_position": 0.15})["range_pos_bucket"] == "bottom"


def test_trade_bucket_reads_the_latest_record_per_trade(tmp_path):
    p = tmp_path / "ctx.jsonl"
    lines = [
        {"trade_id": 7, "event_type": "trade_entry_recorded", "candle_body_strength": 0.2},
        {"trade_id": 7, "event_type": "trade_entry_recorded", "candle_body_strength": 0.95},   # later wins
        {"trade_id": "x", "candle_body_strength": 0.5},                                      # ignored
        "not json",
    ]
    p.write_text("\n".join(json.dumps(x) if isinstance(x, dict) else x for x in lines), encoding="utf-8")
    tf.clear_cache()
    assert tf.trade_bucket({"id": 7}, "body_bucket", p) == "full"
    assert tf.trade_bucket({"id": "7"}, "body_bucket", p) == "full"
    assert tf.trade_bucket({"id": 8}, "body_bucket", p) is None
    assert tf.trade_bucket({"id": 7}, "not_a_field", p) is None
    assert tf.coverage([{"id": 7}, {"id": 8}], p)["body_bucket"] == 1
    assert tf.load_context(tmp_path / "missing.jsonl") == {}
    tf.clear_cache()
