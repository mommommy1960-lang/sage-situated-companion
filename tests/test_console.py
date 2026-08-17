"""
SAGE Situated Companion
Roadmap 2 — Console Application Tests

Verifies that the first runnable SAGE application correctly composes
the external input adapter, frozen SAGE Core V1 runtime, generation
adapter, and output adapter.

These tests exercise the application boundary without modifying
the verified core architecture.
"""

from apps.console import SageConsole
from sage.runtime import SageRuntime


def make_console(
    tmp_path,
    *,
    preferred_address=None,
):
    """
    Create an isolated SAGE console whose persistent memory remains
    inside the pytest temporary directory.
    """

    runtime = SageRuntime()

    runtime.memory.storage_path = (
        tmp_path / "console_memory.json"
    )
    runtime.memory.memories.clear()

    return SageConsole(
        runtime=runtime,
        preferred_address=preferred_address,
    )


def test_console_processes_direct_user_message(
    tmp_path,
):
    """
    A normal console message should cross the complete SAGE
    application pipeline and return generated output.
    """

    console = make_console(tmp_path)

    response = console.process_message(
        "Help me understand quantum mechanics."
    )

    assert (
        response
        == "Help me understand quantum mechanics."
    )


def test_console_rejects_empty_message(
    tmp_path,
):
    """
    Empty input should not enter the SAGE pipeline.
    """

    console = make_console(tmp_path)

    assert console.process_message("") is None
    assert console.process_message("     ") is None

    assert (
        console.runtime.memory.summary()[
            "total_memories"
        ]
        == 0
    )


def test_console_records_message_in_memory(
    tmp_path,
):
    """
    Console input should retain the persistent-memory behavior
    provided by the frozen SAGE runtime.
    """

    console = make_console(tmp_path)

    console.process_message(
        "Remember this console request."
    )

    memories = console.runtime.memory.recall(
        category="situated_event"
    )

    assert len(memories) == 1

    memory = memories[0]

    assert (
        memory.metadata["source"]
        == "console_user"
    )

    assert (
        memory.metadata["decision_action"]
        == "respond"
    )


def test_console_uses_direct_request_decision(
    tmp_path,
):
    """
    Console messages should enter SAGE as direct user requests.
    """

    console = make_console(tmp_path)

    console.process_message(
        "Tell me what you observed."
    )

    memories = console.runtime.memory.recall(
        category="situated_event"
    )

    assert len(memories) == 1

    memory = memories[0]

    assert (
        memory.metadata["decision_reason"]
        == "direct_user_request"
    )


def test_console_preserves_communication_mode(
    tmp_path,
):
    """
    The application path should preserve the communication mode
    selected by the SAGE runtime.
    """

    console = make_console(tmp_path)

    console.process_message(
        "Continue our conversation."
    )

    memories = console.runtime.memory.recall(
        category="situated_event"
    )

    assert len(memories) == 1

    assert (
        memories[0].metadata[
            "communication_mode"
        ]
        == "normal"
    )


def test_console_can_use_preferred_address(
    tmp_path,
):
    """
    Preferred-address configuration should remain available to the
    application generation layer when conversational mode is used.
    """

    console = make_console(
        tmp_path,
        preferred_address="Queen",
    )

    assert (
        console.preferred_address
        == "Queen"
    )


def test_console_runtime_can_start_and_stop(
    tmp_path,
):
    """
    The runtime owned by the console remains independently
    controllable through the existing Core V1 lifecycle.
    """

    console = make_console(tmp_path)

    start_result = console.runtime.start()

    assert console.runtime.running is True
    assert start_result["status"] == "running"

    stop_result = console.runtime.stop()

    assert console.runtime.running is False
    assert stop_result["status"] == "stopped"


def test_console_uses_complete_adapter_stack(
    tmp_path,
):
    """
    The console must contain all three concrete Roadmap 2 adapters.
    """

    console = make_console(tmp_path)

    from interfaces.basic_input import (
        BasicInputAdapter,
    )
    from interfaces.basic_generation import (
        BasicGenerationAdapter,
    )
    from interfaces.basic_output import (
        BasicOutputAdapter,
    )

    assert isinstance(
        console.input_adapter,
        BasicInputAdapter,
    )

    assert isinstance(
        console.generation_adapter,
        BasicGenerationAdapter,
    )

    assert isinstance(
        console.output_adapter,
        BasicOutputAdapter,
    )
