
"""
SAGE Situated Companion
Intervention Decision Engine

Determines whether Sage should remain silent, observe, respond,
or proactively interrupt based on situated context and event risk.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class InterventionAction(str, Enum):
    SILENT = "silent"
    OBSERVE = "observe"
    RESPOND = "respond"
    INTERRUPT = "interrupt"


@dataclass
class InterventionDecision:
    action: InterventionAction
    reason: str
    priority: float
    confidence: float


class InterventionEngine:
    """
    Evaluates situated events and determines whether intervention
    is justified.

    The engine deliberately separates perception from action:
    detecting something does not automatically mean Sage should
    interrupt the user.
    """

    def evaluate(
        self,
        *,
        event_type: str,
        payload: dict[str, Any],
        confidence: float = 1.0,
        safety_level: float = 0.0,
        activity: str | None = None,
        conversation_active: bool = False,
    ) -> InterventionDecision:

        confidence = self._clamp(confidence)
        safety_level = self._clamp(safety_level)

        # Immediate safety conditions outrank ordinary interaction.
        if safety_level >= 0.85:
            return InterventionDecision(
                action=InterventionAction.INTERRUPT,
                reason="high_safety_risk",
                priority=1.0,
                confidence=confidence,
            )

        # Moderate safety concerns deserve attention without
        # automatically escalating to an emergency interruption.
        if safety_level >= 0.50:
            return InterventionDecision(
                action=InterventionAction.RESPOND,
                reason="moderate_safety_risk",
                priority=0.75,
                confidence=confidence,
            )

        # Direct requests from the user should normally receive
        # a response.
        if event_type in {"request", "question", "command"}:
            return InterventionDecision(
                action=InterventionAction.RESPOND,
                reason="direct_user_request",
                priority=0.70,
                confidence=confidence,
            )

        # Low-confidence perception should not trigger unnecessary
        # interruptions.
        if confidence < 0.50:
            return InterventionDecision(
                action=InterventionAction.OBSERVE,
                reason="low_confidence_observation",
                priority=0.20,
                confidence=confidence,
            )

        # Context changes are useful for maintaining situated state
        # but normally do not require Sage to speak.
        if event_type in {"location", "activity", "context"}:
            return InterventionDecision(
                action=InterventionAction.OBSERVE,
                reason="context_update",
                priority=0.25,
                confidence=confidence,
            )

        # During an active conversation, relevant conversational
        # events may justify a normal response.
        if conversation_active and event_type == "conversation":
            return InterventionDecision(
                action=InterventionAction.RESPOND,
                reason="active_conversation",
                priority=0.60,
                confidence=confidence,
            )

        return InterventionDecision(
            action=InterventionAction.SILENT,
            reason="no_intervention_required",
            priority=0.0,
            confidence=confidence,
        )

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))
