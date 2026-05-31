# JARVIS Voice Conversation Mode

**Date:** 2026-05-31
**Scope:** JARVIS voice input/output only. Adds an optional hands-free
conversation mode beside the existing preview mode. Read-only console
preserved. No Strategy Factory, trading files, command execution, broker /
paper / live control, audio storage, transcript storage, or new endpoints
touched.
**Verdict:** `JARVIS_VOICE_CONVERSATION_READONLY` — conversation mode ships as
an optional toggle and grants **no new capability**; it only composes two
already-authorized, click-gated actions (Ask read-only + Read last answer).

---

## 1. Goal

Add an optional Alexa-style hands-free loop on top of the existing voice UI:

1. Click the mic.
2. Speech is captured.
3. A transcript is generated.
4. The transcript is auto-submitted to the **read-only** Ask endpoint.
5. The answer (or refusal) is received.
6. The answer is read aloud automatically.
7. The UI returns to ready.

The existing **Voice Preview Mode** (transcript fills the question box only;
operator must click *Ask read-only*) must continue to exist unchanged. A clear
toggle switches between the two. Interruptions (no-speech, aborted, permission
denied, overlapping requests, barge-in) must be handled gracefully.

## 2. Safety model — why this stays read-only

Conversation mode adds **no new server capability**. It calls the *same*
answer-only `POST /api/jarvis/ask` endpoint that the typed flow already uses,
sending **only** the `{question}` field. Every question — typed or spoken —
still passes through the existing `jarvis_conversation_safety` classifier, so
forbidden execution / trading / mutation requests are refused exactly as
before. The auto-read step uses the browser `SpeechSynthesis` API on the
already-rendered answer text (`jvLastAnswerText`) — the same text the manual
"Read last answer" button reads. In short, conversation mode is a client-side
composition of two actions the operator can already trigger by hand; it cannot
do anything they could not already do.

No `getUserMedia` / `MediaRecorder` / `AudioContext` / `navigator.mediaDevices`
is used (the read-only console forbids raw-capture APIs). No `localStorage` /
`sessionStorage` / `indexedDB` / `document.cookie`. No new routes. No trading,
broker, paper, live, refresh, or execution wiring.

## 3. Implementation (`templates/jarvis.html`)

### Mode toggle (HTML)
A `role="radiogroup"` with two `role="radio"` **spans** (never real form
controls): `jvModePreview` (default, `is-active`/`aria-checked=true`) and
`jvModeConversation`. A live hint (`jvModeHint`) explains the current mode.

### Shared helpers (placed outside per-function test slices)
- `jvPostQuestion(q)` — POSTs `{question}` only to `/api/jarvis/ask`, returns
  the parsed JSON. Used by both the typed Ask flow and conversation mode.
- `jvSpeakAnswer(onEnd)` — reads **only** `jvLastAnswerText` aloud via
  `SpeechSynthesis`; cancels any queued speech first; calls `onEnd` when speech
  finishes / errors / is skipped so the turn can return to ready. Never reads
  the question or any command field.
- `jvRunConversation(transcript, setStatus)` — the turn: ask read-only →
  `renderAsk` → auto read aloud → ready. Releases the busy guard only when the
  whole turn settles (incl. the `.catch` for endpoint failures).
- `wireVoiceMode()` — toggles the two spans (class + `aria-checked`), swaps the
  hint text, **cancels in-flight speech**, and clears `jvVoiceBusy` on every
  switch so a half-finished turn never bleeds into the next.

### Conversation flow wired into `wireVoice()`
- `jvVoiceMode` (`'preview'` | `'conversation'`) and `jvVoiceBusy` (single-flight
  guard) state vars.
- `start()`: ignores the click if `listening || jvVoiceBusy` (overlap guard);
  cancels any active read-aloud (**barge-in**); sets `jvVoiceBusy = true`;
  wraps `rec.start()` to surface a calm retry hint on `InvalidStateError`.
- `onresult`: both modes fill `input.value` first (operator always sees the
  text). In conversation mode it sets `convStarted = true` and calls
  `jvRunConversation`; in preview mode it just shows "Transcript ready — review
  it, then click Ask read-only."
- `onend`: clears `jvVoiceBusy` only when `!convStarted` (in conversation mode
  the turn clears its own guard after ask + read-aloud).
- `onerror`: resets `listening`/`convStarted`/`jvVoiceBusy` and shows a
  per-code message (no-speech, aborted, not-allowed, audio-capture, network).

