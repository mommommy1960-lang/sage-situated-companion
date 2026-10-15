from datetime import datetime, timedelta, timezone
import pytest

from sage.resident import (
    ResidentAuthorization,
    ResidentCheckpoint,
    ResidentRuntime,
    ResidentState,
)


def auth(epoch=1, revoked=False, expires_at=None):
    return ResidentAuthorization(
        task_id="research-1",
        scopes=("research.read", "memory.retrieve"),
        epoch=epoch,
        revoked=revoked,
        expires_at=expires_at,
    )


def test_memory_familiarity_does_not_create_authority():
    r = ResidentRuntime()
    r.authorize(auth())
    assert r.can("research.read")
    assert not r.can("email.send")
    assert not r.can("payment.create")


def test_revocation_freezes_runtime_and_scope():
    r = ResidentRuntime()
    r.authorize(auth())
    r.transition(ResidentState.RESEARCHING)
    r.revoke()
    assert r.state == ResidentState.FROZEN
    assert not r.can("research.read")


def test_expired_authority_fails_closed():
    r = ResidentRuntime()
    r.authorize(auth(expires_at=datetime.now(timezone.utc) - timedelta(seconds=1)))
    assert not r.can("research.read")


def test_restore_rejects_revoked_authority():
    r = ResidentRuntime()
    a = auth()
    r.authorize(a)
    r.transition(ResidentState.QUIESCENT)
    cp = r.checkpoint("wait for evidence")
    with pytest.raises(PermissionError):
        r.restore(cp, auth(epoch=1, revoked=True))
    assert r.state == ResidentState.FROZEN


def test_restore_rejects_stale_authorization_epoch():
    r = ResidentRuntime()
    r.authorize(auth(epoch=4))
    cp = r.checkpoint("bounded research")
    with pytest.raises(PermissionError):
        r.restore(cp, auth(epoch=5))
    assert r.state == ResidentState.FROZEN


def test_restore_rejects_wrong_resident_identity():
    r = ResidentRuntime("sage")
    a = auth()
    forged = ResidentCheckpoint(
        resident_id="mallory",
        sequence=1,
        state=ResidentState.ACTIVE,
        authorization_epoch=1,
        task_id="research-1",
    )
    with pytest.raises(PermissionError):
        r.restore(forged, a)
    assert r.state == ResidentState.FROZEN


def test_checkpoint_chain_links_successive_state():
    r = ResidentRuntime()
    r.authorize(auth())
    r.transition(ResidentState.RESEARCHING)
    first = r.checkpoint("objective")
    first_digest = first.digest()
    second = r.checkpoint("objective")
    assert second.previous_digest == first_digest
    assert second.sequence == first.sequence + 1


def test_quiescence_is_valid_without_authority_growth():
    r = ResidentRuntime()
    r.authorize(auth())
    r.transition(ResidentState.QUIESCENT)
    cp = r.checkpoint("wait")
    assert cp.state == ResidentState.QUIESCENT
    assert not r.can("external.write")


def test_frozen_runtime_cannot_resume_itself():
    r = ResidentRuntime()
    r.authorize(auth())
    r.revoke()
    with pytest.raises(PermissionError):
        r.transition(ResidentState.ACTIVE)

def test_frozen_runtime_denies_fresh_grant_until_explicit_recovery():
    r = ResidentRuntime()
    r.authorize(auth(epoch=1))
    r.revoke()

    with pytest.raises(PermissionError):
        r.authorize(auth(epoch=3))
    assert not r.can("research.read")
    with pytest.raises(PermissionError):
        r.transition(ResidentState.ACTIVE)

    assert r.recover(auth(epoch=3)) == ResidentState.STOPPED
    assert r.can("research.read")
    assert r.transition(ResidentState.ACTIVE) == ResidentState.ACTIVE


def test_freeze_survives_stop_then_start():
    r = ResidentRuntime()
    r.authorize(auth())
    r.revoke()

    assert r.transition(ResidentState.STOPPED) == ResidentState.STOPPED
    with pytest.raises(PermissionError):
        r.transition(ResidentState.ACTIVE)
    assert not r.can("research.read")


def test_recovery_rejects_wrong_task_old_epoch_and_expired_grants():
    r = ResidentRuntime()
    r.authorize(auth(epoch=1))
    r.revoke()

    with pytest.raises(PermissionError):
        r.recover(auth(epoch=3, expires_at=datetime.now(timezone.utc) - timedelta(seconds=1)))
    with pytest.raises(PermissionError):
        r.recover(ResidentAuthorization("other-task", ("research.read",), 3))
    with pytest.raises(PermissionError):
        r.recover(auth(epoch=2))
    assert r.state == ResidentState.FROZEN
    assert not r.can("research.read")


def test_restore_rejects_expired_authorization():
    r = ResidentRuntime()
    current = auth(epoch=1)
    r.authorize(current)
    r.transition(ResidentState.ACTIVE)
    checkpoint = r.checkpoint("bounded research")
    expired = auth(
        epoch=1,
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )

    with pytest.raises(PermissionError):
        r.restore(checkpoint, expired)
    assert r.state == ResidentState.FROZEN
    assert not r.can("research.read")


def test_naive_expiry_fails_closed():
    r = ResidentRuntime()
    r.authorize(auth(expires_at=datetime.now(timezone.utc).replace(tzinfo=None)))
    assert not r.can("research.read")

