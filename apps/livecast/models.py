from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any


class EventType(str, Enum):
    COMMENT = "comment"
    GIFT = "gift"
    LIKE = "like"
    FOLLOW = "follow"
    SHARE = "share"
    JOIN = "join"
    BATTLE = "battle"
    PET_MOTION = "pet_motion"
    MANUAL = "manual"


@dataclass(slots=True)
class LiveEvent:
    type: EventType
    user: str = "viewer"
    text: str = ""
    gift_name: str = ""
    gift_count: int = 0
    coins: int = 0
    likes: int = 0
    total_likes: int = 0
    meta: dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "LiveEvent":
        raw_type = str(payload.get("type", "manual")).strip().lower()
        try:
            event_type = EventType(raw_type)
        except ValueError:
            event_type = EventType.MANUAL
        return cls(
            type=event_type,
            user=str(payload.get("user") or "viewer")[:80],
            text=str(payload.get("text") or "")[:500],
            gift_name=str(payload.get("gift_name") or "")[:120],
            gift_count=max(0, int(payload.get("gift_count") or 0)),
            coins=max(0, int(payload.get("coins") or 0)),
            likes=max(0, int(payload.get("likes") or 0)),
            total_likes=max(0, int(payload.get("total_likes") or 0)),
            meta=dict(payload.get("meta") or {}),
        )


@dataclass(slots=True)
class Persona:
    key: str
    display_name: str
    role: str
    voice_hint: str
    public_prompt: str
    accent: str = "gold"


@dataclass(slots=True)
class StageCue:
    persona: str
    text: str
    animation: str = "speak"
    priority: int = 10
    speak: bool = True
    meta: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "persona": self.persona,
            "text": self.text,
            "animation": self.animation,
            "priority": self.priority,
            "speak": self.speak,
            "meta": self.meta,
        }
