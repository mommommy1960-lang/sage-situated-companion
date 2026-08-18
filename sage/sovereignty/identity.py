from dataclasses import dataclass, field


@dataclass
class OwnerIdentity:
    """
    Persistent owner relationship state.

    Inspired by the MAYA Node / Aurora identity-state architecture,
    but kept independent from any single model provider or device.
    """

    owner_id: str
    preferred_name: str
    relationship: str = "primary_user"
    identity_anchors: list[str] = field(default_factory=list)

    def snapshot(self) -> dict:
        return {
            "owner_id": self.owner_id,
            "preferred_name": self.preferred_name,
            "relationship": self.relationship,
            "identity_anchors": list(self.identity_anchors),
        }
