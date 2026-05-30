# S26-D16 — Walk-Forward / Rolling-Window Stability (frozen engine, validation only)

**Tests whether S26 "Trend + Support/Resistance + EMA/RSI" (long-only v1) performance is
stable across time windows or depends too much on one lucky period, using the FROZEN engine
and existing daily CSVs. VALIDATION ONLY — no optimization, no parameter change, no strategy
rule change, no new filters, no source/engine/test change. Windows are fixed mechanically;
nothing is tuned.**

- **Created:** 2026-05-30 · **Reference commit:** `51486b3` (S26-D15 regime breakdown)
- **Frozen engine:** `engine/trend_sr_ema_rsi_daily.py` — UNCHANGED.
- **Reconciliation:** the continuous-stream 2013–2022 buckets reproduce the committed IS
  numbers EXACTLY (NQ +7.6536R/117 trades, ES +7.6725R/125 trades), confirming the rolling
  buckets sit on the real frozen trade lists.

---

## 1. S26 current status

- **RESEARCH_CANDIDATE only.**
- **NOT paper-ready. NOT live-ready. NOT deployable.**

This step is diagnostic. It produces **no** trading recommendation.

## 2. Method (fixed, non-optimized)

- **Data:** `data_offline/` daily CSVs (gitignored). NQ/ES 2013–2025, MNQ/MES 2019–2025. No
  2026. No data file modified.
- **Rolling basis:** the frozen engine is run **ONCE on the full continuous per-market
  stream**; closed trades are bucketed by **exit-year**; year / rolling-3yr / rolling-5yr
  blocks are aggregated from those buckets. The continuous stream keeps indicators warm from
  2013 — a standalone short window would blank its first ~200 bars to EMA200 warmup, which
  would distort early-window trade counts.
- **IS/OOS basis:** IS 2013–2022 and OOS 2023–2025 are re-run as **separate standalone
  streams** to reproduce the committed D3/D5/D12 splits.
- **Why two bases:** continuous 2023–2025 carries MORE trades than the re-warmed standalone
  OOS (NQ 39 vs 32; ES 31 vs 27) because the standalone OOS loses its first ~200 bars to
  warmup. Both bases are reported; **neither changes a rule.**

## 3. NQ year-by-year (reference primary) — continuous 156 trades / +16.8159R

| Year | n | Total R | +/- |
|---|---|---|---|
| 2013 | 3 | +3.2897 | + |
| 2014 | 17 | −1.2545 | − |
| 2015 | 21 | −2.7328 | − |
| 2016 | 10 | −4.4470 | − |
| 2017 | 16 | +4.2862 | + |
| 2018 | 12 | +0.3501 | + |
| 2019 | 11 | +1.7840 | + |
| 2020 | 9 | +4.8232 | + |
| 2021 | 14 | +2.5430 | + |
| 2022 | 4 | −0.9883 | − |
| 2023 | 13 | +1.8180 | + |
| 2024 | 12 | +4.9348 | + |
| 2025 | 14 | +2.4094 | + |

**NQ losing years: 2014, 2015, 2016, 2022.** The three consecutive 2014–2016 losses are the
core weakness.

## 4. ES year-by-year (independent primary) — continuous 156 trades / +19.6301R

| Year | n | Total R | +/- |
|---|---|---|---|
| 2013 | 5 | +3.9060 | + |
| 2014 | 12 | −3.5544 | − |
| 2015 | 27 | −4.5901 | − |
| 2016 | 16 | −8.3428 | − |
| 2017 | 13 | +7.0068 | + |
| 2018 | 13 | −0.7869 | − |
| 2019 | 11 | +3.6053 | + |
| 2020 | 8 | +5.0495 | + |
| 2021 | 16 | +5.7606 | + |
| 2022 | 4 | −0.3815 | − |
| 2023 | 8 | −0.4258 | − |
| 2024 | 12 | +4.0465 | + |
| 2025 | 11 | +8.3369 | + |

**ES losing years: 2014, 2015, 2016, 2018, 2022, 2023.** ES shares the same 2014–2016 losing
stretch and is far deeper in it (2016 alone −8.34R).

## 5. NQ rolling 3-year and 5-year windows

**Rolling 3-year (8/11 positive):**

