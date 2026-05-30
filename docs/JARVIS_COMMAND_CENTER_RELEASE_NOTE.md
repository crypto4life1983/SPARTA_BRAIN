# SPARTA JARVIS Command Center — Release Note

**Feature commit:** `7c9cad2f97928a8cce98468349701b1c485a7061` (`7c9cad2`)
**Subject:** Add SPARTA JARVIS command center
**Date:** 2026-05-30

## What JARVIS adds

A cinematic, read-only command console for SPARTA Brain.

- **`GET /jarvis`** — a dark-blue holographic dashboard page (`templates/jarvis.html`):
  central "SPARTA JARVIS ONLINE" orb, glass panels, CSS-only glow/pulse/scan,
  responsive layout, no external CDN.
- **`GET /api/jarvis/status`** — a fail-closed JSON aggregator that reuses
  existing read-only signals across eight sections:
  System Core, AI Brains (Claude / Codex / Gemini / Ollama), Trading Bridge,
  Content Engine, Money Engine, Moving Company (placeholder), Daily Mission,
  and Safety Gates.
- **Navigation** — one additive `/jarvis` link in `templates/base.html`.
- **System manual** — a `jarvis_command_center` entry registered via
  `db.upsert_manual_entry()` so `/guide` stays accurate.

Committed files:

- `app.py`
- `templates/base.html`
- `templates/jarvis.html`
- `tests/test_jarvis_route.py`

## Safety posture

- **Additive only** — no existing route, template, or behavior was changed
  or removed; the feature is appended.
- **Read-only / status-oriented** — every section reports state only. Missing
  sources render as `not connected` / `waiting for signal`; no metric or
  profit number is ever fabricated.
- **No execution control** — nothing on this page or its API trades, uploads,
  or fires automation. Trading data stays read-only.
- **Safety gates surfaced as locked posture** — Trading execution `LOCKED`,
  Approvals `REQUIRED`, YouTube upload `APPROVAL_REQUIRED`, Live automation
  `BLOCKED`. The console cannot flip these; they are status, not toggles.

## Tests passed (before the feature commit)

- `python -m py_compile app.py` → **PY_COMPILE_OK**
- `pytest tests/test_jarvis_route.py --rootdir=tests` → **11 passed**

> Note on `--rootdir=tests`: a pre-existing corrupted 0-byte directory in the
> repo root (name = U+F022 + `hydra ` + trailing space) crashes pytest's
> root-directory collector. Running with `--rootdir=tests` from the repo root
> sidesteps it. That directory was **not** modified or deleted.

## Ignored-log decision

The working note `brain_memory/logs/system_changes.md` was intentionally
**not** committed: `brain_memory/logs/` is excluded by `.gitignore`. No
`git add -f` was used to override the ignore rule. The JARVIS feature is
fully committed without it.

## Next recommended validation

Run the local server and open the page in a browser:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8765
# then open http://127.0.0.1:8765/jarvis
```

Confirm the orb shows **ONLINE**, the eight panels populate (or show
`not connected` / `waiting for signal`), and the Safety Gates panel reports
the locked posture above.
