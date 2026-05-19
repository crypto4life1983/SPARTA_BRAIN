# Always-Used Brain Memory Context

Before doing any major work in this project, read the relevant Brain Memory files first.

Always read:
- `brain_memory/identity.md`
- `brain_memory/operating_rules.md`

For trading work, read:
- `brain_memory/projects/trading_bot/project.md`
- `brain_memory/projects/trading_bot/decisions.md`
- `brain_memory/projects/trading_bot/lessons.md`
- `brain_memory/projects/trading_bot/next_actions.md`

For Hydra/video work, read:
- `brain_memory/projects/hydra_video/project.md`
- `brain_memory/projects/hydra_video/decisions.md`
- `brain_memory/projects/hydra_video/lessons.md`
- `brain_memory/projects/hydra_video/next_actions.md`

For YouTube work, read:
- `brain_memory/projects/youtube_growth/project.md`
- `brain_memory/projects/youtube_growth/decisions.md`
- `brain_memory/projects/youtube_growth/lessons.md`
- `brain_memory/projects/youtube_growth/next_actions.md`

For affiliate work, read:
- `brain_memory/projects/affiliate_system/project.md`
- `brain_memory/projects/affiliate_system/decisions.md`
- `brain_memory/projects/affiliate_system/lessons.md`
- `brain_memory/projects/affiliate_system/next_actions.md`

Before changing code, follow the **Behavior Guardrails** below. Additionally:
- Add tests if helper code is created.

After work, append:
- A decision to the relevant `decisions.md`.
- A lesson to the relevant `lessons.md` if something was learned.
- A next action to the relevant `next_actions.md`.
- A summary to `brain_memory/logs/system_changes.md`.

## Behavior Guardrails

### Think Before Coding
Before making changes, identify the goal, assumptions, risks, and the smallest safe path. If the request is ambiguous or has multiple possible meanings, ask for clarification instead of guessing.

### Simplicity First
Prefer the simplest solution that solves the real problem. Do not over-engineer, add unnecessary abstractions, or create large systems when a small change is enough.

### Surgical Changes
Only modify files directly required for the task. Do not refactor unrelated code, rename things unnecessarily, or touch working systems without a clear reason.

### Goal-Driven Execution
Before implementing, define what success means. After changes, verify the result with the smallest relevant test, check, or proof. If tests cannot be run, explain exactly why.

### SPARTA Read-Only Default
For SPARTA_BRAIN, trading, automation, affiliate, YouTube upload, or external research systems, default to read-only analysis unless explicitly authorized to change them. Never touch credentials, live trading logic, broker execution, wallet/API keys, or production upload flows without explicit permission.

# SPARTA_BRAIN — Project Notes

Local AI dashboard at `C:\SPARTA_BRAIN\` running on FastAPI + Ollama.

## Clone Engine

Mahmoud's personal style clone. Lives at `SPARTACUS_CLONE_ENGINE/`,
wired into the dashboard at `/clone`.

### Two ways to use it (both work, both edit the same files)

**Dashboard** — `http://127.0.0.1:8765/clone` — three tabs:

- **Generate**: pick format (Instagram caption / YouTube Shorts script /
  sales reply / lead follow-up / DM), drop in topic or inbound message,
  click Generate. Copy button on the result.
- **Train**: form fields (type / input / output / notes). Click `+ Add to
  batch` to queue multiple examples, then `Train Clone` to run the
  pipeline. Shows the analyzer report inline.
- **Memory**: read-only view of `tone_rules.txt`, `response_patterns.txt`,
  `examples.json` with the latest backup timestamp.

**CLI** — same tools, no dashboard needed:

```bash
cd C:\SPARTA_BRAIN\SPARTACUS_CLONE_ENGINE
.venv\Scripts\python output\content_generator.py --type instagram "Your topic"
.venv\Scripts\python output\reply_generator.py --type sales "Incoming message"
.venv\Scripts\python auto_training\trainer.py
```

