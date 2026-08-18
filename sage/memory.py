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
import hashlib


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
    explicit_remember: bool = False

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

    def compute_content_hash(self) -> str:
        """
        Compute a deterministic hash of the memory content.
        Used for duplicate detection.
        """
        normalized = self.content.strip().lower()
        return hashlib.md5(normalized.encode()).hexdigest()

    @staticmethod
    def assess_significance(
        content: str,
        category: str = "general",
        confidence: float = 1.0,
        explicit_remember: bool = False,
    ) -> float:
        """
        Deterministically assess significance of a memory (0.0 to 1.0).
        
        Significance is based on:
        - Explicit remember requests: always 1.0
        - System/safety categories: elevated base significance
        - Confidence level: multiplied with base significance
        - Content length/structure: minimal adjustment
        
        This is deterministic and does not use external APIs or LLMs.
        """
        if explicit_remember:
            return 1.0

        # Base significance by category
        base_significance = {
            "safety": 0.95,
            "system": 0.90,
            "user_preference": 0.85,
            "conversation": 0.50,
            "situated_event": 0.60,
            "general": 0.35,
        }.get(category, 0.35)

        # Apply confidence modifier
        assessed = base_significance * max(0.0, min(1.0, confidence))

        # Penalize very short or empty content slightly
        if not content or len(content.strip()) < 3:
            assessed *= 0.3

        # Clamp to valid range
        return max(0.0, min(1.0, assessed))


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

    def _find_duplicate_memory(
        self,
        content: str,
        category: str,
        similarity_threshold: float = 0.95,
    ) -> Memory | None:
        """
        Check if a similar memory already exists.
        Returns the existing memory if found, None otherwise.
        
        This prevents obvious duplicates from accumulating.
        """
        # Normalize whitespace: convert multiple spaces to single space
        normalized_content = ' '.join(
            content.strip().lower().split()
        )
        new_hash = hashlib.md5(
            normalized_content.encode()
        ).hexdigest()

        for memory in self.memories.values():
            if memory.category != category:
                continue

            # Normalize existing memory content the same way
            normalized_existing = ' '.join(
                memory.content.strip().lower().split()
            )
            existing_hash = hashlib.md5(
                normalized_existing.encode()
            ).hexdigest()

            if existing_hash == new_hash:
                return memory

        return None

    def remember(
        self,
        content: str,
        category: str = "general",
        importance: float | None = None,
        metadata: dict[str, Any] | None = None,
        explicit_remember: bool = False,
        confidence: float = 1.0,
    ) -> Memory:
        """
        Record a new memory.
        
        If no importance is provided, it is computed deterministically
        from content, category, confidence, and explicit_remember flag.
        
        If a duplicate memory already exists in the same category,
        that existing memory is returned instead.
        """

        # Check for duplicates
        duplicate = self._find_duplicate_memory(content, category)
        if duplicate is not None:
            # Update access count for existing memory
            duplicate.access_count += 1
            duplicate.last_accessed = datetime.now(timezone.utc)
            self.save()
            return duplicate

        # Compute significance if not provided
        if importance is None:
            importance = Memory.assess_significance(
                content=content,
                category=category,
                confidence=confidence,
                explicit_remember=explicit_remember,
            )
        else:
            importance = max(0.0, min(1.0, importance))

        memory = Memory(
            content=content,
            category=category,
            importance=importance,
            metadata=metadata or {},
            explicit_remember=explicit_remember,
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

    def retrieve_relevant_memories(
        self,
        query: str | None = None,
        context_keywords: list[str] | None = None,
        limit: int = 5,
        min_importance: float = 0.4,
    ) -> list[Memory]:
        """
        Retrieve memories relevant to the current interaction.
        
        Filters by:
        - Query text matching (if provided)
        - Context keywords matching (if provided)
        - Minimum importance threshold
        - Sorted by importance and recency
        
        This is deterministic and testable. Empty query returns
        no results to avoid dumping entire memory into every interaction.
        
        When a query or keywords are provided, only memories matching
        those criteria are returned. No fallback to unrelated memories.
        """
        if not query and not context_keywords:
            return []

        results = list(self.memories.values())

        # Filter by minimum importance
        results = [
            m for m in results
            if m.importance >= min_importance
        ]

        # Filter by query text (strict: if query given, only return matches)
        if query:
            query_terms = query.lower().split()
            # Filter out single-letter terms to avoid false substring matches
            # (single letters often appear in other words as substrings)
            query_terms = [t for t in query_terms if len(t) > 1]
            if query_terms:
                query_results = [
                    m for m in results
                    if any(
                        term in m.content.lower()
                        for term in query_terms
                    )
                ]
                # No fallback: if query provided, only matching memories returned
                results = query_results
            else:
                # If only single-letter terms, return empty
                results = []

        # Filter by context keywords (strict: if keywords given, only return matches)
        if context_keywords:
            context_keywords_lower = [
                k.lower() for k in context_keywords
            ]
            context_results = [
                m for m in results
                if any(
                    keyword in m.content.lower()
                    for keyword in context_keywords_lower
                )
            ]
            # No fallback: if keywords provided, only matching memories returned
            results = context_results

        # Sort by importance (desc), then recency (desc)
        results.sort(
            key=lambda m: (
                m.importance,
                m.created_at,
            ),
            reverse=True,
        )

        selected = results[:limit]

        # Update access metrics
        for memory in selected:
            memory.access_count += 1
            memory.last_accessed = datetime.now(timezone.utc)

        if selected:
            self.save()

        return selected

    def retrieve_memories_by_category(
        self,
        category: str,
        limit: int = 5,
        min_importance: float = 0.4,
    ) -> list[Memory]:
        """
        Retrieve memories from a specific category.
        
        Sorted by importance and recency.
        """
        results = [
            m for m in self.memories.values()
            if m.category == category
            and m.importance >= min_importance
        ]

        results.sort(
            key=lambda m: (
                m.importance,
                m.created_at,
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
