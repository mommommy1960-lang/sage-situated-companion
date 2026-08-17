"""
SAGE Situated Companion
Roadmap 2 — Basic Generation Adapter

Provides the first concrete implementation of the GenerationAdapter
contract.

This deterministic adapter demonstrates how an approved SAGE response
intention can be transformed into generated content while remaining
outside the frozen SAGE Core V1 architecture.
"""

from typing import Any

from interfaces.contracts import GenerationAdapter


class BasicGenerationAdapter(GenerationAdapter):
    """
    Basic deterministic generation adapter.

    This implementation does not depend on a language model.
    It establishes and exercises the generation boundary so a future
    model-backed adapter can be introduced without modifying Core V1.
    """

    def generate(
        self,
        *,
        instruction: str,
        context: dict[str, Any],
        personality: dict[str, Any],
        communication_mode: str,
    ) -> str:
        """
        Generate content according to the supplied SAGE constraints.
        """

        instruction = instruction.strip()

        if not instruction:
            return ""

        if communication_mode == "safety":
            return instruction

        preferred_address = personality.get(
            "preferred_address"
        )

        if (
            communication_mode == "conversational"
            and preferred_address
        ):
            return (
                f"{preferred_address}, "
                f"{instruction}"
            )

        return instruction
