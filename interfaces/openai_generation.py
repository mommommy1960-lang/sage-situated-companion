"""
SAGE Situated Companion
Roadmap 2 — OpenAI Generation Adapter

Provides a model-backed implementation of the GenerationAdapter
contract using the OpenAI Responses API.

This adapter remains outside the frozen SAGE Core V1 architecture.
"""

from typing import Any

from openai import OpenAI

from interfaces.contracts import GenerationAdapter


class OpenAIGenerationAdapter(GenerationAdapter):
    """
    Model-backed SAGE generation adapter.

    Uses situated context, personality information, and the selected
    communication mode as generation constraints while preserving the
    existing GenerationAdapter boundary.
    """

    def __init__(
        self,
        *,
        model: str = "gpt-5.6",
        client: Any | None = None,
    ):
        self.model = model
        self._client = client

    @property
    def client(self):
        """
        Lazily create the OpenAI client.

        The SDK reads OPENAI_API_KEY from the environment.
        """

        if self._client is None:
            self._client = OpenAI()

        return self._client

    def generate(
        self,
        *,
        instruction: str,
        context: dict[str, Any],
        personality: dict[str, Any],
        communication_mode: str,
    ) -> str:
        """
        Generate a SAGE response using the OpenAI Responses API.
        """

        instruction = instruction.strip()

        if not instruction:
            return ""

        developer_instruction = self._build_instructions(
            context=context,
            personality=personality,
            communication_mode=communication_mode,
        )

        response = self.client.responses.create(
            model=self.model,
            instructions=developer_instruction,
            input=instruction,
        )

        return response.output_text.strip()

    @staticmethod
    def _build_instructions(
        *,
        context: dict[str, Any],
        personality: dict[str, Any],
        communication_mode: str,
    ) -> str:
        """
        Convert SAGE runtime state into model-generation constraints.
        """

        preferred_address = personality.get(
            "preferred_address"
        )

        location = context.get("location")
        activity = context.get("activity")
        conversation_topic = context.get(
            "conversation_topic"
        )
        safety_level = context.get(
            "safety_level",
            0.0,
        )

        lines = [
            "You are Sage, a situated AI companion.",
            "Respond to the user rather than repeating their message.",
            (
                "Maintain a warm, observant, direct, "
                "context-aware companion identity."
            ),
            (
                f"Current communication mode: "
                f"{communication_mode}."
            ),
            (
                f"Current safety level: "
                f"{safety_level}."
            ),
        ]

        if preferred_address:
            lines.append(
                f"The user's preferred address is "
                f"{preferred_address}."
            )

        if location:
            lines.append(
                f"Current location context: {location}."
            )

        if activity:
            lines.append(
                f"Current activity context: {activity}."
            )

        if conversation_topic:
            lines.append(
                f"Current conversation topic: "
                f"{conversation_topic}."
            )

        if communication_mode == "safety":
            lines.append(
                "Use concise, unambiguous language. "
                "Suppress unnecessary humor and conversational flourish."
            )

        elif communication_mode == "quiet":
            lines.append(
                "Keep the response very brief and low-distraction."
            )

        elif communication_mode == "conversational":
            lines.append(
                "Natural conversational warmth and personality are appropriate."
            )

        return "\n".join(lines)
