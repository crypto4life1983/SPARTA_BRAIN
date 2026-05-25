# TRADING MASTER STATE AUDIT

**Generated:** 2026-05-25 (UTC reference frame)
**Scope:** `C:\SPARTA_BRAIN` + `C:\Users\mahmo\obsidian-trade-logger`
**Mode:** `READ_ONLY_AUDIT` — no backtest, no Databento/QC/network, no broker
calls, no live or paper bot control, no `review_queue.json` mutation, no
strategy config mutation, no scheduler changes, no commits, no reopening of
closed/rejected arcs.
**Authority rule:** sealed reports + live state files override brain memory
when they disagree.

> This document is the single page to read before any further trading work.
> It does not authorize anything. Live trading remains `BLOCKED_AT_6_GATES`;
> FRC has never been granted; no strategy is money-proven.

---

## 0 · Repo cleanliness snapshot (pre-write)

| Repo | Branch | Tracked dirty | Untracked dirty | Verdict |
|---|---|---|---|---|
| `C:\SPARTA_BRAIN` | `master` | `brain_memory/logs/system_changes.md` only via `lessons.md` add; otherwise clean of tracked file modification at trading-arc paths | Massive: `external_research_hunter/`, `reports/`, `strategy_lab/data/`, `sparta_commander/`, `research_os/`, `docs/`, `staged/`, `local_secrets/` and the entire `cme_calendar_sources/` HTML mirror — all untracked, no `git add` performed | **DIRTY (untracked-heavy, tracked-clean for trading code paths)** |
| `C:\Users\mahmo\obsidian-trade-logger` | (git repo, default branch not checked) | Many tracked-modified: `bot_core.py`, `config/strategies.json`, `multi_bot.py`, `paper_bot*.py`, `strategies.py`, all four crypto `engine.log` + `_bot.log` + `_heartbeat.txt` + `_bot.pid`, `paper_monitor.log`, `watchdog_stdout.txt`, plus all `reports/*` MD/JSON; deleted `xrp_rbr_*` log family | Many untracked: `analytics/`, `backtest/`, `data/_backups/`, `data/binance_cache/` (large BTC zip cache 2020-2024), `Kraken_Trading_History.zip` (~12.5 GB), `config/{live_config.json,strategy_status.json,watchdog_config.json}`, `data/{GLD,SPX,TLT}_daily.csv` | **DIRTY (heavy live-bot working state)** |

Neither repo was staged or committed during this audit.

---

## 1 · SPARTA_BRAIN trading components — current state

`SPARTA_BRAIN` is the research / governance / advisory side. **It does not
execute orders, place trades, or hold credentials for any broker.** The only
secret-bearing file at the project root is `local_secrets/` (gitignored,
contents not inspected).

### Top-level dirs that touch trading

| Dir | Role | Latest meaningful mtime | Status |
|---|---|---|---|
| `external_research_hunter/` | Candidate diagnostic harness builds (NKE, B005_001, B005_004) | 2026-05-25 (B005_004 packet) | ACTIVE — B005_004 awaiting operator-side QC submit |
| `reports/external_research_hunter/` | Sealed Hunter Brain memos, parking reports, decision memos | 2026-05-25 (`s7_next_candidate_selection_after_five_parks.md`) | AUTHORITATIVE for arc state |
| `reports/research_os/` | SPARTA Research OS `no_trading_change_report_*` brief layer | 2026-05-16 (H1-Auth-4) | ADVISORY_ONLY, paused at H1-Auth-4 |
| `reports/regime_intelligence/` | Shadow Validation infra + Phase 5 closeouts | 2026-05-20 | Phase 5I closed; awaiting Day-7 checkpoint 2026-05-27 |
| `reports/sparta_commander/` | Commander 2.0 internal QA (artifact-drift remediation) | 2026-05-17 | LIVE_TELEGRAM_SAFE; no execution |
| `reports/sparta_research_firm_bridge/` | Firm-bridge design / firewall scaffold | 2026-05-17 (phase 3D closure) | Design-only |
| `reports/tradingagents_reference/` | Static review of `TauricResearch/TradingAgents` | 2026-05-17 | Inspiration only (verdict C) |
| `reports/tradingview_bridge/` (under subdir) | Strategy-lab artifact-drift work | 2026-05-17 | Cleanup-only |
| `reports/strategy_factory/` | Phase-1-5 idea-intake / spec / backtest-readiness for variants | 2026-05-15..16 | Experimental; v2-variant-c-wider-window phase 5 last |
| `strategy_lab/` | Lifecycle / safety / scorecard modules | 2026-05-15 (anti-overfit batch JSONs heavy) | Code-only; 1 paper candidate in PAPER_REVIEW |
| `sparta_commander/` | Hermes-style read-only orchestration code | (cached) | Phases 1-4 + 3.5 QA shipped 2026-05-16 |
| `sparta_research_firm_bridge/` | Firm-bridge code | (cached) | Design-only |
| `sparta_regime_intelligence/` | Regime intelligence code | (cached) | Phase 5 closed |
| `tradingview_bridge/` | TV bridge code + tests | (cached) | Module exists, no recent reports at top level |
| `docs/` | Phase-2 safety contract template; MNQ databento-first workflow | 2026-05-23 (`mnq_databento_first_qc_fallback_workflow.md`) | Plan-only |
| `brain_memory/` | CLAUDE.md-referenced logs | (lessons.md = 2026-05-24; logs polluted) | See §8 for stale-memory warnings |

### Profit Brain (inside SPARTA_BRAIN)

Daily refresh logs in `brain_memory/logs/profit_brain_daily_refresh.log` and
`logs/frozen_stack_daily_evidence_cycle/*/profit_brain_refresh.json` (last
sample 2026-05-22). Status per `reports/sparta_trading_profit_brain_final_status.md`:

- Gate: **RED** (correctly)
- Data quality 65/100; calibrated confidence 37/100
- Unlock requires: ≥20 closed trades, no single symbol >60% of open exposure,
  scheduler RUNNING, valid heartbeats, data quality >70, calibrated confidence >45
- No execution added; no live trading logic changed; external trading repo
  inspected read-only only

### Strategy Lab live state (read from `strategy_lab/data/`)

