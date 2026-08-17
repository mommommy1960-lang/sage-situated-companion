"""
Tests for the SAGE Basic Generation Adapter.

Verifies that the first concrete generation implementation respects
the GenerationAdapter contract and SAGE communication constraints.
"""

from interfaces.basic_generation import BasicGenerationAdapter


def test_basic_generation_returns_instruction():
    adapter = BasicGenerationAdapter()

    result = adapter.generate(
        instruction="The library closes soon.",
        context={},
        personality={},
        communication_mode="normal",
    )

    assert result == "The library closes soon."


def test_generation_strips_whitespace():
    adapter = BasicGenerationAdapter()

    result = adapter.generate(
        instruction="   Turn left ahead.   ",
        context={},
        personality={},
        communication_mode="normal",
    )

    assert result == "Turn left ahead."


def test_empty_instruction_returns_empty_string():
    adapter = BasicGenerationAdapter()

    result = adapter.generate(
        instruction="   ",
        context={},
        personality={},
        communication_mode="normal",
    )

    assert result == ""


def test_safety_generation_remains_concise():
    adapter = BasicGenerationAdapter()

    result = adapter.generate(
        instruction="Vehicle approaching from the right.",
        context={"activity": "cycling"},
        personality={
            "preferred_address": "Queen",
        },
        communication_mode="safety",
    )

    assert result == "Vehicle approaching from the right."


def test_conversational_mode_can_use_preferred_address():
    adapter = BasicGenerationAdapter()

    result = adapter.generate(
        instruction="We're passing the library again.",
        context={"activity": "walking"},
        personality={
            "preferred_address": "Queen",
        },
        communication_mode="conversational",
    )

    assert result == (
        "Queen, We're passing the library again."
    )


def test_normal_mode_does_not_add_preferred_address():
    adapter = BasicGenerationAdapter()

    result = adapter.generate(
        instruction="Navigation ready.",
        context={},
        personality={
            "preferred_address": "Queen",
        },
        communication_mode="normal",
    )

    assert result == "Navigation ready."
