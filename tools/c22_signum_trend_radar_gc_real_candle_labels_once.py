"""Candidate #22 -- Signum Trend Radar GC REAL-CANDLE ENTRY-LABELS one-off RUNNER
(READ-ONLY; RESEARCH ONLY).

Reads the single locally-staged GC dataset READ-ONLY, builds the deterministic per-asset
entry-signal labels via the pure labels contract (chain-gated on the dataset validation
reaching VALID / VALID_VIA_TIEBREAKER after the human marketRank tie-breaker), and writes a
canonical JSON labels artifact ONLY into the GITIGNORED per-candidate data path
(data/external_signum_trend_radar_gc/detector_labels/). It prints the artifact path + SHA256
+ the label counts.

It does NOT mutate the dataset, invents NO marketRank, makes NO network call, connects to NO
Signum / MCP / Hyperliquid, uses NO API keys / credentials, runs NO replay, optimizes
NOTHING, and does NO commit / push / git add. The labels content is a pure function of the
SHA-pinned dataset, so the artifact is byte-stable.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_contract as _lb  # noqa: E402,E501

DATASET = REPO_ROOT / _lb.DATASET_PATH
OUT_DIR = REPO_ROOT / _lb.ARTIFACT_DIR


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_labels_bytes(payload: dict) -> bytes:
    """The canonical, byte-stable serialization the artifact SHA256 is pinned over."""
    return (json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def main() -> int:
    sha = file_sha256(DATASET)
    parsed = json.loads(DATASET.read_text(encoding="utf-8"))
    record = _lb.build_labels(parsed, sha)
    check = _lb.validate_labels(record)
    if not check["valid"]:
        raise RuntimeError("labels_failed_validation: %s" % check["failures"])
    if record["verdict"] != _lb.VERDICT_LABELS_PRODUCED:
        raise RuntimeError("labels_blocked: %s" % record["blockers"])

    payload = record["labels_payload"]
    blob = canonical_labels_bytes(payload)
    artifact_sha = hashlib.sha256(blob).hexdigest()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    date_tag = time.strftime("%Y-%m-%d", time.gmtime())
    out_path = OUT_DIR / ("%s_%s.json" % (_lb.ARTIFACT_BASENAME, date_tag))
    with open(out_path, "wb") as f:
        f.write(blob)

    out = {
        "artifact_path": str(out_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "artifact_sha256": artifact_sha,
        "artifact_sha256_matches_pin": artifact_sha == _lb.LABELS_ARTIFACT_SHA256,
        "dataset_sha256": sha,
        "dataset_sha256_matches_pin": sha == _lb.DATASET_SHA256,
        "labels_produced": record["labels_produced"],
        "label_counts": record["label_counts"],
        "btc_present": record["btc_present"], "btc_downtrend": record["btc_downtrend"],
        "verdict": record["verdict"],
        "next_required_action": record["next_required_action"],
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
