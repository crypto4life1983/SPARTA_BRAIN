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
    "llama3.1:8b":  "FREE local",
    "llama3":       "FREE local",
    "mistral:7b":   "FREE local",
    "qwen2.5:7b":   "FREE local",
    "qwen2.5:14b":  "FREE local",
    "gpt-4o-mini":  "LOW cost",
    "gpt-4.1-mini": "MEDIUM cost",
    "gpt-4o":       "HIGH quality / higher cost",
    "gpt-4.1":      "HIGH quality / higher cost",
}

# Universal local fallback when a task setting is empty/missing.
SAFE_LOCAL_FALLBACK = "llama3"


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
    return JSONResponse(status_code=503, content={"error": str(e)})


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
    if req.key == "ai_mode" and req.value not in ("free", "balanced", "premium"):
        raise HTTPException(400, "ai_mode must be free, balanced, or premium")
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
    return {"ok": True}


# ============================================================
# Smart Model Router - status + safe-defaults endpoints
# ============================================================

@app.get("/api/router/status")
def api_router_status():
    """Snapshot of the live model routing decisions. Always reads DB
    fresh - this is the source of truth the UI panels render."""
    ai_mode = (db.get_setting("ai_mode") or "balanced").lower()
    tasks = {}
    for t in TASK_KEYS:
        model = get_task_model(t)
        paid = is_paid_model(model)
        tasks[t] = {
            "model": model,
            "is_paid": paid,
            "provider": "openai" if paid else "ollama",
            "tier_label": MODEL_TIERS.get(model, "unknown"),
        }
    return {"ai_mode": ai_mode, "tasks": tasks}


@app.post("/api/router/apply-free-safe-defaults")
def api_apply_free_safe_defaults():
    """One-shot reset: ai_mode=free + every task model -> llama3 +
    quality_mode=local_only. The bullet-proof 'no surprises' button."""
    db.set_setting("ai_mode", "free")
    db.set_setting("quality_mode", "local_only")
    for task in TASK_KEYS:
        db.set_setting(f"{task}_model", SAFE_LOCAL_FALLBACK)
    return {
        "ok": True,
        "applied": "free_safe_defaults",
        "ai_mode": "free",
        "task_model": SAFE_LOCAL_FALLBACK,
    }


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8765, reload=False)
