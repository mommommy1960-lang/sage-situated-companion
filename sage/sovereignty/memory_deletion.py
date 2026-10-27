"""Owner-authorized deletion boundary for SAGE's local JSON MemoryStore.

Single-owner local store only. Do not use this adapter for a multi-tenant
hosted service. Storage file must be private to the owner. A successful result
does not assert deletion from backups, replicas, logs, or other devices.
"""
from .bridge import SovereignBridge


def delete_local_memory(*, bridge: SovereignBridge, store, memory_id: str,
                        grant, verify_current_authority):
    """Delete one local memory after fresh authority verification.

    Uses the bridge's single-operation permission consumption and durable
    ledger when configured. A failed file write can require manual recovery;
    no cross-file database transaction exists between JSON and SQLite.
    """
    if not isinstance(memory_id, str) or not memory_id:
        raise ValueError("Nonempty memory ID required")
    if bridge.ledger is None:
        raise ValueError("Audit ledger required")
    # Do not include content or personal metadata in the audit event.
    def effect():
        if memory_id not in store.memories:
            return False
        # MemoryStore.forget currently deletes from RAM before writing JSON.
        # Restore in-memory state on a failed save, then re-raise.
        original = store.memories[memory_id]
        try:
            return store.forget(memory_id)
        except Exception:
            store.memories[memory_id] = original
            raise

    # The existing bridge records success/failure without deleted content.
    return bridge.execute(
        "memory.delete", grant, effect,
        verify_current_authority=verify_current_authority,
    )
