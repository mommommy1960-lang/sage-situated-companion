import json
import pytest

from sage.memory import MemoryStore
from sage.user_controls import (
    ActionLevel, ConsentController, UserMemoryController,
)


def test_each_sensor_requires_explicit_consent():
    consent = ConsentController()
    with pytest.raises(PermissionError):
        consent.require_sensor("camera")
    consent.set_sensor_consent("camera", True)
    consent.require_sensor("camera")
    with pytest.raises(PermissionError):
        consent.require_sensor("microphone")


def test_familiarity_cannot_escalate_action_level():
    consent = ConsentController()
    consent.grant_action("calendar.write", ActionLevel.SUGGEST)
    with pytest.raises(PermissionError):
        consent.require_action("calendar.write", ActionLevel.ACT)


def test_user_can_export_correct_and_delete_memory(tmp_path):
    store = MemoryStore(str(tmp_path / "memory.json"))
    memory = store.remember("wrong", explicit_remember=True)
    controls = UserMemoryController(store)

    exported = controls.export(tmp_path / "export.json")
    assert json.loads(exported.read_text())[0]["content"] == "wrong"

    assert controls.correct(memory.memory_id, "correct") is True
    assert store.memories[memory.memory_id].content == "correct"
    assert store.memories[memory.memory_id].metadata["corrected_by_user"] is True

    assert controls.delete(memory.memory_id) is True
    assert memory.memory_id not in store.memories


def test_user_can_delete_all_memory(tmp_path):
    store = MemoryStore(str(tmp_path / "memory.json"))
    store.remember("one")
    store.remember("two")
    UserMemoryController(store).delete_all()
    assert store.memories == {}
