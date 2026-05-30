# JARVIS Step 24 — Panel Glossary

- **Generated:** 2026-05-30
- **Type:** documentation only (no code, no UI, no API change)
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status

A plain-language glossary of every visible JARVIS section and key panel: what
each means, what healthy / warning / critical readings look like, and what the
operator should do. **Documentation only** — it adds no capability, control, or
API change.

---

## 1. Purpose and relation to Steps 20–23

- **Step 20** polished the UI (CSS/HTML/labels only).
- **Step 21** proved the polished UI is live and safe
  (**JARVIS_POST_POLISH_SMOKE_PASS**).
- **Step 22** gave the operator runbook (how to operate and interpret it).
- **Step 23** set the known limits and the safe, risk-tiered roadmap.
- **Step 24 (this memo)** is the reference glossary operators read alongside
  the runbook — a plain-language definition of every section and key panel.

---

## 2. Current committed baseline

| Step | Commit | What it did |
| --- | --- | --- |
| Step 20 | `4200253` | Safe UI-only polish pass (`templates/jarvis.html` only). |
| Step 21 | `4f55aae` | Post-polish live smoke memo (validation only). |
| Step 22 | `82ccf52` | Operator guide / runbook (documentation only). |
| Step 23 | `37d7dcc` | Known limits & safe roadmap (documentation only). |

---

## 3. JARVIS identity

- **Read-only observer** — it mirrors aggregated state and never mutates
  anything.
- **No execution authority** — no commands, scripts, prompts, or missions are
  run from the page.
- **No broker / paper / live control** — there is no order path;
  `paper_ready`, `live_ready`, and `broker_control` are always false.

---

## 4. Panel-id alias note

The Step 24 spec named four panels with shorthand that are **not** literal
template ids. They are documented here mapped to the real committed ids so
nothing is ambiguous:

| Spec shorthand | Actual id | Reads |
| --- | --- | --- |
| `pCommander` | `pSnapshot` | `commander_snapshot` |
| `pResearch` | `pTradingDetail` | `trading_detail` |
| `pStatus` | `pCore` | `system_core` |
| `pDocs` | `pMissions` + `pPromptLib` + `pSystemMap` | `mission_board` + `prompt_library` + `system_map` (the "Documentation & Maps" section, not a single panel) |

The real key panel ids are: `pSnapshot`, `pCore`, `pBrains`, `pTrading`,
`pHealth`, `pRouteSmoke`, `pHygiene`, `pMissions`, `pPromptLib`, `pSystemMap`,
`pTradingDetail`, `pCacheFreshness`.

---

## 5. Section glossary (the six dividers)

| Section | Meaning | Contains |
| --- | --- | --- |
| **Command Overview** | The single-glance verdict for the whole system. | `pSnapshot` |
| **Core Systems** | The foundational infrastructure: server, AI brains, git repository, project artifacts, brain memory. | `pCore`, `pBrains`, `pGit`, `pProject`, `pBrainMem` |
| **Operations** | Read-only engine status plus the daily plan. | `pTrading`, `pContent`, `pMoney`, `pMoving`, `pMission`, `pNext` |
| **Safety & Reliability** | Safety gates, operator posture, and the cached health / route / cache-freshness / hygiene reports. | `pSafety`, `pOpSafety`, `pHealth`, `pRouteSmoke`, `pCacheFreshness`, `pHygiene` |
| **Research Visibility** | Read-only trading research detail — no broker, paper, or live. | `pTradingDetail` |
| **Documentation & Maps** | Tracked, display-only mission board, prompt library, and system wiring map. | `pMissions`, `pPromptLib`, `pSystemMap` |

---

## 6. Key panel glossary

### `pSnapshot` — Commander's Snapshot (alias `pCommander`, reads `commander_snapshot`)
- **Means:** the derived top-level verdict: overall state plus safety, health,
  route, trading posture, cache, counts, and warnings.
