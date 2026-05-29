"""126-21 relative-strength signal primitives. BYTE-IDENTICAL to the locked s21 mechanic (validated by fidelity test)."""


def trailing_return(closes, i, lookback=126, skip=21):
    j = i - skip
    k = i - skip - lookback
    if k < 0 or j < 0 or j >= len(closes) or k >= len(closes):
        return None
    if closes[k] is None or closes[j] is None or closes[k] <= 0:
        return None
    return closes[j] / closes[k] - 1.0


def cross_sectional_rank(signals):
    valid = [(s, v) for s, v in signals.items() if v is not None]
    valid.sort(key=lambda x: (-x[1], x[0]))
    return [s for s, _ in valid]


def select_top_m(ranked, m):
    if m <= 0:
        return []
    return list(ranked[:m])


def is_rebalance_bar(i, warmup, rebalance_days):
    if rebalance_days <= 0:
        raise ValueError("rebalance_days must be > 0")
    return i >= warmup and (i - warmup) % rebalance_days == 0
