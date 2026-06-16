# SPARTA Portfolio Capital-Efficiency Input Contract v1

> **Research-only. Advisory-only. Input contract / specification only.**
> No broker control. No live trading. No live capital allocation. No
> paper-order execution. No order sizing. No exchange connection. No API keys.
> No `.env`. No scheduler. **No external network calls. No input is read in
> this bundle. No metric computed. No allocation computed.** This contract
> defines *which FROZEN, committed artifacts* the Portfolio Capital-Efficiency
> lane may later read, and the admissibility / freeze rules they must satisfy.

**Input contract id:** `portfolio_capital_efficiency_input_contract_v1` ·
**version:** `1.0` · **phase:** `P1_input_contract`

**Lane status (self-declared):** `WATCH` — inherits the upstream registries'
verdict ceiling and never surfaces PASS / ACTIVE / STRONG.

**Companion (P0):**
`reports/portfolio_capital_efficiency_protocol_v1/protocol.{json,md}`.

---

## 1. Objective + framework-only posture

Define exactly which **FROZEN, committed** research artifacts the lane MAY
read, and the rules they must satisfy, **before** any capital-efficiency metric
is computed (P2) or any advisory allocation is shaped (P5).

**This bundle is framework-only.** It reads nothing in its runtime, computes
nothing, **connects to no indicator results**, and authorizes no allocation.
Connecting concrete frozen outputs is a separate, separately-authorized step.

## 2. Candidate #10 — deferred, NOT connected

**Candidate #10 indicator results are NOT connected by this contract.** C10
must **finish and freeze by itself first** on its own track.

- **Connection status:** `deferred_not_connected`.
- **Blocked until:** C10 produces a FROZEN, committed replay / verdict
  artifact from its own lane.
- **When admissible:** once C10 has a frozen, committed replay output, it
  becomes an *ordinary read-only bench input* subject to the **same**
  admissibility rules as any other frozen per-strategy report — and may then be
  read to evaluate **overlap, correlation, and capital efficiency**. Only the
  frozen committed form; **never** the working tree.

**Candidate #10 frozen replay outputs are a deferred future input and are not connected by this contract.**

## 3. Admissible input classes (read-only, frozen-only)

| Class | Form | Access | Frozen required |
|---|---|---|---|
| `strategy_report_registry_output` | committed `report.json` normalized by `tools/strategy_report_registry.py` | read-only | yes |
| `strategy_candidate_registry_output` | committed candidate status summaries from `tools/strategy_candidate_registry.py` | read-only | yes |
| `frozen_per_strategy_backtest_report` | committed per-strategy `report.json` (PASS/WATCH/FAIL + cost-aware stats over a checksummed dataset) | read-only | yes |

## 4. Required fields per input

`candidate_id` · `verdict_ceiled` (WATCH max) · `asset_exposure` ·
`regime_exposure` · `direction` · `frozen_cost_aware_expectancy` (ranking only,
never auto-sizing) · `standalone_risk` · `dataset_freeze_ref` (sha256 / freeze
record) · `contract_version_pin`.

## 5. Admissibility rules

- **Committed only** — any uncommitted working-tree file is inadmissible.
- **Frozen with checksum** — the underlying dataset must have been frozen with
  a sha256 / checksum upstream; reports over mutable data are inadmissible.
- **Version-pinned** — each report cites its dataset version + the upstream
  data-contract version it was validated under.
- **Verdict ceiling inherited** — any raw PASS / ACTIVE / STRONG is clamped to
  WATCH; the lane never surfaces them.
- **No live positions / balances**, **no network-sourced numbers**.
- **Reproducible** — same frozen inputs reproduce the same read bit-for-bit.

## 6. Inadmissible inputs

- Live broker / exchange balances or positions.
- Any uncommitted working-tree artifact (including the in-flight C10 files,
  labels, replay, detector).
- Any dataset not frozen with a checksum upstream.
- Any number from a live network fetch.
- Any report surfacing a raw PASS / ACTIVE / STRONG verdict that bypasses the
  WATCH ceiling.
- Any synthetic / mock-valued stand-in used for an evidence claim.

## 7. Verdict ceiling

`max_surfaced_verdict = WATCH`. PASS / ACTIVE / STRONG are forbidden. The lane
is downstream and advisory; it must never imply readiness it has not earned.

## 8. Freeze requirements

Inputs must be committed, checksummed, and contract-version-pinned; no mutable
inputs; any input revision creates a **new version** — the lane never reads a
silently-edited artifact in place.

## 9. PASS / WATCH / FAIL rules

- **PASS** — every cited input is committed + frozen + checksummed, exposes all
  required fields, cites dataset + contract version, respects the WATCH
  ceiling, and reproduces bit-for-bit. **PASS means "inputs fit for a future
  read", never "allocate".**
- **WATCH** — inputs satisfied but at least one borderline (thin field
  coverage, marginal freeze provenance accepted by the operator); documented +
  re-checked before any compute phase.
- **FAIL** — any input uncommitted / unfrozen / unpinned, surfaces a bypassed
  PASS/ACTIVE/STRONG, is sourced from live balances/positions/network, or
  cannot be reproduced bit-for-bit.

## 10. Required future artifacts

- **Metric Spec v1** (P2) — exact formulas + inputs per metric. Spec only.
- **Allocation Baseline Spec v1** (P3) — reference models + concentration cap.
- **Overlap/Correlation Method v1** (P4) — redundancy estimation method.
- **Advisory Memo Schema v1** (P5) — shape of the human-review allocation memo.
- Lane closeout memo if the capital-efficiency idea PARKs / RETIREs.

## 11. No-profit-claim policy

- This contract does not imply edge and does not allocate capital.
- Clean, frozen inputs do not imply profit.
- A capital-efficiency score does not imply future returns.
- An advisory allocation memo is a human-review aid, never an execution
  instruction.
- No allocation is authorized by this contract alone (P2+ outputs require their
  own separate authorization).

## 12. Safety boundaries (pinned, non-negotiable)

- Research-only. Advisory-only. Input contract / specification only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No live capital allocation. No paper-order execution. No
  order placement. No order sizing for execution.
- No scheduler / background daemon. No external network calls in this
  contract's runtime.
- No input read, no metric computed, no allocation computed in this bundle.
- Do not modify paper / live execution files. Do not touch Candidate #10
  files, tests, labels, replay, detector, or working-tree state.
- Candidate #10 indicator results are NOT connected by this contract; C10 must
  finish and freeze by itself first.
- Consume only FROZEN, committed, admissible artifacts; never live positions or
  uncommitted working trees.
- Do not claim profitability. Do not claim live-readiness. Do not claim STRONG
  evidence from this contract alone.
- **A capital-efficiency score does not imply future returns.**
- **An advisory allocation is not an execution instruction.**
- **No allocation is authorized by this contract alone.**
