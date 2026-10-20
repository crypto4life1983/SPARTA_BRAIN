# Replay priors for the hypothesis ledger — 2026-10-20

**READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER**

An in-sample prior per hypothesis from the replay of the bot's own code (replay_2026-10-20: 2593 dedup trades taken, 2149 refused by the gate, 2487 allowed but not taken by the one-slot book). Rendered next to the forward score in the ledger; never used for promotion or rejection.

| id | replay prior ΔR | n | p(Δ>0) | stable across half-years | by half-year | note |
|---|---|---|---|---|---|---|
| block_long_in_TREND_DOWN | - | 0 | - | - | - |  |
| blockwhere__hold_bucket=short | +0.680 | 449 | 1.0 | yes | 2024-11 +0.44 (n=121), 2025-05 +0.81 (n=135), 2025-11 +0.90 (n=82), 2026-05 +0.59 (n=85), 2026-09 +0.73 (n=26) | block where {'hold_bucket': 'short'} |
| blockwhere__strategy=D__direction=short | -0.034 | 509 | 0.215 | no | 2024-11 -0.17 (n=104), 2025-05 +0.18 (n=138), 2025-11 -0.06 (n=172), 2026-05 -0.21 (n=90), 2026-09 +1.03 (n=5) | block where {'direction': 'short', 'strategy': 'D'} |
| enforce_hard_stop | - | 0 | - | - | - | replay never breaches the cap |
| extend_timeout__40 | +0.002 | 1160 | 0.55 | no | 2024-11 -0.01 (n=250), 2025-05 +0.03 (n=332), 2025-11 +0.04 (n=341), 2026-05 -0.02 (n=220), 2026-09 -0.70 (n=17) | hold 40 days instead of 20 on 20-day timeouts |
| partial_tp_or_trail_1R | - | 0 | - | - | - | replay exits embed the live partial rule |
| partial_tp_or_trail_2R | - | 0 | - | - | - | replay exits embed the live partial rule |
| review_pause_D2 | - | 0 | - | - | - |  |
| unblock__SLOT_OCCUPIED | +0.074 | 2487 | 0.999 | no | 2024-11 +0.21 (n=582), 2025-05 -0.13 (n=799), 2025-11 +0.10 (n=571), 2026-05 +0.28 (n=431), 2026-09 -0.17 (n=104) | take signals refused for SLOT_OCCUPIED |
| unblock__TREND_DOWN_BLOCKS_LONG | +0.218 | 964 | 1.0 | no | 2024-11 +0.71 (n=171), 2025-05 +0.62 (n=184), 2025-11 -0.26 (n=323), 2026-05 +0.13 (n=264), 2026-09 +1.21 (n=22) | take signals refused for TREND_DOWN_BLOCKS_LONG |
| unblock__TREND_UP_BLOCKS_SHORT | -0.073 | 298 | 0.066 | no | 2024-11 -0.02 (n=128), 2025-05 -0.25 (n=120), 2025-11 +0.74 (n=19), 2026-05 +0.37 (n=19), 2026-09 -0.86 (n=12) | take signals refused for TREND_UP_BLOCKS_SHORT |

- stable = the sign of the mean delta in every half-year with >= 10 trades matches the overall sign.
- A negative prior does not reject a hypothesis; a positive one does not confirm it. The forward thresholds decide.

_READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER_
