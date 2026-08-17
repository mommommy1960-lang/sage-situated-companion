"""
SAGE Situated Companion
Roadmap 2 — Complete Round-Trip Integration Tests

Verifies that normalized external input can enter through the adapter
boundary, pass through the frozen SAGE Core V1 runtime, generate
content according to the selected communication mode, and leave
through the output boundary.

Pipeline:

ExternalInput
    -> BasicInputAdapter
    -> SituatedEvent
    -> SageRuntime
    -> InterventionDecision
    -> CommunicationMode
    -> BasicGenerationAdapter
    -> OutputRequest
    -> BasicOutputAdapter
    -> OutputResult
"""

from interfaces.contracts import (
    ExternalInput,
    OutputRequest,
)

from interfaces.basic_input import BasicInputAdapter
from interfaces.basic_generation import BasicGenerationAdapter
from interfaces.basic_output import BasicOutputAdapter

from sage.runtime import SageRuntime
from sage.intervention import InterventionAction


def make_sage(tmp_path):
    """
    Create an isolated SAGE runtime for round-trip testing.
    """

    sage = SageRuntime()

    sage.memory.storage_path = (
        tmp_path / "round_trip_memory.json"
    )
    sage.memory.memories.clear()

    return sage


def test_complete_user_request_round_trip(tmp_path):
    """
    Verify a direct external user request can travel from the
    external-input boundary through SAGE and back out through
    the output boundary.
    """

    sage = make_sage(tmp_path)

    input_adapter = BasicInputAdapter()
    generation_adapter = BasicGenerationAdapter()
    output_adapter = BasicOutputAdapter()

    external = ExternalInput(
        source="user",
        input_type="request",
        payload={
            "text": "Help me understand this."
        },
        confidence=1.0,
    )

    event = input_adapter.to_situated_event(
        external
    )

    runtime_result = sage.ingest_event(
        event
    )

    decision = runtime_result["decision"]
    communication_mode = (
        runtime_result["communication_mode"].value
    )

    assert (
        decision.action
        == InterventionAction.RESPOND
    )

    generated = generation_adapter.generate(
        instruction=external.payload["text"],
        context={
            "activity": (
                runtime_result["context"].activity
            ),
        },
        personality={
            "preferred_address": "Queen",
        },
        communication_mode=communication_mode,
    )

    request = OutputRequest(
        content=generated,
        output_type="text",
        priority=decision.priority,
        metadata={
            "source": external.source,
            "decision_reason": decision.reason,
            "communication_mode": communication_mode,
        },
    )

    output_result = output_adapter.deliver(
        request
    )

    assert output_result.success is True
    assert output_result.adapter == "basic_output"
    assert output_result.output_type == "text"

    assert (
        output_result.metadata["content"]
        == "Help me understand this."
    )

    assert (
        output_result.metadata[
            "request_metadata"
        ]["decision_reason"]
        == "direct_user_request"
    )


def test_complete_safety_round_trip(tmp_path):
    """
    Verify a high-safety external event can cross the full pipeline
    while retaining SAGE's safety-priority communication behavior.
    """

    sage = make_sage(tmp_path)

    input_adapter = BasicInputAdapter()
    generation_adapter = BasicGenerationAdapter()
    output_adapter = BasicOutputAdapter()

    external = ExternalInput(
        source="safety_monitor",
        input_type="safety",
        payload={
            "severity": 0.95,
            "message": (
                "Vehicle approaching from the right."
            ),
        },
        confidence=0.99,
    )

    event = input_adapter.to_situated_event(
        external
    )

    runtime_result = sage.ingest_event(
        event
    )

    decision = runtime_result["decision"]
    communication_mode = (
        runtime_result["communication_mode"].value
    )

    assert (
        decision.action
        == InterventionAction.INTERRUPT
    )

    assert communication_mode == "safety"

    generated = generation_adapter.generate(
        instruction=external.payload["message"],
        context={
            "safety_level": (
                runtime_result[
                    "context"
                ].safety_level
            ),
        },
        personality={
            "preferred_address": "Queen",
        },
        communication_mode=communication_mode,
    )

    assert (
        generated
        == "Vehicle approaching from the right."
    )

    request = OutputRequest(
        content=generated,
        output_type="audio",
        priority=decision.priority,
        metadata={
            "source": external.source,
            "decision_reason": decision.reason,
            "communication_mode": communication_mode,
        },
    )

    output_result = output_adapter.deliver(
        request
    )

    assert output_result.success is True
    assert output_result.output_type == "audio"

    assert (
        output_result.metadata["content"]
        == "Vehicle approaching from the right."
    )

    assert (
        output_result.metadata[
            "request_metadata"
        ]["communication_mode"]
        == "safety"
    )


def test_round_trip_preserves_persistent_memory(
    tmp_path,
):
    """
    Verify that completing the external round-trip does not bypass
    SAGE's persistent-memory behavior.
    """

    sage = make_sage(tmp_path)

    input_adapter = BasicInputAdapter()
    generation_adapter = BasicGenerationAdapter()
    output_adapter = BasicOutputAdapter()

    external = ExternalInput(
        source="user",
        input_type="request",
        payload={
            "text": "Remember this request."
        },
        confidence=1.0,
    )

    event = input_adapter.to_situated_event(
        external
    )

    runtime_result = sage.ingest_event(
        event
    )

    generated = generation_adapter.generate(
        instruction=external.payload["text"],
        context={},
        personality={},
        communication_mode=(
            runtime_result[
                "communication_mode"
            ].value
        ),
    )

    request = OutputRequest(
        content=generated,
        priority=(
            runtime_result[
                "decision"
            ].priority
        ),
    )

    output_result = output_adapter.deliver(
        request
    )

    assert output_result.success is True

    memories = sage.memory.recall(
        category="situated_event"
    )

    assert len(memories) == 1

    assert (
        memories[0].metadata["source"]
        == "user"
    )
