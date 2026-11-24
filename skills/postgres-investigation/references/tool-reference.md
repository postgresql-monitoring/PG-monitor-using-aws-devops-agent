# Tool reference

Login: `dbops_reader` with `pg_monitor` on database `test`. All tools are read-only. `statement_timeout` is 8s. Row cap is 50.

| Tool | Arguments | Source |
|---|---|---|
| check_extensions | none | pg_extension |
| get_activity_summary | none | pg_stat_activity |
| get_blocking_sessions | none | pg_stat_activity, pg_blocking_pids |
| get_slow_queries | min_seconds (1-3600, default 5) | pg_stat_activity |
| get_top_statements | order_by: total_time, mean_time, calls, io; limit | pg_stat_statements |
| get_wait_events | none | pg_stat_activity |
| get_lock_summary | none | pg_locks |
| get_index_usage | schema (default public) | pg_stat_user_tables |
| get_unused_indexes | schema (default public) | pg_stat_user_indexes |
| get_database_stats | none | pg_stat_database |
| get_replication_lag | none | pg_stat_replication |
| explain_query | queryid (SELECT only) | EXPLAIN of pg_stat_statements.query |

## Thresholds (db.t4g.small)

| Metric | Warning | High |
|---|---|---|
| CPUUtilization | 70% for 5 min | 90% for 5 min |
| DatabaseConnections | 40 | 80 |
| ReadLatency | 20 ms | 50 ms |
| FreeableMemory | under 200 MB | under 100 MB |

Do not recommend killing sessions. `dbops_reader` cannot call `pg_terminate_backend`.

The tool list describes the intended interface. The initial catalog implements aggregate activity, waits, locks and database statistics; other tools require separate implementation and privacy review. `explain_query` is disabled in the initial release. Thresholds are illustrative, not measured or universally appropriate.
