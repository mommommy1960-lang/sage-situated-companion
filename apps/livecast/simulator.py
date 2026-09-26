from __future__ import annotations

import argparse
import json
import time
import urllib.request

SAMPLE = [
    {"type": "comment", "user": "Mary", "text": "!sage what kind of show is this?"},
    {"type": "follow", "user": "Chris"},
    {"type": "gift", "user": "Ari", "gift_name": "Rose", "gift_count": 1, "coins": 1},
    {"type": "comment", "user": "Nova", "text": "!aurora report to the lounge"},
    {"type": "pet_motion", "user": "camera", "text": "motion in enclosure"},
    {"type": "like", "user": "crowd", "likes": 25, "total_likes": 100},
]


def post(server: str, payload: dict) -> dict:
    req = urllib.request.Request(
        server.rstrip("/") + "/event",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="http://127.0.0.1:8765")
    parser.add_argument("--delay", type=float, default=1.5)
    args = parser.parse_args()
    for item in SAMPLE:
        print(post(args.server, item))
        time.sleep(args.delay)


if __name__ == "__main__":
    main()
