import sqlite3
import pytest

from sage.sovereignty import OwnerIdentity, CapabilityGrant, SovereignBridge
from sage.sovereignty.sqlite_audit import SQLiteAuditLedger


def test_receipts_survive_reopen(tmp_path):
    db = tmp_path / "receipts.db"
    ledger = SQLiteAuditLedger(db)
    ledger.append("memory.delete_requested", {"owner_id": "owner-a", "record_id": "synthetic-1"})
    expected = ledger.entries[0].entry_hash
    ledger.close()
    reopened = SQLiteAuditLedger(db)
    assert reopened.verify_integrity()
    assert reopened.entries[0].entry_hash == expected
    reopened.close()


def test_tampering_detected_after_reopen(tmp_path):
    db = tmp_path / "receipts.db"
    ledger = SQLiteAuditLedger(db)
    ledger.append("action", {"synthetic": True})
    ledger.close()
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE audit_entries SET operation = 'altered' WHERE idx = 0")
    with pytest.raises(ValueError, match="integrity"):
        SQLiteAuditLedger(db)


def test_bridge_records_denial_durably(tmp_path):
    ledger = SQLiteAuditLedger(tmp_path / "receipts.db")
    bridge = SovereignBridge(OwnerIdentity("owner-a", "Test Owner"), ledger)
    grant = CapabilityGrant(operation="memory.delete", owner_id="owner-b")
    assert bridge.authorize("memory.delete", grant) is False
    ledger.close()
    reopened = SQLiteAuditLedger(tmp_path / "receipts.db")
    assert reopened.entries[0].data["authorized"] is False
    reopened.close()


def test_repeated_append_and_index_continuity(tmp_path):
    ledger = SQLiteAuditLedger(tmp_path / "receipts.db")
    for n in range(4):
        ledger.append("synthetic", {"n": n})
    assert [e.index for e in ledger.entries] == list(range(4))
    assert ledger.verify_integrity()
    ledger.close()
