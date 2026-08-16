"""
SAGE Situated Companion
Persistent Memory Engine

Stores durable memories independently from the immediate conversation
context so useful information can survive across runtime sessions.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid


@dataclass
class Memory:
    """A single persistent memory."""

    content: str
    category: str = "general"
    importance: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)
    memory_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_accessed: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    access_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["last_accessed"] = self.last_accessed.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Memory":
        restored = dict(data)

        restored["created_at"] = datetime.fromisoformat(
            restored["created_at"]
        )

        restored["last_accessed"] = datetime.fromisoformat(
            restored["last_accessed"]
        )

        return cls(**restored)


class MemoryStore:
    """
    Persistent memory manager for Sage.

    Memories are held in memory while Sage is running and may also
    be serialized to disk for persistence between sessions.
    """

    def __init__(self, storage_path: str = "sage_memory.json"):
        self.storage_path = Path(storage_path)
        self.memories: dict[str, Memory] = {}

        self.load()

    def remember(
        self,
        content: str,
        category: str = "general",
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> Memory:

        importance = max(0.0, min(1.0, importance))

        memory = Memory(
            content=content,
            category=category,
            importance=importance,
            metadata=metadata or {},
        )

        self.memories[memory.memory_id] = memory
        self.save()

        return memory

    def recall(
        self,
        query: str | None = None,
        category: str | None = None,
        limit: int = 10,
    ) -> list[Memory]:

        results = list(self.memories.values())

        if category is not None:
            results = [
                memory
                for memory in results
                if memory.category == category
            ]

        if query:
            terms = query.lower().split()

            results = [
                memory
                for memory in results
                if any(
                    term in memory.content.lower()
                    for term in terms
                )
            ]

        results.sort(
            key=lambda memory: (
                memory.importance,
                memory.created_at,
            ),
            reverse=True,
        )

        selected = results[:limit]

        for memory in selected:
            memory.access_count += 1
            memory.last_accessed = datetime.now(timezone.utc)

        if selected:
            self.save()

        return selected

    def forget(self, memory_id: str) -> bool:
        if memory_id not in self.memories:
            return False

        del self.memories[memory_id]
        self.save()

        return True

    def clear(self) -> None:
        self.memories.clear()
        self.save()

    def save(self) -> None:
        data = [
            memory.to_dict()
            for memory in self.memories.values()
        ]

        self.storage_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load(self) -> None:
        if not self.storage_path.exists():
            return

        try:
            raw = json.loads(
                self.storage_path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            return

        for item in raw:
            try:
                memory = Memory.from_dict(item)
                self.memories[memory.memory_id] = memory
            except (KeyError, TypeError, ValueError):
                continue

    def summary(self) -> dict[str, Any]:
        categories: dict[str, int] = {}

        for memory in self.memories.values():
            categories[memory.category] = (
                categories.get(memory.category, 0) + 1
            )

        return {
            "total_memories": len(self.memories),
            "categories": categories,
            "storage_path": str(self.storage_path),
        }


if __name__ == "__main__":
    memory = MemoryStore()

    saved = memory.remember(
        "Sage persistent memory engine initialized.",
        category="system",
        importance=1.0,
    )

    print("Stored:", saved.memory_id)
    print("Memory state:", memory.summary())
