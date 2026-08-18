"""
SAGE Situated Companion
Roadmap 2 — OpenAI Generation Adapter Tests

Tests the model-backed generation boundary without making live
network requests or requiring an API key during automated testing.
"""

from types import SimpleNamespace

from interfaces.openai_generation import (
    OpenAIGenerationAdapter,
)


class FakeResponses:
    """
    Fake Responses API used to verify SAGE generation behavior
    without contacting an external model.
    """

    def __init__(self):
        self.last_request = None

    def create(
        self,
        *,
        model,
        instructions,
        input,
    ):
        self.last_request = {
            "model": model,
            "instructions": instructions,
            "input": input,
        }

        return SimpleNamespace(
            output_text="Hello Queen. SAGE is online."
        )


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def make_adapter():
    client = FakeClient()

    adapter = OpenAIGenerationAdapter(
        model="gpt-5.6",
        client=client,
    )

    return adapter, client


def test_openai_adapter_generates_response():
    adapter, _ = make_adapter()

    result = adapter.generate(
        instruction="Hello Sage.",
        context={
            "location": None,
            "activity": None,
            "conversation_topic": None,
            "safety_level": 0.0,
        },
        personality={
            "preferred_address": "Queen",
        },
        communication_mode="normal",
    )

    assert result == "Hello Queen. SAGE is online."


def test_openai_adapter_passes_user_input():
    adapter, client = make_adapter()

    adapter.generate(
        instruction="Tell me where we are.",
        context={},
        personality={},
        communication_mode="normal",
    )

    assert (
        client.responses.last_request["input"]
        == "Tell me where we are."
    )


def test_openai_adapter_uses_configured_model():
    adapter, client = make_adapter()

    adapter.generate(
        instruction="Hello.",
        context={},
        personality={},
        communication_mode="normal",
    )

    assert (
        client.responses.last_request["model"]
        == "gpt-5.6"
    )


def test_openai_adapter_includes_identity():
    adapter, client = make_adapter()

    adapter.generate(
        instruction="Who are you?",
        context={},
        personality={},
        communication_mode="normal",
    )

    instructions = (
        client.responses.last_request[
            "instructions"
        ]
    )

    assert (
        "You are Sage, a situated AI companion."
        in instructions
    )


def test_openai_adapter_includes_preferred_address():
    adapter, client = make_adapter()

    adapter.generate(
        instruction="Hello.",
        context={},
        personality={
            "preferred_address": "Queen",
        },
        communication_mode="conversational",
    )

    instructions = (
        client.responses.last_request[
            "instructions"
        ]
    )

    assert "Queen" in instructions


def test_openai_adapter_includes_situated_context():
    adapter, client = make_adapter()

    adapter.generate(
        instruction="What is happening?",
        context={
            "location": "library",
            "activity": "walking",
            "conversation_topic": "quantum mechanics",
            "safety_level": 0.2,
        },
        personality={},
        communication_mode="conversational",
    )

    instructions = (
        client.responses.last_request[
            "instructions"
        ]
    )

    assert "library" in instructions
    assert "walking" in instructions
    assert "quantum mechanics" in instructions
    assert "0.2" in instructions


def test_openai_adapter_strengthens_safety_mode():
    adapter, client = make_adapter()

    adapter.generate(
        instruction="Warn the user.",
        context={
            "safety_level": 0.95,
        },
        personality={},
        communication_mode="safety",
    )

    instructions = (
        client.responses.last_request[
            "instructions"
        ]
    )

    assert (
        "concise, unambiguous language"
        in instructions
    )


def test_openai_adapter_returns_empty_for_empty_input():
    adapter, client = make_adapter()

    result = adapter.generate(
        instruction="   ",
        context={},
        personality={},
        communication_mode="normal",
    )

    assert result == ""
    assert client.responses.last_request is None


def test_openai_adapter_accepts_memories_without_error():
    adapter, client = make_adapter()

    memory = SimpleNamespace(
        content="User prefers quiet evenings after work.",
        importance=0.9,
    )

    result = adapter.generate(
        instruction="What should I do tonight?",
        context={
            "location": "home",
            "activity": "resting",
            "conversation_topic": "evening plans",
            "safety_level": 0.1,
        },
        personality={"preferred_address": "Queen"},
        communication_mode="conversational",
        memories=[memory],
    )

    assert result == "Hello Queen. SAGE is online."
    instructions = client.responses.last_request["instructions"]
    assert "Relevant memory context" in instructions
    assert "User prefers quiet evenings after work." in instructions


def test_openai_adapter_ignores_empty_memories():
    adapter, client = make_adapter()

    adapter.generate(
        instruction="Hello.",
        context={},
        personality={},
        communication_mode="normal",
        memories=[
            SimpleNamespace(content="", importance=0.9),
            SimpleNamespace(content="   ", importance=0.8),
        ],
    )

    instructions = client.responses.last_request["instructions"]
    assert "Relevant memory context" not in instructions


def test_openai_adapter_safety_mode_ignores_memories():
    adapter, client = make_adapter()

    adapter.generate(
        instruction="Tell the user to evacuate.",
        context={"safety_level": 0.95},
        personality={},
        communication_mode="safety",
        memories=[
            SimpleNamespace(
                content="User prefers calm and humorous responses.",
                importance=1.0,
            )
        ],
    )

    instructions = client.responses.last_request["instructions"]
    assert "Use concise, unambiguous language." in instructions
    assert "User prefers calm and humorous responses." not in instructions
