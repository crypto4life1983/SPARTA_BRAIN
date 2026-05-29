"""Portfolio construction + cost model + paper order generation. Long-only, top-8 equal-weight (1/8), relative-rank exit."""


def rotation_exits(prev_holdings, new_selected):
    new_set = set(new_selected)
    return [s for s in prev_holdings if s not in new_set]


def rotation_entries(prev_holdings, new_selected):
    prev_set = set(prev_holdings)
    return [s for s in new_selected if s not in prev_set]


def equal_weight_targets(selected, equity, m):
    if not selected or m <= 0 or equity <= 0:
        return {}
    w = equity / m
    return {s: w for s in selected}


def commission_cost(shares, per_share=0.005, min_per_trade=1.0, scalar=1.0):
    n = abs(shares)
    if n <= 0 or scalar <= 0:
        return 0.0
    return max(min_per_trade, n * per_share) * scalar


def slippage_cost(shares, price, bps=1.0, scalar=1.0):
    n = abs(shares)
    if n <= 0 or price <= 0 or scalar <= 0:
        return 0.0
    return n * price * (bps / 10000.0) * scalar


def build_paper_orders(holdings, selected, prices, equity, m=8, per_share=0.005, min_comm=1.0, slip_bps=1.0):
    """Pure order generation: given current holdings {sym:{shares}}, the new top-M selection, fill prices, and equity,
    return a list of paper order dicts (EXIT/ENTER/REBALANCE). Long-only; one lot per name; no shorting/leverage/pyramid."""
    if any(p <= 0 for s, p in prices.items() if s in set(selected) | set(holdings)):
        raise ValueError("non-positive fill price; refuse to build orders (NO-TRADE; data integrity).")
    orders = []
    tgt = (equity / m) if (equity > 0 and m > 0) else 0.0
    for sym in rotation_exits(list(holdings.keys()), selected):
        px = prices[sym]; sh = holdings[sym]["shares"]
        comm = commission_cost(sh, per_share, min_comm); slip = slippage_cost(sh, px, slip_bps)
        orders.append({"symbol": sym, "action": "EXIT", "shares": -sh, "fill_price": px,
                       "commission_usd": comm, "slippage_usd": slip, "cashflow_usd": sh * px - comm - slip})
    for sym in selected:
        px = prices[sym]
        if sym in holdings:
            cur = holdings[sym]["shares"] * px; delta_val = tgt - cur
            if abs(delta_val) < 1e-9:
                continue
            sh = delta_val / px  # +buy / -sell to reach target
            comm = commission_cost(sh, per_share, min_comm); slip = slippage_cost(sh, px, slip_bps)
            cf = -(sh * px) - comm - slip if sh > 0 else (-sh) * px - comm - slip
            orders.append({"symbol": sym, "action": "REBALANCE", "shares": sh, "fill_price": px,
                           "commission_usd": comm, "slippage_usd": slip, "cashflow_usd": cf})
        else:
            sh = tgt / px
            comm = commission_cost(sh, per_share, min_comm); slip = slippage_cost(sh, px, slip_bps)
            orders.append({"symbol": sym, "action": "ENTER", "shares": sh, "fill_price": px,
                           "commission_usd": comm, "slippage_usd": slip, "cashflow_usd": -(sh * px) - comm - slip})
    return orders
