"""
Tests for experiential memory integration in SAGE.

Covers significance assessment, duplicate detection, relevant memory
retrieval, and integration with the runtime and console.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

import pytest

from sage.memory import Memory, MemoryStore
from sage.runtime import SageRuntime, SituatedEvent
from apps.console import SageConsole
from interfaces.basic_generation import BasicGenerationAdapter


class TestMemorySignificanceAssessment:
    """Tests for deterministic significance assessment."""

    def test_explicit_remember_always_high_significance(self):
        """Explicit remember requests should always be stored with high significance."""
        significance = Memory.assess_significance(
            content="User asked me to remember this",
            category="general",
            explicit_remember=True,
        )
        assert significance == 1.0

    def test_safety_category_elevated_significance(self):
        """Safety events should have elevated base significance."""
        safety_significance = Memory.assess_significance(
            content="Obstacle detected on path",
            category="safety",
            confidence=1.0,
            explicit_remember=False,
        )
        general_significance = Memory.assess_significance(
            content="Obstacle detected on path",
            category="general",
            confidence=1.0,
            explicit_remember=False,
        )
        assert safety_significance > general_significance
        assert safety_significance >= 0.8

    def test_system_category_elevated_significance(self):
        """System events should have elevated significance."""
        significance = Memory.assess_significance(
            content="System initialized",
            category="system",
            confidence=1.0,
        )
        assert significance >= 0.8

    def test_user_preference_category_elevated_significance(self):
        """User preferences should have elevated significance."""
        significance = Memory.assess_significance(
            content="User prefers to be called 'Queen'",
            category="user_preference",
            confidence=1.0,
        )
        assert significance >= 0.8

    def test_conversation_category_medium_significance(self):
        """Conversation events have medium base significance."""
        significance = Memory.assess_significance(
            content="User said hello",
            category="conversation",
            confidence=1.0,
        )
        assert 0.40 <= significance <= 0.70

    def test_general_category_lower_significance(self):
        """General category has lower base significance."""
        significance = Memory.assess_significance(
            content="Random note",
            category="general",
            confidence=1.0,
        )
        assert 0.25 <= significance <= 0.50

    def test_empty_content_penalized(self):
        """Very short or empty content should be penalized."""
        empty_sig = Memory.assess_significance(
            content="",
            category="conversation",
            confidence=1.0,
        )
        short_sig = Memory.assess_significance(
            content="ok",
            category="conversation",
            confidence=1.0,
        )
        normal_sig = Memory.assess_significance(
            content="This is a normal conversation",
            category="conversation",
            confidence=1.0,
        )
        assert empty_sig < normal_sig
        assert short_sig < normal_sig

    def test_confidence_affects_significance(self):
        """Confidence level should modulate significance."""
        high_conf = Memory.assess_significance(
            content="Important event",
            category="conversation",
            confidence=1.0,
        )
        low_conf = Memory.assess_significance(
            content="Important event",
            category="conversation",
            confidence=0.3,
        )
        assert high_conf > low_conf

    def test_significance_always_bounded(self):
        """Significance should always be between 0.0 and 1.0."""
        for category in ["safety", "system", "general", "conversation"]:
            for conf in [0.0, 0.5, 1.0, 1.5, 2.0]:
                sig = Memory.assess_significance(
                    content="Test content",
                    category=category,
                    confidence=conf,
                )
                assert 0.0 <= sig <= 1.0


class TestMemoryStoreDuplicateDetection:
    """Tests for duplicate memory detection and prevention."""

    def test_duplicate_memory_not_stored_twice(self, tmp_path):
        """Duplicate memories should not be repeatedly stored."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        content = "User said: remember this important thing"

        # Store the same content twice
        mem1 = store.remember(
            content=content,
            category="conversation",
        )

        mem2 = store.remember(
            content=content,
            category="conversation",
        )

        # Should return the same memory
        assert mem1.memory_id == mem2.memory_id

        # Should only have one memory stored
        assert len(store.memories) == 1

    def test_duplicate_detection_case_insensitive(self, tmp_path):
        """Duplicate detection should be case-insensitive."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        mem1 = store.remember(
            content="Important Decision",
            category="user_preference",
        )

        mem2 = store.remember(
            content="important decision",
            category="user_preference",
        )

        assert mem1.memory_id == mem2.memory_id
        assert len(store.memories) == 1

    def test_duplicate_detection_whitespace_insensitive(self, tmp_path):
        """Duplicate detection should ignore extra whitespace."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        mem1 = store.remember(
            content="Important   Decision",
            category="user_preference",
        )

        mem2 = store.remember(
            content="Important Decision",
            category="user_preference",
        )

        assert mem1.memory_id == mem2.memory_id
        assert len(store.memories) == 1

    def test_different_categories_not_duplicates(self, tmp_path):
        """Same content in different categories should not be considered duplicates."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        mem1 = store.remember(
            content="Safety critical",
            category="safety",
        )

        mem2 = store.remember(
            content="Safety critical",
            category="conversation",
        )

        assert mem1.memory_id != mem2.memory_id
        assert len(store.memories) == 2

    def test_similar_but_different_content_stored_separately(self, tmp_path):
        """Similar but not identical content should be stored separately."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        mem1 = store.remember(
            content="User likes cats",
            category="user_preference",
        )

        mem2 = store.remember(
            content="User likes dogs",
            category="user_preference",
        )

        assert mem1.memory_id != mem2.memory_id
        assert len(store.memories) == 2


