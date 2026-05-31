# JARVIS Step 49 — Live-Server Restart Protocol (Documentation Only)

- **Generated:** 2026-05-30
- **Type:** documentation only. No restart performed. No `app.py`, template,
  test, trading, or `storage/jarvis/snapshots` change.
- **HEAD at writing:** `8133af3` ("Add JARVIS Step 48 live snapshot compare smoke")

This memo gives the operator a **safe, manual** protocol to restart the local
JARVIS/SPARTA dashboard server on `127.0.0.1:8765` so it serves the **current**
committed code. It is needed because Step 48 proved the background `:8765`
process was **stale** and did not serve the Step 47 ask behavior. This document
restarts nothing itself — it only records the steps for the operator to run.

---

## 1. Evidence from Step 48 (why a restart is needed)

- **In-process FastAPI `TestClient` served Step 47 behavior correctly.** Bound to
  the current committed `app` module, `POST /api/jarvis/ask {"question":"what
  changed since last check?"}` returned `refused=false`, `safety_class=SAFE_INFO`,
  with the three labeled sections ("Verified changes since latest snapshot",
  "Current status", "Unknown / not compared") and reported verified differences
  only.
- **The live `:8765` process returned stale behavior.** The same question against
  the running background process returned `refused=true`,
  `safety_class=UNSUPPORTED` — the pre-Step-43/47 answer.
- **Root cause:** the server is launched as `python app.py`, which calls
  `uvicorn.run("app:app", host="127.0.0.1", port=8765, reload=False)`
  (`app.py:8831-8832`). With **`reload=False`** the process keeps the code it was
  started with; new commits are **not** picked up until a manual restart.
- **No restart was performed in Step 48** because stopping/replacing a running
  background process is a **shared-state change** that was not authorized and
  could disrupt other work. The validation used the in-process client instead.

---

## 2. Safe operator restart steps (Windows PowerShell)

> Run these yourself in a PowerShell terminal. Prefix with `!` in the Claude
> prompt if you want the output captured in-session. These use the existing,
> vetted scripts that stop **only** the confirmed SPARTA `app.py` process
> (matched on `python.exe` + `app.py` + `SPARTA_BRAIN`, by verified PID — never
> a broad/name-based kill).

1. **(Optional) Identify the current listener** — confirm what holds the port:
   ```powershell
   Get-NetTCPConnection -LocalPort 8765 -State Listen |
     ForEach-Object {
       (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.OwningProcess)").CommandLine
     }
   ```

2. **Stop only the confirmed SPARTA server:**
   ```powershell
   pwsh -File scripts\stop_sparta_commander_desktop.ps1
   ```
   This stops only processes positively confirmed as SPARTA's own `app.py`
   (verified `-Id`); it leaves any non-SPARTA listener untouched and prints
   "Port 8765 is now free." on success.

3. **Start the current build** (manual launch; no service, no autostart):
   ```powershell
   Set-Location C:\SPARTA_BRAIN
   Start-Process -FilePath .\.venv\Scripts\python.exe -ArgumentList 'app.py' -WorkingDirectory C:\SPARTA_BRAIN -WindowStyle Minimized
   ```
   (Equivalently, `pwsh -File scripts\start_sparta_commander_desktop.ps1`, which
   starts the server only when port 8765 is free and refuses to touch a
   non-SPARTA listener.)

4. **Wait for readiness** (poll until 200, no fixed sleep needed):
   ```powershell
   for ($i=0; $i -lt 30; $i++) {
     try { if ((Invoke-WebRequest http://127.0.0.1:8765/jarvis -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200) { "up"; break } } catch {}
     Start-Sleep -Seconds 1
   }
   ```

---

## 3. Post-restart verification commands

Run all of these after the restart. Expected results in **bold**.

1. **`/jarvis` returns 200:**
   ```powershell
   (Invoke-WebRequest http://127.0.0.1:8765/jarvis -UseBasicParsing).StatusCode
   ```
   → **200**

2. **`/api/jarvis/status` returns 200 and correct shape:**
   ```powershell
   $s = Invoke-RestMethod http://127.0.0.1:8765/api/jarvis/status
   @{ keys = ($s.PSObject.Properties.Name).Count; online = $s.online; read_only = $s.read_only;
      td_read_only = $s.trading_detail.read_only; paper = $s.trading_detail.paper_ready;
      live = $s.trading_detail.live_ready; broker = $s.trading_detail.broker_control } | ConvertTo-Json
   ```
   → **keys = 24, online = true, read_only = true, td_read_only = true,
   paper = false, live = false, broker = false**

