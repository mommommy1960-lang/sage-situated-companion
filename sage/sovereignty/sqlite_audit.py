"""Durable local sovereignty audit ledger for development and offline operation.

This SQLite-backed store is separate from the hosted Maya Node service.
Hash chaining detects local modification but does not prevent a privileged
attacker from rewriting the database and every hash. Protect backups and
anchor hashes externally before making stronger tamper-resistance claims.
Avoid placing raw personal memory content in audit event data.
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .audit import SovereignAuditLedger, AuditEntry


class SQLiteAuditLedger(SovereignAuditLedger):
    """Append-only API for a locally durable hash-chained audit journal."""

    def __init__(self, database_path):
        super().__init__()
        self.database_path = str(Path(database_path))
        self._db = sqlite3.connect(self.database_path)
        self._db.execute("PRAGMA busy_timeout = 5000")
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS audit_entries (
                idx INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                data_json TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL
            )"""
        )
        self._db.commit()
        self._reload()
        if not self.verify_integrity():
            self._db.close()
            raise ValueError("Audit ledger integrity check failed")

    def _reload(self):
        rows = self._db.execute(
            "SELECT idx, timestamp, operation, data_json, previous_hash, entry_hash "
            "FROM audit_entries ORDER BY idx"
        ).fetchall()
        self.entries = [
            AuditEntry(
                index=row[0],
                timestamp=row[1],
                operation=row[2],
                data=json.loads(row[3]),
                previous_hash=row[4],
                entry_hash=row[5],
            )
            for row in rows
        ]

    def append(self, operation, data):
        if not operation or not isinstance(data, dict):
            raise ValueError("Operation and dictionary event data required")
        # Re-read on every append to avoid stale state across instances.
        self._db.execute("BEGIN IMMEDIATE")
        try:
            self._reload()
            if not self.verify_integrity():
                raise ValueError("Audit ledger integrity check failed")
            index = len(self.entries)
            timestamp = datetime.now(timezone.utc).isoformat()
            previous_hash = self.entries[-1].entry_hash if self.entries else "0" * 64
            safe_data = json.loads(json.dumps(data, sort_keys=True, default=str))
            entry_hash = self._hash_payload(index, timestamp, operation, safe_data, previous_hash)
            self._db.execute(
                "INSERT INTO audit_entries VALUES (?, ?, ?, ?, ?, ?)",
                (index, timestamp, operation, json.dumps(safe_data, sort_keys=True),
                 previous_hash, entry_hash),
            )
            self._db.commit()
            entry = AuditEntry(index, timestamp, operation, safe_data, previous_hash, entry_hash)
            self.entries.append(entry)
            return entry
        except Exception:
            self._db.rollback()
            self._reload()
            raise

    def verify_integrity(self):
        return super().verify_integrity()

    def close(self):
        self._db.close()
