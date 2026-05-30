# S28-D1 — New Strategy Hypothesis Selection Memo

**Compares five candidate hypotheses and selects exactly one next branch to test.
MEMO ONLY — no code, no backtest, no optimization, no data fetch, no change to
Donchian/S26/S27, no paper/live. The selection is a research direction, not an
authorization to build.**

- **Created:** 2026-05-30 · **HEAD:** `4505fbf`
- **Donchian:** PARKED. **S26 Trend+S/R+EMA/RSI:** PARK_CANDIDATE. **S27 Mean Reversion:**
  PARKED after IS_FAIL.

---

## 1. Context from the parked branches

| Branch | Outcome | The lesson it leaves |
|---|---|---|
| **Donchian** (S23–S25) | WATCH → ENTRY_EDGE_NOT_SUPPORTED → SEQUENCE_RISK_FRAGILE | Raw breakout entry showed **no edge vs random**; net flips **negative without the top 3 winners**; OOS only 16 trades. Fat-tail-winner dependence. |
| **S26 Trend+S/R+EMA/RSI** | OOS PASS but PARK_CANDIDATE | Entry edge **INCONCLUSIVE**, thin IS (PF~1.20), **FRICTION_SENSITIVE** (IS negative at 0.10R), whole record post-2016, **2014–2016 NQ+ES collapse**, OOS single-year-dominated. |
| **S27 Mean Reversion** | IS_FAIL | 18 trades, **−1.75R**, PF 0.84, negative expectancy, 3/10 positive years, **top-3 gate FAIL**; capped target rarely reached, two-step confirmation too restrictive. |

**What the next hypothesis must avoid:** weak/inconclusive entry edge · thin or negative IS
expectancy · high friction sensitivity · regime concentration & the **2014–2016 chop collapse**
(the one failure shared across branches) · top-winner dependence · low trade count from
over-restrictive entries.

**Data reality:** daily OHLCV for NQ, ES, MNQ, MES is provisioned **including a real `volume`
column** — so volume- or ATR-expansion proxies need **no new fetch**. No intraday, no other
underlyings. NQ and independent ES remain the clean multi-market pair.

## 2. Candidate comparison

| # | Candidate | Entry edge separable & testable? | Regime risk | Friction | Trade count | Distinct from parked? | Data | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | Volatility-confirmed trend continuation | yes, but likely inconclusive | **HIGH** (=S26) | moderate | moderate | **No** (S26 family) | none new | WEAK |
| 2 | **Breakout-RETEST + vol-expansion + no-trade regime gate** | **yes — double-testable (vs random AND vs raw breakout)** | MEDIUM (gated) | low-moderate | low-moderate | **Yes** | none new | **STRONGEST** |
| 3 | Pullback, NQ-only confirm, ES kept independent | yes, but likely inconclusive | HIGH (=S26) | moderate | moderate | No (S26 family) | none new | MODERATE |
| 4 | Bad-regime / no-trade classifier | n/a (no entry) | the regime tool itself | n/a | n/a | Yes | none new | STRONG INSIGHT, not standalone |
| 5 | Time/seasonal tendency + trend filter | yes, cleanly (overfit-prone) | HIGH (decays) | low-moderate | **low** | Yes | none new | WEAK-MODERATE |

## 3. Ranking (best → worst)

**2 → 4 → 3 → 5 → 1.**

## 4. Selected hypothesis — **Idea 2: Breakout-Retest with Volatility-Expansion confirmation (+ mechanical bad-regime no-trade gate)**

Wait for a clean break of a prior daily resistance level; **do not enter the breakout.** Enter
only on a subsequent **retest that holds** the broken level (prior resistance becomes support),
**and** only when a volatility/volume expansion confirms participation. **Skip all trades** in a
mechanically-flagged low-vol/chop regime.

## 5. Why it won

