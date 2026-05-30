# JARVIS Step 33 — Voice Conversation Layer Safety Plan (docs-only)

- **Generated:** 2026-05-30
- **Type:** documentation / plan only. No code, UI, test, endpoint, or storage change.
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status
- **Ask API (Step 30):** `POST` http://127.0.0.1:8765/api/jarvis/ask

This plan designs the **safest path** to add voice/audio conversation to JARVIS
so the operator can eventually **speak** to JARVIS and **hear** answers, while
preserving the existing **read-only** safety model. Nothing is built here — no
microphone UI, no speech-to-text, no text-to-speech, no audio storage, no
endpoints.

---

## 1. Purpose & relation to Steps 20–32

Steps 20–24 polished and documented the read-only dashboard. Step 25 planned the
conversation layer; **26** shipped the display-only shell; **27** planned the
answer-only backend; **28** shipped the pure safety classifier; **29** wrote the
tests-first ask contract; **30** implemented the answer-only
`POST /api/jarvis/ask`; **31** wired the read-only ask UI; **32** ran the
live/ASGI smoke.

**Step 33 (this step)** plans how **voice** can ride on top of that *same text
pipeline* without weakening any guarantee. The key idea: **voice is only a new
way to PRODUCE the question text.** Everything downstream — classifier, refusal,
read-only answer — stays exactly as it is today.

---

## 2. Current committed baseline

| Step | Commit | | Step | Commit |
| --- | --- | --- | --- | --- |
| 20 | `4200253` | | 27 | `e961481` |
| 21 | `4f55aae` | | 28 | `a5b47b4` |
| 22 | `82ccf52` | | 29 | `ed8f23c` |
| 23 | `37d7dcc` | | 30 | `73e1cb0` |
| 24 | `9523da8` | | 31 | `f9ea464` |
| 25 | `6b88d9b` | | 32 | `b35f4be` |
| 26 | `f2268f3` | | | |

---

## 3. Current JARVIS conversation capability

- A **text ask UI** exists (`#jvAskInput` + “Ask read-only”).
- **`POST /api/jarvis/ask`** exists (Step 30).
- The **safety classifier** exists (`classify_jarvis_question`, Step 28).
- **Read-only answers only.**
- **No execution / trading / mutation.**

> Voice changes none of this. It only adds an alternate input source that ends up
> as the same `{question}` string posted to the same endpoint.

---

## 4. What “voice JARVIS” means

1. Operator **speaks** into the microphone.
2. The **browser** turns speech into **text** (transcript), locally.
3. The transcript text is sent to the **existing** `POST /api/jarvis/ask`.
4. The **existing safety classifier** still decides safe vs forbidden.
5. The **answer (or refusal)** is displayed exactly as today.
6. **Optionally**, the browser’s built-in **text-to-speech** reads the returned
   answer aloud.

---

## 5. Required voice safety pipeline

1. **Microphone permission** requested explicitly by the operator (no auto-listen).
2. **Speech-to-text** produces a transcript **in the browser**.
3. **Transcript preview** is shown (it fills the existing input).
4. Operator **confirms** by clicking the existing **“Ask read-only”** control
   (no auto-submit).
5. `POST /api/jarvis/ask` receives **only** `{question: transcript}`.
6. The **classifier refuses** forbidden content (trading/execution/mutation),
   unchanged.
7. The **response** is displayed.
8. **Optional TTS** reads the response **only after** the answer is returned —
   never the raw transcript, never a command.

---

## 6. What voice must **never** do

- Bypass the classifier
- Execute commands
- Trigger scripts
- Refresh status
- Write files
- Save audio
- Save transcripts
- Create chat logs
- Control broker / paper / live trading
- Place / approve trades
- Auto-submit dangerous (or any) requests

---

## 7. Browser technology options

- **Speech-to-text (first version):** Web Speech API
  (`SpeechRecognition` / `webkitSpeechRecognition`) where available —
  browser-native, no server round-trip for audio.
