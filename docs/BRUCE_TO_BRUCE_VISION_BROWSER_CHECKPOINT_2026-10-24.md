# Sage local vision checkpoint — October 24, 2026

Built an opt-in browser still-image captioner using Transformers.js 3.8.1 and Xenova/vit-gpt2-image-captioning revision 215b4edcb7ec1fad5905a18a03f7b2007f6fabd0. Source in hosted Site project appgprj_6adcf2820b8081918884a14320a69d21, commit a7caab010b43ccb7487b36c4b0bb1813227eeea7.

Browser sample inference returned: two cats laying on a bed with a remote. Added manual reading and optional 30-second visible-page spoken observations; explicit choice can include a caption younger than 60 seconds in the next text question. Images remain local. Initial model download can be hundreds of MB. Hidden/pagehide/Stop terminate inference. Tests pass for stale-result suppression, speech and tab state. Tablet camera inference and audio remain unverified.

This is experimental still-image captioning, not Gemini-equivalent visual conversation, screen sharing, motion analysis or traffic warnings. User requires all of those companion capabilities, plus consented lasting memory, location context, verified live place information and easier session resumption. Those remain outstanding. Gemini Live camera conversation is a UX reference, not a connected service.

User tablet test confirmed text recovery and spoken replies; active session reset still occurs after leaving page. Intermittent text-service error is unresolved despite subsequent successful direct tests. Grounding prompt improved business facts but generated unsupported claims and truncated a response; accuracy not considered solved.
