# Bruce-to-Bruce: Sage tab pause fix — October 24, 2026

User reported camera preview and location coordinates working on tablet. Screenshot shows microphone phrase transcribed into question field. Model reply and audible output on physical tablet remain unverified.

Root cause: visibilitychange called full Stop, clearing approvals and text. Deployed separate pause handler: cancels model request, stops device streams and speech, retains approvals, question and answer in the open tab. Start Sage must be pressed on return; sensors do not restart automatically. Explicit Stop still clears approvals and question. Does not persist approvals across reloads or closed tabs.

Regression test passed using mocked browser environment: retention, cancellation, no automatic resume, explicit Stop reset. Physical device retest pending.

Site: https://sage-companion-device-lab.myqueen1960.chatgpt.site
Sites source commit: 3cf24fc13b97ecb6fa8618a8a0d1b8a162eb105c
Deployment: appgdep_6add0bf755c481918187459db0e44258 — succeeded.

Next: refresh site once, start, approve, switch tabs and return; confirm approvals retained. Then request a written answer and press Read answer aloud. Voice call may compete for device audio; test separately without assuming cause.
