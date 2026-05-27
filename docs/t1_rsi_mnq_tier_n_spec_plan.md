# T1 RSI MNQ — Tier-N Specification PLAN

**Status:** PLAN (not DRAFT, not SEALED). Operator confirms DRAFT-level ambiguities at a separate fresh authorization. No code. No fetch. No run by this PLAN.

**Authored (UTC):** `2026-05-27T17:00:00Z`
**Authorization:** *"Authorize T1 RSI MNQ Tier-N spec PLAN only."*
**Controller session:** THIS_SESSION_ONLY

**Plan source upstream (READ-ONLY anchors):**
- S12-D1 P11 PARK memo (this session): commit `ce279cf`, seal `321b8940a5516762`
- S12-D1 P11 PARK memo (parallel canonical): commit `ecbd0011`, seal `b9722d424f6faabe`
- S10-D2 lifecycle park report (this session): commit `b580aedb`, seal `8d59e94a736aa82d`
- Parallel post-park selection plan: commit `0e3f9d49` (`docs/next_research_track_selection_plan_after_s12_d1_park.md`)
- Parallel session has also independently authored an `s13-d1` chain (SEAL `262491c`; P1 plan-lock `005cb8a`); this T1 chain uses operator-specified shorter naming under `docs/t1_rsi_mnq_tier_n_spec_plan.md` at non-colliding paths