- `paper_candidate_states.json` (2026-05-19): 1 candidate
  `trend_following_donchian_confirmation` → state **`PAPER_REVIEW`**, reason
  "persistence stress found low-confidence regime instability"
- `paper_arena/paper_arena.json` (2026-05-12): 2 arenas (`cand_01` BTCUSDT
  EXPERIMENTAL; `seed_atr_compression_expansion` SIMULATED_OBSERVATION
  +6.5% / 24 trades)
- `evidence_packs/packs.json` (2026-05-12): 2 packs —
  `seed_atr_compression_expansion` → `ready_for_review`,
  `seed_regime_filter_overlay` → `reject_or_rework`
- `watchlist_approvals/decisions.json`, `review_decisions/decisions.json`,
  `human_review/review_log.json` all dated 2026-05-12

### Approvals ledger

`reports/approvals/approvals.json` shows multiple `EXPIRED` `/revenue` plan
approvals (decided 2026-05-22). No trading-related approvals are active.

---

## 2 · obsidian-trade-logger trading components — current state

This is the **external live/paper trading system**. SPARTA may inspect, but
must not control or mutate it.

### Live execution surface (DANGEROUS — see §9)

| File | Purpose | Mtime |
|---|---|---|
| `bot_core.py` (64 KB) | Multi-bot core scan + decision loop | 2026-05-01 |
| `multi_bot.py`, `multi_bot_alerts.py`, `multi_trade_state.py`, `multi_trade_tracker.py` | Multi-pair orchestration | 2026-04-30 / 2026-04-21 |
| `paper_bot.py` (70 KB) + `paper_bot_eth.py`, `paper_bot_sol.py`, `paper_bot_xrp.py`, `paper_bot_xrp_rbr.py` | Per-pair paper bots | 2026-05-08 |
| `live_bot_xrp_rbr.py` (49 KB) | XRP RBR live bot | 2026-04-21 |
| `kraken_adapter.py`, `mock_kraken_adapter.py`, `paper_kraken_adapter.py` | Kraken broker adapters | 2026-04-19 / 2026-04-20 |
| `execution_orchestrator.py`, `risk_engine.py`, `reconciliation.py`, `state_store.py` | Order/state machinery | 2026-04-19 |
| `watchdog.py`, `auto_go_live.py`, `go_live_check.py` | Liveness + go-live promotion | 2026-04-19..20 |
| `strategies.py` (43 KB) | Strategy library | 2026-04-30 |
| `learning_engine.py`, `learning_worker.py` | Online learning loop | 2026-04-15 / 2026-05-02 |
| `engine_dashboard.py`, `xrp_dashboard.py` | Streamlit dashboards | 2026-04-19 |
| `analyze_performance.py` (108 KB) | Performance analytics | 2026-04-16 |

### Config (live)

| File | Mtime | Key state |
|---|---|---|
| `config/live_config.json` | 2026-04-23 | `account_size=10000`, `risk_pct=0.01`, 12 USDT symbols, run_time `01:00`, `binance_account=2000`, `kraken_account=2000`, `timeout_days=20`, **contains a live Telegram bot token + chat_id (real credentials present in clear)** — see §11 |
| `config/strategies.json` | 2026-04-30 | `LIQ_SWEEP`, `RSI_TREND`, `BRK_RETEST` all `enabled=true`; symbols `[ETH,BTC,SOL,XRP,ADA,LINK,DOT]USD`; `max_open_trades=3`, `risk_pct=0.005`, `initial_balance=2000.0`, strategy priority `[BRK_RETEST, RSI_TREND, LIQ_SWEEP]` |
| `config/strategy_status.json` | 2026-04-29 | All 7 strategies (D, D2, E, E2, F, F2, G) `active=true`, no manual override |
| `config/strategy_decision_config.json` | 2026-05-04 | `mode="SAFE_OBSERVE"`, `min_closed_trades=10`, `min_confidence=60`, `require_positive_expectancy=true`, `block_negative_expectancy=true`, `block_low_confidence=true`, `fallback_allow_when_insufficient_data=true` |
| `config/trade_coordinator_config.json` | 2026-05-04 | `max_open_trades_per_symbol=1`, `block_opposite_direction=true`, `treat_exchanges_as_same_symbol=true` |
| `config/watchdog_config.json` | 2026-05-09 | `manual_stop=false`, `auto_start=true` |
| `config/v2_scorecard_config.json` | 2026-04-30 | `v2_start_ts=2026-04-30T14:30:00Z`; thresholds locked |
| `config/micro_live.env` | 2026-04-20 | (env file, not opened) |

### Heartbeat status (fresh today 2026-05-25)

| Source | Last beat (UTC) | Scan count | Notes |
|---|---|---|---|
| `logs/paper_bot_heartbeat.json` | 2026-05-25T14:03:16Z (PID 31500) | 17 055 | Status `running`; **10 open trades**; `last_loop_duration_seconds=15.51`; no error; pair selection ranks ETH#1, BTC#2, SOL#3, XRP#4 (TREND_DOWN regime for ETH/SOL/XRP); 11 symbols rejected `low volume`; `learning_engine_status=ACTIVE` (last success 2026-05-13T17:47:58Z); `pair_selection_run_count=960` |
| `logs/btc_heartbeat.txt` | 2026-05-25T14:03:16Z | 17 055 | OK |
| `logs/eth_heartbeat.txt` | 2026-05-25T14:00:02Z | 17 050 | OK |
| `logs/sol_heartbeat.txt` | 2026-05-25T13:59:11Z | 17 050 | OK |
| `logs/xrp_heartbeat.txt` | 2026-05-25T14:00:02Z | 17 050 | OK |
| `logs/expansion_event_logger.log` | 2026-05-25T11:01:04 (3.2 MB) | — | Active |
| `logs/evidence_gate_memory.log` | 2026-05-25T10:40:06 | — | Active |
| `logs/health_check.log` | 2026-05-25T07:00:01 | — | Active |
| `logs/strategy_decision_engine.log` | 2026-05-23T01:00:10 (948 KB) | — | Daily cadence |
| `logs/system_b_runner_state.json` | 2026-05-25T00:05:20 | — | Active |
| Pre-breakout observer | 2026-05-11T23:12 | — | **Quiet ~2 weeks** (may be expected) |
| Daily-analysis scheduler heartbeat | 2026-05-11T23:18 | — | **Quiet ~2 weeks — needs verification** |
| Learning worker control | 2026-05-13T21:19 | — | Quiet ~12 days |
| Deleted family | `xrp_rbr_*` (bot.pid, exec.jsonl, heartbeat, live state, paper stdout/heartbeat, trades.csv) | — | Pipeline retired or migrated |

