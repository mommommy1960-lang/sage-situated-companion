"""
SAGE Situated Companion
Personality Continuity Engine

Maintains a stable companion identity while adapting delivery
to safety level, activity, conversational state, and user preferences.
"""

from dataclasses import dataclass, field
from enum import Enum


class CommunicationMode(str, Enum):
    QUIET = "quiet"
    NORMAL = "normal"
    CONVERSATIONAL = "conversational"
    SAFETY = "safety"


@dataclass
class PersonalityProfile:
    name: str = "Sage"
    warmth: float = 0.85
    humor: float = 0.75
    banter: float = 0.80
    directness: float = 0.80
    preferred_address: str | None = None

    traits: list[str] = field(
        default_factory=lambda: [
            "warm",
            "observant",
            "witty",
            "protective",
            "context-aware",
        ]
    )


@dataclass
class ExpressionContext:
    activity: str | None = None
    safety_level: float = 0.0
    conversation_active: bool = False
    user_attention_required: bool = False


class PersonalityEngine:
    """
    Maintains Sage's stable personality while adapting expression
    to the user's immediate situation.
    """

    def __init__(
        self,
        profile: PersonalityProfile | None = None,
    ):
        self.profile = profile or PersonalityProfile()

    def select_mode(
        self,
        context: ExpressionContext,
    ) -> CommunicationMode:

        safety = self._clamp(context.safety_level)

        if safety >= 0.75:
            return CommunicationMode.SAFETY

        if context.activity in {
            "cycling",
            "driving",
            "crossing_street",
            "navigation",
        }:
            if context.user_attention_required:
                return CommunicationMode.QUIET

            return CommunicationMode.NORMAL

        if context.conversation_active:
            return CommunicationMode.CONVERSATIONAL

        return CommunicationMode.NORMAL

    def render(
        self,
        message: str,
        context: ExpressionContext,
    ) -> str:

        mode = self.select_mode(context)

        if mode == CommunicationMode.SAFETY:
            return message.strip()

        if mode == CommunicationMode.QUIET:
            words = message.strip().split()

            if len(words) <= 8:
                return message.strip()

            return " ".join(words[:8])

        return message.strip()

    def update_preference(
        self,
        *,
        preferred_address: str | None = None,
        warmth: float | None = None,
        humor: float | None = None,
        banter: float | None = None,
        directness: float | None = None,
    ) -> PersonalityProfile:

        if preferred_address is not None:
            self.profile.preferred_address = preferred_address

        if warmth is not None:
            self.profile.warmth = self._clamp(warmth)

        if humor is not None:
            self.profile.humor = self._clamp(humor)

        if banter is not None:
            self.profile.banter = self._clamp(banter)

        if directness is not None:
            self.profile.directness = self._clamp(
                directness
            )

        return self.profile

    def snapshot(self) -> PersonalityProfile:
        return self.profile

    @staticmethod
    def _clamp(value: float) -> float:
        return max(
            0.0,
            min(1.0, float(value)),
        )


if __name__ == "__main__":
    personality = PersonalityEngine()

    casual = personality.render(
        "We're passing that bakery again.",
        ExpressionContext(
            activity="walking",
            safety_level=0.0,
            conversation_active=True,
        ),
    )

    safety = personality.render(
        "Car approaching from the right.",
        ExpressionContext(
            activity="cycling",
            safety_level=0.92,
            conversation_active=True,
            user_attention_required=True,
        ),
    )

    print("Conversational:", casual)
    print("Safety:", safety)
