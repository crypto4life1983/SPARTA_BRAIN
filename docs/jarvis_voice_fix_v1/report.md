# JARVIS Voice Fix v1

**Date:** 2026-05-31
**Scope:** JARVIS voice input only. Read-only console preserved. No Strategy
Factory, trading files, command execution, audio storage, transcript storage,
or auto-submit touched.
**Verdict:** `JARVIS_VOICE_FIXED` (with a documented browser-limit fallback —
see Limits).

---

## 1. Symptom

Chrome shows `Voice input error: not-allowed` when clicking **Speak to fill**,
even though the site microphone permission is already set to *Allow*. The voice
UI renders but speech-to-text never starts.

## 2. Diagnosis

The voice control uses the browser **Web Speech API**
(`window.SpeechRecognition || window.webkitSpeechRecognition`) — see
`templates/jarvis.html`, `wireVoice()`. The old handler called `rec.start()`
and, on failure, printed the raw error code with no explanation.

Chrome raises `not-allowed` for `SpeechRecognition.start()` in several distinct
situations that all look identical to the user, and a site permission reading
"Allow" does **not** rule them out:

1. **Insecure origin (most common).** Web Speech recognition only runs on a
   *secure context*: HTTPS, or the loopback hosts `localhost` / `127.0.0.1`.
   When the dashboard is opened over plain HTTP on a LAN name or IP
   (e.g. `http://192.168.x.x:8765/jarvis`), Chrome blocks the microphone and
   reports `not-allowed` regardless of the site permission. `127.0.0.1:8765`
   works; a LAN address does not.
2. **Browser-wide / OS mic block.** The per-site permission can be "Allow"
   while the browser-level microphone setting (or another app holding the
   device) blocks capture, surfacing as `not-allowed` / `service-not-allowed`.
3. **`start()` race.** Calling `start()` again before the previous session has
   fully ended throws `InvalidStateError`, which the old code swallowed
   silently, leaving the user with no feedback.

The other error codes (`no-speech`, `aborted`, `audio-capture`, `network`) were
collapsed into the same generic message, so a user could not tell "permission
blocked" from "I didn't say anything".

### Why we did NOT add `getUserMedia`

`SpeechRecognition` does not require `getUserMedia`/`MediaRecorder`, and the
read-only console's test suite explicitly **forbids** raw-capture APIs
(`getUserMedia`, `MediaRecorder`, `AudioContext`, `navigator.mediaDevices`) so
the console can never record or store audio. The fix therefore relies only on
the secure-context check, the **Permissions API** (state read, no capture), and
clearer error mapping.

## 3. Fix

Rewrote `wireVoice()` in `templates/jarvis.html`:

- **Secure-context guard.** Detects `window.isSecureContext` plus the loopback
  hosts. On an insecure origin it disables the control and explains *exactly*
  why (`not-allowed` because the page is not on localhost/127.0.0.1/HTTPS) and
  points the user to type instead.
- **Permissions API hint (no capture).** `navigator.permissions.query({name:
  'microphone'})` reads the grant state up front: a `denied` state is explained
  before the user clicks; a `granted` state gives a ready prompt; an
  `onchange` handler keeps the hint live. Unsupported browsers skip silently.
- **Separated error messages.** `not-allowed` / `service-not-allowed`,
  `no-speech`, `aborted`, `audio-capture`, and `network` now each map to a
  distinct, actionable message. Permission-blocked tells the user how to allow
  the mic and to check the browser-wide setting / other apps.
- **`start()` race guard.** A thrown `InvalidStateError` now shows a calm retry
  hint instead of being swallowed.
- **Graceful fallback everywhere.** Every failure path keeps the typed
  read-only flow working and tells the user they can still type the question.

### Read-only guarantees preserved

- Transcript fills `#jvAskInput` **only** (`input.value = transcript`). No
  auto-submit, no `fetch`, no endpoint call from voice.
- No audio or transcript is stored (no recorder, no storage APIs).
- The operator must still click **Ask read-only**, so the existing safety
  classifier always decides safe vs forbidden — even for spoken questions.
- Voice **output** (`wireSpeak()`) is unchanged and still reads only the last
  returned answer / refusal text (`jvLastAnswerText`), never the question or
  any command field.

## 4. Files changed

| File | Change |
|------|--------|
| `templates/jarvis.html` | Rewrote `wireVoice()` with secure-context guard, Permissions API hint, separated error mapping, `start()` race guard, graceful fallbacks. |
| `tests/test_jarvis_route.py` | Added 9 "JARVIS voice fix v1" tests. |

No other files touched. No new routes, no `/api/jarvis/refresh`, no trading
code, no execution path.

## 5. Tests

New tests in `tests/test_jarvis_route.py`:

- `test_jarvis_voicefix_v1_page_renders_ok`
- `test_jarvis_voicefix_v1_checks_secure_context`
- `test_jarvis_voicefix_v1_separates_error_codes`
- `test_jarvis_voicefix_v1_uses_permissions_api_not_capture`
- `test_jarvis_voicefix_v1_no_capture_apis_in_template`
- `test_jarvis_voicefix_v1_still_fills_input_only_no_network`
- `test_jarvis_voicefix_v1_graceful_fallback_present`
- `test_jarvis_voicefix_v1_output_reads_answer_not_question`
- `test_jarvis_voicefix_v1_no_real_control_or_refresh`

### Results

Run with the project venv (`.venv`). Note: a pre-existing corrupt directory in
the repo root (on-disk name `hydra ` — a private-use char + trailing
space) breaks pytest's root enumeration, so the suite is run from inside
`tests/` with `PYTHONPATH=..` and `--noconftest`. This is an environment
artifact unrelated to this change.

```
PYTHONPATH=.. .venv/Scripts/python -m pytest \
  test_jarvis_route.py test_jarvis_conversation_safety.py \
  --noconftest -q -p no:cacheprovider
=> 283 passed, 446 warnings

PYTHONPATH=.. .venv/Scripts/python -m pytest \
  test_jarvis_factory_panels.py test_jarvis_ask_contract.py \
  test_jarvis_snapshot_report.py --noconftest -q
=> 134 passed
```

All JARVIS tests pass, including the existing read-only / no-capture /
no-auto-submit / classifier-gating guards.

## 6. Validation

- `/jarvis` returns HTTP 200 (TestClient route tests pass).
- Voice UI renders (`Voice preview`, `Speak to fill`, status line).
- No trading routes or actions added; `git diff` touches only the template and
  the test file; no trading/broker/order/execute/`/api/` tokens in the template
  diff.
- Existing JARVIS test suite green.

## 7. Limits (browser-dependent)

If a user is on a genuinely unsupported browser, or the OS/browser blocks the
microphone outside the page's control, the Web Speech API cannot be made to
work from page code. In those cases the control degrades gracefully: it
disables with a clear reason and the typed read-only flow continues to work.
For those environments the practical verdict is
`JARVIS_VOICE_PARTIAL_BROWSER_LIMIT`. In the reported case (Chrome, permission
allowed), the dominant cause is an insecure origin; opening the dashboard on
`http://127.0.0.1:8765/jarvis` plus the new diagnostics resolves it →
`JARVIS_VOICE_FIXED`.

## 8. Commit status

Not committed — awaiting approval per the bundle's commit policy.
`git status`: `templates/jarvis.html` and `tests/test_jarvis_route.py` modified;
report files added under `docs/jarvis_voice_fix_v1/`.
