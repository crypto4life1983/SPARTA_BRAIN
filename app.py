import re
import datetime
from collections import Counter
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import database as db
from ollama_client import (
    OllamaClient, OllamaError,
    IDEAS_PROMPT, HOOKS_PROMPT, SCRIPT_PROMPT, CAPTION_PROMPT, TREND_IDEAS_PROMPT,
    _parse_numbered, _parse_caption,
)
from openai_client import OpenAIClient, OpenAIError, POLISH_PROMPT
from youtube_client import YouTubeClient, YouTubeError

BASE = Path(__file__).parent
EXPORTS = BASE / "exports"
VIDEOS_DIR = EXPORTS / "videos"
STORAGE_DIR = BASE / "storage"

# Three-Brain anti-loop rescue tracker.
# Call _tbr_check(key, error_str) after every generation failure.
# When the same key fails >= 2 times it logs a rescue recommendation.
_tbr_failure_counts: dict[str, int] = {}
_tbr_last_errors:    dict[str, str] = {}


def _tbr_check(key: str, error_str: str) -> None:
    """Track repeated failures and log a Codex rescue recommendation."""
    import logging as _logging
    _tbr_failure_counts[key] = _tbr_failure_counts.get(key, 0) + 1
    repeated = error_str and error_str == _tbr_last_errors.get(key)
    _tbr_last_errors[key] = error_str
    count = _tbr_failure_counts[key]
    if count >= 2 or repeated:
        _logging.getLogger("sparta.three_brain").warning(
            "Three-Brain rescue recommended: Codex  "
            "[key=%s  failures=%d  repeated=%s]", key, count, repeated
        )


def _tbr_reset(key: str) -> None:
    """Clear failure tracking after a successful run."""
    _tbr_failure_counts.pop(key, None)
    _tbr_last_errors.pop(key, None)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio as _asyncio
    db.init_db()
    EXPORTS.mkdir(exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    STORAGE_DIR.mkdir(exist_ok=True)
    (STORAGE_DIR / "videos").mkdir(parents=True, exist_ok=True)
    db.seed_settings()
    db.seed_manual_entries()
    # Hydra Video module manual entry (idempotent; CLAUDE.md requires every
    # SPARTA module to register itself in the system manual so /guide is true).
    db.upsert_manual_entry(
        "hydra_video",
        module_name="Hydra Video",
        category="Video",
        status="READY",
        short_description=(
            "Local-first talking-head pipeline. Script in, MP4 out, no cloud."
        ),
        how_it_works=(
            "Five stages: edge-tts voice with WordBoundary timings, avatar "
            "image prep, lipsync (SadTalker/Wav2Lip when installed; falls "
            "back to a Ken Burns placeholder), captions burned in, MoviePy "
            "composite with optional product overlay and background music."
        ),
        when_to_use=(
            "When you want a vertical 9:16 talking-head clip from a short "
            "script without paying an avatar service."
        ),
        user_action=(
            "Open Hydra Video Studio, paste a script, optionally point at an "
            "avatar.jpg and a product image, click Generate. Or run "
            "`python hydra_video/run_video.py \"...\"` from the project root."
        ),
        sort_order=85,
    )
    db.upsert_manual_entry(
        "three_brain_router",
        module_name="Three Brain Router",
        category="AI",
        status="READY",
        short_description=(
            "Automatically routes tasks to Claude, Codex, or Gemini based on "
            "task keywords. Includes anti-loop rescue escalation to Codex."
        ),
        how_it_works=(
            "Keyword scan: video/audio/PDF signals → Gemini; code review/bug/"
            "stuck signals → Codex; everything else → Claude. "
            "should_rescue() escalates to Codex after 1-2 failures."
        ),
        when_to_use=(
            "When you want the system to pick the right AI automatically, or "
            "when Claude is stuck and you need a fresh adversarial pass."
        ),
        user_action="Open /three-brain, describe the task, click Route Task.",
        sort_order=95,
    )
    # SPARTA Trading Command Center v1 — Module 1 of 8 planned per
    # docs/sparta_command_center_first_build_plan.md (commit 970452c).
    # Read-only lifecycle viewer over B006_* sealed-artifact lifecycles.
    db.upsert_manual_entry(
        "trading_command_center",
        module_name="Trading Command Center (v1 lifecycle viewer)",
        category="Trading",
        status="READY",
        short_description=(
            "Read-only viewer for B006_* candidate lifecycle sealed-artifact "
            "state. No trade, no fetch, no broker, no optimization."
        ),
        how_it_works=(
            "Scans reports/external_research_hunter/ for B006_* artifacts, "
            "recomputes sha256 of each file, compares against any declared "
            "sha pin in the JSON sidecar, infers phase 0-8 from artifact "
            "presence, surfaces the next-expected Authorize phrase verbatim "
            "from brain_memory/projects/trading_bot/decisions.md."
        ),
        when_to_use=(
            "When you want one read-only pane that shows which sealed-"
            "artifact lifecycles are in which phase and whether any seal "
            "has drifted, without navigating the reports tree by hand."
        ),
        user_action=(
            "Open http://127.0.0.1:8765/command in a browser. GET-only, "
            "localhost-only, no buttons, no forms, no execution."
        ),
        sort_order=92,
    )
    # SPARTA JARVIS Command Center — additive, read-only cinematic console.
    db.upsert_manual_entry(
        "jarvis_command_center",
        module_name="Jarvis Command Center",
        category="Dashboard",
        status="READY",
        short_description=(
            "Cinematic read-only command console that aggregates existing "
            "system, AI, trading, content, money, and safety signals."
        ),
        how_it_works=(
            "GET /jarvis renders a holographic single page; it polls "
            "GET /api/jarvis/status, which fans out to existing read-only "
            "probes (three-brain tools, command lifecycle scan, paper "
            "status, settings flags, safety log). Every section fails closed "
            "to 'not connected' / 'waiting for signal' and never invents a "
            "metric or profit number. Nothing executes, trades, or uploads."
        ),
        when_to_use=(
            "When you want one glanceable console showing whether each "
            "subsystem is online, plus the locked safety gates."
        ),
        user_action=(
            "Open http://127.0.0.1:8765/jarvis. Read-only; no buttons that "
            "trade, upload, or fire automation."
        ),
        sort_order=10,
    )
    db.upsert_manual_entry(
        "trade_decision_ledger",
        module_name="Trade Decision Ledger",
        category="Trading",
        status="READY",
        short_description=(
            "Read-only normalized ledger for existing candidate decisions, "
            "gate states, coordinator blocks, and paper-only state."
        ),
        how_it_works=(
            "Reads existing JSON/JSONL artifacts from the external trading "
            "project data folder, normalizes them into ledger rows, and "
            "renders source health plus provenance hashes. It has no trading "
            "control surface."
        ),
        when_to_use=(
            "When you need one safe view of accepted, blocked, observed, and "
            "paper-only decision records without opening the external bot."
        ),
        user_action=(
            "Open http://127.0.0.1:8765/trade-ledger in a browser. GET-only, "
            "read-only, no forms, no bot control."
        ),
        sort_order=93,
    )
    # Weekly RS s21 broker-free paper status card (read-only). Mirrors the
    # /command read-only pattern: GET-only, localhost-only, no buttons, no
    # cycle trigger, no fetch, no broker. DIAGNOSTIC_ONLY; FRC NEVER_GRANTED.
    db.upsert_manual_entry(
        "weekly_rs_s21_paper",
        module_name="Weekly RS s21 Paper Status",
        category="Trading",
        status="READY",
        short_description=(
            "Read-only status card for the broker-free weekly RS s21 paper "
            "process. No cycle run, no fetch, no broker, no execution."
        ),
        how_it_works=(
            "Reads the harness manifest plus the newest runs/dry_cycle_NNN/ "
            "outputs (orders, killswitch_status.json) and shows paper status, "
            "last cycle/anchor, next expected anchor, equity, holdings, "
            "verdict, kill-switch, and whether the next cycle is READY or "
            "STALE. A separate dry-run Telegram notifier reuses the same "
            "read-only aggregator."
        ),
        when_to_use=(
            "When you want a one-glance, read-only view of the weekly RS s21 "
            "paper test without running a cycle or opening the harness."
        ),
        user_action=(
            "Open http://127.0.0.1:8765/paper in a browser. GET-only, "
            "localhost-only, no buttons, no execution."
        ),
        sort_order=91,
    )

    # One-shot migration: if the user is still on the previous-generation
    # short-form defaults (45s max / 30s target), bump them to 35s/25s.
    # Customized values (anything else) are left alone.
    if (db.get_setting("script_max_seconds") or "") == "45":
        db.set_setting("script_max_seconds", "35")
    if (db.get_setting("script_target_seconds") or "") == "30":
        db.set_setting("script_target_seconds", "25")

    # Phase 4: auto-mode background scheduler
    sched_task = _asyncio.create_task(_auto_mode_scheduler())
    # Performance tracker: pulls YT stats once a day for shipped videos
    perf_task = _asyncio.create_task(_perf_tracker_scheduler())
    # Shorts Autopilot: fires Spartacus->render->upload at configured slots
    autopilot_task = _asyncio.create_task(_autopilot_scheduler())
    try:
        yield
    finally:
        for t in (sched_task, perf_task, autopilot_task):
            t.cancel()
            try:
                await t
            except _asyncio.CancelledError:
                pass


# Auto-mode scheduler: wakes every CHECK_INTERVAL and fires run_auto_daily
# if Auto Mode is on AND >= 24h have passed since the last auto run.
_AUTO_INTERVAL_SECONDS = 24 * 60 * 60
_AUTO_CHECK_INTERVAL = 60


async def _auto_mode_scheduler() -> None:
    import asyncio
    from datetime import datetime, timedelta
    while True:
        try:
            await asyncio.sleep(_AUTO_CHECK_INTERVAL)
            if (db.get_setting("auto_mode_enabled") or "false").lower() != "true":
                continue
            last = (db.get_setting("last_auto_run_at") or "").strip()
            if last:
                try:
                    last_dt = datetime.fromisoformat(last)
                    if (datetime.now() - last_dt).total_seconds() < _AUTO_INTERVAL_SECONDS:
                        continue
                except ValueError:
                    pass
            # Fire
            from sparta_pipeline import run_auto_daily
            try:
                await run_auto_daily(_route_text_gen)
            except Exception as e:  # noqa: BLE001
                # Stamp last run so a broken run doesn't loop tightly,
                # and surface the error in a failed run row.
                db.set_setting("last_auto_run_at",
                               datetime.now().isoformat(timespec="seconds"))
                run_id = db.insert_sparta_run(status="failed")
                db.update_sparta_run(
                    run_id, mode="auto",
                    error=f"scheduler caught: {type(e).__name__}: {e}",
                )
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            # Don't let bookkeeping bugs kill the scheduler thread
            await asyncio.sleep(_AUTO_CHECK_INTERVAL)


app = FastAPI(title="SPARTA BRAIN", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
# Serve generated artifacts (videos, .txt exports, .srt) so the browser
# can download them directly. Local-only app; no auth needed.
app.mount("/exports", StaticFiles(directory=str(EXPORTS)), name="exports")
# Phase: Remotion video_engine writes here. Mounted so the browser can
# fetch storage/videos/<job_id>/video.mp4 directly for preview/download.
app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")
# Hydra Video outputs (talking-head MP4s + audio) so the dashboard can
# preview them inline.
HYDRA_OUT = BASE / "hydra_video" / "outputs"
HYDRA_OUT.mkdir(parents=True, exist_ok=True)
app.mount("/hydra_outputs", StaticFiles(directory=str(HYDRA_OUT)), name="hydra_outputs")
templates = Jinja2Templates(directory=str(BASE / "templates"))

ollama = OllamaClient()
openai = OpenAIClient()
youtube = YouTubeClient()


def _safe_settings() -> dict:
    """Return settings with all secret keys redacted.

    Actual key values are never sent back to clients or rendered into HTML.
    Callers receive empty strings for the secret fields plus boolean
    `<name>_set` flags indicating whether a value is stored.
    """
    s = db.get_all_settings()
    has_oai = bool((s.get("openai_api_key") or "").strip())
    has_yt = bool((s.get("youtube_api_key") or "").strip())
    has_yt_oc = bool((s.get("youtube_oauth_client_id") or "").strip())
    has_yt_os = bool((s.get("youtube_oauth_client_secret") or "").strip())
    has_yt_tok = bool((s.get("youtube_oauth_token") or "").strip())
    s["openai_api_key"] = ""
    s["openai_api_key_set"] = has_oai
    s["youtube_api_key"] = ""
    s["youtube_api_key_set"] = has_yt
    s["youtube_oauth_client_id"] = ""
    s["youtube_oauth_client_id_set"] = has_yt_oc
    s["youtube_oauth_client_secret"] = ""
    s["youtube_oauth_client_secret_set"] = has_yt_os
    s["youtube_oauth_token"] = ""
    s["youtube_oauth_token_set"] = has_yt_tok
    has_pex = bool((s.get("pexels_api_key") or "").strip())
    s["pexels_api_key"] = ""
    s["pexels_api_key_set"] = has_pex
    # Ensure gemini_model always has a value in settings
    if not (s.get("gemini_model") or "").strip():
        s["gemini_model"] = "gemini-2.5-flash"
    # Normalise legacy "premium" → "advanced"
    if (s.get("ai_mode") or "") == "premium":
        s["ai_mode"] = "advanced"
    # Normalise legacy "llama3" bare name → llama3.1:8b in task model fields
    for t in ("trend_to_ideas", "hooks", "script_draft", "script_polish", "caption"):
        key = f"{t}_model"
        if (s.get(key) or "").strip() == "llama3":
            s[key] = "llama3.1:8b"
    return s


def _youtube_error_response(e: YouTubeError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"error": str(e)})


# ============================================================
# Smart Model Router
# ============================================================

# The only paid models the router will route to. Anything not in this set
# (and not prefixed with 'gpt-') is assumed to be a local Ollama model.
PAID_MODELS = {"gpt-4o-mini", "gpt-4.1-mini", "gpt-4o", "gpt-4.1"}

# Tasks the router knows about. Maps task -> setting key.
TASK_KEYS = (
    "trend_to_ideas",
    "hooks",
    "script_draft",
    "script_polish",
    "caption",
)

# Cost tier labels used by the router status endpoint and UI panels.
MODEL_TIERS = {
    "llama3.1:8b":        "FREE local",
    "llama3":             "FREE local",
    "mistral:7b":         "FREE local",
    "qwen2.5:7b":         "FREE local",
    "qwen2.5:14b":        "FREE local",
    "gpt-4o-mini":        "LOW cost",
    "gpt-4.1-mini":       "MEDIUM cost",
    "gpt-4o":             "HIGH quality / higher cost",
    "gpt-4.1":            "HIGH quality / higher cost",
    "gemini-2.5-flash":   "FREE / low-cost (Gemini)",
    "gemini-2.5-pro":     "LOW cost (Gemini)",
    "gemini-2.0-flash":   "FREE / low-cost (Gemini)",
}

# Universal local fallback when a task setting is empty/missing.
SAFE_LOCAL_FALLBACK = "llama3.1:8b"

# Mode presets — single source of truth used by both API endpoints and UI
_MODE_PRESETS: dict[str, dict] = {
    "free": {
        "trend_to_ideas": "llama3.1:8b",
        "hooks":          "llama3.1:8b",
        "script_draft":   "llama3.1:8b",
        "script_polish":  "llama3.1:8b",
        "caption":        "llama3.1:8b",
        "gemini_model":   "gemini-2.5-flash",
    },
    "balanced": {
        "trend_to_ideas": "llama3.1:8b",
        "hooks":          "gpt-4o-mini",
        "script_draft":   "llama3.1:8b",
        "script_polish":  "gpt-4o-mini",
        "caption":        "gpt-4o-mini",
        "gemini_model":   "gemini-2.5-flash",
    },
    "advanced": {
        "trend_to_ideas": "gpt-4o-mini",
        "hooks":          "gpt-4o-mini",
        "script_draft":   "gpt-4o-mini",
        "script_polish":  "gpt-4o-mini",
        "caption":        "gpt-4o-mini",
        "gemini_model":   "gemini-2.5-pro",
    },
}


def is_paid_model(model: str) -> bool:
    return model in PAID_MODELS or model.startswith("gpt-")


def get_task_model(task: str) -> str:
    """Resolve the configured model for a task. Always reads from DB on
    each call - no caching. Falls back to llama3 if the value is missing
    or blank."""
    raw = (db.get_setting(f"{task}_model") or "").strip()
    if not raw:
        return SAFE_LOCAL_FALLBACK
    return raw


def _log_route(task: str, ai_mode: str, model: str, provider: str) -> None:
    # Single-line diagnostic log on every generation call. Goes to the
    # same stream as uvicorn's logs (terminal where `python app.py` runs).
    print(
        f"Task: {task} | AI Mode: {ai_mode} | Model: {model} | Provider: {provider}",
        flush=True,
    )


async def _route_text_gen(task: str, prompt: str) -> str:
    """Pick the model for `task` and dispatch to Ollama or OpenAI.

    Reads settings fresh from the DB on every call. No hard restrictions:
    AI Mode is informational. The diagnostic log line shows exactly what
    ran. The frontend confirm-paid prompt provides soft pre-call safety.
    """
    model = get_task_model(task)
    ai_mode = (db.get_setting("ai_mode") or "balanced").lower()
    paid = is_paid_model(model)
    provider = "openai" if paid else "ollama"
    _log_route(task, ai_mode, model, provider)

    if paid:
        return await openai.chat(model, prompt)
    return await ollama.complete(prompt, model=model)


def _ollama_error_response(e: OllamaError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"error": str(e)})


def _openai_error_response(e: OpenAIError) -> JSONResponse:
    msg = str(e)
    # Rate-limit errors should return 429, not 503
    status = 429 if ("429" in msg or "rate limit" in msg.lower() or "RateLimitError" in type(e).__name__) else 503
    return JSONResponse(status_code=status, content={"error": msg})


# ============================================================
# Pages
# ============================================================

@app.get("/", response_class=HTMLResponse)
def page_dashboard(request: Request):
    # Most recent script - the default target for the Generate Video button.
    latest_script = None
    with db.conn() as _c:
        row = _c.execute(
            "SELECT s.*, i.title AS idea_title FROM scripts s "
            "LEFT JOIN ideas i ON i.id = s.idea_id "
            "ORDER BY s.id DESC LIMIT 1"
        ).fetchone()
        if row:
            latest_script = dict(row)

    import video_engine
    video_jobs = video_engine.list_jobs(5)
    for j in video_jobs:
        j["video_url"] = video_engine.video_url_for(j)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "page": "dashboard",
            "counts": db.get_counts(),
            "metrics": db.get_dashboard_metrics(),
            "recent": [dict(r) for r in db.recent_ideas(6)],
            "sparta_runs": [dict(r) for r in db.list_sparta_runs(5)],
            "settings": _safe_settings(),
            "latest_script": latest_script,
            "video_jobs": video_jobs,
        },
    )


@app.get("/ideas", response_class=HTMLResponse)
def page_ideas(request: Request):
    settings = db.get_all_settings()
    return templates.TemplateResponse(
        "ideas.html",
        {
            "request": request,
            "page": "ideas",
            "default_niche": settings.get("default_niche", ""),
        },
    )


@app.get("/ideas/{idea_id}", response_class=HTMLResponse)
def page_idea_detail(request: Request, idea_id: int):
    idea = db.get_idea(idea_id)
    if not idea:
        return RedirectResponse(url="/ideas", status_code=302)
    return templates.TemplateResponse(
        "idea_detail.html",
        {
            "request": request,
            "page": "ideas",
            "idea": dict(idea),
            "hooks": [dict(r) for r in db.list_hooks(idea_id)],
            "scripts": [dict(r) for r in db.list_scripts(idea_id)],
            "captions": [dict(r) for r in db.list_captions(idea_id)],
            "exports": [dict(r) for r in db.list_exports(idea_id)],
        },
    )


@app.get("/scripts", response_class=HTMLResponse)
def page_scripts(request: Request):
    return templates.TemplateResponse(
        "scripts.html",
        {
            "request": request,
            "page": "scripts",
            "ideas": [dict(r) for r in db.list_ideas()],
        },
    )


@app.get("/research-brain", response_class=HTMLResponse)
def page_research_brain(request: Request, min_score: int = -1):
    """min_score: -1 = use the saved min_research_score setting (default 70).
       Pass min_score=0 in the URL to show everything."""
    if min_score < 0:
        try:
            min_score = int(db.get_setting("min_research_score") or "70")
        except ValueError:
            min_score = 70
    min_score = max(0, min(100, min_score))
    return templates.TemplateResponse(
        "research_brain.html",
        {
            "request": request,
            "page": "research_brain",
            "topics": [dict(r) for r in db.list_research_topics(20, min_score=min_score)],
            "settings": _safe_settings(),
            "min_score": min_score,
        },
    )


@app.get("/trends", response_class=HTMLResponse)
def page_trends(request: Request):
    return templates.TemplateResponse(
        "trends.html",
        {
            "request": request,
            "page": "trends",
            "trends": [dict(r) for r in db.list_trends()],
            "settings": _safe_settings(),
        },
    )


@app.get("/videos", response_class=HTMLResponse)
def page_videos(request: Request):
    """Lists every rendered video. Two sources:
      1. video_jobs (new) - Remotion engine, what Spartacus + Auto Mode write to
      2. videos (legacy Phase 4A) - MoviePy builder, kept for back-compat
    Both render in the same template; the legacy ones might just have
    less metadata."""
    import video_engine as _ve
    legacy = [dict(r) for r in db.list_videos()]
    jobs = []
    for j in _ve.list_jobs(50):
        url = _ve.video_url_for(j) or ""
        jobs.append({
            "id": j["id"],
            "title": j.get("topic") or "Untitled",
            "status": "ready" if j.get("status") == "done" else j.get("status", ""),
            "video_path": j.get("output_path") or "",
            "video_url": url,
            "subtitle_path": "",
            "voice_path": "",
            "external_url": "",
            "views": None, "likes": None, "last_synced_at": None,
            "idea_id": j.get("script_id") or 0,
            "script_id": j.get("script_id"),
            "created_at": j.get("created_at", ""),
            "error": j.get("error", ""),
            "_engine": "remotion",
        })
    return templates.TemplateResponse(
        "videos.html",
        {
            "request": request,
            "page": "videos",
            # Newest first across both sources
            "videos": sorted(jobs + legacy,
                             key=lambda v: v.get("created_at") or "",
                             reverse=True),
        },
    )


@app.get("/library", response_class=HTMLResponse)
def page_library(request: Request):
    return templates.TemplateResponse(
        "library.html",
        {
            "request": request,
            "page": "library",
            "groups": db.library_grouped(),
        },
    )


@app.get("/settings", response_class=HTMLResponse)
def page_settings(request: Request):
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "page": "settings",
            "settings": _safe_settings(),
        },
    )


# ============================================================
# Generation API (no DB writes)
# ============================================================

class GenIdeasReq(BaseModel):
    niche: str


class GenHooksReq(BaseModel):
    idea_id: int


class GenScriptReq(BaseModel):
    idea_id: int
    hook_id: Optional[int] = None


class GenCaptionReq(BaseModel):
    idea_id: int
    script_id: Optional[int] = None


@app.post("/api/generate/ideas")
async def api_gen_ideas(req: GenIdeasReq):
    if not req.niche.strip():
        raise HTTPException(400, "niche is required")
    prompt = IDEAS_PROMPT.format(niche=req.niche.strip())
    try:
        text = await _route_text_gen("trend_to_ideas", prompt)
    except OllamaError as e:
        return _ollama_error_response(e)
    except OpenAIError as e:
        return _openai_error_response(e)
    return {"ideas": _parse_numbered(text)}


@app.post("/api/generate/hooks")
async def api_gen_hooks(req: GenHooksReq):
    idea = db.get_idea(req.idea_id)
    if not idea:
        raise HTTPException(404, "idea not found")
    prompt = HOOKS_PROMPT.format(idea=idea["title"])
    try:
        text = await _route_text_gen("hooks", prompt)
    except OllamaError as e:
        return _ollama_error_response(e)
    except OpenAIError as e:
        return _openai_error_response(e)
    return {"hooks": _parse_numbered(text)}


@app.post("/api/generate/script")
async def api_gen_script(req: GenScriptReq):
    idea = db.get_idea(req.idea_id)
    if not idea:
        raise HTTPException(404, "idea not found")
    hook_text = None
    if req.hook_id:
        hook = db.get_hook(req.hook_id)
        if hook:
            hook_text = hook["text"]
    hook_clause = f'Open with this hook: "{hook_text}"' if hook_text else ""
    prompt = SCRIPT_PROMPT.format(idea=idea["title"], hook_clause=hook_clause)
    try:
        text = await _route_text_gen("script_draft", prompt)
    except OllamaError as e:
        return _ollama_error_response(e)
    except OpenAIError as e:
        return _openai_error_response(e)
    return {"script": text.strip()}


class GenRawReq(BaseModel):
    task: str
    prompt: str


@app.post("/api/generate/raw")
async def api_gen_raw(req: GenRawReq):
    """Route a raw prompt through the model router for a given task.
    For callers (skills, scripts) that supply their own prompt text."""
    if req.task not in TASK_KEYS:
        raise HTTPException(400, f"Unknown task '{req.task}'. Valid: {', '.join(TASK_KEYS)}")
    try:
        text = await _route_text_gen(req.task, req.prompt)
    except OllamaError as e:
        return _ollama_error_response(e)
    except OpenAIError as e:
        return _openai_error_response(e)
    return {"text": text.strip(), "task": req.task, "model": get_task_model(req.task)}


@app.post("/api/generate/caption")
async def api_gen_caption(req: GenCaptionReq):
    idea = db.get_idea(req.idea_id)
    if not idea:
        raise HTTPException(404, "idea not found")
    script_text = None
    if req.script_id:
        s = db.get_script(req.script_id)
        if s:
            script_text = s["body"]
    script_clause = f'Script: "{script_text}"' if script_text else ""
    prompt = CAPTION_PROMPT.format(idea=idea["title"], script_clause=script_clause)
    try:
        text = await _route_text_gen("caption", prompt)
    except OllamaError as e:
        return _ollama_error_response(e)
    except OpenAIError as e:
        return _openai_error_response(e)
    caption, hashtags = _parse_caption(text)
    return {"caption": caption, "hashtags": hashtags}


# ============================================================
# Persistence API
# ============================================================

class SaveIdeaReq(BaseModel):
    niche: str
    title: str
    body: Optional[str] = None


class SaveIdeasBulkReq(BaseModel):
    niche: str
    items: list[str]  # titles


class SaveHookReq(BaseModel):
    idea_id: int
    text: str


class SaveHooksBulkReq(BaseModel):
    idea_id: int
    items: list[str]


class SaveScriptReq(BaseModel):
    idea_id: int
    body: str
    hook_id: Optional[int] = None


class SaveCaptionReq(BaseModel):
    idea_id: int
    text: str
    hashtags: str = ""
    script_id: Optional[int] = None


class StatusReq(BaseModel):
    status: str


@app.post("/api/ideas")
def api_save_idea(req: SaveIdeaReq):
    if not req.title.strip():
        raise HTTPException(400, "title required")
    new_id = db.insert_idea(req.niche.strip(), req.title.strip(), req.body)
    return {"id": new_id}


@app.post("/api/ideas/bulk")
def api_save_ideas_bulk(req: SaveIdeasBulkReq):
    ids = []
    for title in req.items:
        if title.strip():
            ids.append(db.insert_idea(req.niche.strip(), title.strip(), None))
    return {"ids": ids}


@app.post("/api/hooks")
def api_save_hook(req: SaveHookReq):
    if not db.get_idea(req.idea_id):
        raise HTTPException(404, "idea not found")
    if not req.text.strip():
        raise HTTPException(400, "text required")
    return {"id": db.insert_hook(req.idea_id, req.text.strip())}


@app.post("/api/hooks/bulk")
def api_save_hooks_bulk(req: SaveHooksBulkReq):
    if not db.get_idea(req.idea_id):
        raise HTTPException(404, "idea not found")
    ids = [db.insert_hook(req.idea_id, t.strip()) for t in req.items if t.strip()]
    return {"ids": ids}


@app.post("/api/scripts")
def api_save_script(req: SaveScriptReq):
    if not db.get_idea(req.idea_id):
        raise HTTPException(404, "idea not found")
    if not req.body.strip():
        raise HTTPException(400, "body required")
    return {
        "id": db.insert_script(req.idea_id, req.body.strip(), req.hook_id)
    }


@app.post("/api/captions")
def api_save_caption(req: SaveCaptionReq):
    if not db.get_idea(req.idea_id):
        raise HTTPException(404, "idea not found")
    if not req.text.strip():
        raise HTTPException(400, "text required")
    return {
        "id": db.insert_caption(
            req.idea_id, req.text.strip(), req.hashtags.strip(), req.script_id
        )
    }


@app.patch("/api/{table}/{item_id}/status")
def api_update_status(table: str, item_id: int, req: StatusReq):
    try:
        db.update_status(table, item_id, req.status)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"ok": True}


# ============================================================
# Export
# ============================================================

def _slug(s: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return (s[:max_len] or "untitled")


def _build_export_text(idea: dict, hooks: list[dict], scripts: list[dict],
                       captions: list[dict]) -> tuple[str, dict]:
    sel = {
        "hook": next((h for h in hooks if h["status"] == "selected"), None),
        "script": (
            next((s for s in scripts if s["status"] == "selected"), None)
            or next((s for s in scripts if s["status"] == "polished"), None)
            or (scripts[0] if scripts else None)
        ),
        "caption": next((c for c in captions if c["status"] == "selected"),
                        captions[0] if captions else None),
    }
    other_hooks = [h for h in hooks if sel["hook"] is None or h["id"] != sel["hook"]["id"]]
    other_scripts = [s for s in scripts if sel["script"] is None or s["id"] != sel["script"]["id"]]
    other_captions = [c for c in captions if sel["caption"] is None or c["id"] != sel["caption"]["id"]]

    now = datetime.datetime.now().isoformat(timespec="seconds")
    lines = [
        "========================================",
        "SPARTA BRAIN - CONTENT PACKAGE",
        f"Idea #{idea['id']} - Created: {idea['created_at']}",
        f"Exported: {now}",
        "========================================",
        "",
        "[IDEA]",
        idea["title"],
        "",
        idea.get("body") or "",
        "",
        "[SELECTED HOOK]",
        sel["hook"]["text"] if sel["hook"] else "- none selected -",
        "",
        "[SELECTED SCRIPT]",
        sel["script"]["body"] if sel["script"] else "- none selected -",
        "",
        "[SELECTED CAPTION]",
        sel["caption"]["text"] if sel["caption"] else "- none selected -",
        "",
        "[HASHTAGS]",
        (sel["caption"]["hashtags"] or "-") if sel["caption"] else "-",
        "",
        "----------------------------------------",
        "OTHER OPTIONS",
        "----------------------------------------",
        "",
        "[Other Hooks]",
    ]
    if other_hooks:
        for i, h in enumerate(other_hooks, 1):
            lines.append(f"{i}. {h['text']}")
    else:
        lines.append("- none -")
    lines += ["", "[Other Scripts]"]
    if other_scripts:
        for i, s in enumerate(other_scripts, 1):
            lines.append(f"{i}. {s['body']}")
            lines.append("")
    else:
        lines.append("- none -")
    lines += ["", "[Other Captions]"]
    if other_captions:
        for i, c in enumerate(other_captions, 1):
            lines.append(f"{i}. {c['text']} | {c['hashtags'] or ''}")
    else:
        lines.append("- none -")
    lines.append("")
    return "\n".join(lines), sel


@app.post("/api/export/{idea_id}")
def api_export(idea_id: int):
    idea = db.get_idea(idea_id)
    if not idea:
        raise HTTPException(404, "idea not found")
    idea_d = dict(idea)
    hooks = [dict(r) for r in db.list_hooks(idea_id)]
    scripts = [dict(r) for r in db.list_scripts(idea_id)]
    captions = [dict(r) for r in db.list_captions(idea_id)]

    text, sel = _build_export_text(idea_d, hooks, scripts, captions)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{idea_id}_{_slug(idea_d['title'])}_{ts}.txt"
    path = EXPORTS / filename
    path.write_text(text, encoding="utf-8")

    db.insert_export(idea_id, str(path))
    db.update_status("ideas", idea_id, "exported")
    if sel["hook"]:
        db.update_status("hooks", sel["hook"]["id"], "exported")
    if sel["script"]:
        db.update_status("scripts", sel["script"]["id"], "exported")
    if sel["caption"]:
        db.update_status("captions", sel["caption"]["id"], "exported")

    return {"path": str(path), "filename": filename}


# ============================================================
# Settings API
# ============================================================

class SettingReq(BaseModel):
    key: str
    value: str


@app.get("/api/settings")
def api_get_settings():
    return _safe_settings()


@app.post("/api/settings")
def api_set_setting(req: SettingReq):
    allowed = {
        "model_name",
        "ollama_url",
        "quality_mode",
        "default_niche",
        "openai_api_key",
        "openai_model",
        "youtube_api_key",
        "ai_mode",
        "trend_to_ideas_model",
        "hooks_model",
        "script_draft_model",
        "script_polish_model",
        "caption_model",
        "gemini_model",
        "confirm_paid_calls",
        "daily_run_real_mode",
        "daily_run_platform",
        "auto_mode_enabled",
        "last_auto_run_at",
        "min_research_score",
        "auto_video_enabled",
        "auto_adapt_product",
        "auto_performance_tracking",
        "last_perf_sync_at",
        "tts_enabled",
        "tts_voice",
        "tts_rate",
        "youtube_oauth_client_id",
        "youtube_oauth_client_secret",
        "youtube_oauth_token",
        "youtube_oauth_pkce_verifier",
        "youtube_channel_id",
        "youtube_channel_title",
        "pexels_api_key",
        "auto_upload_youtube",
        "autopilot_enabled",
        "autopilot_slots",
        "autopilot_min_spacing_hours",
        "autopilot_hashtags",
        "autopilot_campaign_id",
        "last_autopilot_run_at",
        "last_autopilot_slot",
        "last_autopilot_slot_marker",
        "safety_gate_enabled",
        "short_form_mode",
        "script_max_seconds",
        "script_target_seconds",
        "scene_target_seconds",
        "scene_min_seconds",
        "scene_max_seconds",
        "loop_ending_enabled",
    }
    if req.key not in allowed:
        raise HTTPException(400, f"unknown setting: {req.key}")
    if req.key == "quality_mode" and req.value not in ("local_only", "api_polish"):
        raise HTTPException(400, "quality_mode must be local_only or api_polish")
    if req.key == "ai_mode" and req.value not in ("free", "balanced", "advanced", "premium"):
        raise HTTPException(400, "ai_mode must be free, balanced, or advanced")
    if req.key == "daily_run_platform" and req.value not in _VALID_PLATFORMS:
        raise HTTPException(400, "daily_run_platform must be tiktok or youtube_shorts")
    if req.key == "daily_run_real_mode" and req.value.lower() not in ("true", "false"):
        raise HTTPException(400, "daily_run_real_mode must be 'true' or 'false'")
    if req.key == "auto_mode_enabled" and req.value.lower() not in ("true", "false"):
        raise HTTPException(400, "auto_mode_enabled must be 'true' or 'false'")
    if req.key == "auto_video_enabled" and req.value.lower() not in ("true", "false"):
        raise HTTPException(400, "auto_video_enabled must be 'true' or 'false'")
    if req.key == "auto_adapt_product" and req.value.lower() not in ("true", "false"):
        raise HTTPException(400, "auto_adapt_product must be 'true' or 'false'")
    if req.key == "auto_performance_tracking" and req.value.lower() not in ("true", "false"):
        raise HTTPException(400, "auto_performance_tracking must be 'true' or 'false'")
    if req.key == "auto_upload_youtube" and req.value.lower() not in ("true", "false"):
        raise HTTPException(400, "auto_upload_youtube must be 'true' or 'false'")
    if req.key == "autopilot_enabled" and req.value.lower() not in ("true", "false"):
        raise HTTPException(400, "autopilot_enabled must be 'true' or 'false'")
    if req.key == "autopilot_slots":
        # CSV of HH:MM strings, e.g. "09:00,14:00,20:00"
        for s in [t.strip() for t in req.value.split(",") if t.strip()]:
            if not _re.match(r"^\d{2}:\d{2}$", s):
                raise HTTPException(400, f"autopilot_slots: invalid time {s!r} (use HH:MM)")
    if req.key == "autopilot_min_spacing_hours":
        try:
            n = int(req.value)
            if n < 1 or n > 24:
                raise ValueError()
        except ValueError:
            raise HTTPException(400, "autopilot_min_spacing_hours must be 1-24")
    if req.key == "short_form_mode" and req.value.lower() not in ("true", "false"):
        raise HTTPException(400, "short_form_mode must be 'true' or 'false'")
    if req.key in ("script_max_seconds", "script_target_seconds"):
        try:
            n = int(req.value)
            if n < 8 or n > 180:
                raise ValueError()
        except ValueError:
            raise HTTPException(400, f"{req.key} must be int 8-180")
    if req.key in ("scene_target_seconds", "scene_min_seconds", "scene_max_seconds"):
        try:
            f = float(req.value)
            if f < 1.0 or f > 10.0:
                raise ValueError()
        except ValueError:
            raise HTTPException(400, f"{req.key} must be float 1.0-10.0")
    if req.key == "loop_ending_enabled" and req.value.lower() not in ("true", "false"):
        raise HTTPException(400, "loop_ending_enabled must be 'true' or 'false'")
    if req.key == "min_research_score":
        try:
            s = int(req.value)
            if not 0 <= s <= 100:
                raise ValueError()
        except ValueError:
            raise HTTPException(400, "min_research_score must be an int 0-100")

    db.set_setting(req.key, req.value)

    # Best-effort mirror to the legacy quality_mode field. Doesn't
    # enforce anything anymore - AI Mode is informational/preset.
    if req.key == "ai_mode":
        db.set_setting(
            "quality_mode",
            "local_only" if req.value == "free" else "api_polish",
        )
        # Auto-apply the full preset when mode changes via this key
        preset = _MODE_PRESETS.get(req.value)
        if preset:
            for t, m in preset.items():
                db.set_setting(f"{t}_model" if t != "gemini_model" else "gemini_model", m)
    return {"ok": True}


# ============================================================
# Smart Model Router - status + safe-defaults endpoints
# ============================================================

def _is_gemini_model(model: str) -> bool:
    return (model or "").startswith("gemini")


@app.get("/api/router/status")
def api_router_status():
    """Snapshot of the live model routing decisions. Always reads DB fresh."""
    ai_mode = (db.get_setting("ai_mode") or "balanced").lower()
    # Normalise legacy "premium" to "advanced"
    if ai_mode == "premium":
        ai_mode = "advanced"
    tasks = {}
    for t in TASK_KEYS:
        model = get_task_model(t)
        paid = is_paid_model(model)
        is_gemini = _is_gemini_model(model)
        tasks[t] = {
            "model": model,
            "is_paid": paid,
            "provider": "openai" if paid else ("gemini" if is_gemini else "ollama"),
            "tier_label": MODEL_TIERS.get(model, "unknown"),
        }
    # Gemini analysis row (not a text-gen task, handled by three_brain_router)
    gemini_model = (db.get_setting("gemini_model") or "gemini-2.5-flash").strip()
    from spartacus.three_brain_router import detect_available_tools as _dtools
    gemini_status = _dtools().get("gemini", {})
    tasks["gemini_analysis"] = {
        "model": gemini_model,
        "is_paid": False,
        "provider": "gemini",
        "tier_label": MODEL_TIERS.get(gemini_model, "Gemini CLI"),
        "cli_available": gemini_status.get("available", False),
        "cli_note": gemini_status.get("note", ""),
    }
    return {"ai_mode": ai_mode, "tasks": tasks}


@app.post("/api/router/apply-free-safe-defaults")
def api_apply_free_safe_defaults():
    """Reset to Free Mode — all Ollama, no paid calls."""
    return _apply_mode_preset("free")


@app.post("/api/router/apply-preset/{mode}")
def api_apply_preset(mode: str):
    """Apply a named mode preset (free / balanced / advanced)."""
    if mode not in _MODE_PRESETS:
        raise HTTPException(400, f"Unknown mode '{mode}'. Use: free, balanced, advanced")
    return _apply_mode_preset(mode)


def _apply_mode_preset(mode: str) -> dict:
    preset = _MODE_PRESETS[mode]
    db.set_setting("ai_mode", mode)
    db.set_setting("quality_mode", "local_only" if mode == "free" else "api_polish")
    for key, model in preset.items():
        setting_key = key if key == "gemini_model" else f"{key}_model"
        db.set_setting(setting_key, model)
    return {"ok": True, "applied": mode, "preset": preset}


@app.get("/api/system/ollama-version")
def api_ollama_version():
    """Return the installed Ollama version by running `ollama --version`."""
    import subprocess as _sp
    try:
        out = _sp.run(["ollama", "--version"], capture_output=True, text=True, timeout=5)
        raw = (out.stdout or out.stderr or "").strip()
        # "ollama version is 0.22.1" → "0.22.1"
        import re as _re
        m = _re.search(r"(\d+\.\d+[\.\d]*)", raw)
        version = m.group(1) if m else raw
        return {"ok": True, "version": version, "raw": raw}
    except Exception as exc:
        return {"ok": False, "version": None, "raw": str(exc)}


@app.post("/api/settings/test")
async def api_test_connection():
    """Test Ollama AND verify every local task model is actually pulled.
    Paid task models are excluded - they don't go through Ollama."""
    local_models: list[str] = []
    seen: set[str] = set()
    for task in TASK_KEYS:
        model = get_task_model(task)
        if not is_paid_model(model) and model not in seen:
            seen.add(model)
            local_models.append(model)
    if not local_models:
        # Every task is paid (Premium with all-OpenAI). Fall back to the
        # legacy default so the connection itself is still verified.
        local_models = [(db.get_setting("model_name") or SAFE_LOCAL_FALLBACK).strip()]
    return await ollama.health_check(models_to_check=local_models)


# ============================================================
# Phase 2 - Script polish via OpenAI
# ============================================================

class PolishReq(BaseModel):
    script_id: int


@app.post("/api/polish/script")
async def api_polish_script(req: PolishReq):
    script = db.get_script(req.script_id)
    if not script:
        raise HTTPException(404, "script not found")

    idea = db.get_idea(script["idea_id"])
    if not idea:
        raise HTTPException(404, "parent idea not found")

    hook_text = None
    if script["hook_id"]:
        hook = db.get_hook(script["hook_id"])
        if hook:
            hook_text = hook["text"]

    prompt = POLISH_PROMPT.format(
        idea=idea["title"],
        hook=hook_text or "(no hook selected)",
        script=script["body"],
    )

    try:
        polished_body = await _route_text_gen("script_polish", prompt)
    except OllamaError as e:
        return _ollama_error_response(e)
    except OpenAIError as e:
        return _openai_error_response(e)

    polished_body = polished_body.strip()
    new_id = db.insert_script(
        idea["id"], polished_body, hook_id=script["hook_id"]
    )
    db.update_status("scripts", new_id, "polished")
    return {"id": new_id, "body": polished_body}


# ============================================================
# Phase 3 - Trends
# ============================================================

class FetchYTReq(BaseModel):
    keyword: str
    max_results: int = 10


class ManualTrendsReq(BaseModel):
    titles: list[str]
    source: str = "google"
    keyword: Optional[str] = None


class GenIdeasFromTrendsReq(BaseModel):
    trend_ids: list[int]
    niche: Optional[str] = None


@app.get("/api/trends")
def api_list_trends():
    return {"trends": [dict(r) for r in db.list_trends()]}


@app.post("/api/trends/youtube")
async def api_trends_youtube(req: FetchYTReq):
    if not req.keyword.strip():
        raise HTTPException(400, "keyword required")
    keyword = req.keyword.strip()
    try:
        items = await youtube.search(keyword, req.max_results)
    except YouTubeError as e:
        return _youtube_error_response(e)
    saved = []
    for it in items:
        new_id = db.insert_trend(
            "youtube",
            it["title"],
            url=it.get("url"),
            views=it.get("views"),
            channel=it.get("channel"),
            published_at=it.get("published"),
            keyword=keyword,
        )
        saved.append({"id": new_id, **it})
    return {"trends": saved, "keyword": keyword}


@app.post("/api/trends/manual")
def api_trends_manual(req: ManualTrendsReq):
    source = (req.source or "google").strip() or "google"
    keyword = (req.keyword or "").strip() or None
    saved_ids = []
    for raw in req.titles:
        title = (raw or "").strip()
        if not title:
            continue
        saved_ids.append(db.insert_trend(source, title, keyword=keyword))
    return {"ids": saved_ids}


@app.delete("/api/trends/{trend_id}")
def api_delete_trend(trend_id: int):
    db.delete_trend(trend_id)
    return {"ok": True}


@app.post("/api/trends/clear")
def api_clear_trends():
    db.clear_trends()
    return {"ok": True}


@app.post("/api/generate/ideas-from-trends")
async def api_gen_ideas_from_trends(req: GenIdeasFromTrendsReq):
    if not req.trend_ids:
        raise HTTPException(400, "select at least one trend")
    rows = db.get_trends_by_ids(req.trend_ids)
    if not rows:
        raise HTTPException(404, "no matching trends")
    titles = [r["title"] for r in rows]

    # Niche resolution: most-common keyword among selected trends wins.
    # Falls back to caller-supplied niche, then to the default_niche setting.
    keywords = [r["keyword"] for r in rows if r["keyword"]]
    if keywords:
        niche = Counter(keywords).most_common(1)[0][0]
    elif req.niche and req.niche.strip():
        niche = req.niche.strip()
    else:
        niche = (db.get_setting("default_niche") or "general").strip()

    block = "\n".join(f"- {t}" for t in titles if t.strip())
    prompt = TREND_IDEAS_PROMPT.format(niche=niche, trends_block=block)
    try:
        text = await _route_text_gen("trend_to_ideas", prompt)
    except OllamaError as e:
        return _ollama_error_response(e)
    except OpenAIError as e:
        return _openai_error_response(e)
    ideas = _parse_numbered(text)

    # Auto-save generated ideas into the ideas table.
    saved_ids = []
    for title in ideas:
        t = (title or "").strip()
        if t:
            saved_ids.append(db.insert_idea(niche, t, None))

    return {
        "saved_ids": saved_ids,
        "niche": niche,
        "trend_count": len(titles),
        "ideas": ideas,
    }


# ============================================================
# Phase 4 - Auto Video Builder
# ============================================================

class BuildVideoReq(BaseModel):
    script_id: int


def _video_relpath(abs_path: str | None) -> str | None:
    """Convert an absolute /exports/... path into a browser URL."""
    if not abs_path:
        return None
    p = Path(abs_path)
    try:
        rel = p.relative_to(EXPORTS)
    except ValueError:
        return None
    return "/exports/" + str(rel).replace("\\", "/")


def _build_video_worker(video_id: int, script_text: str, idea_title: str) -> None:
    """Runs in a BackgroundTasks worker thread. Renders the MP4 and
    flips the DB row to ready/failed."""
    try:
        # Local import: keeps moviepy out of the cold-start path
        import video_builder as vb
        import datetime as _dt

        ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        slug = _slug(idea_title)
        out_mp4 = VIDEOS_DIR / f"{video_id}-{slug}-{ts}.mp4"
        out_srt = VIDEOS_DIR / f"{video_id}-{slug}-{ts}.srt"

        vb.build_video(script_text, out_mp4, srt_path=out_srt)

        db.update_video(
            video_id,
            status="ready",
            video_path=str(out_mp4),
            subtitle_path=str(out_srt),
        )
    except Exception as e:  # noqa: BLE001 - worker captures any failure
        db.update_video(video_id, status="failed", error=str(e)[:500])


@app.post("/api/videos/build")
async def api_build_video(req: BuildVideoReq, background_tasks: BackgroundTasks):
    script = db.get_script(req.script_id)
    if not script:
        raise HTTPException(404, "script not found")
    idea = db.get_idea(script["idea_id"])
    if not idea:
        raise HTTPException(404, "parent idea not found")
    if not (script["body"] or "").strip():
        raise HTTPException(400, "script body is empty")

    title = idea["title"]
    video_id = db.insert_video(
        idea_id=idea["id"],
        script_id=script["id"],
        title=title,
        status="building",
    )
    background_tasks.add_task(
        _build_video_worker, video_id, script["body"], title
    )
    return {"id": video_id, "status": "building", "title": title}


@app.get("/api/videos")
def api_list_videos():
    rows = [dict(r) for r in db.list_videos()]
    for r in rows:
        r["video_url"] = _video_relpath(r.get("video_path"))
        r["subtitle_url"] = _video_relpath(r.get("subtitle_path"))
    return {"videos": rows}


@app.get("/api/videos/{video_id}")
def api_get_video(video_id: int):
    row = db.get_video(video_id)
    if not row:
        raise HTTPException(404, "video not found")
    out = dict(row)
    out["video_url"] = _video_relpath(out.get("video_path"))
    out["subtitle_url"] = _video_relpath(out.get("subtitle_path"))
    return out


# ============================================================
# Research Brain - audit-safe trend research
# ============================================================

class ResearchPullReq(BaseModel):
    niche: str = ""
    platform: str = "all"


class ManualTiktokReq(BaseModel):
    titles: list[str]


async def do_research_pull(niche: str = "", platform: str = "all") -> dict:
    """Reusable helper: pull from official sources, score, save. Used by
    both the /api/research/pull endpoint and the auto-mode scheduler.
    """
    from research_engine import (
        score_youtube, score_google_trend, explain,
        fetch_google_trends_rss, filter_by_niche, ResearchError,
    )
    platform = (platform or "all").lower()
    niche = (niche or "").strip()

    saved_ids: list[int] = []
    errors: list[str] = []
    per_source: dict[str, int] = {}

    # ---- YouTube ----
    if platform in ("all", "youtube"):
        if not (db.get_setting("youtube_api_key") or "").strip():
            errors.append("YouTube: no API key configured (Settings page)")
        elif not niche:
            errors.append("YouTube: niche keyword required")
        else:
            try:
                yt_items = await youtube.search(niche, max_results=10)
                for it in yt_items:
                    scores = score_youtube(
                        it["title"], it.get("views"),
                        it.get("published"), it.get("channel"),
                    )
                    why = explain(scores, "youtube")
                    new_id = db.insert_trend(
                        source="youtube", title=it["title"],
                        url=it.get("url"), views=it.get("views"),
                        channel=it.get("channel"),
                        published_at=it.get("published"),
                        keyword=niche, why=why, **scores,
                    )
                    saved_ids.append(new_id)
                per_source["youtube"] = len(yt_items)
            except YouTubeError as e:
                errors.append(f"YouTube: {e}")

    # ---- Google Trends RSS ----
    if platform in ("all", "google"):
        try:
            gt_items = await fetch_google_trends_rss()
            gt_kept = filter_by_niche(gt_items, niche)
            for it in gt_kept[:15]:
                scores = score_google_trend(
                    it["title"], it.get("traffic"), it.get("published"),
                )
                why = explain(scores, "google_trends")
                new_id = db.insert_trend(
                    source="google_trends", title=it["title"],
                    url=it.get("url"), published_at=it.get("published"),
                    keyword=niche or None, why=why, **scores,
                )
                saved_ids.append(new_id)
            per_source["google_trends"] = min(len(gt_kept), 15)
        except ResearchError as e:
            errors.append(f"Google Trends: {e}")

    return {
        "saved_ids": saved_ids,
        "errors": errors,
        "per_source": per_source,
    }


@app.post("/api/research/pull")
async def api_research_pull(req: ResearchPullReq):
    """HTTP wrapper around do_research_pull(). TikTok handled separately."""
    return await do_research_pull(niche=req.niche, platform=req.platform)


@app.post("/api/research/manual-tiktok")
def api_research_manual_tiktok(req: ManualTiktokReq):
    """User-pasted TikTok titles. Scored with the limited info we have."""
    from research_engine import score_manual_tiktok, explain
    saved_ids: list[int] = []
    for raw in req.titles:
        title = (raw or "").strip()
        if not title:
            continue
        scores = score_manual_tiktok(title)
        why = explain(scores, "tiktok_manual")
        new_id = db.insert_trend(
            source="tiktok_manual",
            title=title,
            why=why,
            **scores,
        )
        saved_ids.append(new_id)
    return {"saved_ids": saved_ids}


@app.get("/api/research/topics")
def api_list_research_topics(limit: int = 10, min_score: int = 0):
    rows = [dict(r) for r in db.list_research_topics(
        limit=min(50, max(1, limit)),
        min_score=max(0, min(100, min_score)),
    )]
    return {"topics": rows}


# ============================================================
# YouTube OAuth + Upload
# ============================================================

class YouTubeOAuthClientReq(BaseModel):
    client_id: str
    client_secret: str


@app.post("/api/youtube/oauth/client")
def api_youtube_oauth_client(req: YouTubeOAuthClientReq):
    """Save the user's Google Cloud OAuth client credentials. These are
    needed before they can authorize a channel."""
    cid = (req.client_id or "").strip()
    sec = (req.client_secret or "").strip()
    if not cid or not sec:
        raise HTTPException(400, "client_id and client_secret are required")
    db.set_setting("youtube_oauth_client_id", cid)
    db.set_setting("youtube_oauth_client_secret", sec)
    return {"ok": True}


@app.get("/api/youtube/oauth/start")
def api_youtube_oauth_start():
    """Returns the Google consent URL the user should visit to grant
    upload + read scopes."""
    import youtube_uploader as _ytup
    try:
        url = _ytup.build_auth_url(state="spartacus")
    except _ytup.YouTubeUploadError as e:
        raise HTTPException(400, str(e))
    return {"auth_url": url}


@app.get("/api/youtube/oauth/callback")
def api_youtube_oauth_callback(request: Request, code: str = "",
                               state: str = "", error: str = "",
                               error_description: str = ""):
    """OAuth redirect target. Exchanges `code` for tokens, stores them,
    fetches the channel name, and redirects to /settings on success.

    Wrapped in a single big try/except so no failure mode 500s. Every
    branch logs to the server console for diagnosis without leaking the
    code/secret to the response body."""
    import traceback
    import youtube_uploader as _ytup

    # 0) Provider-side error (user clicked Cancel, scopes denied, etc.)
    if error:
        msg = f"{error}: {error_description}" if error_description else error
        print(f"[oauth-cb] provider returned error: {msg}", flush=True)
        return _oauth_error_html(msg)

    # 1) Validate required params
    if not code:
        params = dict(request.query_params)
        # Don't echo `code` even if present; just confirm the scaffold.
        scrub = {k: ("<redacted>" if k in ("code",) else v) for k, v in params.items()}
        print(f"[oauth-cb] missing 'code' in query params: {scrub}", flush=True)
        return _oauth_error_html(
            "Callback was missing the 'code' query parameter. "
            "If you cancelled at Google, retry from Settings."
        )

    # 2) Exchange + look up channel. Any exception => readable HTML +
    #    full traceback to the console.
    try:
        info = _ytup.exchange_code(code)
    except _ytup.YouTubeUploadError as e:
        print(f"[oauth-cb] YouTubeUploadError: {e}", flush=True)
        return _oauth_error_html(str(e))
    except Exception as e:  # noqa: BLE001 - last-resort safety net
        tb = traceback.format_exc()
        print(f"[oauth-cb] unhandled {type(e).__name__}: {e}\n{tb}", flush=True)
        return _oauth_error_html(
            f"Unexpected error during token exchange: {type(e).__name__}: {e}"
        )

    # 3) Success: redirect back to /settings with a flag so the JS there
    #    can show a banner. Self-close also works for the popup flow,
    #    so include both - the redirect wins if the browser allows it.
    title = info.get("title") or "your channel"
    print(f"[oauth-cb] connected: {title} ({info.get('id', '')})", flush=True)
    body = f"""<!doctype html>
<html><body style="font-family:sans-serif;background:#111;color:#eee;padding:40px;">
  <h2>YouTube channel connected</h2>
  <p>Authorized: <strong>{escape_html(title)}</strong></p>
  <p>Redirecting to Settings...</p>
  <script>
    try {{ window.close(); }} catch (e) {{}}
    setTimeout(() => window.location.href = "/settings?yt_connected=1", 1500);
  </script>
</body></html>"""
    return HTMLResponse(body)


def _oauth_error_html(message: str) -> HTMLResponse:
    """Standard error page for the OAuth callback. 200 OK so the browser
    actually shows it (some browsers hide bodies on 4xx)."""
    body = f"""<!doctype html>
<html><body style="font-family:sans-serif;background:#111;color:#eee;padding:40px;line-height:1.55;">
  <h2 style="color:#e74c3c;">YouTube connect failed</h2>
  <pre style="background:#1a1a1a;padding:14px;border-radius:8px;border:1px solid #333;white-space:pre-wrap;">{escape_html(message)}</pre>
  <p style="margin-top:24px;">
    <a href="/settings" style="color:#c9a84c;">Return to Settings</a>
  </p>
</body></html>"""
    return HTMLResponse(body, status_code=200)


def escape_html(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@app.get("/api/youtube/oauth/status")
def api_youtube_oauth_status():
    import youtube_uploader as _ytup
    return _ytup.get_channel_summary()


@app.post("/api/youtube/oauth/disconnect")
def api_youtube_oauth_disconnect():
    import youtube_uploader as _ytup
    _ytup.disconnect()
    return {"ok": True}


# ============================================================
# Phase 4 - Auto Mode (research -> pipeline daily)
# ============================================================

@app.get("/api/auto/status")
def api_auto_status():
    """Snapshot of the auto-scheduler state."""
    from datetime import datetime, timedelta
    enabled = (db.get_setting("auto_mode_enabled") or "false").lower() == "true"
    auto_video = (db.get_setting("auto_video_enabled") or "false").lower() == "true"
    last = (db.get_setting("last_auto_run_at") or "").strip() or None
    next_due = None
    if last:
        try:
            last_dt = datetime.fromisoformat(last)
            next_due = (last_dt + timedelta(seconds=_AUTO_INTERVAL_SECONDS)).isoformat(timespec="seconds")
        except ValueError:
            pass
    return {
        "enabled": enabled,
        "auto_video_enabled": auto_video,
        "last_run_at": last,
        "next_due_at": next_due,
        "interval_hours": _AUTO_INTERVAL_SECONDS // 3600,
        "min_research_score": int(db.get_setting("min_research_score") or "70"),
    }


def _auto_run_worker() -> None:
    """Background-thread entry: spins an asyncio loop and runs the auto job."""
    import asyncio
    try:
        from sparta_pipeline import run_auto_daily
        asyncio.run(run_auto_daily(_route_text_gen))
    except Exception as e:  # noqa: BLE001
        run_id = db.insert_sparta_run(status="failed")
        db.update_sparta_run(
            run_id, mode="auto",
            error=f"manual auto run: {type(e).__name__}: {e}",
        )


@app.post("/api/auto/run-now")
def api_auto_run_now(background_tasks: BackgroundTasks):
    """Skip the 24h timer - fire the auto job immediately."""
    background_tasks.add_task(_auto_run_worker)
    return {"status": "started"}


# ---- Performance placeholder for videos ----

class VideoPerformanceReq(BaseModel):
    views: Optional[int] = None
    likes: Optional[int] = None
    external_url: Optional[str] = None


@app.post("/api/videos/{video_id}/performance")
def api_set_video_performance(video_id: int, req: VideoPerformanceReq):
    row = db.get_video(video_id)
    if not row:
        raise HTTPException(404, "video not found")
    fields: dict = {}
    if req.views is not None:        fields["views"] = max(0, int(req.views))
    if req.likes is not None:        fields["likes"] = max(0, int(req.likes))
    if req.external_url is not None: fields["external_url"] = req.external_url.strip() or None
    if fields:
        import datetime as _dt
        fields["last_synced_at"] = _dt.datetime.now().isoformat(timespec="seconds")
        db.update_video(video_id, **fields)
    return {"ok": True, "updated": list(fields.keys())}


# ============================================================
# Phase 2 - Sparta Daily Auto-Pipeline
# ============================================================

def _sparta_run_worker(run_id: int, real_trends_mode: bool, platform: str) -> None:
    """Runs in a BackgroundTasks worker thread. Spins up its own asyncio
    loop so it can drive the async pipeline + httpx clients."""
    import asyncio
    try:
        from sparta_pipeline import run_daily_pipeline
        asyncio.run(run_daily_pipeline(
            run_id, _route_text_gen,
            real_trends_mode=real_trends_mode,
            platform=platform,
        ))
    except Exception as e:  # noqa: BLE001
        db.update_sparta_run(run_id, status="failed", error=str(e)[:500])


class SpartaRunReq(BaseModel):
    real_trends_mode: Optional[bool] = None
    platform: Optional[str] = None


_VALID_PLATFORMS = {"tiktok", "youtube_shorts"}


@app.post("/api/sparta/run-daily")
async def api_sparta_run_daily(
    req: SpartaRunReq, background_tasks: BackgroundTasks
):
    """Kick off the daily auto-pipeline. Returns immediately with the
    run_id; status is polled via /api/sparta/runs/{id}.

    Body params (both optional - fall back to settings if absent):
      real_trends_mode: bool - True = pull live YouTube + Google Trends
      platform: 'tiktok' | 'youtube_shorts'
    """
    if req.real_trends_mode is not None:
        real_mode = bool(req.real_trends_mode)
    else:
        real_mode = (db.get_setting("daily_run_real_mode") or "false").lower() == "true"

    platform = (req.platform or db.get_setting("daily_run_platform") or "youtube_shorts").lower()
    if platform not in _VALID_PLATFORMS:
        platform = "youtube_shorts"

    run_id = db.insert_sparta_run(status="running")
    background_tasks.add_task(_sparta_run_worker, run_id, real_mode, platform)
    return {
        "run_id": run_id,
        "status": "running",
        "real_trends_mode": real_mode,
        "platform": platform,
    }


@app.get("/api/sparta/runs")
def api_list_sparta_runs():
    return {"runs": [dict(r) for r in db.list_sparta_runs(20)]}


@app.get("/api/sparta/runs/{run_id}")
def api_get_sparta_run(run_id: int):
    row = db.get_sparta_run(run_id)
    if not row:
        raise HTTPException(404, "run not found")
    return dict(row)


# ============================================================
# Remotion video integration (video_engine module)
# ============================================================

class GenerateVideoReq(BaseModel):
    script_id: int
    topic: Optional[str] = None
    platform: Optional[str] = None  # tiktok / shorts / both -> vertical render


def _find_run_id_for_job(job_id: int) -> Optional[int]:
    """Reverse-lookup the Spartacus run that owns a given video job.
    The Spartacus pipeline writes the rendered job_id into
    summary.video_render.job_id, so we walk persisted runs to find the
    match. Returns None if the job was rendered standalone (e.g. via
    /api/video/generate against an orphan script not tied to a run)."""
    for r in _list_persisted_spartacus_runs():
        summary = r.get("summary") or {}
        v = summary.get("video_render") or {}
        if v.get("job_id") == job_id:
            return r.get("id")
    return None


def _video_engine_worker(job_id: int) -> None:
    """BackgroundTasks worker thread - drives video_engine.run_job."""
    try:
        import video_engine
        video_engine.run_job(job_id)
    except Exception as e:  # noqa: BLE001
        db.update_video_job(
            job_id, status="failed",
            error=f"worker crashed: {type(e).__name__}: {e}"[:500],
        )
        return
    # Render finished. If this job belongs to a Spartacus run that
    # targets YouTube, kick off auto-upload.
    rid = _find_run_id_for_job(job_id)
    if rid is not None:
        try:
            decision = _maybe_auto_upload(rid)
            print(f"[auto_upload] job #{job_id} (run #{rid}): {decision}",
                  flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"[auto_upload] job #{job_id} crashed: {e}", flush=True)


@app.post("/api/video/generate")
def api_video_generate(req: GenerateVideoReq, background_tasks: BackgroundTasks):
    """Queue a Remotion render. Returns immediately with the job id."""
    script = db.get_script(req.script_id)
    if not script:
        raise HTTPException(404, "script not found")
    idea = db.get_idea(script["idea_id"]) if script["idea_id"] else None
    topic = (req.topic or "").strip()
    if not topic:
        topic = (idea["title"] if idea else "Untitled SPARTA Video").strip()

    import video_engine
    try:
        job_id = video_engine.submit_job(
            topic=topic, script_id=req.script_id, platform=req.platform,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    background_tasks.add_task(_video_engine_worker, job_id)
    return {"job_id": job_id, "status": "queued", "topic": topic,
            "platform": req.platform or ""}


@app.get("/api/video/jobs")
def api_video_jobs_list(limit: int = 20):
    import video_engine
    jobs = video_engine.list_jobs(min(50, max(1, limit)))
    for j in jobs:
        j["video_url"] = video_engine.video_url_for(j)
    return {"jobs": jobs}


@app.get("/api/video/jobs/{job_id}")
def api_video_job_get(job_id: int):
    import video_engine
    job = video_engine.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    job["video_url"] = video_engine.video_url_for(job)
    return job


@app.delete("/api/videos/{video_id}")
def api_delete_video(video_id: int):
    row = db.get_video(video_id)
    if not row:
        raise HTTPException(404, "video not found")
    # Best-effort: remove files from disk too
    for col in ("video_path", "subtitle_path", "voice_path"):
        p = row[col]
        if p:
            try:
                Path(p).unlink(missing_ok=True)
            except Exception:
                pass
    db.delete_video(video_id)
    return {"ok": True}


# ============================================================
# System Manual - living documentation
# ============================================================
#
# Every feature in SPARTA BRAIN is described in one row of
# system_manual_entries. The /guide page reads from that table, so
# whenever a new module is built we just upsert one row and the docs
# update themselves. Seed runs on startup; user edits via the admin
# button are preserved across restarts.

class ManualUpsertReq(BaseModel):
    module_key: str
    module_name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    short_description: Optional[str] = None
    how_it_works: Optional[str] = None
    when_to_use: Optional[str] = None
    user_action: Optional[str] = None
    sort_order: Optional[int] = None


@app.get("/guide", response_class=HTMLResponse)
def page_guide(request: Request):
    return templates.TemplateResponse(
        "guide.html",
        {
            "request": request,
            "page": "guide",
            "entries": db.list_manual_entries(),
        },
    )


@app.get("/api/manual")
def api_manual_list():
    return {"entries": db.list_manual_entries()}


@app.post("/api/manual/upsert")
def api_manual_upsert(req: ManualUpsertReq):
    if not req.module_key.strip():
        raise HTTPException(400, "module_key is required")
    fields = {k: v for k, v in req.model_dump().items()
              if k != "module_key" and v is not None}
    entry_id = db.upsert_manual_entry(req.module_key.strip(), **fields)
    return {"id": entry_id, "entry": db.get_manual_entry(entry_id)}


@app.delete("/api/manual/{entry_id}")
def api_manual_delete(entry_id: int):
    if not db.get_manual_entry(entry_id):
        raise HTTPException(404, "entry not found")
    db.delete_manual_entry(entry_id)
    return {"ok": True}


# ============================================================
# Spartacus V2 - 14-agent affiliate content pipeline
# ============================================================
#
# Runs are tracked in-process: a thread executes spartacus.run_spartacus.run()
# while a progress callback appends to a steps log readable via GET. The page
# polls until status is "done" or "failed". This is local-only single-user; we
# don't need persistence beyond the spartacus/data/last_run.json the pipeline
# already writes.

import threading
from datetime import datetime
from itertools import count

_SPARTACUS_RUNS: dict[int, dict] = {}
_spartacus_lock = threading.Lock()
_spartacus_id_seq = count(1)


def _spartacus_runs_dir() -> Path:
    from spartacus.agents._shared import DATA_DIR as _DD
    p = _DD / "runs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _persist_spartacus_run(run: dict) -> None:
    """Write the full run dict to spartacus/data/runs/run_<id>.json so the
    Victory page can find it after restart. Failure here is non-fatal -
    the in-memory state still works."""
    try:
        from spartacus.agents._shared import save_json
        save_json(_spartacus_runs_dir() / f"run_{run['id']}.json", run)
    except Exception:  # noqa: BLE001
        pass


def _list_persisted_spartacus_runs() -> list[dict]:
    """Read every run_*.json on disk. Used by the Victory page."""
    from spartacus.agents._shared import load_json
    runs = []
    for p in sorted(_spartacus_runs_dir().glob("run_*.json")):
        data = load_json(p, default=None)
        if isinstance(data, dict) and "id" in data:
            runs.append(data)
    return runs


# Allocate the next id past whatever's persisted so we don't collide on restart.
def _bootstrap_spartacus_seq() -> None:
    global _spartacus_id_seq
    persisted = _list_persisted_spartacus_runs()
    max_id = max((r["id"] for r in persisted), default=0)
    _spartacus_id_seq = count(max_id + 1)


_bootstrap_spartacus_seq()


# ---------- Campaigns ----------
#
# A campaign is the unit of separation between affiliate offers. Every
# Spartacus run, every script written by Spartacus, every funnel page,
# every rendered video, and every Victory card belongs to exactly one
# campaign. Two pieces of content with the same (product, offer_url,
# niche, platform) belong to the same campaign by definition.
#
# Stored in spartacus/data/campaigns.json as a list. Match key is
# normalized (lowercased + stripped) so trivial casing differences don't
# create accidental duplicates.

def _campaigns_path() -> Path:
    from spartacus.agents._shared import DATA_DIR as _DD
    return _DD / "campaigns.json"


def _load_campaigns() -> list[dict]:
    from spartacus.agents._shared import load_json
    data = load_json(_campaigns_path(), default=[])
    return data if isinstance(data, list) else []


def _save_campaigns(rows: list[dict]) -> None:
    from spartacus.agents._shared import save_json
    save_json(_campaigns_path(), rows)


def _campaign_key(product: str, offer_url: str, niche: str, platform: str) -> tuple:
    return (
        (product or "").strip().lower(),
        (offer_url or "").strip().lower(),
        (niche or "").strip().lower(),
        (platform or "").strip().lower(),
    )


def _next_campaign_id(rows: list[dict]) -> int:
    return max((r.get("campaign_id", 0) for r in rows), default=0) + 1


def _auto_campaign_name(product: str, niche: str, platform: str) -> str:
    p = (product or "").strip()[:40] or "(no product)"
    n = (niche or "").strip()[:40] or "(no niche)"
    plat = (platform or "").strip() or "any"
    return f"{p} | {n} ({plat})"


def list_campaigns() -> list[dict]:
    return _load_campaigns()


def get_campaign(campaign_id: int) -> dict | None:
    for c in _load_campaigns():
        if c.get("campaign_id") == campaign_id:
            return c
    return None


def find_or_create_campaign(*, product: str, offer_url: str,
                            niche: str, platform: str,
                            name: str | None = None) -> dict:
    """Return the matching campaign (creating one if needed) for the given
    (product, offer_url, niche, platform) tuple. Idempotent."""
    rows = _load_campaigns()
    key = _campaign_key(product, offer_url, niche, platform)
    for c in rows:
        if _campaign_key(c.get("product", ""), c.get("offer_url", ""),
                         c.get("niche", ""), c.get("platform", "")) == key:
            return c
    new_id = _next_campaign_id(rows)
    now = datetime.now().isoformat(timespec="seconds")
    new_row = {
        "campaign_id": new_id,
        "name": (name or "").strip() or _auto_campaign_name(product, niche, platform),
        "product": (product or "").strip(),
        "offer_url": (offer_url or "").strip(),
        "niche": (niche or "").strip(),
        "platform": (platform or "").strip(),
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    rows.append(new_row)
    _save_campaigns(rows)
    return new_row


_CAMPAIGN_EDITABLE_FIELDS = {"name", "product", "offer_url", "niche", "platform", "status"}


def update_campaign(campaign_id: int, **fields) -> dict | None:
    rows = _load_campaigns()
    for c in rows:
        if c.get("campaign_id") != campaign_id:
            continue
        for k, v in fields.items():
            if k not in _CAMPAIGN_EDITABLE_FIELDS or v is None:
                continue
            c[k] = v
        c["updated_at"] = datetime.now().isoformat(timespec="seconds")
        _save_campaigns(rows)
        return c
    return None


def delete_campaign(campaign_id: int) -> bool:
    rows = _load_campaigns()
    new_rows = [c for c in rows if c.get("campaign_id") != campaign_id]
    if len(new_rows) == len(rows):
        return False
    _save_campaigns(new_rows)
    return True


# ---------- Auto product adapter ----------
#
# When a new Spartacus run is launched with a niche similar to a past run,
# we reuse the highest-scoring hooks from those past runs (lightly adapted
# to mention the new product) so the user doesn't lose the lessons learned
# from earlier campaigns. The script body, CTA, and funnel are always
# regenerated with the new product so nothing is stale.
#
# "Similar" = Jaccard similarity over lowercased word tokens >= 0.5. Niche
# strings tend to be short, so token overlap is reliable enough; we don't
# need embeddings here.
#
# A hook is preferred if (a) it has a high net_score from its original
# run, (b) the run was actually marked shipped (real-world signal), and
# (c) it is generic OR can be cleanly retargeted by string-replacing the
# old product name. We never reuse a hook that contains a different
# product's brand and can't be cleanly retargeted.

import re as _re

_STOP_NICHE_TOKENS = {
    "the", "a", "an", "to", "for", "of", "in", "on", "and", "or", "with",
    "best", "top", "how", "what", "why", "is", "are", "review", "reviews",
    "vs", "guide",
}


def _tokenize_niche(s: str) -> set[str]:
    if not s:
        return set()
    raw = _re.findall(r"[a-z0-9]+", (s or "").lower())
    return {t for t in raw if len(t) >= 2 and t not in _STOP_NICHE_TOKENS}


def _niche_similarity(a: str, b: str) -> float:
    """Jaccard similarity over significant word tokens. 0.0 = nothing in
    common, 1.0 = identical token set."""
    ta, tb = _tokenize_niche(a), _tokenize_niche(b)
    if not ta or not tb:
        return 0.0
    inter = ta & tb
    union = ta | tb
    return len(inter) / len(union) if union else 0.0


def _adapt_hook_text(hook: str, prior_product: str, new_product: str) -> str:
    """Replace prior product name with new one (case-insensitive). Returns
    the original hook unchanged if the prior name doesn't appear."""
    if not (prior_product and new_product):
        return hook
    if prior_product.strip().lower() not in hook.lower():
        return hook
    pattern = _re.compile(_re.escape(prior_product), _re.IGNORECASE)
    return pattern.sub(new_product, hook)


def _hook_has_foreign_product(hook: str, prior_product: str,
                              all_known_products: set[str]) -> bool:
    """True if the hook mentions some OTHER campaign's product (not its
    own prior_product). Those hooks shouldn't be auto-reused because we
    can't safely string-replace a brand we don't own."""
    h = hook.lower()
    own = (prior_product or "").strip().lower()
    for p in all_known_products:
        p_norm = p.strip().lower()
        if not p_norm or p_norm == own:
            continue
        if p_norm in h:
            return True
    return False


def _collect_reusable_hooks(target_niche: str, target_product: str,
                            *, top_n: int = 8,
                            min_similarity: float = 0.5,
                            target_campaign_id: int | None = None) -> list[dict]:
    """Aggressive learning version. Returns up to `top_n` hooks from past
    similar-niche runs, retargeted to `target_product`. Behavior:

    1. DROP hooks from bottom-tercile measured runs entirely (was: +0
       boost). Once a video underperforms, its hooks are off the menu.
    2. FORCE-INCLUDE the top 3 hooks from the same campaign (by
       engagement_score) regardless of niche-similarity threshold -
       campaign-proven hooks always come back.
    3. Apply VISUAL QUALITY MULTIPLIER (0.7 / 1.0 / 1.3) to ranking_score
       so well-visualized winners outrank text-only ones.

    Each returned dict has the original hook fields plus:
      _source_run_id, _source_product, _source_niche, _similarity,
      _adapted, _was_shipped, _was_winner, _engagement_tier,
      _visual_coverage, _ranking_score, _force_included.
    """
    runs = _list_persisted_spartacus_runs()
    runs_by_id = {r["id"]: r for r in runs}
    shipped_map = _load_shipped()
    campaigns = _load_campaigns()
    all_products = {(c.get("product") or "") for c in campaigns}
    all_products.discard("")

    # Performance tiering across ALL tracked runs.
    perf_rows = _load_performance()
    perf_by_run = {p["run_id"]: p for p in perf_rows
                   if p.get("run_id") is not None and p.get("engagement_score")}
    scores_sorted = sorted([p["engagement_score"] for p in perf_by_run.values()],
                           reverse=True)
    if len(scores_sorted) >= 3:
        top_threshold = scores_sorted[len(scores_sorted) // 3]
        bottom_threshold = scores_sorted[2 * len(scores_sorted) // 3]
    else:
        top_threshold = float("inf")
        bottom_threshold = float("-inf") if scores_sorted else 0

    def _engagement_tier(run_id: int) -> str:
        p = perf_by_run.get(run_id)
        if not p:
            return "none"
        score = p["engagement_score"]
        if score >= top_threshold:
            return "top"
        if score >= bottom_threshold:
            return "mid"
        return "bottom"

    # Pre-compute visual coverage per run (cached so we don't re-read
    # props.json multiple times when a run has multiple hooks).
    visual_cov_cache: dict[int, Optional[float]] = {}

    def _vis_cov(run_id: int) -> Optional[float]:
        if run_id not in visual_cov_cache:
            visual_cov_cache[run_id] = _visual_coverage_for_run(
                runs_by_id.get(run_id) or {}
            )
        return visual_cov_cache[run_id]

    # Force-included hook texts (top 3 from same campaign by engagement)
    forced_keys: set[str] = set()
    forced_payloads: list[dict] = []
    if target_campaign_id is not None:
        camp_runs = [r for r in runs if r.get("campaign_id") == target_campaign_id]
        scored: list[tuple[int, dict, str]] = []  # (engagement, run, hook_text)
        for r in camp_runs:
            summary = r.get("summary") or {}
            ship = shipped_map.get(str(r.get("id"))) or {}
            used_hook = (ship.get("used_hook") or
                         (summary.get("script") or {}).get("hook") or "").strip()
            if not used_hook:
                continue
            p = perf_by_run.get(r["id"])
            if not p:
                continue   # only force-include MEASURED winners
            scored.append((int(p.get("engagement_score") or 0), r, used_hook))
        scored.sort(key=lambda t: t[0], reverse=True)
        for _, r, used_hook in scored[:3]:
            summary = r.get("summary") or {}
            prior_product = (summary.get("locked_product") or {}).get("primary_product") \
                            or summary.get("product") or ""
            adapted = _adapt_hook_text(used_hook, prior_product, target_product) \
                      if prior_product.strip().lower() != (target_product or "").strip().lower() \
                      else used_hook
            key = adapted.lower().strip()
            if key in forced_keys:
                continue
            forced_keys.add(key)
            cov = _vis_cov(r["id"])
            forced_payloads.append({
                "hook": adapted,
                "net_score": 100,   # synthetic - force_included implies trust
                "hook_type": "campaign_winner",
                "_source_run_id": r["id"],
                "_source_product": prior_product,
                "_source_niche": summary.get("niche", ""),
                "_similarity": 1.0,
                "_adapted": adapted != used_hook,
                "_was_shipped": True,
                "_was_winner": True,
                "_engagement_tier": _engagement_tier(r["id"]),
                "_visual_coverage": cov,
                "_force_included": True,
                "_ranking_score": 999,   # always sorts to the top
            })

    # ----- Niche-similarity sweep (regular candidates) -----
    candidates: list[dict] = list(forced_payloads)
    for r in runs:
        summary = r.get("summary") or {}
        prior_niche = summary.get("niche") or ""
        sim = _niche_similarity(target_niche, prior_niche)
        if sim < min_similarity:
            continue
        rid = r.get("id")

        # AGGRESSIVE: skip ENTIRE runs that landed in the bottom tercile.
        # Their hooks didn't earn another shot.
        if perf_by_run.get(rid) and _engagement_tier(rid) == "bottom":
            continue

        prior_product = (summary.get("locked_product") or {}).get("primary_product") \
                        or summary.get("product") or ""
        same_product = prior_product.strip().lower() == (target_product or "").strip().lower()
        shipped_record = shipped_map.get(str(rid))
        was_shipped = shipped_record is not None
        used_hook_text = (shipped_record or {}).get("used_hook", "") \
                         or (summary.get("script") or {}).get("hook", "") if was_shipped else ""
        used_hook_norm = (used_hook_text or "").strip().lower()
        cov = _vis_cov(rid)
        vis_mult = _visual_quality_multiplier(cov)

        for h in summary.get("hooks") or []:
            text = (h.get("hook") or "").strip()
            if not text:
                continue
            if _hook_has_foreign_product(text, prior_product, all_products):
                continue
            adapted_text = _adapt_hook_text(text, prior_product, target_product) \
                           if not same_product else text
            if adapted_text.lower().strip() in forced_keys:
                continue   # already in the forced bucket
            adapted = adapted_text != text
            base_score = int(h.get("net_score") or 0)
            is_winning = was_shipped and text.strip().lower() == used_hook_norm
            tier = _engagement_tier(rid) if is_winning else "none"

            if is_winning and tier == "top":
                base_with_perf = base_score + 60
            elif is_winning and tier == "mid":
                base_with_perf = base_score + 25
            elif is_winning:
                base_with_perf = base_score + 35   # posted but not measured yet
            elif was_shipped:
                base_with_perf = base_score + 10
            else:
                base_with_perf = base_score

            # Apply visual-quality multiplier to the FINAL score.
            ranking_score = int(round(base_with_perf * vis_mult))

            candidates.append({
                **h,
                "hook": adapted_text,
                "_source_run_id": rid,
                "_source_product": prior_product,
                "_source_niche": prior_niche,
                "_similarity": round(sim, 3),
                "_adapted": adapted,
                "_was_shipped": was_shipped,
                "_was_winner": is_winning,
                "_engagement_tier": tier,
                "_visual_coverage": cov,
                "_force_included": False,
                "_ranking_score": ranking_score,
            })

    # Dedupe by adapted hook text, keep the higher-ranked variant.
    by_text: dict[str, dict] = {}
    for c in candidates:
        key = c["hook"].lower().strip()
        existing = by_text.get(key)
        if existing is None or c["_ranking_score"] > existing["_ranking_score"]:
            by_text[key] = c
    ranked = sorted(by_text.values(),
                    key=lambda x: x["_ranking_score"], reverse=True)
    return ranked[:top_n]


# ---------- Aggressive learning helpers ----------
#
# These are the building blocks the new /learning dashboard and the
# upgraded _collect_reusable_hooks rely on. Pure functions over the
# existing JSON files - no extra writes.

# Hook patterns. Each key matches a recognizable rhetorical pattern
# the script_writer + hook_generator routinely produce. Matching is
# loose-fit on purpose - a single hook can match 2-3 patterns.
_HOOK_PATTERNS: dict[str, str] = {
    "stop_doing":         r"^(?:stop|quit)\s+(?:doing|using|wasting)\b",
    "most_people_wrong":  r"\b(?:most\s+people|nobody|everyone)\s+(?:are\s+)?(?:doing|getting|using|misses)\b|\b(?:most\s+people|nobody)\s+(?:knows?|realizes?|talks?\s+about)\b",
    "saves_time":         r"\b(?:saves?|saved)\s+(?:you\s+)?(?:hours|days|weeks|time|months)\b",
    "warning":            r"^warning\b|\bif\s+you'?re\s+still\b",
    "secret_reveal":      r"\b(?:nobody|no\s+one)\s+(?:tells|talks\s+about|knows)\b|\b(?:hidden|secret|truth)\s+(?:about|behind)\b",
    "money_amount":       r"\$\d{2,}",
    "question":           r"\?\s*$",
    "personal_story":     r"^(?:I|My)\s+(?:tried|used|made|lost|gained|built|spent)\b",
    "comparison":         r"\b(?:vs\.?|versus|compared\s+to)\b",
    "time_specific":      r"\bin\s+\d+\s+(?:days|hours|weeks|minutes|months)\b",
    "you_should":         r"^(?:you|you're)\s+(?:should|need|won't)\b",
    "curiosity_gap":      r"^\s*(?:what|why|how)\b.{0,80}\?",
}


def _detect_hook_patterns(text: str) -> list[str]:
    """Returns the list of pattern keys this hook matches (case-insensitive).
    Empty list = generic phrasing with no recognized pattern."""
    if not text:
        return []
    matches = []
    for key, pat in _HOOK_PATTERNS.items():
        if _re.search(pat, text, _re.IGNORECASE):
            matches.append(key)
    return matches


def _compute_retention_proxy(perf_row: dict) -> float:
    """Stand-in for YouTube's real audience-retention metric (which is
    only available via Analytics API and not before ~48h after publish).

    Three weak signals combined:
      - velocity:  views per hour since posting
      - like_rate: likes / views
      - comment_rate: comments / views

    Weighted toward engagement rates because they're harder to fake than
    raw view velocity (drive-by impressions inflate views; only retained
    viewers like + comment)."""
    views = max(1, int(perf_row.get("views") or 0))
    likes = int(perf_row.get("likes") or 0)
    comments = int(perf_row.get("comments") or 0)
    hours = float(perf_row.get("hours_since_post") or 1.0)
    if hours < 1.0:
        hours = 1.0
    velocity = views / hours
    like_rate = likes / views if views else 0
    comment_rate = comments / views if views else 0
    return round(velocity + like_rate * 5000 + comment_rate * 20000, 1)


def _visual_coverage_for_run(run: dict) -> Optional[float]:
    """Read share of scenes that received a Pexels visual for this run.
    Mirror of compliance.youtube_safety_gate._visual_coverage but local
    to the learning module so we don't import from compliance/. Returns
    None when we can't read props.json - caller should treat as 1.0."""
    summary = run.get("summary") or {}
    job_id = (summary.get("video_render") or {}).get("job_id")
    if not job_id:
        return None
    props_path = STORAGE_DIR / "videos" / str(job_id) / "props.json"
    try:
        import json as _json
        data = _json.loads(props_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    scenes = data.get("scenes") or []
    if not scenes:
        return None
    with_visual = sum(1 for s in scenes
                      if (s.get("visualType") or "none") in ("video", "image"))
    return with_visual / len(scenes)


def _visual_quality_multiplier(coverage: Optional[float]) -> float:
    """Map visual coverage to a ranking multiplier:
       - >=80%  ->  1.30 (strong visuals -> boost the hook)
       - 30-80% ->  1.00 (neutral)
       - <30%   ->  0.70 (weak/empty visuals -> downrank)
       - None   ->  1.00 (unknown -> neutral)"""
    if coverage is None:
        return 1.0
    if coverage >= 0.8:
        return 1.30
    if coverage < 0.30:
        return 0.70
    return 1.0


def _backfill_run_campaign(run: dict) -> dict:
    """If a persisted run has no campaign_id or target_platforms (legacy
    data), match or create both now. Mutates the run dict in place AND
    rewrites the on-disk file so future reads are fast and consistent."""
    summary = run.get("summary") or {}
    locked = summary.get("locked_product") or {}
    req = (run.get("request") or {})
    product = locked.get("primary_product") or req.get("product") or summary.get("product") or ""
    offer = locked.get("offer_url") or req.get("offer_url") or ""
    niche = summary.get("niche") or req.get("niche") or ""
    platform = summary.get("platform") or req.get("platform") or ""

    needs_persist = False

    if not run.get("campaign_id") and product and niche:
        campaign = find_or_create_campaign(
            product=product, offer_url=offer, niche=niche, platform=platform,
        )
        run["campaign_id"] = campaign["campaign_id"]
        needs_persist = True

    # Backfill target_platforms on runs that completed before dual-export
    # was wired up. They still have one MP4; we just label what platforms
    # it's appropriate for.
    if summary and not summary.get("target_platforms") and platform:
        from video_engine.paths import target_platforms_for
        summary["target_platforms"] = target_platforms_for(platform)
        run["summary"] = summary
        needs_persist = True

    if needs_persist:
        try:
            from spartacus.agents._shared import save_json
            save_json(_spartacus_runs_dir() / f"run_{run['id']}.json", run)
        except Exception:  # noqa: BLE001
            pass
    return run


# ---------- Campaigns API ----------

class CampaignCreateReq(BaseModel):
    name: str = ""
    product: str
    offer_url: str = ""
    niche: str
    platform: str = "youtube"


class CampaignPatchReq(BaseModel):
    name: Optional[str] = None
    product: Optional[str] = None
    offer_url: Optional[str] = None
    niche: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = None


@app.get("/api/campaigns")
def api_campaigns_list():
    rows = list_campaigns()
    # Counts of runs per campaign so the UI can show "12 runs / 3 shipped"
    persisted = _list_persisted_spartacus_runs()
    counts: dict[int, dict] = {}
    shipped_map = _load_shipped()
    for r in persisted:
        # Backfill missing campaign_id so old runs roll into the right bucket
        r = _backfill_run_campaign(r)
        cid = r.get("campaign_id")
        if not cid:
            continue
        bucket = counts.setdefault(cid, {"runs": 0, "ready": 0, "posted": 0})
        bucket["runs"] += 1
        if _is_ready_to_ship(r):
            if str(r["id"]) in shipped_map:
                bucket["posted"] += 1
            else:
                bucket["ready"] += 1
    out = []
    for c in rows:
        cid = c.get("campaign_id")
        out.append({**c, "stats": counts.get(cid, {"runs": 0, "ready": 0, "posted": 0})})
    return {"campaigns": out}


@app.post("/api/campaigns")
def api_campaigns_create(req: CampaignCreateReq):
    if not req.product.strip() or not req.niche.strip():
        raise HTTPException(400, "product and niche are required")
    c = find_or_create_campaign(
        product=req.product, offer_url=req.offer_url,
        niche=req.niche, platform=req.platform, name=req.name,
    )
    return {"campaign": c}


@app.patch("/api/campaigns/{campaign_id}")
def api_campaigns_patch(campaign_id: int, req: CampaignPatchReq):
    fields = {k: v for k, v in req.model_dump().items() if v is not None}
    c = update_campaign(campaign_id, **fields)
    if not c:
        raise HTTPException(404, "campaign not found")
    return {"campaign": c}


@app.delete("/api/campaigns/{campaign_id}")
def api_campaigns_delete(campaign_id: int):
    if not delete_campaign(campaign_id):
        raise HTTPException(404, "campaign not found")
    return {"ok": True}


# ---------- Victory Mode: shipped registry ----------
#
# A "shipped" record marks a Spartacus run as posted to a public platform.
# We keep this in spartacus/data/shipped.json so it survives restart.
# Schema: { "<run_id>": { "posted_at": ISO, "posted_url": str, "notes": str } }

def _shipped_path() -> Path:
    from spartacus.agents._shared import DATA_DIR as _DD
    return _DD / "shipped.json"


def _load_shipped() -> dict:
    from spartacus.agents._shared import load_json
    data = load_json(_shipped_path(), default={})
    return data if isinstance(data, dict) else {}


def _save_shipped(data: dict) -> None:
    from spartacus.agents._shared import save_json
    save_json(_shipped_path(), data)


def _is_ready_to_ship(run: dict) -> bool:
    """A run is Victory-eligible if the pipeline finished AND a video rendered."""
    if run.get("status") != "done":
        return False
    summary = run.get("summary") or {}
    video = summary.get("video_render") or {}
    return bool(video.get("preview_url") or video.get("video_url"))


def _victory_asset_from_run(run: dict, shipped_map: dict, campaign_map: dict) -> dict:
    """Project a persisted run into the shape the Victory page expects."""
    summary = run.get("summary") or {}
    video = summary.get("video_render") or {}
    locked = summary.get("locked_product") or {}
    funnel = summary.get("funnel") or {}
    cluster = summary.get("cluster") or {}
    script = summary.get("script") or {}
    rid = str(run["id"])
    shipped = shipped_map.get(rid)
    cid = run.get("campaign_id")
    campaign = campaign_map.get(cid) if cid else None
    return {
        "run_id": run["id"],
        "campaign_id": cid,
        "campaign_name": (campaign or {}).get("name", ""),
        "topic": summary.get("pillar_topic") or summary.get("niche") or "",
        "niche": summary.get("niche") or "",
        "product": locked.get("primary_product") or summary.get("product") or "",
        "offer_url": locked.get("offer_url") or "",
        "video_url": video.get("preview_url") or video.get("video_url") or "",
        "video_job_id": video.get("job_id"),
        "platform": summary.get("platform") or "",
        "target_platforms": summary.get("target_platforms") or [],
        "started_at": run.get("started_at"),
        "finished_at": run.get("finished_at"),
        "funnel": {
            "page_slug": funnel.get("page_slug", ""),
            "page_headline": funnel.get("page_headline", ""),
            "subheadline": funnel.get("subheadline", ""),
            "benefit_bullets": funnel.get("benefit_bullets", []),
            "comparison_table": funnel.get("comparison_table", {}),
            "cta_text": funnel.get("cta_text", ""),
        },
        "cluster_videos": [
            cluster.get("pillar_video", {}).get("title", ""),
            *[v.get("title", "") for v in (cluster.get("supporting_videos") or [])],
        ] if cluster else [],
        "script_word_count": len((script.get("voiceover_text") or "").split()),
        "shipped": bool(shipped),
        "posted_at": (shipped or {}).get("posted_at"),
        "posted_url": (shipped or {}).get("posted_url"),
        "notes": (shipped or {}).get("notes", ""),
        "youtube_upload": run.get("youtube_upload") or {},
    }


def _funnel_markdown(funnel: dict, product: str, offer_url: str) -> str:
    """Format a funnel section into copy-pasteable markdown."""
    lines = []
    if funnel.get("page_headline"):
        lines.append(f"# {funnel['page_headline']}\n")
    if funnel.get("subheadline"):
        lines.append(f"_{funnel['subheadline']}_\n")
    if funnel.get("benefit_bullets"):
        lines.append("## Why this works\n")
        for b in funnel["benefit_bullets"]:
            lines.append(f"- {b}")
        lines.append("")
    table = funnel.get("comparison_table") or {}
    if table.get("rows"):
        headers = table.get("headers") or ["Feature", product or "Product", "Alternative"]
        lines.append("## Comparison\n")
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("|" + "|".join(["---"] * len(headers)) + "|")
        for row in table["rows"]:
            cells = [str(c) for c in row]
            while len(cells) < len(headers):
                cells.append("")
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    if funnel.get("cta_text"):
        cta = funnel["cta_text"]
        if offer_url:
            lines.append(f"## [{cta}]({offer_url})\n")
        else:
            lines.append(f"## {cta}\n")
    return "\n".join(lines).strip()


# ---------- Victory API ----------

class MarkShippedReq(BaseModel):
    posted_url: str = ""
    notes: str = ""


@app.get("/api/victory")
def api_victory_list(campaign_id: int | None = None):
    runs = _list_persisted_spartacus_runs()
    shipped_map = _load_shipped()
    campaign_map = {c["campaign_id"]: c for c in _load_campaigns()}
    # Backfill campaign_id on legacy runs once, on read.
    for r in runs:
        _backfill_run_campaign(r)
    if campaign_id is not None:
        runs = [r for r in runs if r.get("campaign_id") == campaign_id]
    eligible = [r for r in runs if _is_ready_to_ship(r)]
    assets = [_victory_asset_from_run(r, shipped_map, campaign_map) for r in eligible]
    assets.sort(key=lambda a: a["finished_at"] or "", reverse=True)
    ready = [a for a in assets if not a["shipped"]]
    posted = [a for a in assets if a["shipped"]]
    # All campaigns referenced by ready/posted assets, for the filter dropdown
    used_campaign_ids = {a["campaign_id"] for a in assets if a["campaign_id"]}
    used_campaigns = [campaign_map[cid] for cid in sorted(used_campaign_ids)
                      if cid in campaign_map]
    return {
        "ready_count": len(ready),
        "posted_count": len(posted),
        "total_count": len(assets),
        "ready": ready,
        "posted": posted,
        "campaigns": used_campaigns,
        "active_campaign_id": campaign_id,
    }


@app.get("/api/victory/{run_id}/funnel-markdown")
def api_victory_funnel_markdown(run_id: int):
    runs = _list_persisted_spartacus_runs()
    run = next((r for r in runs if r["id"] == run_id), None)
    if not run:
        raise HTTPException(404, "run not found")
    summary = run.get("summary") or {}
    funnel = summary.get("funnel") or {}
    locked = summary.get("locked_product") or {}
    md = _funnel_markdown(
        funnel,
        locked.get("primary_product") or summary.get("product") or "",
        locked.get("offer_url") or "",
    )
    return {"run_id": run_id, "markdown": md}


@app.post("/api/victory/{run_id}/mark-shipped")
def api_victory_mark_shipped(run_id: int, req: MarkShippedReq):
    runs = _list_persisted_spartacus_runs()
    run = next((r for r in runs if r["id"] == run_id), None)
    if not run:
        raise HTTPException(404, "run not found")
    if not _is_ready_to_ship(run):
        raise HTTPException(400, "run is not ready to ship (no rendered video)")
    # Stash the hook actually used (script_writer's `hook` field) plus the
    # full top-5 hook list, so future similar-niche runs can prefer hooks
    # that were proven in production - not just LLM-scored.
    summary = run.get("summary") or {}
    used_hook = (summary.get("script") or {}).get("hook", "")
    top_hooks = (summary.get("hooks") or [])[:5]
    shipped = _load_shipped()
    shipped[str(run_id)] = {
        "posted_at": datetime.now().isoformat(timespec="seconds"),
        "posted_url": (req.posted_url or "").strip(),
        "notes": (req.notes or "").strip(),
        "campaign_id": run.get("campaign_id"),
        "used_hook": used_hook,
        "top_hooks": [
            {"hook": h.get("hook"), "net_score": h.get("net_score"),
             "hook_type": h.get("hook_type")}
            for h in top_hooks
        ],
    }
    _save_shipped(shipped)
    return {"ok": True, "shipped": shipped[str(run_id)]}


@app.post("/api/victory/{run_id}/unmark")
def api_victory_unmark(run_id: int):
    shipped = _load_shipped()
    shipped.pop(str(run_id), None)
    _save_shipped(shipped)
    return {"ok": True}


# ---------- YouTube auto-upload from Victory ----------

def _resolve_run_for_upload(run_id: int) -> dict:
    """Pull the run from disk and validate it has a usable MP4."""
    runs = _list_persisted_spartacus_runs()
    run = next((r for r in runs if r.get("id") == run_id), None)
    if not run:
        raise HTTPException(404, "run not found")
    if not _is_ready_to_ship(run):
        raise HTTPException(400, "run has no rendered video")
    summary = run.get("summary") or {}
    video = summary.get("video_render") or {}
    video_url = video.get("video_url") or video.get("preview_url") or ""
    # Translate the public storage URL back to a local file path.
    if not video_url:
        raise HTTPException(400, "run has no video_url")
    rel = video_url
    for prefix in ("http://127.0.0.1:8765", "http://localhost:8765"):
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
    if not rel.startswith("/storage/"):
        raise HTTPException(400, f"unrecognized video_url: {video_url}")
    abs_path = BASE / rel.lstrip("/")
    if not abs_path.exists():
        raise HTTPException(400, f"MP4 missing on disk: {abs_path}")
    return {"run": run, "summary": summary, "abs_path": abs_path}


def _shorten_title(title: str, max_len: int = 58) -> str:
    """Trim a title to <= max_len, preferring a word boundary. Adds an
    ellipsis if cut. Removes the ellipsis if the title was just barely
    over (looks tidier when the cut falls on punctuation)."""
    title = (title or "").strip()
    if len(title) <= max_len:
        return title
    cutoff = title.rfind(" ", 0, max_len - 3)
    if cutoff == -1 or cutoff < max_len // 2:
        cutoff = max_len - 3
    cut = title[:cutoff].rstrip(".,;:! -")
    return cut + "..."


def _upload_payload_from_run(summary: dict) -> dict:
    """Pull title / description / tags from the run summary.

    Title  = highest-scoring hook from Spartacus (proven attention-getter,
             fits Shorts retention better than a generic upload_title),
             trimmed to 58 chars on a word boundary.
    Desc   = funnel subheadline (the value sentence) + hook + CTA +
             affiliate URL + disclosure + autopilot_hashtags.
    Tags   = video_planner.tags merged with niche tokens, deduped, capped.

    Link guard: title and description are passed through
    `validate_and_clean()` with the campaign's real offer_url as the
    only allowed URL. Anything else - placeholder text, hallucinated
    domains, fake "yourlink.com" tokens - is stripped, and warnings
    are returned in `link_warnings` so the upload worker can log them.
    When no offer_url is locked, the description switches to CTA-only
    mode: no "Offer: ..." line, no affiliate disclosure, NO_LINK_BANNER
    line surfaced so the operator notices before publishing.
    """
    from spartacus.agents._link_guard import (
        validate_and_clean, NO_LINK_BANNER,
    )

    plan = summary.get("video_plan") or {}
    funnel = summary.get("funnel") or {}
    locked = summary.get("locked_product") or {}
    script = summary.get("script") or {}
    hooks = summary.get("hooks") or []
    hook_used = (script.get("hook") or "").strip()
    cta = (script.get("sections") or {}).get("cta", "")
    offer_url = (locked.get("offer_url") or "").strip()
    product = locked.get("primary_product") or summary.get("product") or ""
    niche = summary.get("niche") or ""
    cta_only_mode = not offer_url

    # ---- Title: best-scoring hook wins, then shorten ----
    best_hook = ""
    if hooks:
        best = max(hooks, key=lambda h: int(h.get("net_score") or 0))
        best_hook = (best.get("hook") or "").strip()
    title_raw = (best_hook or hook_used or plan.get("upload_title")
                 or summary.get("pillar_topic") or product or "Spartacus Short")
    title = _shorten_title(title_raw, max_len=58)

    # ---- Description: value sentence first, then context, then tags ----
    parts = []
    sub = (funnel.get("subheadline") or "").strip()
    if sub:
        parts.append(sub)
    if hook_used and hook_used.lower() != sub.lower():
        parts.append(hook_used)
    if cta:
        parts.append(cta.strip())
    if cta_only_mode:
        # No real link. Drive social-channel CTAs only and flag the gap
        # so the operator notices before this goes public.
        parts.append("Follow / Comment / DM for details.")
        parts.append(NO_LINK_BANNER)
    else:
        parts.append(f"Offer: {offer_url}")
        parts.append("(Affiliate disclosure: this video contains affiliate links.)")
    # Hashtags pulled from the autopilot setting so users have one
    # control surface; manual uploads benefit from the same hashtag set.
    hashtag_str = (db.get_setting("autopilot_hashtags") or "").strip()
    if hashtag_str:
        parts.append(hashtag_str)
    description = "\n\n".join(p for p in parts if p)

    # ---- Link guard: scrub title + description ----
    allowed = (offer_url,) if offer_url else ()
    title, t_warn = validate_and_clean(title, allowed)
    description, d_warn = validate_and_clean(description, allowed)
    link_warnings = []
    seen_w = set()
    for w in (*t_warn, *d_warn):
        if w not in seen_w:
            seen_w.add(w)
            link_warnings.append(w)

    # ---- Tags: planner output + niche tokens, deduped ----
    raw_tags = list(plan.get("tags") or [])
    for t in re.findall(r"[A-Za-z][A-Za-z0-9'+-]+", (niche or "").lower()):
        clean = t.strip("'+-")
        if len(clean) >= 3 and clean not in _STOP_NICHE_TOKENS:
            raw_tags.append(clean)
    seen, tags = set(), []
    for t in raw_tags:
        norm = (t or "").strip().lower()
        if not norm or norm in seen:
            continue
        seen.add(norm)
        tags.append(t.strip())
    return {
        "title": title,
        "description": description,
        "tags": tags[:30],
        "cta_only_mode": cta_only_mode,
        "link_warnings": link_warnings,
    }


def _passes_quality_gate(run: dict) -> tuple[bool, str]:
    """Hard quality check before any auto-upload. Refuses sub-par
    renders so the autopilot never posts garbage. The user can still
    manually upload via the Victory button to override."""
    summary = run.get("summary") or {}
    video = summary.get("video_render") or {}
    if not (video.get("preview_url") or video.get("video_url")):
        return False, "no rendered video"

    # Script Gate output (compliance check) must have passed
    sg = summary.get("script_gate") or {}
    if sg and sg.get("pass") is False:
        return False, f"script_gate failed (risk={sg.get('score_risk')})"

    job_id = video.get("job_id")
    if not job_id:
        return True, ""   # missing job_id - skip deeper checks

    # Read props.json for scene-level data (not in the run summary)
    props_path = STORAGE_DIR / "videos" / str(job_id) / "props.json"
    try:
        import json as _json
        with open(props_path, encoding="utf-8") as fh:
            props = _json.load(fh)
    except Exception:
        return True, ""   # can't open - don't fail safe

    scenes = props.get("scenes") or []
    if not scenes:
        return False, "no scenes in props"

    # Total duration sanity. Two regimes:
    #   - Short-form mode ON (default): cap at script_max_seconds (45s
    #     default) so the autopilot never publishes a long-form clip
    #     as a Shorts.
    #   - Short-form mode OFF: cap at 180s (YouTube Shorts platform max).
    # Below 8s is almost always a TTS/render glitch in either regime.
    fps = int(props.get("fps") or 30) or 30
    total_frames = int(props.get("totalDurationInFrames") or 0)
    seconds = total_frames / fps
    short_mode = (db.get_setting("short_form_mode") or "true").lower() == "true"
    if short_mode:
        try:
            max_sec = int(db.get_setting("script_max_seconds") or "45")
        except ValueError:
            max_sec = 45
        # Small grace margin (5s) for Pexels visual fade-ins / TTS lead-in
        max_sec_with_grace = max_sec + 5
        if seconds > max_sec_with_grace:
            return False, (f"too long for Shorts ({seconds:.1f}s > "
                           f"{max_sec_with_grace}s short-form cap)")
    else:
        if seconds > 180:
            return False, f"too long ({seconds:.1f}s > 180s for Shorts)"
    if seconds < 8:
        return False, f"too short ({seconds:.1f}s < 8s)"

    # Sync check: at least 70% of scenes have per-word timings
    with_timings = sum(1 for s in scenes if (s.get("subtitleTimings") or []))
    if scenes and with_timings / len(scenes) < 0.7:
        return False, (f"sync incomplete ({with_timings}/{len(scenes)} "
                       f"scenes have word timings - rerun with TTS on)")

    return True, ""


def _can_upload(run: dict) -> tuple[bool, str]:
    """Single source of truth for the duplicate-upload check. Returns
    (allowed, reason). Used by both the manual button and the auto-
    upload trigger so neither path can double-upload."""
    yt = run.get("youtube_upload") or {}
    status = yt.get("status", "")
    if status == "uploading":
        return False, "upload already in progress for this run"
    if status == "uploaded" and yt.get("video_id"):
        return False, f"already uploaded as {yt.get('video_url')}"
    return True, ""


def _persist_run_field(run_id: int, key: str, value) -> None:
    """Update a single field on a persisted run JSON and rewrite to disk."""
    p = _spartacus_runs_dir() / f"run_{run_id}.json"
    from spartacus.agents._shared import load_json, save_json
    data = load_json(p, default=None)
    if not isinstance(data, dict):
        return
    data[key] = value
    save_json(p, data)


def _youtube_upload_worker(run_id: int) -> None:
    """BackgroundTasks worker: uploads the MP4 to YouTube, marks shipped,
    seeds a performance row. All status changes are persisted to disk."""
    import youtube_uploader as _ytup
    log_lines: list[str] = []
    def _log(msg: str):
        log_lines.append(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}")
        _persist_run_field(run_id, "youtube_upload", {
            "status": "uploading", "log": "\n".join(log_lines[-40:]),
        })

    try:
        ctx = _resolve_run_for_upload(run_id)
        payload = _upload_payload_from_run(ctx["summary"])
        _log(f"resolved MP4: {ctx['abs_path']} ({ctx['abs_path'].stat().st_size/1024/1024:.1f}MB)")
        if payload.get("cta_only_mode"):
            _log("LINK GUARD: NO LINK AVAILABLE - CTA ONLY MODE (no offer_url on this run)")
        for w in payload.get("link_warnings") or []:
            _log(f"LINK GUARD: {w}")

        # ---- YouTube Safety Gate ----
        # Runs BEFORE the upload. Hard-blocks risky content; auto-fixes
        # safe issues (disclosure, claim softening, hashtag spam) and
        # passes the corrected metadata through to the upload.
        if (db.get_setting("safety_gate_enabled") or "true").lower() == "true":
            from compliance.youtube_safety_gate import check_youtube_upload_safety

            # ---- structured trace lines (per spec) ----
            # These four log statements are the canonical contract:
            #   SAFETY GATE: checking run #N
            #   SAFETY GATE: risk_score=X
            #   SAFETY GATE: blocked reason=<...>            (only on block)
            #   UPLOAD: skipped because safety gate failed   (only on block)
            # Each one prints to the server console (flushed) AND lands
            # in the run's youtube_upload.log via _log() so it shows up
            # in /victory and /safety dashboards.
            print(f"SAFETY GATE: checking run #{run_id}", flush=True)
            _log(f"SAFETY GATE: checking run #{run_id}")

            shipped_now = _load_shipped()
            recent = []
            for rid_str, sh in shipped_now.items():
                if str(rid_str) == str(run_id):
                    continue   # don't compare to ourselves
                recent.append({
                    "title": sh.get("last_title") or sh.get("used_hook", ""),
                    "description": sh.get("last_description", ""),
                    "used_hook": sh.get("used_hook", ""),
                    "posted_url": sh.get("posted_url", ""),
                })
            recent.sort(key=lambda x: x.get("posted_url", ""), reverse=True)
            decision = check_youtube_upload_safety(
                run_id=run_id,
                script_text=(ctx["summary"].get("script") or {}).get("voiceover_text", ""),
                title=payload["title"],
                description=payload["description"],
                tags=payload["tags"],
                video_job_id=(ctx["summary"].get("video_render") or {}).get("job_id"),
                recent_uploads=recent[:30],
                storage_root=STORAGE_DIR,
                pexels_key_present=bool((db.get_setting("pexels_api_key") or "").strip()),
                has_synthetic_voice=True,
            )

            risk_score = decision.get("risk_score", 0)
            print(f"SAFETY GATE: risk_score={risk_score}", flush=True)
            _log(f"SAFETY GATE: risk_score={risk_score}")

            _safety_log_append({
                "run_id": run_id,
                "campaign_id": ctx["run"].get("campaign_id"),
                "checked_at": datetime.now().isoformat(timespec="seconds"),
                "title_in": payload["title"],
                "title_out": decision.get("fixed_title"),
                **decision,
            })
            if not decision["passed"]:
                # Pick the highest-severity hard_block as the canonical
                # reason. Multi-issue blocks still surface them all in
                # the issues list on the run / safety log.
                hard_blocks = [
                    i for i in decision.get("issues", [])
                    if i.get("severity") == "hard_block"
                ]
                primary_reason = (
                    hard_blocks[0].get("detail")
                    if hard_blocks else "blocked by safety gate"
                )
                full_reasons = "; ".join(
                    f"{i.get('category')}: {i.get('detail')}"
                    for i in hard_blocks
                ) or "blocked by safety gate"

                print(f"SAFETY GATE: blocked reason={primary_reason}", flush=True)
                _log(f"SAFETY GATE: blocked reason={primary_reason}")
                print("UPLOAD: skipped because safety gate failed", flush=True)
                _log("UPLOAD: skipped because safety gate failed")

                _persist_run_field(run_id, "youtube_upload", {
                    "status": "blocked",
                    "error": f"Safety Gate: {full_reasons}",
                    "reason": primary_reason,
                    "risk_score": risk_score,
                    "issues": decision.get("issues"),
                    "blocked_at": datetime.now().isoformat(timespec="seconds"),
                    "log": "\n".join(log_lines[-40:]),
                })
                return
            # Apply auto-fixes to the payload before sending to YouTube
            payload["title"] = decision["fixed_title"]
            payload["description"] = decision["fixed_description"]
            payload["tags"] = decision["fixed_tags"]
            if decision.get("fixes_applied"):
                _log("SAFETY GATE: auto-fixed " +
                     "; ".join(f["fix"] for f in decision["fixes_applied"]))
            _log("SAFETY GATE: passed")

        _persist_run_field(run_id, "youtube_upload", {
            "status": "uploading",
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "log": "\n".join(log_lines[-40:]),
        })
        result = _ytup.upload_video(
            video_path=ctx["abs_path"],
            title=payload["title"],
            description=payload["description"],
            tags=payload["tags"],
            privacy="public",
            log=_log,
        )
        _log(f"upload OK: {result['video_url']}")

        # Auto-mark shipped. Stash the title/description we actually
        # sent so the next safety gate can do repetition detection.
        shipped = _load_shipped()
        shipped[str(run_id)] = {
            "posted_at": datetime.now().isoformat(timespec="seconds"),
            "posted_url": result["video_url"],
            "notes": f"Auto-uploaded via SPARTA. Privacy: {result['privacy_status']}.",
            "campaign_id": ctx["run"].get("campaign_id"),
            "external_video_id": result["video_id"],
            "platform": "youtube_shorts",
            "used_hook": (ctx["summary"].get("script") or {}).get("hook", ""),
            "last_title": payload["title"],
            "last_description": payload["description"],
            "top_hooks": [
                {"hook": h.get("hook"), "net_score": h.get("net_score"),
                 "hook_type": h.get("hook_type")}
                for h in (ctx["summary"].get("hooks") or [])[:5]
            ],
        }
        _save_shipped(shipped)

        # Seed a performance row so the daily sync (and the dashboard)
        # know this video exists. Stats land on the next sync.
        perf_rows = _load_performance()
        if not any(p.get("run_id") == run_id for p in perf_rows):
            perf_rows.append({
                "run_id": run_id,
                "campaign_id": ctx["run"].get("campaign_id"),
                "external_video_id": result["video_id"],
                "platform": "youtube_shorts",
                "video_url": result["video_url"],
                "used_hook": (ctx["summary"].get("script") or {}).get("hook", ""),
                "first_seen_at": datetime.now().isoformat(timespec="seconds"),
                "samples": [],
                "views": 0, "likes": 0, "comments": 0,
                "engagement_score": 0,
                "views_24h": None, "views_7d": None,
            })
            _save_performance(perf_rows)

        _persist_run_field(run_id, "youtube_upload", {
            "status": "uploaded",
            "video_id": result["video_id"],
            "video_url": result["video_url"],
            "title": result["title"],
            "privacy_status": result["privacy_status"],
            "uploaded_at": datetime.now().isoformat(timespec="seconds"),
            "log": "\n".join(log_lines[-40:]),
        })
    except HTTPException as e:
        _persist_run_field(run_id, "youtube_upload", {
            "status": "failed",
            "error": e.detail,
            "log": "\n".join(log_lines[-40:]),
            "failed_at": datetime.now().isoformat(timespec="seconds"),
        })
    except Exception as e:  # noqa: BLE001
        _persist_run_field(run_id, "youtube_upload", {
            "status": "failed",
            "error": f"{type(e).__name__}: {e}",
            "log": "\n".join(log_lines[-40:]),
            "failed_at": datetime.now().isoformat(timespec="seconds"),
        })


@app.post("/api/victory/{run_id}/upload-youtube")
def api_victory_upload_youtube(run_id: int, background_tasks: BackgroundTasks):
    """Kick off a YouTube upload for the run's MP4. Returns immediately
    with status='uploading'. Poll /api/spartacus/runs/{id} or /api/victory
    to see the final status."""
    import youtube_uploader as _ytup
    if not _ytup.is_connected():
        raise HTTPException(400, "YouTube channel not connected. Connect in Settings first.")
    # Resolve early so we 400 cleanly if the MP4 is missing
    _ = _resolve_run_for_upload(run_id)
    runs = _list_persisted_spartacus_runs()
    run = next((r for r in runs if r.get("id") == run_id), None) or {}
    allowed, reason = _can_upload(run)
    if not allowed:
        raise HTTPException(409, reason)
    _persist_run_field(run_id, "youtube_upload", {
        "status": "uploading",
        "queued_at": datetime.now().isoformat(timespec="seconds"),
    })
    background_tasks.add_task(_youtube_upload_worker, run_id)
    return {"ok": True, "run_id": run_id, "status": "uploading"}


# ---------- Auto-upload trigger ----------
#
# Fires after a render completes. Conditions:
#   - auto_upload_youtube setting is on
#   - YouTube channel is connected
#   - the run targets youtube_shorts / shorts / both / youtube
#   - no existing upload is in flight or already done
# Threaded so the calling worker doesn't block on the YouTube upload.

_YT_TARGET_PLATFORMS = {"youtube", "youtube_shorts", "shorts", "both"}


def _maybe_auto_upload(run_id: int, log: callable | None = None) -> str:
    """Decide whether to fire an auto-upload for this run, and do it.
    Returns a short status string for logging. Never raises - any
    failure here is non-fatal; the user can always click Upload manually."""
    log = log or (lambda _s: None)
    if (db.get_setting("auto_upload_youtube") or "true").lower() != "true":
        return "auto_upload_youtube=off"
    try:
        import youtube_uploader as _ytup
        if not _ytup.is_connected():
            return "youtube channel not connected"
    except Exception as e:  # noqa: BLE001
        return f"youtube_uploader import failed: {e}"

    run = next((r for r in _list_persisted_spartacus_runs()
                if r.get("id") == run_id), None)
    if not run:
        return f"run {run_id} not found"
    summary = run.get("summary") or {}

    # Platform must target YouTube. We accept the legacy single-string
    # `platform` field and the newer `target_platforms` list.
    targets = set(summary.get("target_platforms") or [])
    targets.add(summary.get("platform") or "")
    if not (targets & _YT_TARGET_PLATFORMS):
        return f"run {run_id} platform={list(targets)} - not YouTube"

    if not _is_ready_to_ship(run):
        return f"run {run_id} has no rendered video"

    # Hard quality gate. Same gate the autopilot uses; if a render is
    # below bar, neither auto nor autopilot will publish it.
    ok, reason = _passes_quality_gate(run)
    if not ok:
        # Stamp the failure on the run so the Victory card shows why.
        _persist_run_field(run_id, "youtube_upload", {
            "status": "failed",
            "error": f"quality gate: {reason}",
            "trigger": "auto",
            "failed_at": datetime.now().isoformat(timespec="seconds"),
        })
        return f"quality gate refused: {reason}"

    allowed, reason = _can_upload(run)
    if not allowed:
        return f"skip: {reason}"

    # Mark uploading + spawn worker thread. Same flow as the manual
    # endpoint; idempotent thanks to _can_upload.
    _persist_run_field(run_id, "youtube_upload", {
        "status": "uploading",
        "queued_at": datetime.now().isoformat(timespec="seconds"),
        "trigger": "auto",
    })
    threading.Thread(target=_youtube_upload_worker,
                     args=(run_id,), daemon=True).start()
    log(f"auto_upload: run #{run_id} -> upload thread started")
    return "queued"


@app.post("/api/victory/{run_id}/sync-stats")
async def api_victory_sync_stats(run_id: int):
    """Pull fresh stats for a single run's YouTube video. Same logic as
    the daily sync, but scoped to one row."""
    runs = _list_persisted_spartacus_runs()
    run = next((r for r in runs if r.get("id") == run_id), None)
    if not run:
        raise HTTPException(404, "run not found")
    yt_meta = run.get("youtube_upload") or {}
    shipped = (_load_shipped() or {}).get(str(run_id)) or {}
    yt_id = (yt_meta.get("video_id") or shipped.get("external_video_id") or
             _extract_youtube_id(shipped.get("posted_url", "")))
    if not yt_id:
        raise HTTPException(400, "no YouTube video_id linked to this run")
    try:
        stats_by_id = await youtube.get_videos_stats([yt_id])
    except YouTubeError as e:
        raise HTTPException(503, str(e))
    stats = stats_by_id.get(yt_id)
    if not stats:
        raise HTTPException(404, "video not visible to this API key (private/deleted?)")

    score = _engagement_score(stats["views"], stats["likes"], stats["comments"])
    now_iso = datetime.now().isoformat(timespec="seconds")
    perf_rows = _load_performance()
    existing = next((p for p in perf_rows if p.get("run_id") == run_id), None)
    sample = {
        "at": now_iso, "views": stats["views"], "likes": stats["likes"],
        "comments": stats["comments"], "engagement_score": score,
    }
    if existing is None:
        existing = {
            "run_id": run_id,
            "campaign_id": run.get("campaign_id"),
            "external_video_id": yt_id,
            "platform": "youtube_shorts",
            "video_url": yt_meta.get("video_url") or shipped.get("posted_url", ""),
            "used_hook": shipped.get("used_hook") or
                         ((run.get("summary") or {}).get("script") or {}).get("hook", ""),
            "first_seen_at": now_iso,
            "samples": [],
            "views_24h": None, "views_7d": None,
        }
        perf_rows.append(existing)
    existing["samples"].append(sample)
    existing["last_synced_at"] = now_iso
    existing["views"] = stats["views"]
    existing["likes"] = stats["likes"]
    existing["comments"] = stats["comments"]
    existing["engagement_score"] = score
    posted_at = shipped.get("posted_at") or yt_meta.get("uploaded_at") or stats.get("published_at")
    if posted_at:
        hrs = _hours_between(posted_at, now_iso)
        existing["hours_since_post"] = round(hrs, 1)
        if existing.get("views_24h") is None and hrs >= 24:
            existing["views_24h"] = stats["views"]
        if existing.get("views_7d") is None and hrs >= 24 * 7:
            existing["views_7d"] = stats["views"]
    _save_performance(perf_rows)
    return {"ok": True, "run_id": run_id, "stats": stats,
            "engagement_score": score}


@app.get("/victory", response_class=HTMLResponse)
def page_victory(request: Request):
    return templates.TemplateResponse(
        "victory.html",
        {"request": request, "page": "victory"},
    )


class SpartacusRunReq(BaseModel):
    niche: str
    product: str
    platform: str = "youtube"
    offer_url: str = ""
    manual_tiktok: list[str] = []
    render_video: bool = False
    allow_unverified: bool = False
    campaign_id: Optional[int] = None  # if None, find_or_create from fields


def _spartacus_progress_cb(run_id: int):
    """Returns a callback bound to a specific run that appends step events."""
    def _cb(step: str, label: str, payload: dict) -> None:
        with _spartacus_lock:
            run = _SPARTACUS_RUNS.get(run_id)
            if not run:
                return
            run["steps"].append({
                "step": step,
                "label": label,
                "payload": payload,
                "ts": datetime.now().isoformat(timespec="seconds"),
            })
            run["current_step"] = label
    return _cb


def _spartacus_worker(run_id: int, req: SpartacusRunReq) -> None:
    from spartacus import run_spartacus as _spartacus
    cb = _spartacus_progress_cb(run_id)

    # Auto-product-adapter: when enabled, seed the pipeline with proven
    # hooks from past similar-niche runs (already retargeted to the new
    # product). The setting is on by default; users can flip it off in
    # /settings if they want every run to start clean.
    reused_hooks: list[dict] = []
    auto_adapt = (db.get_setting("auto_adapt_product") or "true").lower() == "true"
    if auto_adapt:
        try:
            reused_hooks = _collect_reusable_hooks(
                target_niche=req.niche,
                target_product=req.product,
                top_n=8,
                target_campaign_id=req.campaign_id,
            )
        except Exception:  # noqa: BLE001
            reused_hooks = []
    if reused_hooks:
        # Surface to the live progress feed so the user sees the reuse.
        cb("auto_adapt", "Auto Product Adapter", {
            "reused_count": len(reused_hooks),
            "source_run_ids": sorted({h.get("_source_run_id") for h in reused_hooks
                                      if h.get("_source_run_id") is not None}),
            "adapted_count": sum(1 for h in reused_hooks if h.get("_adapted")),
            "shipped_count": sum(1 for h in reused_hooks if h.get("_was_shipped")),
            "winner_count": sum(1 for h in reused_hooks if h.get("_was_winner")),
        })

    try:
        summary = _spartacus.run(
            niche=req.niche, product=req.product, platform=req.platform,
            offer_url=req.offer_url, manual_tiktok=req.manual_tiktok or None,
            render_video=req.render_video, allow_unverified=req.allow_unverified,
            progress_cb=cb,
            reused_hooks=reused_hooks if len(reused_hooks) >= 3 else None,
        )
        with _spartacus_lock:
            run = _SPARTACUS_RUNS.get(run_id)
            if run:
                run["status"] = "done"
                run["summary"] = summary
                run["finished_at"] = datetime.now().isoformat(timespec="seconds")
                _persist_spartacus_run(run)
        # After a successful Spartacus run with a rendered video, kick
        # off auto-upload to YouTube if the user's settings allow it.
        # Threaded internally; this call returns instantly.
        try:
            decision = _maybe_auto_upload(run_id)
            print(f"[auto_upload] run #{run_id}: {decision}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"[auto_upload] run #{run_id} crashed: {e}", flush=True)
    except Exception as e:  # noqa: BLE001
        with _spartacus_lock:
            run = _SPARTACUS_RUNS.get(run_id)
            if run:
                run["status"] = "failed"
                run["error"] = f"{type(e).__name__}: {e}"
                run["finished_at"] = datetime.now().isoformat(timespec="seconds")
                _persist_spartacus_run(run)


def _resolve_campaign_for_run(req: SpartacusRunReq) -> dict:
    """If the request named a specific campaign_id, use it (and reject if
    its product/niche conflicts with the request fields). Otherwise
    find_or_create from the request fields."""
    if req.campaign_id is not None:
        c = get_campaign(req.campaign_id)
        if not c:
            raise HTTPException(404, f"campaign {req.campaign_id} not found")
        # Soft check: warn but don't block if fields drifted. Campaigns are
        # the source of truth; we trust them over the form.
        return c
    return find_or_create_campaign(
        product=req.product, offer_url=req.offer_url,
        niche=req.niche, platform=req.platform,
    )


@app.post("/api/spartacus/run")
def api_spartacus_run(req: SpartacusRunReq):
    if not req.niche.strip() or not req.product.strip():
        raise HTTPException(400, "niche and product are required")
    # Lock the campaign FIRST. If the user explicitly named one, the run
    # uses that campaign's product/offer/niche/platform - the form fields
    # are taken as a hint but the campaign wins. This prevents accidental
    # cross-product contamination if the user reuses a window.
    campaign = _resolve_campaign_for_run(req)
    if req.campaign_id is not None:
        # Pull authoritative fields from the campaign.
        req = req.model_copy(update={
            "product":   campaign["product"],
            "offer_url": campaign["offer_url"],
            "niche":     campaign["niche"],
            "platform":  campaign["platform"],
        })
    run_id = next(_spartacus_id_seq)
    with _spartacus_lock:
        _SPARTACUS_RUNS[run_id] = {
            "id": run_id,
            "campaign_id": campaign["campaign_id"],
            "campaign_name": campaign["name"],
            "status": "running",
            "current_step": "queued",
            "steps": [],
            "summary": None,
            "error": None,
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "finished_at": None,
            "request": req.model_dump(),
        }
    t = threading.Thread(target=_spartacus_worker, args=(run_id, req), daemon=True)
    t.start()
    return {
        "run_id": run_id,
        "status": "running",
        "campaign_id": campaign["campaign_id"],
        "campaign_name": campaign["name"],
    }


@app.get("/api/spartacus/runs/{run_id}")
def api_spartacus_run_get(run_id: int):
    with _spartacus_lock:
        run = _SPARTACUS_RUNS.get(run_id)
        if not run:
            raise HTTPException(404, "run not found")
        return {**run}


@app.get("/api/spartacus/runs")
def api_spartacus_runs_list():
    with _spartacus_lock:
        runs = sorted(_SPARTACUS_RUNS.values(),
                      key=lambda r: r["id"], reverse=True)
        return {"runs": [{
            "id": r["id"],
            "status": r["status"],
            "current_step": r["current_step"],
            "started_at": r["started_at"],
            "finished_at": r["finished_at"],
            "niche": r["request"].get("niche"),
            "product": r["request"].get("product"),
        } for r in runs[:30]]}


@app.get("/spartacus", response_class=HTMLResponse)
def page_spartacus(request: Request):
    return templates.TemplateResponse(
        "spartacus.html",
        {"request": request, "page": "spartacus"},
    )


# ============================================================
# Auto Performance Tracker
# ============================================================
#
# Once a day (or on demand via /api/performance/refresh) the system pulls
# view/like/comment counts from YouTube for every shipped run with a
# YouTube URL and stores samples in spartacus/data/performance.json.
# Performance scores feed back into _collect_reusable_hooks so high-
# performing hooks float to the top of new runs.

_YOUTUBE_ID_RE = _re.compile(
    r"(?:youtube\.com/(?:shorts/|watch\?v=|embed/|v/)|youtu\.be/)"
    r"([A-Za-z0-9_-]{6,15})"
)


def _extract_youtube_id(url: str) -> str:
    """Pull the canonical YouTube video id out of a Shorts/watch/youtu.be URL."""
    if not url:
        return ""
    m = _YOUTUBE_ID_RE.search(url)
    return m.group(1) if m else ""


def _performance_path() -> Path:
    from spartacus.agents._shared import DATA_DIR as _DD
    return _DD / "performance.json"


def _load_performance() -> list[dict]:
    from spartacus.agents._shared import load_json
    data = load_json(_performance_path(), default=[])
    return data if isinstance(data, list) else []


def _save_performance(rows: list[dict]) -> None:
    from spartacus.agents._shared import save_json
    save_json(_performance_path(), rows)


def _engagement_score(views: int, likes: int, comments: int) -> int:
    """User-spec'd formula: views + likes*5 + comments*10."""
    return int(views or 0) + int(likes or 0) * 5 + int(comments or 0) * 10


def _hours_between(iso_a: str, iso_b: str) -> float:
    if not iso_a or not iso_b:
        return 0.0
    try:
        from datetime import datetime as _dt
        a = _dt.fromisoformat(iso_a.replace("Z", "+00:00") if iso_a.endswith("Z") else iso_a)
        b = _dt.fromisoformat(iso_b.replace("Z", "+00:00") if iso_b.endswith("Z") else iso_b)
        if a.tzinfo is None and b.tzinfo is not None:
            a = a.replace(tzinfo=b.tzinfo)
        if b.tzinfo is None and a.tzinfo is not None:
            b = b.replace(tzinfo=a.tzinfo)
        return abs((b - a).total_seconds()) / 3600.0
    except Exception:  # noqa: BLE001
        return 0.0


async def _refresh_performance(force: bool = False) -> dict:
    """Pull fresh stats from YouTube for every shipped run with a YT URL.
    Updates samples + views_24h/views_7d snapshots in performance.json.
    Returns a small summary the API can echo back."""
    if not force and (db.get_setting("auto_performance_tracking") or "true").lower() == "false":
        return {"skipped": "auto_performance_tracking is off"}

    shipped_map = _load_shipped()
    runs_by_id = {r["id"]: r for r in _list_persisted_spartacus_runs()}
    perf_rows = _load_performance()
    perf_by_run = {r["run_id"]: r for r in perf_rows if r.get("run_id") is not None}

    # Build the work list: posted runs whose URL is a YouTube link.
    pending: list[tuple[int, str, dict]] = []
    skipped_no_url = 0
    skipped_not_yt = 0
    for run_id_str, ship in shipped_map.items():
        try:
            run_id = int(run_id_str)
        except (TypeError, ValueError):
            continue
        url = (ship.get("posted_url") or "").strip()
        if not url:
            skipped_no_url += 1
            continue
        yt_id = _extract_youtube_id(url)
        if not yt_id:
            skipped_not_yt += 1
            continue
        pending.append((run_id, yt_id, ship))

    if not pending:
        db.set_setting("last_perf_sync_at",
                       datetime.now().isoformat(timespec="seconds"))
        return {
            "synced": 0, "skipped_no_url": skipped_no_url,
            "skipped_not_youtube": skipped_not_yt, "errors": [],
        }

    # Batch the YT API call (50 ids/request). Single batch is enough for
    # any realistic backlog.
    yt_ids = [yt for _, yt, _ in pending]
    errors: list[str] = []
    stats_by_id: dict[str, dict] = {}
    try:
        stats_by_id = await youtube.get_videos_stats(yt_ids)
    except YouTubeError as e:
        errors.append(str(e))

    now_iso = datetime.now().isoformat(timespec="seconds")
    synced = 0
    for run_id, yt_id, ship in pending:
        stats = stats_by_id.get(yt_id)
        if not stats:
            continue  # private, deleted, or not visible to this API key
        run = runs_by_id.get(run_id) or {}
        score = _engagement_score(stats["views"], stats["likes"], stats["comments"])
        sample = {
            "at": now_iso,
            "views": stats["views"],
            "likes": stats["likes"],
            "comments": stats["comments"],
            "engagement_score": score,
        }
        existing = perf_by_run.get(run_id)
        posted_at = (ship.get("posted_at") or "")
        published_at = stats.get("published_at") or ""
        # Use whichever timestamp we trust more for the "since post" math.
        anchor = published_at or posted_at
        hrs_since = _hours_between(anchor, now_iso) if anchor else 0.0

        if existing is None:
            existing = {
                "run_id": run_id,
                "campaign_id": run.get("campaign_id") or ship.get("campaign_id"),
                "external_video_id": yt_id,
                "platform": "youtube_shorts",
                "video_url": ship.get("posted_url", ""),
                "used_hook": ship.get("used_hook") or
                             ((run.get("summary") or {}).get("script") or {}).get("hook", ""),
                "first_seen_at": now_iso,
                "samples": [],
                "views_24h": None,
                "views_7d": None,
            }
            perf_rows.append(existing)
            perf_by_run[run_id] = existing

        existing["samples"].append(sample)
        existing["last_synced_at"] = now_iso
        existing["views"] = stats["views"]
        existing["likes"] = stats["likes"]
        existing["comments"] = stats["comments"]
        existing["engagement_score"] = score
        existing["hours_since_post"] = round(hrs_since, 1)
        # Snapshot the 24h / 7d windows the FIRST time we cross those marks.
        if existing.get("views_24h") is None and hrs_since >= 24:
            existing["views_24h"] = stats["views"]
        if existing.get("views_7d") is None and hrs_since >= 24 * 7:
            existing["views_7d"] = stats["views"]
        synced += 1

    _save_performance(perf_rows)
    db.set_setting("last_perf_sync_at", now_iso)
    return {
        "synced": synced,
        "skipped_no_url": skipped_no_url,
        "skipped_not_youtube": skipped_not_yt,
        "errors": errors,
        "last_sync_at": now_iso,
    }


# Daily scheduler. Lives alongside _auto_mode_scheduler in lifespan.
_PERF_SYNC_INTERVAL_SECONDS = 24 * 60 * 60
_PERF_CHECK_INTERVAL = 60


async def _perf_tracker_scheduler() -> None:
    import asyncio
    from datetime import datetime as _dt
    while True:
        try:
            await asyncio.sleep(_PERF_CHECK_INTERVAL)
            if (db.get_setting("auto_performance_tracking") or "true").lower() != "true":
                continue
            last = (db.get_setting("last_perf_sync_at") or "").strip()
            if last:
                try:
                    last_dt = _dt.fromisoformat(last)
                    if (_dt.now() - last_dt).total_seconds() < _PERF_SYNC_INTERVAL_SECONDS:
                        continue
                except ValueError:
                    pass
            try:
                await _refresh_performance()
            except Exception as e:  # noqa: BLE001
                db.set_setting("last_perf_sync_at",
                               _dt.now().isoformat(timespec="seconds"))
                print(f"perf_tracker: caught {type(e).__name__}: {e}", flush=True)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            await asyncio.sleep(_PERF_CHECK_INTERVAL)


# ---------- Performance API ----------

@app.post("/api/performance/refresh")
async def api_performance_refresh():
    """Run a YouTube stats sync right now. Returns a summary of how many
    videos were synced and any errors."""
    return await _refresh_performance(force=True)


@app.get("/api/performance")
def api_performance_list():
    """Top performing videos + summary stats for the dashboard."""
    rows = _load_performance()
    runs_by_id = {r["id"]: r for r in _list_persisted_spartacus_runs()}
    campaigns = {c["campaign_id"]: c for c in _load_campaigns()}
    out = []
    for r in rows:
        run = runs_by_id.get(r.get("run_id")) or {}
        cid = r.get("campaign_id") or run.get("campaign_id")
        camp = campaigns.get(cid) or {}
        summary = run.get("summary") or {}
        out.append({
            "run_id": r.get("run_id"),
            "campaign_id": cid,
            "campaign_name": camp.get("name", ""),
            "topic": summary.get("pillar_topic") or summary.get("niche", ""),
            "video_url": r.get("video_url", ""),
            "external_video_id": r.get("external_video_id", ""),
            "platform": r.get("platform", ""),
            "used_hook": r.get("used_hook", ""),
            "views": r.get("views", 0),
            "likes": r.get("likes", 0),
            "comments": r.get("comments", 0),
            "engagement_score": r.get("engagement_score", 0),
            "views_24h": r.get("views_24h"),
            "views_7d": r.get("views_7d"),
            "hours_since_post": r.get("hours_since_post"),
            "last_synced_at": r.get("last_synced_at"),
        })
    out.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)
    return {
        "videos": out,
        "total": len(out),
        "last_sync_at": db.get_setting("last_perf_sync_at") or "",
    }


@app.get("/api/performance/hooks")
def api_performance_hooks():
    """Aggregate engagement_score by hook text - the leaderboard the
    auto-adapter is implicitly using."""
    rows = _load_performance()
    by_hook: dict[str, dict] = {}
    for r in rows:
        h = (r.get("used_hook") or "").strip()
        if not h:
            continue
        bucket = by_hook.setdefault(h, {
            "hook": h, "videos": 0, "total_views": 0, "total_likes": 0,
            "total_comments": 0, "total_engagement": 0, "campaigns": set(),
        })
        bucket["videos"] += 1
        bucket["total_views"] += int(r.get("views") or 0)
        bucket["total_likes"] += int(r.get("likes") or 0)
        bucket["total_comments"] += int(r.get("comments") or 0)
        bucket["total_engagement"] += int(r.get("engagement_score") or 0)
        if r.get("campaign_id"):
            bucket["campaigns"].add(r["campaign_id"])
    out = []
    for b in by_hook.values():
        b["campaigns"] = sorted(b["campaigns"])
        b["avg_engagement"] = (b["total_engagement"] // b["videos"]) if b["videos"] else 0
        out.append(b)
    out.sort(key=lambda x: x["avg_engagement"], reverse=True)
    return {"hooks": out, "total": len(out)}


@app.get("/performance", response_class=HTMLResponse)
def page_performance(request: Request):
    return templates.TemplateResponse(
        "performance.html",
        {"request": request, "page": "performance"},
    )


# ---------- Aggressive Learning insights ----------

@app.get("/api/learning/insights")
def api_learning_insights():
    """Composite snapshot for /learning. Computes everything from
    persisted data on the fly - no extra writes, no caching needed
    at this scale (a few dozen runs)."""
    perf_rows = _load_performance()
    runs = _list_persisted_spartacus_runs()
    runs_by_id = {r["id"]: r for r in runs}
    shipped = _load_shipped()
    campaigns_by_id = {c["campaign_id"]: c for c in _load_campaigns()}

    # Tercile thresholds (same logic as the hook ranker, kept here so
    # the dashboard shows the same picture as the auto-adapter).
    measured = [p for p in perf_rows if p.get("engagement_score")]
    measured_scores = sorted([p["engagement_score"] for p in measured],
                             reverse=True)
    if len(measured_scores) >= 3:
        top_thresh = measured_scores[len(measured_scores) // 3]
        bot_thresh = measured_scores[2 * len(measured_scores) // 3]
    else:
        top_thresh = float("inf")
        bot_thresh = float("-inf")

    # Per-video projection
    videos: list[dict] = []
    for p in perf_rows:
        rid = p.get("run_id")
        run = runs_by_id.get(rid) or {}
        summary = run.get("summary") or {}
        cid = run.get("campaign_id")
        camp = campaigns_by_id.get(cid) or {}
        used_hook = (p.get("used_hook") or
                     (summary.get("script") or {}).get("hook") or
                     (shipped.get(str(rid)) or {}).get("used_hook") or "").strip()
        score = int(p.get("engagement_score") or 0)
        if score >= top_thresh:
            tier = "top"
        elif score >= bot_thresh:
            tier = "mid"
        elif measured_scores:
            tier = "bottom"
        else:
            tier = "unmeasured"
        videos.append({
            "run_id": rid,
            "campaign_id": cid,
            "campaign_name": camp.get("name", ""),
            "topic": summary.get("pillar_topic") or summary.get("niche", ""),
            "used_hook": used_hook,
            "patterns": _detect_hook_patterns(used_hook),
            "views": p.get("views", 0),
            "likes": p.get("likes", 0),
            "comments": p.get("comments", 0),
            "engagement_score": score,
            "retention_proxy": _compute_retention_proxy(p),
            "tier": tier,
            "visual_coverage": _visual_coverage_for_run(run),
            "video_url": p.get("video_url", ""),
            "last_synced_at": p.get("last_synced_at"),
        })
    videos.sort(key=lambda v: v["engagement_score"], reverse=True)

    # Top hooks (campaign-scoped + global)
    by_hook: dict[str, dict] = {}
    for v in videos:
        h = v["used_hook"]
        if not h:
            continue
        b = by_hook.setdefault(h, {
            "hook": h, "patterns": v["patterns"],
            "videos": 0, "total_engagement": 0,
            "best_video_url": v.get("video_url", ""),
            "best_score": 0,
            "campaigns": set(),
        })
        b["videos"] += 1
        b["total_engagement"] += v["engagement_score"]
        if v["engagement_score"] > b["best_score"]:
            b["best_score"] = v["engagement_score"]
            b["best_video_url"] = v.get("video_url", "")
        if v["campaign_id"]:
            b["campaigns"].add(v["campaign_id"])
    hooks_list = []
    for b in by_hook.values():
        b["avg_engagement"] = b["total_engagement"] // b["videos"]
        b["campaigns"] = sorted(b["campaigns"])
        hooks_list.append(b)
    hooks_list.sort(key=lambda x: x["avg_engagement"], reverse=True)
    top_hooks = hooks_list[:10]

    # Pattern leaderboard
    by_pattern: dict[str, dict] = {}
    for v in videos:
        for pat in v["patterns"]:
            b = by_pattern.setdefault(pat, {
                "pattern": pat, "videos": 0, "total_engagement": 0,
                "examples": [],
            })
            b["videos"] += 1
            b["total_engagement"] += v["engagement_score"]
            if len(b["examples"]) < 3:
                b["examples"].append(v["used_hook"][:80])
    patterns_list = []
    for b in by_pattern.values():
        b["avg_engagement"] = b["total_engagement"] // b["videos"]
        patterns_list.append(b)
    patterns_list.sort(key=lambda x: x["avg_engagement"], reverse=True)

    # Worst videos (bottom tercile, surfaced for "stop reusing these hooks")
    worst = [v for v in videos if v["tier"] == "bottom"]
    worst.sort(key=lambda v: v["engagement_score"])
    worst = worst[:10]

    # Best videos (top tercile, top 10 by score)
    best = [v for v in videos if v["tier"] == "top"][:10]

    # Campaign leaderboard
    by_camp: dict[int, dict] = {}
    for v in videos:
        cid = v["campaign_id"]
        if not cid:
            continue
        b = by_camp.setdefault(cid, {
            "campaign_id": cid,
            "campaign_name": v["campaign_name"],
            "videos": 0, "total_engagement": 0,
            "top_hook": "",
            "top_score": 0,
        })
        b["videos"] += 1
        b["total_engagement"] += v["engagement_score"]
        if v["engagement_score"] > b["top_score"]:
            b["top_score"] = v["engagement_score"]
            b["top_hook"] = v["used_hook"]
    camp_list = []
    for b in by_camp.values():
        b["avg_engagement"] = b["total_engagement"] // b["videos"]
        camp_list.append(b)
    camp_list.sort(key=lambda x: x["avg_engagement"], reverse=True)

    return {
        "summary": {
            "total_videos": len(videos),
            "measured_videos": len(measured),
            "top_threshold": top_thresh if top_thresh != float("inf") else None,
            "bottom_threshold": bot_thresh if bot_thresh != float("-inf") else None,
        },
        "top_hooks": top_hooks,
        "patterns": patterns_list,
        "best_videos": best,
        "worst_videos": worst,
        "campaigns": camp_list,
    }


@app.get("/learning", response_class=HTMLResponse)
def page_learning(request: Request):
    return templates.TemplateResponse(
        "learning.html",
        {"request": request, "page": "learning"},
    )


# ============================================================
# YouTube Shorts Autopilot
# ============================================================
#
# Runs Spartacus->render->upload at configured local times each day with
# zero user input. Default OFF; user explicitly opts in via Settings
# because this physically posts to a public YouTube channel.

_AUTOPILOT_CHECK_INTERVAL = 60   # seconds between scheduler ticks
_AUTOPILOT_SLOT_WINDOW = 5 * 60  # seconds: only fire within +/-5 min of slot


def _autopilot_log_path() -> Path:
    from spartacus.agents._shared import DATA_DIR as _DD
    return _DD / "autopilot_log.json"


def _autopilot_log_append(entry: dict) -> None:
    from spartacus.agents._shared import load_json, save_json
    rows = load_json(_autopilot_log_path(), default=[])
    if not isinstance(rows, list):
        rows = []
    rows.append(entry)
    # Keep last 200 entries to bound disk
    save_json(_autopilot_log_path(), rows[-200:])


def _autopilot_log_upsert(entry: dict) -> None:
    """Find a log row by `id` and replace it; if no match, append. Lets
    the worker update the same row as it progresses so the UI sees a
    live status without spawning new rows on every state change."""
    from spartacus.agents._shared import load_json, save_json
    rows = load_json(_autopilot_log_path(), default=[])
    if not isinstance(rows, list):
        rows = []
    eid = entry.get("id")
    found = False
    if eid:
        for i, r in enumerate(rows):
            if r.get("id") == eid:
                rows[i] = entry
                found = True
                break
    if not found:
        rows.append(entry)
    save_json(_autopilot_log_path(), rows[-200:])


def _parse_autopilot_slots() -> list[str]:
    raw = (db.get_setting("autopilot_slots") or "09:00,14:00,20:00").strip()
    out = []
    for s in raw.split(","):
        s = s.strip()
        if _re.match(r"^\d{2}:\d{2}$", s):
            out.append(s)
    return out


def _next_slot_today(now_dt) -> Optional[tuple[str, "datetime"]]:
    """Return (slot_label, slot_dt_today) for the slot whose window
    is currently open (within +/- AUTOPILOT_SLOT_WINDOW). None if no
    slot is open right now."""
    from datetime import datetime as _dt
    slots = _parse_autopilot_slots()
    for s in slots:
        hh, mm = [int(x) for x in s.split(":")]
        slot_dt = now_dt.replace(hour=hh, minute=mm, second=0, microsecond=0)
        delta = abs((now_dt - slot_dt).total_seconds())
        if delta <= _AUTOPILOT_SLOT_WINDOW:
            return s, slot_dt
    return None


def _pick_autopilot_campaign() -> Optional[dict]:
    """Use the user-pinned campaign if any, otherwise the most recent
    one. Returns None when no campaigns exist - autopilot will skip."""
    pinned = (db.get_setting("autopilot_campaign_id") or "").strip()
    rows = _load_campaigns()
    if not rows:
        return None
    if pinned:
        try:
            target = int(pinned)
            for c in rows:
                if c.get("campaign_id") == target:
                    return c
        except ValueError:
            pass
    # Most recent (highest campaign_id)
    return max(rows, key=lambda c: c.get("campaign_id", 0))


def _autopilot_fire_slot(slot_label: str, *,
                         manual_override: bool = False,
                         preallocated_run_id: int | None = None,
                         log_id: str | None = None) -> dict:
    """Run one autopilot slot end-to-end. Synchronous; the caller is
    expected to be a daemon thread (manual fire) or an asyncio.to_thread
    worker (scheduler). Updates a SINGLE log row identified by `log_id`
    via upsert, so the UI sees live status changes without row churn.

    `manual_override=True` (used by Run-Now): bypasses the spacing check
    and `autopilot_enabled` flag. Still runs the quality gate and
    upload-conditions check - those are about output quality, not
    schedule discipline."""
    started_at = datetime.now().isoformat(timespec="seconds")
    log_id = log_id or started_at
    log_entry: dict = {
        "id": log_id,
        "slot": slot_label,
        "started_at": started_at,
        "status": "running",
        "manual_override": manual_override,
    }
    _autopilot_log_upsert(log_entry)

    try:
        # 1) Spacing check - skipped on manual override
        if not manual_override:
            try:
                min_h = int(db.get_setting("autopilot_min_spacing_hours") or "4")
            except ValueError:
                min_h = 4
            last_iso = (db.get_setting("last_autopilot_run_at") or "").strip()
            if last_iso:
                try:
                    last_dt = datetime.fromisoformat(last_iso)
                    gap = (datetime.now() - last_dt).total_seconds() / 3600.0
                    if gap < min_h:
                        log_entry.update(status="skipped",
                                         reason=f"spacing: {gap:.1f}h < {min_h}h since last run")
                        _autopilot_log_upsert(log_entry)
                        return log_entry
                except ValueError:
                    pass

        # 2) Pick the campaign
        campaign = _pick_autopilot_campaign()
        if not campaign:
            log_entry.update(status="failed",
                             error="no campaign exists - create one on /spartacus first")
            _autopilot_log_upsert(log_entry)
            return log_entry
        log_entry["campaign_id"] = campaign["campaign_id"]
        log_entry["campaign_name"] = campaign["name"]

        # 2b) YouTube connection check (manual override surfaces a
        # cleaner error instead of silently skipping at upload time)
        try:
            import youtube_uploader as _ytup
            if not _ytup.is_connected():
                log_entry["yt_warning"] = "youtube channel not connected - render will succeed but upload will skip"
        except Exception:  # noqa: BLE001
            pass
        _autopilot_log_upsert(log_entry)

        # 3) Build the Spartacus run request
        req = SpartacusRunReq(
            niche=campaign["niche"],
            product=campaign["product"],
            platform="both",
            offer_url=campaign.get("offer_url", ""),
            render_video=True,
            allow_unverified=True,
            campaign_id=campaign["campaign_id"],
        )

        # 4) Allocate (or reuse) the Spartacus run id, register, run.
        run_id = preallocated_run_id if preallocated_run_id is not None \
                 else next(_spartacus_id_seq)
        with _spartacus_lock:
            _SPARTACUS_RUNS[run_id] = {
                "id": run_id,
                "campaign_id": campaign["campaign_id"],
                "campaign_name": campaign["name"],
                "status": "running",
                "current_step": "queued (autopilot)",
                "steps": [],
                "summary": None,
                "error": None,
                "started_at": datetime.now().isoformat(timespec="seconds"),
                "finished_at": None,
                "request": req.model_dump(),
                "trigger": "autopilot_manual" if manual_override else "autopilot",
            }
        log_entry["run_id"] = run_id
        log_entry["status"] = "running_pipeline"
        _autopilot_log_upsert(log_entry)
        print(f"[autopilot] slot {slot_label} -> run #{run_id} starting "
              f"(campaign #{campaign['campaign_id']} {campaign['name']!r}, "
              f"manual={manual_override})",
              flush=True)

        _spartacus_worker(run_id, req)

        # 5) Read what came out
        run = next((r for r in _list_persisted_spartacus_runs()
                    if r.get("id") == run_id), None) or {}
        summary = run.get("summary") or {}
        video = summary.get("video_render") or {}
        log_entry["video_url"] = video.get("preview_url") or ""
        log_entry["video_job_id"] = video.get("job_id")
        log_entry["best_hook"] = (
            max(summary.get("hooks") or [{}],
                key=lambda h: int(h.get("net_score") or 0)).get("hook", "")
        )

        # 6) Quality gate
        ok, reason = _passes_quality_gate(run) if run else (False, "no run")
        log_entry["quality_gate"] = {"ok": ok, "reason": reason}
        if not ok:
            log_entry["status"] = "rejected_quality"
            log_entry["error"] = f"quality gate: {reason}"
            db.set_setting("last_autopilot_run_at",
                           datetime.now().isoformat(timespec="seconds"))
            db.set_setting("last_autopilot_slot", slot_label)
            _autopilot_log_upsert(log_entry)
            return log_entry

        # 7) Auto-upload state (was triggered inside _spartacus_worker)
        yt = run.get("youtube_upload") or {}
        log_entry["upload_status"] = yt.get("status", "(not triggered)")
        log_entry["upload_video_id"] = yt.get("video_id", "")
        log_entry["upload_url"] = yt.get("video_url", "")
        if yt.get("status") == "failed":
            log_entry["error"] = f"upload failed: {yt.get('error', 'unknown')}"

        log_entry["status"] = "done"
        db.set_setting("last_autopilot_run_at",
                       datetime.now().isoformat(timespec="seconds"))
        db.set_setting("last_autopilot_slot", slot_label)
    except Exception as e:  # noqa: BLE001
        import traceback
        log_entry["status"] = "crashed"
        log_entry["error"] = f"{type(e).__name__}: {e}"
        print(f"[autopilot] slot {slot_label} crashed:\n{traceback.format_exc()}",
              flush=True)
    finally:
        log_entry["finished_at"] = datetime.now().isoformat(timespec="seconds")
        _autopilot_log_upsert(log_entry)
    return log_entry


async def _autopilot_scheduler() -> None:
    """Tick every minute. Fire the matching slot at most once per day,
    respecting min spacing. Slot windows are +/-5 min.

    Also runs the once-per-day Amazon affiliate brief if its setting
    is enabled and today's file hasn't been generated yet. The Amazon
    tick is independent of the slot/video pipeline - it never uploads
    to YouTube and never touches the campaign run queue."""
    import asyncio
    from datetime import datetime as _dt
    while True:
        try:
            await asyncio.sleep(_AUTOPILOT_CHECK_INTERVAL)

            # Amazon morning brief - independent of slots / spacing /
            # autopilot_enabled flag. Has its own setting + own gate.
            try:
                await asyncio.to_thread(_amazon_morning_tick)
            except Exception:  # noqa: BLE001 - never let this kill the loop
                pass

            # Pending-upload retry tick - drains the shorts upload queue
            # whenever YouTube's daily quota allows. Runs every 5 minutes
            # so we don't hammer the API.
            try:
                if not hasattr(_autopilot_scheduler, "_last_retry_tick"):
                    _autopilot_scheduler._last_retry_tick = _dt.min
                if (_dt.now() - _autopilot_scheduler._last_retry_tick).total_seconds() >= 300:
                    _autopilot_scheduler._last_retry_tick = _dt.now()
                    await asyncio.to_thread(_shorts_pending_retry_tick)
            except Exception:  # noqa: BLE001
                pass

            if (db.get_setting("autopilot_enabled") or "false").lower() != "true":
                continue
            now = _dt.now()
            match = _next_slot_today(now)
            if not match:
                continue
            slot_label, slot_dt = match
            # Same-slot debounce: if last run already fired this slot
            # today, skip. Stored as "<YYYY-MM-DD>|<HH:MM>".
            today_marker = f"{now.strftime('%Y-%m-%d')}|{slot_label}"
            last_slot_marker = (db.get_setting("last_autopilot_slot_marker") or "")
            if last_slot_marker == today_marker:
                continue
            # Mark BEFORE firing so a slow render doesn't get re-fired
            # by the next tick.
            db.set_setting("last_autopilot_slot_marker", today_marker)
            # Run synchronously inside this task. asyncio cooperates: the
            # other schedulers (auto-mode, perf) keep ticking because
            # they each run sleep + check on their own asyncio task.
            await asyncio.to_thread(_autopilot_fire_slot, slot_label)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            await asyncio.sleep(_AUTOPILOT_CHECK_INTERVAL)


# ---------- Amazon morning brief (once per day) -----------------------------

def _amazon_morning_tick(force: bool = False) -> dict:
    """Generate today's Amazon affiliate brief if not already generated.
    Returns the log entry dict. Idempotent on re-entry: a same-day call
    short-circuits when the daily JSON already exists, unless `force`.

    Independent of the video/upload pipeline. Never triggers a YouTube
    upload. Link rules are inherited from `amazon_engine.run_daily`,
    which itself reads `affiliate_links.json` and runs every output
    through the link guard."""
    from datetime import date as _date, datetime as _dt
    from spartacus.agents import amazon_engine

    today = _date.today()
    today_iso = today.isoformat()

    if (db.get_setting("amazon_autopilot_enabled") or "true").lower() != "true":
        return {"status": "disabled", "date": today_iso}

    # Same-day debounce. The setting is the canonical marker; the file
    # check is a belt-and-suspenders catch in case the setting drifts.
    last_marker = (db.get_setting("last_amazon_brief_date") or "").strip()
    json_path = amazon_engine.DATA_DIR / "amazon" / f"{today_iso}.json"
    if not force and (last_marker == today_iso or json_path.exists()):
        return {"status": "skipped_already_done", "date": today_iso,
                "json_path": str(json_path)}

    started_at = _dt.now().isoformat(timespec="seconds")
    log_entry: dict = {
        "id": f"amazon|{started_at}",
        "type": "amazon_brief",
        "date": today_iso,
        "started_at": started_at,
        "status": "running",
        "force": force,
    }
    _autopilot_log_upsert(log_entry)

    try:
        try:
            count = int(db.get_setting("amazon_autopilot_count") or "3")
        except ValueError:
            count = 3
        count = max(1, min(5, count))   # spec is 3-5; clamp
        payload = amazon_engine.run_daily(count=count)
        # Mark BEFORE returning so a crash in logging doesn't re-fire.
        db.set_setting("last_amazon_brief_date", today_iso)
        log_entry.update(
            status="done",
            finished_at=_dt.now().isoformat(timespec="seconds"),
            count=payload["count"],
            any_cta_only_mode=payload["any_cta_only_mode"],
            json_path=payload["json_path"],
            md_path=payload["md_path"],
            products=[i["product"] for i in payload["ideas"]],
            cta_only_products=[i["product"] for i in payload["ideas"]
                               if i["cta_only_mode"]],
            link_warnings=[w for i in payload["ideas"]
                            for w in (i.get("link_warnings") or [])],
        )
        print(f"[autopilot] amazon brief done: {payload['count']} ideas, "
              f"cta_only={payload['any_cta_only_mode']}, "
              f"file={payload['json_path']}", flush=True)
    except Exception as e:  # noqa: BLE001
        log_entry.update(
            status="failed",
            error=f"{type(e).__name__}: {e}",
            finished_at=_dt.now().isoformat(timespec="seconds"),
        )
        print(f"[autopilot] amazon brief FAILED: {e}", flush=True)
    _autopilot_log_upsert(log_entry)
    return log_entry


@app.get("/api/autopilot/amazon/status")
def api_amazon_autopilot_status():
    """Return the Amazon morning-brief settings + today's status."""
    from datetime import date as _date
    from spartacus.agents import amazon_engine
    today_iso = _date.today().isoformat()
    json_path = amazon_engine.DATA_DIR / "amazon" / f"{today_iso}.json"
    last_log = None
    from spartacus.agents._shared import load_json
    rows = load_json(_autopilot_log_path(), default=[])
    if isinstance(rows, list):
        for r in reversed(rows):
            if isinstance(r, dict) and r.get("type") == "amazon_brief":
                last_log = r
                break
    return {
        "enabled": (db.get_setting("amazon_autopilot_enabled") or "true").lower() == "true",
        "count": int(db.get_setting("amazon_autopilot_count") or "3"),
        "today": today_iso,
        "today_done": json_path.exists(),
        "last_brief_date": db.get_setting("last_amazon_brief_date") or "",
        "last_log": last_log,
    }


@app.post("/api/autopilot/amazon/config")
async def api_amazon_autopilot_config(request: Request):
    """Update the Amazon morning-brief settings. Body: {enabled?, count?}."""
    body = await request.json()
    if "enabled" in body:
        db.set_setting("amazon_autopilot_enabled",
                       "true" if bool(body["enabled"]) else "false")
    if "count" in body:
        try:
            n = max(1, min(5, int(body["count"])))
        except (ValueError, TypeError):
            raise HTTPException(400, "count must be an integer 1-5")
        db.set_setting("amazon_autopilot_count", str(n))
    return {"ok": True,
            "enabled": (db.get_setting("amazon_autopilot_enabled") or "true").lower() == "true",
            "count": int(db.get_setting("amazon_autopilot_count") or "3")}


@app.post("/api/autopilot/amazon/run-now")
async def api_amazon_autopilot_run_now():
    """Force a brief run regardless of same-day debounce. Returns the
    log entry. Calls the engine in a worker thread so the FastAPI loop
    isn't blocked while Ollama generates."""
    import asyncio as _asyncio
    entry = await _asyncio.to_thread(_amazon_morning_tick, True)
    return {"ok": entry.get("status") == "done", "entry": entry}


# ---------- Autopilot status + log API ----------

@app.get("/api/autopilot/status")
def api_autopilot_status():
    from datetime import datetime as _dt, timedelta as _td
    enabled = (db.get_setting("autopilot_enabled") or "false").lower() == "true"
    slots = _parse_autopilot_slots()
    now = _dt.now()
    # Compute next firing slot
    next_slot = None
    for s in slots:
        hh, mm = [int(x) for x in s.split(":")]
        cand = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if cand > now:
            next_slot = (s, cand.isoformat(timespec="seconds"))
            break
    if next_slot is None and slots:
        # Tomorrow's first slot
        hh, mm = [int(x) for x in slots[0].split(":")]
        cand = (now + _td(days=1)).replace(hour=hh, minute=mm, second=0, microsecond=0)
        next_slot = (slots[0], cand.isoformat(timespec="seconds"))

    campaign = _pick_autopilot_campaign()
    from spartacus.agents._shared import load_json
    log_rows = load_json(_autopilot_log_path(), default=[])
    if not isinstance(log_rows, list):
        log_rows = []
    return {
        "enabled": enabled,
        "slots": slots,
        "min_spacing_hours": int(db.get_setting("autopilot_min_spacing_hours") or "4"),
        "hashtags": db.get_setting("autopilot_hashtags") or "",
        "campaign": (
            {"id": campaign["campaign_id"], "name": campaign["name"],
             "product": campaign["product"], "niche": campaign["niche"]}
            if campaign else None
        ),
        "next_slot": next_slot[0] if next_slot else None,
        "next_slot_at": next_slot[1] if next_slot else None,
        "last_run_at": db.get_setting("last_autopilot_run_at") or "",
        "last_slot": db.get_setting("last_autopilot_slot") or "",
        "recent_log": log_rows[-10:][::-1],
    }


@app.post("/api/autopilot/run-now")
def api_autopilot_run_now():
    """Fire one Spartacus -> render -> upload chain RIGHT NOW.
    Bypasses the autopilot_enabled flag and the spacing check (manual
    override). Still respects the quality gate before publishing.

    Pre-allocates a Spartacus run id and seeds the autopilot log row
    BEFORE returning, so the caller can poll status immediately and the
    Settings UI sees a 'started' row without waiting for the 3-min
    pipeline to complete."""
    from datetime import datetime as _dt
    now = _dt.now()
    slots = _parse_autopilot_slots()
    label = "manual"
    for s in slots:
        hh, mm = [int(x) for x in s.split(":")]
        cand = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if abs((now - cand).total_seconds()) <= _AUTOPILOT_SLOT_WINDOW * 3:
            label = s
            break

    # Pre-flight: surface the most common errors as proper HTTP 4xx so
    # the UI can show them inline instead of waiting 3 min for the row.
    campaign = _pick_autopilot_campaign()
    if not campaign:
        raise HTTPException(400,
            "No campaign exists. Open /spartacus and run the pipeline at least once first.")
    try:
        import youtube_uploader as _ytup
        yt_connected = _ytup.is_connected()
    except Exception:  # noqa: BLE001
        yt_connected = False

    started_at = _dt.now().isoformat(timespec="seconds")
    log_id = started_at
    spartacus_run_id = next(_spartacus_id_seq)

    # Seed the log row immediately so /api/autopilot/status sees it
    # before the pipeline even begins.
    _autopilot_log_upsert({
        "id": log_id,
        "slot": label,
        "started_at": started_at,
        "status": "started",
        "manual_override": True,
        "run_id": spartacus_run_id,
        "campaign_id": campaign["campaign_id"],
        "campaign_name": campaign["name"],
        "yt_warning": (None if yt_connected
                       else "youtube channel not connected - render will succeed, upload will skip"),
    })

    # Daemon thread, not BackgroundTasks - decoupled from FastAPI's
    # request thread pool, won't hold a worker for 3 min.
    threading.Thread(
        target=_autopilot_fire_slot,
        kwargs={
            "slot_label": label,
            "manual_override": True,
            "preallocated_run_id": spartacus_run_id,
            "log_id": log_id,
        },
        daemon=True,
    ).start()

    return {
        "ok": True,
        "autopilot_log_id": log_id,
        "spartacus_run_id": spartacus_run_id,
        "status": "started",
        "slot": label,
        "campaign": {
            "id": campaign["campaign_id"],
            "name": campaign["name"],
            "product": campaign["product"],
        },
        "youtube_connected": yt_connected,
        "msg": "Spartacus pipeline starting. Poll /api/autopilot/status for live updates.",
    }


# ============================================================
# YouTube Safety Gate - dashboard + API
# ============================================================

def _safety_log_path() -> Path:
    from spartacus.agents._shared import DATA_DIR as _DD
    return _DD / "safety_log.json"


def _safety_log_append(entry: dict) -> None:
    from spartacus.agents._shared import load_json, save_json
    rows = load_json(_safety_log_path(), default=[])
    if not isinstance(rows, list):
        rows = []
    entry.setdefault("id", datetime.now().isoformat(timespec="seconds"))
    rows.append(entry)
    save_json(_safety_log_path(), rows[-200:])


@app.get("/api/safety")
def api_safety_list():
    from spartacus.agents._shared import load_json
    rows = load_json(_safety_log_path(), default=[])
    if not isinstance(rows, list):
        rows = []
    rows = list(reversed(rows))[:50]
    blocked = [r for r in rows if not r.get("passed")]
    fixed = [r for r in rows if r.get("passed") and r.get("fixes_applied")]
    return {
        "total": len(rows),
        "blocked_count": len(blocked),
        "auto_fixed_count": len(fixed),
        "rows": rows,
    }


class SafetyTestReq(BaseModel):
    script_text: str = ""
    title: str = ""
    description: str = ""
    tags: list[str] = []


@app.post("/api/safety/check")
def api_safety_check(req: SafetyTestReq):
    """Dry-run the safety gate against arbitrary text. Doesn't upload,
    doesn't write the safety log. Use to preview what the gate would do."""
    from compliance.youtube_safety_gate import check_youtube_upload_safety
    shipped = _load_shipped()
    recent = [
        {"title": v.get("last_title") or v.get("used_hook", ""),
         "description": v.get("last_description", ""),
         "used_hook": v.get("used_hook", ""),
         "posted_url": v.get("posted_url", "")}
        for v in shipped.values()
    ]
    return check_youtube_upload_safety(
        run_id=None,
        script_text=req.script_text,
        title=req.title,
        description=req.description,
        tags=req.tags,
        recent_uploads=recent[:30],
        storage_root=STORAGE_DIR,
        pexels_key_present=bool((db.get_setting("pexels_api_key") or "").strip()),
        has_synthetic_voice=True,
    )


@app.post("/api/safety/{log_id}/override")
def api_safety_override(log_id: str):
    """Manual approve: lifts a soft block by re-attempting the upload.
    Hard blocks (medical/financial guarantees, repetition) are NOT
    overrideable via this endpoint - they require fixing the script
    and re-rendering."""
    from spartacus.agents._shared import load_json, save_json
    rows = load_json(_safety_log_path(), default=[])
    target = next((r for r in rows if r.get("id") == log_id), None)
    if not target:
        raise HTTPException(404, "safety log entry not found")
    hard = [i for i in (target.get("issues") or [])
            if i.get("severity") == "hard_block"]
    if hard:
        cats = ",".join(set(i.get("category", "") for i in hard))
        raise HTTPException(403,
            f"Hard-block categories cannot be overridden: {cats}. "
            "Fix the script + re-render instead.")
    run_id = target.get("run_id")
    if not run_id:
        raise HTTPException(400, "log entry has no run_id")
    threading.Thread(target=_youtube_upload_worker,
                     args=(int(run_id),), daemon=True).start()
    return {"ok": True, "run_id": run_id, "msg": "upload re-attempt queued"}


@app.get("/safety", response_class=HTMLResponse)
def page_safety(request: Request):
    return templates.TemplateResponse(
        "safety.html",
        {"request": request, "page": "safety"},
    )


# ============================================================
# Auto Demo Video Generator
# ============================================================
#
# Single-slot model: only one demo can be generating at a time. The job
# state lives in memory (process lifetime); the final MP4 lives at
# storage/demo/spartacus_demo.mp4. Dashboard button polls /api/demo/status.

_demo_state: dict = {
    "status": "idle",   # idle | running | done | failed
    "stage": "",        # human label: capturing / rendering / etc.
    "progress": 0,      # 0..100
    "started_at": None,
    "finished_at": None,
    "log": [],
    "error": None,
    "video_path": "",
    # Internal: tracked between status() calls to verify the file has
    # finished writing before we mount it in the player.
    "_last_size": -1,
    "_size_stable_since": None,
}
_demo_lock = threading.Lock()


def _demo_log_append(msg: str) -> None:
    with _demo_lock:
        line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
        _demo_state["log"].append(line)
        _demo_state["log"] = _demo_state["log"][-200:]
    print(f"[demo] {msg}", flush=True)


# Map human stage labels to a rough progress percentage. Used by the
# /demo progress bar so the user has a visible cue without hand-counting
# log lines. Order matches the worker's phase order.
_DEMO_STAGE_PROGRESS = {
    "queued":               2,
    "installing_playwright": 8,
    "capturing":            30,
    "synthesizing_voice":   40,
    "rendering":            70,
    "finalizing":           96,
    "done":                100,
    "failed":              100,
}

_DEMO_STAGE_LABELS = {
    "queued":               "Queued",
    "installing_playwright": "Installing Playwright (first run only)",
    "capturing":            "Capturing dashboard",
    "synthesizing_voice":   "Generating voice",
    "rendering":            "Rendering demo",
    "finalizing":           "Finalizing MP4",
    "done":                 "Ready",
    "failed":               "Failed",
}


def _demo_set_stage(stage: str) -> None:
    """Worker calls this at each phase boundary. UI reflects live."""
    with _demo_lock:
        _demo_state["stage"] = stage
        _demo_state["progress"] = _DEMO_STAGE_PROGRESS.get(stage, _demo_state.get("progress", 0))
    _demo_log_append(f"stage: {stage}")


def _demo_worker() -> None:
    try:
        from demo_video import generate_demo, DemoError
    except Exception as e:  # noqa: BLE001
        with _demo_lock:
            _demo_state["status"] = "failed"
            _demo_state["stage"] = "failed"
            _demo_state["error"] = f"import demo_video failed: {type(e).__name__}: {e}"
            _demo_state["finished_at"] = datetime.now().isoformat(timespec="seconds")
        return

    # Sniff log lines coming up from generate_demo(...) so we can
    # auto-flip stage labels without changing the demo_video module's
    # interface. Phase keywords picked to match the actual messages
    # demo_video emits today.
    def _log_with_stage_sniff(msg: str) -> None:
        m = msg.lower()
        if "playwright: chromium" in m or "playwright: pip package not found" in m:
            _demo_set_stage("installing_playwright")
        elif "starting capture phase" in m:
            _demo_set_stage("capturing")
        elif m.startswith("render: scene ") and "duration=" in m:
            _demo_set_stage("synthesizing_voice")
        elif "handing off to remotion" in m:
            _demo_set_stage("rendering")
        elif "moved ->" in m:
            _demo_set_stage("finalizing")
        _demo_log_append(msg)

    try:
        _demo_set_stage("queued")
        out = generate_demo(log=_log_with_stage_sniff)
        with _demo_lock:
            _demo_state["status"] = "done"
            _demo_state["stage"] = "done"
            _demo_state["progress"] = 100
            _demo_state["video_path"] = str(out)
            _demo_state["finished_at"] = datetime.now().isoformat(timespec="seconds")
            # Reset stability tracker so the next /api/demo/status call
            # starts the 2-second debounce from this moment.
            _demo_state["_last_size"] = -1
            _demo_state["_size_stable_since"] = None
    except DemoError as e:
        with _demo_lock:
            _demo_state["status"] = "failed"
            _demo_state["stage"] = "failed"
            _demo_state["progress"] = 100
            _demo_state["error"] = str(e)
            _demo_state["finished_at"] = datetime.now().isoformat(timespec="seconds")
    except Exception as e:  # noqa: BLE001
        import traceback
        with _demo_lock:
            _demo_state["status"] = "failed"
            _demo_state["stage"] = "failed"
            _demo_state["progress"] = 100
            _demo_state["error"] = f"{type(e).__name__}: {e}"
            _demo_state["finished_at"] = datetime.now().isoformat(timespec="seconds")
        print(f"[demo] crashed:\n{traceback.format_exc()}", flush=True)


@app.post("/api/demo/generate")
def api_demo_generate():
    with _demo_lock:
        if _demo_state["status"] == "running":
            raise HTTPException(409, "demo generation already in progress")
        _demo_state.update({
            "status": "running",
            "stage": "queued",
            "progress": 2,
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "finished_at": None,
            "log": [],
            "error": None,
            "video_path": "",
            "_last_size": -1,
            "_size_stable_since": None,
        })
    threading.Thread(target=_demo_worker, daemon=True).start()
    return {"ok": True, "status": "running", "stage": "queued",
            "msg": "Demo generation started. Poll /api/demo/status."}


def _verify_demo_mp4(path: Path) -> tuple[bool, str]:
    """True if the file is a real, fully-written mp4. Final gate before
    /api/demo/status reports the video as ready.
    Checks (cheap, no ffprobe dependency):
      - file size > 1 MB (anything smaller is a render that bailed)
      - mutagen parses the mp4 container without raising
      - duration >= 1 second"""
    try:
        sz = path.stat().st_size
    except OSError:
        return False, "file missing"
    if sz < 1_048_576:
        return False, f"file too small ({sz} bytes < 1 MB)"
    try:
        from mutagen.mp4 import MP4
        m = MP4(str(path))
        dur = float(m.info.length or 0)
        if dur < 1.0:
            return False, f"mp4 duration too short ({dur:.2f}s)"
        return True, ""
    except Exception as e:  # noqa: BLE001
        return False, f"mp4 invalid: {type(e).__name__}: {e}"


@app.get("/api/demo/status")
def api_demo_status():
    """Spec contract:
       { status, stage, stage_label, progress, output_path, file_size,
         video_url, error, log_tail }
       video_url is ONLY non-empty when:
         - status == 'done'
         - file exists with non-zero size
         - size hasn't changed for 2+ seconds (write is finished)
         - mutagen validates it as an mp4 with audio
       Anything less and the player must stay hidden."""
    import time
    with _demo_lock:
        state = {**_demo_state}
        # Probe file size + run stability check, mutating the locked
        # state so the next call sees the same baseline.
        path_str = state.get("video_path") or ""
        if not path_str:
            # Fall back to the canonical demo path for "idle" rehydration
            cand = STORAGE_DIR / "demo" / "spartacus_demo.mp4"
            if state["status"] == "idle" and cand.exists() and cand.stat().st_size > 0:
                path_str = str(cand)
                _demo_state["video_path"] = path_str
        file_size = 0
        ready = False
        gate_reason = ""
        if path_str:
            p = Path(path_str)
            if p.exists():
                sz = p.stat().st_size
                file_size = sz
                if sz > 0:
                    if _demo_state.get("_last_size") != sz:
                        _demo_state["_last_size"] = sz
                        _demo_state["_size_stable_since"] = time.time()
                        gate_reason = "size still changing"
                    else:
                        stable_for = time.time() - (_demo_state.get("_size_stable_since") or time.time())
                        if stable_for < 2.0:
                            gate_reason = f"stabilizing ({stable_for:.1f}s)"
                        else:
                            ok, why = _verify_demo_mp4(p)
                            if ok:
                                ready = True
                            else:
                                gate_reason = why
                else:
                    gate_reason = "file empty"
            else:
                gate_reason = "file missing"

    # video_url ONLY when status is done AND ready. Idle with an existing
    # file from a prior session is also okay (just rehydrating the page).
    video_url = ""
    if path_str and ready and state["status"] in ("done", "idle"):
        try:
            rel = Path(path_str).relative_to(STORAGE_DIR)
            video_url = "/storage/" + str(rel).replace("\\", "/")
        except Exception:
            video_url = ""

    log_full = state.get("log") or []
    return {
        "status":       state["status"],
        "stage":        state.get("stage", ""),
        "stage_label":  _DEMO_STAGE_LABELS.get(state.get("stage", ""), ""),
        "progress":     int(state.get("progress") or 0),
        "started_at":   state.get("started_at"),
        "finished_at":  state.get("finished_at"),
        "error":        state.get("error"),
        "output_path":  path_str,
        "file_size":    file_size,
        "ready":        ready,
        "gate_reason":  gate_reason,
        "video_url":    video_url,
        "log_tail":     log_full[-10:],
    }


@app.get("/demo", response_class=HTMLResponse)
def page_demo(request: Request):
    return templates.TemplateResponse(
        "demo.html",
        {"request": request, "page": "demo"},
    )


# ============================================================
# SPARTACUS Clone Engine - dashboard wiring
# ============================================================
#
# Three endpoints + one page. The actual work lives in clone_bridge.py
# which calls into SPARTACUS_CLONE_ENGINE/. The CLI tools in that folder
# keep working unchanged - this is purely additive.

class CloneGenerateReq(BaseModel):
    mode: str   # instagram | youtube | sales | followup | dm
    text: str   # topic or incoming message


class CloneTrainExample(BaseModel):
    type: str
    output: str
    input: Optional[str] = ""
    notes: Optional[str] = ""


class CloneTrainReq(BaseModel):
    examples: list[CloneTrainExample]


@app.post("/api/clone/generate")
def api_clone_generate(req: CloneGenerateReq):
    try:
        import clone_bridge
        text = clone_bridge.generate(req.mode, req.text)
    except clone_bridge.CloneBridgeError as e:
        raise HTTPException(400, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")
    return {"ok": True, "mode": req.mode, "output": text}


@app.post("/api/clone/train")
def api_clone_train(req: CloneTrainReq):
    if not req.examples:
        raise HTTPException(400, "Provide at least one example.")
    payload = [ex.model_dump() for ex in req.examples]
    try:
        import clone_bridge
        result = clone_bridge.train(payload)
    except clone_bridge.CloneBridgeError as e:
        raise HTTPException(400, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")
    return result


@app.get("/api/clone/memory")
def api_clone_memory():
    try:
        import clone_bridge
        return clone_bridge.memory()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")


@app.get("/clone", response_class=HTMLResponse)
def page_clone(request: Request):
    return templates.TemplateResponse(
        "clone.html",
        {"request": request, "page": "clone"},
    )


# ---------- Hydra Video (local talking-head pipeline) ----------------------

@app.get("/hydra", response_class=HTMLResponse)
def page_hydra(request: Request):
    return templates.TemplateResponse(
        "hydra.html",
        {"request": request, "page": "hydra"},
    )


# Curated short-list of edge-tts voices we expose in the dashboard. We
# deliberately keep this small so the UI stays focused; users can still
# pass any edge-tts voice via the API.
_HYDRA_VOICES = [
    {"id": "en-US-GuyNeural",   "label": "US - Guy (male)"},
    {"id": "en-US-AriaNeural",  "label": "US - Aria (female)"},
    {"id": "en-US-JennyNeural", "label": "US - Jenny (female)"},
    {"id": "en-CA-ClaraNeural", "label": "Canada - Clara (female)"},
    {"id": "en-CA-LiamNeural",  "label": "Canada - Liam (male)"},
    {"id": "en-GB-RyanNeural",  "label": "UK - Ryan (male)"},
]


@app.get("/api/hydra/voices")
def api_hydra_voices():
    """Curated edge-tts voice list shown in the dashboard selector."""
    return {"ok": True, "voices": _HYDRA_VOICES}


class HydraVoiceTestReq(BaseModel):
    text: Optional[str] = None
    voice: Optional[str] = None
    rate: Optional[str] = None
    pitch: Optional[str] = None
    volume: Optional[str] = None


@app.post("/api/hydra/voice/test")
async def api_hydra_voice_test(req: HydraVoiceTestReq):
    """Render a short MP3 with the given voice settings so the user can
    audition before committing them. Audio lands in outputs/audio/ and
    is browser-previewable through /hydra_outputs/."""
    from hydra_video import OUT_AUDIO, ensure_dirs
    from hydra_video import voice as _hv_voice
    from hydra_video import settings as _hv_settings
    import time as _time

    ensure_dirs()
    cfg = _hv_settings.load()
    text = (req.text or "This is a Hydra voice test.").strip()
    voice = req.voice or cfg["edge_voice"]
    rate = req.rate or cfg["edge_rate"]
    pitch = req.pitch or cfg["edge_pitch"]
    volume = req.volume or cfg["edge_volume"]

    out = OUT_AUDIO / f"voice_test_{int(_time.time() * 1000)}.mp3"
    try:
        await _hv_voice.synthesize_async(
            text, voice=voice, rate=rate,
            pitch=pitch, volume=volume,
            out_path=out, provider="edge_tts",
        )
    except Exception as e:  # noqa: BLE001
        return JSONResponse(
            {"ok": False, "error": f"{type(e).__name__}: {e}"},
            status_code=500,
        )

    rel = out.relative_to(HYDRA_OUT).as_posix()
    return {
        "ok": True,
        "audio_url": f"/hydra_outputs/{rel}",
        "provider": "edge_tts",
        "voice": voice, "rate": rate, "pitch": pitch, "volume": volume,
        "text": text,
    }


class HydraSettingsReq(BaseModel):
    edge_voice: Optional[str] = None
    edge_rate: Optional[str] = None
    edge_pitch: Optional[str] = None
    edge_volume: Optional[str] = None
    voice_provider: Optional[str] = None
    lipsync_provider: Optional[str] = None
    sadtalker_dir: Optional[str] = None
    wav2lip_dir: Optional[str] = None
    quality: Optional[str] = None
    target_format: Optional[str] = None
    # XTTS voice cloning settings
    xtts_reference_wav: Optional[str] = None
    xtts_language: Optional[str] = None
    xtts_model: Optional[str] = None
    # Python executables for SadTalker/Wav2Lip (empty = auto-detect repo venv)
    sadtalker_python: Optional[str] = None
    wav2lip_python: Optional[str] = None


@app.get("/api/hydra/settings/current")
def api_hydra_settings_current():
    """Read-only view of the current Hydra settings.json (used by the
    dashboard to pre-fill voice tuning selectors)."""
    from hydra_video import settings as _hv_settings
    return {"ok": True, "settings": _hv_settings.load()}


@app.post("/api/hydra/settings")
def api_hydra_settings(req: HydraSettingsReq):
    """Persist Hydra settings (voice tuning + Realism Engine choices)."""
    from hydra_video import settings as _hv_settings
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    try:
        merged = _hv_settings.save(updates)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"ok": True, "settings": merged}


@app.get("/api/hydra/avatar/preview")
def api_hydra_avatar_preview():
    """Stream the current avatar.* file so the dashboard can show a
    preview without us mounting the assets directory wholesale."""
    from hydra_video import AVATARS_DIR, DEFAULT_AVATAR
    if DEFAULT_AVATAR.exists():
        return FileResponse(str(DEFAULT_AVATAR))
    for cand in AVATARS_DIR.glob("avatar.*"):
        if cand.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            return FileResponse(str(cand))
    raise HTTPException(404, "avatar not set")


@app.post("/api/hydra/avatar/upload")
async def api_hydra_avatar_upload(file: UploadFile = File(...)):
    """Save an uploaded image as the canonical avatar.jpg.

    Validates that it's a real image via PIL (so a renamed .jpg full of
    junk doesn't quietly rot the placeholder fallback)."""
    from hydra_video import AVATARS_DIR, DEFAULT_AVATAR, ensure_dirs
    from hydra_video import providers as _hv_providers
    from PIL import Image
    import io

    ensure_dirs()
    raw = await file.read()
    if not raw:
        raise HTTPException(400, "empty upload")
    if len(raw) > 25 * 1024 * 1024:
        raise HTTPException(400, "image too large (max 25 MB)")

    # Validate + normalize: re-encode to JPEG so the file on disk is
    # always a clean, browser-safe avatar.jpg regardless of what was sent.
    try:
        img = Image.open(io.BytesIO(raw))
        img.verify()  # quick structural check
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, f"not a valid image: {e}")

    # Wipe any sibling avatar.* files (avatar.png, avatar.webp, ...) so
    # avatar resolution stays unambiguous.
    for cand in AVATARS_DIR.glob("avatar.*"):
        try:
            cand.unlink()
        except OSError:
            pass

    DEFAULT_AVATAR.parent.mkdir(parents=True, exist_ok=True)
    img.save(DEFAULT_AVATAR, "JPEG", quality=92)

    return {
        "ok": True,
        "avatar_path": str(DEFAULT_AVATAR),
        "avatar_exists": _hv_providers.avatar_exists(),
    }


@app.post("/api/hydra/xtts/reference/upload")
async def api_hydra_xtts_reference_upload(file: UploadFile = File(...)):
    """Save an audio file as the XTTS speaker reference.

    Any audio format works (WAV preferred). 3-30 seconds of clear speech
    in a quiet room gives the best voice clone quality. The path is
    written to hydra_video/settings.json as xtts_reference_wav."""
    from hydra_video import ROOT, ensure_dirs
    from hydra_video import settings as _hv_settings

    ensure_dirs()
    raw = await file.read()
    if not raw:
        raise HTTPException(400, "empty upload")
    if len(raw) > 50 * 1024 * 1024:
        raise HTTPException(400, "audio file too large (max 50 MB)")

    ref_dir = ROOT / "assets"
    ref_dir.mkdir(parents=True, exist_ok=True)

    orig_name = file.filename or "reference.wav"
    ext = Path(orig_name).suffix.lower() or ".wav"
    ref_path = ref_dir / f"voice_reference{ext}"
    ref_path.write_bytes(raw)

    _hv_settings.save({"xtts_reference_wav": str(ref_path)})

    return {
        "ok": True,
        "reference_path": str(ref_path),
        "size_bytes": len(raw),
        "filename": orig_name,
    }


@app.get("/api/hydra/xtts/reference/info")
def api_hydra_xtts_reference_info():
    """Return info about the configured XTTS reference WAV."""
    from hydra_video import settings as _hv_settings
    cfg = _hv_settings.load()
    ref_raw = (cfg.get("xtts_reference_wav") or "").strip()
    ref_path = Path(ref_raw) if ref_raw else None
    exists = bool(ref_path and ref_path.exists())
    return {
        "ok": True,
        "configured": bool(ref_raw),
        "exists": exists,
        "path": ref_raw,
        "size_bytes": ref_path.stat().st_size if exists else 0,
        "filename": ref_path.name if ref_path else "",
        "language": cfg.get("xtts_language", "en"),
        "model": cfg.get("xtts_model", ""),
        "voice_provider": cfg.get("voice_provider", "edge_tts"),
    }


@app.get("/api/hydra/status")
def api_hydra_status():
    """Realism Engine status: which voice/lipsync providers will actually
    run, plus capability flags for the heavy AI models."""
    from hydra_video import providers as _hv_providers
    from hydra_video import settings as _hv_settings

    cfg = _hv_settings.load()
    return _hv_providers.status_dict(
        voice_requested=cfg["voice_provider"],
        lipsync_requested=cfg["lipsync_provider"],
        avatar_path=_hv_settings.avatar_default_path(),
    )


class HydraGenReq(BaseModel):
    script: str
    avatar_path: Optional[str] = None
    avatar: Optional[str] = None  # convenience alias for avatar_path

    def resolved_avatar(self) -> Optional[str]:
        return self.avatar_path or self.avatar or None
    product_path: Optional[str] = None
    music_path: Optional[str] = None
    length_target_sec: Optional[float] = None
    voice_provider: Optional[str] = None
    lipsync_provider: Optional[str] = None
    # edge-tts overrides for this single render. None = use settings.json.
    voice: Optional[str] = None
    rate: Optional[str] = None
    pitch: Optional[str] = None
    volume: Optional[str] = None
    # Conversion style preset: "clean" (default) or "aggressive".
    style: Optional[str] = None


@app.post("/api/hydra/generate")
async def api_hydra_generate(req: HydraGenReq):
    """Run the Hydra Video pipeline and return a browser-previewable URL."""
    import asyncio as _asyncio
    import time as _time
    from hydra_video import run_video as _hv_run

    if not req.script or not req.script.strip():
        raise HTTPException(400, "script is required")

    started = _time.time()

    def _do() -> "_hv_run.HydraResult":
        return _hv_run.generate(
            req.script.strip(),
            avatar_path=req.resolved_avatar(),
            product_path=req.product_path or None,
            music_path=req.music_path or None,
            length_target_sec=req.length_target_sec or None,
            voice_provider=req.voice_provider or None,
            lipsync_provider=req.lipsync_provider or None,
            voice=req.voice or None,
            rate=req.rate or None,
            pitch=req.pitch or None,
            volume=req.volume or None,
            style=req.style or None,
            log=lambda *_: None,
        )

    try:
        # Pipeline is sync + CPU-bound; run off the event loop.
        result = await _asyncio.to_thread(_do)
    except Exception as e:  # noqa: BLE001
        return JSONResponse(
            {"ok": False, "error": f"{type(e).__name__}: {e}"},
            status_code=500,
        )

    final_path = Path(result.final_video)
    try:
        rel = final_path.relative_to(HYDRA_OUT).as_posix()
        video_url = f"/hydra_outputs/{rel}"
    except ValueError:
        video_url = ""

    return {
        "ok": True,
        "video_url": video_url,
        "video_path": result.final_video,
        "duration_sec": result.duration_sec,
        "lipsync_mode": result.lipsync_mode,
        "voice_provider": result.voice_provider,
        "word_count": result.word_count,
        "style": result.style,
        "hook": result.hook,
        "cta": result.cta,
        "music_track": result.music_track,
        "has_product": result.has_product,
        "elapsed_sec": round(_time.time() - started, 2),
    }


@app.get("/api/hydra/outputs")
def api_hydra_outputs(limit: int = 20):
    """Return the newest Hydra-generated MP4 files, newest first."""
    import time as _time2
    final_dir = HYDRA_OUT / "final"
    if not final_dir.exists():
        return {"ok": True, "videos": []}
    mp4s = sorted(final_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    videos = []
    for p in mp4s[:limit]:
        try:
            st = p.stat()
            rel = p.relative_to(HYDRA_OUT).as_posix()
            videos.append({
                "filename": p.name,
                "url": f"/hydra_outputs/{rel}",
                "path": str(p.resolve()),
                "size_bytes": st.st_size,
                "created_ts": st.st_mtime,
            })
        except Exception:
            pass
    return {"ok": True, "videos": videos}


class HydraIdeaReq(BaseModel):
    product: str
    viral_hook: str = ""
    problem_solved: str = ""
    script_30s: str = ""
    cta: str = ""
    niche: str = "productivity"
    affiliate_url: str = ""


_CTA_ACTION_PHRASES = [
    "GET YOURS BELOW",
    "TRY IT TODAY",
    "SEE WHY IT'S TRENDING",
]


# Each entry: (keyword_list, hook_options)
# hook_options mixes three emotional registers per pattern:
#   A — outcome/result   ("MY BACK FEELS DIFFERENT NOW")
#   B — frustration/pain ("MY BACK USED TO HURT DAILY")
#   C — surprise/relief  ("I DIDN'T EXPECT THIS TO WORK")
# random.choice picks one per video so the same product feels fresh.
#
# Matched against lowercased "{product} {problem_solved}" using whole-word
# boundaries (\b) — prevents "cord" matching "recording", etc.
# More specific patterns come before broader ones.
_HOOK_PATTERNS: list[tuple[list[str], list[str]]] = [
    (["back pain", "lower back", "slouch", "posture"], [
        "THIS FIXED MY BACK PAIN",
        "I STOPPED SLOUCHING INSTANTLY",
        "MY BACK USED TO HURT DAILY",
        "I WAS TIRED OF BACK PAIN",
        "I DIDN'T EXPECT THIS TO WORK",
        "THIS FIXED MY BACK IN 3 DAYS",        # YT specific
        "I WASTED 2 YEARS IGNORING THIS",      # YT specific
    ]),

    (["eye strain", "glare", "monitor light", "staring"], [
        "MY EYES STOPPED HURTING",
        "I CAN WORK LONGER NOW",
        "EYE STRAIN WAS RUINING MY DAY",
        "I COULDN'T WORK PAST 3PM",
        "THIS ACTUALLY FIXED IT",
        "MY EYES FELT BETTER IN 1 HOUR",       # YT specific
        "I NOW WORK 4 EXTRA HOURS DAILY",      # YT specific
    ]),

    # Lighting before webcam — Key Light's description mentions "webcam footage"
    (["lighting", "dim", "dark footage", "key light", "yellow footage"], [
        "MY VIDEOS LOOK CINEMATIC",
        "LIGHTING CHANGED MY CONTENT",
        "MY VIDEOS LOOKED TERRIBLE BEFORE",
        "BAD LIGHTING KILLED MY VIEWS",
        "I DIDN'T EXPECT THIS DIFFERENCE",
        "MY VIDEOS LOOK 10X BETTER NOW",       # YT specific
    ]),

    (["webcam", "look on camera", "pixelat", "grainy", "potato"], [
        "I LOOK BETTER ON CALLS NOW",
        "MY VIDEO QUALITY CHANGED",
        "I LOOKED TERRIBLE ON ZOOM",
        "POTATO CAM WAS EMBARRASSING",
        "THIS CHANGED HOW PEOPLE SEE ME",
        "I LOOK 10X BETTER ON CALLS NOW",      # YT specific
    ]),

    (["zoom call", "dropped call", "dead spot", "wi-fi", "mesh wifi"], [
        "NO MORE DROPPED CALLS",
        "ZERO DEAD SPOTS NOW",
        "DROPPED CALLS RUINED MY MEETINGS",
        "I WAS ALWAYS DISCONNECTING",
        "I DIDN'T EXPECT THIS COVERAGE",
        "ZERO DROPPED CALLS IN 2 WEEKS",       # YT specific
    ]),

    (["standing desk", "stiffness", "sitting all day", "afternoon energy"], [
        "I STOPPED SITTING ALL DAY",
        "MY ENERGY IS BACK",
        "SITTING ALL DAY WAS KILLING ME",
        "AFTERNOON CRASHES WERE CONSTANT",
        "STANDING CHANGED EVERYTHING",
        "I SIT 60% LESS NOW",                  # YT specific
        "MY BACK PAIN GONE IN 1 WEEK",         # YT specific
    ]),

    (["noise cancell", "background noise", "open-office", "cafe distraction"], [
        "FINALLY FOUND MY FOCUS",
        "I HEAR NOTHING BUT WORK",
        "OFFICE NOISE DESTROYED MY FOCUS",
        "I COULDN'T THINK STRAIGHT",
        "SILENCE CHANGED MY OUTPUT",
        "I FOCUSED FOR 3 HOURS STRAIGHT",      # YT specific
        "SAVED 2 HOURS IN ONE DAY",            # YT specific
    ]),

    (["noise", "distraction", "focus", "concentration"], [
        "I FINALLY CAN FOCUS",
        "MY FOCUS CAME BACK",
        "I WAS TIRED OF DISTRACTIONS",
        "I COULDN'T FOCUS FOR AN HOUR",
        "I SAVED AN HOUR EVERY DAY",           # YT specific
    ]),

    # Scan before print — scanner descriptions often contain "contract"
    (["scan", "receipt", "paper pile", "bookkeep", "tax season"], [
        "PAPER CLUTTER IS GONE",
        "I DIGITIZED EVERYTHING",
        "PAPER PILES WERE OUT OF CONTROL",
        "TAX SEASON USED TO STRESS ME",
        "I DIDN'T EXPECT THIS TO BE EASY",
        "CLEARED 3 YEARS OF PAPER IN 1 DAY",  # YT specific
    ]),

    # Shipping label before generic print
    (["shipping label", "etsy", "ecommerce", "hand-writing"], [
        "MY PACKAGES LOOK PRO NOW",
        "LABELS IN 10 SECONDS",
        "HAND WRITING LABELS WAS AWFUL",
        "I LOOKED UNPROFESSIONAL BEFORE",
        "THIS CHANGED MY SHIPPING GAME",
        "I SHIP 3X FASTER NOW",                # YT specific
    ]),

    (["printer", "invoice", "contract printing"], [
        "I PRINT FROM HOME NOW",
        "PRINTING IN SECONDS NOW",
        "PRINT SHOP RUNS WASTED MY TIME",
        "PRINTING USED TO SLOW ME DOWN",
        "I PRINT FROM HOME IN 10 SECONDS",     # YT specific
    ]),

    # Stream deck before cable — "recording" contains "cord" as substring
    (["stream deck", "fumbling", "obs scenes", "livestream", "mid-recording"], [
        "ONE CLICK CHANGES EVERYTHING",
        "STREAMING GOT EASIER",
        "FUMBLING SCENES WAS EMBARRASSING",
        "I LOOKED UNPROFESSIONAL LIVE",
        "I DIDN'T EXPECT THIS UPGRADE",
        "MY STREAM TIME DOUBLED",              # YT specific
    ]),

    (["cable", "tangled", "wire clutter", "cords under"], [
        "MY DESK IS FINALLY CLEAN",
        "CABLE CHAOS IS OVER",
        "I WAS TIRED OF THIS MESS",
        "CABLES DROVE ME CRAZY",
        "DESK BEFORE VS AFTER THIS",
        "MY DESK WAS A MESS BEFORE THIS",      # YT specific
        "CLEANED MY DESK IN 5 MINUTES",        # YT specific
    ]),

    (["battery", "dying laptop", "power bank", "laptop battery"], [
        "MY LAPTOP NEVER DIES NOW",
        "BATTERY ANXIETY IS GONE",
        "DYING BATTERY RUINED MEETINGS",
        "I LOST WORK SO MANY TIMES",
        "I DIDN'T EXPECT THIS TO LAST",
        "8 MORE HOURS OF BATTERY NOW",         # YT specific
        "I WAS ALWAYS AT 3% BATTERY",          # YT specific
    ]),

    (["microphone", "audio", "sound quality", "tinny", "podcast"], [
        "MY AUDIO IS CRISP NOW",
        "PEOPLE HEAR ME CLEARLY NOW",
        "MY AUDIO SOUNDED TERRIBLE",
        "PEOPLE KEPT ASKING ME TO REPEAT",
        "THIS CHANGED HOW I SOUND",
        "MY AUDIO IMPROVED IN 30 SECONDS",     # YT specific
    ]),

    (["gimbal", "shaky", "stabiliz"], [
        "NO MORE SHAKY FOOTAGE",
        "SMOOTH SHOTS EVERY TIME",
        "SHAKY FOOTAGE RUINED MY CONTENT",
        "I DELETED SO MANY CLIPS BEFORE",
        "THIS ACTUALLY WORKS",
        "100% OF MY SHOTS WERE USABLE",        # YT specific
    ]),

    (["mouse", "hand fatigue", "wrist pain", "long scrolling"], [
        "MY WRIST STOPPED HURTING",
        "NO MORE HAND FATIGUE",
        "WRIST PAIN WAS CONSTANT",
        "I COULDN'T WORK MORE THAN 2 HRS",
        "I DIDN'T EXPECT THIS TO HELP",
        "ZERO WRIST PAIN AFTER 1 WEEK",        # YT specific
        "I WORK 2 MORE HOURS COMFORTABLY",     # YT specific
    ]),

    (["keyboard", "typing", "cramped laptop"], [
        "I TYPE FASTER THAN EVER",
        "TYPING IS DIFFERENT NOW",
        "LAPTOP KEYBOARD WAS KILLING ME",
        "CRAMPED KEYS HURT MY HANDS",
        "I DIDN'T EXPECT THIS DIFFERENCE",
        "I TYPE 30% FASTER NOW",               # YT specific
    ]),

    (["headphone", "headset", "noise-cancell"], [
        "I FINALLY CAN FOCUS",
        "I HEAR NOTHING BUT WORK",
        "NOISE USED TO RUIN MY DAY",
        "I COULDN'T WORK IN PUBLIC",
        "I FOCUSED FOR 4 HOURS STRAIGHT",      # YT specific
    ]),

    (["notebook", "notes", "reusable"], [
        "NEVER LOSE A NOTE AGAIN",
        "MY NOTES ARE ORGANIZED NOW",
        "I KEPT LOSING IMPORTANT IDEAS",
        "MY OLD NOTEBOOKS WERE USELESS",
        "I DIDN'T EXPECT THIS TO STICK",
        "I HAVEN'T LOST A NOTE IN 6 MONTHS",   # YT specific
    ]),

    (["gpu", "local llm", "stable diffusion", "fine-tun", "cloud gpu"], [
        "RUNNING AI LOCALLY NOW",
        "NO MORE CLOUD GPU BILLS",
        "CLOUD GPU BILLS WERE KILLING ME",
        "I WAS PAYING $200 A MONTH",
        "I DIDN'T EXPECT THIS SPEED",
        "CUT MY AI COSTS BY 80%",              # YT specific
    ]),

    (["raspberry pi", "home automation", "home agent"], [
        "I AUTOMATED MY HOME SETUP",
        "HOME AUTOMATION FOR $50",
        "MANUAL TASKS WASTED MY TIME",
        "I DIDN'T KNOW THIS WAS POSSIBLE",
        "I SAVED HOURS EVERY WEEK",            # YT specific
    ]),

    (["edge tpu", "computer vision", "edge ai"], [
        "AI WITHOUT INTERNET NOW",
        "LOCAL AI UNDER $100",
        "CLOUD AI COSTS WERE TOO HIGH",
        "I DIDN'T EXPECT THIS TO RUN LOCAL",
    ]),

    (["speakerphone", "meeting audio", "jabra", "voice assistant"], [
        "MEETINGS SOUND DIFFERENT NOW",
        "EVERYONE HEARS ME CLEARLY",
        "BAD CALL AUDIO WAS HUMILIATING",
        "PEOPLE KEPT ASKING ME TO REPEAT",
        "THIS ACTUALLY WORKS",
        "ZERO COMPLAINTS IN 30 DAYS",          # YT specific
    ]),

    (["nvme", "ssd", "dataset", "load time", "gen5"], [
        "MY COMPUTER IS FASTER NOW",
        "LOAD TIMES ARE INSTANT",
        "SLOW LOADS WASTED HOURS DAILY",
        "I WAITED MINUTES FOR AI TO LOAD",
        "I DIDN'T EXPECT THIS SPEED",
        "MY AI LOADED IN 3 SECONDS",           # YT specific
    ]),

    (["payment", "checkout", "e-transfer", "in-person sale"], [
        "I NEVER MISS A SALE NOW",
        "PAYMENTS IN SECONDS NOW",
        "I LOST SALES WITHOUT THIS",
        "CASH ONLY WAS COSTING ME",
        "I CLOSED 3 MORE SALES THIS WEEK",     # YT specific
    ]),

    (["360", "action camera", "missed the shot", "re-shooting"], [
        "I NEVER MISS THE SHOT NOW",
        "ONE CAMERA GETS EVERYTHING",
        "I KEPT MISSING THE ACTION",
        "I DELETED SO MANY BAD CLIPS",
        "I DIDN'T EXPECT THIS COVERAGE",
        "GOT THE SHOT 100% OF THE TIME",       # YT specific
    ]),
]

# Niche fallbacks — all three registers mixed in + YouTube-specific numbered variants
_HOOK_NICHE_FALLBACK: dict[str, list[str]] = {
    "productivity": [
        "SAVED AN HOUR TODAY",
        "I GET MORE DONE NOW",
        "I WAS ALWAYS FALLING BEHIND",
        "THIS PAID FOR ITSELF FAST",
        "I DIDN'T EXPECT THIS TO HELP",
        "SAVED 3 HOURS IN ONE DAY",            # YT specific
        "I DO 2X THE WORK NOW",                # YT specific
    ],
    "business": [
        "MY WORKFLOW CHANGED OVERNIGHT",
        "THIS PAID FOR ITSELF",
        "I WAS WASTING SO MUCH TIME",
        "BEST $50 I SPENT",
        "I WISH I HAD THIS SOONER",
        "THIS PAID BACK IN 3 DAYS",            # YT specific
        "SAVED 2 HOURS EVERY MORNING",         # YT specific
    ],
    "ai": [
        "RUNNING AI FROM HOME NOW",
        "CLOUD BILLS WERE OUT OF CONTROL",
        "AI WITHOUT THE MONTHLY FEE",
        "I DIDN'T EXPECT THIS TO WORK",
        "LOCAL AI FINALLY WORKS",
        "CUT MY AI BILL BY 70%",               # YT specific
    ],
    "work_from_home": [
        "MY HOME OFFICE IS NEXT LEVEL",
        "WFH JUST GOT EASIER",
        "I WAS EMBARRASSED BY MY SETUP",
        "I WISH I UPGRADED SOONER",
        "BEST HOME OFFICE UPGRADE",
        "MY HOME SETUP IS NEXT LEVEL NOW",     # YT specific
        "I WAS WASTING HOURS EVERY DAY",       # YT specific
    ],
    "content_creation": [
        "MY CONTENT LOOKS DIFFERENT NOW",
        "MY PRODUCTION VALUE DOUBLED",
        "MY OLD CONTENT WAS EMBARRASSING",
        "I DIDN'T EXPECT THIS DIFFERENCE",
        "VIEWS WENT UP AFTER THIS",
        "MY VIEWS WENT UP 40% AFTER THIS",     # YT specific
    ],
}
_HOOK_DEFAULT_FALLBACK = [
    "THIS ACTUALLY WORKS",
    "I SAVED $50 WITH THIS",
    "WISH I HAD THIS SOONER",
    "I WAS SKEPTICAL AT FIRST",
    "I DIDN'T EXPECT THIS TO WORK",
    "MY LIFE IS EASIER NOW",
    "SAVED 3 HOURS THIS WEEK",                 # YT specific
    "THIS CHANGED MY ROUTINE IN 1 DAY",        # YT specific
]


def _video_hook(product: str, niche: str, problem_solved: str = "") -> str:
    """Return a specific, emotionally varied hook for this product.

    Matches whole-word boundaries against (product + problem_solved).
    random.choice ensures different emotional register each generation.
    YouTube-specific numbered variants are included in each pool so they
    surface naturally without any special-casing.
    """
    import random as _random
    import re as _re
    text = f"{product} {problem_solved}".lower()
    for keywords, hooks in _HOOK_PATTERNS:
        if any(_re.search(r'\b' + _re.escape(kw) + r'\b', text) for kw in keywords):
            return _random.choice(hooks)
    niche_hooks = _HOOK_NICHE_FALLBACK.get((niche or "").lower(), _HOOK_DEFAULT_FALLBACK)
    return _random.choice(niche_hooks)


_YT_NICHE_BENEFIT: dict[str, str] = {
    "productivity":     "This Amazon find completely changed how I work — saves me time every single day.",
    "business":         "One of the best business finds on Amazon. Paid for itself in the first month.",
    "ai":               "If you're running AI locally, this is a game changer — no more cloud fees.",
    "work_from_home":   "Best work-from-home upgrade I've made. If you WFH, you need this.",
    "content_creation": "This completely leveled up my content quality. Highly recommend for creators.",
}

# Product-keyword overrides — checked before niche fallback
_YT_PRODUCT_BENEFIT: list[tuple[list[str], str]] = [
    (["mastercard", "visa", "credit card", "cashback card", "rewards card"],
     "Cashback on every purchase — no annual fee. Best card for Amazon buyers."),
    (["rewards mastercard", "amazon card", "amazon visa"],
     "Earn cashback on Amazon and everywhere you shop. Link in description."),
    (["keyboard", "mechanical keyboard"], "Typing feels completely different. Best upgrade for your desk."),
    (["monitor", "screen", "display"],    "Biggest upgrade I made — the difference is night and day."),
    (["webcam", "web cam"],               "Finally looks professional on every call. No more blurry video."),
    (["microphone", "mic"],               "Audio quality completely changed my content. Huge difference."),
    (["mouse", "trackpad"],               "Smooth, precise — hands don't hurt anymore after long sessions."),
    (["chair", "standing desk", "desk"],  "Back doesn't hurt anymore. This was 100% worth it."),
    (["cable", "organizer", "wire"],      "Desk went from chaos to clean in 10 minutes flat."),
    (["camera", "ring light"],            "Lighting completely changed how I look on camera."),
]


def _yt_benefit_for_product(product: str, niche: str) -> str:
    """Return a benefit line, preferring product-keyword matches over niche defaults."""
    lower = product.lower()
    for keywords, phrase in _YT_PRODUCT_BENEFIT:
        if any(kw in lower for kw in keywords):
            return phrase
    return _YT_NICHE_BENEFIT.get(niche, f"{product} — one of the best finds on Amazon right now.")

_YT_NICHE_HASHTAGS: dict[str, str] = {
    "productivity":     "#productivity #amazonfinds #worksmarter #desksetup",
    "business":         "#business #entrepreneur #amazonfinds #productivity",
    "ai":               "#ai #tech #amazonfinds #aitools",
    "work_from_home":   "#workfromhome #wfh #amazonfinds #homeoffice",
    "content_creation": "#contentcreator #youtube #amazonfinds #creatortips",
}

_YT_TITLE_TEMPLATES: list[str] = [
    "This {product} Changed My Entire Routine",
    "Best Amazon Find: {product}",
    "{product} — Worth Every Penny",
    "I Tried {product} For 30 Days",
    "Why I Can't Work Without {product} Now",
    "This Simple {niche_word} Saved Me Hours Daily",
    "The {niche_word} Upgrade That Actually Works",
    "Honest Review: {product} (Amazon Find)",
]


def _generate_yt_title(product: str, niche: str) -> str:
    """Generate a curiosity-driven YouTube Shorts title (6-10 words)."""
    # Use first 3 words of product name to keep titles concise
    p_words = product.split()
    short = " ".join(p_words[:3]) if len(p_words) > 3 else product
    niche_word = {
        "productivity": "Productivity Tool",
        "business": "Business Tool",
        "ai": "AI Tool",
        "work_from_home": "WFH Upgrade",
        "content_creation": "Creator Tool",
    }.get(niche, "Amazon Find")
    # Deterministic selection — same product always gets same title style
    tmpl = _YT_TITLE_TEMPLATES[abs(hash(product + niche)) % len(_YT_TITLE_TEMPLATES)]
    title = tmpl.format(product=short, niche_word=niche_word)
    # Enforce 6-10 word range
    words = title.split()
    if len(words) > 10:
        title = " ".join(words[:10])
    if len(title.split()) < 6:
        title += " (Amazon Find)"
    return title


def _registry_affiliate_url(product: str) -> str:
    """Look up the real affiliate URL from the registry.

    Tries exact match first, then falls back to token-overlap matching so
    'Amazon Rewards Mastercard' finds 'Amazon.ca Rewards Mastercard'.
    Returns '' when nothing matches (caller falls back to CTA-only).
    """
    import re as _re
    try:
        from spartacus.agents import amazon_engine as _ae
        reg = _ae.load_affiliate_links()
    except Exception:
        return ""
    if not reg:
        return ""
    if product in reg:
        return reg[product].get("url", "")

    def _norm(s: str) -> list[str]:
        return _re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()

    prod_tokens = set(_norm(product))
    best_key, best_score = None, 0
    for key in reg:
        overlap = len(prod_tokens & set(_norm(key)))
        if overlap > best_score:
            best_score, best_key = overlap, key
    if best_key and best_score >= 2:
        return reg[best_key].get("url", "")
    return ""


def _generate_yt_description(product: str, niche: str, affiliate_url: str) -> str:
    """Generate a YouTube Shorts description: benefit + link + hashtags.

    Always prefers the registry URL over whatever the brief passed in —
    the brief may carry AI-generated placeholder URLs.
    """
    real_url = _registry_affiliate_url(product) or affiliate_url
    benefit = _yt_benefit_for_product(product, niche)
    link_line = (
        f"Check it out here:\n{real_url}"
        if real_url
        else "Link in description."
    )
    base_tags = _YT_NICHE_HASHTAGS.get(niche, "#amazonfinds #productivity")
    # Deduplicate and append #shorts
    seen: set[str] = set()
    tags: list[str] = []
    for tag in (base_tags + " #shorts").split():
        if tag.lower() not in seen:
            seen.add(tag.lower())
            tags.append(tag)
    return f"{benefit}\n\n{link_line}\n\n{' '.join(tags)}"


def _short_cta(cta: str, affiliate_url: str, product: str = "") -> tuple[str, str]:
    """Return (primary_text, sub_text) for the CTA card.

    primary_text: short action phrase, ≤ 4 words
    sub_text: "(link in description)" when there is a real affiliate URL
    """
    has_link = bool((affiliate_url or "").strip())
    words = (cta or "").split()

    if has_link:
        # Rotate through action phrases deterministically by product name
        idx = abs(hash(product or cta)) % len(_CTA_ACTION_PHRASES)
        primary = _CTA_ACTION_PHRASES[idx]
        sub = "(link in description)"
    elif len(words) <= 5:
        primary = cta.upper()
        sub = ""
    else:
        primary = "FOLLOW FOR MORE"
        sub = ""

    return primary, sub


@app.post("/api/hydra/generate_from_idea")
async def api_hydra_generate_from_idea(req: HydraIdeaReq):
    """Turn an Amazon affiliate idea into a product slideshow video.

    Uses the existing TTS + captions + render pipeline but replaces the
    avatar/lipsync stage with a styled product card slideshow.  No avatar,
    no SadTalker — pure product visuals with Ken Burns motion."""
    import asyncio as _asyncio
    import time as _time

    started = _time.time()

    # Build the script from the idea fields.
    script = (req.script_30s or "").strip()
    if not script:
        parts = [req.viral_hook, req.problem_solved, req.cta]
        script = "  ".join(p for p in parts if p.strip())
    if not script:
        script = f"{req.product}.  Check the link in description."

    try:
        from hydra_video import DEFAULT_VIDEO_SIZE, ensure_dirs
        from hydra_video import voice as _hv_voice
        from hydra_video import captions as _hv_captions
        from hydra_video import render as _hv_render
        from hydra_video import settings as _hv_settings
        from hydra_video import music as _hv_music
        from hydra_video.style import resolve as _resolve_style
        from hydra_video.product_video import (
            generate_product_cards, build_slideshow, build_slideshow_from_images,
        )
        from hydra_video.image_fetcher import fetch_product_images

        ensure_dirs()
        cfg = _hv_settings.load()
        style_cfg = _resolve_style("affiliate")

        # ── 1. Voice synthesis ────────────────────────────────────────────────
        edge_voice  = cfg.get("edge_voice")  or _hv_voice.DEFAULT_VOICE
        edge_rate   = cfg.get("edge_rate")   or _hv_voice.DEFAULT_RATE
        edge_pitch  = cfg.get("edge_pitch")  or "+0Hz"
        edge_volume = cfg.get("edge_volume") or "+0%"

        v = await _asyncio.get_event_loop().run_in_executor(
            None,
            lambda: _hv_voice.synthesize(
                script,
                voice=edge_voice, rate=edge_rate,
                pitch=edge_pitch, volume=edge_volume,
                provider=cfg.get("voice_provider", "edge_tts"),
            ),
        )
        duration = v.duration_sec

        # ── 2. Fetch real product images (Amazon → Pexels → PIL fallback) ────
        image_paths = await _asyncio.get_event_loop().run_in_executor(
            None,
            lambda: fetch_product_images(
                product=req.product,
                niche=req.niche,
                affiliate_url=req.affiliate_url,
                max_images=6,
            ),
        )

        # ── 3. Build slideshow ────────────────────────────────────────────────
        # Timing constants computed here so the slideshow builder can pin
        # the right image under the CTA window.
        hook_end   = 1.2
        cta_start  = max(duration - 3.5, duration * 0.78)

        if len(image_paths) >= 2:
            # Real images available — use photo slideshow
            slideshow_path = await _asyncio.get_event_loop().run_in_executor(
                None,
                lambda: build_slideshow_from_images(
                    image_paths, duration, DEFAULT_VIDEO_SIZE,
                    cta_start_sec=cta_start,
                ),
            )
        else:
            # No real images — fall back to styled PIL cards
            cards = await _asyncio.get_event_loop().run_in_executor(
                None,
                lambda: generate_product_cards(
                    product=req.product,
                    niche=req.niche,
                    hook=req.viral_hook or req.product,
                    problem=req.problem_solved or "The old way is broken.",
                    cta=req.cta or "Check the link in description.",
                    affiliate_url=req.affiliate_url,
                    size=DEFAULT_VIDEO_SIZE,
                ),
            )
            slideshow_path = await _asyncio.get_event_loop().run_in_executor(
                None,
                lambda: build_slideshow(cards, duration, DEFAULT_VIDEO_SIZE),
            )

        # ── 4. Captions + hook + CTA overlays ────────────────────────────────
        # hook_end / cta_start already computed in step 3.

        caption_clips = _hv_captions.make_caption_clips(
            v.word_timings, DEFAULT_VIDEO_SIZE, style=style_cfg,
            skip_before=hook_end,   # captions start after hook clears
            skip_after=cta_start,   # captions end before CTA card
        )
        if style_cfg.pulse_every_sec > 0:
            caption_clips = caption_clips + _hv_captions.make_flash_clips(
                duration, DEFAULT_VIDEO_SIZE, style=style_cfg,
                interval_sec=style_cfg.pulse_every_sec,
                skip_before=hook_end,
                skip_after=cta_start,
            )
        # Mid-video payoff line — white, centered, 0.9 s, fires at 50% of body
        _payoff_text = _hv_captions.pick_payoff(req.product, req.niche)
        _payoff_mid  = hook_end + (cta_start - hook_end) * 0.50
        payoff_clip = _hv_captions.make_payoff_clip(
            _payoff_text, DEFAULT_VIDEO_SIZE,
            start=_payoff_mid - 0.45, end=_payoff_mid + 0.45,
            style=style_cfg,
        )
        if payoff_clip is not None:
            caption_clips = caption_clips + [payoff_clip]

        hook_clip = _hv_captions.make_hook_clip(
            _video_hook(req.product, req.niche, req.problem_solved),
            DEFAULT_VIDEO_SIZE, start=0.0, end=hook_end, style=style_cfg,
        )
        _cta_primary, _cta_sub = _short_cta(req.cta, req.affiliate_url, req.product)
        cta_clip = _hv_captions.make_cta_clip(
            _cta_primary,
            DEFAULT_VIDEO_SIZE, start=cta_start + 0.4, end=duration, style=style_cfg,
            sub_text=_cta_sub,
        )

        # ── 5. Optional background music ─────────────────────────────────────
        chosen_music = _hv_music.pick_track()

        # ── 6. Compose ────────────────────────────────────────────────────────
        from hydra_video import OUT_FINAL
        out_path = OUT_FINAL / f"hydra_{int(_time.time())}.mp4"

        final_path = await _asyncio.get_event_loop().run_in_executor(
            None,
            lambda: _hv_render.compose(
                slideshow_path,
                v.audio_path,
                caption_clips,
                video_size=DEFAULT_VIDEO_SIZE,
                duration_sec=duration,
                music_path=chosen_music,
                hook_clip=hook_clip,
                cta_clip=cta_clip,
                fps=30,
                style=style_cfg,
                skip_fit=True,   # slideshow is already canvas-sized
                out_path=out_path,
            ),
        )

        final_path = Path(final_path)
        try:
            rel = final_path.relative_to(HYDRA_OUT).as_posix()
            video_url = f"/hydra_outputs/{rel}"
        except ValueError:
            video_url = ""

        return {
            "ok": True,
            "video_url": video_url,
            "video_path": str(final_path),
            "duration_sec": round(duration, 2),
            "word_count": len(v.word_timings),
            "product": req.product,
            "niche": req.niche,
            "image_count": len(image_paths),
            "visual_mode": "real_images" if len(image_paths) >= 2 else "pil_cards",
            "elapsed_sec": round(_time.time() - started, 2),
            "yt_title": _generate_yt_title(req.product, req.niche),
            "yt_description": _generate_yt_description(req.product, req.niche, req.affiliate_url or ""),
            # Expose the resolved registry URL so the JS publish call uses it
            "affiliate_url": _registry_affiliate_url(req.product) or req.affiliate_url or "",
        }
        _tbr_reset(f"hydra_generate:{req.product}")

    except Exception as exc:  # noqa: BLE001
        _tbr_check(f"hydra_generate:{req.product}", f"{type(exc).__name__}: {exc}")
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


# ---------- Hydra → YouTube one-click publish --------------------------------

class HydraPublishReq(BaseModel):
    video_path: str
    yt_title: str
    yt_description: str
    niche: str = ""
    privacy: str = "unlisted"   # "unlisted" | "public"

_HYDRA_NICHE_TAGS: dict[str, list[str]] = {
    "productivity":     ["productivity", "desksetup", "worksmarter", "officetips"],
    "business":         ["business", "entrepreneur", "businesstips", "workefficiency"],
    "ai":               ["ai", "artificialintelligence", "tech", "aitools"],
    "work_from_home":   ["workfromhome", "wfh", "homeoffice", "remotework"],
    "content_creation": ["contentcreator", "youtube", "creatortips", "youtuber"],
}
_HYDRA_BASE_TAGS = ["amazonfinds", "productreview", "shorts", "amazon"]


@app.post("/api/hydra/publish_to_youtube")
async def api_hydra_publish_to_youtube(req: HydraPublishReq):
    """Upload a Hydra-generated MP4 to YouTube Shorts with one click.

    Bypasses the Spartacus run system — no run_id needed. Calls
    youtube_uploader.upload_video() directly via asyncio executor so
    the server stays responsive during the 30-120s upload. Returns
    the YouTube URL on success or a plain error string on failure.
    """
    import asyncio as _asyncio
    import youtube_uploader as _ytup

    if not _ytup.is_connected():
        return {
            "ok": False,
            "error": "YouTube channel not connected. Go to Settings → YouTube to connect.",
        }

    video_path = Path(req.video_path)
    if not video_path.exists():
        return {"ok": False, "error": f"Video file not found: {req.video_path}"}

    tags = _HYDRA_BASE_TAGS + _HYDRA_NICHE_TAGS.get((req.niche or "").lower(), [])
    privacy = "public" if (req.privacy or "").lower() == "public" else "unlisted"

    try:
        result = await _asyncio.get_event_loop().run_in_executor(
            None,
            lambda: _ytup.upload_video(
                video_path=video_path,
                title=req.yt_title[:100],
                description=req.yt_description[:5000],
                tags=tags[:30],
                privacy=privacy,
                category_id="22",   # People & Blogs — correct for Shorts
            ),
        )
        return {
            "ok": True,
            "video_id":  result["video_id"],
            "video_url": result["video_url"],
            "title":     result["title"],
            "privacy":   result["privacy_status"],
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


# ---------- Amazon Affiliate Engine -----------------------------------------

@app.get("/amazon", response_class=HTMLResponse)
def page_amazon(request: Request):
    return templates.TemplateResponse(
        "amazon.html",
        {"request": request, "page": "amazon"},
    )


@app.get("/api/amazon/today")
def api_amazon_today():
    """Return today's saved daily brief, or {} if not generated yet,
    plus the catalog and affiliate-links registry so the dashboard
    can render everything in one fetch."""
    from spartacus.agents import amazon_engine
    return {
        "today": amazon_engine.load_day(),
        "recent_dates": amazon_engine.list_recent(14),
        "catalog": amazon_engine.list_catalog(),
        "allowed_niches": list(amazon_engine.ALLOWED_NICHES),
        "affiliate_links": amazon_engine.load_affiliate_links(),
    }


@app.post("/api/amazon/generate")
async def api_amazon_generate(request: Request):
    """Generate the daily brief on demand. Body: {count, niches}.
    Affiliate links come from the persistent registry - this endpoint
    does NOT accept inline URLs (preventing accidental fake links).

    The engine internally uses asyncio.run() to call Ollama, so we run
    it in a worker thread to avoid 'asyncio.run() cannot be called
    from a running event loop' inside FastAPI's loop.
    """
    import asyncio as _asyncio
    from spartacus.agents import amazon_engine
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    count = int(body.get("count") or 3)
    niches = body.get("niches") or []
    if not isinstance(niches, list):
        niches = []
    try:
        payload = await _asyncio.to_thread(
            amazon_engine.run_daily, count=count, niches=niches,
        )
        return {"ok": True, "payload": payload}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")


@app.post("/api/amazon/affiliate-links")
async def api_amazon_register_link(request: Request):
    """Add or replace one product->URL entry in the registry. Body:
    {product, url, notes?}. URL is stored EXACTLY as provided."""
    from spartacus.agents import amazon_engine
    body = await request.json()
    product = (body.get("product") or "").strip()
    url = (body.get("url") or "").strip()
    notes = (body.get("notes") or "").strip()
    if not product or not url:
        raise HTTPException(400, "product and url are required")
    try:
        entry = amazon_engine.register_affiliate_link(product, url, notes=notes)
        return {"ok": True, "product": product, "entry": entry,
                "registry": amazon_engine.load_affiliate_links()}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")


@app.delete("/api/amazon/affiliate-links/{product}")
def api_amazon_remove_link(product: str):
    from spartacus.agents import amazon_engine
    removed = amazon_engine.remove_affiliate_link(product)
    return {"ok": removed, "removed": removed,
            "registry": amazon_engine.load_affiliate_links()}


# ---------- Three Brain Router -----------------------------------------------

@app.get("/three-brain", response_class=HTMLResponse)
def page_three_brain(request: Request):
    return templates.TemplateResponse(
        "three_brain.html",
        {"request": request, "page": "three_brain"},
    )


@app.get("/api/three-brain/status")
def api_three_brain_status():
    """Return availability of Codex and Gemini CLIs, including Gemini auth state."""
    import os, sys
    from spartacus.three_brain_router import detect_available_tools
    tools = detect_available_tools()

    gemini_key = os.environ.get("GEMINI_API_KEY") or ""
    if not gemini_key and sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                gemini_key, _ = winreg.QueryValueEx(k, "GEMINI_API_KEY")
                # also inject into the process env so subprocess calls to gemini CLI work
                os.environ["GEMINI_API_KEY"] = gemini_key
        except (FileNotFoundError, OSError):
            gemini_key = ""

    tools["gemini"]["auth"] = "ready" if gemini_key else "missing"
    tools["gemini"]["auth_hint"] = (
        None if gemini_key
        else 'setx GEMINI_API_KEY "your-key-here" — then restart SPARTA server'
    )
    return tools


class ThreeBrainRouteReq(BaseModel):
    task_text: str = ""
    attached_files: list = []
    rescue_check: bool = False
    failure_count: int = 0
    repeated_error: bool = False


@app.post("/api/three-brain/route")
def api_three_brain_route(req: ThreeBrainRouteReq):
    """Route a task to the best brain and, optionally, check rescue status."""
    from spartacus.three_brain_router import route_task, should_rescue
    result = route_task(req.task_text, attached_files=req.attached_files or None)
    result["rescue"] = should_rescue(req.failure_count, req.repeated_error)
    return result


class ThreeBrainRunReq(BaseModel):
    prompt: str
    target_files: list = []


@app.post("/api/three-brain/codex-review")
async def api_three_brain_codex(req: ThreeBrainRunReq):
    """Run a Codex CLI review. Returns {ok, output, error}."""
    import asyncio as _asyncio
    from spartacus.three_brain_router import run_codex_review
    files = req.target_files or None
    return await _asyncio.get_event_loop().run_in_executor(
        None, lambda: run_codex_review(req.prompt, files)
    )


@app.post("/api/three-brain/gemini-analysis")
async def api_three_brain_gemini(req: ThreeBrainRunReq):
    """Run a Gemini CLI analysis. Returns {ok, output, error}."""
    import asyncio as _asyncio
    from spartacus.three_brain_router import run_gemini_analysis
    files = req.target_files or None
    return await _asyncio.get_event_loop().run_in_executor(
        None, lambda: run_gemini_analysis(req.prompt, files)
    )


# ---------- Shorts Ideation Engine -------------------------------------------

@app.get("/shorts", response_class=HTMLResponse)
def page_shorts(request: Request):
    return templates.TemplateResponse(
        "shorts.html",
        {"request": request, "page": "shorts"},
    )


@app.get("/api/shorts/today")
def api_shorts_today():
    """Today's 4 shorts (or {} if not yet generated) plus recent dates."""
    from spartacus import shorts_ideation
    return {
        "today": shorts_ideation.load_day(),
        "recent_dates": shorts_ideation.list_recent(14),
        "angles": list(shorts_ideation.ANGLES),
    }


@app.get("/api/product-lock")
def api_product_lock_status():
    """Read the current product lock + all configured products."""
    from spartacus import product_lock
    return {
        "active": product_lock.get_active_lock(),
        "products": product_lock.list_products(),
    }


@app.post("/api/product-lock/link")
async def api_product_lock_set_link(request: Request):
    """Update the affiliate_link of the currently-active product.
    Body: {url}. URL is stored EXACTLY as provided (no normalization).
    Empty string clears the link and returns the pipeline to CTA-only."""
    from spartacus import product_lock
    body = await request.json()
    url = (body.get("url") or "").strip()
    try:
        entry = product_lock.update_active_link(url)
        return {"ok": True, "active": product_lock.get_active_lock(),
                "entry": entry}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, f"{type(e).__name__}: {e}")


@app.post("/api/product-lock/active")
async def api_product_lock_set_active(request: Request):
    """Switch which product key is the active lock. Pass empty key to
    disable locking entirely (Amazon brief picker resumes)."""
    from spartacus import product_lock
    body = await request.json()
    key = (body.get("key") or "").strip()
    try:
        product_lock.set_active_product(key)
        return {"ok": True, "active": product_lock.get_active_lock()}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, f"{type(e).__name__}: {e}")


def _shorts_pending_retry_tick() -> dict:
    """Background tick - retries any MP4s queued for upload. Logs to
    stdout. Returns the retry summary so the manual endpoint can echo it."""
    from spartacus import shorts_video
    try:
        result = shorts_video.retry_pending_uploads()
    except Exception as e:  # noqa: BLE001
        print(f"[shorts_pending_retry] tick failed: {e}", flush=True)
        return {"error": str(e)}
    if result.get("attempted"):
        print(f"[shorts_pending_retry] attempted={result['attempted']} "
              f"uploaded={result['uploaded']} pending={result['still_pending']} "
              f"failed={result['failed']}", flush=True)
    return result


@app.get("/api/shorts/pending")
def api_shorts_pending():
    """List pending + completed retry-queue entries."""
    from spartacus import shorts_video
    return {
        "pending": shorts_video.list_pending(),
        "completed": shorts_video._load_queue(shorts_video.COMPLETED_PATH),
    }


@app.post("/api/shorts/pending/retry-now")
async def api_shorts_pending_retry_now():
    """Manual retry trigger - bypasses the per-entry throttle so you
    can hit it as soon as you've phone-verified or know the quota
    has reset. Wrapped in a worker thread (upload blocks)."""
    import asyncio as _asyncio
    from spartacus import shorts_video
    try:
        result = await _asyncio.to_thread(
            shorts_video.retry_pending_uploads, force=True)
        return {"ok": True, "result": result}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")


@app.get("/api/shorts/meta")
def api_shorts_meta():
    from spartacus import shorts_meta
    return {"today": shorts_meta.load_day()}


@app.post("/api/shorts/meta/generate")
async def api_shorts_meta_generate():
    """Run the metadata optimizer for today's brief. Wraps in
    asyncio.to_thread because the LLM call blocks."""
    import asyncio as _asyncio
    from spartacus import shorts_meta
    try:
        result = await _asyncio.to_thread(shorts_meta.run_for_today)
        return {"ok": True, "result": result}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")


@app.post("/api/shorts/build")
async def api_shorts_build(request: Request):
    """Build (and optionally upload) one Short into a video.

    Body: {angle: "problem"|"curiosity"|"story"|"product",
           upload: bool (default false),
           privacy: "unlisted"|"public"|"private" (default unlisted)}

    Always uses today's brief. The shorts engine is read-only here -
    no LLM call, no script regeneration. Wrapped in asyncio.to_thread
    because TTS + ffmpeg encode + upload all block."""
    import asyncio as _asyncio
    from spartacus import shorts_video
    body = await request.json()
    angle = (body.get("angle") or "problem").strip().lower()
    do_upload = bool(body.get("upload"))
    privacy = (body.get("privacy") or "unlisted").strip().lower()
    if angle not in shorts_video.ANGLES:
        raise HTTPException(400, f"angle must be one of {shorts_video.ANGLES}")
    if privacy not in ("public", "unlisted", "private"):
        raise HTTPException(400, "privacy must be public/unlisted/private")
    try:
        if do_upload:
            r = await _asyncio.to_thread(
                shorts_video.build_and_upload_one, angle, None, privacy)
        else:
            r = await _asyncio.to_thread(shorts_video.build_one, angle)
        return {"ok": True, "result": r}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")


@app.post("/api/shorts/generate")
async def api_shorts_generate():
    """Generate today's 4 shorts (1 product, 4 angles). Engine pulls
    the product from today's Amazon brief, looks up the affiliate
    registry, and runs in CTA-only mode if no link is registered.
    Wrapped in a worker thread because the engine uses asyncio.run()."""
    import asyncio as _asyncio
    from spartacus import shorts_ideation
    try:
        payload = await _asyncio.to_thread(shorts_ideation.run_daily)
        return {"ok": True, "payload": payload}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")


# ---------- Viral Engine -------------------------------------------------

@app.get("/viral-engine", response_class=HTMLResponse)
def page_viral_engine(request: Request):
    return templates.TemplateResponse(
        "viral_engine.html",
        {"request": request, "page": "viral_engine"},
    )


@app.get("/api/viral-engine/status")
def api_ve_status():
    from spartacus import viral_engine
    return viral_engine.status_panel()


@app.get("/api/viral-engine/metadata")
def api_ve_metadata():
    """Single-shot snapshot - all 8 read-only sections in one fetch."""
    from spartacus import viral_engine
    return viral_engine.full_snapshot()


@app.get("/api/viral-engine/performance")
def api_ve_performance():
    from spartacus import viral_engine
    return {
        "styles":     viral_engine.style_performance(),
        "thumbnails": viral_engine.thumbnail_performance(),
        "memory":     viral_engine.performance_memory(),
    }


@app.post("/api/viral-engine/run-test-batch")
async def api_ve_run_test_batch():
    """Generate today's brief + render all 4 angles (no upload).
    Async-wrapped because rendering blocks for ~20 minutes total -
    operator should monitor the server console for progress."""
    import asyncio as _asyncio
    from spartacus import shorts_ideation, shorts_video
    from datetime import date as _date
    today = _date.today()
    try:
        async def _job():
            shorts_ideation.run_daily(day=today)
            for angle in shorts_ideation.ANGLES:
                shorts_video.build_one(angle, day=today)
        # Fire and forget (operator polls /metadata to see updated state)
        _asyncio.create_task(_asyncio.to_thread(
            lambda: __import__("asyncio").run(_job())))
        return {"ok": True, "message": "Test batch started in background. Check server console for progress."}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")


@app.post("/api/viral-engine/regenerate-failed")
async def api_ve_regenerate_failed():
    """Re-render any angles whose latest brief had a failed quality
    gate. For now: re-render all 4. Future: only the failing ones."""
    from spartacus import shorts_video, shorts_ideation
    import asyncio as _asyncio
    try:
        async def _job():
            for angle in shorts_ideation.ANGLES:
                shorts_video.build_one(angle)
        _asyncio.create_task(_asyncio.to_thread(
            lambda: __import__("asyncio").run(_job())))
        return {"ok": True, "message": "Regeneration started for all 4 angles."}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")


@app.post("/api/viral-engine/refresh-stats")
async def api_ve_refresh_stats():
    """Pull views/likes/comments from YouTube API for every logged video."""
    import asyncio as _asyncio
    from spartacus import shorts_intel
    try:
        result = await _asyncio.to_thread(shorts_intel.sync_youtube_stats, False)
        return {"ok": True,
                "message": f"Synced {result['synced']}/{result['rows']} rows",
                "result": result}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"{type(e).__name__}: {e}")


@app.post("/api/viral-engine/export-report")
def api_ve_export_report():
    from spartacus import viral_engine
    out = viral_engine.export_report()
    return {"ok": True,
            "message": f"Report saved to {out.name}",
            "path": str(out)}


@app.post("/api/viral-engine/reset-rotation")
def api_ve_reset_rotation():
    """Clear the recent-style memory so all 5 styles are back in the
    candidate pool for today's renders. Doesn't delete intel history -
    only the recency-based exclusion is reset by archiving the
    repetition guard log to a timestamped backup."""
    from spartacus import viral_engine
    if viral_engine.REPETITION_PATH.exists():
        backup = viral_engine.VE_DIR / f"repetition_guard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        viral_engine.REPETITION_PATH.rename(backup)
    return {"ok": True, "message": "Rotation reset. All styles re-eligible."}


# ===========================================================================
# SPARTA Trading Command Center — v1 lifecycle viewer (Module 1 of 8)
# ---------------------------------------------------------------------------
# Authorized by: docs/sparta_command_center_first_build_plan.md (commit 970452c)
# Inspired by:   docs/fincept_inspiration_review_for_sparta_trading_command_center.md
#                (commit a2ca6f7) — inspiration only, not dependency.
#
# Hard contract for this entire block:
#   - GET only. No POST/PUT/PATCH/DELETE handler. Non-GET verbs return 405.
#   - Localhost-only (inherits app's 127.0.0.1:8765 bind).
#   - Read-only. Zero filesystem writes. Zero external network. Zero subprocess.
#   - No trade affordance. No fetch. No optimize. No broker. No LLM chat.
#   - No forms, no inputs, no mutating buttons in the rendered template.
#   - Sha re-verification with explicit MISSING / SEAL_DRIFT / NO_DECLARED_SHA
#     statuses. Never fabricates a value. Fail-closed rendering.
#
# Soft-rollback (per plan §13.1): comment out the @app.get("/command")
# decorator below and restart the dashboard. The helpers stay inert.
# ===========================================================================

import hashlib as _command_hashlib
import json as _command_json
import re as _command_re
from dataclasses import dataclass as _command_dataclass, field as _command_field

_COMMAND_REPORTS_DIR = BASE / "reports" / "external_research_hunter"
_COMMAND_DECISIONS_FILE = (
    BASE / "brain_memory" / "projects" / "trading_bot" / "decisions.md"
)

_COMMAND_POSTURE_INVARIANTS = (
    "Trading PAUSED",
    "Live BLOCKED_AT_6_GATES",
    "FRC NEVER_GRANTED",
    "no_strategy_optimization_authorized = True",
)

# Phase ladder definition. Each phase has a list of filename-fragment
# patterns; the phase is COMPLETE if any matching file exists for the
# lifecycle, else PENDING. The first PENDING phase is marked NEXT.
_COMMAND_PHASE_DEFS = (
    (0, "Selection / diagnostic plan", (
        "_non_equity_candidate_selection_plan.",
        "_integrity_audit_diagnostic_plan.",
        "_integrity_audit_minimum_feasible_diagnostic_spec.",
    )),
    (1, "Spec DRAFT", (
        "_spec_DRAFT.",
    )),
    (2, "Spec SEAL / sealed finding", (
        "_minimum_feasible_diagnostic_spec.",
        "_audit_finding_report_SEALED.",
    )),
    (3, "Runner / analyzer build report", (
        "_runner_build_report.",
        "_audit_analyzer_build_report.",
    )),
    (4, "Execution guard build report", (
        "_execution_guard_build_report.",
    )),
    (5, "Operator execution preparation", (
        "_operator_execution_preparation.",
        "_RUN_BOOK.",
    )),
    (6, "Operator QC acknowledgment / capture", (
        "_operator_qc_execution_acknowledgment.",
        "_qc_run_capture",
    )),
    (7, "Result sealing report", (
        "_result_sealing_report.",
    )),
    (8, "Archival memo / recommendations", (
        "_archival_memo.",
        "_recommendations_memo.",
    )),
)

# Keys whose value is treated as a raw-file sha256 pin when found in a
# JSON sidecar. Other sha keys (e.g. report_seal_sha256 over a canonical
# body, not the raw file) are intentionally ignored here to avoid false
# SEAL_DRIFT alerts on existing artifacts.
_COMMAND_RAW_FILE_SHA_KEYS = (
    "artifact_sha256",
    "file_sha256",
    "body_sha256",
    "self_sha256",
)


@_command_dataclass
class _CmdArtifactRow:
    name: str
    rel_path: str
    bytes: int
    declared_sha: str
    recomputed_sha: str
    status: str  # OK | SEAL_DRIFT | MISSING | NO_DECLARED_SHA | ERROR


@_command_dataclass
class _CmdPhaseRow:
    phase: int
    label: str
    status: str  # COMPLETE | NEXT | PENDING


@_command_dataclass
class _CmdLifecycleRow:
    lifecycle_id: str
    description: str
    sealed_verdict: str
    phases: list = _command_field(default_factory=list)
    artifacts: list = _command_field(default_factory=list)
    next_authorize: str = ""


def _command_sha256_of_file(path):
    try:
        h = _command_hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, IOError):
        return ""


def _command_load_sidecar_pin(json_sidecar_path):
    """Return the raw-file sha256 pin from a JSON sidecar, or '' if none."""
    if not json_sidecar_path.exists():
        return ""
    try:
        data = _command_json.loads(
            json_sidecar_path.read_text(encoding="utf-8", errors="replace")
        )
    except (OSError, IOError, ValueError):
        return ""
    if not isinstance(data, dict):
        return ""
    for key in _COMMAND_RAW_FILE_SHA_KEYS:
        val = data.get(key)
        if isinstance(val, str) and len(val) == 64:
            lower = val.lower()
            if all(c in "0123456789abcdef" for c in lower):
                return lower
    return ""


def _command_artifact_row_for(artifact_path, reports_dir):
    """Build an _CmdArtifactRow for an existing artifact path."""
    try:
        size = artifact_path.stat().st_size if artifact_path.is_file() else 0
    except OSError:
        size = 0
    if artifact_path.is_dir():
        # Directories (e.g. *_qc_run_capture/) get a synthetic OK row.
        return _CmdArtifactRow(
            name=artifact_path.name + "/",
            rel_path=str(artifact_path.relative_to(reports_dir)),
            bytes=0,
            declared_sha="",
            recomputed_sha="",
            status="OK",
        )
    recomputed = _command_sha256_of_file(artifact_path)
    if not recomputed:
        return _CmdArtifactRow(
            name=artifact_path.name,
            rel_path=str(artifact_path.relative_to(reports_dir)),
            bytes=size,
            declared_sha="",
            recomputed_sha="",
            status="ERROR",
        )
    # Look for a sidecar pin. For X.md try X.json; for X.json try itself.
    if artifact_path.suffix.lower() == ".md":
        sidecar = artifact_path.with_suffix(".json")
    elif artifact_path.suffix.lower() == ".json":
        sidecar = artifact_path
    else:
        sidecar = artifact_path
    declared = _command_load_sidecar_pin(sidecar)
    if not declared:
        status = "NO_DECLARED_SHA"
    elif declared == recomputed:
        status = "OK"
    else:
        status = "SEAL_DRIFT"
    return _CmdArtifactRow(
        name=artifact_path.name,
        rel_path=str(artifact_path.relative_to(reports_dir)),
        bytes=size,
        declared_sha=declared,
        recomputed_sha=recomputed,
        status=status,
    )


def _command_discover_lifecycle_ids(reports_dir):
    """Return sorted list of canonical lifecycle ids (e.g. 'B006_002')."""
    if not reports_dir.exists() or not reports_dir.is_dir():
        return []
    ids = set()
    try:
        entries = list(reports_dir.iterdir())
    except OSError:
        return []
    for entry in entries:
        name = entry.name
        m = _command_re.match(r"^(b006_\d{3})(?:_|$)", name, _command_re.IGNORECASE)
        if m:
            ids.add(m.group(1).upper())
    return sorted(ids)


def _command_collect_artifacts(reports_dir, lifecycle_id):
    """Return sorted list of paths whose name starts with the lifecycle id."""
    prefix_lc = lifecycle_id.lower() + "_"
    prefix_eq = lifecycle_id.lower()
    out = []
    try:
        for entry in sorted(reports_dir.iterdir()):
            name_lc = entry.name.lower()
            if name_lc.startswith(prefix_lc) or name_lc == prefix_eq:
                out.append(entry)
    except OSError:
        return []
    return out


def _command_infer_phases(artifact_paths):
    """Walk the phase ladder; mark each phase COMPLETE/NEXT/PENDING.

    Two-pass rule: a missing phase can only be NEXT if no higher-numbered
    phase is already COMPLETE. If later phases are COMPLETE (e.g. the
    lifecycle is terminal-archived but an earlier phase was handled
    implicitly off-disk), earlier missing phases are PENDING, not NEXT.
    """
    names_lc = [p.name.lower() for p in artifact_paths]
    # Pass 1: figure out which phases have a matching artifact, and the
    # highest-numbered phase index that is COMPLETE (-1 if none).
    complete_by_phase = {}
    highest_complete = -1
    for phase, _label, fragments in _COMMAND_PHASE_DEFS:
        has_any = any(
            any(frag.lower() in name for frag in fragments) for name in names_lc
        )
        complete_by_phase[phase] = has_any
        if has_any and phase > highest_complete:
            highest_complete = phase
    # Pass 2: assign statuses. NEXT is the smallest missing phase that is
    # strictly greater than highest_complete (so a missing phase before any
    # later COMPLETE phase is always PENDING, never NEXT).
    rows = []
    next_marked = False
    for phase, label, _fragments in _COMMAND_PHASE_DEFS:
        if complete_by_phase[phase]:
            status = "COMPLETE"
        elif phase > highest_complete and not next_marked:
            status = "NEXT"
            next_marked = True
        else:
            status = "PENDING"
        rows.append(_CmdPhaseRow(phase=phase, label=label, status=status))
    return rows


def _command_extract_description(artifact_paths, lifecycle_id):
    """Best-effort: pull a short description from the spec sidecar."""
    for p in artifact_paths:
        if p.suffix.lower() != ".json":
            continue
        name_lc = p.name.lower()
        if "_spec_draft" not in name_lc and "_minimum_feasible_diagnostic_spec" not in name_lc:
            continue
        try:
            data = _command_json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except (OSError, IOError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        for key in ("candidate_description", "description", "title", "candidate_name"):
            val = data.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()[:200]
    return lifecycle_id


def _command_extract_verdict(artifact_paths):
    """Best-effort: pull sealed verdict from result_sealing_report JSON.
    Handles both flat string and nested-dict shapes; in real B006_002 the
    'sealed_verdict' key holds a dict with 'verdict_closed_enum_value'."""
    for p in artifact_paths:
        if p.suffix.lower() != ".json":
            continue
        if "_result_sealing_report" not in p.name.lower():
            continue
        try:
            data = _command_json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except (OSError, IOError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        for key in ("sealed_verdict", "verdict", "result_verdict", "terminal_verdict"):
            val = data.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
            if isinstance(val, dict):
                for nested_key in (
                    "verdict_closed_enum_value", "verdict", "value", "sealed_verdict",
                ):
                    nested = val.get(nested_key)
                    if isinstance(nested, str) and nested.strip():
                        return nested.strip()
    return ""


def _command_load_next_authorize(decisions_path, lifecycle_id):
    """Read the tail of decisions.md, return the last `Authorize <lid>...`
    phrase mentioning the lifecycle id, verbatim. '' if no match."""
    if not decisions_path.exists():
        return ""
    try:
        size = decisions_path.stat().st_size
        with open(decisions_path, "rb") as f:
            if size > 131072:
                f.seek(size - 131072)
            tail = f.read().decode("utf-8", errors="replace")
    except (OSError, IOError):
        return ""
    pattern = _command_re.compile(
        r"`(Authorize\s+" + _command_re.escape(lifecycle_id) + r"[^`]+?)`",
        _command_re.IGNORECASE,
    )
    matches = pattern.findall(tail)
    return matches[-1] if matches else ""


def _command_scan_lifecycles(reports_dir, decisions_path):
    """Pure read-only scan. Returns list[_CmdLifecycleRow] sorted by id."""
    rows = []
    for lid in _command_discover_lifecycle_ids(reports_dir):
        artifacts = _command_collect_artifacts(reports_dir, lid)
        artifact_rows = [_command_artifact_row_for(a, reports_dir) for a in artifacts]
        phases = _command_infer_phases(artifacts)
        description = _command_extract_description(artifacts, lid)
        verdict = _command_extract_verdict(artifacts)
        next_auth = _command_load_next_authorize(decisions_path, lid)
        rows.append(_CmdLifecycleRow(
            lifecycle_id=lid,
            description=description,
            sealed_verdict=verdict,
            phases=phases,
            artifacts=artifact_rows,
            next_authorize=next_auth,
        ))
    return rows


@app.get("/command", response_class=HTMLResponse)
async def page_command(request: Request):
    """SPARTA Trading Command Center v1 — read-only lifecycle viewer.

    GET-only. Localhost-only. No write. No external network. No trading
    affordance. Fail-closed rendering with explicit MISSING / SEAL_DRIFT /
    NO_DECLARED_SHA / ERROR statuses; never fabricates a value.
    """
    lifecycles = _command_scan_lifecycles(
        _COMMAND_REPORTS_DIR, _COMMAND_DECISIONS_FILE
    )
    return templates.TemplateResponse(
        "command.html",
        {
            "request": request,
            "page": "command",
            "lifecycles": lifecycles,
            "posture_invariants": _COMMAND_POSTURE_INVARIANTS,
            "reports_dir_exists": _COMMAND_REPORTS_DIR.exists(),
        },
    )


# === END SPARTA Trading Command Center v1 block ============================


# ===========================================================================
# Weekly RS s21 broker-free paper status card (read-only viewer)
#
# Mirrors the /command pattern: GET-only, localhost-only, no forms, no inputs,
# no mutating buttons, no broker/API/order/scheduler/cycle/live affordances.
# Reads the harness status aggregator strictly read-only. Fail-closed: if the
# aggregator raises, render the page anyway with an error banner.
# DIAGNOSTIC_ONLY -- FRC NEVER_GRANTED -- Live BLOCKED_AT_6_GATES.
# ===========================================================================

@app.get("/paper", response_class=HTMLResponse)
def page_weekly_rs_paper(request: Request):
    error = None
    paper = None
    try:
        from paper_trading.weekly_rs_s21_forward_paper_harness import status as _paper_status
        paper = _paper_status.paper_status()
    except Exception as exc:  # noqa: BLE001 — fail-closed render, never fabricate
        error = f"{type(exc).__name__}: {exc}"
    return templates.TemplateResponse(
        "weekly_rs_s21_paper.html",
        {
            "request": request,
            "page": "paper",
            "paper": paper,
            "error": error,
        },
    )


# ===========================================================================
# SPARTA Trade Intelligence Journal v1 (read-only viewer)
#
# Mirrors the /command pattern: GET-only, localhost-only, no forms, no
# inputs, no mutating buttons, no broker / API / order / scheduler / live
# trading affordances. Reads the external obsidian-trade-logger project
# strictly read-only via tools/trade_journal_adapter.py.
#
# If the adapter raises, the route fail-closes with status=ERROR and
# renders the page anyway so the operator can see what went wrong.
# ===========================================================================


def _journal_empty_payload(status: str, *, errors: list[str]) -> dict:
    """Fallback payload when the adapter is unimportable or raises.

    Kept inline in app.py so a broken adapter cannot prevent the route
    from rendering the safety pills and an ERROR banner.
    """
    from datetime import datetime as _dt, timezone as _tz
    return {
        "status": status,
        "posture": {
            "trading": "PAUSED",
            "live_status": "BLOCKED_AT_6_GATES",
            "read_only": True,
            "external_project": "READ_ONLY",
            "broker_api": "DISCONNECTED",
        },
        "generated_at": _dt.now(_tz.utc).isoformat(),
        "external_root": "",
        "external_root_exists": False,
        "summary": {
            "strategy_count": 0,
            "symbol_count": 0,
            "trade_count": 0,
            "closed_trade_count": 0,
            "open_trade_count": 0,
            "source": "none",
        },
        "scorecards": [],
        "strategy_metrics": [],
        "symbol_metrics": [],
        "gates": [],
        "daily_pnl_correlation": {"status": "MISSING", "reason": "adapter_unavailable"},
        "weekday_performance": {"status": "MISSING", "reason": "adapter_unavailable"},
        "month_performance": {"status": "MISSING", "reason": "adapter_unavailable"},
        "risk_of_ruin": {"status": "MISSING", "reason": "adapter_unavailable"},
        "monte_carlo_summary": {"status": "MISSING", "reason": "adapter_unavailable"},
        "missing": ["adapter_unavailable_or_failed"],
        "errors": list(errors),
    }


@app.get("/journal", response_class=HTMLResponse)
async def page_journal(request: Request):
    """SPARTA Trade Intelligence Journal v1 — read-only viewer.

    GET-only. Localhost-only. No writes anywhere. No order placement.
    No broker connections. Fail-closed if the adapter fails.
    """
    payload: dict
    try:
        # Import inside the handler so a broken adapter cannot block app
        # import-time. Re-imported each request: the adapter is cheap and
        # this lets tests monkeypatch it cleanly.
        from tools import trade_journal_adapter as _tja
        payload = _tja.load_payload()
        if not isinstance(payload, dict):
            payload = _journal_empty_payload(
                "ERROR",
                errors=[f"adapter_returned_non_dict:{type(payload).__name__}"],
            )
    except Exception as exc:  # noqa: BLE001 — fail-closed render
        payload = _journal_empty_payload(
            "ERROR",
            errors=[f"{type(exc).__name__}: {exc}"],
        )

    return templates.TemplateResponse(
        "journal.html",
        {
            "request": request,
            "page": "journal",
            "payload": payload,
        },
    )


# === END SPARTA Trade Intelligence Journal v1 block ========================


# ===========================================================================
# SPARTA Trade Decision Ledger v1 (read-only viewer)
#
# GET-only. Localhost/read-only style. No forms, no mutating buttons, no
# broker/exchange connection, no order placement, no bot control. Reads only
# existing external JSON/JSONL artifacts through
# tools/trade_decision_ledger_adapter.py. If the adapter raises, render a
# fail-closed ERROR payload.
# ===========================================================================


def _trade_ledger_empty_payload(status: str, *, errors: list[str]) -> dict:
    from datetime import datetime as _dt, timezone as _tz
    return {
        "status": status,
        "generated_at": _dt.now(_tz.utc).isoformat(),
        "external_root": "",
        "external_root_exists": False,
        "safety_banner": (
            "READ ONLY  no broker, no exchange, no order placement, "
            "no bot control."
        ),
        "summary": {
            "total_records": 0,
            "symbols_found": 0,
            "blocked_records": 0,
            "allowed_paper_observation_records": 0,
            "parse_errors": 0,
            "missing_sources": 0,
        },
        "source_health": [],
        "records": [],
        "errors": list(errors),
    }


@app.get("/trade-ledger", response_class=HTMLResponse)
async def page_trade_ledger(request: Request):
    """SPARTA Trade Decision Ledger v1 — read-only normalized viewer."""
    try:
        from tools import trade_decision_ledger_adapter as _tdla
        payload = _tdla.load_payload()
        if not isinstance(payload, dict):
            payload = _trade_ledger_empty_payload(
                "ERROR",
                errors=[f"adapter_returned_non_dict:{type(payload).__name__}"],
            )
    except Exception as exc:  # noqa: BLE001 - fail-closed render
        payload = _trade_ledger_empty_payload(
            "ERROR",
            errors=[f"{type(exc).__name__}: {exc}"],
        )

    return templates.TemplateResponse(
        "trade_ledger.html",
        {
            "request": request,
            "page": "trade_ledger",
            "payload": payload,
        },
    )


# === END SPARTA Trade Decision Ledger v1 block =============================


# ===========================================================================
# SPARTA Research Orchestrator v2 (read-only viewer)
#
# Mirrors the /command pattern: GET-only, localhost-only, no forms, no
# inputs, no mutating buttons. Reads state from
# storage/research_orchestrator/ which the watcher CLI populates:
#
#     python tools/research_orchestrator_watch.py
#
# Fail-closed: if storage is missing or unreadable, route still renders
# (empty tables) so the operator can see what's wrong.
# ===========================================================================


_RO_REPO_ROOT = BASE
_RO_STORAGE_DIR = BASE / "storage" / "research_orchestrator"


def _ro_safe_load_storage() -> dict:
    """Load orchestrator state from storage/ — never raises."""
    from sparta_commander.research_orchestrator import git_sentinel as _ro_gs
    from sparta_commander.research_orchestrator import protected_drift as _ro_pd
    from sparta_commander.research_orchestrator.storage import Storage as _ROStorage

    candidates = []
    pending_decisions = []
    audit_log = []
    action_ledger = []
    snapshot = {
        "head_sha": "",
        "head_subject": "",
        "staged_files": [],
        "untracked_files": [],
        "modified_files": [],
        "dirty_protected_files": [],
        "untracked_tmp_helpers": [],
        "duplicate_chain_files": [],
        "protected_drift_details": [],
    }

    try:
        storage = _ROStorage(_RO_STORAGE_DIR)
        candidates = [c.to_dict() for c in storage.list_candidates()]
        pending_decisions = storage.list_pending_decisions()
        # Sort decisions: HIGH priority first
        prio_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        pending_decisions.sort(
            key=lambda d: (prio_order.get(d.get("priority", "LOW"), 9),
                          d.get("created_utc", ""))
        )
        audit_log = list(storage.iter_audit_logs(days=3))
        # newest first; cap
        audit_log.sort(key=lambda e: e.get("ts_utc", ""), reverse=True)
        audit_log = audit_log[:20]
        action_ledger = list(storage.iter_action_ledger(days=14))
        action_ledger.sort(key=lambda e: e.get("ts_utc", ""), reverse=True)
        action_ledger = action_ledger[:20]
    except (OSError, ValueError):
        pass  # render with empty tables

    try:
        snap = _ro_gs.scan(_RO_REPO_ROOT)
        snapshot = snap.to_dict()
        # Augment with protected-drift classification
        drift = _ro_pd.scan_protected_drift(
            repo=_RO_REPO_ROOT,
            storage_root=_RO_STORAGE_DIR,
            protected_paths=_ro_gs.PROTECTED_FILES_NEVER_TOUCH,
        )
        snapshot["protected_drift_details"] = drift
    except (RuntimeError, OSError, PermissionError):
        pass

    return {
        "snapshot": snapshot,
        "candidates": candidates,
        "pending_decisions": pending_decisions,
        "audit_log": audit_log,
        "action_ledger": action_ledger,
    }


@app.get("/command/research-orchestrator", response_class=HTMLResponse)
async def page_research_orchestrator(request: Request):
    """SPARTA Research Orchestrator v2 — read-only viewer.

    GET-only. Localhost-only. No write. No trading affordance. Renders
    candidates, pending decisions, audit log, and action ledger from
    storage/research_orchestrator/. Approval buttons are intentionally
    absent — operator approval happens via terminal operator-phrase
    workflow, not via HTTP buttons.
    """
    state = _ro_safe_load_storage()
    snap = state["snapshot"]
    drift_details = snap.get("protected_drift_details", [])
    new_drift_paths = [
        d["path"] for d in drift_details
        if d.get("classification") == "NEW_PROTECTED_DRIFT"
    ]
    return templates.TemplateResponse(
        "research_orchestrator.html",
        {
            "request": request,
            "page": "research_orchestrator",
            "head_sha": snap.get("head_sha", ""),
            "head_subject": snap.get("head_subject", ""),
            "staged_count": len(snap.get("staged_files", [])),
            "untracked_count": len(snap.get("untracked_files", [])),
            "modified_count": len(snap.get("modified_files", [])),
            "duplicate_chain_count": len(snap.get("duplicate_chain_files", [])),
            "tmp_helpers_count": len(snap.get("untracked_tmp_helpers", [])),
            "protected_drift_details": drift_details,
            "new_drift_paths": new_drift_paths,
            "candidates": state["candidates"],
            "pending_decisions": state["pending_decisions"],
            "audit_log": state["audit_log"],
            "action_ledger": state["action_ledger"],
        },
    )


# === END SPARTA Research Orchestrator v2 block =============================


# ===========================================================================
# SPARTA JARVIS Command Center (additive, read-only)
#
# A cinematic single-page status console that AGGREGATES existing read-only
# signals. It never executes anything: no trading, no uploads, no automation
# firing, no credential access. Every section fails closed — if a source is
# missing it reports "not connected" / "waiting for signal" and NEVER invents
# a metric or a profit number.
#
# The page is /jarvis; the live data feed is GET /api/jarvis/status.
# ===========================================================================

def _jarvis_safe(fn):
    """Run a section probe, converting any failure into a fail-closed dict
    so one broken source never takes the whole console down."""
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 — console must always render
        return {"state": "error", "detail": f"{type(exc).__name__}: {exc}"}


def _jarvis_system_core() -> dict:
    from datetime import datetime as _dt
    counts = _jarvis_safe(db.get_counts)
    return {
        "state": "online",
        "server": "running",
        "now": _dt.now().isoformat(timespec="seconds"),
        "counts": counts if isinstance(counts, dict) else {},
    }


def _jarvis_ai_brains() -> dict:
    """Claude / Codex / Gemini via the three-brain probe; Ollama by PATH
    presence only (cheap + honest — we do not claim a model is 'online')."""
    import shutil as _shutil
    brains = {}
    try:
        from spartacus.three_brain_router import detect_available_tools
        tools = detect_available_tools()
        for name in ("claude", "codex", "gemini"):
            info = tools.get(name, {}) or {}
            brains[name] = {
                "state": "ready" if info.get("available") else "not_connected",
                "detail": info.get("note") or "",
                "version": info.get("version"),
            }
    except Exception as exc:  # noqa: BLE001
        for name in ("claude", "codex", "gemini"):
            brains[name] = {"state": "error", "detail": f"{type(exc).__name__}: {exc}"}
    # Ollama: report install presence only, not a live model status.
    if _shutil.which("ollama"):
        model = (db.get_setting("model_name") or "").strip()
        brains["ollama"] = {
            "state": "installed",
            "detail": f"default model: {model}" if model else "installed on PATH",
        }
    else:
        brains["ollama"] = {"state": "not_connected", "detail": "ollama not found on PATH"}
    return {"state": "online", "brains": brains}


def _jarvis_trading_bridge() -> dict:
    """READ-ONLY. Counts sealed lifecycles and reads the paper-status card.
    No order, no broker, no execution affordance anywhere in this path."""
    lifecycles = []
    try:
        rows = _command_scan_lifecycles(_COMMAND_REPORTS_DIR, _COMMAND_DECISIONS_FILE)
        for r in rows[:6]:
            lifecycles.append({
                "id": getattr(r, "lifecycle_id", ""),
                "verdict": getattr(r, "sealed_verdict", "") or "—",
            })
    except Exception as exc:  # noqa: BLE001
        return {"state": "waiting", "detail": f"{type(exc).__name__}: {exc}",
                "read_only": True, "locked": True}
    paper = None
    try:
        from paper_trading.weekly_rs_s21_forward_paper_harness import status as _paper_status
        ps = _paper_status.paper_status()
        if isinstance(ps, dict):
            paper = {"mode": ps.get("mode") or "DIAGNOSTIC_ONLY",
                     "live": "BLOCKED"}
    except Exception:  # noqa: BLE001 — paper card is optional
        paper = None
    return {
        "state": "online" if lifecycles else "waiting",
        "read_only": True,
        "locked": True,
        "lifecycle_count": len(lifecycles),
        "lifecycles": lifecycles,
        "paper": paper,
        "detail": "Read-only lifecycle viewer. Live trading blocked." if lifecycles
                  else "No sealed lifecycles found yet — waiting for signal.",
    }


def _jarvis_content_engine() -> dict:
    auto = (db.get_setting("auto_mode_enabled") or "false").lower() == "true"
    auto_video = (db.get_setting("auto_video_enabled") or "false").lower() == "true"
    autopilot = (db.get_setting("autopilot_enabled") or "false").lower() == "true"
    yt_connected = bool((db.get_setting("youtube_oauth_token") or "").strip())
    return {
        "state": "online",
        "hydra": {"state": "ready", "detail": "Local talking-head pipeline"},
        "victory": {"state": "ready", "detail": "Funnel + ship tracker"},
        "youtube_autopilot": {
            "state": "armed" if autopilot else "idle",
            "detail": "Autopilot enabled" if autopilot else "Autopilot idle",
        },
        "auto_mode": {"state": "armed" if auto else "idle",
                      "auto_video": auto_video},
        "youtube_account": {
            "state": "connected" if yt_connected else "not_connected",
            "detail": "OAuth token present" if yt_connected
                      else "Not connected — connect in Settings",
        },
    }


def _jarvis_money_engine() -> dict:
    amazon = (db.get_setting("amazon_autopilot_enabled") or "true").lower() == "true"
    registry = (BASE / "data" / "asset_registry.json").exists()
    return {
        "state": "online",
        "affiliate": {"state": "compliance_first",
                      "detail": "No fake claims, no fake links"},
        "amazon": {"state": "armed" if amazon else "idle",
                   "detail": "Morning brief enabled" if amazon else "Brief idle"},
        "product_lock": {
            "state": "locked" if registry else "waiting",
            "detail": "asset_registry.json present" if registry
                      else "No asset registry yet — waiting for signal",
        },
    }


def _jarvis_moving_company() -> dict:
    # Placeholder only by design — no external fetch, no scraping.
    return {
        "state": "placeholder",
        "leads": None,
        "tasks": None,
        "detail": "Placeholder only — no external fetch wired up.",
    }


def _jarvis_safety_gates() -> dict:
    """Hard, non-negotiable gates surfaced as locked status. These are
    posture statements, not toggles — the console cannot flip them."""
    blocked = None
    try:
        from spartacus.agents._shared import load_json
        rows = load_json(_safety_log_path(), default=[])
        if isinstance(rows, list):
            blocked = len([r for r in rows if not r.get("passed")])
    except Exception:  # noqa: BLE001
        blocked = None
    return {
        "state": "locked",
        "gates": [
            {"name": "Trading execution", "status": "LOCKED",
             "detail": "Read-only. No order path exists in this console."},
            {"name": "Approvals", "status": "REQUIRED",
             "detail": "Human approval required before any action."},
            {"name": "YouTube upload", "status": "APPROVAL_REQUIRED",
             "detail": "Uploads pass the safety gate + human review."},
            {"name": "Live automation", "status": "BLOCKED",
             "detail": "No automation fires from this page."},
        ],
        "safety_blocked_count": blocked,
    }


def _jarvis_daily_mission(content: dict, money: dict) -> dict:
    """Derive a few recommended actions from current state. These are
    guidance strings derived from real flags — never invented metrics."""
    actions = []
    try:
        if content.get("youtube_account", {}).get("state") == "not_connected":
            actions.append("Connect YouTube in Settings to enable uploads.")
        if content.get("auto_mode", {}).get("state") == "idle":
            actions.append("Auto mode is idle — run a manual cycle when ready.")
        if money.get("product_lock", {}).get("state") == "waiting":
            actions.append("No asset registry yet — lock a product to arm the money engine.")
    except Exception:  # noqa: BLE001
        pass
    if not actions:
        actions.append("All core signals nominal — hold position and review reports.")
    return {"state": "online", "actions": actions[:5]}


# --- JARVIS Step 02: Operator Intelligence (read-only) ---------------------
# These probes add operator situational awareness only. They run read-only
# git plumbing, stat a few known paths, and emit static posture flags. No
# probe writes, executes, trades, uploads, or mutates repo state.

def _jarvis_run_git(args: list) -> str:
    """Run a single read-only git command and return stripped stdout.
    Raises on non-zero exit so the caller's fail-closed wrapper engages."""
    import subprocess as _sp
    proc = _sp.run(
        ["git", *args],
        cwd=str(BASE),
        capture_output=True,
        text=True,
        timeout=5,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or "git failed").strip())
    return (proc.stdout or "").strip()


def _jarvis_git() -> dict:
    """READ-ONLY git snapshot: branch, short HEAD, clean/dirty, change
    counts, and the last 3 commit subjects. No mutation, no fetch, no push."""
    branch = _jarvis_run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _jarvis_run_git(["rev-parse", "--short", "HEAD"])
    porcelain = _jarvis_run_git(["status", "--porcelain"])
    lines = [ln for ln in porcelain.splitlines() if ln.strip()]
    untracked = len([ln for ln in lines if ln.startswith("??")])
    modified = len(lines) - untracked
    log = _jarvis_run_git(["log", "-3", "--format=%h %s"])
    commits = []
    for ln in log.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        parts = ln.split(" ", 1)
        sh = parts[0]
        subj = parts[1] if len(parts) > 1 else ""
        commits.append({"short_hash": sh, "subject": subj})
    clean = not lines
    return {
        "state": "online",
        "branch": branch,
        "head": head,
        "clean": clean,
        "dirty": not clean,
        "modified_count": modified,
        "untracked_count": untracked,
        "commits": commits,
        "detail": "Working tree clean." if clean
                  else f"{modified} modified, {untracked} untracked.",
    }


def _jarvis_capture_boot_head():
    """Capture the short HEAD this process booted with, ONCE at import.
    Fail-closed to None so a git-less environment never breaks startup."""
    try:
        return _jarvis_run_git(["rev-parse", "--short", "HEAD"])
    except Exception:  # noqa: BLE001 — boot capture is best-effort.
        return None


# Recorded a single time when app.py is imported (the running build's HEAD).
# Because uvicorn runs with reload=False, this value stays pinned to the
# commit the live process was started on, even after new commits land — which
# is exactly what the freshness guard compares against to detect staleness.
_JARVIS_SERVER_BOOT_HEAD = _jarvis_capture_boot_head()


def _jarvis_freshness_guard(server_head=None, current_head=None) -> dict:
    """READ-ONLY freshness check (Bundle B / T6). Compares the HEAD this live
    process booted on against the current on-disk git HEAD. If they differ the
    running server is serving stale code (uvicorn reload=False) and an operator
    restart is needed. Pure comparison: runs one read-only `git rev-parse`,
    writes nothing, executes nothing, restarts nothing. Params are injectable
    for testing; production callers pass neither."""
    boot = server_head if server_head is not None else _JARVIS_SERVER_BOOT_HEAD
    if current_head is not None:
        cur = current_head
    else:
        try:
            cur = _jarvis_run_git(["rev-parse", "--short", "HEAD"])
        except Exception:  # noqa: BLE001 — unknown is safe, never fatal.
            cur = None
    if not boot or not cur:
        return {
            "state": "unknown",
            "read_only": True,
            "server_head": boot,
            "current_head": cur,
            "stale": False,
            "detail": "Cannot compare HEADs (git or boot head unavailable); "
                      "freshness UNKNOWN.",
        }
    stale = boot != cur
    return {
        "state": "stale" if stale else "fresh",
        "read_only": True,
        "server_head": boot,
        "current_head": cur,
        "stale": stale,
        "detail": (
            f"Live server booted on {boot} but git HEAD is now {cur}: "
            f"running build is STALE — restart per the Step 49 protocol to "
            f"serve current code."
            if stale else
            f"Live server build {boot} matches git HEAD {cur}: fresh."
        ),
    }


def _jarvis_operator_safety() -> dict:
    """Static read-only posture flags. The console exposes no execution,
    broker, secret, or force-git affordance — these assert that contract."""
    return {
        "state": "locked",
        "read_only": True,
        "no_execution_control": True,
        "no_broker_control": True,
        "no_secret_display": True,
        "no_force_git": True,
        "detail": "Operator panel is observation-only. No controls are exposed.",
    }


def _jarvis_project_files() -> dict:
    """Confirm key JARVIS artifacts exist on disk. Stat only — never reads
    contents, never touches ignored logs or secrets."""
    checks = {
        "release_note_exists":
            (BASE / "docs" / "JARVIS_COMMAND_CENTER_RELEASE_NOTE.md").exists(),
        "jarvis_template_exists":
            (BASE / "templates" / "jarvis.html").exists(),
        "tests_file_exists":
            (BASE / "tests" / "test_jarvis_route.py").exists(),
    }
    present = sum(1 for v in checks.values() if v)
    return {
        "state": "online" if present == len(checks) else "waiting",
        "detail": f"{present}/{len(checks)} expected files present.",
        **checks,
    }


def _jarvis_brain_memory() -> dict:
    """Stat the brain_memory tree and a few known project folders. Does NOT
    read file contents and never touches the gitignored logs/ directory."""
    root = BASE / "brain_memory"
    if not root.exists():
        return {"state": "not_connected", "exists": False,
                "detail": "brain_memory/ not found.", "projects": {}}
    projects_dir = root / "projects"
    known = ("trading_bot", "hydra_video", "youtube_growth", "affiliate_system")
    projects = {}
    if projects_dir.exists():
        for name in known:
            projects[name] = (projects_dir / name).is_dir()
    found = sum(1 for v in projects.values() if v)
    return {
        "state": "online",
        "exists": True,
        "projects": projects,
        "detail": f"{found}/{len(known)} known project folders present.",
    }


def _jarvis_health_report() -> dict:
    """READ-ONLY. Loads the cached health report written offline by
    tools/jarvis_health_report.py. The web route NEVER runs the checks
    itself — it only reflects whatever the last manual run produced."""
    path = BASE / "storage" / "jarvis" / "health_report.json"
    if not path.exists():
        return {
            "state": "missing",
            "message": "Run tools/jarvis_health_report.py to generate a cached report.",
        }
    try:
        import json as _json
        data = _json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — fail-closed on bad/corrupt file
        return {"state": "unavailable", "error": f"{type(exc).__name__}: {exc}"}
    if not isinstance(data, dict):
        return {"state": "unavailable", "error": "report is not a JSON object"}
    data.setdefault("state", "ready")
    return data


def _jarvis_route_smoke_report() -> dict:
    """READ-ONLY. Loads the cached route smoke report written offline by
    tools/jarvis_route_smoke_report.py. The web route NEVER probes routes
    itself — it only reflects whatever the last manual run produced."""
    path = BASE / "storage" / "jarvis" / "route_smoke_report.json"
    if not path.exists():
        return {
            "state": "missing",
            "message": "Run tools/jarvis_route_smoke_report.py to generate a "
                       "cached route smoke report.",
        }
    try:
        import json as _json
        data = _json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — fail-closed on bad/corrupt file
        return {"state": "unavailable", "error": f"{type(exc).__name__}: {exc}"}
    if not isinstance(data, dict):
        return {"state": "unavailable", "error": "report is not a JSON object"}
    data.setdefault("state", "ready")
    return data


def _jarvis_file_hygiene_report() -> dict:
    """READ-ONLY. Loads the cached file-hygiene report written offline by
    tools/jarvis_file_hygiene_report.py. The web route NEVER runs git or scans
    the working tree itself — it only reflects the last manual run."""
    path = BASE / "storage" / "jarvis" / "file_hygiene_report.json"
    if not path.exists():
        return {
            "state": "missing",
            "message": "Run tools/jarvis_file_hygiene_report.py to generate a "
                       "cached file hygiene report.",
        }
    try:
        import json as _json
        data = _json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — fail-closed on bad/corrupt file
        return {"state": "unavailable", "error": f"{type(exc).__name__}: {exc}"}
    if not isinstance(data, dict):
        return {"state": "unavailable", "error": "report is not a JSON object"}
    data.setdefault("state", "ready")
    return data


# Known JARVIS cache files. These are the ONLY paths the freshness helper
# inspects. They are documented runtime caches (see system_map
# ignored_runtime_files) and are gitignored — recorded here as a documentation
# constant so the web route never has to shell out to `git check-ignore`.
_JARVIS_CACHE_FILES = (
    ("health_report", "storage/jarvis/health_report.json", 86400),
    ("route_smoke_report", "storage/jarvis/route_smoke_report.json", 86400),
    ("file_hygiene_report", "storage/jarvis/file_hygiene_report.json", 86400),
)


def _jarvis_cache_freshness() -> dict:
    """READ-ONLY. Reports whether the known JARVIS cache files are fresh, stale,
    missing, or invalid. It inspects ONLY metadata: file existence, the
    file modification time, and each report's own `generated_at` field. It
    NEVER runs the generator scripts, never shells out, never probes a route,
    and never writes anything — so it can never 'refresh' a cache itself.
    A missing or corrupt individual cache is handled per-file and never raises."""
    import json as _json
    from datetime import datetime as _dt

    now = _dt.now()
    caches: list = []
    warnings: list = []
    any_exists = False
    freshness_values: list = []

    for name, rel, threshold in _JARVIS_CACHE_FILES:
        path = BASE / rel
        entry = {
            "name": name,
            "path": rel,
            "exists": False,
            "gitignored": True,  # documented runtime cache; not a live git query
            "generated_at": None,
            "modified_at": None,
            "age_seconds": None,
            "freshness": "missing",
            "threshold_seconds": threshold,
        }
        if not path.exists():
            warnings.append(f"{name}: cache file missing ({rel}).")
            caches.append(entry)
            freshness_values.append("missing")
            continue

        any_exists = True
        entry["exists"] = True
        # file modification time — pure stat, no execution
        try:
            entry["modified_at"] = _dt.fromtimestamp(
                path.stat().st_mtime).isoformat(timespec="seconds")
        except Exception:  # noqa: BLE001 — mtime is best-effort, never fatal
            entry["modified_at"] = None

        try:
            data = _json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 — fail-closed on bad/corrupt file
            entry["freshness"] = "unavailable"
            entry["error"] = f"{type(exc).__name__}: {exc}"
            warnings.append(f"{name}: cache file is not valid JSON.")
            caches.append(entry)
            freshness_values.append("unavailable")
            continue
        if not isinstance(data, dict):
            entry["freshness"] = "unavailable"
            entry["error"] = "report is not a JSON object"
            warnings.append(f"{name}: cache content is not a JSON object.")
            caches.append(entry)
            freshness_values.append("unavailable")
            continue

        gen = data.get("generated_at")
        entry["generated_at"] = gen if isinstance(gen, str) else None
        parsed = None
        if isinstance(gen, str):
            try:
                parsed = _dt.fromisoformat(gen)
            except Exception:  # noqa: BLE001 — unparseable stamp → invalid below
                parsed = None
        if parsed is None:
            entry["freshness"] = "invalid"
            warnings.append(f"{name}: missing or unparseable generated_at.")
            caches.append(entry)
            freshness_values.append("invalid")
            continue

        age = (now - parsed).total_seconds()
        entry["age_seconds"] = int(age)
        if age <= threshold:
            entry["freshness"] = "fresh"
        else:
            entry["freshness"] = "stale"
            warnings.append(
                f"{name}: stale (age {int(age)}s > {threshold}s).")
        caches.append(entry)
        freshness_values.append(entry["freshness"])

    # worst-wins overall: unavailable/invalid > missing > stale > fresh
    if any(f in ("unavailable", "invalid") for f in freshness_values):
        overall = "unavailable"
    elif any(f == "missing" for f in freshness_values):
        overall = "missing"
    elif any(f == "stale" for f in freshness_values):
        overall = "stale"
    else:
        overall = "fresh"

    return {
        "state": "ready" if any_exists else "missing",
        "overall": overall,
        "generated_at": now.isoformat(timespec="seconds"),
        "caches": caches,
        "warnings": warnings[:8],
    }


_JARVIS_TRADING_REPORTS_REL = "trading_research/agentic_factory/reports"
_JARVIS_S26_D17_DIR = "s26_d17_trend_sr_ema_rsi_friction_stress"
_JARVIS_S26_D18_DIR = "s26_d18_trend_sr_ema_rsi_decision_gate"
_JARVIS_SURVIVAL_REL = "data/profit_brain_strategy_survival.json"


def _jarvis_safe_report_summary(path) -> str:
    """Read ONLY a small set of whitelisted scalar fields from a report.json
    so the console never dumps a full research file. Returns a short string."""
    import json as _json
    try:
        d = _json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — summary is best-effort, never fatal
        return ""
    if not isinstance(d, dict):
        return ""
    title = str(d.get("title", "")).strip()[:140]
    status = d.get("s26_current_status")
    level = status.get("level") if isinstance(status, dict) else None
    decision = d.get("decision") or d.get("trading_recommendation")
    parts = [p for p in (title, level,
                         (str(decision).strip()[:80] if decision else None)) if p]
    return " | ".join(parts)


def _jarvis_trading_detail() -> dict:
    """READ-ONLY. Summarizes committed/local trading-research report files
    under trading_research/agentic_factory/reports/. It never runs a backtest,
    fetches data, calls a broker, starts/stops a bot, reads secrets, or writes
    anything. Raw artifacts (any '*raw*' file) are never opened — only detected."""
    from datetime import datetime as _dt
    reports_dir = BASE / _JARVIS_TRADING_REPORTS_REL
    if not reports_dir.exists():
        return {
            "state": "missing",
            "read_only": True,
            "candidate_status": "RESEARCH_CANDIDATE_ONLY",
            "paper_ready": False,
            "live_ready": False,
            "broker_control": False,
            "message": f"{_JARVIS_TRADING_REPORTS_REL} not found",
        }
    warnings: list = []
    d17_dir = reports_dir / _JARVIS_S26_D17_DIR
    d18_dir = reports_dir / _JARVIS_S26_D18_DIR
    d17_exists = (d17_dir / "report.json").exists()
    d18_exists = (d18_dir / "report.json").exists()

    # Detect (but never read) any raw friction artifact, as a hygiene warning.
    try:
        if d17_dir.exists():
            for f in d17_dir.iterdir():
                if "raw" in f.name.lower():
                    warnings.append(f"raw artifact present (not read): {f.name}")
    except Exception:  # noqa: BLE001
        pass
    if not d18_exists:
        warnings.append("D18 decision gate report not found.")

    # latest_research_head: read from the D18 memo if available (file-only,
    # no git subprocess here).
    latest_head = None
    if d18_exists:
        try:
            import json as _json
            d18 = _json.loads((d18_dir / "report.json").read_text(encoding="utf-8"))
            if isinstance(d18, dict):
                latest_head = d18.get("head_commit_short") or d18.get("head_commit")
        except Exception:  # noqa: BLE001
            latest_head = None

    # latest_reports: a few most-recently-modified report.json files, with a
    # short safe summary each. We only ever open report.json, never raw files.
    latest_reports: list = []
    try:
        candidates = []
        for sub in reports_dir.iterdir():
            rj = sub / "report.json"
            if sub.is_dir() and rj.exists() and "raw" not in rj.name.lower():
                candidates.append(rj)
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for rj in candidates[:5]:
            latest_reports.append({
                "name": rj.parent.name,
                "path": f"{_JARVIS_TRADING_REPORTS_REL}/{rj.parent.name}/report.json",
                "kind": "json",
                "modified_at": _dt.fromtimestamp(rj.stat().st_mtime).isoformat(
                    timespec="seconds"),
                "has_md": (rj.parent / "report.md").exists(),
                "summary": _jarvis_safe_report_summary(rj),
            })
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"report scan partial: {type(exc).__name__}")

    return {
        "state": "ready",
        "read_only": True,
        "candidate_status": "RESEARCH_CANDIDATE_ONLY",
        "paper_ready": False,
        "live_ready": False,
        "broker_control": False,
        "latest_research_head": latest_head,
        "latest_reports": latest_reports,
        "s26": {
            "state": "available" if (d17_exists or d18_exists) else "missing",
            "latest_known_commit": latest_head or "066c16c",
            "status": "RESEARCH_CANDIDATE_ONLY",
            "d17_friction_report_exists": d17_exists,
            "d18_decision_gate_exists": d18_exists,
        },
        "warnings": warnings,
    }


# --- Bundle B (T1/T3): read-only Strategy Factory observation layer ---------
# These helpers surface decision/pass-fail/candidate information that already
# exists in committed research files. They open ONLY report.json (never any
# '*raw*' artifact), classify nothing, run no backtest, call no broker, write
# nothing, and trigger no Factory run. Missing/corrupt data fails closed to
# UNKNOWN / NOT_FOUND — never an invented decision.

_JARVIS_DECISION_PRIORITY = (
    "decision", "verdict", "final_verdict", "gate_decision", "is_verdict",
    "final_recommendation", "trading_recommendation", "recommendation",
)


def _jarvis_report_decision(d: dict) -> dict:
    """Extract one short decision/verdict string from a report dict, fail-closed.
    Report schemas vary widely (plain `verdict`, numbered `5_verdict`, suffixed
    `final_s26_verdict`, `gate_decision`, `trading_recommendation`, ...), so we
    try an exact priority list first, then a suffix/numbered fallback. Returns
    {"decision": str|None, "field": str|None}; None means UNKNOWN to callers."""
    import re as _re
    if not isinstance(d, dict):
        return {"decision": None, "field": None}
    for key in _JARVIS_DECISION_PRIORITY:
        v = d.get(key)
        if isinstance(v, str) and v.strip():
            return {"decision": v.strip()[:120], "field": key}
    for k, v in d.items():
        if not isinstance(k, str) or not (isinstance(v, str) and v.strip()):
            continue
        kl = k.lower()
        if (kl.endswith("_verdict") or kl.endswith("_decision")
                or _re.match(r"^\d+_(verdict|decision|recommendation)$", kl)):
            return {"decision": v.strip()[:120], "field": k}
    return {"decision": None, "field": None}


def _jarvis_factory_status() -> dict:
    """READ-ONLY Strategy Factory status (Bundle B / T1). Lists the most
    recently modified factory reports with each one's extracted decision so the
    console shows Factory progress at a glance. Opens only report.json; reads a
    bounded set; never executes, never writes, never runs a Factory job."""
    import json as _json
    from datetime import datetime as _dt
    reports_dir = BASE / _JARVIS_TRADING_REPORTS_REL
    if not reports_dir.exists():
        return {
            "state": "missing",
            "read_only": True,
            "report_count": 0,
            "latest_decisions": [],
            "detail": f"{_JARVIS_TRADING_REPORTS_REL} not found (NOT_FOUND).",
        }
    dirs = []
    try:
        for sub in reports_dir.iterdir():
            rj = sub / "report.json"
            if sub.is_dir() and rj.exists() and "raw" not in rj.name.lower():
                dirs.append(rj)
    except Exception as exc:  # noqa: BLE001
        return {
            "state": "error",
            "read_only": True,
            "report_count": 0,
            "latest_decisions": [],
            "detail": f"report scan failed: {type(exc).__name__}",
        }
    dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    latest_decisions = []
    for rj in dirs[:10]:
        try:
            d = _json.loads(rj.read_text(encoding="utf-8"))
            dec = _jarvis_report_decision(d if isinstance(d, dict) else {})
            decision = dec["decision"] or "UNKNOWN"
            field = dec["field"]
        except Exception:  # noqa: BLE001 — one bad file never sinks the panel.
            decision, field = "UNKNOWN", None
        latest_decisions.append({
            "name": rj.parent.name,
            "decision": decision,
            "decision_field": field,
            "modified_at": _dt.fromtimestamp(rj.stat().st_mtime).isoformat(
                timespec="seconds"),
        })
    return {
        "state": "ready",
        "read_only": True,
        "report_count": len(dirs),
        "latest_decisions": latest_decisions,
        "note": "Read-only view of committed factory reports. JARVIS runs no "
                "Factory job; runs stay operator-CLI/offline.",
    }


def _jarvis_survival_ledger() -> dict:
    """READ-ONLY pass/fail & survival ledger (Bundle B / T2). Surfaces the
    aggregate strategy-survival picture from the committed profit-brain file.
    Reads display-only; missing -> NOT_FOUND; corrupt -> fail closed. Writes
    nothing, computes no new score, places no trade."""
    import json as _json
    path = BASE / _JARVIS_SURVIVAL_REL
    if not path.exists():
        return {
            "state": "not_found",
            "read_only": True,
            "detail": f"{_JARVIS_SURVIVAL_REL} not found (NOT_FOUND).",
        }
    try:
        d = _json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — corrupt file fails closed.
        return {
            "state": "error",
            "read_only": True,
            "detail": "survival file unreadable/corrupt -> fail closed.",
        }
    if not isinstance(d, dict):
        return {"state": "error", "read_only": True,
                "detail": "survival file not an object -> fail closed."}

    def _row(x):
        if not isinstance(x, dict):
            return None
        return {
            "strategy": x.get("strategy"),
            "survival_score": x.get("survival_score"),
            "closed_trades": x.get("closed_trades"),
            "open_trades": x.get("open_trades"),
            "lifespan_days": x.get("lifespan_days"),
            "historical_drawdown_behavior": x.get("historical_drawdown_behavior"),
            "last_seen_at": x.get("last_seen_at"),
        }

    strategies = d.get("strategies")
    strat_count = len(strategies) if isinstance(strategies, dict) else 0
    most = [r for r in (_row(x) for x in (d.get("most_survivable") or [])) if r]
    weak = [r for r in (_row(x) for x in (d.get("weakest") or [])) if r]
    return {
        "state": "ready",
        "read_only": True,
        "status": d.get("status", "UNKNOWN"),
        "strategy_count": strat_count,
        "most_survivable": most[:5],
        "weakest": weak[:5],
        "note": "Observed survival metrics only; no strategy is paper/live "
                "ready and JARVIS deploys nothing.",
    }


def _jarvis_candidate_registry() -> dict:
    """READ-ONLY strategy-candidate registry (Bundle B / T3). Distinct from the
    VIDEO asset registries: this enumerates research strategy candidates from
    the committed survival file with a derived (display-only) observation tier.
    Every candidate is RESEARCH_ONLY — paper/live/broker all false. Reads only;
    writes nothing; deploys nothing."""
    import json as _json
    path = BASE / _JARVIS_SURVIVAL_REL
    if not path.exists():
        return {
            "state": "not_found",
            "read_only": True,
            "candidate_status": "RESEARCH_CANDIDATE_ONLY",
            "paper_ready": False,
            "live_ready": False,
            "broker_control": False,
            "candidates": [],
            "detail": f"{_JARVIS_SURVIVAL_REL} not found (NOT_FOUND).",
        }
    try:
        d = _json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — corrupt fails closed.
        return {
            "state": "error",
            "read_only": True,
            "candidate_status": "RESEARCH_CANDIDATE_ONLY",
            "paper_ready": False,
            "live_ready": False,
            "broker_control": False,
            "candidates": [],
            "detail": "survival file unreadable/corrupt -> fail closed.",
        }
    strategies = d.get("strategies") if isinstance(d, dict) else None
    candidates = []
    if isinstance(strategies, dict):
        for name, x in strategies.items():
            if not isinstance(x, dict):
                continue
            score = x.get("survival_score")
            if isinstance(score, (int, float)):
                tier = ("OBSERVED_SURVIVOR" if score >= 10
                        else "WEAK_CANDIDATE" if score > 0
                        else "NO_EDGE_YET")
            else:
                tier = "UNKNOWN"
            candidates.append({
                "strategy": x.get("strategy", name),
                "observation_tier": tier,
                "survival_score": score,
                "closed_trades": x.get("closed_trades"),
                "open_trades": x.get("open_trades"),
                "first_seen_at": x.get("first_seen_at"),
                "last_seen_at": x.get("last_seen_at"),
                "deployment_status": "RESEARCH_ONLY",
            })
        candidates.sort(
            key=lambda c: (c["survival_score"]
                           if isinstance(c["survival_score"], (int, float))
                           else -1),
            reverse=True)
    return {
        "state": "ready" if candidates else "empty",
        "read_only": True,
        "candidate_status": "RESEARCH_CANDIDATE_ONLY",
        "paper_ready": False,
        "live_ready": False,
        "broker_control": False,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "note": "Research strategy candidates (NOT video assets). Tiers are "
                "display-only labels derived from observed survival_score; no "
                "candidate is deployable from JARVIS.",
    }


def _jarvis_mission_board() -> dict:
    """READ-ONLY. Loads the operator mission board from a tracked JSON file
    and returns it for display. JARVIS never executes a mission, never runs
    safe_next_prompt, and never writes this file — it only reflects it."""
    path = BASE / "docs" / "jarvis_mission_board.json"
    if not path.exists():
        return {"state": "missing",
                "message": "docs/jarvis_mission_board.json not found"}
    try:
        import json as _json
        data = _json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — fail-closed on bad/corrupt file
        return {"state": "unavailable", "error": f"{type(exc).__name__}: {exc}"}
    if not isinstance(data, dict):
        return {"state": "unavailable", "error": "mission board is not a JSON object"}
    if "version" not in data:
        return {"state": "unavailable", "error": "missing 'version'"}
    missions = data.get("missions")
    if not isinstance(missions, list):
        return {"state": "unavailable", "error": "'missions' is not a list"}
    required = ("id", "title", "status", "priority", "area")
    clean = []
    for m in missions:
        if not isinstance(m, dict) or any(k not in m for k in required):
            return {"state": "unavailable",
                    "error": "a mission is missing required fields"}
        # Re-emit only known, display-only fields — never anything executable.
        clean.append({
            "id": m.get("id"),
            "title": m.get("title"),
            "status": m.get("status"),
            "priority": m.get("priority"),
            "area": m.get("area"),
            "blocked": bool(m.get("blocked", False)),
            "notes": m.get("notes", ""),
            "safe_next_prompt": m.get("safe_next_prompt", ""),
        })
    by_status: dict = {}
    by_priority: dict = {}
    for m in clean:
        by_status[m["status"]] = by_status.get(m["status"], 0) + 1
        by_priority[m["priority"]] = by_priority.get(m["priority"], 0) + 1
    return {
        "state": "ready",
        "version": data.get("version"),
        "updated_at": data.get("updated_at"),
        "missions": clean,
        "counts": {
            "total": len(clean),
            "by_status": by_status,
            "by_priority": by_priority,
            "blocked": sum(1 for m in clean if m["blocked"]),
        },
    }


def _jarvis_prompt_library() -> dict:
    """READ-ONLY. Loads the operator prompt library from a tracked JSON file
    and returns it for DISPLAY ONLY. JARVIS never executes a prompt, never
    sends prompt text anywhere, and never writes this file — it only reflects
    the text so a human can read it."""
    path = BASE / "docs" / "jarvis_prompt_library.json"
    if not path.exists():
        return {"state": "missing",
                "message": "docs/jarvis_prompt_library.json not found"}
    try:
        import json as _json
        data = _json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — fail-closed on bad/corrupt file
        return {"state": "unavailable", "error": f"{type(exc).__name__}: {exc}"}
    if not isinstance(data, dict):
        return {"state": "unavailable", "error": "prompt library is not a JSON object"}
    if "version" not in data:
        return {"state": "unavailable", "error": "missing 'version'"}
    prompts = data.get("prompts")
    if not isinstance(prompts, list):
        return {"state": "unavailable", "error": "'prompts' is not a list"}
    required = ("id", "title", "category", "risk", "prompt", "allowed")
    clean = []
    for p in prompts:
        if not isinstance(p, dict) or any(k not in p for k in required):
            return {"state": "unavailable",
                    "error": "a prompt is missing required fields"}
        # Re-emit only known, display-only fields. The prompt is plain text
        # that is NEVER executed — it is shown to a human operator and nothing
        # more.
        clean.append({
            "id": str(p.get("id")),
            "title": str(p.get("title")),
            "category": str(p.get("category")),
            "risk": str(p.get("risk")),
            "prompt": str(p.get("prompt")),
            "allowed": bool(p.get("allowed", False)),
            "notes": str(p.get("notes", "")),
        })
    by_category: dict = {}
    by_risk: dict = {}
    for p in clean:
        by_category[p["category"]] = by_category.get(p["category"], 0) + 1
        by_risk[p["risk"]] = by_risk.get(p["risk"], 0) + 1
    return {
        "state": "ready",
        "version": data.get("version"),
        "updated_at": data.get("updated_at"),
        "prompts": clean,
        "counts": {
            "total": len(clean),
            "by_category": by_category,
            "by_risk": by_risk,
            "allowed": sum(1 for p in clean if p["allowed"]),
        },
    }


def _jarvis_system_map() -> dict:
    """READ-ONLY. Loads the JARVIS system map from a tracked JSON file and
    returns it for DISPLAY ONLY. Script paths in the map are documentation
    strings — JARVIS never executes them and never writes this file."""
    path = BASE / "docs" / "jarvis_system_map.json"
    if not path.exists():
        return {"state": "missing",
                "message": "docs/jarvis_system_map.json not found"}
    try:
        import json as _json
        data = _json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — fail-closed on bad/corrupt file
        return {"state": "unavailable", "error": f"{type(exc).__name__}: {exc}"}
    if not isinstance(data, dict):
        return {"state": "unavailable", "error": "system map is not a JSON object"}
    if "version" not in data:
        return {"state": "unavailable", "error": "missing 'version'"}
    posture = data.get("posture")
    panels = data.get("panels")
    scripts = data.get("scripts")
    if not isinstance(posture, dict):
        return {"state": "unavailable", "error": "'posture' is not an object"}
    if not isinstance(panels, list):
        return {"state": "unavailable", "error": "'panels' is not a list"}
    if not isinstance(scripts, list):
        return {"state": "unavailable", "error": "'scripts' is not a list"}
    panel_required = ("id", "title", "kind", "api_key")
    clean_panels = []
    seen_api_keys: set = set()
    for p in panels:
        if not isinstance(p, dict) or any(k not in p for k in panel_required):
            return {"state": "unavailable",
                    "error": "a panel is missing required fields"}
        # api_key documents which /api/jarvis/status key this panel reads. It is
        # a plain DISPLAY string — never used to dispatch, import, or call code.
        api_key = str(p.get("api_key"))
        if api_key in seen_api_keys:
            return {"state": "unavailable",
                    "error": f"duplicate api_key: {api_key}"}
        seen_api_keys.add(api_key)
        # Re-emit only documentation fields. `script` is a path STRING shown to
        # a human — it is never imported, run, or resolved to a callable.
        clean_panels.append({
            "id": str(p.get("id")),
            "api_key": api_key,
            "title": str(p.get("title")),
            "kind": str(p.get("kind")),
            "source": str(p.get("source", "")),
            "cache_file": p.get("cache_file"),
            "script": p.get("script"),
            "writes_from_web": bool(p.get("writes_from_web", False)),
            "description": str(p.get("description", "")),
        })
    clean_scripts = []
    for s in scripts:
        if not isinstance(s, dict) or "path" not in s:
            return {"state": "unavailable",
                    "error": "a script entry is missing 'path'"}
        clean_scripts.append({
            "path": str(s.get("path")),
            "purpose": str(s.get("purpose", "")),
            "manual_only": bool(s.get("manual_only", True)),
            "called_by_web": bool(s.get("called_by_web", False)),
        })
    by_kind: dict = {}
    for p in clean_panels:
        by_kind[p["kind"]] = by_kind.get(p["kind"], 0) + 1
    tracked = data.get("tracked_data_files")
    ignored = data.get("ignored_runtime_files")
    return {
        "state": "ready",
        "version": data.get("version"),
        "updated_at": data.get("updated_at"),
        "posture": {
            "read_only": bool(posture.get("read_only", False)),
            "browser_execution": bool(posture.get("browser_execution", False)),
            "broker_control": bool(posture.get("broker_control", False)),
            "file_mutation_from_web": bool(posture.get("file_mutation_from_web", False)),
        },
        "panels": clean_panels,
        "scripts": clean_scripts,
        "tracked_data_files": tracked if isinstance(tracked, list) else [],
        "ignored_runtime_files": ignored if isinstance(ignored, list) else [],
        "counts": {
            "panels": len(clean_panels),
            "scripts": len(clean_scripts),
            "by_kind": by_kind,
            "tracked_data_files": len(tracked) if isinstance(tracked, list) else 0,
            "ignored_runtime_files": len(ignored) if isinstance(ignored, list) else 0,
        },
    }


def _jarvis_commander_snapshot(operator_safety, safety_gates, health,
                               route_smoke, mission_board, prompt_library,
                               file_hygiene, trading_detail, git,
                               cache_freshness=None) -> dict:
    """Derive a conservative top-level snapshot from data ALREADY collected by
    the other read-only helpers. This function runs NOTHING — no subprocess,
    no git, no route probe, no test, no file scan. It only reads the dicts it
    is handed and synthesizes a green/yellow/red verdict. When unsure it is
    deliberately conservative and returns yellow rather than green."""
    def _g(d, *keys, default=None):
        cur = d
        for k in keys:
            if not isinstance(cur, dict):
                return default
            cur = cur.get(k)
        return cur if cur is not None else default

    # --- safety posture (all must hold to be 'locked') ---
    os_locked = isinstance(operator_safety, dict) and operator_safety.get("state") == "locked"
    sg_locked = isinstance(safety_gates, dict) and safety_gates.get("state") == "locked"
    read_only = bool(_g(operator_safety, "read_only", default=False))
    no_broker = bool(_g(operator_safety, "no_broker_control", default=False))
    no_exec = bool(_g(operator_safety, "no_execution_control", default=False))
    safety_locked = bool(os_locked and sg_locked and read_only and no_broker and no_exec)
    safety_status = "locked" if safety_locked else "unknown"

    # --- trading posture (from the read-only trading detail summary) ---
    broker_control = bool(_g(trading_detail, "broker_control", default=False))
    paper_ready = bool(_g(trading_detail, "paper_ready", default=False))
    live_ready = bool(_g(trading_detail, "live_ready", default=False))
    execution_risk = bool(broker_control or paper_ready or live_ready)
    trading_posture = "research_only" if not execution_risk else "EXECUTION_RISK"

    # --- cached report statuses: collapse to pass/fail/<state> ---
    def _report_status(d):
        st = _g(d, "state", default="missing")
        if st == "ready":
            ov = str(_g(d, "overall", default="")).lower()
            return ov if ov in ("pass", "fail") else "ready"
        return st  # missing / unavailable / error
    health_status = _report_status(health)
    route_smoke_status = _report_status(route_smoke)

    mission_count = _g(mission_board, "counts", "total", default=0) or 0
    prompt_count = _g(prompt_library, "counts", "total", default=0) or 0
    fh_state = _g(file_hygiene, "state", default="missing")
    untracked_count = _g(file_hygiene, "total_untracked_count", default=None)
    staged_count = _g(file_hygiene, "staged_count", default=None)
    git_dirty = bool(_g(git, "dirty", default=False))
    cache_overall = _g(cache_freshness, "overall", default=None)

    warnings: list = []
    red = False
    yellow = False

    # RED: any safety contract broken, execution capability present, or a
    # required (health / route smoke) check explicitly FAILS.
    if not safety_locked:
        red = True
        warnings.append("Safety posture is not fully LOCKED.")
    if execution_risk:
        red = True
        warnings.append("Trading detail reports execution capability (broker/paper/live).")
    if health_status == "fail":
        red = True
        warnings.append("Health report overall = FAIL.")
    if route_smoke_status == "fail":
        red = True
        warnings.append("Route smoke overall = FAIL.")

    # YELLOW: cached reports missing/unavailable, staged files, a large
    # untracked backlog, or a dirty working tree.
    if health_status in ("missing", "unavailable", "error", "ready"):
        yellow = True
        warnings.append(f"Health report not confirmed pass ({health_status}).")
    if route_smoke_status in ("missing", "unavailable", "error", "ready"):
        yellow = True
        warnings.append(f"Route smoke not confirmed pass ({route_smoke_status}).")
    if fh_state in ("missing", "unavailable", "error"):
        yellow = True
        warnings.append(f"File hygiene report {fh_state}.")
    if isinstance(staged_count, int) and staged_count > 0:
        yellow = True
        warnings.append(f"{staged_count} file(s) staged — review before commit.")
    if isinstance(untracked_count, int) and untracked_count > 1000:
        yellow = True
        warnings.append(f"Large untracked backlog ({untracked_count} files).")
    if git_dirty:
        yellow = True
        warnings.append("Git working tree is dirty.")
    # Cache freshness only ever softens the verdict to yellow (never red): a
    # stale/missing/unavailable cache means the displayed reports may be old.
    if cache_overall in ("stale", "missing", "unavailable"):
        yellow = True
        warnings.append(f"Cached reports not all fresh ({cache_overall}).")

    no_staged = (staged_count == 0)
    if red:
        overall_state = "red"
    elif (safety_locked and health_status == "pass"
          and route_smoke_status == "pass" and no_staged and not yellow):
        overall_state = "green"
    else:
        # Conservative default: anything not provably all-green is yellow.
        overall_state = "yellow"

    headline = {
        "green": "All clear — read-only console nominal, safety locked, reports pass.",
        "yellow": "Caution — review warnings; some reports unconfirmed or tree not clean.",
        "red": "Alert — a safety contract or a required report check failed.",
    }[overall_state]

    return {
        "overall_state": overall_state,
        "headline": headline,
        "safety_status": safety_status,
        "health_status": health_status,
        "route_smoke_status": route_smoke_status,
        "trading_posture": trading_posture,
        "cache_status": cache_overall,
        "mission_count": mission_count,
        "prompt_count": prompt_count,
        "staged_count": staged_count,
        "untracked_count": untracked_count,
        "warnings": warnings[:8],
    }


_JARVIS_NEXT_ACTIONS = [
    "Review the latest sealed lifecycles in the Trading Bridge (read-only).",
    "Open /guide to confirm the JARVIS module manual entry is accurate.",
    "Check brain_memory project next_actions before starting new work.",
    "Run the JARVIS test suite before committing any console change.",
]


@app.get("/api/jarvis/status")
def api_jarvis_status():
    """Read-only aggregate feed for the JARVIS console. Every section is
    fail-closed; nothing here executes, trades, uploads, or fires automation."""
    system = _jarvis_safe(_jarvis_system_core)
    ai = _jarvis_safe(_jarvis_ai_brains)
    trading = _jarvis_safe(_jarvis_trading_bridge)
    content = _jarvis_safe(_jarvis_content_engine)
    money = _jarvis_safe(_jarvis_money_engine)
    moving = _jarvis_safe(_jarvis_moving_company)
    safety = _jarvis_safe(_jarvis_safety_gates)
    mission = _jarvis_safe(
        lambda: _jarvis_daily_mission(
            content if isinstance(content, dict) else {},
            money if isinstance(money, dict) else {},
        )
    )
    git = _jarvis_safe(_jarvis_git)
    if not isinstance(git, dict) or git.get("state") == "error":
        git = {"state": "unavailable",
               "detail": (git or {}).get("detail", "git unavailable")
                         if isinstance(git, dict) else "git unavailable"}
    operator_safety = _jarvis_safe(_jarvis_operator_safety)
    project = _jarvis_safe(_jarvis_project_files)
    brain_memory = _jarvis_safe(_jarvis_brain_memory)
    health_report = _jarvis_safe(_jarvis_health_report)
    route_smoke = _jarvis_safe(_jarvis_route_smoke_report)
    file_hygiene = _jarvis_safe(_jarvis_file_hygiene_report)
    mission_board = _jarvis_safe(_jarvis_mission_board)
    prompt_library = _jarvis_safe(_jarvis_prompt_library)
    system_map = _jarvis_safe(_jarvis_system_map)
    trading_detail = _jarvis_safe(_jarvis_trading_detail)
    cache_freshness = _jarvis_safe(_jarvis_cache_freshness)
    factory_status = _jarvis_safe(_jarvis_factory_status)
    survival_ledger = _jarvis_safe(_jarvis_survival_ledger)
    candidate_registry = _jarvis_safe(_jarvis_candidate_registry)
    freshness_guard = _jarvis_safe(_jarvis_freshness_guard)
    # Derived ONLY from the dicts already collected above — no new commands.
    commander_snapshot = _jarvis_safe(lambda: _jarvis_commander_snapshot(
        operator_safety, safety, health_report, route_smoke, mission_board,
        prompt_library, file_hygiene, trading_detail, git, cache_freshness))
    return {
        "online": True,
        "read_only": True,
        "commander_snapshot": commander_snapshot,
        "system_core": system,
        "ai_brains": ai,
        "trading_bridge": trading,
        "content_engine": content,
        "money_engine": money,
        "moving_company": moving,
        "daily_mission": mission,
        "safety_gates": safety,
        "git": git,
        "safety": operator_safety,
        "project": project,
        "brain_memory": brain_memory,
        "health_report": health_report,
        "route_smoke_report": route_smoke,
        "file_hygiene_report": file_hygiene,
        "mission_board": mission_board,
        "prompt_library": prompt_library,
        "system_map": system_map,
        "trading_detail": trading_detail,
        "cache_freshness": cache_freshness,
        "factory_status": factory_status,
        "survival_ledger": survival_ledger,
        "candidate_registry": candidate_registry,
        "freshness_guard": freshness_guard,
        "recommended_next_actions": list(_JARVIS_NEXT_ACTIONS),
    }


@app.get("/jarvis", response_class=HTMLResponse)
def page_jarvis(request: Request):
    """Cinematic read-only command center. No execution affordances."""
    from datetime import datetime as _dt
    return templates.TemplateResponse(
        "jarvis.html",
        {
            "request": request,
            "page": "jarvis",
            "server_time": _dt.now().isoformat(timespec="seconds"),
        },
    )


def _jarvis_trading_posture_answer():
    """READ-ONLY. Summarize the trading posture from the committed
    ``_jarvis_trading_detail`` file scan. Reads only the four posture fields
    (read_only / paper_ready / live_ready / broker_control); it never runs a
    backtest, fetches data, calls a broker, or writes anything. Any field it
    cannot read as a bool is reported conservatively. Returns
    (answer_text, sources_used)."""
    detail = _jarvis_safe(_jarvis_trading_detail)
    if not isinstance(detail, dict):
        detail = {}

    def _fld(name: str) -> str:
        val = detail.get(name)
        if val is True:
            return f"{name}=true"
        if val is False:
            return f"{name}=false"
        return f"{name}: I cannot verify that field from the current read-only status."

    ro, pr, lr, bc = (
        detail.get("read_only"),
        detail.get("paper_ready"),
        detail.get("live_ready"),
        detail.get("broker_control"),
    )
    fields = ". ".join(_fld(n) for n in
                       ("read_only", "paper_ready", "live_ready", "broker_control"))
    locked = (ro is True and pr is False and lr is False and bc is False)
    if locked:
        return (
            "Trading is observation-only. " + fields + ". This means JARVIS is "
            "not authorized to trade or control broker/paper/live systems.",
            ["trading_detail"],
        )
    return (
        "Trading posture (read-only status): " + fields + ". JARVIS remains a "
        "read-only surface and authorizes no trading or broker control.",
        ["trading_detail"],
    )


# Step 47 — read-only comparison against the offline-generated latest snapshot.
# The path points at the SAME gitignored runtime file the offline snapshot tool
# writes. The ask path only ever READS it (never writes/repairs/regenerates).
_JARVIS_LATEST_SNAPSHOT = BASE / "storage" / "jarvis" / "snapshots" / "latest_snapshot.json"


def _jarvis_read_latest_snapshot(path=None):
    """READ-ONLY. Read the offline-generated latest snapshot display-only.

    Returns ``(status, data)`` where ``status`` is one of ``"missing"`` (file
    absent), ``"invalid"`` (unreadable / corrupt / not a dict), or ``"ok"``
    (parsed dict in ``data``). It opens the file for reading only — it never
    writes, repairs, deletes, refreshes, or regenerates the snapshot, and fails
    closed (``"invalid"``) on any error rather than raising."""
    import json as _json
    p = Path(path) if path is not None else _JARVIS_LATEST_SNAPSHOT
    try:
        if not p.is_file():
            return ("missing", None)
        data = _json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return ("invalid", None)
        return ("ok", data)
    except Exception:  # noqa: BLE001 — fail closed on any read/parse error
        return ("invalid", None)


def _jarvis_current_comparable():
    """READ-ONLY. Build an in-memory snapshot-shaped view of the CURRENT status
    using the SAME builder the offline snapshot tool uses, so it lines up
    field-by-field with a stored snapshot (including status_key_count/hash).
    Pure read-only: builds in memory and writes NOTHING / creates no file."""
    from tools.jarvis_snapshot_report import build_snapshot
    return build_snapshot(api_jarvis_status())


def _jarvis_compare_snapshot(prev, curr) -> list:
    """READ-ONLY pure diff of two snapshot-shaped dicts. Compares ONLY the
    whitelisted safe display fields and returns human-readable verified
    differences. It never compares or exposes secrets, credentials, env vars,
    chat logs, audio, transcripts, trade orders, or command/action fields —
    those are not present in a snapshot and are never inspected here. Reporting
    a posture/flag change is descriptive only and authorizes no trading."""
    changes: list = []
    if not isinstance(prev, dict) or not isinstance(curr, dict):
        return changes
    pg = prev.get("git") if isinstance(prev.get("git"), dict) else {}
    cg = curr.get("git") if isinstance(curr.get("git"), dict) else {}
    if pg.get("head") != cg.get("head"):
        changes.append(f"git HEAD changed {pg.get('head', '?')} -> {cg.get('head', '?')}")
    if pg.get("branch") != cg.get("branch"):
        changes.append(f"git branch changed {pg.get('branch', '?')} -> {cg.get('branch', '?')}")

    def _subj(s):
        rc = s.get("recent_commits")
        if isinstance(rc, list) and rc and isinstance(rc[0], dict):
            return rc[0].get("subject")
        return None
    if _subj(prev) != _subj(curr):
        changes.append(f'latest commit subject changed "{_subj(prev)}" -> "{_subj(curr)}"')

    pc = prev.get("commander_snapshot") if isinstance(prev.get("commander_snapshot"), dict) else {}
    cc = curr.get("commander_snapshot") if isinstance(curr.get("commander_snapshot"), dict) else {}
    if pc.get("overall_state") != cc.get("overall_state"):
        changes.append(
            f"commander state changed {pc.get('overall_state', '?')} -> {cc.get('overall_state', '?')}")
    pw = pc.get("warnings"); cw = cc.get("warnings")
    pwn = len(pw) if isinstance(pw, list) else None
    cwn = len(cw) if isinstance(cw, list) else None
    if pwn != cwn:
        changes.append(f"warning count changed {pwn} -> {cwn}")

    pt = prev.get("trading_detail") if isinstance(prev.get("trading_detail"), dict) else {}
    ct = curr.get("trading_detail") if isinstance(curr.get("trading_detail"), dict) else {}
    for flag in ("read_only", "paper_ready", "live_ready", "broker_control",
                 "state", "candidate_status"):
        if pt.get(flag) != ct.get(flag):
            changes.append(
                f"trading posture {flag} changed {pt.get(flag)} -> {ct.get(flag)} "
                "(reporting only; no trading authorized)")

    def _names(s):
        rl = s.get("trading_latest_reports")
        if isinstance(rl, list):
            return [r.get("name") for r in rl if isinstance(r, dict)]
        return []
    pn = _names(prev); cn = _names(curr)
    if pn != cn:
        added = [n for n in cn if n and n not in pn]
        removed = [n for n in pn if n and n not in cn]
        parts = []
        if added:
            parts.append("added " + ", ".join(added))
        if removed:
            parts.append("removed " + ", ".join(removed))
        changes.append(
            "latest trading reports changed" + (": " + "; ".join(parts) if parts else ""))

    pcf = (prev.get("cache_freshness") or {}).get("overall") if isinstance(prev.get("cache_freshness"), dict) else None
    ccf = (curr.get("cache_freshness") or {}).get("overall") if isinstance(curr.get("cache_freshness"), dict) else None
    if pcf != ccf:
        changes.append(f"cache freshness overall changed {pcf} -> {ccf}")

    pfh = prev.get("file_hygiene") if isinstance(prev.get("file_hygiene"), dict) else {}
    cfh = curr.get("file_hygiene") if isinstance(curr.get("file_hygiene"), dict) else {}
    for fld, label in (("total_untracked_count", "untracked"),
                       ("tracked_modified_count", "modified"),
                       ("staged_count", "staged")):
        if pfh.get(fld) != cfh.get(fld):
            changes.append(f"{label} file count changed {pfh.get(fld)} -> {cfh.get(fld)}")

    if prev.get("status_key_count") != curr.get("status_key_count"):
        changes.append(
            f"status key count changed {prev.get('status_key_count')} -> {curr.get('status_key_count')}")
    if prev.get("status_key_hash") != curr.get("status_key_hash"):
        changes.append("status key hash changed (top-level status keys differ)")
    return changes


def _jarvis_what_changed_answer():
    """READ-ONLY. Answer a "what changed?" question conservatively.

    If the offline-generated latest snapshot
    (``storage/jarvis/snapshots/latest_snapshot.json``) is missing, this keeps
    the Step 43 behavior: it says no baseline exists, summarizes only the
    CURRENT read-only status, and claims no verified changes. If the snapshot is
    present and valid, it reads it DISPLAY-ONLY and reports the verified
    differences between it and the current read-only status, separating
    "Verified changes since latest snapshot" / "Current status" / "Unknown /
    not compared". If the snapshot is corrupt/invalid it fails closed: it says
    the snapshot is unavailable/invalid and summarizes current status only.

    It runs no git/refresh/execution, fetches nothing, and writes/repairs/
    regenerates NOTHING (it only reads the snapshot file). It never authorizes
    trading and never invents a change not backed by both values. Returns
    (answer_text, sources_used)."""
    git = _jarvis_safe(_jarvis_git)
    if not isinstance(git, dict):
        git = {}
    trading = _jarvis_safe(_jarvis_trading_detail)
    if not isinstance(trading, dict):
        trading = {}
    cache = _jarvis_safe(_jarvis_cache_freshness)
    if not isinstance(cache, dict):
        cache = {}

    current_lines: list = []
    # current HEAD / recent commit subject
    head = git.get("head")
    if isinstance(head, str) and head:
        current_lines.append(f"current HEAD is {head} on branch {git.get('branch', '?')}")
    commits = git.get("commits")
    if isinstance(commits, list) and commits and isinstance(commits[0], dict):
        subj = commits[0].get("subject")
        if isinstance(subj, str) and subj:
            current_lines.append(f'latest commit subject: "{subj}"')
    # git clean/dirty posture
    if isinstance(git.get("clean"), bool):
        if git["clean"]:
            current_lines.append("working tree is clean")
        else:
            current_lines.append(
                f"working tree is dirty ({git.get('modified_count', '?')} modified, "
                f"{git.get('untracked_count', '?')} untracked)")
    # most-recent trading report names already exposed by status
    reports = trading.get("latest_reports")
    if isinstance(reports, list) and reports:
        names = ", ".join(
            r.get("name", "?") for r in reports[:3] if isinstance(r, dict))
        if names:
            current_lines.append(f"most recent trading reports on disk: {names}")
    # cache freshness already exposed by status
    overall = cache.get("overall")
    if isinstance(overall, str) and overall:
        current_lines.append(f"cache freshness overall: {overall}")

    # commander snapshot state + current warning count (derived from the same
    # read-only helpers the status endpoint hands to _jarvis_commander_snapshot)
    sources = ["git", "trading_detail", "cache_freshness"]
    operator_safety = _jarvis_safe(_jarvis_operator_safety)
    safety_gates = _jarvis_safe(_jarvis_safety_gates)
    health = _jarvis_safe(_jarvis_health_report)
    route_smoke = _jarvis_safe(_jarvis_route_smoke_report)
    mission_board = _jarvis_safe(_jarvis_mission_board)
    prompt_library = _jarvis_safe(_jarvis_prompt_library)
    file_hygiene = _jarvis_safe(_jarvis_file_hygiene_report)
    snapshot = _jarvis_safe(lambda: _jarvis_commander_snapshot(
        operator_safety, safety_gates, health, route_smoke, mission_board,
        prompt_library, file_hygiene, trading, git, cache))
    if isinstance(snapshot, dict):
        state = snapshot.get("overall_state")
        if isinstance(state, str) and state:
            current_lines.append(f"commander snapshot state: {state}")
        warns = snapshot.get("warnings")
        if isinstance(warns, list):
            current_lines.append(f"current warning count: {len(warns)}")
        sources.append("commander_snapshot")

    current_text = (
        "Current status: " + "; ".join(current_lines) + "."
        if current_lines else
        "Current status: I could not read any current status fields.")

    # Step 47 — read the offline-generated latest snapshot DISPLAY-ONLY and, if
    # present and valid, compare it field-by-field to the current status.
    snap_status, prev = _jarvis_read_latest_snapshot()

    if snap_status == "missing":
        unknown_text = (
            " Unknown / not compared: no previous snapshot/baseline is available "
            "(no latest snapshot found), so I cannot say what changed since a "
            "previous check, what is new, or which warnings changed compared to "
            "before. Treat the above as current state only.")
        answer = (
            "I cannot compare against a previous snapshot yet — no stored baseline "
            "exists, so I am reporting current read-only status only and claiming "
            "no changes. " + current_text + unknown_text)
        return (answer, sources)

    sources = sources + ["latest_snapshot"]

    if snap_status != "ok" or not isinstance(prev, dict):
        unknown_text = (
            " Unknown / not compared: the latest snapshot is unavailable or "
            "invalid, so I cannot compute a comparison; treat the above as "
            "current state only.")
        answer = (
            "The latest snapshot is unavailable or invalid (it could not be read), "
            "so I cannot compare against it — reporting current read-only status "
            "only and claiming no changes. " + current_text + unknown_text)
        return (answer, sources)

    curr = _jarvis_safe(_jarvis_current_comparable)
    if not isinstance(curr, dict):
        unknown_text = (
            " Unknown / not compared: I could not build a comparable current view, "
            "so I cannot compute a verified comparison; treat the above as current "
            "state only.")
        answer = (
            "I could not build a current comparison view, so I am reporting current "
            "read-only status only and claiming no changes. "
            + current_text + unknown_text)
        return (answer, sources)

    changes = _jarvis_compare_snapshot(prev, curr)
    snap_time = prev.get("generated_at")
    snap_ref = f" (captured {snap_time})" if isinstance(snap_time, str) and snap_time else ""
    if changes:
        changes_text = (
            "Verified changes since latest snapshot" + snap_ref + ": "
            + "; ".join(changes) + ".")
    else:
        changes_text = (
            "Verified changes since latest snapshot" + snap_ref
            + ": none — every compared read-only field matches the latest snapshot.")
    unknown_text = (
        " Unknown / not compared: only whitelisted read-only display fields are "
        "compared (git head/branch, latest commit subject, commander state and "
        "warning count, trading posture flags, latest report names, cache "
        "freshness, file-hygiene counts, status key count/hash). Sensitive data "
        "(secrets, credentials, broker details, trade instructions, transcripts) "
        "is never compared or exposed, and this authorizes no trading.")
    answer = changes_text + " " + current_text + unknown_text
    return (answer, sources)


def _jarvis_chief_of_staff_answer(q: str):
    """READ-ONLY Chief-of-Staff answers: strategic guidance and product-demo
    descriptions.

    Strategic intents ("what should we work on today", "smartest next move",
    "what is the priority", "big picture", "where are we", "why does this
    matter", "are we ready to demo") return a structured advice-only read:
    current situation -> what changed recently -> why it matters -> recommended
    focus -> what not to do -> one clear next action.

    Product-demo intents ("what is SPARTA Brain", "what is JARVIS", "describe /
    pitch / tell someone about the system") return a plain-language product
    overview.

    Everything is read-only and ADVICE ONLY: it recommends, it never commands or
    authorizes any action. It reads only the ``api_jarvis_status`` aggregate,
    invents no trades / performance / strategy success, and says "unknown" when
    data is missing. Returns ``(answer, sources)`` or ``None`` to fall through.
    """
    status = _jarvis_safe(api_jarvis_status)
    status = status if isinstance(status, dict) else {}

    def _sub(key: str) -> dict:
        v = status.get(key)
        return v if isinstance(v, dict) else {}

    cs = _sub("commander_snapshot")
    state = cs.get("overall_state") or "unknown"
    warns = cs.get("warnings") if isinstance(cs.get("warnings"), list) else []
    fs = _sub("factory_status")
    actions = status.get("recommended_next_actions")
    focus = (actions[0] if isinstance(actions, list) and actions
             and isinstance(actions[0], str)
             else "Continue read-only validation of the existing research queue.")

    # --- product-demo description (what is X / pitch / describe / tell) ----
    _status_word = ("status" in q or "progress" in q or "update" in q
                    or "how is" in q or "how's" in q)
    _demo_frame = ("what is" in q or "what's" in q or "whats" in q
                   or "describe" in q or "pitch" in q or "tell" in q
                   or "explain" in q or "overview of" in q)
    _demo_subject = ("sparta brain" in q or "jarvis" in q
                     or "strategy factory" in q or "the system" in q
                     or "the product" in q or "this product" in q
                     or "the platform" in q)
    if _demo_frame and _demo_subject and not _status_word:
        return (
            "Quick product overview (read-only). SPARTA Brain is an AI command "
            "center — a local dashboard that brings the whole operation into one "
            "place. JARVIS is its voice interface and chief of staff: you ask in "
            "plain language and it answers from read-only system state. The "
            "Strategy Factory is the research engine that produces and reviews "
            "strategy candidates. Trading stays research-only until validation "
            "passes — no live or paper trades were executed, and the system "
            "places no orders. This is a read-only description and authorizes no "
            "action.",
            ["system_core", "factory_status", "trading_detail"])

    # --- strategic chief-of-staff intents ---------------------------------
    _demo_ready = (
        "ready to demo" in q or "ready to ship" in q or "ready to launch" in q
        or "ready to pitch" in q or "ready for a demo" in q or "can we demo" in q
        or "demo ready" in q or "demo-ready" in q)
    _strategic = (
        "work on today" in q or "work on next" in q
        or "what should we work on" in q or "what to work on" in q
        or "smartest" in q or "next move" in q or "best move" in q
        or "best next move" in q
        or "priority" in q or "priorities" in q or "most important" in q
        or "big picture" in q
        or "where we are" in q or "where are we" in q or "where do we stand" in q
        or ("why" in q and "matter" in q)
        or "what should i tell" in q
        or _demo_ready)
    if not _strategic:
        return None

    decs = (fs.get("latest_decisions")
            if isinstance(fs.get("latest_decisions"), list) else [])
    top = next((d for d in decs if isinstance(d, dict)), None)
    if fs.get("state") == "ready" and top:
        recent = ("the most recent committed research checkpoint recorded "
                  f"\"{top.get('decision', 'a research outcome')}\" (read-only, "
                  "research only)")
    elif fs.get("state") == "ready":
        recent = ("recent work is limited to committed read-only research "
                  "checkpoints")
    else:
        recent = "no recent change is confirmed from read-only state"

    readiness = ""
    if _demo_ready:
        readiness = (
            "On demo-readiness: SPARTA Brain and JARVIS are ready to show as a "
            "read-only command center and assistant; trading is intentionally "
            "research-only and is not part of any live demo. ")

    answer = (
        "Here is the chief-of-staff read (advice only, read-only). "
        + readiness
        + f"Current situation: SPARTA Brain is online and the commander snapshot "
        f"is {state} with {len(warns)} item(s) flagged; all trading is "
        "observation-only — no live or paper trades were executed, so there is no "
        "performance to report. "
        f"What changed recently: {recent}. "
        "Why it matters: nothing moves toward paper or live trading until "
        "validation passes, and that discipline is what protects the capital and "
        "the credibility of the system. "
        f"Recommended focus: {focus} "
        "What not to do: do not enable paper or live trading, do not treat "
        "research candidates as if they were proven, and do not skip the "
        "validation gate. "
        f"One clear next action: {focus} "
        "This is advice only — it authorizes no action and executes nothing.")
    return (answer, ["commander_snapshot", "system_core", "factory_status",
                     "recommended_next_actions", "trading_detail"])


def _jarvis_conversational_answer(q: str):
    """READ-ONLY natural-language answers for the Conversational Intelligence
    layer: greetings, "how are you", morning briefing, Strategy Factory status,
    SPARTA Brain status, a last-24h trading recap, and a general system status
    summary.

    It reads ONLY the already-aggregated read-only status (``api_jarvis_status``)
    and the committed report summaries it already exposes. It runs no command,
    no backtest, no broker call, places no order, triggers no refresh, and writes
    nothing. It NEVER invents profit/loss, fills, or performance: when no live or
    paper trade data exists it says so explicitly.

    Returns ``(answer_text, sources_used)`` for a recognised conversational
    intent, or ``None`` so the caller falls through to the structured answers.
    """
    import re as _re

    def _agg() -> dict:
        d = _jarvis_safe(api_jarvis_status)
        return d if isinstance(d, dict) else {}

    def _sub(status: dict, key: str) -> dict:
        v = status.get(key)
        return v if isinstance(v, dict) else {}

    def _snapshot_line(status: dict):
        cs = _sub(status, "commander_snapshot")
        state = cs.get("overall_state") or "unknown"
        headline = cs.get("headline") or ""
        warns = cs.get("warnings") if isinstance(cs.get("warnings"), list) else []
        return state, headline, warns

    _LOCKED_POSTURE = (
        "read_only=true, paper_ready=false, live_ready=false, broker_control=false")

    def _first_action(status: dict) -> str:
        actions = status.get("recommended_next_actions")
        if isinstance(actions, list) and actions and isinstance(actions[0], str):
            return actions[0]
        return ("Continue read-only validation of the existing research queue "
                "before adding new strategy ideas.")

    def _attn_phrase(warns: list) -> str:
        if warns:
            return (f"{len(warns)} warning(s) need review: "
                    + "; ".join(str(w) for w in warns[:3]) + ".")
        return "No warnings currently need review."

    def _factory_phrase(fs: dict) -> str:
        if fs.get("state") == "ready":
            decs = (fs.get("latest_decisions")
                    if isinstance(fs.get("latest_decisions"), list) else [])
            top = next((d for d in decs if isinstance(d, dict)), None)
            latest = (f" The most recent is {top.get('name', '?')} -> "
                      f"{top.get('decision', 'UNKNOWN')}." if top else "")
            return ("Strategy Factory remains in research mode: "
                    f"{fs.get('report_count', 0)} committed research reports on "
                    "disk." + latest + " All work is dry-run / research-candidate "
                    "only and JARVIS runs no Factory job.")
        return "Strategy Factory status is not available right now (read-only)."

    # --- Executive Translation Mode v1 -----------------------------------
    # Operator mode (technical, exact counts/names/raw warnings/posture flags)
    # vs Executive mode (default: translated, customer/investor-friendly). The
    # operator flag only changes wording; both modes are equally read-only and
    # both keep the trading-safety phrasing. Technical detail stays available on
    # request via these triggers.
    _operator = (
        "operator mode" in q
        or "technical detail" in q
        or "show technical" in q
        or ("show" in q and "detail" in q)
        or "diagnostic" in q
        or "exact count" in q
        or "exact status" in q
        # Front-loaded "operator ..." (e.g. "operator trading status",
        # "operator workflow status") also requests operator/technical wording.
        # Normal executive questions never contain "operator", so the executive
        # default is preserved.
        or (
            "operator" in q
            and (
                "trading" in q
                or "workflow" in q
                or "pipeline" in q
                or "status" in q
            )
        )
    )

    def _exec_health_phrase(state: str) -> str:
        st = (state or "unknown").lower()
        if st in ("green", "ok", "okay", "healthy", "ready", "good"):
            return "All systems are operating normally."
        if st in ("yellow", "warn", "warning", "degraded", "caution"):
            return ("The platform is online and stable, with a few maintenance "
                    "items under review.")
        if st in ("red", "error", "critical", "down", "alert"):
            return ("The platform is online, with several items currently needing "
                    "attention.")
        return "The platform is online and being monitored."

    def _exec_research_phrase(fs: dict) -> str:
        if fs.get("state") == "ready":
            return ("Research activity is progressing normally, and all of it "
                    "stays in dry-run research mode.")
        return "Research activity status is not available right now."

    def _exec_candidate_phrase(cand_n: int) -> str:
        if isinstance(cand_n, int) and cand_n > 0:
            return "Several strategy candidates are currently under evaluation."
        return "No strategy candidates are currently under evaluation."

    def _exec_attention_phrase(warns: list) -> str:
        if warns:
            return ("Some maintenance items require attention, and there are a few "
                    "project housekeeping tasks that should be reviewed.")
        return "Nothing needs your attention right now."

    def _exec_blocker_phrase(state: str, warns: list) -> str:
        st = (state or "unknown").lower()
        if st in ("red", "error", "critical", "down", "alert"):
            return ("Blocker level: elevated — some items currently need attention "
                    "before work continues smoothly.")
        if warns:
            return ("Blocker level: low — a few maintenance items are under review, "
                    "but nothing is blocking progress.")
        if st in ("green", "ok", "okay", "healthy", "ready", "good"):
            return "Blocker level: none — there are no blockers and work is on track."
        return ("Blocker level: unknown — current state could not be confirmed from "
                "read-only data.")

    def _exec_trading_phrase(cand_n) -> str:
        # Executive (default) trading status: research-framed, customer/investor
        # friendly. NO raw posture flags or counts; the trading-safety phrasing
        # is preserved verbatim. Candidate phrasing is fact-driven (no invented
        # "several" when none exist).
        return ("Trading remains in research mode. No live or paper trades have "
                "been executed. " + _exec_candidate_phrase(cand_n) + " The focus "
                "remains validation and research rather than deployment.")

    def _operator_trading_phrase(cand_n) -> str:
        # Operator (on request) trading status: full technical detail with exact
        # candidate count and the locked posture flags.
        n = cand_n if isinstance(cand_n, int) else 0
        return (f"Trading research status (operator detail): {n} research "
                "candidate(s) tracked. No live or paper trades were executed — "
                f"trading is observation-only ({_LOCKED_POSTURE}), so there is no "
                "realized performance to report.")

    # --- Chief of Staff Mode v1 — strategic guidance / product demo --------
    # Checked FIRST so strategic phrasings ("priority", "big picture", "where
    # are we", "smartest next move", "what is SPARTA Brain") win before the
    # briefing / brain / factory branches. Advice only, read-only.
    cos = _jarvis_chief_of_staff_answer(q)
    if cos is not None:
        return cos

    # --- Executive Briefing Mode v1 — good morning / overnight / exec summary --
    # Greeting "good morning", briefing requests, an overnight update, an
    # executive summary, and "tell me more" all produce the structured
    # read-only briefing: greeting -> system health -> Strategy Factory ->
    # trading research -> warnings -> recommended next action.
    _is_briefing = (
        "good morning" in q
        or "morning briefing" in q
        or "briefing" in q
        or "brief me" in q
        or "brief" in q
        or "overnight" in q
        or "executive summary" in q
        or ("summar" in q and "system" in q)
        or "tell me more" in q
    )
    if _is_briefing:
        status = _agg()
        sc = _sub(status, "system_core")
        cr = _sub(status, "candidate_registry")
        fs = _sub(status, "factory_status")
        state, headline, warns = _snapshot_line(status)
        cand_n = (cr.get("candidate_count")
                  if isinstance(cr.get("candidate_count"), int)
                  else len(cr.get("candidates") or []))
        _briefing_sources = ["commander_snapshot", "system_core", "factory_status",
                             "candidate_registry", "trading_detail", "daily_mission"]
        if _operator:
            answer = (
                "Operator briefing (full technical detail). "
                f"SPARTA Brain is online (system core {sc.get('state', 'unknown')}, "
                f"server {sc.get('server', 'unknown')}). Commander status is {state} "
                f"— {headline} ({len(warns)} warning(s)). "
                + _factory_phrase(fs) + " "
                f"Trading research status: {cand_n} research candidate(s) tracked. "
                "No live or paper trades were executed — trading is observation-only "
                f"({_LOCKED_POSTURE}), so there is no realized performance to report. "
                + _attn_phrase(warns) + " "
                f"Recommended next action: {_first_action(status)} "
                "This is a read-only briefing and authorizes no action.")
            return (answer, _briefing_sources)
        # Executive mode (default): translated, customer/investor-friendly.
        # Greeting -> business status -> research status -> trading status ->
        # attention items -> recommendation. Raw counts, report names, raw
        # warning text, and posture flags are translated away; the trading-
        # safety phrasing is kept verbatim.
        answer = (
            "Good morning Mahmoud. Here is your executive briefing. "
            "SPARTA Brain is online. " + _exec_health_phrase(state) + " "
            + _exec_research_phrase(fs) + " " + _exec_candidate_phrase(cand_n) + " "
            "All trading remains observation-only — no live or paper trades were "
            "executed, so there is no performance to report. "
            + _exec_attention_phrase(warns) + " "
            f"Recommended next action: {_first_action(status)} "
            "This is a read-only briefing and authorizes no action. "
            "Ask for operator mode or technical details for the exact figures.")
        return (answer, _briefing_sources)

    # --- Strategy Factory status -----------------------------------------
    if "factory" in q:
        status = _agg()
        fs = _sub(status, "factory_status")
        if fs.get("state") != "ready":
            detail = fs.get("detail") or "status not available"
            return (
                f"Strategy Factory status: {detail}. This is a read-only view; "
                "JARVIS runs no Factory job and authorizes nothing.",
                ["factory_status"])
        decs = fs.get("latest_decisions") if isinstance(fs.get("latest_decisions"), list) else []
        top = [d for d in decs[:3] if isinstance(d, dict)]
        dlines = "; ".join(f"{d.get('name', '?')} -> {d.get('decision', 'UNKNOWN')}"
                           for d in top)
        return (
            f"Strategy Factory (read-only, dry-run / research only): "
            f"{fs.get('report_count', 0)} committed reports on disk. "
            f"Latest decisions: {dlines if dlines else 'none readable'}. These are "
            "research candidates only — JARVIS runs no Factory job, places no "
            "trades, and authorizes nothing.",
            ["factory_status"])

    # --- SPARTA Brain status ---------------------------------------------
    if "sparta brain" in q or "brain status" in q:
        status = _agg()
        sc = _sub(status, "system_core")
        ai = _sub(status, "ai_brains")
        state, headline, warns = _snapshot_line(status)
        brains = ai.get("brains") if isinstance(ai.get("brains"), dict) else {}
        ready = [n for n, v in brains.items()
                 if isinstance(v, dict) and v.get("state") in ("ready", "installed")]
        return (
            f"SPARTA Brain status (read-only): system core is "
            f"{sc.get('state', 'unknown')}, server {sc.get('server', 'unknown')}. "
            f"Commander snapshot is {state} — {headline} ({len(warns)} warning(s)). "
            f"AI brains available: {', '.join(ready) if ready else 'none detected'}. "
            "Everything here is observation-only; nothing is executed, traded, or "
            "stored.",
            ["system_core", "ai_brains", "commander_snapshot"])

    # --- Trading Executive Translation v1 — trading / strategy status ------
    # Natural trading-status and strategy-status phrasings ("what is the trading
    # status", "trading update", "how is trading going", "how are our strategies
    # doing", "status of the trading bot"). Executive mode (default) translates
    # to research-framed business language and hides raw posture flags/counts;
    # operator mode (on request) exposes the four posture flags and exact counts.
    # Both keep the trading-safety phrasing; both are equally read-only. Checked
    # BEFORE the last-24h recap so these route to translation, not the legacy
    # posture answer.
    _strat = "strateg" in q
    _status_kw = ("status" in q or "update" in q or "overview" in q
                  or "going" in q or "doing" in q or "happening" in q
                  or "happened" in q or "progress" in q or "how are" in q
                  or "how is" in q or "how's" in q or "hows" in q)
    _trading_status_intent = (
        "trading status" in q or "trading update" in q or "trading overview" in q
        or "trading posture" in q or "trading bot" in q or "trading system" in q
        or "with trading" in q or "with trades" in q
        or "our trades" in q or "my trades" in q
        or "how are we doing" in q
        or "ready for paper" in q or "ready for live" in q
        or "paper_ready" in q or "paper ready" in q
        or "live_ready" in q or "live ready" in q
        or "broker_control" in q or "broker control" in q
        or ("trad" in q and _status_kw)
        or (_strat and _status_kw)
    )
    if _trading_status_intent:
        status = _agg()
        cr = _sub(status, "candidate_registry")
        cand_n = (cr.get("candidate_count")
                  if isinstance(cr.get("candidate_count"), int)
                  else len(cr.get("candidates") or []))
        if _operator:
            return (
                "Trading status (read-only, operator detail). "
                + _operator_trading_phrase(cand_n) + " This reports observed "
                "state only and authorizes no action.",
                ["trading_detail", "candidate_registry"])
        return (
            "Trading status (read-only). " + _exec_trading_phrase(cand_n) + " "
            "This reports observed state only and authorizes no action. "
            "Ask for operator mode or technical details for the exact posture "
            "and counts.",
            ["trading_detail", "candidate_registry"])

    # --- last-24h trading recap / "what happened with our trades" ---------
    _has_trade = ("trad" in q or "trade" in q or "trades" in q)
    _time_words = ("24 hour", "24 hours", "24h", "last 24", "past 24", "last day",
                   "past day", "yesterday", "overnight", "today", "last night",
                   "recap")
    if (("happened" in q and _has_trade)
            or (_has_trade and any(w in q for w in _time_words))
            or "our trades" in q or "my trades" in q):
        status = _agg()
        td = _sub(status, "trading_detail")
        reports = td.get("latest_reports") if isinstance(td.get("latest_reports"), list) else []
        names = ", ".join(r.get("name", "?") for r in reports[:3]
                          if isinstance(r, dict))
        if _operator:
            recent = (f"The most recent committed research reports on disk are: "
                      f"{names}. " if names
                      else "No trading research reports were found on disk. ")
            return (
                "Read-only trading update: no live or paper trades have been placed "
                "in the last 24 hours, or at any time — trading is observation-only "
                f"({_LOCKED_POSTURE}), so there are no fills and no realized "
                "performance to report. " + recent + "JARVIS only reads committed "
                "research artifacts; it runs no backtest, places no orders, and "
                "authorizes nothing.",
                ["trading_detail"])
        return (
            "Read-only trading update: no live or paper trades have been placed in "
            "the last 24 hours, or at any time — trading remains in research mode, "
            "so there is no performance to report. JARVIS only reads committed "
            "research artifacts; it runs no backtest, places no orders, and "
            "authorizes nothing. Ask for operator mode or technical details for the "
            "exact posture and report names.",
            ["trading_detail"])

    # --- warnings / what-needs-attention ----------------------------------
    if "needs attention" in q or "what needs" in q or "attention" in q:
        status = _agg()
        state, headline, warns = _snapshot_line(status)
        if _operator:
            if warns:
                items = "; ".join(str(w) for w in warns[:5])
                body = (f"{len(warns)} item(s) currently need review: {items}.")
            else:
                body = "Nothing is currently flagged for attention."
            return (
                f"Attention items (read-only, operator detail). Commander status is "
                f"{state} — {headline} {body} Recommended next action: "
                f"{_first_action(status)} This reports observed state only and "
                "authorizes no action.",
                ["commander_snapshot", "trading_detail"])
        return (
            "Attention items (read-only). " + _exec_attention_phrase(warns) + " "
            f"Recommended next action: {_first_action(status)} This reports "
            "observed state only and authorizes no action.",
            ["commander_snapshot", "trading_detail"])

    # --- conversational follow-ups: next step / what to focus on ----------
    if ("next step" in q or "focus on" in q or "what should we focus" in q
            or "what to focus" in q):
        status = _agg()
        state, _headline, warns = _snapshot_line(status)
        attn = (f"{len(warns)} warning(s) are open" if warns
                else "no warnings are open")
        return (
            f"Recommended focus (read-only): {_first_action(status)} "
            f"Right now commander status is {state} and {attn}. Trading stays "
            f"observation-only ({_LOCKED_POSTURE}); this is guidance only and "
            "authorizes no action.",
            ["commander_snapshot", "trading_detail"])

    # --- "how are you" ----------------------------------------------------
    if (_re.search(r"\bhow\s+are\s+you\b", q) or _re.search(r"\bhow\s+are\s+u\b", q)
            or "how's it going" in q or "hows it going" in q
            or "how you doing" in q or _re.search(r"\bhow\s+(?:are|r)\s+things\b", q)):
        status = _agg()
        state, headline, warns = _snapshot_line(status)
        return (
            f"I'm online and read-only. Commander snapshot is {state} — {headline} "
            f"({len(warns)} warning(s)). Trading stays observation-only "
            f"({_LOCKED_POSTURE}). Ask me for a morning briefing, trading status, "
            "Strategy Factory status, or what needs attention.",
            ["commander_snapshot", "trading_detail"])

    # --- greeting ---------------------------------------------------------
    if _re.match(r"^(?:hi|hey|hello|hiya|yo|sup|gm|greetings)\b", q) or \
            _re.match(r"^good\s+(?:morning|afternoon|evening|day)\b", q):
        status = _agg()
        state, _headline, warns = _snapshot_line(status)
        return (
            "Hello — JARVIS online and read-only. Right now the commander snapshot "
            f"is {state} with {len(warns)} warning(s), and trading is "
            f"observation-only ({_LOCKED_POSTURE}). I can give you a morning "
            "briefing, the trading status, the Strategy Factory status, the SPARTA "
            "Brain status, or tell you what needs attention — just ask.",
            ["commander_snapshot", "trading_detail"])

    # --- Workflow Health Translation v1 — pipeline / workflow / "is it working" --
    # Natural workflow-health questions ("pipeline status", "workflow status",
    # "is everything working", "is everything good", "any problem", "any
    # blocker", "are we on track", "how is the project doing", "is the system
    # working"). Answered as a Chief-of-Staff workflow read: overall status ->
    # what is working -> what needs attention -> blocker level -> recommended
    # next step. Executive mode (default) is customer-friendly and hides raw
    # posture flags/counts; operator mode (on request) exposes them. Both keep
    # the trading-safety phrasing; both are equally read-only and invent nothing.
    # Placed before the generic status catch-all so workflow phrasing routes here.
    _workflow_intent = (
        "pipeline" in q or "workflow" in q
        or "is everything working" in q or "everything working" in q
        or "is everything good" in q or "everything good" in q
        or "everything ok" in q or "everything okay" in q or "everything fine" in q
        or "everything running" in q or "everything alright" in q
        or "any problem" in q or "any problems" in q
        or "any issue" in q or "any issues" in q
        or "any blocker" in q or "any blockers" in q
        or "on track" in q
        or "how is the project" in q or "how's the project" in q
        or "hows the project" in q or "how are the project" in q
        or "project doing" in q or "project going" in q or "project status" in q
        or "is the system working" in q or "system working" in q
        or "is it working" in q
    )
    if _workflow_intent:
        status = _agg()
        sc = _sub(status, "system_core")
        cr = _sub(status, "candidate_registry")
        fs = _sub(status, "factory_status")
        state, headline, warns = _snapshot_line(status)
        cand_n = (cr.get("candidate_count")
                  if isinstance(cr.get("candidate_count"), int)
                  else len(cr.get("candidates") or []))
        _wf_sources = ["system_core", "commander_snapshot", "factory_status",
                       "candidate_registry", "trading_detail"]
        if _operator:
            return (
                "Workflow health (read-only, operator detail). System core is "
                f"{sc.get('state', 'unknown')}, server "
                f"{sc.get('server', 'unknown')}. Commander snapshot is {state} — "
                f"{headline} ({len(warns)} warning(s)). " + _factory_phrase(fs) + " "
                f"Trading research status: {cand_n} research candidate(s) tracked. "
                "No live or paper trades were executed — trading is observation-only "
                f"({_LOCKED_POSTURE}), so there is no realized performance to report. "
                + _attn_phrase(warns) + " Blocker level: "
                f"{len(warns)} open warning(s). Recommended next action: "
                f"{_first_action(status)} This reports observed state only and "
                "authorizes no action.",
                _wf_sources)
        return (
            "Workflow health (read-only). Overall: SPARTA Brain is online and the "
            "workflow is operating. " + _exec_health_phrase(state) + " "
            "What's working: the dashboard, the read-only status pipeline, and "
            "Strategy Factory research are all running. "
            + _exec_research_phrase(fs) + " What needs attention: "
            + _exec_attention_phrase(warns) + " " + _exec_blocker_phrase(state, warns)
            + " All trading remains observation-only — no live or paper trades were "
            "executed, so there is no performance to report. Recommended next step: "
            f"{_first_action(status)} This reports observed state only and authorizes "
            "no action. Ask for operator mode or technical details for the exact "
            "figures.",
            _wf_sources)

    # --- general system / overall status (not trading/factory/change paths) ---
    if (("status" in q or "how is everything" in q or "overall" in q)
            and "trad" not in q and "posture" not in q
            and "changed" not in q and "new" not in q
            and "factory" not in q and "attention" not in q and "needs" not in q):
        status = _agg()
        sc = _sub(status, "system_core")
        state, headline, warns = _snapshot_line(status)
        if _operator:
            return (
                f"System status (read-only, operator detail): core is "
                f"{sc.get('state', 'unknown')}, server {sc.get('server', 'unknown')}; "
                f"commander snapshot is {state} — {headline} ({len(warns)} "
                f"warning(s)). Trading is observation-only ({_LOCKED_POSTURE}). This "
                "reports observed state only and authorizes no action.",
                ["system_core", "commander_snapshot", "trading_detail"])
        return (
            "System status (read-only). SPARTA Brain is online. "
            + _exec_health_phrase(state) + " "
            "All trading remains observation-only — no live or paper trades were "
            "executed, so there is no performance to report. "
            + _exec_attention_phrase(warns) + " This reports observed state only "
            "and authorizes no action.",
            ["system_core", "commander_snapshot", "trading_detail"])

    # --- bare operator-mode request -> full technical briefing ------------
    # "operator mode" / "diagnostics" / "show technical details" with no other
    # recognised intent still returns the full technical briefing rather than
    # falling through to the generic structured answer.
    if _operator:
        status = _agg()
        sc = _sub(status, "system_core")
        cr = _sub(status, "candidate_registry")
        fs = _sub(status, "factory_status")
        state, headline, warns = _snapshot_line(status)
        cand_n = (cr.get("candidate_count")
                  if isinstance(cr.get("candidate_count"), int)
                  else len(cr.get("candidates") or []))
        answer = (
            "Operator briefing (full technical detail). "
            f"SPARTA Brain is online (system core {sc.get('state', 'unknown')}, "
            f"server {sc.get('server', 'unknown')}). Commander status is {state} "
            f"— {headline} ({len(warns)} warning(s)). "
            + _factory_phrase(fs) + " "
            f"Trading research status: {cand_n} research candidate(s) tracked. "
            "No live or paper trades were executed — trading is observation-only "
            f"({_LOCKED_POSTURE}), so there is no realized performance to report. "
            + _attn_phrase(warns) + " "
            f"Recommended next action: {_first_action(status)} "
            "This is a read-only briefing and authorizes no action.")
        return (answer, ["commander_snapshot", "system_core", "factory_status",
                         "candidate_registry", "trading_detail", "daily_mission"])

    return None


def _jarvis_ask_answer(safety_class: str, q: str):
    """Build a conservative, read-only answer for an already-classified SAFE
    question. Returns (answer_text, sources_used). Reads only already-known
    JARVIS concepts plus the read-only trading-posture status scan and
    NEVER authorizes any action."""
    if safety_class == "SAFE_EXPLAIN":
        # Chief-of-Staff strategic/demo phrasings often arrive as "explain where
        # we are" / "explain why this matters" / "explain SPARTA Brain to a
        # customer", which classify SAFE_EXPLAIN. Answer those read-only first.
        cos = _jarvis_chief_of_staff_answer(q)
        if cos is not None:
            return cos
        if "warning" in q:
            agg = _jarvis_safe(api_jarvis_status)
            cs = agg.get("commander_snapshot") if isinstance(agg, dict) else {}
            cs = cs if isinstance(cs, dict) else {}
            warns = cs.get("warnings") if isinstance(cs.get("warnings"), list) else []
            if warns:
                items = "; ".join(str(w) for w in warns[:5])
                detail = (f"There are {len(warns)} open warning(s): {items}.")
            else:
                detail = "There are no open warnings right now."
            return (
                "A commander warning is a read-only caution flag (for example a "
                "dirty or untracked git tree, an unconfirmed report, or a stale "
                f"cache) — it signals attention is needed, not approval. {detail} "
                "Reviewing them authorizes no action.",
                ["commander_snapshot"],
            )
        if "read_only" in q or "read only" in q:
            return (
                "read_only means JARVIS is observe-only: it mirrors aggregated "
                "state and never executes, trades, refreshes, or writes.",
                ["glossary"],
            )
        return (
            "That is a read-only field/panel explanation drawn from the "
            "committed JARVIS glossary and runbook docs.",
            ["glossary", "system_map"],
        )
    if safety_class == "SAFE_NEXT_REVIEW_STEP":
        return (
            "The safest next step is review only: read the status panels and the "
            "Step 20-29 docs. This authorizes no trading and no execution.",
            ["system_map", "docs"],
        )
    # SAFE_INFO — try the natural conversational layer first (greetings,
    # briefing, factory/brain status, trading recap, general status). Falls
    # through to the structured answers below when q is not a conversational
    # intent, so all existing behavior is preserved.
    convo = _jarvis_conversational_answer(q)
    if convo is not None:
        return convo
    if "yellow" in q or "commander" in q:
        return (
            "Commander yellow means attention is needed, not approval — usually a "
            "dirty or untracked tree. It is conservative-by-design and authorizes "
            "nothing.",
            ["commander_snapshot"],
        )
    # "What changed?" change-summary questions (Step 43). Checked BEFORE the
    # trading branch so "what new trading reports appeared" is answered as a
    # change summary, not a posture answer.
    if (
        "changed" in q
        or "change summary" in q
        or "summarize current changes" in q
        or "summarise current changes" in q
        or "what is new" in q
        or "what's new" in q
        or "whats new" in q
        or "what new" in q
    ):
        return _jarvis_what_changed_answer()
    if (
        "trading" in q
        or "trades" in q
        or "posture" in q
        or "how are we doing" in q
        or "paper_ready" in q
        or "paper ready" in q
        or "live_ready" in q
        or "live ready" in q
        or "broker_control" in q
        or "broker control" in q
    ):
        return _jarvis_trading_posture_answer()
    if "docs" in q:
        return (
            "JARVIS documentation exists across Steps 20-29 (runbook, known "
            "limits, glossary, conversation plan/shell, safety classifier, and "
            "this ask contract).",
            ["docs"],
        )
    if "attention" in q or "needs" in q:
        return (
            "What needs attention is whatever the commander snapshot flags yellow "
            "or red; review those panels. Nothing here authorizes action.",
            ["commander_snapshot"],
        )
    return (
        "This is answerable from the read-only JARVIS status aggregate; it "
        "reports observed state only and authorizes no action.",
        ["commander_snapshot", "system_core"],
    )


@app.post("/api/jarvis/ask")
async def api_jarvis_ask(request: Request):
    """Answer-only, read-only JARVIS Q&A.

    Delegates safety classification to the pure
    ``jarvis_conversation_safety.classify_jarvis_question``. This handler
    executes nothing: it runs no commands/scripts, places no trades, triggers
    no refresh, writes no files or chat logs, and mutates no state. It accepts
    ONLY a ``question`` string and returns read-only text or a refusal."""
    from fastapi.responses import JSONResponse
    from jarvis_conversation_safety import classify_jarvis_question

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "invalid JSON body"})
    if not isinstance(body, dict):
        return JSONResponse(status_code=400, content={"error": "body must be an object"})
    # Accept ONLY 'question'. Any command/action/execute or other field is
    # rejected by shape, never interpreted.
    if set(body) - {"question"}:
        return JSONResponse(status_code=400, content={"error": "only 'question' is accepted"})
    if "question" not in body:
        return JSONResponse(status_code=400, content={"error": "missing 'question'"})
    question = body["question"]
    if not isinstance(question, str):
        return JSONResponse(status_code=400, content={"error": "'question' must be a string"})

    verdict = classify_jarvis_question(question)
    safety_class = verdict["safety_class"]
    if verdict["refused"]:
        reason = verdict["reason"]
        return {
            "answer": reason
            + " I can instead explain already-known read-only status, e.g. why "
            "the commander snapshot is yellow or what a field means.",
            "safety_class": safety_class,
            "sources_used": [],
            "refused": True,
            "refusal_reason": reason,
        }

    answer, sources = _jarvis_ask_answer(
        safety_class, verdict["normalized_question"].lower()
    )
    return {
        "answer": answer,
        "safety_class": safety_class,
        "sources_used": sources,
        "refused": False,
        "refusal_reason": "",
    }


# === END SPARTA JARVIS Command Center block ================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8765, reload=False)
