# JARVIS Step 36 — Optional Browser TTS Answer Readback

- **Generated:** 2026-05-30
- **Type:** UI text-to-speech wiring + tests + docs. No app.py change, no backend, no server TTS, no storage.
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status
- **Ask API (Step 30):** `POST` http://127.0.0.1:8765/api/jarvis/ask

Step 36 adds **optional** browser text-to-speech so the operator can have the
**returned answer read aloud** after a successful read-only ask. TTS is **off by
default**, **click-gated**, and **never auto-speaks**. It reads **only** the last
rendered answer (or the refusal explanation) — never the question, never any
command/action/execute field. It makes **no** network call and stores **nothing**.

---

## 1. Relation to Steps 20–35

Step 30 shipped the answer-only `POST /api/jarvis/ask`; **31** the read-only ask
UI; **33** the docs-only voice-layer safety plan; **34** the disabled voice
preview; **35** browser speech-to-text that fills the input only. **Step 36**
implements the final voice roadmap item from Step 33 — optional browser
`SpeechSynthesis` that reads returned answers aloud, off by default, with no
backend, no storage, and no auto-speak.

---

## 2. Files changed (allowed files only)

- **`templates/jarvis.html`** — added an optional **Voice output** block inside
  the existing `#jvVoicePreview` area: a non-interactive
  `<span role="button" id="jvSpeakAnswerBtn">Read last answer</span>` plus a
  status line. Added a module-level `jvLastAnswerText`, set inside `renderAsk`
  **only** from the model answer (`d.answer`) or refusal explanation
  (`d.refusal_reason`) — reset on every response. Added `wireSpeak()`: it uses
  `window.speechSynthesis` + `SpeechSynthesisUtterance`, is **off by default**,
  speaks only on explicit click / Enter / Space, and degrades gracefully to
  *“Voice output unavailable in this browser.”* STT and the `{question}`-only
  ask flow are unchanged.
- **`tests/test_jarvis_route.py`** — reconciled **2** prior audio scans that
  forbade `speechSynthesis` (Step 36 intentionally adds browser TTS), then added
  a **Step 36** section (16 tests).
- **`docs/jarvis_step_36_voice_tts_answer_readback/`** — this memo.

**Not done:** no `app.py` / `jarvis_conversation_safety.py` change; no endpoint;
no server-side TTS; no `getUserMedia`/`MediaRecorder`/`AudioContext`/
`navigator.mediaDevices`; no external TTS API; no `fetch`/XHR from the read-aloud
handler; no audio/transcript storage; no `localStorage`/`sessionStorage`/
`IndexedDB`/cookies; no auto-submit; no auto-speak; no refresh/execution/broker/
paper/live control; no change to the `{question}` payload or the
`/api/jarvis/status` shape.

---

## 3. Prior tests reconciled (honest, surgical)

Step 36 **intentionally adds** browser `SpeechSynthesis`, so two prior audio
scans that forbade it had to change. Every genuinely-dangerous API stays banned:

| Test | Why it changed | What it still guards |
| --- | --- | --- |
| `..._step_34_no_microphone_or_audio_apis` | `speechSynthesis` intentionally added | still forbids `getUserMedia` / `MediaRecorder` / `AudioContext` / `navigator.mediaDevices` |
| `..._step_35_no_forbidden_audio_or_tts_apis` | `speechSynthesis` intentionally added | still forbids `getUserMedia` / `MediaRecorder` / `AudioContext` / `navigator.mediaDevices` |

---

## 4. TTS answer-readback summary

