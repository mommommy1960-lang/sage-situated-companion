"""
SAGE Situated Companion
Interface Contracts

Defines the boundary between the frozen SAGE Core V1 architecture
and external input, generation, output, software, and hardware systems.

Core rule:

    Extend around the core before extending the core.

External systems should translate their native data into these
interface contracts rather than embedding device-specific behavior
inside the verified SAGE core.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sage.runtime import SituatedEvent


@dataclass
class ExternalInput:
    """
    Raw information received from an external system before it has
    been translated into a SAGE SituatedEvent.
    """

    source: str
    input_type: str
    payload: dict[str, Any]
    confidence: float = 1.0
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class OutputRequest:
    """
    A normalized request for an external output system.

    The generation/output layer may eventually route these requests
    to text, speech, displays, notifications, accessibility systems,
    vehicle interfaces, or other supported endpoints.
    """

    content: str
    output_type: str = "text"
    priority: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class OutputResult:
    """
    Result returned by an output adapter after attempting delivery.
    """

    success: bool
    adapter: str
    output_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class InputAdapter(ABC):
    """
    Contract for systems that provide information to SAGE.

    Examples may eventually include:

    - microphones
    - cameras
    - GPS
    - navigation services
    - mobile devices
    - bicycles
    - vehicles
    - wearable sensors
    - software applications

    An adapter receives technology-specific information and converts
    it into the common SituatedEvent representation understood by
    the frozen SAGE Core V1 runtime.
    """

    @abstractmethod
    def to_situated_event(
        self,
        external_input: ExternalInput,
    ) -> SituatedEvent:
        """
        Convert external information into a SAGE SituatedEvent.
        """

        raise NotImplementedError


class OutputAdapter(ABC):
    """
    Contract for systems capable of delivering SAGE output.

    Output adapters remain separate from intervention decisions.
    The core determines whether interaction is warranted; an output
    adapter determines how an approved output reaches the world.
    """

    @abstractmethod
    def deliver(
        self,
        request: OutputRequest,
    ) -> OutputResult:
        """
        Deliver an output request through the adapter.
        """

        raise NotImplementedError


class GenerationAdapter(ABC):
    """
    Contract for systems that transform an approved SAGE response
    intention into generated content.

    A future implementation may connect this contract to a language
    model or another generation system without requiring that model
    to become part of Core V1.
    """

    @abstractmethod
    def generate(
        self,
        *,
        instruction: str,
        context: dict[str, Any],
        personality: dict[str, Any],
        communication_mode: str,
    ) -> str:
        """
        Generate content using situated and personality constraints.
        """

        raise NotImplementedError