### Performance state (read-only)

- `reports/strategy_performance.json` (2026-05-25T03:05:18 UTC):
  - **7 closed trades / 10 open trades / 0 wins / 6 losses**
  - **win_rate = 0.0**, **profit_factor = 0.0178**, **realized_pnl = −$138.81**
  - **average_r = −0.9913**, **max_drawdown_if_available = −$138.81**
  - Symbols active: ADA, ARB, AVAX, BNB, ETH, XRP USDT
  - Strategies tagged: D, D2, E, E2, F, F2, G
- Recent diagnostic reports present: `reports/exit_path_root_cause.{md,json}`,
  `reports/open_trade_exit_review.{md,json}` (root-cause work on exits)

### Independent paper trackers

- `reports/nq_paper_orb/latest.md` (report 2026-05-24, last data 2026-05-18):
  - Status: **PAUSE**
  - 4/60 trading days, 4/40 trades (3 long / 1 short), paper equity $50,860.50, net PnL +$860.50, max DD −0.32%
  - **CRITICAL alert active: `DATA_MISSING_CURRENT_SESSION` — last data 124.1 h old (>48 h threshold)**
  - Launch spec hash = current spec hash = `7707dee46cbf89f1` (no spec drift)
- `reports/paper_funding_carry/latest.md` (report 2026-05-25, fresh):
  - Status: **ON TRACK** — 12/90 days, paper equity $9,973.38, max DD −0.01%, no alerts
  - Funding net since inception +$3.80; cost consumption 584.2 % of gross funding (small denominator)
  - Theoretical positions ~24 % each in BTC/ETH/SOL/XRP USDT perp basket
- `nq_paper_tracker/` modules: `pipeline.py`, `alerts.py`, `spec.py` (2026-05-13 to 2026-05-16)
- `paper_tracker/` modules (general): freshness + alerts (2026-05-13)

### docs (authoritative human-gated path)

- `docs/observation_mode/path_to_live_decision.md` (2026-05-19) is the
  single load-bearing reference for the two paper-to-live tracks:
  - **Track A — Crypto funding carry `always_on_monthly`:** launched
    2026-05-13; Day-30 informal 2026-06-12; **Day-90 graduation 2026-08-11**.
    Anchors: CAGR +8.18 % (band +5.7 %…+10.6 %), worst DD −1.22 %
    (ceiling better than −3.7 %). Needs ≥90 calendar days, no unresolved
    CRITICAL, written human go-live sign-off.
  - **Track B — NQ ORB `MNQ_risk_$500`:** launched 2026-05-13; needs
    **60+ trading days AND ≥40 fired trades**, ≥10 long AND ≥10 short,
    realized positive after costs, MaxDD <15 %, worst day better than −5 %,
    no unresolved CRITICAL, written human sign-off. Anchors (Phase 11C):
    3-yr OOS +$24 416 (~14 % CAGR/$50 k), worst DD −13.11 %, mean Sharpe 1.02,
    WR ~46 %.
  - Earliest realistic live test: **NOT before 2026-08-11 (crypto) or NQ
    60d/40t gate**, then small loss-capped test only.

### Recent observation-mode reports

- `observation_mode/nq_refresh_cycle1_modelM_report.md` (2026-05-19) —
  Cycle 1 Model-M refresh done
- `observation_mode/nq_seam_validator_fix_complete_and_hold.md` (2026-05-18)
- `observation_mode/sr_*.md` (2026-05-16) — Step-5A research-arc separation memo

---

## 3 · Arc-by-arc status

Status legend: `ACTIVE` · `REJECTED` (sealed, do not revive) · `PARKED`
(sealed evidence chain, may inform future direction but not revived) ·
`PAUSED` · `BLOCKED` · `CLOSED` · `OBSERVATION_ONLY` · `NEEDS_VERIFICATION`.

