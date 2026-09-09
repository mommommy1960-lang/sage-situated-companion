from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8765/control"
HEALTH = "http://127.0.0.1:8765/health"


def wait_for_server(timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(HEALTH, timeout=1) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.4)
    return False


def main() -> int:
    print("\n=== Commons Live Ensemble ===")
    print("Starting local show-control server...")
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "apps.livecast.server:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8765",
        ],
        cwd=str(ROOT),
    )

    if not wait_for_server():
        print("The server did not start. Check the error above.")
        proc.terminate()
        return 1

    print(f"Control room ready: {URL}")
    print("Close this window or press Ctrl+C when the show is over.")
    webbrowser.open(URL)

    try:
        return proc.wait()
    except KeyboardInterrupt:
        print("\nStopping Commons Live Ensemble...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
