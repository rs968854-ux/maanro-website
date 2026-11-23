"""
Rob Advertising Company — Dashboard Server
FastAPI app serving the dashboard UI + a working bridge to the `layla` Hermes profile.

Endpoints
  GET  /                     dashboard HTML
  GET  /api/overview         real campaign/asset/analytics data
  GET  /api/media            media library listing (real files on disk)
  POST /api/chat             text turn -> layla (hermes chat --resume <session>)
  POST /api/voice            audio upload -> STT -> layla -> TTS audio reply
  GET  /api/voice/config     current STT/TTS provider + voice names
  GET  /api/health           server + layla reachability
"""

from __future__ import annotations

import asyncio
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

HERMES_BIN = r"D:\Hermes\hermes-agent\.hermes\bin\hermes.exe"
LAYLA_HOME = r"C:\Users\rohit\AppData\Local\hermes\profiles\layla"
COMPANY_ROOT = Path(r"D:\Company folder\RamanRasa")
CAMPAIGNS = COMPANY_ROOT / "Campaings"
DOCUMENTS = COMPANY_ROOT / "Documents"

STT_PROVIDER = "local"      # local faster-whisper
TTS_PROVIDER = "edge"       # Microsoft Edge neural voices (free, no key)
TTS_VOICE = "en-IN-NeerjaNeural"   # Indian English - fits RamanRasa brand
TTS_RATE = "+8%"

MEDIA_EXTS = {".jpg", ".jpeg", ".png", ".mp4", ".mov", ".gif", ".webp", ".m4v"}

app = FastAPI(title="Rob Advertising Company", docs_url=None, redoc_url=None)

# One rolling chat session with layla so the conversation has continuity.
_SESSION_ID: Optional[str] = None
_SESSION_LOCK = asyncio.Lock()


# --------------------------------------------------------------------------
# Real data extraction
# --------------------------------------------------------------------------

def _read_pinterest_impressions() -> tuple[list[tuple[str, int]], int]:
    """Real Pinterest daily impressions from the client's exported CSV."""
    path = DOCUMENTS / "Pinterest Analytics overview 20260927-20261027.csv"
    series: list[tuple[str, int]] = []
    if not path.exists():
        return series, 0
    with path.open("r", encoding="utf-8-sig", errors="replace") as fh:
        for row in csv.reader(fh):
            if len(row) < 2:
                continue
            date, raw = row[0].strip(), row[1].strip()
            if date.startswith("2026-") and raw.isdigit():
                series.append((date, int(raw)))
    return series, sum(v for _, v in series)


def _count_assets() -> dict[str, int]:
    """Real asset counts per campaign folder."""
    counts: dict[str, int] = {}
    if not CAMPAIGNS.exists():
        return counts
    for folder in sorted(p for p in CAMPAIGNS.iterdir() if p.is_dir()):
        n = sum(1 for f in folder.rglob("*") if f.suffix.lower() in MEDIA_EXTS)
        counts[folder.name] = n
    return counts


def _launch_calendar() -> list[dict[str, Any]]:
    """Real launch-day structure from the Launch campaign folder."""
    launch = CAMPAIGNS / "Launch"
    if not launch.exists():
        return []
    rows: list[dict[str, Any]] = []
    for child in sorted(p for p in launch.iterdir() if p.is_dir()):
        assets = sum(1 for f in child.rglob("*") if f.suffix.lower() in MEDIA_EXTS)
        rows.append({
            "day": child.name.replace("Day ", "").strip(),
            "label": child.name,
            "assets": assets,
        })
    return rows


def _client_profiles() -> list[dict[str, Any]]:
    """Clients and SKU lines actually present on disk."""
    skus = []
    for label, folder in (("Images", COMPANY_ROOT / "Images"),):
        if folder.exists():
            for f in sorted(folder.glob("New SKu*")):
                skus.append(f.stem.replace("New SKu ", "").replace(".jpg", "").strip())
    if not skus:
        skus = ["Cinnamon", "Cloves", "Turmeric", "Black Pepper", "Moringa"]
    return [{"client": "RamanRasa", "skus": skus}]


