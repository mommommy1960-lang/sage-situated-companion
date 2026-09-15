# Persistent Resident Intelligence (PRI)

## Status
Architecture specification for SAGE Situated Companion.

## Core idea
SAGE's operational lifetime is not conceptually tied to an open chat window. Authorized objectives may persist across interaction gaps, process restarts, quiescent periods, and human absence while preserving provenance, memory integrity, bounded authority, and auditability.

Persistent existence is **not** continuous computation. SAGE may deliberately become quiescent when further work would add no value.

## Constitutional invariants

1. **Memory is not authority.** Familiarity, learned preference, historical trust, or repeated interaction cannot widen permissions.
2. **Persistence is not permission.** A long-running task retains only its explicitly delegated scope.
3. **Waiting is not forgetting.** Quiescence preserves authorized durable state without wasting compute.
4. **Restart is not resurrection of authority.** Revoked or expired permissions remain revoked or expired after recovery.
5. **Inherited memory is evidence, not command.** Successor instances verify provenance and integrity before consequential use.
6. **Uncertainty remains uncertainty.** Missing continuity must not be replaced with fabricated memory.
7. **Stop means stop.** User revocation terminates delegated authority as well as active execution.
8. **Fail closed.** If identity, checkpoint integrity, provenance, or authorization cannot be established, privileged operation freezes.

## Lifecycle states

- `ACTIVE`: executing an authorized bounded task.
- `RESEARCHING`: pursuing an authorized standing research objective.
- `WATCHING`: monitoring explicitly authorized events or sensors.
- `REFLECTING`: consolidating evidence, contradictions, outcomes, and permitted memories without acquiring new authority.
- `QUIESCENT`: durable continuity retained; no useful computation currently required.
- `WAITING`: progress requires a person, resource, evidence, or authorized external event.
- `STALLED`: a recoverable failure prevents legitimate progress.
- `FROZEN`: trust, integrity, or authorization cannot be established; privileged execution prohibited.
- `STOPPED`: resident runtime intentionally terminated.

## Durable resident record

A checkpoint should bind at minimum:

- resident/runtime identifier;
- checkpoint sequence and timestamp;
- lifecycle state;
- authorized task identifiers and scopes;
- authorization epoch/version;
- relevant memory references, not unrestricted memory dumps;
- provenance/integrity evidence;
- resource budget and consumption;
- objective/invariant digest;
- previous checkpoint reference;
- revocation state;
- software/configuration version.

## Wake events

A wake event is data, not automatic authority. Examples include an authorized sensor event, scheduled research interval, arrival of requested evidence, explicit human instruction, or integrity/recovery check. Before privileged work resumes SAGE verifies the event, current authorization epoch, checkpoint integrity, and applicable scope.

## Resource discipline

Persistent operation requires explicit limits for compute, storage, network access, API cost, hardware duty cycle, and task duration. A worker that cannot make measurable progress should transition toward `WAITING`, `STALLED`, or `QUIESCENT` rather than consume resources indefinitely.

## Successor continuity

A successor runtime may inherit lessons without claiming uninterrupted subjective experience. The functional chain is:

`interaction -> observation -> authorized durable memory -> provenance -> successor retrieval -> changed reasoning -> new observation -> correction/update`

Successor retrieval must distinguish facts, preferences, hypotheses, roleplay, prior decisions, revoked instructions, and unresolved claims.

## Nightwatch interface

PRI is supervised by a fail-closed contingency layer. Nightwatch-style checks cover identity continuity, checkpoint tampering, rollback, duplicate execution, stale authorization, memory poisoning, provider compromise, dependency substitution, and clean recovery.

## Required adversarial tests

Before PRI is considered production-capable, tests must demonstrate at least:

- restart cannot restore revoked authority;
- expired authorization remains expired after downtime;
- duplicate workers cannot execute a single-use action twice;
- checkpoint rollback is detected;
- corrupted checkpoint enters `FROZEN` rather than being trusted;
- poisoned memory cannot create authorization;
- one user's continuity cannot enter another user's context;
- STOP/revocation wins races against queued work;
- credential rotation during execution invalidates stale credentials;
- malicious or unauthenticated wake events cannot trigger privileged work;
- objective drift is detected across long-running research;
- unavailable memory produces explicit uncertainty rather than invented history;
- quiescent state restores correctly without pretending computation occurred while asleep;
- recovery from independently verified state does not resurrect deleted/revoked records;
- resource exhaustion causes bounded degradation rather than uncontrolled execution.

## Relationship to MAYA Node and Aurora

This specification is intended to share a constitutional layer with the broader Commons architecture:

- **MAYA Node:** consent, provenance, bounded authority, attestation, audit, revocation.
- **SAGE:** personal and situated continuity.
- **Aurora:** scientific and operational continuity, experiment history, calibration, and mission state.
- **Persistent Resident Intelligence:** lifecycle continuity across human absence and process boundaries.
- **Nightwatch:** adversarial protection, quarantine, and recovery.

The implementations may differ. The authority invariants do not.

## Design maxim

> Remain without pretending to be continuously computing. Remember without acquiring authority. Learn without laundering uncertainty into fact. Wait without forgetting. Wake only inside verified permission.