- **Healthy:** `overall_state = green` (clean posture, all required checks pass).
- **Warning:** `overall_state = yellow` — most often a dirty/untracked working
  tree. Needs attention, not approval.
- **Critical:** `overall_state = red`, or trading posture not `research_only`.
- **Operator action:** read the warnings line. Yellow: note it and continue
  observing. Red: stop and investigate the failing signal.

### `pCore` — System Core (alias `pStatus`, reads `system_core`)
- **Means:** server running state, brain state, server time, and library counts.
- **Healthy:** server running; brain online; sensible counts.
- **Warning:** brain state not online, or counts missing.
- **Critical:** server not running / section error.
- **Operator action:** if the server isn't running, restart it offline and
  re-check. Do not add a UI control.

### `pBrains` — AI Brains (reads `ai_brains`)
- **Means:** per-brain state (Claude / Codex / Gemini / Ollama).
- **Healthy:** expected brains present and online.
- **Warning:** a brain idle / waiting / placeholder (informational).
- **Critical:** brain error / not connected when it is expected.
- **Operator action:** warn states are usually informational; investigate
  offline only if a required brain is down.

### `pTrading` — Trading Bridge (reads `trading_bridge`)
- **Means:** READ-ONLY / LOCKED trading posture, sealed lifecycle count, and
  per-lifecycle verdicts.
- **Healthy:** posture READ-ONLY / LOCKED; lifecycle count as expected.
- **Warning:** lifecycle count 0 / waiting.
- **Critical:** posture shows anything other than read-only / locked.
- **Operator action:** a critical posture change is a safety regression — stop
  and investigate. There is no order path here by design.

### `pHealth` — Health Report (reads `health_report`)
- **Means:** CACHED offline compile/test health (py_compile, pytest).
- **Healthy:** overall pass; py_compile and pytest pass.
- **Warning:** no cached report (manual tool not run) — not a live failure.
- **Critical:** overall fail / a check failed.
- **Operator action:** if failing, read the stderr tail and fix offline;
  regenerate the cached report with the manual tool. Never run the tool from
  the web.

### `pRouteSmoke` — Route Smoke (reads `route_smoke_report`)
- **Means:** CACHED GET-only route check with per-route status codes.
- **Healthy:** overall pass; required routes 200.
- **Warning:** no cached report, or a non-required 404 (e.g. `/money-spartan`).
- **Critical:** a required route fails.
- **Operator action:** required-route failures — investigate the route offline.
  Non-required 404s are expected noise.

### `pCacheFreshness` — Cache Freshness (reads `cache_freshness`)
- **Means:** DISPLAY-ONLY cache metadata: per-cache age vs threshold,
  gitignored status, timestamps. Reads metadata only; never refreshes.
- **Healthy:** overall fresh; each cache within its threshold.
- **Warning:** stale or missing — a manual cached report is old or not
  generated (not a live failure).
- **Critical:** invalid / unavailable (corrupt or unreadable cache file).
- **Operator action:** stale/missing — regenerate the cached report offline
  with the manual tool. Invalid — inspect the file offline.

### `pHygiene` — File Hygiene (reads `file_hygiene_report`)
- **Means:** CACHED git/untracked summary: untracked, tracked-modified, staged
  counts; top untracked dirs; cached reports stay gitignored.
- **Healthy:** staged count 0; cached reports gitignored.
- **Warning:** non-zero staged count, or a large untracked backlog.
- **Critical:** a cached report shown as NOT ignored, or git read unavailable.
- **Operator action:** investigate a non-zero staged count before commit work;
  ensure cached reports remain gitignored.

### `pMissions` — Mission Board (alias `pDocs`, reads `mission_board`)
- **Means:** DISPLAY-ONLY tracked operator missions with status/priority.
  "Safe next prompt" text is display only.
- **Healthy:** board renders with mission cards.
- **Warning:** NO MISSION BOARD (file missing) or blocked missions present.
- **Critical:** section unavailable / error.
- **Operator action:** missions are informational. Nothing on this panel
  executes; never add a run/execute control.

