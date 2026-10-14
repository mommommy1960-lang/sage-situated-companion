# SAGE Situated Companion Phase 1 Feasibility Brief

**Date:** October 14, 2026  
**Owner:** Mya P. Brown, Civic Continuum  
**Evidence level:** Implemented documentation; proposed hardware and evaluation plan

SAGE is an early-stage, consent-governed companion system combining a software runtime with a future mobile hardware enclosure, sensors, local controls, and an auditable permission boundary. The current scope is a non-confidential Phase 1 feasibility review.

**SAGE is not represented as production-ready, safety-certified, or authorized for manufacturing.** Design requirements below are intended boundaries, not claims of validated hardware performance.

## Completed on October 14

Civic Continuum prepared a six-page preliminary hardware intake covering all 21 sections of the requested PRD structure, checked its rendered layout, and sent it in the existing Minewing feasibility correspondence. Unresolved inputs were marked TBD rather than filled with example industrial specifications.

Ricky Yuan is the Minewing contact for this preliminary SAGE feasibility exchange. His public professional profile describes electronics solutions and integrated manufacturing. A formal managerial job title, contracted development relationship, endorsement, or completed technical assessment is not established.

- [Minewing official website](https://www.minewingems.com/)
- [Ricky Yuan public professional profile](https://www.linkedin.com/in/ricky-yuan-9aa1b4375/)
- [Civic Continuum reviewer dashboard](https://github.com/mommommy1960-lang/commons-sentience-sandbox/blob/main/docs/civic-continuum/DR_THOMAS_REVIEW_DASHBOARD.md)

## Non-confidential functional boundaries

| Area | Intended function or required boundary | Still to define |
|---|---|---|
| Companion runtime | Conversation, contextual continuity and situational companionship within explicit, scope-limited permission | Measurable performance and supported use cases |
| Camera and microphone | Authorized environmental context and user voice input; no continuous raw recording, storage or transmission by default | Sensor selection, capture metrics and processing allocation |
| Physical privacy control | Disable relevant sensor power or physical signal path independently of application software | Electrical design, affected paths and verification method |
| Indicators | Concept states include quiet/standby, active conversation and high alert; visible states must correspond to actual sensing and controls | Colors, patterns, privacy/freeze indications and mapping |
| Motion sensing | Defined activity and movement context | Sensor choice, sample rates and accuracy |
| Connectivity and memory | Offline behavior preserves permission and local control; local-first encrypted sensitive storage is intended; cloud continuation requires explicit permission | Device/phone/network allocation, capacity, retention and offline limits |
| Freeze and restoration | User override restricts active capabilities and preserves an auditable record; restoration requires fresh permission | Physical trigger, response time, fault handling and restricted-state behavior |

## Open engineering inputs

TBD means a requirement or decision is unresolved. It does not mean a template example has been adopted.

| Intake area | Open inputs |
|---|---|
| Product and user definition | Intended users, operating environments, quantified customer need and performance targets |
| Electrical and power | Input voltage, battery and charging architecture, runtime, power budget, thermal limits and protections |
| Mechanical and exterior design | Dimensions, weight, reference exterior, mounting/carrying method, material, PCB/battery allocation, drawings and 3D model |
| Firmware and interfaces | Compute/OS choice, drivers, pin definitions, protocols, self-test, watchdog, update/recovery behavior and test points |
| Environmental and reliability | Temperature, humidity, ingress, drop/vibration, duty cycle, service life and reliability targets |
| Compliance | Intended markets, applicable standards, laboratories and acceptance thresholds |
| Materials and BOM | Selected parts, cost ceiling, supply life, lead times and substitution rules |
| Prototype and production planning | Build deliverables, supervised evaluation conditions, fixtures, calibration, serialization, packaging, dates and costs |
| Acceptance and risk | Measurement methods, quantitative pass/fail/stop limits, physical-safety mitigations and evidence needed before promotion |

No final dimensions, voltage, storage capacity, temperature range, BOM, certification level or production batch quantity is asserted by this brief.

## Requested Phase 1 outputs

1. Hardware and firmware requirements and unresolved assumptions.
2. Candidate sensors, compute, power, enclosure and communications architecture.
3. Privacy and physical-safety hazard review.
4. A five-unit supervised prototype plan.
5. Measurable acceptance, failure and stop criteria.
6. Estimated schedule and cost for a separately scoped next stage.

The five units are a planning request, not an order or fabrication authorization. Later design-validation, production-validation and mass-production phases have no approved quantity or launch date.

## Proposed evaluation criteria

| Boundary | Proposed evidence or stop condition |
|---|---|
| Permission and revocation | Consequential actions require current in-scope permission; unauthorized actions stop the evaluation |
| Hardware privacy | Relevant sensor power/signal disables independently of the app; continued capture through the disabled path is a stop condition |
| Freeze and restoration | Active capabilities restrict as specified; restoration without fresh permission fails; response target remains TBD |
| Disconnection and recovery | Local controls and permission remain effective through network loss and reconnection |
| Physical behavior | Electrical, thermal and fault limits and measurement methods must be agreed before testing |
| Indicators and audit | Displayed states correspond to actual control/sensor states; consequential actions have a reviewable record |

These are proposed criteria, not completed hardware tests.

## Current evidence and next step

| State | What is established |
|---|---|
| Completed documentation and correspondence | Preliminary intake prepared, visually checked and sent on October 14 |
| Proposed | Hardware architecture, component choices and supervised prototype evaluation |
| Pending | Minewing review of remaining inputs and the minimum requirements for a separately quoted feasibility/design stage |
| Not established | Hardware feasibility, physical safety, reliability, compliance, manufacturability or production readiness |

The next step is to identify which open inputs are required before a meaningful feasibility assessment and which can be defined within a separately quoted design engagement. No billable engineering, purchasing, tooling, fabrication or manufacturing is authorized by this publication.

## Disclosure boundary

This public brief contains high-level requirements, completed-work status, evidence labels and open gates. Raw correspondence, the supplier-authored intake template, private commercial terms, protected designs, source material, credentials and personal contact details remain in the controlled record.

Public review does not imply endorsement, ownership transfer, a license to manufacture or approval to commercialize. See [Legal and IP Notice](../LEGAL_AND_IP_NOTICE.md). Earlier project records and corrections remain preserved.
