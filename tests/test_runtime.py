"""
Integration tests for the SAGE Situated Companion runtime.

These tests verify that the runtime coordinates situated context,
intervention decisions, persistent memory, personality continuity,
conversation restoration, and safety-priority behavior.
"""

from sage.runtime import SageRuntime, SituatedEvent
from sage.intervention import InterventionAction


def make_sage(tmp_path):
    """
    Create a Sage runtime whose persistent memory is isolated
    inside the pytest temporary directory.
    """

    sage = SageRuntime()

    sage.memory.storage_path = tmp_path / "sage_test_memory.json"
    sage.memory.memories.clear()

    return sage


def test_runtime_starts_and_stops(tmp_path):
    sage = make_sage(tmp_path)

    start_result = sage.start()

    assert sage.running is True
    assert start_result["status"] == "running"
    assert start_result["system"] == "sage-situated-companion"

    stop_result = sage.stop()

    assert sage.running is False
    assert stop_result["status"] == "stopped"


def test_activity_event_updates_runtime_and_context(tmp_path):
    sage = make_sage(tmp_path)

    event = SituatedEvent(
        source="bike_unit",
        event_type="activity",
        payload={"activity": "cycling"},
        confidence=0.97,
    )

    result = sage.ingest_event(event)

    assert sage.state.activity == "cycling"
    assert sage.state.last_event == event
    assert event in sage.event_history

    assert result["context"].activity == "cycling"

    assert (
        result["decision"].action
        == InterventionAction.OBSERVE
    )


def test_location_event_updates_runtime_and_context(tmp_path):
    sage = make_sage(tmp_path)

    result = sage.ingest_event(
        SituatedEvent(
            source="mobile_unit",
            event_type="location",
            payload={"location": "library"},
            confidence=0.95,
        )
    )

    assert sage.state.location == "library"
    assert result["context"].location == "library"


def test_conversation_state_can_be_interrupted_and_resumed(
    tmp_path,
):
    sage = make_sage(tmp_path)

    sage.ingest_event(
        SituatedEvent(
            source="conversation",
            event_type="conversation",
            payload={"topic": "quantum mechanics"},
        )
    )

    assert (
        sage.state.conversation_topic
        == "quantum mechanics"
    )

    assert (
        sage.context.snapshot().conversation_topic
        == "quantum mechanics"
    )

    sage.ingest_event(
        SituatedEvent(
            source="system",
            event_type="conversation_interrupted",
            payload={},
        )
    )

    assert (
        sage.state.interrupted_topic
        == "quantum mechanics"
    )

    assert (
        sage.context.snapshot().interrupted_topic
        == "quantum mechanics"
    )

    sage.ingest_event(
        SituatedEvent(
            source="system",
            event_type="conversation_resumed",
            payload={},
        )
    )

    assert (
        sage.state.conversation_topic
        == "quantum mechanics"
    )

    assert sage.state.interrupted_topic is None

    assert (
        sage.context.snapshot().conversation_topic
        == "quantum mechanics"
    )

    assert (
        sage.context.snapshot().interrupted_topic
        is None
    )


def test_high_safety_event_requests_interruption(tmp_path):
    sage = make_sage(tmp_path)

    result = sage.ingest_event(
        SituatedEvent(
            source="safety_monitor",
            event_type="safety",
            payload={"severity": 0.95},
            confidence=0.99,
        )
    )

    decision = result["decision"]

    assert (
        decision.action
        == InterventionAction.INTERRUPT
    )

    assert decision.reason == "high_safety_risk"

    assert (
        result["communication_mode"].value
        == "safety"
    )


def test_moderate_safety_event_requests_response(tmp_path):
    sage = make_sage(tmp_path)

    result = sage.ingest_event(
        SituatedEvent(
            source="safety_monitor",
            event_type="safety",
            payload={"severity": 0.60},
            confidence=0.95,
        )
    )

    decision = result["decision"]

    assert (
        decision.action
        == InterventionAction.RESPOND
    )

    assert decision.reason == "moderate_safety_risk"


def test_direct_user_request_receives_response(tmp_path):
    sage = make_sage(tmp_path)

    result = sage.ingest_event(
        SituatedEvent(
            source="user",
            event_type="request",
            payload={
                "text": "Help me understand this."
            },
            confidence=1.0,
        )
    )

    decision = result["decision"]

    assert (
        decision.action
        == InterventionAction.RESPOND
    )

    assert decision.reason == "direct_user_request"


def test_low_confidence_perception_does_not_interrupt(
    tmp_path,
):
    sage = make_sage(tmp_path)

    result = sage.ingest_event(
        SituatedEvent(
            source="camera",
            event_type="vision",
            payload={"objects": ["vehicle"]},
            confidence=0.30,
        )
    )

    decision = result["decision"]

    assert (
        decision.action
        == InterventionAction.OBSERVE
    )

    assert (
        decision.reason
        == "low_confidence_observation"
    )


def test_event_is_recorded_in_persistent_memory(tmp_path):
    sage = make_sage(tmp_path)

    sage.ingest_event(
        SituatedEvent(
            source="bike_unit",
            event_type="activity",
            payload={"activity": "cycling"},
            confidence=0.97,
        )
    )

    memories = sage.memory.recall(
        category="situated_event"
    )

    assert len(memories) == 1

    memory = memories[0]

    assert memory.metadata["source"] == "bike_unit"

    assert (
        memory.metadata["decision_action"]
        == "observe"
    )

    assert (
        memory.metadata["communication_mode"]
        == "normal"
    )


def test_memory_survives_store_reload(tmp_path):
    memory_path = tmp_path / "persistent_memory.json"

    sage = SageRuntime()
    sage.memory.storage_path = memory_path
    sage.memory.memories.clear()

    sage.ingest_event(
        SituatedEvent(
            source="mobile_unit",
            event_type="location",
            payload={"location": "library"},
            confidence=0.90,
        )
    )

    assert memory_path.exists()

    from sage.memory import MemoryStore

    reloaded = MemoryStore(
        storage_path=str(memory_path)
    )

    memories = reloaded.recall(
        category="situated_event"
    )

    assert len(memories) == 1
    assert memories[0].metadata["source"] == "mobile_unit"


def test_runtime_has_personality_engine(tmp_path):
    sage = make_sage(tmp_path)

    assert sage.personality is not None

    assert (
        sage.personality.profile.name
        == "Sage"
    )


def test_cycling_uses_normal_mode_when_no_hazard(
    tmp_path,
):
    sage = make_sage(tmp_path)

    result = sage.ingest_event(
        SituatedEvent(
            source="bike_unit",
            event_type="activity",
            payload={"activity": "cycling"},
            confidence=0.97,
        )
    )

    assert (
        result["communication_mode"].value
        == "normal"
    )


def test_high_safety_event_enters_safety_mode(tmp_path):
    sage = make_sage(tmp_path)

    result = sage.ingest_event(
        SituatedEvent(
            source="safety_monitor",
            event_type="safety",
            payload={"severity": 0.95},
            confidence=0.99,
        )
    )

    assert (
        result["communication_mode"].value
        == "safety"
    )


def test_personality_identity_remains_stable_during_safety(
    tmp_path,
):
    sage = make_sage(tmp_path)

    original_name = sage.personality.profile.name

    sage.ingest_event(
        SituatedEvent(
            source="safety_monitor",
            event_type="safety",
            payload={"severity": 0.95},
            confidence=0.99,
        )
    )

    assert sage.personality.profile.name == original_name
    assert sage.personality.profile.name == "Sage"
