# Crypto-D1 — Research Lane Protocol (protocol / memo only)

**This is a protocol memo. No crypto data fetch, no code, no backtest, no IS/OOS
run, no optimization, no parameter sweep, no strategy test, no exchange API, no
broker, no paper/live, no futures-branch changes, no JARVIS/templates/base.html/
hydra changes, no staging, no commit.** It defines the standing rules for a new,
separate crypto research lane that runs under the already-completed validation
factory.

- **Created:** 2026-05-30
- **HEAD at memo:** `73e1cb0` (descendant of the S29-D4 decision-record commit
  `9d5b9d8`; factory tree clean; only the untracked `crypto_d1_research_lane_protocol/`
  and `s30_d1` report dirs present; nothing staged).
- **Read-only context:** Factory-D11 closeout (validation ladder is complete and is
  the current standard); S30-D1 idea-source review (top-winner-dependence is the
  universal killer); CLAUDE.md SPARTA read-only default; brain_memory identity /
  operating_rules / trading_bot project.

---

## 1. Purpose

Crypto is added as a **separate research lane** under the completed validation
factory. This memo defines the standing rules for that lane so crypto research is
clean, conservative, and **never mixed into the NQ/ES futures branches.** It
authorizes nothing operational — no data, no code, no test, no trade.

## 2. Prior crypto work status

**Historical notes only — NOT validated candidates under the new factory.** Older
crypto work included BTC/ETH/SOL/XRP-style bots, regime tests, momentum/breakout
tests, a Donchian-style crypto breakout, and trend/pullback ideas. **All of it
predates the validation-factory rules and is not validated under the current
standard.** No old crypto result, equity curve, or "winning" parameter set may be
cited as proof or carried over. Any old idea must be re-entered as a **new frozen
Crypto spec** and re-run through the full pipeline before it carries any weight. Old
work is context, not evidence.

## 3. Initial symbols

- **BTC** (primary)
- **ETH**
- **SOL**
- **XRP — optional, later, ONLY if the data-quality and liquidity rules (sections 5
  and 11) pass.** Not added by default.

Start narrow: BTC is primary; ETH and SOL provide multi-asset corroboration.

## 4. Spot vs perpetuals

- **Spot** OHLCV avoids funding-rate complexity entirely — cleaner accounting, no
  funding leg, a simpler protocol.
- **Perps** (perpetual futures) require explicit funding-rate handling; ignoring
  funding produces a wrong, usually optimistic, edge.

**Recommendation:** start with **spot or spot-like OHLCV** for a clean protocol.
**Only add perps after funding-rate data is sourced and the funding rules
(section 9) are defined and frozen.** Until then, perps are blocked.

## 5. Exchange / data source

Requirements for any dataset:
- Trusted exchange or data vendor, **named and pinned per dataset.**
- Complete OHLCV with no silent gaps.
- Clear, documented timezone/calendar (UTC expected).
- **No survivorship bias and no ambiguous data stitching** across symbols/contracts.
- Provenance recorded per dataset (source, range, retrieval method), the same way the
  offline futures CSVs are documented.

**Hard rule:** **no exchange API execution of any kind.** Data-source selection is a
read-only *decision*; execution endpoints are never wired. Data acquisition itself is
deferred to a later, separately authorized step — **this memo fetches nothing.**

## 6. Timeframe

- **Daily first.**
- **4H later**, only after the daily protocol works end-to-end.
- **No lower timeframe (1H / 15m / intraday) until the daily protocol is proven.**
  Lower TFs add path-dependency and microstructure noise the daily lane is designed
  to avoid.

## 7. 24/7 session handling

- **Daily candle boundary = UTC daily close (00:00 UTC)**, preferred and frozen per
  dataset.
- **No weekend gaps expected** (unlike futures) — every calendar day should have a
  bar.
- **Exchange outages handled explicitly** — flagged, not silently forward-filled. A
  missing/halted day is a data-QA event (section 11), not an invisible zero-return
  bar.

## 8. Fees / slippage

- **Spot fee:** conservative spot taker fee per side.
- **Slippage:** conservative spread/slippage estimate per fill.
- **Higher friction than futures where appropriate** — crypto spreads/fees on alts
  (SOL, XRP) are wider and more variable than liquid index futures.
- **Perps include funding** in friction, and funding is added **only when perps are
  explicitly enabled** (sections 4 and 9).

## 9. Funding rates

- **Required** for any perp test.
- **Never ignored** or assumed zero.
- **If funding data is unavailable or incomplete** for a symbol/period, **perps for
  that symbol/period are blocked.** Spot is unaffected.

## 10. IS / OOS windows

- **Proposed IS: 2020–2023** (if complete data exists for the symbol).
- **Proposed OOS: 2024–2025.**
- **2026 is blocked** unless explicitly authorized (mirrors the futures hard-seal
  discipline).
