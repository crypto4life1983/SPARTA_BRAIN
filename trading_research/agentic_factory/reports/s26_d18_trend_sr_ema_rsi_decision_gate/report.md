# S26-D18 — Trend / SR / EMA / RSI Candidate Decision-Gate Memo

**Reviews the committed S26 evidence through D17 and produces an honest park-or-continue
recommendation. MEMO ONLY — no new backtest, no market test, no optimization, no parameter/
rule/source/engine/test change, no data fetch. Built strictly from committed S26 reports
(D2–D17) and S26 git history.**

- **Created:** 2026-05-30 · **HEAD:** `066c16c` (S26-D17 friction sensitivity)
- **Frozen engine:** `engine/trend_sr_ema_rsi_daily.py` — UNCHANGED.
- The untracked `_friction_raw.json` (D17) is noted only as an existing generated artifact;
  this memo rests on the committed `report.json`/`report.md` deliverables.

---

## 1. Current candidate status

- **RESEARCH_CANDIDATE only.**
- **NOT paper-ready.**
- **NOT live-ready.**
- **NOT deployable.**

## 2. Evidence summary

### What S26 was trying to test
Whether a **long-only daily** entry — Trend (`close>EMA200 AND EMA50>EMA200`) + S/R pullback
(`low <= 20-day low + 1.5×ATR20`) + EMA/RSI confirmation, managed with a **2N stop** and
**+2R target** — has a **real, robust, tradeable edge** on index futures (NQ reference, ES
independent), surviving OOS, regime, walk-forward and friction stress.

### Strongest positive evidence
- **OOS PASS on both primaries.** NQ OOS +7.999R / PF 1.7694 / 32 trades (D5 `30f2190`); ES
  OOS +11.4584R / PF 2.2352 / 27 trades (D12 `cfe841d`). The independent market agrees in net
  direction.
- **OOS is friction-robust.** Both NQ and ES OOS stay **positive through severe friction**
  (0.20R/trade): NQ OOS +1.599R, ES OOS +6.058R (D17 `066c16c`).
- **Walk-forward broadly positive post-2016.** NQ 8/11 and ES 7/11 rolling-3yr windows
  positive; both 6/9 rolling-5yr positive (D16 `ca0077f`).
- **No D14 hard blocker fired** across D15/D16/D17 — each step permitted the next.

### Strongest negative evidence
- **Thin IS edge.** NQ IS PF 1.2016 / expectancy +0.0654R; ES IS PF 1.2003 / +0.0614R.
- **Entry significance never demonstrated.** ENTRY_EDGE_INCONCLUSIVE — no horizon reached
  EDGE_LIKELY on IS (D6 `cc73d6a`). The edge is not distinguished from the trend filter alone.
- **Regime risk inconclusive.** The profitable volatility regime is **inconsistent across
  markets** — NQ profit in mid-vol (high-vol negative), ES profit in high-vol (low-vol
  negative) (D15 `51486b3`).
- **Single-regime dependence.** The *entire* positive record is the post-2016 trending regime;
  a shared **2014–2016 multi-year collapse** on both markets (ES 3yr −16.49R/PF 0.26, NQ 3yr
  −8.43R/PF 0.51) with **no NQ/ES diversification** (D16 `ca0077f`).
- **OOS single-year-dominated** on both: NQ 2024 = 61.7% of OOS net, ES 2025 = 72.8%
  (D12/D15).

### Friction sensitivity conclusion (D17)
**FRICTION_SENSITIVE.** OOS robust to severe friction on both primaries, but the thin
full-history IS edge — break-even only **~0.06R/trade** — turns **negative at high friction
(0.10R)**: NQ IS −4.05R, ES IS −4.83R. The binding weakness is the thin IS edge.

### Robustness / OOS limitations
- OOS samples are small (NQ 32, ES 27 trades) and single-year-dominated.
- OOS strength sits entirely in the post-2016 trending era; the strategy has **not** survived a
  multi-year choppy regime (lost on both markets 2014–2016).
- IS max DD exceeds or rivals IS net (NQ 10.59R vs 7.65R; ES 16.73R vs 7.67R) and inflates
  further under friction.

### Market / data coverage limitations
- Only **one genuinely independent market** beyond NQ: **ES**. MNQ/MES are same-underlying
  micro proxies (partial history from 2019), descriptive only.
- No data outside 2013–2025; micros begin 2019 so they cannot speak to the 2014–2016 weak
  regime.
