# START HERE — Commons Live Ensemble

This branch is a working local MVP, not a hosted website or phone app. It runs on a computer and opens a browser-based control room.

## Windows

1. Download or clone this repository on the `livecast-ai-mvp` branch.
2. Double-click `START_LIVECAST_WINDOWS.bat`.
3. The first run creates a private `.venv` and installs the needed Python packages.
4. Your browser opens the **Commons Live Ensemble Control** page.
5. Enter your TikTok username and press **START TIKTOK LISTENER**.
6. Start your TikTok LIVE.
7. Press **OPEN TRANSPARENT OVERLAY** to test the cast.
8. In TikTok LIVE Studio or OBS, add `http://127.0.0.1:8765/` as a Browser Source.

## macOS / Linux

From a terminal in the repository folder:

```bash
bash START_LIVECAST.sh
```

The rest is the same as Windows.

## What the big START button does

The control room launches the experimental TikTok LIVE event listener. Comments, gifts, likes, follows, and shares are normalized and passed to the ensemble director. Audience commands can route comments to:

- `!sage`
- `!aurora`
- `!maya`
- `!serafina` or `!snake`

## AI modes

The default **demo** mode is free and proves the full event-routing/overlay pipeline, but it uses canned responses.

For genuinely generated local responses, install Ollama and start with the environment variable `LIVECAST_PROVIDER=ollama`. The current implementation defaults to `llama3.2:3b` unless changed with `LIVECAST_OLLAMA_MODEL`.

This does **not** connect directly to the user's private ChatGPT conversation or private operational Aurora systems.

## Security and animal boundary

- Aurora LIVE is a public performance persona only.
- No private repositories, credentials, unpublished engineering, shell access, or physical controls are exposed to the audience.
- Viewer actions may control show presentation only. Never connect gifts or likes to animal feeding, heating, humidity, enclosure access, or other husbandry controls.

## Prototype caveat

The direct TikTok reader uses the unofficial third-party `TikTokLive` package. TikTok may change its internal LIVE protocol at any time. Keep this adapter isolated and replace it with an approved/licensed event source before treating the system as production commercial infrastructure.
