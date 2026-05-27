# s10-D2 Reparam-Cap - P3 Runner BUILD Report (SEALED)

**Phase:** `P3_BUILD_ONLY_SEALED_NO_RUN`
**Operational status:** `RUNNER_BUILT_NO_SMOKE_RUN_YET`
**Report date UTC:** 2026-05-27T00:31:09Z

**Runner BUILD report seal:** `1eb04aa312f4053134c1e9387be7716aa4564c019168ee2cedcf789063d96405`
**Predecessor (P2 phase-2 plan) seal:** `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
**Plan-lock seal:** `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
**Tier-N spec seal:** `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`

---

## Files built (5 of 6 in this report; driver is sibling report)

| File | Size (bytes) | sha256 |
|---|---|---|
| `external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness/__init__.py` | 696 | `824298556f08c008...` |
| `external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness/main.py` | 23620 | `43632c198cd1faa1...` |
| `external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness/execution_guard.py` | 6725 | `8b78df9decc35538...` |
| `external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness/tests/__init__.py` | 150 | `3b296f70ee8893f8...` |
| `external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness/tests/test_smoke_t1_t15.py` | 12975 | `739436a8852758d0...` |

## Single delta from s8-D1 runner

- Parameter: `starting_cash_mnq_equivalent`
- s8-D1: **$100,000** -> s10-D2: **$500,000**
- Delta count: **1**
- NEW S10-D2 Initialize check: `S-STOP-14` raises `S10_D2_STARTING_CASH_INVARIANT_VIOLATION` if CONFIG starting_cash != 500_000
- All other strategy parameters byte-equivalent

## s8-D1 revival attestation

- s8-D1 chain status: PERMANENTLY_PARKED_AT_COMMIT_6e7b491
- s8-D1 revived by this build: **False**
- s8-D1 used as: STRUCTURAL BASELINE FOR S10-D2 NAMESPACE REWRITE AND STARTING_CASH DELTA
- s8-D1 runner files modified: **[]**

## Static validation (all pass)

- `__init__.py`: parse=True compile=True module_clean=True forbidden_top=[]
- `main.py`: parse=True compile=True module_clean=True forbidden_top=[]
- `execution_guard.py`: parse=True compile=True module_clean=True forbidden_top=[]
- `tests/__init__.py`: parse=True compile=True module_clean=True forbidden_top=[]
- `tests/test_smoke_t1_t15.py`: parse=True compile=True module_clean=True forbidden_top=[]

*End of S10-D2 P3 runner BUILD report.*