| Window | n | Total R | PF | Exp R | Max DD | +/- |
|---|---|---|---|---|---|---|
| 2013–2015 | 41 | −0.6976 | 0.9438 | −0.0170 | 5.6079 | − |
| 2014–2016 | 48 | **−8.4343** | **0.5103** | −0.1757 | 10.5943 | − |
| 2015–2017 | 47 | −2.8936 | 0.8111 | −0.0616 | 8.3629 | − |
| 2016–2018 | 38 | +0.1893 | 1.0121 | +0.0050 | 5.1454 | + |
| 2017–2019 | 39 | +6.4203 | 1.4853 | +0.1646 | 3.3098 | + |
| 2018–2020 | 32 | +6.9573 | 1.7782 | +0.2174 | 3.3098 | + |
| 2019–2021 | 34 | +9.1502 | 2.0429 | +0.2691 | 2.6513 | + |
| 2020–2022 | 27 | +6.3779 | 1.9383 | +0.2362 | 2.6202 | + |
| 2021–2023 | 31 | +3.3727 | 1.3354 | +0.1088 | 3.6202 | + |
| 2022–2024 | 29 | +5.7645 | 1.5875 | +0.1988 | 3.1820 | + |
| 2023–2025 | 39 | +9.1623 | 1.6924 | +0.2349 | 3.1820 | + |

**Rolling 5-year (6/9 positive):** three negatives — 2013–2017 (−0.86R), 2014–2018 (−3.80R),
2015–2019 (−0.76R) — **all contain 2014–2016**. From 2016–2020 onward every 5yr window is
positive (peak 2017–2021 +13.79R, PF 1.73).

**All NQ negative windows (3yr and 5yr) contain 2014–2016.**

## 6. ES rolling 3-year and 5-year windows

**Rolling 3-year (7/11 positive):**

| Window | n | Total R | PF | Exp R | Max DD | +/- |
|---|---|---|---|---|---|---|
| 2013–2015 | 44 | −4.2385 | 0.7025 | −0.0963 | 8.3853 | − |
| 2014–2016 | 55 | **−16.4873** | **0.2638** | −0.2998 | 16.7281 | − |
| 2015–2017 | 56 | −5.9262 | 0.6906 | −0.1058 | 13.9954 | − |
| 2016–2018 | 42 | −2.1229 | 0.8575 | −0.0505 | 8.3428 | − |
| 2017–2019 | 37 | +9.8252 | 2.0536 | +0.2655 | 3.0304 | + |
| 2018–2020 | 32 | +7.8680 | 1.9924 | +0.2459 | 3.0304 | + |
| 2019–2021 | 35 | +14.4155 | 2.6870 | +0.4119 | 2.2435 | + |
| 2020–2022 | 28 | +10.4286 | 2.6648 | +0.3725 | 1.8311 | + |
| 2021–2023 | 28 | +4.9533 | 1.6243 | +0.1769 | 2.1487 | + |
| 2022–2024 | 24 | +3.2391 | 1.3954 | +0.1350 | 2.6065 | + |
| 2023–2025 | 31 | +11.9575 | 2.1095 | +0.3857 | 2.6065 | + |

**Rolling 5-year (6/9 positive):** three negatives — 2013–2017 (−5.57R), 2014–2018
(−10.27R), 2015–2019 (−3.11R) — **all contain 2014–2016**. From 2016–2020 onward every 5yr
window is positive (peak 2017–2021 +20.64R, PF 2.38).

**All ES negative windows (3yr and 5yr) contain 2014–2016.** ES has a **fourth** negative 3yr
window (2016–2018) NQ does not, because ES's 2016 and 2018 were both losing years.

## 7. Common weak windows

**2014–2016 collapses simultaneously on BOTH primary markets** — the choppy, non-trending
mid-decade regime:
- **NQ 3yr 2014–2016:** −8.4343R, **PF 0.5103.**
- **ES 3yr 2014–2016:** −16.4873R, **PF 0.2638** (far worse).

**Every negative rolling window on both markets contains 2014–2016.** This is a **shared,
un-diversified regime weakness** — NQ and ES do not diversify each other here; they fail
together. Consistent with the D15 shared 2014–2016 drawdown cluster.

## 8. Common strong windows

