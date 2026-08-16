"""
SAGE Situated Companion
Core Runtime Orchestrator

The runtime coordinates perception, situated context,
memory, intervention decisions, personality continuity,
and hardware interfaces.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .context import ContextEngine
from .intervention import InterventionEngine
from .memory import MemoryStore


@dataclass
class SituatedEvent:
    source: str
    event_type: str
    payload: dict[str, Any]
    confidence: float = 1.0
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class CompanionState:
    location: str | None = None
    activity: str | None = None
    conversation_topic: str | None = None
    interrupted_topic: str | None = None
    safety_level: float = 0.0
    last_event: SituatedEvent | None = None


class SageRuntime:
    """
    Central event-processing runtime for the Sage situated companion.

    Sensor and software events enter here and are transformed into
    persistent situated state before intervention logic determines
    whether Sage should remain silent, respond, or proactively interrupt.

    Significant situated events and intervention decisions are also
    recorded by the persistent memory engine.
    """

    def __init__(self):
        self.state = CompanionState()
        self.running = False
        self.event_history: list[SituatedEvent] = []

        self.context = ContextEngine()
        self.intervention = InterventionEngine()
        self.memory = MemoryStore()

    def start(self):
        self.running = True

        return {
            "status": "running",
            "system": "sage-situated-companion",
        }

    def stop(self):
        self.running = False

        return {
            "status": "stopped",
            "system": "sage-situated-companion",
        }

    def ingest_event(self, event: SituatedEvent):
        """
        Receive one situated event, update runtime and persistent context,
        evaluate whether intervention is warranted, preserve the event
        in persistent memory, and return the resulting decision.
        """

        self.event_history.append(event)
        self.state.last_event = event

        self._update_situated_state(event)

        context_snapshot = self.context.apply_event(
            event_type=event.event_type,
            payload=event.payload,
        )

        decision = self.intervention.evaluate(
            event_type=event.event_type,
            payload=event.payload,
            confidence=event.confidence,
            safety_level=context_snapshot.safety_level,
            activity=context_snapshot.activity,
            conversation_active=bool(
                context_snapshot.conversation_topic
            ),
        )

        self.memory.remember(
            content=f"{event.event_type}: {event.payload}",
            category="situated_event",
            importance=max(
                event.confidence,
                context_snapshot.safety_level,
            ),
            metadata={
                "source": event.source,
                "decision_action": decision.action.value,
                "decision_reason": decision.reason,
                "decision_priority": decision.priority,
                "event_timestamp": event.timestamp.isoformat(),
            },
        )

        return decision

    def _update_situated_state(self, event: SituatedEvent):
        """
        Maintain the runtime's lightweight current-state representation.
        """

        if event.event_type == "location":
            self.state.location = event.payload.get("location")

        elif event.event_type == "activity":
            self.state.activity = event.payload.get("activity")

        elif event.event_type == "conversation":
            self.state.conversation_topic = event.payload.get("topic")

        elif event.event_type == "conversation_interrupted":
            self.state.interrupted_topic = (
                event.payload.get("topic")
                or self.state.conversation_topic
            )

        elif event.event_type == "conversation_resumed":
            if self.state.interrupted_topic:
                self.state.conversation_topic = (
                    self.state.interrupted_topic
                )

            self.state.interrupted_topic = None

        elif event.event_type == "safety":
            self.state.safety_level = self._clamp(
                event.payload.get("severity", 0.0)
            )

    def snapshot(self) -> CompanionState:
        """
        Return the runtime's current situated state.
        """

        return self.state

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Clamp numeric confidence and safety values to 0.0 through 1.0.
        """

        return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    sage = SageRuntime()

    print(sage.start())

    result = sage.ingest_event(
        SituatedEvent(
            source="bike_unit",
            event_type="activity",
            payload={
                "activity": "cycling",
            },
            confidence=0.97,
        )
    )

    print(result)
    print(sage.memory.summary())