### `renderAsk` stays speak-free
The render function still resets `jvLastAnswerText` and disables the speak
button on every response; it never calls the speak helper. Speech happens only
*after* `renderAsk`, driven by `jvRunConversation`. So a **manual** ask never
auto-speaks — the Step 36 invariant is preserved.

## 4. Interruption handling

| Situation | Handling |
|-----------|----------|
| Overlapping clicks | `if(listening \|\| jvVoiceBusy) return;` single-flight guard |
| Barge-in (speak while answer is reading) | `speechSynthesis.cancel()` in `start()` and on mode switch |
| `no-speech` | Distinct status: "No speech detected. Try again or type." |
| `aborted` | Distinct status; guards reset; typing still works |
| Permission denied (`not-allowed` / `service-not-allowed`) | Distinct actionable status |
| `start()` race (`InvalidStateError`) | Caught; calm retry hint; busy guard released |
| Endpoint failure | `.catch` renders a read-only error note, releases guard, returns to ready |

Every failure path falls back to the typed read-only flow.

## 5. Files changed

| File | Change |
|------|--------|
| `templates/jarvis.html` | Mode toggle HTML + CSS; shared helpers `jvPostQuestion` / `jvSpeakAnswer` / `jvRunConversation` / `wireVoiceMode`; conversation flow + interruption handling in `wireVoice()`; `wireAsk` reuses `jvPostQuestion`. |
| `tests/test_jarvis_route.py` | Added 17 conversation-mode tests; clarified Step 35/36 comments to acknowledge mode-gated conversation. |

No other files touched. No new routes, no `/api/jarvis/refresh`, no trading
code, no execution path.

## 6. Tests

17 new conversation-mode tests in `tests/test_jarvis_route.py`:

- `test_jarvis_convo_page_renders_ok`
- `test_jarvis_convo_both_mode_toggles_present`
- `test_jarvis_convo_preview_is_default`
- `test_jarvis_convo_post_helper_is_question_only_readonly`
- `test_jarvis_convo_runner_submits_readonly_then_reads_answer`
- `test_jarvis_convo_speak_helper_reads_answer_not_question`
- `test_jarvis_convo_overlap_single_flight_guard`
- `test_jarvis_convo_interruption_codes_handled`
- `test_jarvis_convo_barge_in_cancels_active_speech`
- `test_jarvis_convo_gated_on_mode_and_preview_unchanged`
- `test_jarvis_convo_renderask_still_never_auto_speaks`
- `test_jarvis_convo_no_capture_or_storage_apis`
- `test_jarvis_convo_no_real_control_or_refresh`
- `test_jarvis_convo_ask_payload_remains_question_only`
- `test_jarvis_convo_spoken_forbidden_phrase_still_refused`
- `test_jarvis_convo_spoken_safe_phrase_is_answered`
- `test_jarvis_convo_status_shape_unchanged`

### Results

Run with the project venv (`.venv`). Note: a pre-existing corrupt directory in
the repo root (on-disk name `hydra ` — a private-use char + trailing space)
breaks pytest's root enumeration, so the suite is run from inside `tests/` with
`PYTHONPATH=..` and `--noconftest`. Environment artifact, unrelated to this
change.

```
PYTHONPATH=.. .venv/Scripts/python -m pytest \
  test_jarvis_route.py test_jarvis_conversation_safety.py \
  --noconftest -q -p no:cacheprovider
=> 301 passed   (was 283; +17 conversation tests, +1 prior)

PYTHONPATH=.. .venv/Scripts/python -m pytest \
  test_jarvis_factory_panels.py test_jarvis_ask_contract.py \
  test_jarvis_snapshot_report.py --noconftest -q
=> 134 passed
```

All JARVIS tests pass, including the existing read-only / no-capture /
no-auto-submit / no-auto-speak / classifier-gating guards.

## 7. Validation

- `/jarvis` returns HTTP 200; both mode toggles render; preview is default.
- Conversation mode auto-submits read-only and reads the answer aloud;
  preview mode still only fills the question box.
- Ask payload is `{question}` only; classifier still gates every spoken
  question (spoken forbidden phrase → refused; spoken safe phrase → answered).
- No capture/storage APIs, no real controls, no refresh/execution/trading
  wiring in the template diff.
- `/api/jarvis/status` shape unchanged.

## 8. Commit status

Not committed — awaiting approval per the bundle's commit policy. `git status`:
`templates/jarvis.html` and `tests/test_jarvis_route.py` modified; report files
added under `docs/jarvis_voice_conversation_mode/`.
