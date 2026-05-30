# S26-D17 — Friction / Slippage / Commission Stress (frozen engine, validation only)

**Tests whether S26 "Trend + Support/Resistance + EMA/RSI" (long-only v1) still survives
realistic execution costs, by deducting a fixed R-cost per completed trade from the
already-frozen IS/OOS trade lists. VALIDATION ONLY — no optimization, no parameter change, no
strategy rule change, no new filters, no source/engine/test change. Costs are applied to
frozen outcomes only; nothing about entries, exits, stops, or targets is altered.**

- **Created:** 2026-05-30 · **Reference commit:** `ca0077f` (S26-D16 walk-forward stability)
- **Frozen engine:** `engine/trend_sr_ema_rsi_daily.py` — UNCHANGED.
- **Faithfulness:** base (C=0) reproduces the committed D3/D5/D12 splits EXACTLY (NQ IS
  117/+7.6536, NQ OOS 32/+7.999, ES IS 125/+7.6725, ES OOS 27/+11.4584).

---

## 1. S26 current status

- **RESEARCH_CANDIDATE only.**
- **NOT paper-ready. NOT live-ready. NOT deployable.**

This step is diagnostic. It produces **no** trading recommendation.

## 2. Cost model

- **Method:** each completed round-trip trade's realized `r_multiple` is reduced by a flat
  constant **C** (in R). The same C is applied to every trade. Entries/exits/stops/targets are
  untouched — cost is applied to the frozen trade outcomes only.
- **Why R units:** 1R is the strategy's own per-trade risk unit (stop = entry − 2×ATR20, so
  1R = 2N). Expressing cost in R makes the deduction comparable across markets and trades
  without a dollar model. Converting a real per-trade **\$** cost to R means dividing by the
  \$ value of 1R for that trade (point value × 2×ATR20) — that is **not** computed here; these
  are conservative fixed-R scenarios.
- **Formulas:** adjusted total R = `base_total − C·n`; PF / expectancy / win-rate / max-DD are
  recomputed on the cost-adjusted per-trade R sequence in chronological order; **break-even
  cost per trade = `base_total / n`** (the C that drives adjusted total R to exactly 0).
- **Scenarios:** A_low 0.02R · B_moderate 0.05R · C_high 0.10R · D_severe 0.20R per round trip.

## 3. NQ IS / OOS friction results (reference primary)

**NQ IS 2013–2022** — base 117 trades, +7.6536R, PF 1.2016, exp +0.0654R, DD 10.5943R.
**Break-even C = 0.0654R.**

| Scenario | C | Total R | PF | Exp R | Win% | Max DD | +/- |
|---|---|---|---|---|---|---|---|
| A low | 0.02 | +5.3136 | 1.1349 | +0.0454 | 39.3% | 11.27 | + |
| B moderate | 0.05 | +1.8036 | 1.0434 | +0.0154 | 35.0% | 12.29 | + |
| C high | 0.10 | **−4.0464** | 0.9111 | −0.0346 | 31.6% | 15.27 | **−** |
| D severe | 0.20 | **−15.7464** | 0.7073 | −0.1346 | 26.5% | 23.37 | **−** |

**NQ OOS 2023–2025** — base 32 trades, +7.999R, PF 1.7694, exp +0.25R, DD 2.1827R.
**Break-even C = 0.25R.**

| Scenario | C | Total R | PF | Exp R | Win% | Max DD | +/- |
|---|---|---|---|---|---|---|---|
| A low | 0.02 | +7.359 | 1.688 | +0.23 | 53.1% | 2.26 | + |
| B moderate | 0.05 | +6.399 | 1.5721 | +0.20 | 46.9% | 2.38 | + |
| C high | 0.10 | +4.799 | 1.3978 | +0.15 | 43.8% | 2.58 | + |
| D severe | 0.20 | **+1.599** | 1.1139 | +0.05 | 37.5% | 3.56 | **+** |

**NQ reading:** OOS stays positive through **severe** friction; IS survives low/moderate but
goes **negative at high (0.10R)** and deeply negative at severe, with IS max DD inflating to
23.4R.

## 4. ES IS / OOS friction results (independent primary)

**ES IS 2013–2022** — base 125 trades, +7.6725R, PF 1.2003, exp +0.0614R, DD 16.7281R.
**Break-even C = 0.0614R.**

| Scenario | C | Total R | PF | Exp R | Win% | Max DD | +/- |
|---|---|---|---|---|---|---|---|
| A low | 0.02 | +5.1725 | 1.1298 | +0.0414 | 37.6% | 17.71 | + |
| B moderate | 0.05 | +1.4225 | 1.0337 | +0.0114 | 36.8% | 19.24 | + |
| C high | 0.10 | **−4.8275** | 0.8957 | −0.0386 | 32.8% | 21.99 | **−** |
| D severe | 0.20 | **−17.3275** | 0.6847 | −0.1386 | 28.8% | 29.68 | **−** |

