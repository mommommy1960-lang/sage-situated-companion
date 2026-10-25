# Sage approved memory and conversation context — October 24, 2026

Site source commit 5e0d704c0686195d303f093865eeeee90d72294c.

Added editable approved memory stored in localStorage, explicit saving, review and deletion. This survives tab closure in the same browser profile; not encrypted per user, not cross-device sync, erased if site data is cleared. Explicit unchecked-by-default option sends the saved note to the existing Hugging Face text service with questions. Stop disables sharing but does not delete saved notes; Delete saved memory deletes the local record, not text already sent.

Added opt-in previous-turn context (up to four exchanges) stored in sessionStorage. Stop clears it. Older assistant replies are marked potentially inaccurate context, not verified business facts. Added HTTP status to service failure diagnostics when available. No paid fallback.

Verified in browser: saved fictional café note survived reload; deletion persisted after reload; context sharing control appeared and worked. Direct text service recalled Cedar Cup from an explicitly supplied saved test note and Comet from a supplied earlier exchange. Storage, speech, tab continuity, vision lifecycle and observation-loop tests pass. These tests do not prove long-term autonomous learning, account-level memory, continuous visual question answering, background operation, live maps/web lookup, or resolution of tablet session resets and intermittent service errors.