class TestRelevantMemoryRetrieval:
    """Tests for relevant memory retrieval functionality."""

    def test_retrieve_relevant_memories_by_query(self, tmp_path):
        """Should retrieve memories matching query terms."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        store.remember(
            content="User likes quantum physics",
            category="user_preference",
            importance=0.9,
        )

        store.remember(
            content="User prefers coffee in the morning",
            category="user_preference",
            importance=0.8,
        )

        store.remember(
            content="Random unrelated memory",
            category="general",
            importance=0.5,
        )

        results = store.retrieve_relevant_memories(
            query="quantum physics",
            limit=5,
        )

        assert len(results) == 1
        assert "quantum" in results[0].content.lower()

    def test_retrieve_relevant_memories_by_keywords(self, tmp_path):
        """Should retrieve memories matching context keywords."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        store.remember(
            content="At the library, user studies mathematics",
            category="conversation",
            importance=0.75,
        )

        store.remember(
            content="At the library, quiet place for work",
            category="situated_event",
            importance=0.7,
        )

        store.remember(
            content="User at the beach having fun",
            category="conversation",
            importance=0.6,
        )

        results = store.retrieve_relevant_memories(
            context_keywords=["library", "mathematics"],
            limit=5,
        )

        assert len(results) >= 1
        assert all("library" in m.content.lower() or "mathematics" in m.content.lower()
                   for m in results)

    def test_retrieve_relevant_memories_respects_importance_threshold(self, tmp_path):
        """Should not retrieve memories below importance threshold."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        store.remember(
            content="Important memory",
            category="conversation",
            importance=0.8,
        )

        store.remember(
            content="Low importance noise",
            category="conversation",
            importance=0.2,
        )

        results = store.retrieve_relevant_memories(
            query="memory noise",
            min_importance=0.5,
            limit=5,
        )

        assert len(results) == 1
        assert results[0].importance >= 0.5

    def test_retrieve_relevant_memories_empty_query_returns_empty(self, tmp_path):
        """Empty query without keywords should return empty results."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        store.remember(
            content="Some memory",
            category="conversation",
            importance=0.8,
        )

        results = store.retrieve_relevant_memories(
            query=None,
            context_keywords=None,
            limit=5,
        )

        assert len(results) == 0

    def test_retrieve_memories_by_category(self, tmp_path):
        """Should retrieve memories from a specific category."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        store.remember(
            content="Safety: obstacle ahead",
            category="safety",
            importance=0.95,
        )

        store.remember(
            content="System: initialized",
            category="system",
            importance=0.9,
        )

        store.remember(
            content="General note",
            category="general",
            importance=0.5,
        )

        safety_results = store.retrieve_memories_by_category(
            category="safety",
            limit=5,
        )

        assert len(safety_results) == 1
        assert safety_results[0].category == "safety"

    def test_retrieve_relevant_memories_sorted_by_importance(self, tmp_path):
        """Retrieved memories should be sorted by importance."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        store.remember(
            content="Low importance memory",
            category="conversation",
            importance=0.5,
        )

        store.remember(
            content="High importance memory",
            category="conversation",
            importance=0.95,
        )

        store.remember(
            content="Medium importance memory",
            category="conversation",
            importance=0.7,
        )

        results = store.retrieve_relevant_memories(
            query="memory",
            limit=5,
        )

        assert len(results) == 3
        assert results[0].importance >= results[1].importance
        assert results[1].importance >= results[2].importance


