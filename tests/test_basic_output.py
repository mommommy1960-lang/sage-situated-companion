"""
Tests for the SAGE Basic Output Adapter.

Verifies that the first concrete output implementation respects
the OutputAdapter contract and correctly reports successful and
failed normalized delivery attempts.
"""

from interfaces.basic_output import BasicOutputAdapter
from interfaces.contracts import OutputRequest


def test_basic_output_delivers_text():
    adapter = BasicOutputAdapter()

    request = OutputRequest(
        content="Hello from Sage."
    )

    result = adapter.deliver(request)

    assert result.success is True
    assert result.adapter == "basic_output"
    assert result.output_type == "text"
    assert (
        result.metadata["content"]
        == "Hello from Sage."
    )


def test_basic_output_preserves_priority():
    adapter = BasicOutputAdapter()

    request = OutputRequest(
        content="Safety warning.",
        priority=1.0,
    )

    result = adapter.deliver(request)

    assert result.success is True
    assert result.metadata["priority"] == 1.0


def test_basic_output_preserves_request_metadata():
    adapter = BasicOutputAdapter()

    request = OutputRequest(
        content="Turn left ahead.",
        metadata={
            "source": "navigation",
            "communication_mode": "normal",
        },
    )

    result = adapter.deliver(request)

    assert result.success is True

    assert result.metadata["request_metadata"] == {
        "source": "navigation",
        "communication_mode": "normal",
    }


def test_basic_output_rejects_empty_content():
    adapter = BasicOutputAdapter()

    request = OutputRequest(
        content=""
    )

    result = adapter.deliver(request)

    assert result.success is False
    assert result.adapter == "basic_output"
    assert result.error == "empty_content"


def test_basic_output_rejects_whitespace_only_content():
    adapter = BasicOutputAdapter()

    request = OutputRequest(
        content="     "
    )

    result = adapter.deliver(request)

    assert result.success is False
    assert result.error == "empty_content"


def test_basic_output_supports_non_text_output_type():
    adapter = BasicOutputAdapter()

    request = OutputRequest(
        content="Vehicle approaching.",
        output_type="audio",
        priority=1.0,
    )

    result = adapter.deliver(request)

    assert result.success is True
    assert result.output_type == "audio"
