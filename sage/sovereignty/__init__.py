"""
SAGE Sovereignty Layer

Bridges SAGE experiential intelligence with governance concepts
developed in the MAYA Node sovereign architecture.

Initial responsibilities:
- owner identity
- scoped capability authorization
- auditable action records
- future MAYA Node bridge integration
"""

from .identity import OwnerIdentity
from .capabilities import CapabilityGrant, CapabilityScope
from .audit import SovereignAuditLedger
from .bridge import SovereignBridge

__all__ = [
    "OwnerIdentity",
    "CapabilityGrant",
    "CapabilityScope",
    "SovereignAuditLedger",
    "SovereignBridge",
]
