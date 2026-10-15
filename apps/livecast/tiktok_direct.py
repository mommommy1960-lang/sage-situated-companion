"""Optional direct TikTok LIVE event reader.

Uses the third-party ``TikTokLive`` package. It is NOT an official TikTok API
and may break when TikTok changes its internal webcast protocol.

For a commercial product, keep this adapter isolated so it can be replaced by
a licensed/official event source without changing the ensemble engine.
"""
from __future__ import annotations

import argparse
import json
import urllib.request

from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    CommentEvent,
    ConnectEvent,
    FollowEvent,
    GiftEvent,
    LikeEvent,
    ShareEvent,
)


def post_event(server: str, payload: dict) -> None:
    req = urllib.request.Request(
        server.rstrip("/") + "/event",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=3):
            pass
    except Exception as exc:
        print(f"[livecast] bridge error: {exc}")


def _user_name(event) -> str:
    user = getattr(event, "user", None)
    return (
        getattr(user, "nickname", None)
        or getattr(user, "unique_id", None)
        or "viewer"
    )


def build_client(username: str, server: str) -> TikTokLiveClient:
    client = TikTokLiveClient(unique_id=username)

    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        print(f"[livecast] connected to {username}")

    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        post_event(server, {
            "type": "comment",
            "user": _user_name(event),
            "text": getattr(event, "comment", ""),
        })

    @client.on(FollowEvent)
    async def on_follow(event: FollowEvent):
        post_event(server, {"type": "follow", "user": _user_name(event)})

    @client.on(ShareEvent)
    async def on_share(event: ShareEvent):
        post_event(server, {"type": "share", "user": _user_name(event)})

    @client.on(LikeEvent)
    async def on_like(event: LikeEvent):
        post_event(server, {
            "type": "like",
            "user": _user_name(event),
            "likes": int(getattr(event, "count", 0) or 0),
            "total_likes": int(
                getattr(event, "total", 0)
                or getattr(event, "total_likes", 0)
                or 0
            ),
        })

    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent):
        gift = getattr(event, "gift", None)
        # TikTok can emit intermediate events for streakable gifts.
        if bool(getattr(event, "streaking", False)):
            return
        count = int(
            getattr(event, "repeat_count", 0)
            or getattr(gift, "count", 0)
            or getattr(event, "count", 0)
            or 1
        )
        diamond_count = int(
            getattr(gift, "diamond_count", 0)
            or getattr(getattr(gift, "info", None), "diamond_count", 0)
            or 0
        )
        post_event(server, {
            "type": "gift",
            "user": _user_name(event),
            "gift_name": getattr(gift, "name", None) or "Gift",
            "gift_count": count,
            "coins": max(0, diamond_count * count),
        })

    return client


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="TikTok @username")
    parser.add_argument("--server", default="http://127.0.0.1:8765")
    args = parser.parse_args()
    build_client(args.username, args.server).run()


if __name__ == "__main__":
    main()
