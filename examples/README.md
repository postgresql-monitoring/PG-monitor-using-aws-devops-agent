# Example investigations

These examples contain synthetic evidence, not live AWS results.

## Healthy database

**Observation:** CPU 8%, 4 connections, read latency 2 ms; no alarm in the illustrative window.

**Finding:** Metrics do not indicate an active incident. Review an idle-in-transaction session if it persists.

**Action:** Read-only observation; no changes.

## Lock contention

**Observation:** Elevated connections and a dominant lock wait category.

**Finding:** Lock contention is a possible explanation. Additional authorized evidence is required to establish blocking relationships and application transaction ownership.

**Recommendation:** Review transaction duration with the application owner and correlate with approved logs and telemetry.

**Action:** No sessions terminated; no configuration changed.

See the [article](../docs/blog-postgresql.html) for an explicitly simulated Agent Space conversation.
