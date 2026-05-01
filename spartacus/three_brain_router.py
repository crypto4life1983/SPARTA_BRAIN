"""
Three-Brain Auto Router
=======================
SPARTA_BRAIN can delegate tasks to three AI "brains":

  CLAUDE  — default brain; handles writing, strategy, ideation, general Q&A,
             and anything not better suited to the other two.

  GEMINI  — multimodal / long-context brain; best for video files, audio,
             PDFs, screenshots, frame analysis, OCR, and documents too large
             for a standard context window.

  CODEX   — adversarial code-review brain; best for bug hunts, security
             audits, refactors, failed tests, second opinions on code, and
             any situation where Claude appears stuck or self-consistent in a
             wrong answer.

The router inspects the task text (and optionally attached filenames) for
keyword signals and picks the best brain automatically.  It also exposes a
"rescue" heuristic: if Claude has failed the same task more than once, it
recommends escalating to Codex for a fresh adversarial pass.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path


def _cmd(args: list) -> list:
    """On Windows, wrap args with cmd /c so .CMD shims execute correctly."""
    if sys.platform == "win32":
        return ["cmd", "/c"] + args
    return args

# ---------------------------------------------------------------------------
# Keyword tables
# ---------------------------------------------------------------------------

_GEMINI_KEYWORDS = [
    "video", "mp4", "mkv", "mov", "avi",
    "audio", "mp3", "wav", "flac",
    "pdf", "transcript",
    "visual overlay", "frame analysis",
    "long document", "long context",
    "screenshot", "image analysis", "ocr",
]

_CODEX_KEYWORDS = [
    "code review", "review this",
    "bug", "security", "refactor",
    "failed test", "unit test",
    "error", "hallucination",
    "stuck", "second opinion",
    "adversarial", "audit", "vulnerability",
    "lint", "syntax error", "debug",
]


# ---------------------------------------------------------------------------
# 1. detect_available_tools
# ---------------------------------------------------------------------------

def detect_available_tools() -> dict:
    """Probe the environment for Codex and Gemini CLIs."""

    result = {
        "claude": {"available": True, "note": "always available"},
        "codex":  {"available": False, "version": None, "note": ""},
        "gemini": {"available": False, "version": None, "note": ""},
    }

    for tool in ("codex", "gemini"):
        if shutil.which(tool) is None:
            result[tool]["note"] = f"{tool} not found on PATH"
            continue
        try:
            proc = subprocess.run(
                _cmd([tool, "--version"]),
                capture_output=True, text=True, timeout=5,
            )
            version_line = (proc.stdout or proc.stderr or "").strip().splitlines()
            version = version_line[0] if version_line else None
            result[tool]["available"] = True
            result[tool]["version"] = version
            result[tool]["note"] = f"{tool} detected"
        except subprocess.TimeoutExpired:
            result[tool]["note"] = f"{tool} --version timed out"
        except (FileNotFoundError, OSError):
            result[tool]["note"] = f"{tool} found on PATH but not executable"
        except Exception as exc:
            result[tool]["note"] = f"{tool} probe failed: {exc}"

    return result


# ---------------------------------------------------------------------------
# 2. route_task
# ---------------------------------------------------------------------------

def route_task(task_text: str, attached_files=None) -> dict:
    """Classify which brain should handle *task_text*."""

    corpus = task_text.lower()
    if attached_files:
        for f in attached_files:
            corpus += " " + Path(f).name.lower()

    # Check Gemini first (multimodal / long-context signals)
    for kw in _GEMINI_KEYWORDS:
        if kw in corpus:
            tools = detect_available_tools()
            available = tools["gemini"]["available"]
            return {
                "brain": "GEMINI",
                "reason": f"Keyword '{kw}' signals multimodal or long-context work.",
                "available": available,
                "install_hint": (
                    None if available
                    else "Install the Gemini CLI: https://ai.google.dev/gemini-api/docs/gemini-cli"
                ),
            }

    # Check Codex (adversarial / code-review signals)
    for kw in _CODEX_KEYWORDS:
        if kw in corpus:
            tools = detect_available_tools()
            available = tools["codex"]["available"]
            return {
                "brain": "CODEX",
                "reason": f"Keyword '{kw}' signals a code-review or adversarial task.",
                "available": available,
                "install_hint": (
                    None if available
                    else "Install Codex CLI: npm install -g @openai/codex"
                ),
            }

    # Default: Claude
    return {
        "brain": "CLAUDE",
        "reason": "No multimodal or code-review signals detected; Claude handles this.",
        "available": True,
        "install_hint": None,
    }


# ---------------------------------------------------------------------------
# 3. explain_route
# ---------------------------------------------------------------------------

def explain_route(task_text: str) -> str:
    """Return a plain-English sentence explaining the routing decision."""

    decision = route_task(task_text)
    brain = decision["brain"]
    reason = decision["reason"]

    if not decision["available"]:
        hint = decision.get("install_hint", "")
        return (
            f"I would route this to {brain}, but it is not installed. "
            f"{reason}  Hint: {hint}"
        )

    brain_descriptions = {
        "GEMINI": "Gemini (multimodal / long-context brain)",
        "CODEX":  "Codex (adversarial code-review brain)",
        "CLAUDE": "Claude (default general-purpose brain)",
    }
    label = brain_descriptions.get(brain, brain)
    return f"This task will be handled by {label}.  {reason}"


# ---------------------------------------------------------------------------
# 4. should_rescue
# ---------------------------------------------------------------------------

def should_rescue(failure_count: int, repeated_error: bool = False) -> dict:
    """Recommend escalation to Codex based on prior failure count."""

    if failure_count >= 2 or (failure_count >= 1 and repeated_error):
        return {
            "recommend": "CODEX",
            "level": "required",
            "message": (
                "Claude has failed this task multiple times or is stuck in a "
                "repeated error loop.  Escalating to Codex for an adversarial "
                "review is required to break the cycle."
            ),
        }

    if failure_count == 1 and not repeated_error:
        return {
            "recommend": "CODEX",
            "level": "suggested",
            "message": (
                "Claude failed once.  Running a Codex review is suggested to "
                "catch any blind spots before retrying."
            ),
        }

    return {
        "recommend": None,
        "level": "none",
        "message": "All good.",
    }


# ---------------------------------------------------------------------------
# 5. run_codex_review
# ---------------------------------------------------------------------------

_CODEX_NOT_INSTALLED = (
    "Codex CLI not found or not executable.  "
    "Install it with:  npm install -g @openai/codex  then run: codex login"
)
_GEMINI_NOT_INSTALLED = (
    "Gemini CLI not found or not executable.  "
    "Install it from: https://ai.google.dev/gemini-api/docs/gemini-cli  then run: gemini"
)


def _probe_cli(tool: str) -> bool:
    """Return True only when the tool is actually executable (not just on PATH)."""
    if shutil.which(tool) is None:
        return False
    try:
        subprocess.run(_cmd([tool, "--version"]), capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, OSError):
        return False
    except subprocess.TimeoutExpired:
        return True  # slow start but present


def run_codex_review(prompt: str, target_files=None) -> dict:
    """Run `codex \"<prompt>\"` and return its output."""

    if not _probe_cli("codex"):
        return {"ok": False, "output": "", "error": _CODEX_NOT_INSTALLED}

    args = ["codex", prompt]
    if target_files:
        args.extend(str(f) for f in target_files)

    try:
        proc = subprocess.run(_cmd(args), capture_output=True, text=True, timeout=120)
        output = proc.stdout or ""
        if proc.returncode != 0:
            return {"ok": False, "output": output, "error": proc.stderr or "Non-zero exit"}
        return {"ok": True, "output": output, "error": None}
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "", "error": "codex timed out after 120 s"}
    except (FileNotFoundError, OSError):
        return {"ok": False, "output": "", "error": _CODEX_NOT_INSTALLED}
    except Exception as exc:
        return {"ok": False, "output": "", "error": str(exc)}


# ---------------------------------------------------------------------------
# 6. run_gemini_analysis
# ---------------------------------------------------------------------------

def _get_gemini_env() -> dict:
    """Return an env dict with GEMINI_API_KEY set, reading from Windows registry as fallback."""
    import os
    env = os.environ.copy()
    if not env.get("GEMINI_API_KEY") and sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                key_val, _ = winreg.QueryValueEx(k, "GEMINI_API_KEY")
                env["GEMINI_API_KEY"] = key_val
        except (FileNotFoundError, OSError):
            pass
    return env


def run_gemini_analysis(prompt: str, target_files=None) -> dict:
    """Run `gemini \"<prompt>\"` and return its output."""

    if not _probe_cli("gemini"):
        return {"ok": False, "output": "", "error": _GEMINI_NOT_INSTALLED}

    env = _get_gemini_env()
    if not env.get("GEMINI_API_KEY"):
        return {
            "ok": False, "output": "",
            "error": 'Gemini auth missing — run: setx GEMINI_API_KEY "your-key-here" then restart SPARTA server',
        }

    args = ["gemini", prompt]
    if target_files:
        args.extend(str(f) for f in target_files)

    try:
        proc = subprocess.run(_cmd(args), capture_output=True, text=True, timeout=120, env=env)
        output = proc.stdout or ""
        if proc.returncode != 0:
            return {"ok": False, "output": output, "error": proc.stderr or "Non-zero exit"}
        return {"ok": True, "output": output, "error": None}
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "", "error": "gemini timed out after 120 s"}
    except (FileNotFoundError, OSError):
        return {"ok": False, "output": "", "error": _GEMINI_NOT_INSTALLED}
    except Exception as exc:
        return {"ok": False, "output": "", "error": str(exc)}
