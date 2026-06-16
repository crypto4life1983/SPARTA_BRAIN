# SPARTA Portfolio Capital-Efficiency Allocation Baseline Spec v1

> **Research-only. Advisory-only. Allocation baseline spec / framework only.**
> No broker control. No live trading. No live capital allocation. No capital
> deployment. No paper-order execution. No order sizing. No exchange
> connection. No API keys. No `.env`. No scheduler. **No external network
> calls. No real allocation is computed in this bundle. No real portfolio
> result is produced. No data fetch, no detector, no replay, no backtest.**
> This spec pins *how* each allocation baseline would assign advisory research
> weights — it computes no real allocation and deploys no capital.

**Allocation baseline spec id:**
`portfolio_capital_efficiency_allocation_baseline_spec_v1` · **version:** `1.0`
· **phase:** `P3_allocation_baseline_spec`

**Lane status (self-declared):** `WATCH` — inherits the upstream registries'
verdict ceiling; never surfaces PASS / ACTIVE / STRONG.

**Companions:** P0 protocol, P1 input contract, P2 metric spec.

---

## 1. Objective + posture

Pin the **exact method, inputs, and constraints** for each
capital-efficiency **allocation baseline** — the reference models a future
advisory memo would compare. This bundle is **spec/framework-only**: it defines
*how* each baseline *would* assign advisory research weights over FROZEN
admissible strategies (P1), using the P2 metrics.
**No real allocation is computed in this bundle.**
It deploys no capital and produces no real portfolio result.

## 2. Candidate #10 — still deferred, NOT connected

**Candidate #10 remains deferred and is not connected by this spec.** It is
not read, connected, or depended on. C10 is currently **inadmissible** (not
frozen) and therefore receives weight **0** under the `zero_for_inadmissible`
rule. It becomes an ordinary admissible strategy only once it has its **own
FROZEN, committed** replay artifact (P1 rules) — never the working tree.

## 3. Shared symbols

| Symbol | Meaning |
|---|---|
| `S_admissible` | Strategies admissible under P1 (committed + frozen + checksummed + version-pinned, WATCH-ceiled). |
| `S_inadmissible` | Strategies that are inadmissible (unfrozen / uncommitted / unpinned / bypassed-verdict) — weight 0 by rule. |
| `w_i` | Advisory research weight of strategy *i* (**never** an execution size); `0 <= w_i`; weights + cash sum to 1. |
| `sigma_i` | `standalone_risk` of *i* (P1 frozen field). |
| `L` | Pre-declared concentration cap in `(0, 1]` (operator constant; never inferred). |
| `B` | Pre-declared capital-at-risk envelope (operator constant; never inferred). |
| `w_cash` | Cash / unallocated bucket weight; absorbs residual; full allocation when nothing qualifies. |
| `MCE_i` | `marginal_capital_efficiency` rank from P2 (+ future P4); **ranking only**. |

## 4. Allocation baselines (method + constraints; **none computed here**)

### 4.1 `equal_weight` — equal weight per admissible strategy *(reference)*
- **Method:** `w_i = 1 / |S_admissible|` for `i ∈ S_admissible`; inadmissible
  → 0; if `S_admissible` empty → all to `w_cash`.
- **Constraints:** sum-to-one incl. cash, long-only, inadmissible→0, cap `L`.

### 4.2 `equal_risk` — equal risk per strategy (inverse-vol / risk parity) *(reference)*
- **Method:** `raw_i = 1/sigma_i`; `w_i = raw_i / Σ_j raw_j` over
  `S_admissible` with `sigma_i > 0`; inadmissible → 0; missing/non-positive
  `sigma_i` → excluded + flagged.
- **Constraints:** sum-to-one incl. cash, long-only, inadmissible→0, cap `L`,
  budget `B`.

### 4.3 `capped_concentration` — capped concentration per strategy *(reference)*
- **Method:** from a base (equal-weight or equal-risk), clip
  `w_i' = min(w_i, L)`, redistribute clipped excess pro-rata across uncapped
  admissible strategies, iterate until none exceeds `L`; unplaceable residual →
  `w_cash`.
- **Constraints:** sum-to-one incl. cash, long-only, no grouping share > `L`,
  inadmissible→0.

