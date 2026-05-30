# JARVIS Step 34 — UI-Only Voice Preview Shell

- **Generated:** 2026-05-30
- **Type:** UI-only + tests + docs. No app.py change, no backend, no audio APIs.
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status
- **Ask API (Step 30):** `POST` http://127.0.0.1:8765/api/jarvis/ask

This step adds a **visible, display-only** voice-preview area to the existing
JARVIS conversation panel so the operator can see **where voice will live
later**. It implements **no** real speech-to-text or text-to-speech, requests
**no** microphone, and captures/stores **no** audio or transcript. The existing
read-only text ask flow is unchanged.

---

## 1. Relation to Steps 20–33

Step 26 shipped the display-only conversation shell; **30** the answer-only
`POST /api/jarvis/ask`; **31** the read-only ask UI; **32** the live/ASGI smoke;
**33** the docs-only **voice layer safety plan**. **Step 34** implements the
first roadmap item from Step 33 — a **UI-only voice preview shell** with no
backend, no audio APIs, and no storage.

---

## 2. Files changed (allowed files only)

- **`templates/jarvis.html`** — added a display-only voice-preview subsection
  (`id="jvVoicePreview"`) **inside** the existing `#pConversation` panel, plus
  minimal CSS (`.jv-voice-preview` / `.jv-voice-head` / `.jv-voice-row` /
  `.jv-voice-ctl`). The control is a **non-interactive**
  `<span role="button">` labeled **“Voice preview disabled”**. No audio API, no
  storage, no auto-submit; the existing ask flow and payload are untouched.
- **`tests/test_jarvis_route.py`** — added a Step 34 section (9 tests).
- **`docs/jarvis_step_34_voice_preview_shell/`** — this memo.

**Not done:** no `app.py` / `jarvis_conversation_safety.py` change; no endpoint;
no STT/TTS; no microphone request / media-capture; no
`SpeechRecognition`/`webkitSpeechRecognition`/`SpeechSynthesis`/`MediaRecorder`/
`AudioContext`; no audio/transcript storage; no
localStorage/sessionStorage/IndexedDB/cookies; no auto-submit; no
refresh/execution/broker/paper/live control; no change to the `/api/jarvis/ask`
payload (still `{question}` only) or `/api/jarvis/status` shape.

---

## 3. UI shell summary

| Element | Detail |
| --- | --- |
| Location | Inside the existing `#pConversation` “Talk to JARVIS” panel, below the read-only ask note. |
| Container | `div.jv-voice-preview` `id="jvVoicePreview"`. |
| Labels | **Voice preview** · **COMING NEXT** (the “Coming next” tag) · **No microphone access yet** · **No audio is recorded or stored**. |
| Control | `<span class="jv-voice-ctl" role="button" tabindex="0" aria-disabled="true">Voice preview disabled</span>` — non-interactive, no handler, never auto-submits. |
| Ask flow | **Unchanged**: `#jvAskInput` + “Ask read-only” still POST only `{question}`. |
| Persistent warning | **“JARVIS answers only. No execution. No trading control.”** retained. |

---

## 4. Voice safety scan (`templates/jarvis.html`)

| Check | Result |
| --- | --- |
| “Voice preview” text | ✓ (3) |
| “No microphone access yet” | ✓ |
| “No audio is recorded or stored” | ✓ |
| `getUserMedia`/`SpeechRecognition`/`webkitSpeechRecognition`/`SpeechSynthesis`/`MediaRecorder`/`AudioContext`/`navigator.mediaDevices` | 0 ✓ |
| `localStorage`/`sessionStorage`/`indexedDB`/`document.cookie` | 0 ✓ |
| real `<button>`/`<form>`/`onclick`/`method="post"`/`type="submit"` | 0 ✓ |
| `/api/jarvis/refresh` | 0 ✓ |
| ask payload `JSON.stringify({question: q})` | ✓ (1) |
| persistent warning | ✓ |

---

## 5. Tests

**New Step 34 tests (`test_jarvis_route.py`):** `..._page_renders_ok`,
`..._voice_preview_text_appears`, `..._voice_control_is_non_functional_span`,
`..._no_microphone_or_audio_apis`, `..._no_browser_storage_tokens`,
`..._no_refresh_endpoint_in_template`, `..._ask_payload_remains_question_only`,
`..._persistent_warning_present`, `..._status_shape_unchanged`.

---

## 6. Validation

- `python -m py_compile app.py jarvis_conversation_safety.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py --rootdir=tests -q` →
  **208 passed, 0 failed, 0 skipped**
- `python -m json.tool docs/jarvis_step_34_voice_preview_shell/report.json`
  → **JSON_OK**

---

## 7. Recommended next safe step

**Step 35 (JARVIS-VOICE-STT-FILL, separate approval):** wire browser
speech-to-text to **fill the existing input only** — no auto-submit, no
audio/transcript storage, no external STT, graceful no-op when the Web Speech
API is unavailable.

---

**Conclusion:** a display-only voice-preview shell now sits inside the
conversation panel — clearly labeled *Voice preview / Coming next / No
microphone access yet / No audio is recorded or stored* — with a non-interactive
“Voice preview disabled” span. It adds no microphone request, no audio/STT/TTS
API, no recorder, no storage, and no auto-submit. The read-only text ask flow,
the `{question}`-only payload, the persistent warning, and the
`/api/jarvis/status` shape are all unchanged. `app.py` and
`jarvis_conversation_safety.py` are untouched.
