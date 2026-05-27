# Fincept Inspiration Review — for a SPARTA Trading Command Center

**Status:** REVIEW-ONLY memo. No code. No spec. No authorization to build.
**Scope:** Look at the Fincept Terminal project as *external inspiration only* for
a future SPARTA-internal "Trading Command Center" dashboard.
**Author intent:** Decide which of Fincept's surface ideas are worth absorbing
into SPARTA's existing read-only discipline, and which are dangerous or
distracting given SPARTA's current posture (Trading `PAUSED` · Live
`BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · `no_strategy_optimization_authorized = True`).

---

## 0. Hard boundaries this memo respects

The following are *not* on the table in this memo, and any future build step
must continue to honor them:

- **No Fincept code is copied.** No vendored modules, no forked files, no
  derivative redistribution. Inspiration in the design-pattern sense only.
- **No Fincept clone.** SPARTA does not need a generic Bloomberg-style
  terminal; it needs a narrow internal command center that fits SPARTA's
  existing sealed-artifact + read-only philosophy.
- **No trading-strategy file is changed.** All `B006_*`, S7/S8/S9/S10
  sealed artifacts, runner packages, execution guards, RUN_BOOKs, archival
  memos remain byte-stable. This memo touches none of them.
- **No change to S10-D1 (MNQ+MGC long-history Databento work)** or
  **S10-D2 (P4 smoke battery / synthetic fixtures)**. Those tracks remain
  exactly as they are.
- **No live broker execution. No order-placing capability. No FRC grant.**
  Anything that could connect to a broker API, send an order, or even
  *prepare* an order payload is out of scope forever in this memo's
  proposals.
- **No agent or LLM gets read/write exchange credentials.** Per
  `brain_memory/operating_rules.md`, that requires a separate top-level
  authorization after a full risk review.

If a later build step appears to violate any of the above, it is not
covered by this memo and must be re-scoped.

---

## 1. What ideas from Fincept are actually useful for SPARTA

Fincept Terminal's value, at the *idea* level (not the code level), is that
it shows what a "single-pane finance desk" looks like when assembled from
open-source parts. The pieces that map cleanly onto SPARTA's existing
architecture are:

1. **A single command surface across many data domains.** Fincept tries to
   put markets, news, fundamentals, portfolio, and notes behind one shell.
   SPARTA already has `/clone`, `/guide`, the Strategy Lab, sparta_commander,
   research_os, and a growing reports tree. A *narrow* command-center view
   that surfaces the **read-only** state of the trading framework in one
   place is genuinely useful — operator currently has to navigate
   `reports/external_research_hunter/`, `data/`, sealed-artifact paths,
   and brain_memory by hand.

2. **Keyboard-driven, dense, low-chrome layout.** The "terminal aesthetic"
   isn't just nostalgia — it forces the UI to surface *data*, not
   navigation. For an operator-only internal tool, dense panels beat
   marketing-style dashboards. This maps well to SPARTA's
   `direct, no fluff, execution-focused` style preference in
   `brain_memory/identity.md`.

3. **Pluggable data-provider abstraction.** Fincept exposes multiple
   providers behind one interface. SPARTA already has Databento as the
   canonical market-data path; the *idea* (not the code) of "one provider
   port, multiple adapters" is useful for a future world where we might
   add a second vendor for cross-checks (e.g. CME calendar sources already
   sitting under `cme_calendar_sources/`). Inspiration only — SPARTA's
   adapter would be written from scratch and would NEVER include an order
   path.

4. **Live "watchlist" / status-panel pattern.** A panel that subscribes
   to one stream of *read-only* state and re-renders is a clean pattern
   for surfacing things like: which candidate lifecycles are in which
   phase, which sealed artifacts are byte-stable, which fail-closed gates
   are tripped, what's in the operator's "awaiting authorization" queue.

5. **News + notes integrated next to market data.** Inspiration only:
   for SPARTA, the analogue is **research_os briefs** + **brain_memory
   lessons** sitting beside the sealed-artifact view, so the operator
   can see *why* a candidate landed where it did without leaving the
   pane.

6. **Notebook-style "scratch" surface for ad-hoc queries.** Useful as
   a *read-only* SQL/JSON browser over already-sealed report JSON, NOT
   as a live execution surface.

---

## 2. What ideas from Fincept are dangerous or a distraction

These are the parts that look attractive in a generic finance terminal
but would actively damage SPARTA's discipline if absorbed naively:

1. **Anything that talks to a broker.** Fincept's design space includes
   portfolio + order management surfaces. **For SPARTA this is a hard
   no.** Operating rule 7 forbids LLM/agent broker-credential access
   without a fresh top-level authorization. The command center must
   not have a connector slot for a broker. Even greyed-out.

2. **"Paper trading" / simulated-order panels.** These look harmless but
   create a *visual affordance* for live trading. They also tempt
   feature creep ("just add real keys"). SPARTA already has a
   sealed-artifact backtest discipline (QC, LEAN, local Python runners
   under candidate lifecycles). A second simulation surface is
   redundant and risks producing numbers that are not bound to a
   `report_seal_sha256`.

3. **"AI assistant chats with your portfolio" type features.** Mixing
   an LLM with live portfolio state crosses two SPARTA invariants at
   once: (a) no credentials to agents, (b) `no_profitability_claim`.
   An LLM that summarizes portfolio P&L can drift into profit-proof
   language without a seal binding.

4. **Auto-strategy generation / "let the terminal propose trades."**
   Direct collision with `no_strategy_optimization_authorized = True`
   and the candidate-lifecycle phase ladder. Even as a "suggestion"
   panel, this creates pressure to bypass the
   spec-DRAFT→SEAL→runner→guard→operator-side-execution→
   result-sealing→archival path. **Do not import this idea in any
   form, ever.**

5. **One-click "deploy to live" anything.** No matter how many
   confirmation dialogs are bolted on. This is the kind of UI affordance
   that exists in trading terminals because their purpose is execution.
   SPARTA's purpose is *not* execution; it is fail-closed evaluation.
   The two purposes produce different UIs.

6. **Heavy framework lock-in (DearPyGui, custom event loops, native
   GUI runtime, etc.).** Even ignoring the "no copying" rule, adopting
   Fincept's runtime would drag in a UI stack disjoint from SPARTA's
   FastAPI + browser-based dashboard at `127.0.0.1:8765`. Keep
   SPARTA on FastAPI + a thin HTML/JS layer; do not introduce a second
   GUI runtime.

7. **Vendoring or mirroring Fincept's data-provider clients.** Any
   provider client we use must come from the provider's own
   first-party SDK (Databento's official client, etc.), not from a
   third-party aggregator. This is both a license-hygiene and a
   correctness point: re-derived clients drift.

8. **Public-facing exposure.** Fincept-style terminals are typically
   single-operator. The SPARTA command center must remain
   `127.0.0.1`-bound, behind the existing dashboard, with no
   "share link" or "team mode" feature.

---

## 3. Dashboard modules we should build later

These are *future* modules, all read-only, all subordinate to the
fail-closed sealed-artifact discipline. None of them is authorized by
this memo; they are listed in the order that gives the most operator
value per unit of risk.

> Convention: each module name below is a **proposal**, not a built
> route. None is wired into `/guide` yet. Adding any of them requires
> a separate spec DRAFT and operator authorization.

1. **`/command/lifecycles` — Sealed-artifact lifecycle viewer.**
   A read-only panel that lists every `B006_*` (and future analogue)
   candidate lifecycle, its current phase (0–8), the byte-stable seal
   hashes for each artifact, and the literal `Authorize ...` phrase
   required to advance it. No buttons that *advance* anything — the
   phrase still has to be typed by the operator. Pure surfacing.

2. **`/command/gates` — Live block-state surface.**
   Shows current state of the 6 live-gate blocks, FRC status,
   `no_strategy_optimization_authorized`, `Trading PAUSED` flag, and
   *why* each is in its current state (last decision link to
   `brain_memory/projects/trading_bot/decisions.md`). Surfaces only;
   does not modify state.

3. **`/command/data` — Databento + frozen-data inventory.**
   Read-only view of `data/databento/`, `data/databento_cache/`,
   `data/frozen_regime_inputs/`, frozen-stack JSONL evidence cycles,
   asset registry, CME calendar sources. Per file: path, sha256,
   bytes, last-touched, source manifest. NO fetch-trigger button.
   Fetches are still operator-side, manual, separate session.

4. **`/command/reports` — Sealed reports browser.**
   Indexes `reports/research_os/`, `reports/external_research_hunter/`,
   archival memos, result-sealing reports. Per report: declared
   `report_seal_sha256`, canonical body bytes, recomputed-on-load
   sha for staleness check, links to the spec + runner + guard pins.
   Read-only.

5. **`/command/lessons` — Lessons + decisions cross-index.**
   Cross-references `LESSON_*` IDs (e.g. LESSON_B006_001_004,
   LESSON_S10_D1_001) to the decisions that introduced them and the
   later artifacts that demonstrated them working (e.g. DR11 firing
   in B006_002). Helps operator avoid re-litigating closed lessons.

6. **`/command/commander` — sparta_commander operator queue.**
   Surfaces what's in the approval ledger, what intents are pending,
   what personas are in flight. Approval still happens through the
   existing Commander adapter; this is just a *view*. No new
   approval pathway.

7. **`/command/scratch` — JSON/Markdown read-only query pane.**
   A *local-only* surface to grep/jq across `reports/` and `data/`
   without leaving the dashboard. No write path. No upload.

8. **(Far future, separately re-justified) `/command/research`.**
   Read-only panel into research_os ADVISORY_ONLY briefs. Already
   covered by reports browser; promote only if friction is real.

What is **deliberately absent** from this list: any
`/command/trade`, `/command/orders`, `/command/positions`,
`/command/broker`, `/command/optimize`, `/command/auto`,
`/command/propose`, `/command/simulate`. Absent on purpose.

---

## 4. How this fits with the existing pieces

### 4.1. Databento

- Databento remains the **canonical** market-data path. The command
  center adds **no new fetch capability**; it only *describes* what
  is already on disk (path, sha, bytes, manifest).
- Operator-side fetches (per `s10_d1_mnq_mgc_step02b_operator_fetch_runbook.md`
  and similar runbooks) stay manual, stay in a separate session, stay
  under operator credentials. The command center never sees keys.
- Any future second vendor (cross-check only) is gated by a fresh spec
  DRAFT and its own runbook. Not promised here.

### 4.2. Local Python backtests

- The sealed candidate runners (e.g. `b006_002/main.py`, S7/S8/S9
  modules) are **not** touched. The command center does not invoke
  them. It only displays sha pins, build tags, last-run captures.
- LEAN/QC runs continue to be operator-side, separate browser session,
  operator's own QC account. The command center surfaces the captured
  artifacts (e.g. `b006_002_compact_summary_canonical.json`) after
  they land on disk; it does not call QC.
- The local Python smoke battery (S10-D2 P4 17/17) stays exactly as it
  is. The command center may *display* the latest pass-count, but does
  not run the battery.

### 4.3. Sealed reports

- Every `report_seal_sha256` shown in the command center is
  re-verified on display. If the canonical body bytes don't recompute
  to the declared sha, the panel surfaces a `SEAL_DRIFT` flag — it
  does not silently render stale data.
- The fail-closed posture (e.g. the B006_002 result-sealing decline
  when the captured summary was absent) is preserved: missing
  upstream artifact = panel shows missing, not synthesized.
- No panel rewrites a sealed file. Backups + write-once discipline
  remain in force.

### 4.4. SPARTA Commander

- The command center is **a sibling** of sparta_commander, not a
  replacement. Commander handles intents / personas / approvals /
  Telegram adapter. The command center is the operator's *desk view*
  of the same underlying state.
- The two share the same read-only data sources (sealed reports,
  brain_memory, decisions, lessons). The command center never reaches
  into Commander's approval ledger as a writer.
- Telegram adapter and approval ledger remain
  `LIVE_TELEGRAM_SAFE`, manual-start, with the token still in
  `local_secrets/` (gitignored). The command center does not see
  the token.

### 4.5. Read-only trading bridge

- The existing read-only trading bridge stays read-only. The command
  center is downstream of it: it consumes whatever read-only feed
  the bridge already exposes (positions snapshot, balance snapshot,
  if any) and presents it. It adds **zero** write capability.
- If the bridge today does not expose live broker reads, the command
  center does NOT add that path. It surfaces only what already exists.
- No write endpoint, no order intent, no "stage an order" affordance,
  no "what-if order" affordance. Period.

---

## 5. First safe build step

The first build step has to be the one that maximally proves "this
adds nothing dangerous" before any feature surface grows.

**Proposed first step (REVIEW-ONLY proposal; not authorized by this memo):**

> Build a single read-only FastAPI route, `/command` (or
> `/trading_command`), that renders **one panel only**: the
> **Sealed-Artifact Lifecycle Viewer** (Module 1 above), restricted
> to the `B006_*` candidate family already on disk under
> `reports/external_research_hunter/`. The panel:
>
> - Walks `reports/external_research_hunter/` for files matching the
>   known lifecycle artifact names (spec DRAFT, spec SEAL, runner
>   build report, guard build report, operator-prep, acknowledgment,
>   result-sealing report, archival memo).
> - For each artifact, reads it, recomputes sha256, compares against
>   the declared seal in the JSON sidecar, and renders a row with
>   `OK` / `SEAL_DRIFT` / `MISSING`.
> - Renders the current lifecycle phase as 0–8 with the next
>   expected `Authorize ...` phrase pulled verbatim from the latest
>   decision entry in `brain_memory/projects/trading_bot/decisions.md`.
> - Has **no** form fields, **no** POST endpoints, **no** buttons that
>   mutate anything.
> - Is gated to `127.0.0.1` only, behind the existing dashboard.
> - Adds one row to `system_manual_entries` via
>   `db.upsert_manual_entry()` so `/guide` documents it.
> - Has a tiny pytest that asserts:
>   (a) the route returns 200 with at least one B006_002 row present,
>   (b) the route returns no HTML form/POST attributes,
>   (c) `SEAL_DRIFT` is correctly raised when a test fixture supplies
>   a mutated body.

That step is small, surgical, additive, read-only, and gives the
operator immediate value (one place to see lifecycle health) without
touching a single trading-strategy file, without adding any
fetch/QC/LEAN/broker capability, and without modifying the
S10-D1 or S10-D2 work.

If that one panel ships cleanly and survives a week of operator use
without surprises, the *next* candidate module is Module 2
(`/command/gates`). Each subsequent module is a **separate**
authorization, a **separate** spec DRAFT, a **separate** test.

---

## 6. Final recommendation

**Use Fincept only as inspiration, not as dependency.**

Concretely:

- Absorb the *shape* of a dense, keyboard-friendly, read-only
  single-pane operator surface.
- Reject every Fincept feature that implies execution, optimization,
  auto-suggestion, broker connection, or LLM-on-live-portfolio.
- Build SPARTA's command center on the existing FastAPI dashboard,
  from scratch, additively, one read-only panel at a time, each
  panel gated by its own `Authorize ...` phrase and its own spec
  DRAFT.
- Do not vendor, fork, mirror, or import any Fincept code. Do not
  take a runtime dependency on the Fincept project. If a Fincept
  pattern is worth using, re-derive it in SPARTA's own style from
  the public design idea, not from the source.
- Keep the six-gate live block, FRC `NEVER_GRANTED`,
  `no_strategy_optimization_authorized`, Trading `PAUSED`, and all
  sealed-artifact byte-stability invariants in force at every step.

This memo authorizes nothing. It is a thinking document for the
operator to decide *whether* and *when* to issue the first
`Authorize ...` phrase for the proposed Module 1 build.
