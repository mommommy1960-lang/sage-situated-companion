from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from .engine import LiveEnsembleEngine
from .models import LiveEvent
from .providers import DemoProvider, OllamaProvider

APP_DIR = Path(__file__).resolve().parent
PROVIDER = os.getenv("LIVECAST_PROVIDER", "demo").lower()
provider = OllamaProvider() if PROVIDER == "ollama" else DemoProvider()
engine = LiveEnsembleEngine(
    provider=provider,
    like_threshold=int(os.getenv("LIVECAST_LIKE_THRESHOLD", "100")),
)

app = FastAPI(title="Commons Live Ensemble", version="0.1.0")
subscribers: set[asyncio.Queue[dict[str, Any]]] = set()


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


async def broadcast(message: dict[str, Any]) -> None:
    dead = []
    for queue in subscribers:
        try:
            queue.put_nowait(message)
        except asyncio.QueueFull:
            dead.append(queue)
    for queue in dead:
        subscribers.discard(queue)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "provider": PROVIDER,
        "personas": sorted(engine.personas),
        "subscribers": len(subscribers),
    }


@app.get("/")
async def overlay() -> FileResponse:
    return FileResponse(APP_DIR / "overlay.html")


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
                    yield f"data: {json.dumps(item, ensure_ascii=False)}\\n\\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\\n\\n"
        finally:
            subscribers.discard(queue)

    return StreamingResponse(event_source(), media_type="text/event-stream")