The dashboard route just imports the same modules through
`clone_bridge.py` (at the SPARTA_BRAIN root). CLI keeps working
unchanged — adding the dashboard didn't modify any clone-engine file.

### File layout

```
SPARTACUS_CLONE_ENGINE/
  personality/mahmoud_profile.txt    ← who Mahmoud is (manual edits OK)
  knowledge/business.txt             ← business knowledge (manual edits OK)
  knowledge/crypto.txt               ← crypto positions (manual edits OK)
  knowledge/mindset.txt              ← philosophy (manual edits OK)
  communication/tone_rules.txt       ← hard rules + auto-managed Learned section
  communication/response_patterns.txt← templates + auto-managed Learned Examples
  memory/examples.json               ← few-shot examples (auto-appended)
  output/content_generator.py        ← Instagram + YouTube generation
  output/reply_generator.py          ← Sales + Followup + DM replies
  auto_training/
    inbox/new_examples.json          ← drop new examples here
    processed/trained_examples.json  ← append-only history
    rejected/bad_examples.json       ← validation failures with reasons
    trainer.py                       ← runs the pipeline
    style_analyzer.py                ← extracts style patterns
    memory_updater.py                ← rewrites managed sections only
    README.md                        ← detailed usage docs
```

### What's auto-managed vs manual

- Manual edits are safe in `personality/`, `knowledge/`, and the rules
  ABOVE the `<!-- LEARNED_PATTERNS:BEGIN -->` markers in
  `communication/*.txt`.
- The Learned sections between the markers are rewritten on every
  training run. Edit the inbox, not the markers.
- Backups: every text file gets a `*.<timestamp>.bak` next to it before
  any rewrite. Examples.json gets the same treatment.

### Memory of memory

The Clone Engine reads ALL of these every time it generates:
personality + tone + patterns + business + mindset + crypto. Updating
any file changes the next generation - no restart needed.

### Future extensions (planned, not built)

- Gmail / WhatsApp / Instagram importers → auto-populate inbox
- ElevenLabs voice clone for matching audio output
- HeyGen video avatar for video replies
- Daily auto-training scheduler

## Animation Engine — Spartan Wallet Hydra Rule (permanent)

Every generated video must be treated like a **Spartan Wallet 2D animated
story**, not static illustrated slides. Channel identity: money mistakes,
discipline, crypto psychology, impulse buying, saving, trading mistakes, and
self-control. This standard is non-negotiable for every render:

- **Required 30s story spine**: hook, setup, temptation, conflict, consequence,
  judgment.
- **Character system**: Civilian is the tempted POV, Wallet is emotional
  resistance and interruption, Spartan is final authority, Narrator controls
  sharp hooks and short transitions.
- **Kaizen QA**: every render records hook strength, script quality,
  interaction, text overlap, subtitle bugs, voice volume, ending frame, pacing,
  and memorable moment in `kaizen_report.json`.

- **Character motion**: every scene has a `civilianAction` (walk_in / react /
  pick_up_phone) or `spartanAction` (step_forward). Never idle.
- **Camera motion**: every scene has a non-null `cameraAction`
  (zoom_in / pan_left / slow_push / pan_right / zoom_out / shake).
- **Background**: narrator = semantic bg via `_EVENT_BG`; spartan = dark_void;
  wallet = home. No scene should end up `sceneType: "default"` in production.
- **Visual event**: every scene must have at least one animated visual event
  when possible. Narrator: RuntimeError if missing. Civilian/wallet: automatic
  fallback (`salary_pop` for saving/invest keywords; `money_drain` otherwise).

Enforcement: `director_mode.py` repairs weak scripts into Spartan Wallet mode;
`animation_engine.py` `_director()` + narrator fail condition blocks scenes with
no visual event, missing bg, or idle action before render output is accepted.

## Other system docs

The full module map of SPARTA_BRAIN is at `/guide` — every feature has
a row in `system_manual_entries`. When you ship a new feature here, add
a row via `db.upsert_manual_entry()` so `/guide` stays accurate.
