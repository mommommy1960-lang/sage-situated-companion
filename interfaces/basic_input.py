"""
SAGE Situated Companion
Roadmap 2 — Basic Input Adapter

Provides the first concrete implementation of the InputAdapter
contract defined in interfaces/contracts.py.

This adapter accepts normalized ExternalInput data and translates it
into the SituatedEvent representation understood by the frozen
SAGE Core V1 runtime.
"""

from interfaces.contracts import ExternalInput, InputAdapter
from sage.runtime import SituatedEvent


class BasicInputAdapter(InputAdapter):
    """
    Generic concrete adapter for normalized external input.

    This adapter intentionally contains no device-specific logic.
    It demonstrates the complete adapter boundary while preserving
    the frozen SAGE Core V1 architecture.
    """

    def to_situated_event(
        self,
        external_input: ExternalInput,
    ) -> SituatedEvent:
        """
        Translate ExternalInput into a SAGE SituatedEvent.
        """

        return SituatedEvent(
            source=external_input.source,
            event_type=external_input.input_type,
            payload=external_input.payload,
            confidence=external_input.confidence,
            timestamp=external_input.timestamp,
        )