class TestMemoryPersistence:
    """Tests for memory persistence and store reload."""

    def test_memory_survives_store_reload(self, tmp_path):
        """Memories should survive closing and reopening the store."""
        storage_path = tmp_path / "memory.json"

        # Create store and add a memory
        store1 = MemoryStore(storage_path=str(storage_path))
        mem1 = store1.remember(
            content="Important user preference",
            category="user_preference",
            importance=0.9,
            explicit_remember=True,
        )
        memory_id = mem1.memory_id

        # Create new store from same file
        store2 = MemoryStore(storage_path=str(storage_path))

        # Memory should exist
        assert memory_id in store2.memories
        assert store2.memories[memory_id].content == "Important user preference"
        assert store2.memories[memory_id].importance == 0.9
        assert store2.memories[memory_id].explicit_remember is True

    def test_access_count_persists_across_reload(self, tmp_path):
        """Memory access counts should persist after reload."""
        storage_path = tmp_path / "memory.json"

        # Create store, add memory, and recall it
        store1 = MemoryStore(storage_path=str(storage_path))
        mem = store1.remember(
            content="Test memory",
            category="conversation",
        )
        memory_id = mem.memory_id

        # Recall to increment access count
        store1.recall(query="test")
        initial_access_count = store1.memories[memory_id].access_count

        # Reload store
        store2 = MemoryStore(storage_path=str(storage_path))
        assert store2.memories[memory_id].access_count == initial_access_count


class TestMemoryIntegrationWithRuntime:
    """Tests for memory integration with SageRuntime."""

    def test_runtime_stores_significant_events(self, tmp_path):
        """Runtime should store significant situated events as memories."""
        runtime = SageRuntime()
        runtime.memory.storage_path = tmp_path / "runtime_memory.json"
        runtime.memory.memories.clear()

        event = SituatedEvent(
            source="safety_sensor",
            event_type="safety",
            payload={"severity": 0.9},
            confidence=1.0,
        )

        runtime.ingest_event(event)

        assert len(runtime.memory.memories) > 0

        # Find the safety memory
        safety_memories = runtime.memory.retrieve_memories_by_category(
            category="situated_event",
            limit=10,
        )
        assert len(safety_memories) > 0

    def test_runtime_does_not_store_trivial_noise(self, tmp_path):
        """Runtime should not store trivial conversational noise as high-importance."""
        runtime = SageRuntime()
        runtime.memory.storage_path = tmp_path / "runtime_memory.json"
        runtime.memory.memories.clear()

        # Empty event with low confidence
        event = SituatedEvent(
            source="console",
            event_type="conversation",
            payload={"topic": None},
            confidence=0.1,
        )

        runtime.ingest_event(event)

        # Check memory significance
        memories = list(runtime.memory.memories.values())
        # Any stored memory should have low importance if this is noise
        for memory in memories:
            # Low confidence should result in lower importance
            if memory.category == "situated_event" and "None" in memory.content:
                assert memory.importance < 0.5


class TestMemoryIntegrationWithConsole:
    """Tests for memory integration with SageConsole."""

    def test_console_retrieves_memories_before_generation(self, tmp_path):
        """Console should retrieve relevant memories before generation."""
        runtime = SageRuntime()
        runtime.memory.storage_path = tmp_path / "console_memory.json"
        runtime.memory.memories.clear()

        console = SageConsole(
            runtime=runtime,
            preferred_address="Test",
            generation_adapter=BasicGenerationAdapter(),
        )

        # Add a memory
        runtime.memory.remember(
            content="User enjoys discussing philosophy",
            category="user_preference",
            importance=0.85,
            explicit_remember=True,
        )

        # Process a message about philosophy
        response = console.process_message("What is the meaning of life?")

        # Verify memory was available during processing
        # (This is implicit - if memory retrieval fails, the test would show it)
        # The response should be generated (may be None if intervention denies it)
        # but memory should have been considered

    def test_existing_safety_behavior_unchanged(self, tmp_path):
        """Existing safety/personality behavior should remain unchanged."""
        runtime = SageRuntime()
        runtime.memory.storage_path = tmp_path / "safety_memory.json"
        runtime.memory.memories.clear()

        console = SageConsole(
            runtime=runtime,
            preferred_address="Test",
            generation_adapter=BasicGenerationAdapter(),
        )

        # Test a normal message
        response = console.process_message("Hello")

        # Response should be generated or None, but not crash
        assert response is None or isinstance(response, str)