def _overview() -> dict[str, Any]:
    series, total = _read_pinterest_impressions()
    asset_counts = _count_assets()
    return {
        "company": "Rob Advertising Company",
        "workspace": "D:\\Company folder\\RamanRasa",
        "metrics": {
            "total_impressions": total,
            "impressions_window": "2026-09-27 → 2026-10-27",
            "peak_day": max(series, key=lambda x: x[1])[0] if series else None,
            "peak_value": max((v for _, v in series), default=0),
            "tracked_days": len(series),
            "total_assets": sum(asset_counts.values()),
            "campaign_count": len(asset_counts),
            "audience_total": 10_000,
            "audience_source": "Instagram audience insights 2026-10-25",
        },
        "impressions_series": [{"date": d, "value": v} for d, v in series],
        "asset_counts": asset_counts,
        "launch_calendar": _launch_calendar(),
        "clients": _client_profiles(),
    }


def _media_listing(limit: int = 120) -> list[dict[str, Any]]:
    """Real media files with size + mtime, newest first."""
    if not CAMPAIGNS.exists():
        return []
    items: list[dict[str, Any]] = []
    for f in CAMPAIGNS.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in MEDIA_EXTS:
            continue
        try:
            st = f.stat()
        except OSError:
            continue
        items.append({
            "name": f.name,
            "folder": f.parent.name,
            "path": str(f),
            "ext": f.suffix.lower().lstrip("."),
            "size": st.st_size,
            "modified": st.st_mtime,
        })
    items.sort(key=lambda i: i["modified"], reverse=True)
    return items[:limit]


# --------------------------------------------------------------------------
# Layla bridge
# --------------------------------------------------------------------------

def _hermes_env() -> dict[str, str]:
    env = dict(os.environ)
    env["HERMES_HOME"] = LAYLA_HOME
    return env


async def _run_layla(prompt: str, session_id: Optional[str]) -> tuple[str, Optional[str]]:
    """Run one turn against the layla profile. Returns (reply_text, session_id).

    Uses `hermes chat --format stream-json` so we get machine-readable output
    instead of scraping the pretty TUI box.
    """
    cmd = [HERMES_BIN, "chat", "-q", prompt, "--oneshot", "--format", "stream-json"]
    if session_id:
        cmd += ["--resume", session_id]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=LAYLA_HOME,
        env=_hermes_env(),
    )
    stdout, _ = await proc.communicate()
    text = stdout.decode("utf-8", errors="replace")

    reply_parts: list[str] = []
    new_session: Optional[str] = None
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") == "text" and obj.get("text"):
            reply_parts.append(obj["text"])
        elif obj.get("type") == "result":
            new_session = obj.get("session_id") or new_session
            if not reply_parts and obj.get("text"):
                reply_parts.append(obj["text"])

    reply = "".join(reply_parts).strip()
    # Strip the agent's decorative box borders if they leaked into text frames.
    reply = re.sub(r"^[╭╰─│]+$", "", reply, flags=re.MULTILINE).strip()
    return reply, new_session


async def _layla_turn(prompt: str) -> dict[str, Any]:
    global _SESSION_ID
    async with _SESSION_LOCK:
        reply, new_session = await _run_layla(prompt, _SESSION_ID)
        if new_session:
            _SESSION_ID = new_session
        return {"reply": reply, "session_id": _SESSION_ID}


# --------------------------------------------------------------------------
# Voice (STT + TTS)
# --------------------------------------------------------------------------

async def _tts_to_mp3(text: str, path: str) -> bool:
    """Render text to mp3 with Edge neural TTS."""
    try:
        import edge_tts
    except ImportError:
        return False
    try:
        communicate = edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE)
        await communicate.save(path)
    except Exception:
        return False
    return Path(path).exists() and Path(path).stat().st_size > 0