- **Text-to-speech:** browser `SpeechSynthesis` (`window.speechSynthesis`).
- **Local/offline STT:** allowed **later only with separate approval**
  (on-device model). Not in scope now.
- **External STT APIs:** **blocked for now** — any cloud STT (sending audio
  off-device) changes the privacy/data-egress posture and needs separate
  explicit approval.
- **Graceful degradation:** if the Web Speech API is unavailable, the voice
  control does nothing harmful and the text input keeps working as today.

---

## 8. Privacy rules

- **No audio storage** (nothing saved to disk, server, or browser storage).
- **No transcript storage.**
- **No** localStorage / sessionStorage / IndexedDB / cookies for voice data.
- **No server-side logs** of audio or transcripts.
- **No external STT API** in the first version (audio never leaves the device).
- Transcript exists only **transiently** in the input until the operator submits
  or clears it.

---

## 9. UX design

- **“Voice preview only” first** — prove capture + transcript with zero
  auto-action.
- **Microphone control clearly labeled “Voice preview”** (never “Run”,
  “Execute”, “Trade”, “Approve”, “Refresh”, or “Talk”).
- **Transcript appears in the input** (`#jvAskInput`).
- Operator **must click “Ask read-only”** to send.
- **No auto-submit** in the first version.
- **TTS optional and disabled by default** (or behind a clearly labeled,
  off-by-default toggle); it only ever reads a **returned answer**.
- Keep the existing **“JARVIS answers only. No execution. No trading control.”**
  warning visible for the voice affordance.

---

## 10. Test plan for future implementation

- No audio-storage tokens (no `MediaRecorder` save, no blob persistence).
- No localStorage / sessionStorage / IndexedDB / cookie usage.
- Transcript is sent **only** as `{question}`; payload carries no other field.
- No `command` / `action` / `execute` fields posted.
- Forbidden **voice-transcribed** requests (e.g. spoken “place a trade”) are
  refused by the classifier exactly like typed ones.
- `/api/jarvis/status` shape unchanged.
- No `/api/jarvis/refresh` endpoint or wiring.
- No execution / trading controls; mic control labeled “Voice preview”, submit
  stays “Ask read-only”.
- Graceful **no-op** when the Web Speech API is unavailable.
- TTS only reads a **server-returned answer**, after the response, off by default.

---

## 11–14. Roadmap (each step separately approved)

| Step | Name | Scope |
| --- | --- | --- |
| **34** | Voice preview shell (UI-only) | Add a clearly-labeled **“Voice preview”** control to the shell. **No** backend change, **no** storage, **no** auto-submit, **no** TTS. No `<button>`/`<form>`/`onclick`/`method="post"`. |
| **35** | Browser STT → fill input only | Wire speech-to-text to **fill the existing input only**. No auto-submit (operator clicks “Ask read-only”). No audio/transcript storage, no external STT. Graceful no-op if unavailable. |
| **36** | Optional browser TTS | `SpeechSynthesis` reads the **returned answer only**, off by default / clearly toggled. Never reads commands or the raw transcript; only after a response. |
| **37** | Live end-to-end voice smoke | Speak → transcript → “Ask read-only” → answer/refusal → optional TTS. Validation/report-only; spoken safe + forbidden questions behave identically to typed, with no storage/refresh/execution. |

---

## 15. Validation

- `python -m json.tool docs/jarvis_step_33_voice_layer_safety_plan/report.json`
  → **JSON_OK**
- `git diff --name-only` → no tracked files changed
- `git diff --cached --name-only` → nothing staged

---

**Conclusion:** Voice JARVIS is planned as a **thin, additive input layer**: the
browser captures speech, turns it into a transcript **locally**, the operator
**confirms** by clicking the existing “Ask read-only” control, and the
**existing** `/api/jarvis/ask` + classifier handle everything downstream
unchanged. The first version is **preview-only** — no auto-submit, no
audio/transcript storage, no external STT, and optional off-by-default TTS that
reads only returned answers. Steps 34–37 sequence the build, each separately
approved, so voice **never** weakens the read-only, no-execution safety model.
