# Bruce-to-Bruce: resume Sage here

Queen paused for a break after confirming Gemini Live spoken output on her tablet. When she says she is ready to get started again, resume at the microphone test below. Do not repeat key setup.

## Verified
- Google key accepted and saved encrypted by owner-only setup. /api/live/status returned configured:true. No key in this record.
- Real Google Live session connected in browser and answered a public typed greeting; test then stopped cleanly.
- Queen typed Hello on her tablet and explicitly confirmed hearing Sage's reply aloud.
- Microphone streaming is implemented, but tablet input and interruption are NOT verified. Camera sharing is implemented, but live vision is NOT verified.

## First next step
1. Open https://sage-companion-device-lab.myqueen1960.chatgpt.site/#geminiLive
2. Check public-data test consent; Connect Gemini Live (owner sign-in only if requested).
3. Leave camera sharing off. Enable Share my microphone audio with Google; allow microphone.
4. Say: Sage, can you hear me? Confirm her response and input transcript.
5. After successful microphone reply, test interruption. Then separately test camera on public test objects with explicit frame sharing.

No additional key copying, billing activation, or paid fallback. Google free-tier content may be reviewed/used for product improvement. Personal memories and location are not attached to this Live test. Page hidden ends session; four-minute test cap. Background operation is not built.

## Engineering checkpoint
Sites project appgprj_6adcf2820b8081918884a14320a69d21. Version14 source 0ef34138401374f619662fe2697c174dde0cd8cc; saved version appgprj_6adcf2820b8081918884a14320a69d21~appgver_33db17cff1f08191b22da0e9b31cc5d7. Deployment appgdep_6add84bd67e481918d36ef0dd5757d0e succeeded. Source checkout /workspace/sites/sage-companion-device-lab.
- Fixed browser fetch illegal invocation with wrapped fetcher.
- Fixed REST token payload: bidiGenerateContentSetup contains actual setup; do not send SDK liveConnectConstraints directly.
- Protected setup now has split validation messages and scrolls result into view. Credential remains encrypted in D1; permanent key never sent to public client.

Remaining broader work: reliable tablet microphone/camera, interruption, knowledge grounding, memory/vision/location integration, background lifecycle. Do not claim full companion target complete.
