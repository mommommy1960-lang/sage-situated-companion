"""
SAGE Situated Companion
Persistent Context Engine

Maintains the companion's rolling understanding of the user's
current situation across events and conversations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ContextSnapshot:
    location: str | None = None
    activity: str | None = None
    conversation_topic: str | None = None
    interrupted_topic: str | None = None
    route_instruction: str | None = None
    route_distance_ft: int | None = None
    visible_objects: list[str] = field(default_factory=list)
    safety_level: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ContextEngine:
    """
    Maintains rolling situated context.

    Each event updates only the relevant portion of state so Sage
    retains continuity across time instead of rebuilding context
    from scratch for every interaction.
    """

    def __init__(self):
        self.state = ContextSnapshot()

    def apply_event(
        self,
        *,
        event_type: str,
        payload: dict[str, Any],
    ) -> ContextSnapshot:

        if event_type == "location":
            self.state.location = payload.get("location")

        elif event_type == "activity":
            self.state.activity = payload.get("activity")

        elif event_type == "conversation":
            topic = payload.get("topic")

            if topic:
                self.state.conversation_topic = topic

        elif event_type == "conversation_interrupted":
            self.state.interrupted_topic = (
                payload.get("topic")
                or self.state.conversation_topic
            )

        elif event_type == "conversation_resumed":
            if self.state.interrupted_topic:
                self.state.conversation_topic = (
                    self.state.interrupted_topic
                )

            self.state.interrupted_topic = None

        elif event_type == "navigation":
            self.state.route_instruction = payload.get(
                "instruction"
            )
            self.state.route_distance_ft = payload.get(
                "distance_ft"
            )

        elif event_type == "vision":
            objects = payload.get("objects", [])

            if isinstance(objects, list):
                self.state.visible_objects = objects

        elif event_type == "safety":
            self.state.safety_level = self._clamp(
                payload.get("severity", 0.0)
            )

        metadata = payload.get("metadata")

        if isinstance(metadata, dict):
            self.state.metadata.update(metadata)

        self.state.updated_at = datetime.now(timezone.utc)

        return self.state

    def snapshot(self) -> ContextSnapshot:
        return self.state

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))
