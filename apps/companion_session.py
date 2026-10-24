"""Consent-controlled application boundary around the existing SageConsole.

Does not start hardware. Device adapters must separately enforce OS permission
and stop collection; this controller rejects input and suppresses stale output.
"""

from threading import RLock


class CompanionSession:
    def __init__(self, console):
        self.console = console
        self._lock = RLock()
        self._active = False
        self._epoch = 0
        self._cloud_text_allowed = False

    def start(self, *, allow_cloud_text=False):
        with self._lock:
            self._epoch += 1
            self._active = True
            self._cloud_text_allowed = bool(allow_cloud_text)
            self.console.runtime.start()

    def stop(self):
        with self._lock:
            self._epoch += 1
            self._active = False
            self._cloud_text_allowed = False
            self.console.runtime.stop()

    @property
    def active(self):
        with self._lock:
            return self._active

    def respond(self, text):
        with self._lock:
            if not self._active:
                raise PermissionError("Start Sage before sending input")
            if not self._cloud_text_allowed:
                raise PermissionError("Cloud text disclosure has not been approved")
            epoch = self._epoch
        # Model work must not hold the stop lock. Stop cannot retract a payload
        # already sent to the service, but its eventual output is discarded.
        answer = self.console.process_message(text)
        with self._lock:
            if not self._active or epoch != self._epoch:
                return None
            return answer
