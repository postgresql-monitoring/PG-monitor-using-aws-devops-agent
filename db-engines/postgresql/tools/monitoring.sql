-- Illustrative diagnostic catalog. Execute each query independently
-- with an approved monitoring role in a read-only transaction.
-- Activity summary: current database, excluding monitoring connection.
SELECT state, wait_event_type, count(*) AS sessions
FROM pg_stat_activity
WHERE datname = current_database() AND pid <> pg_backend_pid()
GROUP BY state, wait_event_type
ORDER BY sessions DESC
LIMIT 50;

-- Wait events: current database.
SELECT wait_event_type, wait_event, count(*) AS sessions
FROM pg_stat_activity
WHERE datname = current_database() AND pid <> pg_backend_pid()
  AND wait_event IS NOT NULL
GROUP BY wait_event_type, wait_event
ORDER BY sessions DESC
LIMIT 50;

-- Lock summary: backends attached to the current database.
SELECT l.locktype, l.mode, l.granted, count(*) AS locks
FROM pg_locks AS l
JOIN pg_stat_activity AS a ON a.pid = l.pid
WHERE a.datname = current_database() AND a.pid <> pg_backend_pid()
GROUP BY l.locktype, l.mode, l.granted
ORDER BY locks DESC
LIMIT 50;

-- Cumulative database statistics (not an incident timeline).
SELECT numbackends, xact_commit, xact_rollback, blks_read,
       blks_hit, deadlocks, stats_reset
FROM pg_stat_database
WHERE datname = current_database()
LIMIT 1;
