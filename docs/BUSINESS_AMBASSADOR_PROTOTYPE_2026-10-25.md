# Sage Business Ambassador — simulation-first increment

## Scope and evidence

This increment adds an owner-review FAQ workflow, not a production service or a new general-purpose model. The browser robot is an original illustrative animation, **not a Reachy SDK or MuJoCo simulation**. No physical robot is connected or purchased.

The app uses approved public project facts and a fictional bicycle workshop. Questions must match an approved question or alias after normalization; uncertain, compound and unmatched questions get an explicit unknown. This is deliberately narrow deterministic retrieval, not a claim that prompting secures a model. HTML-like input is displayed as text, never injected into the DOM.

The browser lifecycle reuses `apps/tablet_web/device-controller.mjs` without sensor capabilities. Stop and navigation discard delayed answers and pending approvals. This app intentionally stops on hidden tabs; the existing tablet demonstrator's distinct continuity behavior is preserved. Questions, conversation and approvals are volatile; event metadata can remain until cleared/reload. Downloads are optional user-managed copies. Host access logs are outside this in-tab boundary.

`BusinessFAQGenerationAdapter` implements the existing `GenerationAdapter` contract without changing the frozen core. It uses the same JSON source as the browser. The existing SageConsole pipeline can use it. **The Python runtime normally records input in memory**; its test uses a temporary store. Browser privacy behavior does not transfer automatically to a Python deployment. Browser one-use draft approval is a local demonstration, not a server security or Maya/Pulpo enforcement boundary.

## Run locally

Serve `apps/business_ambassador/` over HTTP. The re-export of DeviceController requires the repository root to be served: open `/apps/business_ambassador/`. The hosted static packaging replaces that re-export with the exact existing lifecycle module. No provider account, API key or inference usage is needed.

Python integration, for public test text only:

```python
from apps.console import SageConsole
from interfaces.business_generation import BusinessFAQGenerationAdapter

console = SageConsole(generation_adapter=BusinessFAQGenerationAdapter())
# Configure an appropriate memory store and deployment consent before real use.
answer = console.process_message("What does Civic Continuum do?")
```

## Checks

```sh
python -m pytest -q
node --test tests/device/*.test.mjs tests/business/*.test.mjs
```

New engine tests cover approved aliases, source identity, ambiguity, unknown/injection requests, invalid input, off-state requests, Stop/restart races, exact one-use approvals, expiry, revocation, replacement, profile changes and content-free receipts. The browser's Run boundary checks button executes eight independent local checks; it does not contact a robot or prove server enforcement.

## Reachy integration gates

1. Pin an official SDK revision and model/component licenses before integration.
2. Add an output adapter around Sage's existing `OutputRequest`/`OutputResult`, with no motor commands derived from arbitrary text.
3. Validate bounded gestures through the official MuJoCo simulator, including Stop and disconnect.
4. Benchmark a local speech stack on available compute; robot onboard compute is not assumed sufficient.
5. Verify explicit sensor consent and physical Stop on borrowed/owned hardware before any physical claim.
6. Test installation, error recovery, staff handoff and source updates with a pilot owner before customer use.

Official references checked October 25, 2026:
- https://huggingface.co/docs/reachy_mini/index
- https://huggingface.co/docs/reachy_mini/en/SDK/apps
- https://huggingface.co/blog/local-reachy-mini-conversation
- https://pollen-robotics.com/reachy-mini/

SDK and hardware design licenses differ; no right to manufacture clones is assumed. No endorsement by Pollen Robotics, Hugging Face, Austin or another reviewer is claimed. Private commercial planning and prospect selection remain in the private continuity vault.