**ES OOS 2023–2025** — base 27 trades, +11.4584R, PF 2.2352, exp +0.4244R, DD 2.0697R.
**Break-even C = 0.4244R.**

| Scenario | C | Total R | PF | Exp R | Win% | Max DD | +/- |
|---|---|---|---|---|---|---|---|
| A low | 0.02 | +10.9184 | 2.1487 | +0.4044 | 55.6% | 2.13 | + |
| B moderate | 0.05 | +10.1084 | 2.0224 | +0.3744 | 51.9% | 2.22 | + |
| C high | 0.10 | +8.7584 | 1.8294 | +0.3244 | 48.2% | 2.50 | + |
| D severe | 0.20 | **+6.0584** | 1.5065 | +0.2244 | 48.2% | 3.10 | **+** |

**ES reading:** same shape as NQ — OOS robust to **severe** friction (most robust window in
the study, +6.06R at severe); IS thin, **negative at high (0.10R)**, IS max DD inflates to
29.7R at severe.

## 5. Proxy/micro descriptive results (NOT independent)

MNQ/MES are same-underlying micros with partial history from 2019; descriptive only. Both
windows on both micros stay positive under **all** scenarios including severe (MNQ IS +0.97R,
MNQ OOS +1.28R, MES IS +4.77R, MES OOS +6.39R at severe). **Caveat:** their IS sits entirely
in the post-2016 trending era, so their large IS cushion (break-even 0.24–0.44R) is **not
comparable** to the full-history primaries' thin IS.

## 6. Break-even friction per trade & sensitivity ranking

| Window | Break-even C (R) | Behavior |
|---|---|---|
| **ES IS 2013–2022** | **0.0614** | most fragile — negative by C=0.10R |
| **NQ IS 2013–2022** | **0.0654** | negative by C=0.10R |
| NQ OOS 2023–2025 | 0.25 | positive through severe |
| ES OOS 2023–2025 | 0.4244 | most robust — +6.06R at severe |
| *MNQ IS / OOS* | *0.2358 / 0.2401* | *descriptive* |
| *MES IS / OOS* | *0.3703 / 0.4366* | *descriptive* |

**Most fragile → least fragile:** ES IS → NQ IS → NQ OOS → ES OOS. The two **full-history IS**
windows are the binding constraint — a cushion of only ~0.06R, 4–7× smaller than OOS.

## 7. Final D17 verdict — **FRICTION_SENSITIVE**

- **Not FRICTION_ROBUST:** ROBUST would require the full edge (including IS) to hold under high
  friction. Both full-history IS windows go **negative at high friction (C=0.10R)** — NQ IS
  −4.05R, ES IS −4.83R — with IS break-even only ~0.06R. The conservative call cannot certify
  ROBUST while IS flips negative under high friction on both primaries.
- **Not FRICTION_FRAGILE:** the FRAGILE trigger (IS or ES negative under **moderate** friction)
  did **not** fire — at moderate (0.05R) both IS windows are still positive (NQ +1.80R, ES
  +1.42R) and OOS is strongly positive.
- **Not FRICTION_FAIL:** the FAIL trigger (OOS negative under low/moderate, or both primaries
  fail) did **not** fire — OOS stays positive on both primaries under **every** scenario,
  including severe.
- **Honest call — SENSITIVE:** results survive low and moderate friction on both markets and
  OOS survives even severe friction, but the thin full-history IS edge becomes negative under
  high friction on both primaries — the textbook "survives low/moderate, weak under
  high/severe" pattern. **OOS robust; IS fragile.**

**Flags carried forward:** (1) IS edge thin — break-even ~0.06R, smallest cushion in the
study; (2) both full-history IS windows negative at high friction (0.10R); (3) IS max DD
inflates sharply under friction (ES IS 16.73R → 29.68R at severe); (4) OOS friction-robustness
does **not** cure the post-2016 single-regime concentration flagged in D15/D16.

## 8. Does D17 block or permit D18?

**Permits D18 — does not block.** The D14 hard blocker *"Negative OOS after realistic
friction"* did **NOT** fire — OOS stays positive on both primaries through severe friction.
FRICTION_SENSITIVE allows proceeding to **S26-D18 final research-readiness review**, carrying
the thin-IS-edge friction fragility as an explicit caution. **This is not a clearance to paper
trade; D17 does not upgrade readiness.**

## 9. Trading recommendation

**NONE.** No deployment, no paper, no live. **S26 remains a RESEARCH_CANDIDATE.**

---

### Notes of record
- Validation only — frozen engine, fixed cost scenarios applied to frozen trade outcomes. No
  optimization, no parameter/rule/source/engine/test change, no new filters.
- Base (C=0) reproduces the committed D3/D5/D12 splits exactly.
- Donchian/S23/S24/S25, JARVIS, and `templates/base.html` untouched.
- `_friction_raw.json` in this folder is a generated artifact — left untracked. The temp
  runner `_s26_d17_friction.py` was deleted after this report; `report.json` + `report.md`
  are the durable deliverables.