| # | Arc | Status | Best known result | Why this status | Authoritative file |
|---|---|---|---|---|---|
| 1 | **NKE Options Wheel** | **REJECTED** (`REJECT_TIER1` / sealed REJECT_FAST under DR2) | OOS S1×S3 stress NLV **−$4,872,698.15** vs $50 k threshold; observed OOS NLV +$103 046 (sign-divergence due to first-order assignment accounting bias) | Stress-cell fail; operator declined runner v2, diagnostic rerun, and all rescue attempts. Source: Chocksy gist Wheel; code-grounded but failed stress. | `brain_memory/projects/trading_bot/lessons.md` + `external_research_hunter/HUNTER_BRAIN_LESSONS.md` LESSON_HUNTER_001..008 |
| 2 | **B005_001 — QC Intraday ETF Momentum (Gao Han Li Zhou 2017)** | **REJECTED / ARCHIVED_REJECT_FAST** | OOS Sharpe S0=+0.189 → S3=−3.663 (zero-cost survival only); DR2, DR3, DR5 fired | Cost-stress-dominant fragility; reinforces LESSON_HUNTER_001; "candidate should not be reactivated unless separately authorized" | `reports/external_research_hunter/b005_001_archival_memo.md` (seal `2912b97d…`) |
| 3 | **B005_004 — QC Stocks on the Move / Clenow** | **ACTIVE** — operator-execution-prep packet ready; awaiting operator-side LEAN/QC submit | No result yet (no QC run from this session — operator-side execution only) | Hunter Brain selected B005_004 as next candidate (S7 selection memo enumerates HELD/queued Batch_005 set). Live `execution_guard.py` and guard test sha DIVERGE from sealed-chain sha — flagged in packet for operator pre-flight reconciliation. | `reports/external_research_hunter/b005_004_operator_execution_preparation_report.md` (seal `19dc6cfe…`) |
| 4 | **s2 NKE Options Wheel (parking-tier framing)** | **PARKED** | (same as #1, framed as the first of seven parks) | Single-symbol equity options — inadequate sample + mixed safety footprint | `s5_parking_report` / `s7_next_candidate_selection_after_five_parks.md` |
| 5 | **s3 MNQ Daily Range Breakout** | **PARKED** (seal `1f557888…`) | Insufficient sample + safety issues; no money-proven result | Single-market daily-breakout without trend-confirmation lacks structural edge | `reports/external_research_hunter/s6_…parking_report.md` (parents table) |
| 6 | **s4 Turtle System 1 NQ.c.0 (filter on)** | **PARKED** (seal `8cda3ca6…`) | Only 20 closed trades in 10 years → K9 (insufficient sample) + negative expectancy | Filter aggressively skipped trades; sample bottleneck | s7 selection memo §s4 |
| 7 | **s5 Donchian no-filter NQ.c.0** | **PARKED_SAFE_BUT_NOT_MONEY_PROVEN** (seal `6c308b42…`) | 64 trades, net **−$5,958.69** MNQ-equiv, WR 15.62 %, P/L 5.18, MaxDD 38.61 %, breakeven WR 16.18 % → gap −0.56 pp | Sample bottleneck cleared vs s4, but single-market WR 0.56 pp short of breakeven; K1+K2 fired marginally | s7 selection memo §s5 |
| 8 | **s6 Multi-market Donchian no-filter (NQ + ES + YM)** | **PARKED_SAFE_BUT_NOT_MONEY_PROVEN** (seal `f6953c1f…`) | 191 trades, net **−$63,328.49** MNQ-equiv, WR 14.66 %, P/L 4.68, MaxDD 123.48 %, breakeven WR 17.62 % → gap −2.96 pp. Per-market: ES −$64 286 (dominated loss); NQ −$4 865; YM +$5 823 (only profitable) | Same-family 3-market diversification (~0.88 avg pairwise correlation) FALSIFIED as a path to breakeven; pyramid amplification + ES friction dominated; K11 false positive resolved (cap-binding-events 2730→0 after PortfolioCapTracker bugfix) | `reports/external_research_hunter/s6_multi_market_donchian_no_filter_PARKING_REPORT.md` |
| 9 | **s7 Next-candidate selection plan** | **SEALED PLAN (no candidate instantiated yet)** (seal `8d8851bc…`, 2026-05-25T13:29:44Z) | Recommends **D1 — Cross-asset Donchian no-filter (NQ + GC + ZN + CL)** at 28/40; D2 (no-pyramid) tied at 28/40 as data-cheaper fallback; **D5 (YM-only) explicitly RECOMMENDED AGAINST** as overfit trap | All 5 parking reports + Phase-2 safety template byte-stable; operator owns final s7 direction; D1 needs 3 fresh Databento downloads (GC, ZN, CL) | `reports/external_research_hunter/s7_next_candidate_selection_after_five_parks.md` |
| 10 | **Multi-strategy crypto paper bot (D / D2 / E / E2 / F / F2 / G)** | **ACTIVE (paper) — OBSERVATION_ONLY** | 7 closed trades, 0 wins, realized **−$138.81**, avg R −0.99, profit_factor 0.018; 10 open trades; SAFE_OBSERVE mode | Live in paper, fresh heartbeats, but performance is unambiguously negative; concentration concern (per Profit Brain: XRP 5/5 open exposure earlier) | `reports/strategy_performance.json` + `logs/paper_bot_heartbeat.json` + `config/strategies.json` |
| 11 | **NQ ORB MNQ_risk_$500 (Track B)** | **PAUSED** (CRITICAL data alert) | 4/60 days, 4/40 trades, +$860.50, max DD −0.32 %, WR 75 % (tiny sample) | CRITICAL `DATA_MISSING_CURRENT_SESSION` — last data 124 h old; cannot graduate until cleared | `reports/nq_paper_orb/latest.{md,json}` |
| 12 | **Crypto funding carry `always_on_monthly` (Track A)** | **ACTIVE (paper) — ON TRACK** | 12/90 days, paper equity $9,973.38, max DD −0.01 %, no alerts; funding net +$3.80 vs costs $30 → cost-consumption 584 % (denominator small at 12d) | Path-to-live gate Day-90 = 2026-08-11; needs CAGR within ±30 % of +8.18 %, worst DD better than −3.7 % | `reports/paper_funding_carry/latest.{md,json}` |
| 13 | **Crypto / regime intelligence (SPARTA Regime Intelligence + Shadow Validator)** | **OBSERVATION_ONLY** — Tier-1 DIAGNOSTIC_ONLY / NOT_PROMOTABLE | Phase 5C/5E/5F/5FGH/5I closed 2026-05-20; 204 tests passing; 2025 historical replay 1d/3d/7d theo-vs-bench diffs −0.10 % to −0.13 % (diagnostic) | Pre-committed Shadow Validation Decision Contract with 5 checkpoints; **Day 7 = 2026-05-27**; verdicts strictly `CONTINUE`/`FIX_INFRASTRUCTURE`/`REDESIGN_SIGNAL`/`ARCHIVE_RESEARCH`/`READY_FOR_PAPER_SIMULATION_DESIGN`. No checkpoint can trigger live trading. | `reports/regime_intelligence/SPARTA_SHADOW_VALIDATION_DECISION_CONTRACT_20260520T234945Z.md` |
| 14 | **TradingAgents inspiration** | **CLOSED — inspiration only (verdict C)** | Static review of repo @ commit `61522e1`; no execution path exists in the repo itself | Epistemic/governance risk (non-frozen data, ungated reflection loop, signal-shaped output); not to be integrated; firm-topology only borrowed via SPARTA Research Firm Bridge | `reports/tradingagents_reference/tradingagents_sparta_architecture_review_correction_addendum.md` |
| 15 | **TradingView bridge** | **NEEDS_VERIFICATION** | Code dir `tradingview_bridge/` with tests exists; no recent top-level reports in `reports/tradingview_bridge/`; only artifact-drift remediation reports under `reports/sparta_commander/` reference it | Module health, current role, and whether it's wired into anything live not verified in this audit | `tradingview_bridge/` (code) |
| 16 | **Profit Brain (SPARTA Commander module)** | **BLOCKED — waiting** (gate RED, correctly) | Test suite 404 passing; data quality 65/100; calibrated confidence 37/100 | Unlock requires ≥20 closed trades, no single symbol >60 % open, scheduler RUNNING, valid heartbeats, data quality >70, confidence >45; safety: no execution added | `reports/sparta_trading_profit_brain_final_status.md` |
| 17 | **Strategy Factory** | **ACTIVE (experimental)** | Phase-1-5 outputs through `v2-variant-c-wider-window` (block_idea draft + d5d manual review summary) and earlier baseline / variant_a / variant_b composite reviews | Pure research pipeline; no candidate has been promoted past phase 5 block_idea; experimental | `reports/strategy_factory/` |
| 18 | **SPARTA Commander 2.0** | **ACTIVE — LIVE_TELEGRAM_SAFE** (Phases 1-4 + 3.5 QA shipped 2026-05-16) | Real Telegram bot via single hardened transport boundary; token only in gitignored `local_secrets/`; manual start; mobile-friendly reply formatting | No execution layer for trades; action-execution of approvals NOT built (verifier-gated) | `MEMORY.md` index entry; `reports/sparta_commander/strategy_lab_artifact_drift_remediation.md` |
| 19 | **SPARTA Research Firm Bridge** | **DESIGN-ONLY** | Phase 3D closure 2026-05-17 (firewall scaffold, permission template, dry-read, closure) | Read-only design; not built into the trading bot; no broker access | `reports/sparta_research_firm_bridge/phase3d_closure.md` |
| 20 | **SPARTA Research OS (Hermes-style ADVISORY_ONLY brief layer)** | **ACTIVE (advisory)** | H1-Auth-4 unit tests 48/48 pass for the multi-asset perpetual funding engine; no `simulate_primary` on real data yet | All `no_trading_change_report_*` reports confirm zero trading-state mutation; Phase 1 shipped 2026-05-13 | `reports/research_os/no_trading_change_report_h1_auth4.md` |

### What about the explicitly-listed-but-effectively-merged arcs

- **ORB** = Track B above (NQ ORB MNQ_risk_$500). PAUSED on data alert.
- **Donchian** = s5/s6/s7 chain above. PARKED + selection plan for s7.
- **NQ/MNQ** = same chain (s3 MNQ DRB parked; s5/s6 NQ Donchian parked;
  Track B NQ ORB paused). MNQ databento-first workflow is `docs/`-only plan.
- **QQQ** = not surfaced as a SPARTA arc. The closest equity-side work is
  **B005_001 (Intraday ETF Momentum on QQQ-class ETFs)** → REJECTED.
  No separate QQQ arc is alive.
- **B005_001** in the brief is **REJECTED** (#2 above).

---

## 4 · Best known result per arc

(Already inlined in §3. The single-sentence summary: **no arc has produced a
money-proven result.** The only positive paper readings are the 4-trade,
4-day NQ ORB tracker (+$860.50, currently PAUSED on data alert) and the
12-day funding-carry paper basket (+$3.80 funding net, ON TRACK, cost-
consumption 584 % at small denominator). Everything else is sealed
parking/rejection or in early observation.)

---

## 5 · Which files are authoritative

When sealed reports and brain memory disagree, the sealed report wins.

| Topic | Authoritative file(s) |
|---|---|
| NKE rejection | `external_research_hunter/HUNTER_BRAIN_LESSONS.md` (LESSON_HUNTER_001..008) + `brain_memory/projects/trading_bot/lessons.md` |
| B005_001 rejection | `reports/external_research_hunter/b005_001_archival_memo.{md,json}` |
| B005_004 active spec/build | `reports/external_research_hunter/b005_004_operator_execution_preparation_{report,packet}.{md,json}` + `external_research_hunter/b005_004_stocks_on_the_move_diagnostic_runner/` |
| s2-s6 parks | `reports/external_research_hunter/s{3,4,5,6}_*PARKING_REPORT.{md,json}` + `s{N}_*decision_memo.{md,json}` |
| s7 plan | `reports/external_research_hunter/s7_next_candidate_selection_after_five_parks.{md,json}` |
| Path to live | `obsidian-trade-logger/docs/observation_mode/path_to_live_decision.md` |
| NQ ORB tracker state | `obsidian-trade-logger/reports/nq_paper_orb/latest.{md,json}` |
| Funding carry tracker state | `obsidian-trade-logger/reports/paper_funding_carry/latest.{md,json}` |
| Live multi-bot heartbeats | `obsidian-trade-logger/logs/paper_bot_heartbeat.json` + per-pair `*_heartbeat.txt` |
| Live multi-bot config | `obsidian-trade-logger/config/{live_config,strategies,strategy_status,strategy_decision_config,trade_coordinator_config,watchdog_config,v2_scorecard_config}.json` |
| Live multi-bot performance | `obsidian-trade-logger/reports/strategy_performance.json` + `exit_path_root_cause.{md,json}` + `open_trade_exit_review.{md,json}` |
| Shadow Validation contract | `reports/regime_intelligence/SPARTA_SHADOW_VALIDATION_DECISION_CONTRACT_20260520T234945Z.md` |
| Profit Brain status | `reports/sparta_trading_profit_brain_final_status.md` + `reports/profit_brain_*.{md,json}` |
| MNQ databento workflow plan | `docs/mnq_databento_first_qc_fallback_workflow.md` |
| Commander 2.0 LIVE_TELEGRAM_SAFE | `MEMORY.md` index + `reports/sparta_commander/strategy_lab_artifact_drift_remediation.md` |
| TradingAgents verdict | `reports/tradingagents_reference/tradingagents_sparta_architecture_review_correction_addendum.md` |

---

## 6 · Stale / suspect memory and docs

**These should not be treated as truth without re-verification:**

- `CLAUDE.md` (`C:\SPARTA_BRAIN\CLAUDE.md`) references brain-memory files
  that **do not exist**: `brain_memory/identity.md`,
  `brain_memory/operating_rules.md`,
  `brain_memory/projects/trading_bot/project.md`,
  `brain_memory/projects/trading_bot/decisions.md`,
  `brain_memory/projects/trading_bot/next_actions.md`,
  and all `hydra_video/`, `youtube_growth/`, `affiliate_system/`
  equivalents. Only `brain_memory/projects/trading_bot/lessons.md` exists
  (single entry, accurate, NKE REJECT_TIER1).
- `brain_memory/logs/daily_wrapups.md` (3 313 lines) and
  `brain_memory/logs/decision_log.md` (2 379 lines) and
  `brain_memory/logs/system_changes.md` are **dominated by pytest marker
  entries** (`"pytest decision marker: keep trading logic untouched"`,
  `"pytest daily wrapup marker"`, etc.) — useless as project memory; do
  not mine for state.
- `MEMORY.md` (auto-memory index) is **truncated at 32.9 KB > 24.4 KB
  limit** and its newest pointer is Commander 2.0 / Research OS Phase 1
  (2026-05-13/16). It does NOT cover: B005_001 archival, B005_004 active,
  s5/s6 parks, s7 plan, the Profit Brain gate RED state, the NQ ORB
  PAUSE alert, or the 0/6 live-paper W/L pattern.
- `brain_memory/projects/trading_bot/project.md.20260505_001150.external-source.bak`
  is a `.bak` of a file that no longer exists.
- The `tradingagents_sparta_architecture_review__v1_web_only_superseded.md`
  is marked superseded; only the `_correction_addendum.md` and the
  canonical `tradingagents_sparta_architecture_review.md` should be cited.

---

## 7 · Safe / read-only vs dangerous / live-control surfaces

### Safe / read-only (touch freely under read-only audit)

- All of `C:\SPARTA_BRAIN\reports/**` (sealed-style governance)
- `C:\SPARTA_BRAIN\external_research_hunter/**` (harness code, runners, guards — code only, not invoked here)
- `C:\SPARTA_BRAIN\strategy_lab/**` (lifecycle/safety/scorecard code + experimental data)
- `C:\SPARTA_BRAIN\sparta_commander/**` (orchestration code; no broker calls)
- `C:\SPARTA_BRAIN\research_os/**` (advisory brief code)
- `C:\SPARTA_BRAIN\sparta_research_firm_bridge/**` (design-only code)
- `C:\SPARTA_BRAIN\sparta_regime_intelligence/**` + shadow-validation reports
- `C:\SPARTA_BRAIN\tradingview_bridge/**` (code + tests; current wiring not verified — see §3 #15)
- `C:\SPARTA_BRAIN\docs/**` (plan documents only)
- `obsidian-trade-logger/reports/**`, `obsidian-trade-logger/docs/**`,
  `obsidian-trade-logger/research/**` (research-only, files only)

### Dangerous / live-control (DO NOT touch without explicit, scoped human authorization)

- `obsidian-trade-logger/config/live_config.json` — **contains real Telegram
  bot token + chat_id in clear**. Do not re-print the token. The file should
  be migrated into a gitignored secret store at next safe opportunity (this
  audit performs no migration).
- `obsidian-trade-logger/config/{strategies,strategy_status,strategy_decision_config,trade_coordinator_config,watchdog_config,v2_scorecard_config}.json` — alter strategy parameters / liveness; do not mutate
- `obsidian-trade-logger/bot_core.py`, `multi_bot.py`, `paper_bot*.py`,
  `live_bot_xrp_rbr.py`, `execution_orchestrator.py`,
  `kraken_adapter.py`, `risk_engine.py`, `reconciliation.py`,
  `state_store.py`, `watchdog.py`, `auto_go_live.py`, `go_live_check.py`,
  `strategies.py`, `learning_engine.py`, `learning_worker.py`
- All `logs/*.pid`, `logs/*_heartbeat.txt`, `logs/paper_bot_heartbeat.json`
  (modifying a heartbeat lies to the watchdog)
- The whole `obsidian-trade-logger/data/binance_cache/` zip cache (slow to
  rebuild; treat as cold storage)
- `obsidian-trade-logger/Kraken_Trading_History.zip` (~12.5 GB; cold archive)
- `obsidian-trade-logger/.streamlit/`, `obsidian-trade-logger/staging/`
- Any `review_queue.json` in either repo
- SPARTA's `config/strategies.json`, scheduler files, anything in
  `C:\SPARTA_BRAIN\local_secrets/`

---

## 8 · Bot / dashboard / heartbeat / scheduler status from `obsidian-trade-logger`

| Component | Status today (2026-05-25) | Source |
|---|---|---|
| Multi-pair paper scanner (PID 31500) | **RUNNING**, scan 17 055, 10 open trades, no last_error, last loop 15.5 s | `logs/paper_bot_heartbeat.json` |
| BTC heartbeat | **FRESH** (14:03 UTC) | `logs/btc_heartbeat.txt` |
| ETH heartbeat | **FRESH** (14:00 UTC) | `logs/eth_heartbeat.txt` |
| SOL heartbeat | **FRESH** (13:59 UTC) | `logs/sol_heartbeat.txt` |
| XRP heartbeat | **FRESH** (14:00 UTC) | `logs/xrp_heartbeat.txt` |
| Multi-bot watchdog | Last state 2026-05-13T19:50 (state.json + .log) — **STALE ~12 days; needs verification** | `logs/multi_bot_watchdog_*` |
| Learning worker | Last activity 2026-05-13T21:19 — **STALE ~12 days**; heartbeat 2026-05-11T23:19 — **STALE ~14 days** | `logs/learning_worker_*` |
| Pre-breakout observer | Last 2026-05-11T23:12 — **STALE ~14 days** | `logs/pre_breakout_*` |
| Daily-analysis scheduler | Heartbeat 2026-05-11T23:18 — **STALE ~14 days** | `logs/daily_analysis_scheduler_heartbeat.json` |
| Strategy decision engine | Last 2026-05-23T01:00 — **2 days ago** (daily cadence) | `logs/strategy_decision_engine.log` |
| Trade coordinator | Last 2026-05-20T00:05 — **5 days ago** | `logs/trade_coordinator.log` |
| System-B runner | Last 2026-05-25T00:05 — **FRESH (~14 h)** | `logs/system_b_runner_*` |
| Live signals log | Last 2026-05-25T01:00 — **FRESH** | `logs/live_signals.log` |
| NQ ORB tracker | **PAUSE** (CRITICAL: 124 h stale data) | `reports/nq_paper_orb/latest.{md,json}` |
| Funding carry tracker | **ON TRACK** (fresh) | `reports/paper_funding_carry/latest.{md,json}` |
| XRP RBR live + paper family | **REMOVED** (logs deleted in git working tree) | (deleted: `logs/xrp_rbr_*`) |
| `engine_dashboard.py`, `xrp_dashboard.py` | Code present; runtime status not verified in this audit | — |
| Telegram bridge | Hardcoded in `config/live_config.json` (token + chat_id); runtime status not verified | — |

---

## 9 · Data availability and data risks

### Available locally (no fresh fetch needed)

- `C:\SPARTA_BRAIN\data\_backups\nq_5m_2020-01-01_2026-04-18.csv` and
  `nq_5m_2020-01-01_2026-05-15.csv`
- `obsidian-trade-logger\data\binance_cache\BTCUSDT_1m\` — monthly zip
  archives 2020-01 → 2024-11 (cached; 60+ months)
- `obsidian-trade-logger\data\{GLD,SPX,TLT}_daily.csv`
- `obsidian-trade-logger\data\atr_calibration_report.json` +
  `adaptive_atr_shadow*` data
- Per-pair execution data: `data/{btc,eth,sol,xrp}/engine_state.json` +
  `engine.log` + `trades.jsonl` (all tracked-modified)

### Cached / cold

- `obsidian-trade-logger\Kraken_Trading_History.zip` — **~12.5 GB**;
  treat as archival cold storage (rebuilding is slow)

### NOT cached (fresh download would be required)

- For s7-D1 (cross-asset Donchian): **GC**, **ZN**, **CL** — `databento`
  fetches required
- For s7-D4 (E-mini micros): MNQ, MES, MYM, M2K — 4 fresh fetches
- B005_004 universe: depends on the spec (QC-side data; not Databento)
- TLT/GLD/SPX intraday — only daily present locally

### Data risks

- **NQ ORB tracker CRITICAL**: last data 2026-05-18T19:55 UTC → 124.1 h
  stale (>48 h). Tracker is in `PAUSE`. Must be cleared before next
  Model-M cycle is meaningful. **Do not "refresh" by mutating tracker
  state — fix the upstream feed.**
- **Databento billing risk**: the workflow plan at
  `docs/mnq_databento_first_qc_fallback_workflow.md` explicitly bans
  printing/echoing `DATABENTO_API_KEY`; the key must be read via
  `os.environ.get("DATABENTO_API_KEY")` only. Cost: metadata calls are
  free; full bar downloads have non-zero cost (e.g., 3 fresh
  cross-asset roots for s7-D1).
- **QuantConnect / QC Cloud risk**: B005_004 runner is QC-side; running
  consumes operator QC compute / cloud quota. This session must NOT
  trigger a QC submit. Operator-side submit only.
- **Kraken / broker API risk**: live config has a live Telegram bot token
  in clear and `live_config.json` references `binance_account=2000` +
  `kraken_account=2000`. The audit did **not** inspect any actual API
  keys for Kraken / Binance, but their presence on this machine is
  implied. Do not exfiltrate, log, or print these.
- **Telegram token in cleartext config** (see §11) — already deployed in a
  process; rotating it is a separate operator action, not an audit step.
- **`expansion_event_logger.log` 3.2 MB**, `evidence_gate_memory.log`
  849 KB — disk-growth risk on the live machine; not a correctness risk.

---

## 10 · Exact next recommended candidate / diagnostic

**Recommended next candidate (SPARTA research side):**

- `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl` — direction **D1** from
  the sealed `s7_next_candidate_selection_after_five_parks.md` plan
  (seal `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`).
  Same locked Donchian mechanics (55-d entry / 20-d exit / 2N stop / 4-unit
  pyramid / 0.5N spacing / 1 % portfolio sizing / NO filter), four
  Faith-distinct families: NQ (equity index, cached 127 files) + GC (metals)
  + ZN (10-y note) + CL (energy). Tests the **unfixed** s6 hypothesis that
  cross-family (correlations <0.5) diversification can lift the no-filter
  Donchian above breakeven.

- **Fallback** if Databento downloads are blocked: `s7-no-pyramid-donchian-nq-es-ym`
  (direction **D2**, also 28/40) on cached NQ+ES+YM with `max_units=1`.

- **Explicit AGAINST**: D5 (YM-only) — survivorship/cherry-pick overfit
  trap.

**Next diagnostic action (operator-only, not Claude-side):**

- Submit B005_004 (QC Stocks on the Move / Clenow) via the prepared
  operator-execution packet. **Pre-flight step 2** of the packet must
  reconcile the live-vs-recorded sha drift on
  `b005_004_stocks_on_the_move_diagnostic_runner/execution_guard.py` and
  its test file (the live shas differ from the sealed-chain shas; either
  confirm the post-seal modification is intentional or restore to the
  recorded sha before submit).

**Next diagnostic for the live paper bot:**

- Run the existing `reports/exit_path_root_cause.{md,json}` +
  `reports/open_trade_exit_review.{md,json}` already-written diagnostics
  against the current 7-closed / 0-win record and read out what the
  exit-path root cause says BEFORE any parameter change. The 0/6 W/L,
  −0.99 avg-R signature is a clear "fix exits" pattern, not a "find a new
  strategy" pattern.

---

## 11 · Exact next 3 actions

1. **Operator decision on s7 direction.** Read the sealed plan
   `reports/external_research_hunter/s7_next_candidate_selection_after_five_parks.md`
   and either (a) authorize a fresh `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl`
   Tier-N spec DRAFT (PLAN-only, no code yet), or (b) authorize the D2
   fallback. **Do not** authorize D5. Until this happens, the Hunter Brain
   loop is idle.

2. **Clear the NQ ORB tracker `DATA_MISSING_CURRENT_SESSION` CRITICAL
   alert at its source.** Identify why the NQ minute feed has been stale
   for 124 h (since 2026-05-18T19:55 UTC) and restore freshness via the
   upstream fetcher. Do not advance the Model-M cycle to cycle 2 until
   the alert clears — the path-to-live rule treats unresolved CRITICAL
   as a graduation blocker. (Per `path_to_live_decision.md`, data
   outages resolved in <24 h are OK; we are well past that.)

3. **Investigate the live multi-bot 0/6 W/L pattern before any sizing
   or strategy-set change.** The exit-path-root-cause and open-trade
   exit-review JSON/MD reports are already written; read them, then
   confirm the Profit Brain decision-gate stays RED (it should — closed
   trades <20, data quality 65, calibrated confidence 37). Confirm
   the secondary heartbeats that have been stale ~12-14 days
   (`multi_bot_watchdog`, `learning_worker`, `pre_breakout_observer`,
   `daily_analysis_scheduler`) are intentionally quiet vs unintentionally
   dead. If unintentional, the watchdog itself may be wedged.

(Concurrent operator-side action that is NOT one of the three:
rotate the Telegram bot token currently sitting in clear at
`obsidian-trade-logger/config/live_config.json` and move it to the
gitignored secret store. This is a discrete security maintenance task
operator owns; this audit performs none of it.)

---

## 12 · What NOT to do next

- **Do not** re-open NKE Options Wheel, B005_001, s2 (NKE-as-park-tier),
  s3 (MNQ DRB), s4 (Turtle NQ), s5 (Donchian NQ), or s6 (Multi-market
  NQ+ES+YM). All are sealed; "candidate should not be reactivated unless
  separately authorized."
- **Do not** select direction D5 (YM-only follow-up) — explicitly
  recommended AGAINST as a textbook overfit trap in the sealed s7 plan.
- **Do not** promote any candidate to live trading. Live remains
  `BLOCKED_AT_6_GATES`; FRC has never been granted; the diagnostic-only
  permanent label stands.
- **Do not** modify any sealed artifact, any `*_PARKING_REPORT.{md,json}`,
  any `*_archival_memo.{md,json}`, any `s{N}_*decision_memo.{md,json}`,
  any `phase2_safety_template.*`, the s7 plan, or any byte-stable parent.
- **Do not** mutate `obsidian-trade-logger/config/strategies.json`,
  `strategy_status.json`, `strategy_decision_config.json`,
  `trade_coordinator_config.json`, `watchdog_config.json`, or
  `v2_scorecard_config.json` to silence the 0/6 W/L pattern.
- **Do not** mutate `review_queue.json` in either repo.
- **Do not** change the scheduler, the watchdog, or any per-pair bot PID/heartbeat.
- **Do not** call Databento, QuantConnect, Kraken, Binance, Yahoo,
  Alpha Vantage, Reddit, Stocktwits, or any other network endpoint from
  this Claude session. Databento metadata calls cost ~zero but still
  count as a network call against the locked boundary.
- **Do not** run any backtest in this session. Backtests live in QC or
  in the local engine; either way they are operator-side actions outside
  this audit's scope.
- **Do not** echo, log, or quote the Telegram bot token from
  `live_config.json` (it has been observed; do not propagate).
- **Do not** "refresh" the NQ ORB tracker by mutating tracker state to
  hide the CRITICAL alert. The alert is correctly firing; the fix is
  upstream.
- **Do not** rescue a parked or rejected candidate by patching its
  diagnostic harness (LESSON_HUNTER_001 — candidate fragility is itself
  a signal).
- **Do not** trust `brain_memory/logs/decision_log.md`,
  `daily_wrapups.md`, or `system_changes.md` as project state — they are
  pytest-marker polluted (see §6).
- **Do not** rely on CLAUDE.md's `Always read` paths (most don't exist).
- **Do not** treat the 4-trade NQ ORB +$860.50 or the 12-day funding
  carry +$3.80 as edge — both are far too small a sample to be evidence
  per the path-to-live rules.
- **Do not** commit, push, or tag any branch as part of this audit.

---

## Appendix A · Top of Hunter Brain lesson chain (for ready reference)

- `LESSON_HUNTER_001` — Candidate-fragility-as-signal (NKE).
- `LESSON_HUNTER_002` — Stress-matrix first-order approximation pitfalls (net
  assignment fills against parent option premium before stress summation).
- `LESSON_HUNTER_003` — Assignment classification symbol drift (don't depend
  on transient trackers cleared before `OnAssignmentOrderEvent`).
- `LESSON_HUNTER_004` — Harness self-seal canonical roundtrip (canonical
  JSON roundtrip before sealing so external recompute matches).
- `LESSON_HUNTER_005` — QC `OptionPriceModels` compatibility (use fail-soft
  selector ladder; record chosen factory).
- `LESSON_HUNTER_006` — Namespace ambiguity surfaces late (enumerate
  competing artifacts at the very first readiness check).
- `LESSON_HUNTER_007` — Stress cell vs observed NLV divergence (preregistered
  rule fires; divergence is information, not a basis for override).
- `LESSON_HUNTER_008` — Source priority (code-grounded > paper > video, but
  source quality is a start-confidence, not a finish-grade).

## Appendix B · Six gates blocking live (from sealed memos)

The phrase `BLOCKED_AT_6_GATES` recurs in every sealed Hunter Brain memo.
The six gates are (composite from the chained reports): preregistered Tier-N
spec sealed; runner + execution_guard sealed; safety / data quality clean;
in-sample passes locked K-criteria; OOS passes locked K-criteria; written
human go-live sign-off with size, daily/weekly loss limits, and kill
criteria. No arc has cleared even the in-sample K-criteria gate. FRC
("full-risk capital" / formal-readiness-to-commit) has never been granted.

## Appendix C · Authorities cited

- `obsidian-trade-logger/docs/observation_mode/path_to_live_decision.md`
- `reports/external_research_hunter/HUNTER_BRAIN_LESSONS.md`
- `reports/external_research_hunter/b005_001_archival_memo.md`
- `reports/external_research_hunter/b005_004_operator_execution_preparation_report.md`
- `reports/external_research_hunter/s6_multi_market_donchian_no_filter_PARKING_REPORT.md`
- `reports/external_research_hunter/s7_next_candidate_selection_after_five_parks.md`
- `reports/regime_intelligence/SPARTA_SHADOW_VALIDATION_DECISION_CONTRACT_20260520T234945Z.md`
- `reports/sparta_trading_profit_brain_final_status.md`
- `reports/tradingagents_reference/tradingagents_sparta_architecture_review_correction_addendum.md`
- `reports/strategy_performance.json` (obsidian)
- `reports/nq_paper_orb/latest.{md,json}` (obsidian)
- `reports/paper_funding_carry/latest.{md,json}` (obsidian)
- `logs/paper_bot_heartbeat.json` (obsidian)
- `brain_memory/projects/trading_bot/lessons.md`

---

*End of TRADING_MASTER_STATE_AUDIT. Read-only audit; no other file was
modified during its creation.*
