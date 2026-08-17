"""
Tests for SAGE Roadmap 2 interface contracts.

These tests verify that external systems can implement the SAGE
input, generation, and output boundaries without modifying the
frozen Core V1 architecture.
"""

from interfaces.contracts import (
    ExternalInput,
    GenerationAdapter,
    InputAdapter,
    OutputAdapter,
    OutputRequest,
    OutputResult,
)

from sage.runtime import SituatedEvent


class MockInputAdapter(InputAdapter):
    """
    Minimal concrete input adapter used to verify the contract.
    """

    def to_situated_event(
        self,
        external_input: ExternalInput,
    ) -> SituatedEvent:

        return SituatedEvent(
            source=external_input.source,
            event_type=external_input.input_type,
            payload=external_input.payload,
            confidence=external_input.confidence,
            timestamp=external_input.timestamp,
        )


class MockGenerationAdapter(GenerationAdapter):
    """
    Minimal generation adapter used to verify the generation boundary.
    """

    def generate(
        self,
        *,
        instruction: str,
        context: dict,
        personality: dict,
        communication_mode: str,
    ) -> str:

        return (
            f"{communication_mode}: "
            f"{instruction}"
        )


class MockOutputAdapter(OutputAdapter):
    """
    Minimal output adapter used to verify normalized delivery.
    """

    def deliver(
        self,
        request: OutputRequest,
    ) -> OutputResult:

        return OutputResult(
            success=True,
            adapter="mock_output",
            output_type=request.output_type,
            metadata={
                "content": request.content,
            },
        )


def test_external_input_can_be_created():
    external_input = ExternalInput(
        source="mobile_device",
        input_type="location",
        payload={
            "location": "library",
        },
        confidence=0.95,
    )

    assert external_input.source == "mobile_device"
    assert external_input.input_type == "location"
    assert external_input.confidence == 0.95


def test_input_adapter_creates_situated_event():
    adapter = MockInputAdapter()

    external_input = ExternalInput(
        source="bike_sensor",
        input_type="activity",
        payload={
            "activity": "cycling",
        },
        confidence=0.97,
    )

    event = adapter.to_situated_event(
        external_input
    )

    assert isinstance(event, SituatedEvent)
    assert event.source == "bike_sensor"
    assert event.event_type == "activity"
    assert event.payload == {
        "activity": "cycling",
    }
    assert event.confidence == 0.97


def test_input_adapter_preserves_timestamp():
    adapter = MockInputAdapter()

    external_input = ExternalInput(
        source="camera",
        input_type="vision",
        payload={
            "objects": ["vehicle"],
        },
    )

    event = adapter.to_situated_event(
        external_input
    )

    assert (
        event.timestamp
        == external_input.timestamp
    )


def test_generation_adapter_uses_constraints():
    generator = MockGenerationAdapter()

    result = generator.generate(
        instruction="Car approaching from the right.",
        context={
            "activity": "cycling",
            "safety_level": 0.95,
        },
        personality={
            "name": "Sage",
        },
        communication_mode="safety",
    )

    assert result == (
        "safety: Car approaching from the right."
    )


def test_output_request_defaults_to_text():
    request = OutputRequest(
        content="Hello."
    )

    assert request.content == "Hello."
    assert request.output_type == "text"
    assert request.priority == 0.5


def test_output_adapter_delivers_request():
    adapter = MockOutputAdapter()

    request = OutputRequest(
        content="Car approaching from the right.",
        output_type="text",
        priority=1.0,
    )

    result = adapter.deliver(request)

    assert result.success is True
    assert result.adapter == "mock_output"
    assert result.output_type == "text"
    assert (
        result.metadata["content"]
        == "Car approaching from the right."
    )


def test_output_result_can_report_failure():
    result = OutputResult(
        success=False,
        adapter="speech_output",
        output_type="audio",
        error="device_unavailable",
    )

    assert result.success is False
    assert result.error == "device_unavailable"


def test_interface_boundary_does_not_require_core_change():
    adapter = MockInputAdapter()

    event = adapter.to_situated_event(
        ExternalInput(
            source="future_sensor",
            input_type="custom_sensor_event",
            payload={
                "value": 42,
            },
            confidence=0.88,
        )
    )

    assert isinstance(event, SituatedEvent)
    assert event.source == "future_sensor"
    assert event.event_type == "custom_sensor_event"
