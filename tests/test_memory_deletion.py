import pytest
from sage.memory import MemoryStore
from sage.sovereignty import CapabilityGrant, OwnerIdentity, SovereignBridge
from sage.sovereignty.sqlite_audit import SQLiteAuditLedger
from sage.sovereignty.memory_deletion import delete_local_memory


def setup(tmp_path):
    store = MemoryStore(str(tmp_path / "memories.json"))
    ledger = SQLiteAuditLedger(tmp_path / "audit.db")
    bridge = SovereignBridge(OwnerIdentity("owner-a", "Owner A"), ledger)
    return store, ledger, bridge


def test_authorized_delete_survives_restart_and_has_receipt(tmp_path):
    store, ledger, bridge = setup(tmp_path)
    first = store.remember("synthetic first")
    second = store.remember("synthetic second")
    grant = CapabilityGrant("memory.delete", "owner-a")
    assert delete_local_memory(bridge=bridge, store=store, memory_id=first.memory_id,
                               grant=grant, verify_current_authority=lambda *args: True)
    reopened = MemoryStore(str(tmp_path / "memories.json"))
    assert first.memory_id not in reopened.memories
    assert second.memory_id in reopened.memories
    ledger.close()
    receipts = SQLiteAuditLedger(tmp_path / "audit.db")
    assert receipts.verify_integrity()
    assert receipts.entries[-1].operation == "operation_result"
    assert "synthetic first" not in str(receipts.entries)
    receipts.close()


def test_other_owner_denied_and_memory_preserved(tmp_path):
    store, ledger, bridge = setup(tmp_path)
    memory = store.remember("synthetic private")
    with pytest.raises(PermissionError):
        delete_local_memory(bridge=bridge, store=store, memory_id=memory.memory_id,
                            grant=CapabilityGrant("memory.delete", "owner-b"),
                            verify_current_authority=lambda *args: True)
    assert memory.memory_id in MemoryStore(str(tmp_path / "memories.json")).memories
    ledger.close()


def test_verifier_outage_fails_closed(tmp_path):
    store, ledger, bridge = setup(tmp_path)
    memory = store.remember("synthetic private")
    def outage(*args):
        raise ConnectionError("unavailable")
    with pytest.raises(PermissionError):
        delete_local_memory(bridge=bridge, store=store, memory_id=memory.memory_id,
                            grant=CapabilityGrant("memory.delete", "owner-a"),
                            verify_current_authority=outage)
    assert memory.memory_id in store.memories
    ledger.close()


def test_repeat_deletion_requires_fresh_grant(tmp_path):
    store, ledger, bridge = setup(tmp_path)
    memory = store.remember("synthetic private")
    grant = CapabilityGrant("memory.delete", "owner-a")
    kwargs = dict(bridge=bridge, store=store, memory_id=memory.memory_id,
                  verify_current_authority=lambda *args: True)
    assert delete_local_memory(grant=grant, **kwargs)
    with pytest.raises(PermissionError):
        delete_local_memory(grant=grant, **kwargs)
    assert delete_local_memory(grant=CapabilityGrant("memory.delete", "owner-a"), **kwargs) is False
    ledger.close()
