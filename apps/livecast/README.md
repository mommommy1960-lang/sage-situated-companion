# Commons Live Ensemble (MVP)

A local-first multi-character AI co-host for livestreams.

## What makes this different

Most LIVE automation tools map an event directly to a sound, overlay, or **one** AI character.
This prototype adds an **ensemble director**: viewers can address different persistent cast members
(`!sage`, `!aurora`, `!maya`, `!serafina`), while gifts, likes, follows, pet-camera motion, and
other events can route to different characters and stage cues. The show is a cast, not a chatbot.

It also separates a **public performance shell** from private/operational systems. The public Aurora
persona is intentionally unable to expose or control private engineering systems.

This repository does **not** claim nobody has ever combined these ideas before. It is an implementable
product direction with a differentiated combination: multi-persona routing + public/private boundary +
audience event orchestration + pet-safe stage automation.

## Zero-cost demo

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r apps/livecast/requirements.txt
uvicorn apps.livecast.server:app --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/` in a browser. In OBS or TikTok LIVE Studio, add it as a browser source.

In another terminal:

```bash
python -m apps.livecast.simulator
```

You should see Sage, Aurora, Maya, and Serafina's Herald take turns reacting.

## Local AI mode

Install Ollama separately, download a model, then:

```bash
set LIVECAST_PROVIDER=ollama
# macOS/Linux: export LIVECAST_PROVIDER=ollama
uvicorn apps.livecast.server:app --host 127.0.0.1 --port 8765
```

Default model is `llama3.2:3b`; override with `LIVECAST_OLLAMA_MODEL`.

## Direct TikTok event mode (experimental)

The optional `TikTokLive` Python dependency can read comments, gifts, likes, follows, and shares
from a LIVE room. It is a third-party reverse-engineered client, **not an official TikTok API**,
and can break when TikTok changes its protocol. Keep this connector isolated if building a
commercial product.

```bash
pip install TikTokLive
python -m apps.livecast.tiktok_direct @YOUR_USERNAME
```

The direct adapter posts normalized events to the local engine at `http://127.0.0.1:8765/event`.

## Audience commands

- `!sage <question>` — Sage
- `!aurora <question>` — Aurora public performance shell
- `!maya <question>` — Maya
- `!serafina <question>` or `!snake <question>` — reptile narrator

The router can also react to gifts, follow/share events, like milestones, and safe `pet_motion` events.

## Animal safety

Audience events may control **stream presentation only**: overlays, voices, stage graphics, camera
scene selection, counters, and other non-husbandry effects.

Do not connect Gifts/Likes to feeding, heat, humidity, enclosure locks, handling, lighting schedules,
or any other action that can affect an animal's welfare. A snake-cam mode can be interactive without
making the animal itself an actuator.

## Security boundary

Public LIVE personas must not receive:
- private repository contents
- credentials or API secrets
- unpublished engineering details
- physical control privileges
- private system prompts
- arbitrary filesystem or shell access

If a later version gets tools, each tool should be allow-listed, scoped, logged, interruptible,
and separate from private operational agents.

## Next product steps

1. Add a browser-based show-control dashboard.
2. Add configurable gift-to-scene rules.
3. Add persistent **viewer relationship memory** with consent and retention controls.
4. Add an "ensemble roundtable" mode where multiple characters answer one audience question.
5. Add a pet-cam observation adapter (motion events only, no animal actuation).
6. Add clip markers and automatic highlight extraction.
7. Swap the experimental TikTok reader for a licensed/official event source before commercial scale.
