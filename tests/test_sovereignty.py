from sage.sovereignty import (
    CapabilityGrant,
    CapabilityScope,
    OwnerIdentity,
    SovereignAuditLedger,
    SovereignBridge,
)


def make_owner():
    return OwnerIdentity(
        owner_id="queen-mya",
        preferred_name="Queen",
        identity_anchors=[
            "User retains sovereignty over personal data.",
            "SAGE continuity follows the user, not the device.",
        ],
    )


def test_owner_identity_snapshot():
    owner = make_owner()

    snapshot = owner.snapshot()

    assert snapshot["owner_id"] == "queen-mya"
    assert snapshot["preferred_name"] == "Queen"
    assert len(snapshot["identity_anchors"]) == 2


def test_matching_capability_authorizes_operation():
    owner = make_owner()
    bridge = SovereignBridge(owner)

    grant = CapabilityGrant(
        operation="calendar.read",
        owner_id=owner.owner_id,
        scope=CapabilityScope.SESSION,
    )

    assert bridge.authorize("calendar.read", grant) is True


def test_wrong_operation_is_denied():
    owner = make_owner()
    bridge = SovereignBridge(owner)

    grant = CapabilityGrant(
        operation="calendar.read",
        owner_id=owner.owner_id,
    )

    assert bridge.authorize("email.send", grant) is False


def test_revoked_capability_is_denied():
    owner = make_owner()
    bridge = SovereignBridge(owner)

    grant = CapabilityGrant(
        operation="calendar.read",
        owner_id=owner.owner_id,
    )

    grant.revoke()

    assert bridge.authorize("calendar.read", grant) is False


def test_audit_ledger_detects_tampering():
    ledger = SovereignAuditLedger()

    ledger.append("one", {"value": 1})
    ledger.append("two", {"value": 2})

    assert ledger.verify_integrity() is True

    ledger.entries[0].data["value"] = 999

    assert ledger.verify_integrity() is False


def test_bridge_records_authorization_decision():
    owner = make_owner()
    bridge = SovereignBridge(owner)

    grant = CapabilityGrant(
        operation="memory.export",
        owner_id=owner.owner_id,
    )

    bridge.authorize("memory.export", grant)

    assert len(bridge.ledger.entries) == 1
    assert (
        bridge.ledger.entries[0].operation
        == "authorization_check"
    )
    assert bridge.ledger.verify_integrity() is True
