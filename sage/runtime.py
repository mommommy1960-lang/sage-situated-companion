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
    """

    def __init__(self):
        self.state = CompanionState()
        self.running = False
        self.event_history: list[SituatedEvent] = []

    def start(self):
        self.running = True
        return {
            "status": "running",
            "system": "sage-situated-companion"
        }

    def stop(self):
        self.running = False
        return {
            "status": "stopped",
            "system": "sage-situated-companion"
        }

    def ingest_event(self, event: SituatedEvent):
        self.event_history.append(event)
        self.state.last_event = event

        self._update_situated_state(event)

        return self.evaluate_event(event)

    def _update_situated_state(self, event: SituatedEvent):
        if event.event_type == "location":
            self.state.location = event.payload.get("location")

        elif event.event_type == "activity":
            self.state.activity = event.payload.get("activity")

        elif event.event_type == "conversation":
            self.state.conversation_topic = event.payload.get("topic")

        elif event.event_type == "safety":
            self.state.safety_level = float(
                event.payload.get("severity", 0.0)
            )

    def evaluate_event(self, event: SituatedEvent):
        """
        Temporary baseline decision layer.

        Later versions delegate this decision to intervention.py,
        where relevance, urgency, safety, confidence, interruption
        cost, repetition, and conversational restoration are scored.
        """

        if event.event_type == "safety":
            severity = float(event.payload.get("severity", 0.0))

            if severity >= 0.8:
                return {
                    "action": "interrupt",
                    "reason": "high_safety_priority",
                    "event": event.event_type,
                }

        return {
            "action": "observe",
            "reason": "no_intervention_required",
            "event": event.event_type,
        }


if __name__ == "__main__":
    sage = SageRuntime()

    print(sage.start())

    result = sage.ingest_event(
        SituatedEvent(
            source="bike_unit",
            event_type="activity",
            payload={"activity": "cycling"},
            confidence=0.97,
        )
    )

    print(result)
