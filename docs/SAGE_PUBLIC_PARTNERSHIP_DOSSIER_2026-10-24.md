# Sage - Developer and Funder Partnership Dossier
**Civic Continuum | Mya P. Brown | October 24, 2026**

## Sage: a companion you can stop
Civic Continuum | Mya P. Brown, Founder | October 24, 2026

### The opportunity
Sage is an early companion prototype built around a simple promise: people should be able to see what it can access, choose what they share, and stop it. Our next objective is a reproducible, supervised Android demonstration that combines useful answers with visible controls.

### Why this matters
A companion that uses a camera, microphone or location needs understandable boundaries. Civic Continuum is testing those boundaries in the interaction itself: separate controls, explicit text-sharing consent and a prominent Stop everything action. We are seeking technical collaboration to turn this prototype into a measured pilot.

### What exists today
A public browser device demo, an existing Python companion runtime and a working cloud text-model connection. On her Android tablet, the founder reported camera preview, location display and speech-to-text input. Those observations are distinct from independent validation.

### The next proof
Confirm audible responses on the target tablet; reproduce permission and Stop behavior; then connect the browser to the Python runtime through an authenticated application adapter. The current browser model path is separate from that runtime.

### Partnership request
We invite a focused engineering review and milestone-scoped pilot proposal. Potential support includes Android/browser engineering, integration, testing devices and evaluation design. A financial request and schedule will follow a reviewed work breakdown; neither is being invented in this brief.