### `pPromptLib` — Prompt Library (alias `pDocs`, reads `prompt_library`)
- **Means:** DISPLAY-ONLY tracked prompts with category / risk / allowed flags.
  Prompt text is shown, never run.
- **Healthy:** library renders with prompt cards.
- **Warning:** NO PROMPT LIBRARY (file missing).
- **Critical:** section unavailable / error.
- **Operator action:** read prompts as reference only. There is no
  copy-and-run affordance, and there must never be one.

### `pSystemMap` — System Map (alias `pDocs`, reads `system_map`)
- **Means:** DISPLAY-ONLY wiring map: panels, manual-only scripts,
  tracked/ignored files, and posture flags.
- **Healthy:** posture flags — read-only TRUE, browser execution DISABLED,
  broker control DISABLED, file mutation from web DISABLED.
- **Warning:** version/counts missing.
- **Critical:** any posture flag flips to the unsafe value (e.g. browser
  execution ENABLED).
- **Operator action:** an unsafe posture flag is a serious regression — stop
  and investigate.

### `pTradingDetail` — Trading Research Detail (alias `pResearch`, reads `trading_detail`)
- **Means:** READ-ONLY research detail: candidate status, posture flags, S26
  research state, latest report cards.
- **Healthy:** `read_only` TRUE; `paper_ready` / `live_ready` /
  `broker_control` all FALSE.
- **Warning:** a research report missing / waiting.
- **Critical:** `paper_ready`, `live_ready`, or `broker_control` reported TRUE.
- **Operator action:** any TRUE on paper/live/broker is a CRITICAL safety
  regression — stop and investigate immediately.

---

## 7. Field glossary

| Field | Means | Must be |
| --- | --- | --- |
| `online` | The aggregator responded and the page received its payload (dashboard liveness). Not a claim that all subsystems are green. | true |
| `read_only` | The whole JARVIS surface is observe-only: no execution, no refresh control, no broker/paper/live path, no web file mutation. | true (always) |
| `overall_state` | Commander's Snapshot verdict. | green = healthy, yellow = attention needed (often dirty tree), red = stop and investigate |
| `cache_freshness` | Display-only freshness of the gitignored cached reports (fresh / stale / missing / invalid). | ideally fresh; stale/missing is non-blocking |
| `commander_snapshot` | The derived top-level summary object that powers `pSnapshot`. | present |
| `system_map` | The display-only wiring map object that powers `pSystemMap`, including posture flags. | present with safe posture flags |
| `trading_detail` | The read-only research detail object that powers `pTradingDetail`. | present, `read_only` true |
| `paper_ready` | Whether a paper-trading path is armed. | false (always) |
| `live_ready` | Whether a live-trading path is armed. | false (always) |
| `broker_control` | Whether JARVIS holds any broker control / order path. | false (always) |

---

## 8. Safety interpretation rules

- **Green** — observation healthy.
- **Yellow** — attention needed.
- **Red** — stop and investigate.

**None of these colours authorizes trading or execution.**

---

## 9. Never confuse this with permission

A green dashboard is an observation that the system *looks* healthy. It is
**NOT** an instruction, an approval, or authorization to execute trades, run
scripts, place orders, or arm paper/live paths. JARVIS grants no permissions —
it only shows state. Authorization for any action comes from an explicit human
decision through the proper, separately-gated channel, never from a colour on
this page.

---

## 10. Recommended next safe step

- **JARVIS-STATUS-INTERPRETATION-TABLE-MEMO (Step 25)** — a docs-only
  reference table of every section's possible states and exactly how to read
  each, complementing this glossary; **or**
- **JARVIS-REPORT-ARCHIVE-INDEX-MEMO** — a docs-only index of all committed
  JARVIS step reports with their commit hashes and conclusions.

---

**Conclusion:** documentation-only panel glossary created. No code, UI, tool,
test, API, or trading surface was changed.