- **Separable AND double-testable entry edge.** The retest-that-holds is a discrete, datable
  event that can be significance-tested **two ways**: vs random-in-uptrend, *and* vs entering on
  the raw breakout. The second test isolates the retest's marginal value — the precise thing
  S26 (inconclusive) and Donchian (not supported) never demonstrated — and it even yields
  information about the parked Donchian.
- **Genuinely distinct from parked families.** Donchian entered on the raw breakout; S26 entered
  on a pullback inside an uptrend. The retest-of-a-reclaimed-level is a different event with a
  different trade population, so it produces new information rather than re-discovery.
- **Friction headroom.** Larger structures → wider stops, fewer/larger-R trades — the opposite
  of S26's thin, friction-fragile edge.
- **Regime mitigation is built into the hypothesis, not bolted on.** It absorbs Idea 4's core
  insight as a **hard no-trade regime gate**, attacking the 2014–2016 chop collapse that sank
  both Donchian and S26 — the one failure no prior entry redesign escaped.
- **Immediately testable with existing data**, independently on NQ and ES, using the real daily
  volume column — no fetch.

## 6. Why the others lost

- **Idea 4 (regime classifier):** the strongest *insight* (it targets the universal 2014–2016
  failure directly) but it is **not a standalone entry** — by construction it makes no trades,
  and gating an edgeless entry creates no edge. Its value is realized **inside** the winner as a
  no-trade gate, which is exactly how it is used.
- **Idea 3 (NQ-confirm pullback):** methodologically clean (keeps ES independent, fixing the
  old S27-D1 Idea-3 flaw) but the mechanism is a pullback-in-uptrend — **too close to the parked
  S26**; the NQ-only confirmation is unlikely to add the separable edge S26 already couldn't show.
- **Idea 5 (seasonal):** cleanly testable but a **weak prior**, overfit-prone, regime-dependent,
  and prone to the **low-trade-count** trap that already sank Donchian/S27.
- **Idea 1 (vol-confirmed continuation):** **closest to the parked S26** — same trend dependence
  and same 2014–2016 vulnerability; least new information.

## 7. Key risks for the selected idea

1. **Chop is still the native risk** of a trend-following structure — the vol-expansion gate and
   no-trade regime filter must do real work, not cosmetic filtering.
2. **Overfitting** the level / breakout / retest / vol-gate / regime-gate definitions — all must
   be **frozen before any result, no sweeps** (the S26/S27 anti-overfit discipline).
3. **Trade-count starvation** if the retest + vol gate + regime gate stack too restrictively
   (watch the Donchian/S27 low-count failure — floors must be pre-registered).
4. **Entry significance must actually PASS.** If the retest does not beat raw-breakout entry,
   **PARK immediately** — do not continue "inconclusive" the way S26 did.

## 8. First proposed S28-D2 spec direction

Pre-register a **FROZEN** spec on daily **NQ IS 2013–2022** (OOS 2023–2025 **sealed**):

1. mechanical **resistance level** (e.g. prior N-day high / confirmed swing high);
2. **breakout rule** (close beyond the level by a fixed buffer);
3. **retest-hold rule** (price returns to the level within a fixed window and closes back above);
4. **vol/volume-expansion gate** using ATR and the real daily volume column;
5. a mechanical **bad-regime NO-TRADE gate** (trend-vs-chop label) defined before any result;
6. fixed **R-stop** and capped **R-target** with conservative same-bar precedence; one position
   at a time; R-only;
7. pre-register **both** significance tests (retest vs random-in-regime; **retest vs raw
   breakout**) and the full pass/watch/fail ladder **before** any IS run. No optimization.

## 9. Final line

**“S28-D1 is hypothesis selection only; no strategy code, backtest, OOS, paper, or live trading
is authorized.”**

---

### Notes of record
- Memo only — built from committed Donchian/S26/S27 reports and the provisioned daily data
  inventory. No code, backtest, optimization, or data fetch.
- Donchian/S23/S24/S25, S26, S27, JARVIS, `templates/base.html`, and the hydra dir untouched.
