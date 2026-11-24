# PostgreSQL diagnostics

The initial fixed query catalog in [tools/monitoring.sql](tools/monitoring.sql) covers four read-only monitoring categories. Each statement is independent. Run it only on the approved database using a dedicated monitoring login.

| Query | Purpose |
|---|---|
| Activity summary | Count current backends by state and wait category |
| Wait events | Summarize current waits |
| Lock summary | Count locks by mode and granted state |
| Database statistics | Cumulative statistics for the current database |

No query returns SQL statements, credentials or application rows. Statistics are snapshots or cumulative counters, not historical time-series. Compare with timestamped telemetry rather than treating deltas as inherent.

The remaining tools in the skill reference are planned. Do not register them until implemented and reviewed. The query catalog is not yet wired into Lambda or MCP.
