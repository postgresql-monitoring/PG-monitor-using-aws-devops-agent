# PostgreSQL diagnostics

The initial fixed query catalog in [tools/monitoring.sql](tools/monitoring.sql) covers four read-only monitoring categories. Each statement is independent. Run it only on the approved database using a dedicated monitoring login.

| Query | Purpose |
|---|---|
| Activity summary | Count current backends by state and wait category |
| Wait events | Summarize current waits |
| Lock summary | Count locks by mode and granted state |
| Database statistics | Cumulative statistics for the current database |

No query returns SQL statements, credentials or application rows. Statistics are snapshots or cumulative counters, not historical time-series. Compare with timestamped telemetry rather than treating deltas as inherent.

A reviewed Lambda implementation containing eleven fixed monitoring tools is available in [deployment/lambda/diagnostics](../../deployment/lambda/diagnostics/). EXPLAIN is intentionally unavailable. Gateway configuration and live database testing remain pending.