| Element | Detail |
| --- | --- |
| Location | Inside `#jvVoicePreview`, below the speech-to-text row. |
| Labels | **Voice output** · **READ ANSWER ALOUD** tag · **Off by default** · **Reads returned answers only**. |
| Control | `<span class="jv-voice-ctl is-disabled" id="jvSpeakAnswerBtn" role="button" tabindex="0" aria-disabled="true">Read last answer</span>` — disabled until an answer exists; `addEventListener` (click + Enter/Space); never a real button/form/submit. |
| Mechanism | `window.speechSynthesis` + `new SpeechSynthesisUtterance(text)`; `lang=en-US`, `rate=1`; `synth.cancel()` before each utterance. |
| Source text | `jvLastAnswerText`, set in `renderAsk` **only** from `String(d.answer)`, else (refused) `String(d.refusal_reason)`. Reset to `''` on every response. |
| Off by default | Control starts disabled; the response renderer makes **no** speak call. Speech happens only on an explicit click after an answer renders. |
| Graceful no-op | If `speechSynthesis`/`SpeechSynthesisUtterance` unavailable: control disables, shows *“Voice output unavailable in this browser.”* |
| STT unchanged | `wireVoice()` still fills `#jvAskInput` only; no auto-submit, no fetch. |
| Ask flow | **Unchanged**: `#jvAskInput` + “Ask read-only” still POST only `{question}`. |
| Persistent warning | **“JARVIS answers only. No execution. No trading control.”** retained. |

---

## 5. Voice safety scan (`templates/jarvis.html`)

| Check | Result |
| --- | --- |
| `window.speechSynthesis` / `SpeechSynthesisUtterance` | ✓ present (allowed) |
| `getUserMedia`/`MediaRecorder`/`AudioContext`/`navigator.mediaDevices` | 0 ✓ |
| external TTS / `fetch(` / URL **inside `wireSpeak()`** | 0 ✓ |
| `localStorage`/`sessionStorage`/`indexedDB`/`document.cookie` | 0 ✓ |
| auto-speak calls **inside `renderAsk()`** (`.speak(`/`SpeechSynthesisUtterance`) | 0 ✓ |
| total `synth.speak(u)` calls (the single click-gated one) | 1 ✓ |
| read-aloud reads `input.value`/`jvAskInput`/`d.command`/`d.action`/`d.execute` | 0 ✓ |
| ask payload `JSON.stringify({question: q})` | ✓ (1) |
| real `<button>`/`<form>`/`onclick`/`method="post"`/`type="submit"` | 0 ✓ |
| `/api/jarvis/refresh` | 0 ✓ |
| persistent warning | ✓ |

---

## 6. Tests

**Reconciled prior tests:** 2 (see §3).
**New Step 36 tests (`test_jarvis_route.py`):** `..._page_renders_ok`,
`..._tts_labels_appear`, `..._uses_browser_speech_synthesis_only`,
`..._no_external_tts_or_fetch_in_speak`, `..._no_recorder_or_capture_apis`,
`..._no_browser_storage_tokens`, `..._no_auto_speak_on_response`,
`..._read_aloud_requires_explicit_control`, `..._tts_reads_answer_not_question`,
`..._speak_text_is_answer_or_refusal_only`, `..._stt_still_fills_input_only`,
`..._ask_payload_remains_question_only`, `..._no_refresh_or_real_control`,
`..._persistent_warning_present`, `..._graceful_when_unavailable`,
`..._status_shape_unchanged`.

---

## 7. Validation

- `python -m py_compile app.py jarvis_conversation_safety.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py --rootdir=tests -q` →
  **239 passed, 0 failed, 0 skipped**
- `python -m json.tool docs/jarvis_step_36_voice_tts_answer_readback/report.json`
  → **JSON_OK**
- `git diff --name-only` / `git diff --cached --name-only` → only allowed files;
  nothing staged.

---

## 8. Recommended next safe step

**Step 37 (JARVIS-VOICE-LIVE-SMOKE, separate approval):** a live end-to-end
voice smoke — speak → transcript fills input → click “Ask read-only” →
answer/refusal → optional click “Read last answer”. Validation/report-only;
spoken safe + forbidden questions behave identically to typed, with no storage,
no refresh, no execution, and no auto-speak.

---

**Conclusion:** JARVIS can now optionally read a returned answer aloud, but only
when the operator clicks the off-by-default **“Read last answer”** control. It
uses the browser `SpeechSynthesis` API exclusively, reads only the last answer
(or refusal explanation), never the question or any command, never auto-speaks,
makes no network call, and stores nothing. STT still fills the input only; the
`{question}`-only payload, the persistent warning, and the `/api/jarvis/status`
shape are unchanged. `app.py` and `jarvis_conversation_safety.py` are untouched.
