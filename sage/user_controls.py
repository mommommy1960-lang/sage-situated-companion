"""User-controlled memory and sensor authorization for Sage."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path

from .memory import MemoryStore


class ActionLevel(IntEnum):
    OBSERVE = 0
    SUGGEST = 1
    ASK = 2
    ACT = 3


@dataclass
class ConsentController:
    sensor_grants: dict[str, bool] = field(default_factory=dict)
    action_grants: dict[str, ActionLevel] = field(default_factory=dict)

    def set_sensor_consent(self, sensor: str, granted: bool) -> None:
        self.sensor_grants[sensor] = bool(granted)

    def require_sensor(self, sensor: str) -> None:
        if self.sensor_grants.get(sensor) is not True:
            raise PermissionError(f"sensor consent denied: {sensor}")

    def grant_action(self, operation: str, level: ActionLevel) -> None:
        self.action_grants[operation] = ActionLevel(level)

    def require_action(self, operation: str, requested: ActionLevel) -> None:
        granted = self.action_grants.get(operation, ActionLevel.OBSERVE)
        if requested > granted:
            raise PermissionError("requested action exceeds explicit grant")


class UserMemoryController:
    def __init__(self, store: MemoryStore):
        self.store = store

    def export(self, destination: str | Path) -> Path:
        path = Path(destination)
        payload = [memory.to_dict() for memory in self.store.memories.values()]
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def correct(self, memory_id: str, corrected_content: str) -> bool:
        memory = self.store.memories.get(memory_id)
        if memory is None or not corrected_content.strip():
            return False
        memory.metadata = {
            **memory.metadata,
            "corrected_by_user": True,
            "previous_content_hash": memory.compute_content_hash(),
        }
        memory.content = corrected_content
        self.store.save()
        return True

    def delete(self, memory_id: str) -> bool:
        return self.store.forget(memory_id)

    def delete_all(self) -> None:
        self.store.clear()
