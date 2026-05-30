# JARVIS Step 35 — Browser Speech-to-Text Input Fill Only

- **Generated:** 2026-05-30
- **Type:** UI speech-to-text wiring + tests + docs. No app.py change, no backend, no storage, no TTS.
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status
- **Ask API (Step 30):** `POST` http://127.0.0.1:8765/api/jarvis/ask

Step 35 turns the Step 34 *disabled* voice preview into an **active
speech-to-text control** that **fills the existing question box only**. Voice is
only a new way to **produce the question text**; everything downstream — the
classifier, the refusal, the read-only answer — is unchanged. It never
auto-submits, never calls the ask endpoint from voice, and stores no audio or
transcript. The operator must still click **“Ask read-only”** to send.

---

## 1. Relation to Steps 20–34

Step 26 shipped the display-only conversation shell; **30** the answer-only
`POST /api/jarvis/ask`; **31** the read-only ask UI; **32** the live/ASGI smoke;
**33** the docs-only voice-layer safety plan; **34** the UI-only **disabled**
voice preview shell. **Step 35** implements the first interactive roadmap item
from Step 33 — **browser STT that fills the input only**, with no backend, no
storage, no auto-submit, and no text-to-speech (TTS is deferred to Step 36).

---

## 2. Files changed (allowed files only)

- **`templates/jarvis.html`** — replaced the Step 34 disabled span with an
  **active** speech-to-text control. The control stays a non-interactive
  `<span role="button">` (`id="jvVoiceBtn"`) wired **only** with
  `addEventListener` (click + Enter/Space) — never a real
  `<button>`/`<form>`/submit. Added `wireVoice()` inside the existing render
  IIFE: it reads `window.SpeechRecognition || window.webkitSpeechRecognition`,
  and on a transcript writes `input.value` **only**. It never auto-submits,
  never fetches, and stores nothing. Added `.is-listening` / `.is-disabled` CSS
  states. The read-only ask flow and `{question}`-only payload are untouched.
- **`tests/test_jarvis_route.py`** — reconciled **3** Step 34 tests that
  asserted the OLD disabled state, then added a **Step 35** section (16 tests).
- **`docs/jarvis_step_35_voice_stt_input_fill/`** — this memo.

**Not done:** no `app.py` / `jarvis_conversation_safety.py` change; no endpoint;
no TTS (`SpeechSynthesis`); no `getUserMedia`/`MediaRecorder`/`AudioContext`/
`navigator.mediaDevices`; no external STT; no `fetch`/XHR from voice; no
audio/transcript storage; no `localStorage`/`sessionStorage`/`IndexedDB`/cookies;
no auto-submit; no call to `/api/jarvis/ask` from voice; no
refresh/execution/broker/paper/live control; no change to the `{question}`
payload or the `/api/jarvis/status` shape.

---

## 3. Step 34 tests reconciled (honest, surgical)

Step 35 **intentionally supersedes** the Step 34 disabled preview, so three
Step 34 tests had to change. Every still-valid safety invariant was kept:

| Step 34 test | Why it changed | What it still guards |
| --- | --- | --- |
| `..._voice_preview_text_appears` | Old `COMING NEXT` / `No microphone access yet` copy replaced by STT labels | still asserts `Voice preview` + `No audio or transcript is stored` |
| `..._voice_control_is_non_functional_span` | Control is now active (`Speak to fill`) not `Voice preview disabled` | still asserts `id=jvVoiceBtn` is a `<span role="button">`, **no** real `<button>`/`<form>`/`onclick`/submit/post |
| `..._no_microphone_or_audio_apis` | `SpeechRecognition`/`webkitSpeechRecognition` intentionally added | still forbids `getUserMedia` / `SpeechSynthesis` / `MediaRecorder` / `AudioContext` / `navigator.mediaDevices` |

---

## 4. STT input-fill summary