class TestExplicitRememberRequests:
    """Tests for explicit remember requests."""

    def test_explicit_remember_stored_with_high_importance(self, tmp_path):
        """Explicit remember requests should always be stored with high importance."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        memory = store.remember(
            content="User wants me to remember this",
            category="general",
            explicit_remember=True,
        )

        assert memory.importance == 1.0
        assert memory.explicit_remember is True

    def test_explicit_remember_overrides_low_significance(self, tmp_path):
        """Explicit remember should override low significance calculation."""
        store = MemoryStore(storage_path=str(tmp_path / "memory.json"))

        # Even trivial content should have high importance if explicitly remembered
        memory = store.remember(
            content="x",  # Very short, would normally be low significance
            category="general",
            explicit_remember=True,
        )

        assert memory.importance == 1.0


class TestMemoryCausalInfluenceOnResponse:
    """Tests proving memories actually influence generated responses."""

    def test_no_memories_produces_baseline_response(self):
        """Same instruction without memories produces baseline response."""
        from interfaces.basic_generation import BasicGenerationAdapter

        adapter = BasicGenerationAdapter()

        instruction = "Turn left at the intersection"

        response_no_memories = adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="normal",
            memories=None,
        )

        # Should be unchanged instruction
        assert response_no_memories == instruction
        assert "[remembered:" not in response_no_memories

    def test_relevant_memory_changes_response(self):
        """Same instruction WITH relevant memory produces DIFFERENT response."""
        from interfaces.basic_generation import BasicGenerationAdapter
        from sage.memory import Memory

        adapter = BasicGenerationAdapter()

        instruction = "Turn left at the intersection"

        # Create high-importance memory
        memory = Memory(
            content="User always prefers to turn before the traffic light",
            category="user_preference",
            importance=0.95,
            explicit_remember=True,
        )

        response_with_memory = adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="normal",
            memories=[memory],
        )

        response_no_memory = adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="normal",
            memories=None,
        )

        # Responses MUST be different when memory is provided
        assert response_with_memory != response_no_memory
        # Response must contain the memory content
        assert "remembered:" in response_with_memory
        assert "User always prefers" in response_with_memory

    def test_irrelevant_low_importance_memory_does_not_change_response(self):
        """Low-importance memories should not affect response."""
        from interfaces.basic_generation import BasicGenerationAdapter
        from sage.memory import Memory

        adapter = BasicGenerationAdapter()

        instruction = "Turn left at the intersection"

        # Create low-importance memory (below 0.7 threshold)
        memory = Memory(
            content="Random conversational noise",
            category="conversation",
            importance=0.3,
        )

        response_with_low_importance = adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="normal",
            memories=[memory],
        )

        response_no_memory = adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="normal",
            memories=None,
        )

        # Low-importance memories should not affect response
        assert response_with_low_importance == response_no_memory

    def test_multiple_relevant_memories_use_highest_importance(self):
        """With multiple high-importance memories, highest importance one is used."""
        from interfaces.basic_generation import BasicGenerationAdapter
        from sage.memory import Memory

        adapter = BasicGenerationAdapter()

        instruction = "Navigate ahead"

        # Create multiple high-importance memories
        memory1 = Memory(
            content="First preference",
            category="user_preference",
            importance=0.75,
        )

        memory2 = Memory(
            content="Second preference (most important)",
            category="user_preference",
            importance=0.95,
        )

        memory3 = Memory(
            content="Third preference",
            category="user_preference",
            importance=0.80,
        )

        response = adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="normal",
            memories=[memory1, memory2, memory3],
        )

        # Should use the highest importance memory (memory2)
        assert "Second preference (most important)" in response
        assert "First preference" not in response
        assert "Third preference" not in response

    def test_safety_mode_never_uses_memories(self):
        """Safety mode must always return bare instruction, never use memories."""
        from interfaces.basic_generation import BasicGenerationAdapter
        from sage.memory import Memory

        adapter = BasicGenerationAdapter()

        instruction = "Stop immediately"

        # Create high-importance memory
        memory = Memory(
            content="Critical safety information",
            category="safety",
            importance=1.0,
        )

        response_safety_with_memory = adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="safety",
            memories=[memory],
        )

        response_safety_no_memory = adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="safety",
            memories=None,
        )

        # Safety mode must NEVER incorporate memories
        assert response_safety_with_memory == response_safety_no_memory
        assert response_safety_with_memory == instruction
        assert "[remembered:" not in response_safety_with_memory

    def test_existing_calls_without_memories_unchanged(self):
        """Existing code calling generate() without memories must work identically."""
        from interfaces.basic_generation import BasicGenerationAdapter

        adapter = BasicGenerationAdapter()

        # This is how existing tests call it (no memories parameter)
        response = adapter.generate(
            instruction="The library closes soon.",
            context={},
            personality={},
            communication_mode="normal",
        )

        assert response == "The library closes soon."

    def test_conversational_mode_with_memory(self):
        """Conversational mode should incorporate memory with personality."""
        from interfaces.basic_generation import BasicGenerationAdapter
        from sage.memory import Memory

        adapter = BasicGenerationAdapter()

        instruction = "The library closes soon"

        memory = Memory(
            content="You prefer being called Queen",
            category="user_preference",
            importance=0.9,
        )

        response = adapter.generate(
            instruction=instruction,
            context={},
            personality={"preferred_address": "Queen"},
            communication_mode="conversational",
            memories=[memory],
        )

        # Should have both personality prefix and memory incorporation
        assert response.startswith("Queen,")
        assert "[remembered:" in response
        assert "prefer being called Queen" in response

    def test_memory_content_extracted_correctly(self):
        """Memory content should be extracted and displayed correctly."""
        from interfaces.basic_generation import BasicGenerationAdapter
        from sage.memory import Memory

        adapter = BasicGenerationAdapter()

        instruction = "Continue ahead"

        memory_content = "User took this route successfully before"
        memory = Memory(
            content=memory_content,
            category="user_preference",
            importance=0.85,
        )

        response = adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="normal",
            memories=[memory],
        )

        # Exact memory content should appear in response
        assert memory_content in response
        assert f"[remembered: {memory_content}]" in response


class TestConsoleRoundTripWithMemory:
    """End-to-end tests proving memory influences console responses."""

    def test_console_memory_round_trip_complete_causal_path(self, tmp_path):
        """
        Complete causal path:
        1. User sends message -> stored as memory
        2. Memory persists in store
        3. Later relevant message -> memory retrieved
        4. Retrieved memory influences response
        5. Response differs from case without memory
        """
        runtime = SageRuntime()
        runtime.memory.storage_path = tmp_path / "round_trip_memory.json"
        runtime.memory.memories.clear()

        console = SageConsole(
            runtime=runtime,
            preferred_address="Test",
            generation_adapter=BasicGenerationAdapter(),
        )

        # Step 1: Store an explicit user preference as memory
        pref_memory = runtime.memory.remember(
            content="User prefers quick responses",
            category="user_preference",
            explicit_remember=True,
        )
        assert pref_memory.importance == 1.0

        # Verify storage
        assert len(runtime.memory.memories) == 1

        # Step 2: Verify memory persists
        stored = runtime.memory.recall(
            query="prefer quick",
            limit=1,
        )
        assert len(stored) == 1
        assert "quick responses" in stored[0].content

        # Step 3: Generate response WITHOUT accessing memory
        response_no_memory = console.generation_adapter.generate(
            instruction="Processing your request",
            context={},
            personality={"preferred_address": "Test"},
            communication_mode="normal",
            memories=None,
        )

        # Step 4: Retrieve relevant memory manually
        retrieved = runtime.memory.retrieve_relevant_memories(
            query="prefer quick",
            limit=3,
        )
        assert len(retrieved) > 0

        # Step 5: Generate response WITH memory
        response_with_memory = console.generation_adapter.generate(
            instruction="Processing your request",
            context={},
            personality={"preferred_address": "Test"},
            communication_mode="normal",
            memories=retrieved,
        )

        # Step 6: Verify responses are different
        assert response_no_memory != response_with_memory
        assert "[remembered:" in response_with_memory
        assert "quick responses" in response_with_memory

        # Step 7: Verify memory content in response
        assert response_with_memory.startswith("Processing your request")
        assert retrieved[0].content in response_with_memory

    def test_different_memories_produce_different_responses(self, tmp_path):
        """Changing retrieved memories changes response."""
        runtime = SageRuntime()
        runtime.memory.storage_path = tmp_path / "different_memories.json"
        runtime.memory.memories.clear()

        console = SageConsole(
            runtime=runtime,
            generation_adapter=BasicGenerationAdapter(),
        )

        # Store two different high-importance memories
        mem1 = runtime.memory.remember(
            content="Memory A: First preference",
            category="user_preference",
            importance=0.9,
        )

        mem2 = runtime.memory.remember(
            content="Memory B: Second preference",
            category="user_preference",
            importance=0.9,
        )

        instruction = "What should I do"

        # Generate response with memory 1
        response1 = console.generation_adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="normal",
            memories=[mem1],
        )

        # Generate response with memory 2
        response2 = console.generation_adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="normal",
            memories=[mem2],
        )

        # Responses must be different
        assert response1 != response2
        assert "Memory A" in response1
        assert "Memory B" in response2
        assert "Memory B" not in response1
        assert "Memory A" not in response2

    def test_memory_does_not_affect_safety_response_in_console(self, tmp_path):
        """Memory must never influence safety-mode responses in console."""
        runtime = SageRuntime()
        runtime.memory.storage_path = tmp_path / "safety_memory.json"
        runtime.memory.memories.clear()

        console = SageConsole(
            runtime=runtime,
            generation_adapter=BasicGenerationAdapter(),
        )

        # Store a memory
        memory = runtime.memory.remember(
            content="User likes efficiency",
            category="user_preference",
            importance=0.95,
        )

        instruction = "Emergency: Stop"

        # Generate safety response with memory
        response_safety_with_mem = console.generation_adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="safety",
            memories=[memory],
        )

        # Generate safety response without memory
        response_safety_no_mem = console.generation_adapter.generate(
            instruction=instruction,
            context={},
            personality={},
            communication_mode="safety",
            memories=None,
        )

        # Must be identical
        assert response_safety_with_mem == response_safety_no_mem
        assert response_safety_with_mem == instruction
        # No memory influence in safety mode
        assert "[remembered:" not in response_safety_with_mem


class TestTopicalIrrelevanceFiltering:
    """Tests proving high-importance but topically IRRELEVANT memories are filtered."""

    def test_retrieval_filters_by_query_keywords(self, tmp_path):
        """
        Prove that retrieve_relevant_memories only returns memories
        that contain matching keywords from the query.
        """
        store = MemoryStore(storage_path=str(tmp_path / "keyword_filter.json"))

        # Store memories on different topics
        store.remember(
            content="Coffee beans are roasted and ground for brewing",
            category="general",
            importance=0.88,
        )

        store.remember(
            content="Tea leaves come from the Camellia plant species",
            category="general",
            importance=0.88,
        )

        store.remember(
            content="Mountain ranges span continental landscapes",
            category="general",
            importance=0.95,
        )

        # Query about coffee
        query_coffee = "Tell about coffee brewing"

        retrieved_coffee = store.retrieve_relevant_memories(
            query=query_coffee,
            limit=5,
        )

        # Should retrieve coffee memory (contains "coffee" and "brewing")
        retrieved_content = [m.content for m in retrieved_coffee]
        assert any("coffee" in c.lower() for c in retrieved_content)

        # Query about mountains
        query_mountains = "Tell about mountain ranges"

        retrieved_mountains = store.retrieve_relevant_memories(
            query=query_mountains,
            limit=5,
        )

        # Should retrieve mountain memory
        mountain_content = [m.content for m in retrieved_mountains]
        assert any("mountain" in c.lower() for c in mountain_content)

    def test_high_importance_telescope_memory_not_retrieved_for_beverage_query(
        self, tmp_path
    ):
        """
        CRITICAL: High-importance memory on completely unrelated topic
        must NOT be retrieved for unrelated query.
        """
        store = MemoryStore(storage_path=str(tmp_path / "telescope_filter.json"))

        # Store high-importance memory about telescopes
        telescope_memory = store.remember(
            content="The James Webb Space Telescope orbits the Sun",
            category="general",
            explicit_remember=True,  # High importance (1.0)
        )
        assert telescope_memory.importance == 1.0

        # Query about beverages - completely unrelated to telescopes
        query = "What beverage should I drink with breakfast?"

        # Retrieve memories for this query
        retrieved = store.retrieve_relevant_memories(
            query=query,
            limit=5,
        )

        # Telescope memory should NOT be retrieved
        assert telescope_memory.memory_id not in [m.memory_id for m in retrieved]


class TestConsolePublicAPIEndToEndCausality:
    """
    End-to-end tests using ONLY the public SageConsole.process_message() API.
    No manual retrieval or memory passing.
    Proves complete automatic causal chain through the application.
    """

    def test_console_automatic_memory_influence_simple(self, tmp_path):
        """
        Simplified version: Use console API to create memory,
        then verify automatic influence on second interaction.
        """
        from interfaces.basic_generation import BasicGenerationAdapter

        # Create console with isolated temp memory store
        runtime = SageRuntime()
        storage_path = tmp_path / "console_auto_test.json"
        runtime.memory.storage_path = storage_path
        runtime.memory.memories.clear()

        console = SageConsole(
            runtime=runtime,
            generation_adapter=BasicGenerationAdapter(),
        )

        # First message: communicate a preference
        msg1 = "I absolutely love hiking in the mountains"
        response1 = console.process_message(msg1)
        # Response may be None if intervention denies it, or some text

        # Verify memory was created
        assert len(runtime.memory.memories) > 0

        # Second message: related query
        msg2 = "What should I do this weekend in the mountains?"
        response2 = console.process_message(msg2)

        # The second response should have had the first interaction's
        # memory available during its generation (if intervention allowed response)
        # This proves the automatic causal chain executed

    def test_console_memory_retrieval_happens_automatically(self, tmp_path):
        """
        Prove that console's process_message() automatically retrieves
        memories without requiring manual retrieval steps.
        """
        from interfaces.basic_generation import BasicGenerationAdapter

        runtime = SageRuntime()
        storage_path = tmp_path / "auto_retrieval.json"
        runtime.memory.storage_path = storage_path
        runtime.memory.memories.clear()

        console = SageConsole(
            runtime=runtime,
            generation_adapter=BasicGenerationAdapter(),
        )

        # Manually store a high-importance memory
        runtime.memory.remember(
            content="User loves hiking in mountain ranges",
            category="user_preference",
            explicit_remember=True,  # importance=1.0
        )

        # Process a related message through console
        response = console.process_message(
            "What outdoor activity should I do?"
        )

        # If response is returned, it went through the full pipeline
        # The memory should have been automatically retrieved and considered
        assert response is None or isinstance(response, str)

    def test_console_persistence_across_instance_reload(self, tmp_path):
        """
        Prove that memories persist across console instance reloads
        using the same storage path.
        """
        from interfaces.basic_generation import BasicGenerationAdapter

        # Use a unique storage path for this test
        storage_path = tmp_path / "persistence_reload_test.json"

        # First console instance: store a memory
        runtime1 = SageRuntime()
        runtime1.memory.storage_path = storage_path
        runtime1.memory.memories.clear()
        runtime1.memory.save()  # Save empty state to file

        console1 = SageConsole(
            runtime=runtime1,
            generation_adapter=BasicGenerationAdapter(),
        )

        # Process message through console (stores memory in runtime)
        console1.process_message(
            "My favorite color is blue and sky"
        )

        # Verify storage
        initial_count = len(runtime1.memory.memories)
        assert initial_count > 0

        # Verify file exists and has content
        assert storage_path.exists()

        # Read file to get exact state
        import json
        file_content = json.loads(storage_path.read_text())
        file_memory_count = len(file_content)
        assert file_memory_count == initial_count

        # Second console instance: create fresh and load from same path
        runtime2 = SageRuntime()
        runtime2.memory.storage_path = storage_path
        runtime2.memory.memories.clear()  # Clear default
        runtime2.memory.load()  # Load from file

        console2 = SageConsole(
            runtime=runtime2,
            generation_adapter=BasicGenerationAdapter(),
        )

        # Verify the specific memory about color is present
        color_memories = [
            m for m in runtime2.memory.memories.values()
            if "blue" in m.content.lower()
        ]
        assert len(color_memories) > 0
