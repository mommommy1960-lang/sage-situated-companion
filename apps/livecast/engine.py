from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from .models import LiveEvent, Persona, StageCue
from .moderation import Moderator
from .providers import DemoProvider, TextProvider
from .router import EnsembleRouter


class LiveEnsembleEngine:
    def __init__(
        self,
        provider: TextProvider | None = None,
        persona_path: str | Path | None = None,
        like_threshold: int = 100,
    ) -> None:
        self.provider = provider or DemoProvider()
        self.moderator = Moderator()
        self.router = EnsembleRouter(like_threshold=like_threshold)
        path = Path(persona_path or Path(__file__).with_name("personas.json"))
        raw = json.loads(path.read_text(encoding="utf-8"))
        self.personas = {
            key: Persona(
                key=key,
                display_name=value["display_name"],
                role=value["role"],
                voice_hint=value["voice_hint"],
                public_prompt=value["public_prompt"],
                accent=value.get("accent", "gold"),
            )
            for key, value in raw.items()
        }
        self.history: deque[str] = deque(maxlen=18)

    def process(self, event: LiveEvent) -> StageCue | None:
        if event.type.value == "comment":
            event.text = self.moderator.clean(event.text)
            allowed, _reason = self.moderator.allow(event.user, event.text)
            if not allowed:
                return None

        route = self.router.route(event)
        if route is None:
            return None

        persona = self.personas[route.persona]
        context = "\n".join(self.history)
        try:
            text = self.provider.reply(persona, event, context)
        except Exception:
            # Fail soft: the show stays up if the model provider goes down.
            text = DemoProvider().reply(persona, event, context)

        if not text:
            return None
        self.history.append(f"{persona.display_name} to {event.user}: {text}")
        return StageCue(
            persona=persona.display_name,
            text=text,
            animation=route.animation,
            priority=route.priority,
            meta={
                "persona_key": persona.key,
                "accent": persona.accent,
                "source_event": event.type.value,
                "user": event.user,
            },
        )
