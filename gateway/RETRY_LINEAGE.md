# Scoped retry identity (not exactly-once)

The client saves a request sidecar before transport. Reusing that file reuses its
opaque request ID. Changed content requires explicit `--new-revision`; the old file
is retained, and the gateway resolves the recorded parent before accepting the
same logical case. Copies submitted as genuinely independent cases must use a
separate request state. Neither a username nor client instance proves identity.

Before a create, the client atomically marks its request attempted. A timeout or
later retry is reconciliation-only; if no durable row is visible, the result is
`outcome_unknown`, not permission to create again. Resolve that outcome explicitly.
Direct Owner Feishu mode conservatively stops on attempted retries and requires
Owner reconciliation; it does not silently switch transport.

The production reconciliation backend is the existing Feishu row's 原始JSON
envelope, with server-controlled sink/auth-domain scope, request ID, payload digest
and original payload. No SQLite, ephemeral deployment disk, memory hash or lock is
claimed as a production durable ledger. The table must support searchable JSON
text and the configured identity fields/permissions; otherwise fail closed before
create. Mock JSONL is for isolated tests only. No migration or deployment is done.

Separate processes can race between search and create; Feishu physical duplicates
are NOT globally prevented. Every matching scoped opaque identity remains linked
to one transport case in candidate/Owner admission, with all physical originals
retained. Similar text with different request identities is not merged. A transport
lineage is not proof of an authenticated author or an independent experiment.

The envelope preserves the full permitted payload and structured extension/source
objects. Projection conflicts, missing rights and unknown legacy identity need
explicit governance; contributor rights claims do not constitute Owner approval.

Legacy clients that supply only a fresh submission_id are rejected with 428; they
must upgrade before this gateway is promoted. This avoids claiming retry safety
for clients that never persisted a logical request. CLI names remain unchanged.
