"""In-memory paper book + drawdown tracker. No persistence side-effects here (logging is separate)."""


class PaperBook:
    def __init__(self, start_cash=100000.0):
        self.cash = float(start_cash)
        self.holdings = {}  # sym -> {"shares": float, "cashflow": float}

    def apply_orders(self, orders):
        for o in orders:
            sym = o["symbol"]; sh = o["shares"]; self.cash += o["cashflow_usd"]
            if o["action"] == "EXIT":
                self.holdings.pop(sym, None)
            else:
                h = self.holdings.setdefault(sym, {"shares": 0.0, "cashflow": 0.0})
                h["shares"] += sh; h["cashflow"] += o["cashflow_usd"]
                if abs(h["shares"]) < 1e-12:
                    self.holdings.pop(sym, None)

    def equity(self, prices):
        mv = sum(h["shares"] * prices[s] for s, h in self.holdings.items() if s in prices)
        return self.cash + mv

    def positions(self):
        return sorted(self.holdings.keys())


class DrawdownTracker:
    def __init__(self):
        self.peak = None; self.max_dd = 0.0

    def update(self, equity):
        if self.peak is None or equity > self.peak:
            self.peak = equity
        cur = 0.0 if (self.peak is None or self.peak <= 0) else (self.peak - equity) / self.peak
        self.max_dd = max(self.max_dd, cur)
        return {"current_drawdown": cur, "max_drawdown": self.max_dd, "peak_equity": self.peak}
