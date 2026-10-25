# Automatic observations — October 24, 2026

Site source commit 0ddf65abca7bc45b53b495a4d09f354056632e10 adds completion-paced visible-page camera sampling. Explicit opt-in starts serial frame analysis; next frame waits for completion plus three seconds. Changed captions can be spoken, avoiding interruption while speech or a question is active. Stop, hidden page, camera off and consent removal cancel observations. Errors stop automatic sampling. No real-time motion understanding or background guarantee.

Verified: real sample caption in browser, loop scheduling/Stop/ineligible tests, existing speech/tab/vision tests. Browser timer binding issue found in QA and corrected. Continuous physical camera performance and spoken observations on user's tablet remain unverified. Full multimodal live conversation, persistent memory, location reasoning and live web lookup remain outstanding.
