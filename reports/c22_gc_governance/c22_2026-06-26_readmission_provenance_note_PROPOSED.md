# C22 — 2026-06-26 Window: PROPOSED Re-admission / Provenance Note

Status: **PROPOSED** (documentation only). Written 2026-09-09. Nothing in this note modifies,
minifies, replaces, re-hashes, moves, or deletes any file. The active frozen file and every
quarantine record are byte-unchanged. A human may adopt this note by copying it into
`data/external_signum_trend_radar_gc_inbox/_quarantine/2026-06-26/` as a third record; this
session did not do so.

## 1. The file

| Field | Value |
|---|---|
| Active dataset path | `data/external_signum_trend_radar_gc/gc_crypto_trendradar_daily_20260626.json` |
| Active inbox path | `data/external_signum_trend_radar_gc_inbox/gc_crypto_trendradar_daily_20260626.json` |
| SHA-256 (both, verified 2026-09-09) | `a872f3568f17e95a6dd2c90c2eac3b042113e48e6326962b0b28684d53a8bebb` |
| Size | 113,530 bytes (pretty-printed; ~62 KB when minified) |
| Content | 50 results, `limited=false`, `total=50`, same keys as every other daily window; internal `runDate` 2026-06-26 |
| File mtime (both copies) | 2026-06-26 20:44:48 -03:00 |

## 2. Chronology (from the surviving records; none altered)

1. **2026-06-25 22:02 -03:00 — first quarantine** (`_quarantine/2026-06-26/QUARANTINE_NOTE.txt`).
   Reason recorded: over-collected by bulk pickup while the operator requested 06-25 only;
   FUTURE-DATED relative to the clock (06-25) and ANOMALOUS SIZE (113,530 vs ~62,000 bytes).
   Copies preserved as `dataset__…` and `inbox__…`. Removed from active dataset + inbox.
2. **2026-06-26 00:45 — scheduled pickup re-admitted it** once the calendar made 06-26 same-day
   (future-date guard no longer applied).
3. **2026-06-26 11:58 -03:00 — second quarantine** (`REQUARANTINE_NOTE_2.txt`). Reason recorded:
   NON-CANONICAL serialisation (4,286 newlines; raw/compact ratio ~1.82) although
   content-identical to a normal daily export. Copies preserved as `reentry_20260626T115826__…`.
   Note states: "size/content-shape anomaly guard added so this cannot re-enter even same-day."
4. **2026-06-26 20:44 -03:00 — third entry (current).** The same bytes (identical SHA-256)
   returned to the active dataset and inbox. No note records this event. The importer's
   pretty-print check (`PRETTY_PRINT_WARN_RATIO = 1.30`,
   `c22_signum_gc_local_export_importer_contract.py:78,171-176`) is implemented as a
   **warning**, not a rejection, so it did not block re-entry.
5. **2026-07-15 — frozen V2 evidence pins it.** The V2 26-window artifact
   `detector_labels/c22_gc_real_candle_entry_labels_multiwindow_v2_26w_2026-06-20_2026-07-15.json`
   (artifact SHA-256 `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8`) records
   `source_sha256 = a872f356…` for every 2026-06-26 label row. The 2026-07-20 V2 integrity
   report rebuilt the artifact byte-identically from that file.
6. **2026-09-09 — V3_EXTENDED artifacts pin it again** (82w / 57w profiles), and the V3 integrity
   report proves the V3 rows inside the V2 range are canonical-identical to V2.

## 3. Current dependency

The 2026-06-26 window as it exists on disk is a **frozen-evidence dependency** of:
- the V2 26-window label artifact (the decisive 88-signal cohort includes one BEAR_SHORT decided
  on 2026-06-26: `2026-06-26|BINANCE:AAVEUSDT|BEAR_SHORT`),
- the Phase A REV1 replay spec, B1, B2 and B3 (all bound to the V2 evidence SHA),
- the V3_EXTENDED 82w and 57w artifacts and their integrity reports,
- the 2026-09-09 no-P&L dry run (SHA-pins the V2 artifact before reading it).

Replacing or minifying the file would change `source_sha256` for 50 label rows and break the
byte-identical rebuild of the frozen V2 artifact. **That must not happen.**

## 4. Assessment

- Data content: normal window (50 rows, standard keys, internal runDate consistent with the
  filename, candle chain consistent with 06-25 and 06-27 exports).
- Deviation: whitespace/serialisation only.
- Risk: documentation and invariant drift ("one admitted representation per window" is
  satisfied; "canonical minified serialisation" is not, for this window only).

## 5. Proposed re-admission wording (for a human to adopt or reject)

> RE-ADMISSION RECORD (2026-06-26 window). The pretty-printed export with SHA-256
> `a872f356…` re-entered the active dataset and inbox on 2026-06-26 20:44 -03:00 after two
> quarantines. Its content is a valid daily window; only its serialisation is non-canonical. It
> was subsequently pinned as the source of the 2026-06-26 label rows in the frozen V2 26-window
> artifact (2026-07-15) and is therefore RETAINED AS-IS as frozen evidence. The two quarantine
> notes remain valid history and are not superseded. No minified replacement will be
> substituted while any frozen artifact pins this SHA. Recorded by: ______ on ______.

## 6. What this note does NOT do

- Does not change the importer warning into a rejection (a code change outside this scope).
- Does not touch `_quarantine/2026-06-26/` or its copies.
- Does not re-hash, minify, or re-serialise the active file.