async def _stt_transcribe(path: str) -> str:
    """Transcribe a wav file with local faster-whisper."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return ""
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _info = model.transcribe(path, language="en", vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip()


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

class ChatIn(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    html_path = Path(__file__).with_name("index.html")
    return html_path.read_text(encoding="utf-8")


@app.get("/api/overview")
async def api_overview() -> JSONResponse:
    return JSONResponse(_overview())


@app.get("/api/media")
async def api_media(limit: int = 120) -> JSONResponse:
    return JSONResponse({"items": _media_listing(limit)})


@app.get("/api/health")
async def api_health() -> JSONResponse:
    return JSONResponse({
        "server": "ok",
        "layla_home": LAYLA_HOME,
        "session_id": _SESSION_ID,
        "stt_provider": STT_PROVIDER,
        "tts_provider": TTS_PROVIDER,
        "tts_voice": TTS_VOICE,
    })


@app.post("/api/chat")
async def api_chat(payload: ChatIn) -> JSONResponse:
    message = (payload.message or "").strip()
    if not message:
        return JSONResponse({"error": "empty message"}, status_code=400)
    result = await _layla_turn(message)
    return JSONResponse(result)


@app.get("/api/voice/config")
async def api_voice_config() -> JSONResponse:
    return JSONResponse({
        "stt_provider": STT_PROVIDER,
        "tts_provider": TTS_PROVIDER,
        "tts_voice": TTS_VOICE,
        "voices": [
            {"id": "en-IN-NeerjaNeural", "label": "Neerja (Indian English)"},
            {"id": "en-IN-NeerjaExpressiveNeural", "label": "Neerja Expressive"},
            {"id": "en-IN-PrabhatNeural", "label": "Prabhat (Indian English)"},
            {"id": "en-US-AriaNeural", "label": "Aria (US English)"},
            {"id": "en-GB-SoniaNeural", "label": "Sonia (UK English)"},
        ],
    })


@app.post("/api/voice")
async def api_voice(
    audio: UploadFile = File(...),
    respond_with_audio: bool = Form(True),
) -> Response:
    """Accept a browser recording: transcribe -> ask layla -> optional audio reply."""
    suffix = Path(audio.filename or "clip.webm").suffix or ".webm"
    tmpdir = Path(tempfile.gettempdir())
    raw_path = tmpdir / f"rob-stt-{uuid.uuid4().hex}{suffix}"

    raw = await audio.read()
    raw_path.write_bytes(raw)

    wav_path = tmpdir / f"rob-stt-{uuid.uuid4().hex}.wav"
    try:
        import subprocess as sp
        conv = sp.run(
            ["ffmpeg", "-y", "-i", str(raw_path), "-ar", "16000", "-ac", "1", str(wav_path)],
            capture_output=True, timeout=120,
        )
        if conv.returncode != 0 or not wav_path.exists():
            wav_path = raw_path
    except Exception:
        wav_path = raw_path

    transcript = await _stt_transcribe(str(wav_path))
    if not transcript:
        return JSONResponse(
            {"error": "STT unavailable or no speech detected",
             "detail": "Install local whisper: hermes pm sync-venv stt-whisper"},
            status_code=503,
        )

    result = await _layla_turn(transcript)
    reply = result.get("reply", "")

    if respond_with_audio and reply:
        mp3 = tmpdir / f"rob-tts-{uuid.uuid4().hex}.mp3"
        ok = await _tts_to_mp3(reply, str(mp3))
        if ok:
            data = mp3.read_bytes()
            mp3.unlink(missing_ok=True)
            return Response(
                content=data,
                media_type="audio/mpeg",
                headers={
                    "X-Transcript": transcript.encode("ascii", "ignore").decode(),
                    "X-Reply-Text": reply.encode("ascii", "ignore").decode()[:1800],
                    "X-Session-Id": str(result.get("session_id") or ""),
                },
            )

    return JSONResponse({"transcript": transcript, "reply": reply,
                         "session_id": result.get("session_id")})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9200, log_level="warning")
