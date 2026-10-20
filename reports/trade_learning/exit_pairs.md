# Paired exit experiment (D / F / F2 on the same entry) — 2026-10-20

**READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER**

Each closed entry (exchange, symbol, open_date, direction) that the bot booked under more than one strategy is one signal with several exits. Delta = R(first) − R(second) on the same entry; p = bootstrap probability that the mean delta is positive. The post-fix window is the only admissible evidence; the retired window is history.

- closed entries 46 · with two or more exits 7

| pair | window | n | mean ΔR | sum ΔR | p(Δ>0) | first mean R | second mean R | first wins / second wins |
|---|---|---|---|---|---|---|---|---|
| F-D | all | 0 | - | - | - | - | - | - |
| F-D | retired_pre_fix | 0 | - | - | - | - | - | - |
| F-D | post_fix | 0 | - | - | - | - | - | - |
| F2-D | all | 0 | - | - | - | - | - | - |
| F2-D | retired_pre_fix | 0 | - | - | - | - | - | - |
| F2-D | post_fix | 0 | - | - | - | - | - | - |
| F2-F | all | 0 | - | - | - | - | - | - |
| F2-F | retired_pre_fix | 0 | - | - | - | - | - | - |
| F2-F | post_fix | 0 | - | - | - | - | - | - |
| F-E | all | 1 | -0.659 | -0.66 | 0.0 | +2.699 | +3.358 | 0 / 1 |
| F-E | retired_pre_fix | 1 | -0.659 | -0.66 | 0.0 | +2.699 | +3.358 | 0 / 1 |
| F-E | post_fix | 0 | - | - | - | - | - | - |
| F2-E | all | 1 | -1.119 | -1.12 | 0.0 | +2.487 | +3.606 | 0 / 1 |
| F2-E | retired_pre_fix | 1 | -1.119 | -1.12 | 0.0 | +2.487 | +3.606 | 0 / 1 |
| F2-E | post_fix | 0 | - | - | - | - | - | - |
| F2-D2 | all | 4 | +0.000 | +0.00 | 0.0 | -1.220 | -1.220 | 0 / 0 |
| F2-D2 | retired_pre_fix | 4 | +0.000 | +0.00 | 0.0 | -1.220 | -1.220 | 0 / 0 |
| F2-D2 | post_fix | 0 | - | - | - | - | - | - |

## Best-of-three bias in the journal's dedup

The learning report and the ledger collapse mirrored rows to one signal by keeping the best-R row. When D, F and F2 hold the same entry, that is the best of up to three exits, not a trade anyone took.

- all: no multi-exit entries
- post_fix: no multi-exit entries

## Reading it

- A pair with p ≥ 0.9 on the post-fix window and the same sign on the retired window is a real difference between two exits on identical entries; anything else is noise at this n.
- This is evidence about exits only. It cannot say whether the entry has an edge.
- Nothing here is applied. A persistent, same-sign difference is a candidate for the ledger as a partial / ladder hypothesis, forward-scored like every other.

_READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER_
