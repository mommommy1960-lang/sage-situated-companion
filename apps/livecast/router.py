from __future__ import annotations

from dataclasses import dataclass

from .models import EventType, LiveEvent


@dataclass(slots=True)
class Route:
    persona: str
    intent: str
    priority: int
    animation: str = "speak"


class EnsembleRouter:
    """Turns audience events into show directions."""

    COMMANDS = {
        "!sage": "sage",
        "!aurora": "aurora",
        "!maya": "maya",
        "!serafina": "serafina",
        "!snake": "serafina",
    }

    def __init__(self, like_threshold: int = 100) -> None:
        self.like_threshold = max(10, like_threshold)
        self._last_like_bucket = 0

    def route(self, event: LiveEvent) -> Route | None:
        text = event.text.strip()
        if event.type == EventType.COMMENT:
            low = text.lower()
            for command, persona in self.COMMANDS.items():
                if low.startswith(command):
                    return Route(persona, "direct-question", 30, "spotlight")
            if any(word in low for word in ("snake", "serafina", "python")):
                return Route("serafina", "pet-chat", 15, "snake")
            return Route("sage", "general-chat", 10, "speak")

        if event.type == EventType.GIFT:
            name = event.gift_name.lower()
            # Viewer support changes the stage, not an animal or physical system.
            if "heart me" in name:
                return Route("maya", "fan-club-welcome", 60, "heart")
            if event.coins >= 500:
                return Route("aurora", "vip-gift", 100, "aurora")
            if event.coins >= 100:
                return Route("sage", "major-gift", 80, "crown")
            return Route("sage", "small-gift", 70, "rose")

        if event.type == EventType.FOLLOW:
            return Route("sage", "follow", 35, "follow")
        if event.type == EventType.SHARE:
            return Route("maya", "share", 25, "share")
        if event.type == EventType.PET_MOTION:
            return Route("serafina", "pet-motion", 20, "snake")

        if event.type == EventType.LIKE:
            bucket = event.total_likes // self.like_threshold
            if bucket > self._last_like_bucket:
                self._last_like_bucket = bucket
                return Route("sage", "like-milestone", 20, "hearts")
        return None