**HARD BOUNDARIES (held by this PLAN).** PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No RSI computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No `DATABENTO_API_KEY` access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. No s11-d1 / s12-d1 / parallel session s13-d1 sealed-artifact modification. No s12-d1 revival. No `_revN_` revision of s12-d1 authorized by this plan. No s10-d2 / s10-d1 / s9 / s7-d1 / B005_NNN / B006_NNN / T8 sealed-artifact modification. No ORB branch mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No `pipeline_manifest` modification. No `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No branch change. No git push. No live trading. No profitability claim. **Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC NEVER GRANTED. Advisory label permanent: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. `verdict_never_means_live_ready: True`.**

---

## 1. Candidate identification (LOCKED at PLAN)

| Field | Value |
|---|---|
| `candidate_record_id` | `t1-rsi-mnq-c0-mean-reversion-2-period-databento-long-history` |
| Track family | T-series (higher-frequency mean-reversion track) |
| Successor to | S12-D1 (which parked at `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` due to K9 firing on Donchian-15/8 trend-following) |
| Relationship to parallel `s13-d1` chain | Non-colliding chain; operator authorized T1 naming for this session |

This T1 candidate is **structurally fresh**, not a `_revN_` revision of any prior parked candidate. The first-principles burden against each parked predecessor is enumerated in §3.

---

## 2. Locked-at-PLAN structural decisions

The following load-bearing structural decisions are **LOCKED at PLAN**. Any DRAFT or SEAL revision that attempts to alter them shall be rejected; alteration requires a fresh `candidate_record_id` per the same first-principles burden that gave rise to T1.

| Field | LOCKED at PLAN |
|---|---|
| **Mechanic family** | **F3** — RSI Mean-Reversion, bi-directional, no pyramid |
| **RSI period** | **2** (Connors canonical) |
| **Signal direction** | Long+Short bi-directional |
| **Entry/exit framework** | Long when RSI(2) < 10; close when RSI(2) > 50. Short when RSI(2) > 90; close when RSI(2) < 50. (Exact thresholds may be adjusted to {5, 10, 15, 20} and {50, 60} variants at DRAFT; the structural framework — RSI(2) oversold/overbought bands → mean-reversion → recross-to-median exit — is locked.) |
| **Pyramid mechanism** | NONE / `max_units_per_market = 1` |
| **Universe** | `{MNQ.c.0}` (single Micro E-mini Nasdaq-100 continuous front-month) |
| **Asset class** | Micro-futures (continuous front-month) |
| **Schema** | `ohlcv-1d` (daily bars) |
| **`stype_in`** | `continuous` |
| **IS window** | `2019-05-13 → 2023-12-29` (same as S12-D1; enables apples-to-apples comparison) |
| **OOS window (never inspected at IS)** | `2024-01-02 → 2025-12-30` |
| **Data source** | Reuse audit-clean MNQ.c.0 CSV at `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_1d_2019-05-13_2025-12-30.csv` (sha `8b7b832c62fae185...`); **ZERO new Databento fetch required** |

---

## 3. First-principles burden vs all parked / rejected predecessors

T1 is not a rescue of any prior candidate. Each first-principles distinction:

### 3.1 vs S12-D1 (Donchian-15/8 on MNQ.c.0; parked `INSUFFICIENT_SAMPLE_AT_IS`)
- **Different mechanic family:** F3 (RSI mean-reversion) vs F1 (Donchian trend)
- **Different signal generator:** RSI(2) oversold/overbought oscillator vs Donchian channel breakout
- **Different expected signal frequency:** ~50–65 trades/year (T1) vs ~7–10 trades/year (S12-D1)
- **The S12-D1 falsification (insufficient signal density on Donchian-15/8) does NOT transfer to T1** because the load-bearing falsification cause was the channel-breakout signal generator, not the universe choice.

### 3.2 vs S10-D2 (4-market Donchian-55/20; parked `OOS_INDETERMINATE_K9_FIRED`)
- **Different mechanic family:** RSI mean-reversion vs Donchian trend
- **Different universe:** single MNQ.c.0 vs 4-market NQ+GC+ZN+CL portfolio
- **Different Donchian periods:** N/A (no Donchian in T1)

### 3.3 vs S10-D1 (MNQ+MGC Donchian; parked DR9)
- **Different mechanic family**
- **Different universe:** {MNQ.c.0} vs {MNQ.c.0, MGC.c.0}
- **MGC continuous-stitch DR9 failure structurally absent** (MGC not in T1 universe)

### 3.4 vs s9 (RSI-2 mean-reversion on SPY/TLT/GLD/USO ETF-proxy; parked K1+K2 fires)
- **Different universe:** MNQ futures vs SPY/TLT/GLD/USO ETF-proxy basket
- **Different signal direction:** bi-directional vs s9's long-only
- **Different asset class:** futures vs equity ETFs
- **Different cost surface:** per-contract commission + tick slippage vs per-share + bps
- **The s9 falsification cause** (negative S0 net PnL of −$1,211 on the long-only RSI(2) ETF-proxy version with DR2/DR3 cost-stress fires) was instrument-specific cost/edge interaction, not the RSI(2) signal generator itself. T1's first-principles claim: the s9 falsification does NOT transfer.

### 3.5 vs s7-D1 (Donchian + pyramid on 4-ETF basket; parked K12)
- **Different mechanic family** (RSI mean-reversion vs Donchian trend)
- **NO pyramid in T1** (s7-D1 used pyramid)
- **Different universe** (MNQ futures vs ETF basket)

### 3.6 vs s8-D1 (Donchian no-pyramid 4-market; parked sizing-undersized)
- **Different mechanic family**
- **Different universe** (single instrument vs multi-market)
- **Sizing fix already inherited** from s12-d1 lineage at $100k–$200k starting cash (TBD at DRAFT)

### 3.7 vs s11-d1 (single-instrument MNQ.c.0 Donchian-55/20; sealed but never ran)
- **Different mechanic family** (RSI vs Donchian)
- **Different lookback period** (N/A for RSI)
- **Higher signal frequency by ~5–6×** (~50–65/y vs ~25–50/y)

### 3.8 vs B005_NNN / B006_NNN / T8 ETF-proxy umbrella families
- **Different asset class** (futures vs equity ETFs)
- **Different mechanic family** (where applicable)

### 3.9 vs parallel session's `s13-d1` chain (SEAL `262491c`)
- **Distinct chain at non-colliding paths.** Parallel session uses longer naming (`s13_d1_..._databento_long_history`); this T1 chain uses operator-specified `t1_rsi_mnq` naming. Both chains can coexist; substantive content may converge by independent corroboration analogous to the earlier S10-D2 P6.5 / S12-D1 P6 IS / P11 PARK pattern.
- This T1 PLAN does NOT modify any parallel-session artifact.

---

## 4. K9-reachability analysis at PLAN (NEW framework discipline applied)

Per the L8 lesson from parallel's post-park selection plan (`0e3f9d49`) and the C1.A/C1.D framework, every PLAN must include explicit K9-reachability calculations at both IS and OOS scopes.

### 4.1 K9 threshold per window

| Window | Length (years) | Required trades/year for K9 = 100 |
|---|---:|---|
| IS (S11-D1 / S12-D1 / T1 lineage) | 4.6 | ≥ 21.74 trades/y |
| **OOS** | **2.0** | **≥ 50.00 trades/y** (BINDING) |

The OOS constraint (50/y) is ~2.3× the IS constraint (22/y). T1 must comfortably exceed 50 trades/year **on average across the full diagnostic window**, not by hopeful estimation.

### 4.2 T1 expected trade frequency (PLAN-level disclosure)

| Estimate band | RSI(2) bi-directional on MNQ.c.0 over 4.6y IS |
|---|---|
| Lower bound | **~46 trades/year** (~210 over 4.6y) |
| Central | **~57 trades/year** (~262 over 4.6y) |
| Upper bound | **~68 trades/year** (~313 over 4.6y) |

Estimates based on RSI(2) historical trade-frequency literature (Connors / Larry Connors's RSI(2) on equity index daily data; adapted for bi-directional + futures cost surface). **5–6× higher than Donchian-15/8** on the same universe.

### 4.3 K9 status assessment

| Window | Lower-bound estimate vs K9 threshold | Status |
|---|---|---|
| IS (4.6y; threshold 22/y) | 46 ≫ 22 | **CLEARS WITH MARGIN** |
| **OOS (2.0y; threshold 50/y)** | **46 / 57 / 68 vs 50** | **BORDERLINE-TO-CLEARING** |

**Honest disclosure (carried byte-equivalent from parallel's selection plan):** OOS K9 at the **lower-bound estimate of 46 trades/year is BELOW the 50/y threshold** and would fire OOS K9. At central / upper estimates the candidate clears OOS K9.

This is structurally a more favorable position than S12-D1 (where IS lower bound 80 ↔ K9 100 fired the ratio 0.8; T1 lower bound 46 ↔ OOS threshold 50 yields ratio 0.92 — closer to clearance) but **OOS K9 is NOT guaranteed to clear at lower-bound estimate**. Per C1.A acknowledgement carried into T1 SEAL: if OOS K9 fires at sub-threshold, disposition shall be DR1 `INCONCLUSIVE_HOLD` (not REJECT_FAST).

---

## 5. Cost-stress framework (deferred to SEAL; carry s12-d1 5-tier)

Cost-stress matrix S0/S1/S2/S3/S4 LOCKED at SEAL (deferred from PLAN; carried byte-equivalent from S12-D1 / s11-d1 v1 lineage):

| Tier | cost_scalar | slippage_scalar | Note |
|---|---:|---:|---|
| S0 | 0.0 | 0.0 | zero-cost ideal |
| S1 | 1.0 | 1.0 | baseline retail |
| S2 | 1.5 | 1.5 | stressed retail |
| S3 | 2.0 | 2.0 | adversarial |
| S4 | 3.0 | 3.0 | extreme adversarial |

**Cost-stress is structurally MORE binding for RSI(2) than for Donchian-15/8** because mean-reversion exits at smaller moves (RSI recross to 50 typically yields smaller per-trade moves than full Donchian channel exits). The DR2/DR3/DR5 reject-fast rules apply with higher prior probability at S2/S3 for T1 than for trend-following candidates.

DRAFT-level analysis required: pre-registered S0 edge sign, expected expectancy band, cost-tier flip-to-negative tier (if any). DA register at DRAFT covers commission/fees/slippage (DA8/DA9/DA10 framework-locked).

---

## 6. K-gate + DR-rule framework (deferred to SEAL; carry s12-d1 with adaptations)

K-gates (carry byte-equivalent from S12-D1 with single-instrument simplifications):

| Gate | Trigger |
|---|---|
| K1 | `sharpe_proxy_per_trade < 0` at S1 |
| K2 | `expectancy_per_trade_usd ≤ 0` at S1 |
| K4 | `trade_curve_max_drawdown_abs > 50% × START_CASH` |
| K6 | NOT APPLICABLE (single-instrument) |
| K7 | `silent_filter_introduction_after_lock` |
| K8 | `runtime_safety_invariant_false` |
| K9 | `closed_trades < 100` (IS + OOS both) |
| K10 | NOT APPLICABLE (single-instrument) |
| K11 | NOT APPLICABLE (no leverage cap for F3) |
| K12 | composite cost-stress fail (DR2 + DR3) — **elevated prior probability for RSI(2)** |

DR rules: carry S12-D1 D-rules with the following T1-specific adaptations:
- **DR2 / DR3 / DR5 elevated prior probability:** RSI(2) is more cost-sensitive than Donchian trend; SEAL-time pre-registered S0 edge magnitude required
- **DR10 (turnover-cost-explosion) elevated:** RSI(2) trades 5–6× as often as Donchian-15/8; per-trade dollar move smaller; turnover is ~30–40× higher in dollar terms. DRAFT-level mitigation lever: larger START_CASH (carry s12-d1 DA4=B $100k or higher per DRAFT)
- **DR9 (data continuity):** carried byte-equivalent; MNQ.c.0 audit-clean

---

## 7. No-live / no-Strategy-Lab / no-brokerage invariants (deferred to SEAL; carry s12-d1's 25-invariant set)

Total SEAL invariants planned: **25** (carried byte-equivalent from S12-D1; new T1-specific invariants TBD at DRAFT).

7 inherited B005_NNN framework · 4 inherited B006_001 · 2 inherited B006_002 · 5 inherited s10-D1 specific · 3 inherited s11-d1 specific · 4 NEW T1-specific (mechanic family lock at PLAN; RSI period lock at PLAN; bi-directional lock at PLAN; etc.).

Permanent status surface (independent of any future verdict):
- Trading: `PAUSED`
- Live mode: `BLOCKED_AT_6_GATES`
- FRC: `NEVER_GRANTED`
- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`: permanent
- Six live-trading gates BLOCKED regardless of verdict: YES

