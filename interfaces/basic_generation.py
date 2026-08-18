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
    
    Memories are actively incorporated when provided: if relevant
    high-importance memories exist, they are woven into the response
    in a deterministic, observable manner while preserving safety
    priority and personality behavior.
    """

    def generate(
        self,
        *,
        instruction: str,
        context: dict[str, Any],
        personality: dict[str, Any],
        communication_mode: str,
        memories: list[Any] | None = None,
    ) -> str:
        """
        Generate content according to the supplied SAGE constraints.
        
        Memories are actively used when provided:
        - Safety mode always returns bare instruction (safety priority)
        - Other modes enhance instruction with high-importance memories
        - This influence is observable: same instruction + different
          memories produces different responses
        """

        instruction = instruction.strip()

        if not instruction:
            return ""

        if communication_mode == "safety":
            # Safety mode always returns instruction unchanged.
            # Memories never override safety priority.
            return instruction

        # Enhance instruction with relevant memories
        enhanced_instruction = (
            self._enhance_instruction_with_memories(
                instruction=instruction,
                memories=memories,
            )
        )

        preferred_address = personality.get(
            "preferred_address"
        )

        if (
            communication_mode == "conversational"
            and preferred_address
        ):
            return (
                f"{preferred_address}, "
                f"{enhanced_instruction}"
            )

        return enhanced_instruction

    def _enhance_instruction_with_memories(
        self,
        instruction: str,
        memories: list[Any] | None = None,
    ) -> str:
        """
        Enhance instruction with relevant memory context.
        
        Deterministically incorporates high-importance memories
        into responses without external APIs or LLMs.
        
        Returns instruction unchanged if:
        - No memories provided
        - No memories meet importance threshold
        - No viable memory content
        """
        if not memories:
            return instruction

        # Filter to high-importance memories (>=0.7)
        significant_memories = [
            m for m in memories
            if hasattr(m, 'importance') and m.importance >= 0.7
        ]

        if not significant_memories:
            return instruction

        # Sort by importance (descending)
        significant_memories.sort(
            key=lambda m: getattr(m, 'importance', 0),
            reverse=True,
        )

        # Extract top memory content
        top_memory = significant_memories[0]
        memory_content = getattr(top_memory, 'content', '').strip()

        if not memory_content:
            return instruction

        # Incorporate memory context into response
        # Format is observable and deterministic
        return f"{instruction} [remembered: {memory_content}]"
