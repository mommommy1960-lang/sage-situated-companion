from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json


@dataclass
class AuditEntry:
    index: int
    timestamp: str
    operation: str
    data: dict
    previous_hash: str
    entry_hash: str


class SovereignAuditLedger:
    """
    Lightweight hash-chained audit ledger modeled after MAYA Node's
    immutable ledger architecture.
    """

    def __init__(self):
        self.entries: list[AuditEntry] = []

    @staticmethod
    def _hash_payload(
        index: int,
        timestamp: str,
        operation: str,
        data: dict,
        previous_hash: str,
    ) -> str:
        payload = json.dumps(
            {
                "index": index,
                "timestamp": timestamp,
                "operation": operation,
                "data": data,
                "previous_hash": previous_hash,
            },
            sort_keys=True,
            default=str,
        )

        return hashlib.sha256(payload.encode()).hexdigest()

    def append(self, operation: str, data: dict) -> AuditEntry:
        index = len(self.entries)
        timestamp = datetime.now(timezone.utc).isoformat()

        previous_hash = (
            self.entries[-1].entry_hash
            if self.entries
            else "0" * 64
        )

        entry_hash = self._hash_payload(
            index,
            timestamp,
            operation,
            data,
            previous_hash,
        )

        entry = AuditEntry(
            index=index,
            timestamp=timestamp,
            operation=operation,
            data=dict(data),
            previous_hash=previous_hash,
            entry_hash=entry_hash,
        )

        self.entries.append(entry)
        return entry

    def verify_integrity(self) -> bool:
        previous_hash = "0" * 64

        for index, entry in enumerate(self.entries):
            if entry.index != index:
                return False

            if entry.previous_hash != previous_hash:
                return False

            expected = self._hash_payload(
                entry.index,
                entry.timestamp,
                entry.operation,
                entry.data,
                entry.previous_hash,
            )

            if expected != entry.entry_hash:
                return False

            previous_hash = entry.entry_hash

        return True
