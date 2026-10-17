from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import pytest
from sage.sovereignty import CapabilityGrant, CapabilityScope, OwnerIdentity, SovereignBridge


def test_expiry_boundary_future_and_naive_time():
    start = datetime(2026, 10, 17, tzinfo=timezone.utc)
    grant = CapabilityGrant("memory.export", "owner", created_at=start)
    assert grant.allows("memory.export", "owner", now=start)
    assert not grant.allows("memory.export", "owner", now=start+timedelta(minutes=5))
    assert not grant.allows("memory.export", "owner", now=start-timedelta(seconds=1))
    assert not grant.allows("memory.export", "owner", now=start.replace(tzinfo=None))


def test_only_one_competing_single_operation_consumes():
    grant = CapabilityGrant("memory.export", "owner")
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: grant.consume("memory.export", "owner"), range(30)))
    assert sum(results) == 1


def test_session_rechecks_revocation_and_owner_without_consuming():
    grant = CapabilityGrant("memory.export", "owner", scope=CapabilityScope.SESSION)
    assert not grant.consume("memory.export", "other")
    assert grant.consume("memory.export", "owner")
    assert grant.consume("memory.export", "owner")
    grant.revoke()
    assert not grant.consume("memory.export", "owner")


def test_bridge_denial_and_verifier_outage_never_call_effect():
    bridge = SovereignBridge(OwnerIdentity(owner_id="owner", preferred_name="Owner"))
    calls = []
    grant = CapabilityGrant("memory.export", "owner")
    for verifier in [lambda *args: False, lambda *args: 1]:
        with pytest.raises(PermissionError):
            bridge.execute("memory.export", grant, lambda: calls.append(1), verify_current_authority=verifier)
    def offline(*args): raise RuntimeError("offline")
    with pytest.raises(PermissionError):
        bridge.execute("memory.export", grant, lambda: calls.append(1), verify_current_authority=offline)
    assert calls == [] and not grant.consumed


def test_failed_effect_requires_new_permission_and_keeps_audit():
    bridge = SovereignBridge(OwnerIdentity(owner_id="owner", preferred_name="Owner"))
    grant = CapabilityGrant("memory.export", "owner")
    def fail(): raise RuntimeError("effect failed")
    with pytest.raises(RuntimeError):
        bridge.execute("memory.export", grant, fail, verify_current_authority=lambda *args: True)
    with pytest.raises(PermissionError):
        bridge.execute("memory.export", grant, lambda: "retry", verify_current_authority=lambda *args: True)
    assert bridge.ledger.verify_integrity()


def test_revocation_between_external_check_and_commit_blocks():
    bridge = SovereignBridge(OwnerIdentity(owner_id="owner", preferred_name="Owner"))
    grant = CapabilityGrant("memory.export", "owner")
    def verify(*args): grant.revoke(); return True
    with pytest.raises(PermissionError):
        bridge.execute("memory.export", grant, lambda: pytest.fail("effect ran"), verify_current_authority=verify)
