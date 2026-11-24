# Example investigations

The first two examples are synthetic. The third summarizes a real controlled non-production test.

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

## Observed high CPU investigation

In a controlled test, RDS CPU reached approximately 100% from a ~5% baseline, two alarms fired, and AWS DevOps Agent completed a user-triggered investigation in 5 minutes 19 seconds. Three PostgreSQL MCP tool calls were recorded. No mitigation was executed. See the [sanitized case study](../docs/blog-postgresql.html#validated-cpu); automatic webhook triggering remains unverified.
