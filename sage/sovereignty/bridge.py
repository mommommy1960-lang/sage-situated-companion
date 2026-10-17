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

    def execute(self, operation, grant, action, *, verify_current_authority):
        """Local callback boundary, not a deployed Maya network adapter.

        The controller provides a current external-authority verifier. A failed
        effect still consumes single-use permission; retries require a new grant.
        """
        try:
            externally_allowed = verify_current_authority(operation, self.owner.owner_id, grant) is True
        except Exception:
            externally_allowed = False
        if not externally_allowed or grant is None or not grant.consume(operation, self.owner.owner_id):
            self.record_result(operation, success=False, metadata={"reason": "current_authority_denied"})
            raise PermissionError("Current authority denied")
        try:
            result = action()
        except Exception:
            self.record_result(operation, success=False, metadata={"reason": "effect_failed_no_automatic_retry"})
            raise
        self.record_result(operation, success=True)
        return result

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