---

## 8. Forbidden tracks recognized at PLAN (carried from parallel's selection plan §4)

This T1 PLAN inherits the forbidden-tracks list from parallel's selection plan `0e3f9d49`. T1 satisfies all 8 forbidden-track exclusions:

- **T-FORBID-1** (Donchian-15/8 on MNQ.c.0): T1 uses RSI(2), not Donchian
- **T-FORBID-2** (`_revN_` of s12-d1): T1 is structurally fresh `candidate_record_id`
- **T-FORBID-3** (s10-D2 parameter-iteration revival): T1 different universe + mechanic
- **T-FORBID-4** (s10-d1 MGC revival): T1 universe is MNQ.c.0 only
- **T-FORBID-5** (s9 ETF-proxy revival on SPY/TLT/GLD/USO): T1 universe is MNQ futures, orthogonal
- **T-FORBID-6** (s7-D1 / T8 ETF-proxy revival): T1 universe is MNQ futures, orthogonal
- **T-FORBID-7** (B006_001 / B006_002 SPY vol-targeting): T1 universe is MNQ futures, orthogonal
- **T-FORBID-8** (NKE Tier-1 Options Wheel revival): T1 is mechanic family F3, not OW

---

## 9. Validation V-gates (this PLAN turn)

- **V1** ASCII-only
- **V2** Numbered sections in monotonic order
- **V3** No execution language
- **V4** No self-authorization (this PLAN does NOT authorize DRAFT / SEAL / BUILD / RUN; only a separate operator turn does)
- **V5** No code modification
- **V6** No backtest run
- **V7** No simulator run
- **V8** No signal computation (no RSI computation)
- **V9** No data fetch
- **V10** No network IO
- **V11** No live trading
- **V12** No prior-phase artifact modification (s11-d1 / s12-d1 / parallel s13-d1 sealed artifacts byte-stable)
- **V13** Exactly 3 new files staged this turn: this `docs/` PLAN + 2 `reports/external_research_hunter/` PLAN-sealed pair
- **V14** `lessons.md` unstaged and untouched (preserved across entire session)
- **V15** Load-bearing decisions LOCKED at PLAN: mechanic family F3, RSI period 2, bi-directional, universe MNQ.c.0, IS/OOS windows
- **V16** K9-reachability analysis explicitly included at PLAN time (per L8 framework discipline)
- **V17** Forbidden-tracks list inherited from `0e3f9d49`