| Element | Detail |
| --- | --- |
| Location | Inside `#pConversation`, in the `#jvVoicePreview` block below the read-only ask note. |
| Control | `<span class="jv-voice-ctl" id="jvVoiceBtn" role="button" tabindex="0">Speak to fill</span>` — `addEventListener` (click + Enter/Space), never a real control. |
| Mechanism | `window.SpeechRecognition \|\| window.webkitSpeechRecognition` (browser Web Speech API only); `interimResults=false`, `maxAlternatives=1`, `lang=en-US`. |
| On result | `input.value = transcript; input.focus();` then status → *“Transcript ready — review it, then click ‘Ask read-only’.”* **No** submit, fetch, or storage. |
| Graceful no-op | If unavailable: control disables, shows *“Speech recognition unavailable in this browser.”*; the text input still works. |
| Ask flow | **Unchanged**: `#jvAskInput` + “Ask read-only” still POST only `{question}`; the classifier decides. |
| Persistent warning | **“JARVIS answers only. No execution. No trading control.”** retained. |

---

## 5. Voice safety scan (`templates/jarvis.html`)

| Check | Result |
| --- | --- |
| `window.SpeechRecognition` / `window.webkitSpeechRecognition` | ✓ present (allowed) |
| `getUserMedia`/`MediaRecorder`/`AudioContext`/`SpeechSynthesis`/`navigator.mediaDevices` | 0 ✓ |
| external STT / `fetch(` / `XMLHttpRequest` / URL **inside `wireVoice()`** | 0 ✓ |
| `localStorage`/`sessionStorage`/`indexedDB`/`document.cookie` | 0 ✓ |
| auto-submit tokens (`askJarvis`/`ask(`/`.submit(`/`.click(`/`requestSubmit`) in `wireVoice()` | 0 ✓ |
| voice writes `input.value = transcript` only | ✓ |
| ask payload `JSON.stringify({question: q})` | ✓ (1) |
| real `<button>`/`<form>`/`onclick`/`method="post"`/`type="submit"` | 0 ✓ |
| `/api/jarvis/refresh` | 0 ✓ |
| persistent warning | ✓ |

---

## 6. Tests

**Reconciled Step 34 tests:** 3 (see §3).
**New Step 35 tests (`test_jarvis_route.py`):** `..._page_renders_ok`,
`..._voice_stt_labels_appear`, `..._uses_browser_speech_recognition_only`,
`..._no_forbidden_audio_or_tts_apis`, `..._no_external_stt_or_fetch_in_voice`,
`..._no_browser_storage_tokens`, `..._voice_does_not_auto_submit`,
`..._voice_fills_input_only`, `..._graceful_when_unavailable`,
`..._ask_payload_remains_question_only`, `..._no_refresh_or_real_control`,
`..._persistent_warning_present`, `..._status_shape_unchanged`,
`..._spoken_forbidden_phrase_still_classifier_gated`,
`..._spoken_safe_phrase_is_answered`.

---

## 7. Validation

- `python -m py_compile app.py jarvis_conversation_safety.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py --rootdir=tests -q` → see run output
- `python -m json.tool docs/jarvis_step_35_voice_stt_input_fill/report.json`
  → **JSON_OK**
- `git diff --name-only` / `git diff --cached --name-only` → only allowed files;
  nothing staged.

---

## 8. Recommended next safe step

**Step 36 (JARVIS-VOICE-TTS, separate approval):** optional browser
`SpeechSynthesis` that reads the **returned answer only**, off by default /
clearly toggled. Never reads commands or the raw transcript; only after a
response is returned.

---

**Conclusion:** the voice preview is now an active speech-to-text control that
fills `#jvAskInput` only. It uses the browser Web Speech API exclusively, never
auto-submits, never calls the ask endpoint from voice, and stores no audio or
transcript. The operator must still click **“Ask read-only”**, so the existing
classifier decides safe vs forbidden for spoken questions exactly as for typed
ones. `app.py` and `jarvis_conversation_safety.py` are untouched; the
`{question}`-only payload, the persistent warning, and the
`/api/jarvis/status` shape are all unchanged.
