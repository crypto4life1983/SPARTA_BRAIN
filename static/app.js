// Tiny shared helpers (loaded on every page).

async function api(path, body) {
  const r = await fetch(path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  let data = null;
  try { data = await r.json(); } catch { data = null; }
  if (!r.ok) {
    const msg = (data && (data.error || data.detail)) || `${r.status} ${r.statusText}`;
    throw new Error(msg);
  }
  return data;
}

function showBanner(msg, kind) {
  const el = document.getElementById("banner");
  if (!el) { alert(msg); return; }
  el.textContent = msg;
  el.className = "banner " + (kind || "");
  el.classList.remove("hidden");
  clearTimeout(showBanner._t);
  showBanner._t = setTimeout(() => el.classList.add("hidden"), 5000);
}

function setBusy(btn, busy, label) {
  if (!btn) return;
  if (busy) {
    btn.dataset._label = btn.textContent;
    btn.textContent = label || "Working...";
    btn.disabled = true;
  } else {
    btn.disabled = false;
    btn.textContent = label || btn.dataset._label || btn.textContent;
  }
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

/* =========================================================
   Smart Model Router - confirm-before-paid helper
   ========================================================= */

const PAID_MODELS = new Set(["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o", "gpt-4.1"]);

let __settingsCache = null;
async function getSettingsCached() {
  if (__settingsCache) return __settingsCache;
  try {
    __settingsCache = await fetch("/api/settings").then(r => r.json());
  } catch {
    __settingsCache = {};
  }
  return __settingsCache;
}
function clearSettingsCache() { __settingsCache = null; }

function isPaidModel(model) {
  if (!model) return false;
  return PAID_MODELS.has(model) || /^gpt-/.test(model);
}

/** Returns true if the user accepts the paid call (or no confirmation needed). */
async function confirmIfPaidTask(task) {
  const s = await getSettingsCached();
  const model = s[`${task}_model`];
  if (!isPaidModel(model)) return true;
  // Honor the "Confirm before paid API calls" toggle in Settings.
  // Default-on: only skip the dialog when the value is the literal "false".
  if (s.confirm_paid_calls === "false") return true;
  return window.confirm(`Paid API call (${model}) - continue?`);
}

/* =========================================================
   Current AI Route panels (Ideas, Trends, Scripts, Idea Detail)
   Pulls /api/router/status fresh on every page load - no caching.
   ========================================================= */

const ROUTE_TASK_LABELS = {
  trend_to_ideas: "Idea Forge",
  hooks: "Hooks",
  script_draft: "Script",
  script_polish: "Polish",
  caption: "Caption",
};

async function renderRoutePanels() {
  const panels = document.querySelectorAll(".route-panel[data-route-tasks]");
  if (!panels.length) return;

  let status;
  try {
    status = await fetch("/api/router/status").then(r => r.json());
  } catch (e) {
    panels.forEach(p => { p.textContent = "AI route unavailable"; });
    return;
  }

  panels.forEach(panel => {
    const modeEl = panel.querySelector("[data-route-mode]");
    if (modeEl) {
      modeEl.textContent = (status.ai_mode || "?").toUpperCase();
      modeEl.dataset.mode = status.ai_mode;
    }

    const list = panel.querySelector("[data-route-list]");
    if (!list) return;
    const taskKeys = (panel.dataset.routeTasks || "").split(",").map(s => s.trim()).filter(Boolean);

    list.innerHTML = taskKeys.map(t => {
      const info = (status.tasks || {})[t];
      if (!info) return "";
      const tier = info.is_paid ? "PAID" : "FREE";
      const tierClass = info.is_paid ? "paid" : "free";
      return `<span class="route-task" data-tier="${tierClass}">
        <span class="route-task-name">${ROUTE_TASK_LABELS[t] || t}</span>
        <span class="route-arrow">→</span>
        <code class="route-model">${escapeHtml(info.model)}</code>
        <span class="route-badge">${tier}</span>
      </span>`;
    }).join("");
  });
}

// Auto-render on every page load
renderRoutePanels();

/* =========================================================
   War Room ambient: live status indicators
   - Mission Control panel (only on dashboard)
   - Bottom status pills (every page)
   - Sparta Wins counter (dashboard sets it; other pages skip)
   ========================================================= */

(async function liveStatus() {
  const setSysStatus = (system, state, label) => {
    const el = document.querySelector(`[data-system="${system}"]`);
    if (!el) return;
    el.dataset.state = state;
    el.textContent = (label || state).toUpperCase();
  };

  const setFootPill = (id, state, valueLabel) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.dataset.state = state;
    if (valueLabel) {
      const v = el.querySelector('[data-foot="ai-state"]');
      if (v) v.textContent = valueLabel.toUpperCase();
    }
  };

  // Sparta Wins counter from window.__SPARTA__ (dashboard only)
  if (window.__SPARTA__ && typeof window.__SPARTA__.exports_total === "number") {
    const w = document.querySelector('[data-foot="wins"]');
    if (w) w.textContent = String(window.__SPARTA__.exports_total);
  }

  // 1. Settings → reveal API mode + key flags
  let settings = null;
  try {
    settings = await (await fetch("/api/settings")).json();
  } catch {}

  if (settings) {
    // Trend scanner: scanning if youtube key set, else standby
    setSysStatus("youtube", settings.youtube_api_key_set ? "scanning" : "standby",
                 settings.youtube_api_key_set ? "SCANNING" : "STANDBY");

    // OpenAI: online if api_polish + key set, else standby
    const polishReady = settings.quality_mode === "api_polish" && settings.openai_api_key_set;
    setSysStatus("openai", polishReady ? "online" : "standby", polishReady ? "ONLINE" : "STANDBY");

    // Bottom API Mode pill
    const apiPill = document.getElementById("foot-api");
    if (apiPill) {
      const apiLbl = apiPill.querySelector('[data-foot="api-label"]');
      if (settings.quality_mode === "api_polish") {
        apiPill.dataset.state = polishReady ? "active" : "standby";
        if (apiLbl) apiLbl.textContent = polishReady ? "OPENAI · ACTIVE" : "OPENAI · NO KEY";
      } else {
        apiPill.dataset.state = "standby";
        if (apiLbl) apiLbl.textContent = "LOCAL ONLY";
      }
    }
  }

  // 2. Ollama health check — poll every 20s so a stale OFFLINE badge
  // recovers automatically once Ollama comes back up.
  // Also fetches the live version from /api/system/ollama-version once
  // per page load and stamps it into the footer pill + dashboard row.
  let _ollamaVersionFetched = false;
  async function fetchOllamaVersion() {
    if (_ollamaVersionFetched) return;
    try {
      const vr = await fetch("/api/system/ollama-version");
      const vd = await vr.json();
      if (vd.ok && vd.version) {
        _ollamaVersionFetched = true;
        const ver = "v" + vd.version;
        // Footer pill label: "OLLAMA" → "OLLAMA 0.22.1"
        const aiPill = document.getElementById("foot-ai");
        if (aiPill) {
          const lbl = aiPill.querySelector('[data-foot="ai-label"]');
          if (lbl) lbl.textContent = "OLLAMA " + vd.version;
        }
        // Dashboard Mission Control row
        const dashLbl = document.getElementById("ollama-version-label");
        if (dashLbl) dashLbl.textContent = "Ollama " + vd.version;
      }
    } catch { /* non-fatal */ }
  }

  async function refreshOllamaStatus() {
    try {
      const r = await fetch("/api/settings/test", { method: "POST" });
      const data = await r.json();
      const ok = data && data.ok && data.model_loaded;
      setSysStatus("ollama", ok ? "online" : (data && data.ok ? "standby" : "offline"),
                   ok ? "OPERATIONAL" : (data && data.ok ? "NO MODEL" : "OFFLINE"));

      const aiPill = document.getElementById("foot-ai");
      if (aiPill) {
        aiPill.dataset.state = ok ? "online" : "offline";
        const v = aiPill.querySelector('[data-foot="ai-state"]');
        if (v) v.textContent = ok ? "ONLINE" : "OFFLINE";
      }
    } catch {
      setSysStatus("ollama", "offline", "OFFLINE");
      const aiPill = document.getElementById("foot-ai");
      if (aiPill) {
        aiPill.dataset.state = "offline";
        const v = aiPill.querySelector('[data-foot="ai-state"]');
        if (v) v.textContent = "OFFLINE";
      }
    }
  }

  fetchOllamaVersion();
  await refreshOllamaStatus();
  setInterval(refreshOllamaStatus, 20000);
})();
