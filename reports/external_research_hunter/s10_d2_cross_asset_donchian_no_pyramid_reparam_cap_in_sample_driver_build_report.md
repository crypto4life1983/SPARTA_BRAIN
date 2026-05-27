# s10-D2 Reparam-Cap - P3 In-Sample Driver BUILD Report (SEALED)

**Phase:** `P3_BUILD_ONLY_SEALED_NO_RUN`
**Report date UTC:** 2026-05-27T00:31:09Z

**Driver BUILD report seal:** `ddd604c96508a0ab835bcbae6e72fabc2993cd3f0dc459898ca326617dd96443`
**Predecessor (runner BUILD report) seal:** `1eb04aa312f4053134c1e9387be7716aa4564c019168ee2cedcf789063d96405`
**Tier-N spec seal:** `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`

---

## Driver file

| Path | Size | sha256 |
|---|---|---|
| `external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness/in_sample_driver.py` | 34128 | `19749ada4d98e1b2...` |

## Mechanical baseline inheritance from s8-D1 driver

- s8-D1 driver path: `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/in_sample_driver.py`
- s8-D1 driver sha256: `129411e90fba23ff...`
- s8-D1 driver NOT modified by this build: **True**

**Deltas from s8-D1 driver:**

- namespace identifiers (s8_d1_no_pyramid -> s10_d2_no_pyramid_reparam_cap)
- sealed-chain anchor shas (point to s10-D2 chain seals)
- starting_cash propagates from runner_main.CONFIG (no direct driver change; main.py CONFIG update is the source)
- docstring + __main__ informational text updated for s10-D2 reparam-cap

## Lazy databento attestation

- `databento_imported_at_module_top`: False
- `databento_imported_inside_load_dbn_local_function_only`: True
- `db_DBNStore_from_file_used`: True
- `db_Historical_used_anywhere`: False
- `no_databento_api_call_in_local_path`: True

*End of S10-D2 P3 in-sample driver BUILD report.*