- Max attainable multi-market verdict by design = **PARTIAL_SUPPORT** (independence is by
  underlying, not ticker).

## 3. Decision

**PARK_CANDIDATE.**

## 4. Decision rationale

Park S26 as a documented RESEARCH_CANDIDATE. The strategy is **not broken** — no D14 hard
blocker fired, OOS is positive and friction-robust on both primaries, and the independent
market (ES) agrees with NQ. But the validation ladder D3–D17 has repeatedly returned
**INCONCLUSIVE / SENSITIVE** rather than a strengthening signal, and the cumulative picture is
a **thin edge that lives entirely in the post-2016 trending regime**, lacks demonstrated entry
significance, is friction-sensitive on IS, and whose OOS profit is single-year-dominated.

- **Why not CONTINUE_RESEARCH:** there is no clear, evidence-justified next test on the *same*
  four markets / *same* window that could move the verdict. The open questions (entry
  significance, regime breadth, choppy-regime survival, OOS single-year dominance) need **new
  independent markets** or **other-regime history** (a data-fetch step, separately authorized)
  or a conceptual change — not more analysis of the same data, which would only re-confirm
  INCONCLUSIVE.
- **Why not REDESIGN_REQUIRED:** that overstates the failure. No hard blocker fired; the edge
  is real-but-thin, directionally consistent across the independent market and OOS, and
  friction-robust where it matters most (OOS). The branch is **unproven at the promotion bar,
  not disproven** — so a reversible park is more honest than a forced redesign.
- **Promotion bar not met:** S26 does **not** clear PAPER_REVIEW_CANDIDATE (D14 §4). The "no
  top-year/top-trade dominance" gate **fails** (OOS single-year-dominated on both markets), the
  edge is thin with IS friction-fragility, and regime/walk-forward both returned INCONCLUSIVE
  rather than ACCEPTABLE/STABLE.

## 5. If CONTINUE_RESEARCH

N/A — decision is **PARK_CANDIDATE**.

## 6. If PARK_CANDIDATE — what would unpark it later

Any future unpark requires a **separate, explicitly-authorized** step. Evidence that would
justify unparking:

1. A **genuinely independent market** beyond ES (different underlying — e.g. YM/Dow or
   RTY/Russell) independently confirms a positive, friction-survivable edge, raising
   multi-market support above PARTIAL.
2. **Demonstrated entry edge** — entry significance reaches EDGE_LIKELY (not merely
   inconclusive), distinguishing the entry from the trend filter alone.
3. **OOS profit not single-year-dominated** — positive contribution spread across multiple
   years/markets, not one year carrying 60–73% of net.
4. **Choppy-regime survival** — evidence of survival (or controlled loss) through a multi-year
   non-trending regime comparable to 2014–2016, so the edge is not solely a post-2016 trending
   artifact.
5. **Friction headroom** — a realistic per-trade R-cost model shows the **full-history** edge
   (not just OOS) staying positive under conservative friction.

## 7. If REDESIGN_REQUIRED

N/A — decision is **PARK_CANDIDATE**.

## 8. Guardrails

- **No paper trading authorization.**
- **No live trading authorization.**
- **No new optimization authorized.**
- **No deployment authorization.**
- **No broker / API actions.**
- **No data fetch unless separately authorized.**

This memo authorizes **nothing**. Parking is a documentation state, not a trade action.

## 9. Hashes

- **Current HEAD:** `066c16c87b80fda493e3c312a312a3ae0c9b5d30` (`066c16c`)
- **D17 friction:** `066c16c` · **D16 walk-forward:** `ca0077f` · **D15 regime:** `51486b3`
- **D14 gate design:** `ff6b779` · **D13 closeout:** `91b6931` · **D12 multi-market:** `cfe841d`
- **D5 OOS PASS:** `30f2190` · **D3 IS baseline:** `1bb70f9`

## 10. Trading recommendation

**NONE.** No deployment, no paper, no live. **S26 is PARKED as a RESEARCH_CANDIDATE** with
documented unpark conditions.

---

### Notes of record
- Memo only — built from committed S26 reports (D2–D17) and S26 git history. No new analysis,
  backtest, market test, optimization, parameter/rule/source/engine/test change, or data fetch.
- Donchian/S23/S24/S25, JARVIS, and `templates/base.html` untouched.
- The untracked `_friction_raw.json` (D17) is noted only as an existing artifact; not relied
  upon and not committed.
