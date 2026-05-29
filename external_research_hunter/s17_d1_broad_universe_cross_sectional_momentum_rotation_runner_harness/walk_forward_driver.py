"""s17-d1 K13 walk-forward driver. The 5 fixed pre-committed UNSEARCHED DA22 folds. run_walk_forward() STUB.

K13 = VALIDATION of the LOCKED rule across folds, NOT optimization. NO per-fold refit. NO fold-scheme search.
NO execution at BUILD.
"""

# DA22 fold boundaries LOCKED byte-equivalent at SEAL (bar-index, inclusive; from the trading calendar).
K13_FOLDS = [
    {"fold": "F1", "idx_start": 160, "idx_end": 478, "date_start": "2019-08-21", "date_end": "2020-11-23", "bars": 319},
    {"fold": "F2", "idx_start": 479, "idx_end": 797, "date_start": "2020-11-24", "date_end": "2022-03-02", "bars": 319},
    {"fold": "F3", "idx_start": 798, "idx_end": 1116, "date_start": "2022-03-03", "date_end": "2023-06-08", "bars": 319},
    {"fold": "F4", "idx_start": 1117, "idx_end": 1435, "date_start": "2023-06-09", "date_end": "2024-09-16", "bars": 319},
    {"fold": "F5", "idx_start": 1436, "idx_end": 1758, "date_start": "2024-09-17", "date_end": "2025-12-30", "bars": 323},
]
N_FOLDS = 5
WARMUP_BARS = 160
SUPERMAJORITY_MIN_POSITIVE_FOLDS = 3  # ceil(0.6 * 5)
BOUNDARIES_SEARCHED = False
PER_FOLD_REFIT = False


def fold_bar_indices(fold):
    """Inclusive [idx_start, idx_end] bar-index range for a fold dict."""
    return list(range(fold["idx_start"], fold["idx_end"] + 1))


def validate_fold_scheme():
    """Assert the locked scheme is contiguous, non-overlapping, 5 folds, unsearched. Returns True or raises."""
    if len(K13_FOLDS) != N_FOLDS:
        raise Exception(f"K13_N_FOLDS_DRIFT: {len(K13_FOLDS)} expected {N_FOLDS}")
    for a, b in zip(K13_FOLDS, K13_FOLDS[1:]):
        if b["idx_start"] != a["idx_end"] + 1:
            raise Exception(f"K13_FOLDS_NOT_CONTIGUOUS: {a['fold']} -> {b['fold']}")
    if K13_FOLDS[0]["idx_start"] != WARMUP_BARS:
        raise Exception(f"K13_FIRST_FOLD_START_DRIFT: {K13_FOLDS[0]['idx_start']} expected {WARMUP_BARS}")
    if BOUNDARIES_SEARCHED is not False or PER_FOLD_REFIT is not False:
        raise Exception("K13_ANTI_SNOOP_VIOLATION: boundaries_searched/per_fold_refit must be False")
    return True


def k13_verdict(per_fold_positive, aggregate_net, k9_ok):
    """Apply the locked K13 gate. per_fold_positive: list[bool] len 5; aggregate_net: float; k9_ok: bool.

    PASS iff >= SUPERMAJORITY_MIN_POSITIVE_FOLDS folds positive AND aggregate_net > 0 AND k9_ok.
    """
    if len(per_fold_positive) != N_FOLDS:
        raise Exception(f"K13_FOLD_COUNT_MISMATCH: {len(per_fold_positive)} expected {N_FOLDS}")
    n_pos = sum(1 for x in per_fold_positive if x)
    passed = (n_pos >= SUPERMAJORITY_MIN_POSITIVE_FOLDS) and (aggregate_net > 0) and bool(k9_ok)
    return {
        "n_folds_positive": n_pos, "supermajority_required": SUPERMAJORITY_MIN_POSITIVE_FOLDS,
        "aggregate_net_positive": aggregate_net > 0, "k9_ok": bool(k9_ok),
        "k13_pass": passed, "verdict": "K13_PASS" if passed else "OOS_NOT_ROBUST",
    }


def run_walk_forward(*args, **kwargs):
    raise RuntimeError(
        "P6_7_K13_NOT_AUTHORIZED: run_walk_forward() is gated by separate operator authorization "
        "(Authorize s17-d1 ... P6.7 K13 walk-forward validation). P3 BUILD scope does NOT authorize any "
        "signal computation, backtest, or simulator run. K13 is VALIDATION of LOCKED params; no per-fold refit."
    )
