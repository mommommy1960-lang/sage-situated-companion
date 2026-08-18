from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import uuid


class CapabilityScope(str, Enum):
    SINGLE_OPERATION = "single_operation"
    SESSION = "session"
    OWNER_PERSISTENT = "owner_persistent"


@dataclass
class CapabilityGrant:
    """
    Explicit authorization for a SAGE action.

    This is the local SAGE-side contract. Cryptographic signing from
    MAYA Node will be connected through the SovereignBridge later.
    """

    operation: str
    owner_id: str
    scope: CapabilityScope = CapabilityScope.SINGLE_OPERATION
    metadata: dict = field(default_factory=dict)
    grant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    revoked: bool = False

    def allows(self, operation: str, owner_id: str) -> bool:
        return (
            not self.revoked
            and self.operation == operation
            and self.owner_id == owner_id
        )

    def revoke(self) -> None:
        self.revoked = True
