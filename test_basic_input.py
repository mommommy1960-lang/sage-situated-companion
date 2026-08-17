"""
SAGE Situated Companion
Roadmap 2 — Basic Input Adapter Integration Tests

Verifies the first concrete external-input pipeline:

ExternalInput
    -> BasicInputAdapter
    -> SituatedEvent
    -> SageRuntime
    -> Context
    -> Intervention
    -> Persistent Memory

The frozen SAGE Core V1 architecture is not modified.
"""

from interfaces.contracts import ExternalInput
from interfaces.basic_input import BasicInputAdapter
from sage.runtime import SageRuntime
from sage.intervention import InterventionAction


def make_sage(tmp_path):
    """
    Create an isolated Sage runtime for integration testing.
    """

    sage = SageRuntime()

    sage.memory.storage_path = (
        tmp_path / "basic_input_memory.json"
    )
    sage.memory.memories.clear()

    return sage


def test_basic_adapter_creates_situated_event():
    adapter = BasicInputAdapter()

    external = ExternalInput(
        source="mobile_unit",
        input_type="location",
        payload={"location": "library"},
        confidence=0.95,
    )

    event = adapter.to_situated_event(external)

    assert event.source == "mobile_unit"
    assert event.event_type == "location"
    assert event.payload == {"location": "library"}
    assert event.confidence == 0.95
    assert event.timestamp == external.timestamp


def test_external_location_reaches_runtime(tmp_path):
    sage = make_sage(tmp_path)
    adapter = BasicInputAdapter()

    external = ExternalInput(
        source="mobile_unit",
        input_type="location",
        payload={"location": "library"},
        confidence=0.95,
    )

    event = adapter.to_situated_event(external)
    result = sage.ingest_event(event)

    assert sage.state.location == "library"
    assert result["context"].location == "library"

    assert (
        result["decision"].action
        == InterventionAction.OBSERVE
    )


def test_external_activity_reaches_runtime(tmp_path):
    sage = make_sage(tmp_path)
    adapter = BasicInputAdapter()

    external = ExternalInput(
        source="bike_unit",
        input_type="activity",
        payload={"activity": "cycling"},
        confidence=0.97,
    )

    event = adapter.to_situated_event(external)
    result = sage.ingest_event(event)

    assert sage.state.activity == "cycling"
    assert result["context"].activity == "cycling"

    assert (
        result["decision"].action
        == InterventionAction.OBSERVE
    )

    assert (
        result["communication_mode"].value
        == "normal"
    )


def test_external_safety_event_can_interrupt(tmp_path):
    sage = make_sage(tmp_path)
    adapter = BasicInputAdapter()

    external = ExternalInput(
        source="safety_monitor",
        input_type="safety",
        payload={"severity": 0.95},
        confidence=0.99,
    )

    event = adapter.to_situated_event(external)
    result = sage.ingest_event(event)

    assert (
        result["decision"].action
        == InterventionAction.INTERRUPT
    )

    assert (
        result["decision"].reason
        == "high_safety_risk"
    )

    assert (
        result["communication_mode"].value
        == "safety"
    )


def test_external_event_reaches_persistent_memory(
    tmp_path,
):
    sage = make_sage(tmp_path)
    adapter = BasicInputAdapter()

    external = ExternalInput(
        source="mobile_unit",
        input_type="location",
        payload={"location": "library"},
        confidence=0.95,
    )

    event = adapter.to_situated_event(external)
    sage.ingest_event(event)

    memories = sage.memory.recall(
        category="situated_event"
    )

    assert len(memories) == 1
    assert memories[0].metadata["source"] == "mobile_unit"

    assert (
        memories[0].metadata["decision_action"]
        == "observe"
    )


def test_complete_external_input_pipeline(tmp_path):
    """
    Verify the complete Roadmap 2 input path from an external
    representation through the adapter and frozen SAGE Core V1.
    """

    sage = make_sage(tmp_path)
    adapter = BasicInputAdapter()

    external = ExternalInput(
        source="bike_unit",
        input_type="activity",
        payload={"activity": "cycling"},
        confidence=0.97,
    )

    event = adapter.to_situated_event(external)
    result = sage.ingest_event(event)

    assert event in sage.event_history

    assert sage.state.activity == "cycling"

    assert result["context"].activity == "cycling"

    assert (
        result["decision"].action
        == InterventionAction.OBSERVE
    )

    assert (
        result["communication_mode"].value
        == "normal"
    )

    memories = sage.memory.recall(
        category="situated_event"
    )

    assert len(memories) == 1
