# SAGE × MAYA integration checkpoint — 2026-10-27

## Completed in this branch
- Inspected current `capabilities.py`, `bridge.py`, `audit.py`, `identity.py` and baseline sovereignty tests.
- Preserved the existing expiring, revoked, single-use capability behavior unchanged.
- Added an optional SQLite-backed local audit journal with reopen integrity checks and transactional append.
- Added four targeted tests for restart persistence, modification detection, bridge denial receipt, and sequential append.

## Important limits
- New tests have been **written, not executed or verified green**. CI must run before merge.
- SQLite audit is a local development adapter, **not a deployed Maya Node integration** or remotely anchored tamper-proof record.
- No owner memory records are deleted by this change; deleting memory requires identifying actual memory storage and handling linked indexes, backups, receipts and audit retention.
- No network adapter to Maya Node has been implemented. The bridge still takes an injected `verify_current_authority` callback; a future authenticated client must validate current server-side permission and fail closed.
- No live-model API or paid service is needed for these local tests.

## Integration acceptance gates
1. CI confirms existing permission tests and new persistence tests pass, including denial, expiry, revocation, single-use and effect-failure behavior.
2. Map actual SAGE memory storage and indexes; add owner-scoped deletion with explicit audit metadata that does not contain deleted personal content.
3. Test cross-owner denial, repeat deletion, restart/reload, failure rollback, and backup/retention semantics with synthetic data.
4. Identify hosted Maya Node's source and auth protocol; use signed/verified, scoped, expiring authority at the server, with no secrets in source.
5. Run end-to-end synthetic account integration and receipt export/consistency checks; document results before deployment.

No production website was changed. No hosted deletion test was run. No claim of production readiness is made.