---

## 10. HALT conditions

- **H1** If any V-gate fails → HALT
- **H2** If pre-stage git index is non-empty → HALT
- **H3** If staged file count is anything other than 3 at commit time → HALT
- **H4** If staged file paths are anything other than the 3 PLAN files → HALT
- **H5** If `lessons.md` is staged → HALT and `git restore --staged` before retry
- **H6** If any s11-d1 / s12-d1 / parallel s13-d1 sealed artifact is detected as byte-modified → HALT

---

## 11. DA register placeholders (deferred to DRAFT)

The following parameters are NOT locked at PLAN; they will be enumerated at DRAFT as ambiguities DA1–DA14 for operator confirmation at SEAL:

- DA1 RSI period (lock to 2 at DRAFT; alternative 3 or 4 reserved for operator override)
- DA2 RSI entry oversold threshold (default 10; alternatives 5 / 15 / 20)
- DA3 RSI entry overbought threshold (default 90; alternatives 85 / 80 / 75)
- DA4 RSI exit centerline (default 50; alternative 55 / 60)
- DA5 Exit-by-time max bars (default 5; alternative 3 / 7 / 10)
- DA6 ATR period (carry s12-d1 default: Wilder 20)
- DA7 ATR stop multiplier (carry s12-d1 default: 2.0N — but mean-reversion may use tighter stop; DRAFT-level decision)
- DA8 Per-trade risk % (carry s12-d1 default: 1.0% — may revise to 0.5% at DRAFT per cost-density logic; parallel's s13-d1 chose 0.5%)
- DA9 START_CASH_USD (carry s12-d1 default: $100,000 — may revise to $200,000 at DRAFT per turnover-cost logic; parallel's s13-d1 chose $200k)
- DA10 K4 max-drawdown threshold (carry default 0.50)
- DA11 WARMUP_DAYS (RSI(2) requires only ~5 days; framework default 220 carried for cross-candidate consistency)
- DA12 RTH window (carry default `09:30-16:00 ET America/New_York`)
- DA13 DR9 thresholds (carry default `0.95 / 0.30 / 5 / 5`)
- DA14 DR10 thresholds (**elevated prior probability**; may revise at SEAL per RSI(2) turnover characteristics)

---

## 12. Posture (permanent for this candidate)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| Advisory label permanent | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| `verdict_never_means_live_ready` | True |
| `live_promotion_path_closed` | True |
| Six live-trading gates BLOCKED | YES |

---

## 13. Exact next authorization scopes (NONE pre-approved)

This PLAN does NOT authorize DRAFT / SEAL / BUILD / RUN. Each requires a separate fresh operator authorization block.

| Phase | Authorization phrase |
|---|---|
| T1 Tier-N spec DRAFT | `"Authorize T1 RSI MNQ Tier-N spec DRAFT only"` |
| Deferral | `"Defer / Pause T1 track"` |
| Pivot to alternative track | `"Authorize alternative track selection plan revision only"` |

Per the established controller pattern: DRAFT → SEAL (with DA register confirmation) → P1 plan-lock → P2 phase-2 plan → P3 BUILD → P4 SMOKE → P6 IS → (etc).

---

## 14. Anchor seals (byte-stable; not modified by this PLAN)

| Artifact | Seal (first 16) |
|---|---|
| S12-D1 P11 PARK memo (this session) | `321b8940a5516762` |
| S12-D1 P11 PARK memo (parallel canonical) | `b9722d424f6faabe` |
| S12-D1 sealed Tier-N spec (this session) | `422bbbff75f24816` |
| S10-D2 lifecycle park report (this session) | `8d59e94a736aa82d` |
| S10-D2 P11 PARK memo (parallel canonical) | `e121b82b411697c7` |
| Audit-clean MNQ.c.0 CSV | `8b7b832c62fae185` |

---

**T1 RSI MNQ Tier-N spec PLAN authored. Load-bearing decisions LOCKED at PLAN: F3 mechanic family, RSI period 2, bi-directional, universe {MNQ.c.0}, IS/OOS windows. K9-reachability analysis applied at PLAN per L8 discipline. OOS K9 status: BORDERLINE-TO-CLEARING at lower-bound 46/y vs threshold 50/y; central/upper estimates clear. No DRAFT / SEAL / BUILD / RUN authorized. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**
