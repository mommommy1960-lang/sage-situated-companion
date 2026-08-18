from .audit import SovereignAuditLedger
from .capabilities import CapabilityGrant
from .identity import OwnerIdentity


class SovereignBridge:
    """
    SAGE-side sovereignty boundary.

    This bridge does not replace SAGE Core and does not yet call
    MAYA Node directly. It establishes the stable contract through
    which MAYA Node consent, identity, ledger, and attestation
    services can later connect.
    """

    def __init__(
        self,
        owner: OwnerIdentity,
        ledger: SovereignAuditLedger | None = None,
    ):
        self.owner = owner
        self.ledger = ledger or SovereignAuditLedger()

    def authorize(
        self,
        operation: str,
        grant: CapabilityGrant | None,
    ) -> bool:
        authorized = bool(
            grant
            and grant.allows(
                operation=operation,
                owner_id=self.owner.owner_id,
            )
        )

        self.ledger.append(
            "authorization_check",
            {
                "operation": operation,
                "owner_id": self.owner.owner_id,
                "authorized": authorized,
                "grant_id": (
                    grant.grant_id
                    if grant is not None
                    else None
                ),
            },
        )

        return authorized

    def record_result(
        self,
        operation: str,
        *,
        success: bool,
        metadata: dict | None = None,
    ) -> None:
        self.ledger.append(
            "operation_result",
            {
                "operation": operation,
                "success": success,
                "metadata": metadata or {},
            },
        )