### Open the work
- [Public Sage demo](https://sage-companion-device-lab.myqueen1960.chatgpt.site/)
- [Source code and tests](https://github.com/mommommy1960-lang/sage-situated-companion)
- [Member Commons overview](https://civic-continuum-members.myqueen1960.chatgpt.site/#sage)
- [Founder contact on LinkedIn](https://www.linkedin.com/in/mya-p-brown-486463172/)

### Readiness
Early prototype. Not a safety product, production release, certification, verified commercial traction or guarantee of factual accuracy.

## A focused development partnership
A reusable cover letter - no recipient or affiliation is implied.

### To a prospective engineering or funding partner
I am Mya P. Brown, founder of Civic Continuum. We are developing Sage, a companion prototype that makes human control visible through explicit device permissions, separate cloud-text approval and a Stop everything control.

### What we can show
Our public demo combines local camera preview, location display, browser speech input and an optional text-model connection. I have observed camera preview, location display and speech transcription on my Android tablet. Audible replies remain to be confirmed. Automated lifecycle tests provide additional, bounded evidence; they do not replace device testing.

### What we are asking you to help prove
We are seeking a collaborator for a stationary Android pilot: confirm spoken output, challenge permission and Stop behavior, measure latency and recovery, and integrate the browser with the existing Python companion runtime. We will report failures and unresolved behavior alongside successful tests.

### A practical first conversation
We propose a short demonstration followed by agreement on one exact code revision, test cases, expected outcomes and the evidence each party will retain. Public or synthetic material is sufficient for the initial review. Access to private data, paid work and named publication are outside this invitation unless separately agreed.

### Next step
Please review the demo and source, identify the engineering contribution you could make, and suggest a bounded first milestone. We will define acceptance criteria, responsibilities, costs and an achievable schedule together before committing to a wider pilot.

### Signature
Mya P. Brown
Founder, Civic Continuum

### Contact and evidence
- [Founder profile](https://www.linkedin.com/in/mya-p-brown-486463172/)
- [Public demo](https://sage-companion-device-lab.myqueen1960.chatgpt.site/)
- [Latest implementation changes](https://github.com/mommommy1960-lang/sage-situated-companion/pull/10)

## What we can substantiate
Evidence as of October 24, 2026. Observations, tests and future work are kept separate.

### Founder-reported device observations
On the target Android tablet: live camera preview showed surroundings; local location display showed coordinates; browser speech recognition placed spoken words in the question box after another voice call was paused. These are founder reports, not an independent audit. No coordinates or personal recordings are included.

### Automated and browser checks
The recorded Python baseline contains 145 passing tests. The initial device/API suite contained nine tests; six new device regressions cover speech behavior and tab-session handling. PR10 checks passed before merge. These counts describe separate test scopes, not a security certification or general accuracy score.

### Latest release behavior
v0.3 removes the application-level stop on an ordinary tab switch and preserves session choices, question, answer and pending model request. It adds an independent voice test, voice selection and visible speech diagnostics. Browser checks exercised session retention and explicit Stop. Physical-device retesting of the change is still required.

### Not yet established
Audible replies on the target tablet; reliable background operation; end-to-end connection to Python memory and authority; approved-source retrieval in the browser path; image interpretation; navigation; wearable hardware; battery performance; independent review results; customer demand and commercial unit economics.

### Reproducible reference
PR10 merged revision: 685d91c3a362725f8733e2a80021a2bd031b1ec1. Future results should identify the tested revision, device, browser, test input, expected result and actual result. A passing test should never be presented as proof of all possible behavior.

### Inspect the evidence
- [PR10: session and speech fixes](https://github.com/mommommy1960-lang/sage-situated-companion/pull/10)
- [Device behavior and limits](https://github.com/mommommy1960-lang/sage-situated-companion/blob/main/docs/DEVICE_DEMO.md)
- [Founder tablet observations](https://github.com/mommommy1960-lang/sage-situated-companion/blob/main/docs/SAGE_TABLET_TEST_2026-10-24.md)

## Two paths today. One integration ahead.
Current data flows, followed by the proposed integration. No hardware interlock or air gap is claimed.

### Current browser path
User enables a session -> optional device controls -> typed question or speech transcript in an editable input -> separate cloud-text approval and Ask Sage -> Hugging Face text-model endpoint -> written answer -> optional browser speech playback. The selected question text leaves the device only when submitted through this path.

### Camera and location
Camera preview and geolocation display are local features in the demo. The application does not attach frames or coordinates to model requests. This is a scoped application behavior, not hardware-enforced isolation. Users can still type sensitive information into a question; automatic redaction is not established.

### Microphone and external services
Browser speech recognition may transmit audio to the browser provider's speech service. It must not be described as guaranteed offline or local-only transcription. Voice availability and processing depend on the browser and operating system. Hosting and external asset requests also cross network boundaries; the demo is not air-gapped.

### Stop and page lifecycle
Stop is designed to stop camera tracks, abort recognition, clear the location watch, cancel speech, discard pending model output and reset the input and sharing controls. It does not erase data already received by external providers or guarantee forensic deletion from device memory. Ordinary tab switches retain state; navigation or closing releases device streams. The OS may suspend a background page.

### Existing Python path
The repository also contains a Python companion/session runtime with model-adapter and authority-related components. The public browser demo currently calls the text model directly. It does not yet execute that Python memory/authority path. An authenticated browser-to-runtime adapter is proposed work.

### Proposed integrated path
Authenticated browser session -> validated text request and explicit scope -> CompanionSession / SageRuntime -> approved-source retrieval, when implemented -> model response with source references or a clear lack-of-evidence response -> current-session check -> visible answer and optional speech. Retrieval can improve grounding; it cannot guarantee truth.

### Integration design decisions
Before implementation: define identity, retention and deletion, request cancellation, provider disclosures, document permissions, secret handling and failure behavior. Camera interpretation, persistent memory and background service each need separate scope and tests.

## A pilot with observable gates
Proposed acceptance criteria for partner agreement. No dates, costs or results are promised.

### Gate 1 - repeatable tablet demonstration
Confirm audible voice test and spoken answer on the target tablet. Exercise allow/deny, repeated Start/Stop, late permission completion, empty input, network interruption and tab changes. Log pass/fail per scenario, voice/browser version and unresolved behavior. Required: no post-Stop answer appears in the tested cases; released resources and visible indicators are checked independently where possible.

### Gate 2 - integrated application path
Deploy the authenticated browser-to-runtime adapter. Trace one synthetic request end to end with a request ID. Demonstrate permitted access and denied cross-session access. Keep provider credentials off the client. Confirm submitted model payloads omit camera/location fields in the tested application path. Document browser speech service behavior separately.

### Gate 3 - answer quality and memory controls
Use a fixed, approved document set and a small published question set, including missing evidence and conflicting sources. Check citation support, answer correctness and refusal to invent missing evidence. If durable memory is added, test opt-in, review, deletion and retention behavior; do not assume Stop deletes durable or provider records.

### Gate 4 - supervised first-user pilot
Ask a first-time user to complete the main task without coaching, understand each sharing control and stop the session. Measure time to first answer, completion/error rates and repeated-session battery use on named devices. Define thresholds before the run and report sample size and failures. Keep cycling and safety-critical use out of this pilot.

### Evidence required for every gate
Exact code revision; reproducible steps; synthetic inputs; expected/actual outcomes; browser/device details; timing method; issue log; reviewer identity and permission to attribute. Latency percentiles require repeated measurements and a reported sample size. Zero failures in a finite test is not proof of zero risk.

### Decision rule
Advance only after the agreed critical cases pass or the remaining limitations are explicitly accepted within a narrower scope. A failed gate produces a fix-and-retest plan, not a stronger marketing claim.

## Build trust through useful, testable work
A product hypothesis and partnership scope - not a validated market or an investment return forecast.

### Initial use case
A stationary, opt-in companion that accepts a question by text or voice, returns an understandable answer and gives the user visible controls. A developer-review demo comes before a wearable or bicycle product.

### Product hypothesis to test
People may value clear permission boundaries, easy stopping and transparent capability limits alongside useful conversation. Test that hypothesis with prospective users: can they complete a useful task, understand what leaves the device, and choose to return? No retention, revenue or demand metrics are claimed today.

### Potential differentiation
The present demonstrator emphasizes separate sharing controls, visible status, late-response suppression and public evidence. Comparative superiority over Google, Amazon or other companions has not been measured. A credible comparison would use the same task, device conditions and scoring method across products.

### Requested contributions
Android/browser specialist: voice and lifecycle reliability. Integration engineer: authenticated runtime adapter and retrieval. Independent reviewer: reproducible boundary tests. Potential funder: scoped support for agreed engineering, test hardware and evaluation. Contributions, ownership and any compensation require written agreement before work is commissioned.

### Cost and delivery discipline
No budget or delivery date is approved. Build the estimate from engineering effort, device needs, hosting/inference use and independent testing. The current free model Space can sleep or hit quota; free operation is not an unlimited service guarantee. No paid fallback is authorized. A funding discussion must distinguish one-time build costs from ongoing service costs.

### IP, disclosure and public credit
Start with public source and harmless test inputs. Review the repository's actual license before reuse. Handle nonpublic inventions separately and decide whether confidentiality terms are appropriate before disclosure. Do not demand an NDA for material already public. Do not imply named-partner testing, endorsement or approval without evidence and permission.

### The concrete ask
Review the public demo and PR10. Propose one bounded contribution with deliverables, acceptance criteria, cost assumptions and exclusions. Civic Continuum will prioritize repeatable evidence and user control over unsupported claims.

## Show the boundary. Then show the result.
A short demonstration script and a record of the most important editorial corrections.

### Five-minute stationary demonstration
1. Show the off state and explain what each control does.
2. Start Sage; optionally show camera preview, then turn it off. Do not expose bystanders.
3. Run Test Sage's voice. If silent, show the diagnostic and record the failure.
4. Type a harmless question; explain cloud-text sharing before Ask Sage. Show the actual written response and optional playback.
5. Start another request and press Stop. Check no late answer is rendered in that test; confirm device controls stop.
6. Explain remaining limits and invite a reproducible counterexample.

### Use this packet honestly
Use the cover letter as a template, tailoring the recipient and proposed contribution. Demonstrate only available features. Do not silently substitute a prepared success for an observed result. Update this brief when device testing or integration changes the evidence.

### Source register
- [Current device implementation limits](https://github.com/mommommy1960-lang/sage-situated-companion/blob/main/docs/DEVICE_DEMO.md)
- [Tablet observations and release notes](https://github.com/mommommy1960-lang/sage-situated-companion/blob/main/docs/SAGE_TABLET_TEST_2026-10-24.md)
- [Pinned change set](https://github.com/mommommy1960-lang/sage-situated-companion/pull/10)
- [Live demonstrator](https://sage-companion-device-lab.myqueen1960.chatgpt.site/)

### Version note
Public briefing approved for release by Mya P. Brown on October 24, 2026. Current-state claims are tied to repository evidence and founder observations; proposed integration and pilot gates remain future work. This is an invitation to discuss collaboration, not a certification or an offer of financial returns.

### Collaboration starting scope
Start with public information, harmless synthetic examples and separate accounts. Any confidential exchange, contributions, private access or paid work requires separately agreed scope and appropriate authorization. Existing licenses and rights remain in force.
[Mutual collaboration boundaries](https://github.com/mommommy1960-lang/commons-sentience-sandbox/blob/main/docs/continuity/PUBLIC_COLLABORATION_BOUNDARIES.md)

