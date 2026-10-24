# Sage device interface demonstration

The browser interface in apps/tablet_web is part of the original Sage repository.
It implements opt-in local camera preview, single-phrase browser speech recognition,
local geolocation display and browser spoken playback. Text questions can go to
1Queen/Sage-Agent-Course after separate cloud-text approval. The browser path calls
that model directly; it does not yet run the Python SageRuntime, durable memory or
Maya authority bridge. Do not conflate these paths.

All controls start off. Stop stops camera tracks, aborts speech recognition,
clears the location watch (including watch ID zero), cancels speech playback,
invalidates in-flight model output, clears input/output and resets sharing consent.
A permission dialog completing after Stop cannot restart the camera. Ordinary tab switches keep the session, approvals, question, answer and pending
model request. Actual navigation or closing releases device streams. Explicit Stop
still clears consent. Browser/OS background suspension may interrupt device access. Device APIs require supported browsers,
OS grants and appropriate secure-context/Permissions-Policy settings.

Camera frames and coordinates are never sent to the model. Browser speech
recognition may send audio to its speech service; approval is separate. No raw
recording, persistent browser storage, analytics or automatic message sending is
implemented. CDN and font requests are ordinary external asset requests.

Camera preview is not image interpretation; location display is not navigation.
The browser may suspend a background tab; there is no guaranteed background listening,
hazard detection, emergency response or hardware control. Test stationary with
public phrases. Do not rely on the prototype while riding.

Run `node --test tests/device/*.test.mjs` for device lifecycle, speech diagnostics,
stream parsing and tab-switch regression tests.

The public demo is https://sage-companion-device-lab.myqueen1960.chatgpt.site/ .
Test Sage's voice independently before asking a question. Speech events and errors
are displayed; they do not independently prove the user heard audio. See
[Sage tablet observations](SAGE_TABLET_TEST_2026-10-24.md).
Run `python -m pytest tests -q` for the existing Python suite.

Next developer integration: replace the direct text connection with a deployed,
authenticated application adapter around CompanionSession and SageRuntime; add
approved-source retrieval; define sensory data scopes/retention; integrate an
image-capable model only after explicit image disclosure controls; validate real
Android devices, latency, denial paths, revoke behavior and battery usage.
