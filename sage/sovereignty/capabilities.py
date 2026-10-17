from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
from threading import Lock
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
    expires_at: datetime | None = None
    consumed: bool = False
    _lock: object = field(default_factory=Lock, repr=False, compare=False)

    def __post_init__(self):
        self.scope = CapabilityScope(self.scope)
        if not self.operation or not self.owner_id:
            raise ValueError("Operation and owner are required")
        if self.created_at.utcoffset() is None:
            raise ValueError("Grant timestamps must be timezone-aware")
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(minutes=5)
        if self.expires_at.utcoffset() is None or self.expires_at <= self.created_at:
            raise ValueError("Expiry must follow creation and be timezone-aware")

    def allows(self, operation: str, owner_id: str, *, now: datetime | None = None) -> bool:
        current = now if now is not None else datetime.now(timezone.utc)
        return (
            not self.revoked
            and not self.consumed
            and current.utcoffset() is not None
            and self.created_at <= current < self.expires_at
            and self.operation == operation
            and self.owner_id == owner_id
        )

    def consume(self, operation: str, owner_id: str, *, now: datetime | None = None) -> bool:
        """Commit a local attempt; single-operation grants cannot be reused."""
        with self._lock:
            if not self.allows(operation, owner_id, now=now):
                return False
            if self.scope == CapabilityScope.SINGLE_OPERATION:
                self.consumed = True
            return True

    def revoke(self) -> None:
        with self._lock:
            self.revoked = True
