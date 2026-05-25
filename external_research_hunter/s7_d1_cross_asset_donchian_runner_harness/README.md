# s7 D1 Cross-Asset Donchian (NQ + GC + ZN + CL) -- Runner Harness

**DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. Trading PAUSED. Live BLOCKED_AT_6_GATES.
FRC never granted. No profitability claim.**

This harness is BUILD-only scaffolding for the s7 D1 cross-asset Donchian
no-filter candidate. **No data has been fetched, no smoke has been run, no
backtest has been executed by the BUILD turn.**

## Sealed inheritance chain (sha-pinned)

| Artifact                              | sha256                                                             |
|---------------------------------------|--------------------------------------------------------------------|
| `predecessor (s7 selection plan)`     | `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac` |
| `tier_n_spec_seal_sha256`             | `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3` |
| `plan_lock_seal_sha256`               | `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d` |
| `phase2_plan_seal_sha256`             | `e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a` |
| `phase2_safety_template_md_sha256`    | `1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981` |
| `phase2_safety_template_json_sha256`  | `695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32` |

These shas are also embedded as module constants in `main.py` and re-verified
at `Initialize` per Phase 2 contract C2.

## File map

| File                              | Role |
|-----------------------------------|------|
| `main.py`                         | Algorithm class + helper functions; importable without QC runtime via lazy QC attribute access |
| `execution_guard.py`              | Runtime safety guard; **no side effects on import**; no broker/exchange adapter imports |
| `tests/test_smoke_t1_t15.py`      | T1-T15 synthetic-only smoke tests (PREPARED, NOT EXECUTED at BUILD time) |
| `tests/fixtures/synthetic_*.csv`  | 4 synthetic daily-bar fixtures (`source=SYNTHETIC_PHASE2_SMOKE_FIXTURE`); not real market data |
| `requirements.txt`                | numpy + pandas only at BUILD time |

## What this runner does NOT do

- Does NOT call Databento, QuantConnect, Kraken, Binance, Alpaca, or any other
  network endpoint
- Does NOT import broker / exchange / wallet adapters under any code path
- Does NOT run in live mode (C1 LiveMode refusal raises at Initialize)
- Does NOT execute smoke tests at BUILD time (P4 is a separate authorization)
- Does NOT fetch market data at BUILD time (P5 operator-managed)
- Does NOT execute the in-sample run at BUILD time (P6 is a separate authorization)

## Strategy parameters (locked from Tier-N spec, byte-equivalent to s6 REV1)

- Markets: `NQ.c.0`, `GC.c.0`, `ZN.c.0`, `CL.c.0` (Databento `GLBX.MDP3` continuous front-month)
- Donchian entry length: 55 daily bars; exit length: 20 daily bars
- Filter: **NONE** (AMB6 structurally locked)
- Stop: 2 * Wilder ATR(20) at entry
- Pyramid spacing: 0.5 * N; max units per market: 4
- Portfolio cap: 16 units (uses `pyr.current_unit_count`, not `pyr.total_quantity` -- s6 cap-bugfix inherited)
- Sizing: 1 % portfolio risk per unit
- Cost stress matrix: S0 / S1 / S2 / S3 / S4 (S4 reserved for tail-stress informational only)

## Lifecycle gates

| Stage | Authorization | Status |
|-------|---------------|--------|
| P3 BUILD (this turn)                       | granted | **complete** |
| P4 T1-T15 smoke                            | separate operator authorization required | not yet |
| P5 operator-side Databento fetch           | operator-managed                          | not yet |
| P6 in-sample run                           | separate operator authorization required | not yet |
| P7 in-sample decision memo                 | separate operator authorization required | not yet |
| P8 lifecycle transition (PARK or OOS-AUTH) | separate operator authorization required | not yet |

`NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT` continues to hold.
Live trading is permanently `BLOCKED_AT_6_GATES` for this candidate.
