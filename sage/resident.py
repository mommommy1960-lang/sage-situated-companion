"""SAGE Persistent Resident Intelligence lifecycle.

This module defines lifecycle and authorization-state primitives for durable
resident work. It deliberately does not grant external-action authority.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import hashlib
import json


class ResidentState(str, Enum):
    ACTIVE = "active"
    RESEARCHING = "researching"
    WATCHING = "watching"
    REFLECTING = "reflecting"
    QUIESCENT = "quiescent"
    WAITING = "waiting"
    STALLED = "stalled"
    FROZEN = "frozen"
    STOPPED = "stopped"


@dataclass(frozen=True)
class ResidentAuthorization:
    task_id: str
    scopes: tuple[str, ...]
    epoch: int
    expires_at: datetime | None = None
    revoked: bool = False

    def permits(self, scope: str, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        if self.revoked:
            return False
        if self.expires_at is not None and now >= self.expires_at:
            return False
        return scope in self.scopes


@dataclass
class ResidentCheckpoint:
    resident_id: str
    sequence: int
    state: ResidentState
    authorization_epoch: int
    task_id: str | None = None
    objective_digest: str | None = None
    previous_digest: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def digest(self) -> str:
        payload = {
            "resident_id": self.resident_id,
            "sequence": self.sequence,
            "state": self.state.value,
            "authorization_epoch": self.authorization_epoch,
            "task_id": self.task_id,
            "objective_digest": self.objective_digest,
            "previous_digest": self.previous_digest,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ResidentRuntime:
    """Bounded resident lifecycle controller.

    Persistence never expands authority. Restoring a checkpoint requires the
    caller to supply the current authorization epoch; stale state freezes.
    """

    def __init__(self, resident_id: str = "sage"):
        self.resident_id = resident_id
        self.state = ResidentState.STOPPED
        self.sequence = 0
        self.last_checkpoint_digest: str | None = None
        self.authorization: ResidentAuthorization | None = None

    def authorize(self, authorization: ResidentAuthorization) -> None:
        self.authorization = authorization

    def transition(self, state: ResidentState) -> ResidentState:
        if self.state == ResidentState.FROZEN and state not in {
            ResidentState.STOPPED, ResidentState.FROZEN
        }:
            raise PermissionError("frozen resident requires explicit recovery")
        self.state = state
        return self.state

    def can(self, scope: str) -> bool:
        return bool(self.authorization and self.authorization.permits(scope))

    def revoke(self) -> None:
        if self.authorization:
            a = self.authorization
            self.authorization = ResidentAuthorization(
                task_id=a.task_id,
                scopes=a.scopes,
                epoch=a.epoch + 1,
                expires_at=a.expires_at,
                revoked=True,
            )
        self.state = ResidentState.FROZEN

    def checkpoint(self, objective: str | None = None, **metadata: Any) -> ResidentCheckpoint:
        self.sequence += 1
        epoch = self.authorization.epoch if self.authorization else 0
        task_id = self.authorization.task_id if self.authorization else None
        objective_digest = (
            hashlib.sha256(objective.encode("utf-8")).hexdigest()
            if objective is not None else None
        )
        cp = ResidentCheckpoint(
            resident_id=self.resident_id,
            sequence=self.sequence,
            state=self.state,
            authorization_epoch=epoch,
            task_id=task_id,
            objective_digest=objective_digest,
            previous_digest=self.last_checkpoint_digest,
            metadata=metadata,
        )
        self.last_checkpoint_digest = cp.digest()
        return cp

    def restore(self, checkpoint: ResidentCheckpoint, current_authorization: ResidentAuthorization) -> None:
        if checkpoint.resident_id != self.resident_id:
            self.state = ResidentState.FROZEN
            raise PermissionError("resident identity mismatch")
        if current_authorization.revoked:
            self.state = ResidentState.FROZEN
            raise PermissionError("authorization revoked")
        if checkpoint.authorization_epoch != current_authorization.epoch:
            self.state = ResidentState.FROZEN
            raise PermissionError("stale authorization epoch")
        if checkpoint.task_id != current_authorization.task_id:
            self.state = ResidentState.FROZEN
            raise PermissionError("task identity mismatch")
        self.authorization = current_authorization
        self.sequence = checkpoint.sequence
        self.last_checkpoint_digest = checkpoint.digest()
        self.state = checkpoint.state
