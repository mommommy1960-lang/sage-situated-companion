from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from .engine import LiveEnsembleEngine
from .models import LiveEvent
from .providers import DemoProvider, OllamaProvider

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent.parent
PROVIDER = os.getenv("LIVECAST_PROVIDER", "demo").lower()
provider = OllamaProvider() if PROVIDER == "ollama" else DemoProvider()
engine = LiveEnsembleEngine(
    provider=provider,
    like_threshold=int(os.getenv("LIVECAST_LIKE_THRESHOLD", "100")),
)

app = FastAPI(title="Commons Live Ensemble", version="0.2.0")
subscribers: set[asyncio.Queue[dict[str, Any]]] = set()
tiktok_process: subprocess.Popen | None = None


class EventBody(BaseModel):
    type: str = "manual"
    user: str = "viewer"
    text: str = ""
    gift_name: str = ""
    gift_count: int = 0
    coins: int = 0
    likes: int = 0
    total_likes: int = 0
    meta: dict[str, Any] = Field(default_factory=dict)


class TikTokStartBody(BaseModel):
    username: str


async def broadcast(message: dict[str, Any]) -> None:
    dead = []
    for queue in subscribers:
        try:
            queue.put_nowait(message)
        except asyncio.QueueFull:
            dead.append(queue)
    for queue in dead:
        subscribers.discard(queue)


def _tiktok_running() -> bool:
    return tiktok_process is not None and tiktok_process.poll() is None


def _clean_username(value: str) -> str:
    value = value.strip()
    if value.startswith("@"):
        value = value[1:]
    if not re.fullmatch(r"[A-Za-z0-9._]{1,64}", value):
        raise ValueError("Enter a valid TikTok username, with or without @.")
    return value


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "provider": PROVIDER,
        "personas": sorted(engine.personas),
        "subscribers": len(subscribers),
        "tiktok_listener": _tiktok_running(),
    }


@app.get("/")
async def overlay() -> FileResponse:
    return FileResponse(APP_DIR / "overlay.html")


@app.get("/control")
async def control() -> FileResponse:
    return FileResponse(APP_DIR / "control.html")


@app.get("/control/status")
async def control_status() -> dict[str, Any]:
    return {
        "ok": True,
        "provider": PROVIDER,
        "tiktok_listener": _tiktok_running(),
        "overlay_url": "http://127.0.0.1:8765/",
    }


@app.post("/control/tiktok/start")
async def start_tiktok(body: TikTokStartBody) -> JSONResponse:
    global tiktok_process
    if _tiktok_running():
        return JSONResponse({"ok": True, "running": True, "message": "TikTok listener is already running."})

    try:
        username = _clean_username(body.username)
    except ValueError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)

    try:
        tiktok_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "apps.livecast.tiktok_direct",
                f"@{username}",
                "--server",
                "http://127.0.0.1:8765",
            ],
            cwd=str(REPO_ROOT),
        )
    except Exception as exc:
        tiktok_process = None
        return JSONResponse(
            {
                "ok": False,
                "error": f"Could not start TikTok listener: {exc}",
                "hint": "Make sure TikTokLive is installed from apps/livecast/requirements.txt.",
            },
            status_code=500,
        )

    return JSONResponse(
        {
            "ok": True,
            "running": True,
            "username": f"@{username}",
            "message": "TikTok listener started. Go LIVE on TikTok, then comments/gifts/likes can enter the ensemble.",
        }
    )


@app.post("/control/tiktok/stop")
async def stop_tiktok() -> JSONResponse:
    global tiktok_process
    if not _tiktok_running():
        tiktok_process = None
        return JSONResponse({"ok": True, "running": False, "message": "TikTok listener is already stopped."})

    assert tiktok_process is not None
    tiktok_process.terminate()
    try:
        tiktok_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        tiktok_process.kill()
    tiktok_process = None
    return JSONResponse({"ok": True, "running": False, "message": "TikTok listener stopped."})


@app.post("/event")
async def ingest(body: EventBody) -> JSONResponse:
    event = LiveEvent.from_dict(body.model_dump())
    cue = await asyncio.to_thread(engine.process, event)
    if cue is None:
        return JSONResponse({"accepted": True, "cue": None})
    payload = cue.as_dict()
    await broadcast(payload)
    return JSONResponse({"accepted": True, "cue": payload})


@app.get("/stream")
async def stream(request: Request) -> StreamingResponse:
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=50)
    subscribers.add(queue)

    async def event_source():
        try:
            yield "event: hello\ndata: {}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            subscribers.discard(queue)

    return StreamingResponse(event_source(), media_type="text/event-stream")


@app.on_event("shutdown")
async def shutdown_listener() -> None:
    global tiktok_process
    if _tiktok_running() and tiktok_process is not None:
        tiktok_process.terminate()
        tiktok_process = None