Every rolling window lying entirely in the **post-2016 trending era** is positive on **both**
markets (2017–2021, 2019–2021, 2020–2024, 2021–2025, etc.), with ES generally stronger than
NQ in the same windows. **NQ and ES agree on both the weak and the strong windows — ES does
not contradict NQ.**

## 9. OOS (2023–2025) vs prior comparable windows

- **NQ 2023–2025 (continuous 3yr):** +9.1623R — essentially equal to **2019–2021 (+9.1502R)**
  and above 2018–2020 (+6.9573R).
- **ES 2023–2025 (continuous 3yr):** +11.9575R — **below 2019–2021 (+14.4155R)** and near
  2020–2022 (+10.4286R).

**OOS is strong but NOT an isolated outlier.** It sits in line with (NQ) or below (ES) the
2019–2021 window — consistent with the broader post-2016 regime, not a single lucky spike.
**Caveat:** the *entire* positive record IS the post-2016 trending era; the strategy has
**not** demonstrated survival of a multi-year choppy regime (it lost on both markets across
2014–2016).

## 10. Proxy/micro notes (descriptive only — NOT independent)

MNQ (proxy of NQ) and MES (proxy of ES) are same-underlying micros with partial history from
2019; descriptive only, cannot change the verdict. **Every** MNQ/MES rolling 3yr and 5yr
window (all start ≥2019, i.e. post-2016) is positive — MNQ full +15.42R/66 trades, MES full
+22.67R/59 trades. Consistent with the big contracts' post-2016 strength; says nothing about
the 2014–2016 weakness (no micro data there).

## 11. Final D16 verdict — **WALK_FORWARD_INCONCLUSIVE**

- **Not WALK_FORWARD_STABLE:** the STABLE bar requires no catastrophic multi-year collapse.
  2014–2016 **is** a multi-year collapse on both markets (ES 3yr −16.49R, PF 0.26; NQ 3yr
  −8.43R, PF 0.51), and the **entire** positive track record is the single post-2016 trending
  regime. Cannot cleanly certify STABLE.
- **Not WALK_FORWARD_FRAGILE:** performance does **not** hinge on a few lucky windows — NQ
  8/11 and ES 7/11 rolling-3yr positive, both 6/9 rolling-5yr positive, broadly positive
  across the whole 2017–2025 era on both markets and on the micros.
- **Not WALK_FORWARD_FAIL:** no collapse in major long windows post-2016; ES does not
  contradict NQ (they agree on weak AND strong windows); OOS is in-line with prior post-2016
  windows, not a contradiction.
- **Honest call — INCONCLUSIVE:** strong, consistent post-2016 stability across both markets,
  undercut by a shared, un-diversified 2014–2016 multi-year regime weakness and a
  single-regime (trending) dependence.

**Flags carried forward:** (1) 2014–2016 very bad on both markets (ES PF 0.26); (2) all
negative rolling windows contain 2014–2016 — common regime risk, no NQ/ES diversification;
(3) the whole positive record is the post-2016 trending era — choppy-regime survival unproven;
(4) OOS strong but in-line with 2019–2021, not an isolated spike (reassuring, not upgrading).

## 12. Does D16 block or permit D17?

**Permits D17 — does not block.** The collapse is **confined to one identifiable subperiod
(2014–2016)**; outside it every window is positive, so the D14 hard blocker *"walk-forward
shows collapse outside one subperiod"* did **NOT** fire. WALK_FORWARD_INCONCLUSIVE allows
proceeding to **S26-D17 friction / slippage / commission stress** — especially important given
the thin IS edge. **This is not a clearance to paper trade; D16 does not upgrade readiness.**

## 13. Trading recommendation

**NONE.** No deployment, no paper, no live. **S26 remains a RESEARCH_CANDIDATE.**

---

### Notes of record
- Validation only — frozen engine, fixed windows, no tuning. No optimization, no
  parameter/rule/source/engine/test change, no new filters.
- Continuous-stream 2013–2022 buckets reproduce the committed IS exactly; standalone IS/OOS
  reproduce the committed D3/D5/D12 splits.
- Donchian/S23/S24/S25, JARVIS, and `templates/base.html` untouched.
- `_walk_raw.json` in this folder is a generated artifact — left untracked. The temp runner
  `_s26_d16_walk.py` was deleted after this report; `report.json` + `report.md` are the
  durable deliverables.