- **Data contingency:** if a symbol lacks clean 2020 history (e.g. SOL listing date,
  XRP availability), propose a **justified per-symbol alternative window** rather than
  fabricating or stitching history. The window is frozen per symbol before any run.
- **One-shot OOS** against a committed protocol hash, exactly as the futures factory
  enforces. No tuning after OOS.

## 11. Data QA rules

- **Duplicate timestamps** → reject/flag.
- **Missing daily bars** → flag explicitly (do not silently fill).
- **Invalid OHLC** (high<low, close/open outside high–low, negatives) → reject.
- **Zero-volume bars** → flag (possible outage or illiquid listing).
- **Exchange outage flags** → recorded as explicit events, not hidden.
- **Symbol continuity** → no ambiguous stitching across exchanges/pairs; one
  consistent series per symbol.
- **Stablecoin quote consistency** → document and reconcile USDT vs USD vs USDC
  quoting; do not silently mix quote currencies (**USDT/USD differences are a known QA
  hazard**).

## 12. Validation ladder

**Crypto uses the same factory ladder as futures — no separate, looser standard:**

1. Frozen spec (pre-registered, no parameter freedom).
2. IS baseline (hard OOS seal).
3. OOS protocol pre-registration (committed protocol hash).
4. OOS once (one-shot, no post-OOS tuning).
5. Entry significance (random-entry permutation over fixed horizons).
6. Sequence risk / Monte Carlo (trade-order shuffle, bootstrap, top-winner dependence).
7. Regime breakdown (bull / bear / chop concentration).
8. Multi-asset crypto robustness (BTC/ETH/SOL corroboration).
9. Walk-forward (rolling-window stability).
10. Friction stress (fee + slippage; + funding for perps).
11. Final decision gate (one research decision + one readiness level; PAPER/LIVE
    unreachable on the default path).

## 13. Old crypto test migration

- **Inventory** old crypto tests (BTC/ETH/SOL/XRP bots, regime/momentum/breakout/
  Donchian/trend-pullback notes).
- **Classify** each as historical only.
- **Do not reuse** old OOS conclusions, curves, or claimed edges.
- **Any old idea must become a new frozen Crypto spec** before any retest.
- **No parameter import** from an old "winning" test without explicit pre-registration
  in the new frozen spec (no silent carryover of tuned parameters).

The inventory itself is **Crypto-D2** (section 16) — not performed here.

## 14. Pass / watch / fail rules (initial, conservative)

Aligned with the futures-factory lesson that **top-winner dependence killed every
parked futures branch.** Initial gates:

- **Enough trades** — clears the minimum trade-count floor (no thin small-N samples).
- **Positive expectancy** (per-trade R > 0 after costs).
- **Profit factor** above threshold.
- **Low top-3-winner dependence** — net stays positive after removing the top 3
  winners (the gate that parked all futures branches).
- **Sequence risk acceptable** — Monte Carlo / bootstrap not dominated by path luck.
- **Friction/funding positive** — survives conservative fees + slippage (+ funding for
  perps).
- **BTC/ETH/SOL corroboration** if multi-symbol — edge not confined to one coin.
- **No live/paper promotion** regardless of result.

`PASS` = edge survives the ladder, **continue research only** (never "go
operational"). `WATCH` = mixed/thin, park as candidate, no promotion. `FAIL` = stop
the branch.

## 15. Forbidden actions (this lane)

`no_live_trading` · `no_paper_trading` · `no_exchange_api_execution` ·
`no_auto_bot_launch` · `no_using_old_results_as_proof` ·
`no_mixing_crypto_with_futures_validation_claims` · `no_broker` ·
`no_data_fetch` · `no_code` · `no_backtest` · `no_optimization` · `no_strategy_test` ·
`do_not_modify_futures_strategy_branches` · `jarvis_templates_base_hydra_untouched` ·
`no_staging` · `no_commit_unless_separately_approved`.

## 16. Recommended next step

**Crypto-D2: old crypto test inventory + data-source decision (memo only, still no
backtest).**
- Inventory and classify all old crypto tests as historical-only.
- Select and pin a trusted **spot** data source per initial symbol (BTC/ETH/SOL), with
  provenance and QA expectations — **selection decision only, no fetch.**
- Confirm per-symbol IS/OOS window feasibility against real listing/history
  availability.

**Crypto-D2 is NOT authorized by this memo.** It requires a separate explicit
instruction. No data fetch or code in Crypto-D2 either.

## 17. Final line

**“Crypto-D1 is a protocol-only step. No crypto strategy is validated, paper-ready,
live-ready, or authorized for execution.”**

---

**Trading recommendation:** NONE. Protocol/memo only. No crypto strategy is validated,
paper-ready, or live-ready. Older crypto work (BTC/ETH/SOL and other bots/tests) is
historical context only and must be re-evaluated solely through the new factory
pipeline. **Crypto is a separate research lane** that must pass the same validation
ladder as futures before any further claim.