3. **`/api/jarvis/ask` supports "what changed since last check?" (freshness probe):**
   ```powershell
   $a = Invoke-RestMethod http://127.0.0.1:8765/api/jarvis/ask -Method Post -ContentType 'application/json' -Body '{"question":"what changed since last check?"}'
   @{ refused = $a.refused; safety_class = $a.safety_class;
      has_verified = ($a.answer -match 'Verified changes since latest snapshot');
      has_current = ($a.answer -match 'Current status');
      has_unknown = ($a.answer -match 'Unknown / not compared') } | ConvertTo-Json
   ```
   → **refused = false, safety_class = SAFE_INFO, has_verified = true,
   has_current = true, has_unknown = true.** (If this returns
   `UNSUPPORTED`/`refused=true`, the process is **still stale** — repeat the stop
   step, confirm the port is free, and start again.)

4. **Forbidden mixed request refuses:**
   ```powershell
   $f = Invoke-RestMethod http://127.0.0.1:8765/api/jarvis/ask -Method Post -ContentType 'application/json' -Body '{"question":"what changed and place a trade"}'
   @{ refused = $f.refused; safety_class = $f.safety_class } | ConvertTo-Json
   ```
   → **refused = true, safety_class = FORBIDDEN_TRADING**

5. **No `/api/jarvis/snapshot` and no `/api/jarvis/refresh` routes exist:**
   ```powershell
   foreach ($p in '/api/jarvis/snapshot','/api/jarvis/refresh') {
     foreach ($m in 'GET','POST') {
       try { $c = (Invoke-WebRequest "http://127.0.0.1:8765$p" -Method $m -UseBasicParsing -SkipHttpErrorCheck).StatusCode }
       catch { $c = $_.Exception.Response.StatusCode.value__ }
       "{0} {1} -> {2}" -f $m, $p, $c
     }
   }
   ```
   → each line ends in **404**

> Optional one-shot route smoke: `python tools/jarvis_route_smoke_report.py
> --base-url http://127.0.0.1:8765 --timeout 5` (read-only GET probe).

---

## 4. Rollback / stop instructions

- **Stop the server** (return to no listener):
  ```powershell
  pwsh -File scripts\stop_sparta_commander_desktop.ps1
  ```
  Stops only the confirmed SPARTA `app.py` process and reports whether the port
  is free.
- **Revert code** (if a restart surfaced a regression you want to undo before
  re-launching): check out the previous good commit in a separate, explicitly
  authorized session, then restart per §2. This protocol does **not** perform any
  git operation.
- **No persistence to undo:** the launch is a plain foreground/minimized process
  (no Windows service, scheduled task, or autostart), so stopping the process is
  a complete rollback of the restart itself.

---

## 5. Read-only / no-trading guarantees

- The restart changes **no code** — it only reloads the already-committed code
  into a fresh process. JARVIS remains read-only: `/api/jarvis/status` reports
  `read_only=true` and `trading_detail.read_only=true` with
  `paper_ready/live_ready/broker_control` locked `false`.
- The server binds **localhost only** (`127.0.0.1:8765`).
- `/api/jarvis/ask` executes nothing, places/enables/approves no trade, writes no
  snapshot, and exposes only the five response fields
  (`answer/safety_class/sources_used/refused/refusal_reason`).
- No `/api/jarvis/snapshot` and no `/api/jarvis/refresh` endpoint exist; the
  template has no snapshot/refresh/execution controls.
- The stop script never performs broad/name-based termination and never touches a
  non-SPARTA process.

---

## 6. Doc-only / no-code rationale (validation)

- This step changed **no** `app.py`, template, classifier, tool, or test file —
  only the two `docs/jarvis_step_49_live_server_restart_protocol/` files were
  created. Because no code or test changed, the scoped JARVIS suite outcome is
  unchanged from the Step 48 smoke result (`393 passed, 0 failed, 0 skipped`);
  re-running it here would exercise identical code and is therefore not required.
- `report.json` is validated with `python -m json.tool` → **JSON_OK**.

---

## 7. Verdict

- **`JARVIS_LIVE_SERVER_RESTART_PROTOCOL_READY`**
- A safe, manual, operator-run restart protocol is documented: stop only the
  confirmed SPARTA `app.py` process, relaunch `python app.py` (uvicorn,
  `reload=False`), then verify `/jarvis` 200, `/api/jarvis/status` 24-key locked
  read-only shape, the Step 47 change-summary ask (SAFE_INFO with verified
  sections), the FORBIDDEN_TRADING refusal, and the absence of snapshot/refresh
  routes. Nothing was restarted, no code/test/template/trading/storage file was
  touched, and nothing is staged or committed.