### 4.4 `zero_for_inadmissible` — zero for inadmissible/unfrozen *(hard constraint)*
- **Method:** every `i ∈ S_inadmissible` gets `w_i = 0`, unconditionally. This
  rule **overrides every other baseline**.
- **Note:** C10 is currently inadmissible (deferred, not frozen) → weight 0.

### 4.5 `ranking_only_marginal_efficiency` — ranking only *(WATCH only)*
- **Method:** rank admissible strategies by `MCE_i` (P2, descending). The
  ranking informs a **human** ordering of research attention; it is **never**
  converted into automatic weights or execution sizes. Any human-assigned
  weights still pass through `zero_for_inadmissible` + `capped_concentration` +
  budget `B`.
- **Constraints:** ranking-only never auto-sizes, inadmissible→0, cap `L`.

### 4.6 `cash_unallocated_bucket` — cash when no strategy qualifies *(hard constraint)*
- **Method:** `w_cash = 1 - Σ_i w_i`; if `S_admissible` is empty, `w_cash = 1`
  (full unallocated). `w_cash` is never negative.
- **Note:** cash is an **advisory placeholder**, not a deployed cash position.

## 5. Global allocation constraints

- **Weights (incl. cash) sum to one.**
- **Long-only research weights** (no shorting the bench; `0 <= w_i`).
- **Inadmissible → weight 0** (absolute).
- **Concentration cap `L`** on every candidate / asset / family grouping (P2).
- **Capital-at-risk budget `B` respected** (P2); excess routes to cash.
- **Frozen admissible inputs only**; **no lookahead**; **reproducible**
  bit-for-bit.
- **No real allocation in this bundle.**

## 6. PASS / WATCH / FAIL rules

- **PASS** (for review only) — uses a defined baseline; inputs FROZEN +
  admissible; inadmissible strategies zero; weights (incl. cash) sum to one and
  long-only; no grouping breaches `L`; capital-at-risk within `B`;
  marginal-efficiency used for ranking only; WATCH ceiling held; reproduces
  bit-for-bit. **PASS means "advisory weights fit for human review", never
  "deploy" or "execute".**
- **WATCH** — computable but borderline (thin admissible set, much weight to
  cash, an accepted excluded strategy, sparse P4 correlation); documented +
  re-checked.
- **FAIL** — inadmissible strategy gets positive weight; weights don't sum to
  one or go negative; a grouping breaches `L`; budget `B` exceeded without
  routing to cash; ranking used to auto-size; or WATCH ceiling bypassed.

## 7. Required future artifacts

- **Overlap/Correlation Method v1** (P4) — supplies `rho_ij` for equal-risk
  refinements + the marginal-efficiency ranking.
- **Advisory Memo Schema v1** (P5) — finalises the report schema hosting these
  baselines.
- A separately-authorized **compute bundle** that actually runs these baselines
  over frozen admissible inputs.
- Lane closeout memo if the idea PARKs / RETIREs.

## 8. No-profit-claim policy

- This spec does not imply edge and does not allocate or deploy capital.
- A defined allocation baseline does not imply profit.
- A capital-efficiency score does not imply future returns.
- An advisory allocation memo is a human-review aid, never an execution
  instruction.
- No allocation is authorized by this spec alone.

## 9. Safety boundaries (pinned, non-negotiable)

- Research-only. Advisory-only. Allocation baseline spec / framework only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No live capital allocation. No capital deployment. No
  paper-order execution. No order placement. No order sizing for execution.
- No scheduler / background daemon. No external network calls in this spec's
  runtime.
- No real allocation computed, no real portfolio result, no data fetch, no
  detector, no replay, no backtest in this bundle.
- Do not modify paper / live execution files. Do not read Candidate #10
  working-tree files, tests, labels, replay, or detector.
- Candidate #10 remains deferred and is not connected by this spec; C10 must
  finish and freeze by itself first.
- Consume only FROZEN, committed, admissible artifacts; never live positions or
  uncommitted working trees.
- Do not claim profitability. Do not claim live-readiness. Do not claim STRONG
  evidence from this spec alone.
- **A capital-efficiency score does not imply future returns.**
- **An advisory allocation is not an execution instruction.**
- **No allocation is authorized by this spec alone.**
