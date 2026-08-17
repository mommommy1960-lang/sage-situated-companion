"""
Tests for the SAGE Situated Companion runtime.

These tests verify that the runtime coordinates situated context,
intervention decisions, persistent memory, personality continuity,
and current state correctly.
"""

from sage.runtime import SageRuntime, SituatedEvent
from sage.intervention import InterventionAction


def test_runtime_starts_and_stops():
    sage = SageRuntime()

    start_result = sage.start()

    assert sage.running is True
    assert start_result["status"] == "running"
    assert start_result["system"] == "sage-situated-companion"

    stop_result = sage.stop()

    assert sage.running is False
    assert stop_result["status"] == "stopped"


def test_activity_event_updates_runtime_state():
    sage = SageRuntime()

    event = SituatedEvent(
        source="bike_unit",
        event_type="activity",
        payload={"activity": "cycling"},
        confidence=0.97,
    )

    sage.ingest_event(event)

    assert sage.state.activity == "cycling"
    assert sage.state.last_event == event
    assert event in sage.event_history


def test_location_event_updates_runtime_state():
    sage = SageRuntime()

    event = SituatedEvent(
        source="mobile_unit",
        event_type="location",
        payload={"location": "library"},
        confidence=0.95,
    )

    sage.ingest_event(event)

    assert sage.state.location == "library"


def test_conversation_state_can_be_interrupted_and_resumed():
    sage = SageRuntime()

    sage.ingest_event(
        SituatedEvent(
            source="conversation",
            event_type="conversation",
            payload={"topic": "quantum mechanics"},
        )
    )

    assert sage.state.conversation_topic == "quantum mechanics"

    sage.ingest_event(
        SituatedEvent(
            source="system",
            event_type="conversation_interrupted",
            payload={},
        )
    )

    assert sage.state.interrupted_topic == "quantum mechanics"

    sage.ingest_event(
        SituatedEvent(
            source="system",
            event_type="conversation_resumed",
            payload={},
        )
    )

    assert sage.state.conversation_topic == "quantum mechanics"
    assert sage.state.interrupted_topic is None


def test_high_safety_event_requests_interruption():
    sage = SageRuntime()

    decision = sage.ingest_event(
        SituatedEvent(
            source="safety_monitor",
            event_type="safety",
            payload={"severity": 0.95},
            confidence=0.99,
        )
    )

    assert decision.action == InterventionAction.INTERRUPT
    assert decision.reason == "high_safety_risk"


def test_direct_user_request_receives_response():
    sage = SageRuntime()

    decision = sage.ingest_event(
        SituatedEvent(
            source="user",
            event_type="request",
            payload={"text": "Help me understand this."},
            confidence=1.0,
        )
    )

    assert decision.action == InterventionAction.RESPOND
    assert decision.reason == "direct_user_request"


def test_event_is_recorded_in_memory():
    sage = SageRuntime()

    sage.ingest_event(
        SituatedEvent(
            source="bike_unit",
            event_type="activity",
            payload={"activity": "cycling"},
            confidence=0.97,
        )
    )

    summary = sage.memory.summary()

    assert summary is not None


def test_runtime_has_personality_engine():
    sage = SageRuntime()

    assert sage.personality is not None
    assert sage.personality.profile.name == "Sage"


def test_runtime_personality_enters_safety_mode():
    sage = SageRuntime()

    sage.ingest_event(
        SituatedEvent(
            source="safety_monitor",
            event_type="safety",
            payload={"severity": 0.95},
            confidence=0.99,
        )
    )

    rendered = sage.render_message(
        "Car approaching from the right."
    )

    assert rendered == "Car approaching from the right."
