from threading import Event, Thread
from types import SimpleNamespace
import pytest
from apps.companion_session import CompanionSession


class Console:
    def __init__(self):
        self.calls = []
        self.runtime = SimpleNamespace(start=lambda: None, stop=lambda: None)

    def process_message(self, text):
        self.calls.append(text)
        return "reply"


def test_off_and_unapproved_sessions_never_process_text():
    console = Console()
    session = CompanionSession(console)
    with pytest.raises(PermissionError):
        session.respond("hello")
    session.start()
    with pytest.raises(PermissionError):
        session.respond("hello")
    assert console.calls == []
    session.start(allow_cloud_text=True)
    assert session.respond("hello") == "reply"
    session.stop()
    assert not session.active
    session.start()
    with pytest.raises(PermissionError):
        session.respond("hello")


def test_stop_and_restart_discard_inflight_answer():
    entered, release = Event(), Event()
    console = Console()
    def slow(text):
        entered.set()
        assert release.wait(3)
        return "stale answer"
    console.process_message = slow
    session = CompanionSession(console)
    session.start(allow_cloud_text=True)
    results = []
    worker = Thread(target=lambda: results.append(session.respond("hello")))
    worker.start()
    assert entered.wait(3)
    session.stop()
    session.start(allow_cloud_text=True)
    release.set()
    worker.join(3)
    assert not worker.is_alive()
    assert results == [None]
