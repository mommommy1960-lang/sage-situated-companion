# Existing Sage pipeline: Hugging Face text connection

This increment extends the existing SageConsole/GenerationAdapter boundary.
It preserves the frozen runtime and does not replace Sage with a second app.

Install `python -m pip install -r requirements-huggingface.txt`.
Run `python -m apps.huggingface_console --allow-cloud-text` only after approving
disclosure of the public test questions you will enter to
`1Queen/Sage-Agent-Course` on Hugging Face. No paid fallback is configured.
The existing free Space may sleep, fail, or reach a quota. Availability is not guaranteed.

The adapter sends the entered question and fixed companion instructions.
It deliberately excludes runtime location, personality fields and retrieved memories.
The test command uses temporary local memory, removed when the command exits.
This is not deletion of information already sent to Hugging Face.

`CompanionSession` starts off, requires explicit cloud-text consent, rejects new
requests while off, and invalidates late answers across stop/restart. It does not
cancel an already transmitted provider request or erase stored data. Device
adapters must separately stop their OS streams. The legacy console does not
automatically gain this session gate; use the new entry point for this test.

The model is text-only. Prompt instructions reduce unsupported claims but are
not a factuality guarantee or prompt-injection security boundary. There is no
camera understanding, microphone collection, GPS, navigation, ambient listening,
background mobile service, physical device control, or verified hazard detection.

## Evidence and next acceptance gates

Unit tests cover payload minimization, invalid/empty/oversized answers, off-state
rejection, consent reset, and stop/restart during an in-flight response.
Mocks establish application behavior, not a successful live Space response.

Next: verify the named Space API with a harmless question; add approved-source
retrieval with source identifiers and unknown responses; implement separately
permissioned device adapters; test on Queen's Android tablet; measure latency,
failure recovery, battery impact and accuracy using a documented evaluation set.
Use these measurements before making commercial reliability or superiority claims.
