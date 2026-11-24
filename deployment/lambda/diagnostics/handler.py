import json
import os
import re

import boto3
import psycopg
from psycopg.rows import dict_row

SECRET_ID = os.environ["DB_SECRET_ID"]
STATEMENT_TIMEOUT_MS = min(8000, max(1, int(os.environ.get("STATEMENT_TIMEOUT_MS", "8000"))))
MAX_ROWS = min(50, max(1, int(os.environ.get("MAX_ROWS", "50"))))
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")

_secret = None


def _creds():
    global _secret
    if _secret is None:
        kwargs = {}
        endpoint = os.environ.get("SECRETS_ENDPOINT")
        if endpoint:
            kwargs["endpoint_url"] = endpoint
        raw = boto3.client("secretsmanager", **kwargs).get_secret_value(SecretId=SECRET_ID)["SecretString"]
        _secret = json.loads(raw)
    return _secret


def _conn():
    c = _creds()
    return psycopg.connect(
        host=c["host"],
        port=int(c.get("port", 5432)),
        dbname=c["dbname"],
        user=c["username"],
        password=c["password"],
        sslmode="verify-full",
        sslrootcert=os.environ["RDS_CA_BUNDLE"],
        connect_timeout=5,
        options=f"-c statement_timeout={STATEMENT_TIMEOUT_MS} -c default_transaction_read_only=on",
        row_factory=dict_row,
    )


def _clamp(value, default, lo, hi):
    try:
        n = int(value if value is not None else default)
    except (TypeError, ValueError):
        n = default
    return max(lo, min(hi, n))


def _query(sql, params=None):
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params or {})
        rows = cur.fetchmany(MAX_ROWS)
    return [_jsonable(r) for r in rows]


def _jsonable(row):
    out = {}
    for k, v in row.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        elif isinstance(v, (bytes, memoryview)):
            out[k] = None
        else:
            try:
                json.dumps(v)
                out[k] = v
            except TypeError:
                out[k] = str(v)
    return out


def _ident(name, default):
    value = name or default
    if not IDENT.match(value):
        raise ValueError(f"invalid identifier: {value}")
    return value


def check_extensions(_):
    return _query(
        """
        SELECT extname, extversion
        FROM pg_extension
        WHERE extname IN ('pg_stat_statements')
        """
    )


def get_activity_summary(_):
    return _query(
        """
        SELECT state, wait_event_type, count(*) AS sessions,
               count(*) FILTER (WHERE state = 'active') AS active
        FROM pg_stat_activity
        WHERE datname = current_database() AND pid <> pg_backend_pid()
        GROUP BY state, wait_event_type
        ORDER BY sessions DESC
        """
    )


def get_blocking_sessions(_):
    return _query(
        """
        SELECT a.pid,
               a.state,
               a.wait_event_type,
               a.wait_event,
               now() - a.xact_start AS xact_age,
               now() - a.query_start AS query_age,
               pg_blocking_pids(a.pid) AS blocked_by
        FROM pg_stat_activity a
        WHERE a.datname = current_database() AND (
           cardinality(pg_blocking_pids(a.pid)) > 0
           OR a.pid IN (
                SELECT DISTINCT unnest(pg_blocking_pids(pid))
                FROM pg_stat_activity
                WHERE datname = current_database()
                  AND cardinality(pg_blocking_pids(pid)) > 0
           ))
        ORDER BY cardinality(pg_blocking_pids(a.pid)) DESC, a.xact_start
        """
    )


def get_slow_queries(args):
    seconds = _clamp(args.get("min_seconds"), 5, 1, 3600)
    return _query(
        """
        SELECT pid, state, wait_event_type, wait_event,
               now() - query_start AS query_age,
               now() - xact_start AS xact_age
        FROM pg_stat_activity
        WHERE datname = current_database()
          AND state = 'active'
          AND pid <> pg_backend_pid()
          AND now() - query_start > make_interval(secs => %(seconds)s)
        ORDER BY query_start
        """,
        {"seconds": seconds},
    )


def get_top_statements(args):
    order = {
        "total_time": "total_exec_time",
        "mean_time": "mean_exec_time",
        "calls": "calls",
        "io": "shared_blks_read",
    }.get(args.get("order_by"), "total_exec_time")
    limit = _clamp(args.get("limit"), 20, 1, MAX_ROWS)
    sql = f"""
        SELECT queryid, calls, rows,
               round(total_exec_time::numeric, 1) AS total_exec_ms,
               round(mean_exec_time::numeric, 2) AS mean_exec_ms,
               shared_blks_hit, shared_blks_read
        FROM pg_stat_statements
        WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
        ORDER BY {order} DESC
        LIMIT %(limit)s
    """
    return _query(sql, {"limit": limit})


def get_wait_events(_):
    return _query(
        """
        SELECT wait_event_type, wait_event, state, count(*) AS sessions
        FROM pg_stat_activity
        WHERE datname = current_database()
          AND pid <> pg_backend_pid()
        GROUP BY wait_event_type, wait_event, state
        ORDER BY sessions DESC
        """
    )


def get_lock_summary(_):
    return _query(
        """
        SELECT l.locktype, l.mode, l.granted, count(*) AS locks
        FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid
        WHERE a.datname = current_database() AND a.pid <> pg_backend_pid()
        GROUP BY l.locktype, l.mode, l.granted
        ORDER BY l.granted, locks DESC
        """
    )


def get_index_usage(args):
    schema = _ident(args.get("schema"), "public")
    return _query(
        """
        SELECT schemaname, relname, seq_scan, idx_scan,
               n_live_tup,
               CASE WHEN seq_scan + idx_scan = 0 THEN 0
                    ELSE round(100.0 * idx_scan / (seq_scan + idx_scan), 1)
               END AS idx_scan_pct
        FROM pg_stat_user_tables
        WHERE schemaname = %(schema)s
        ORDER BY seq_scan DESC
        """,
        {"schema": schema},
    )


def get_unused_indexes(args):
    schema = _ident(args.get("schema"), "public")
    return _query(
        """
        SELECT s.schemaname, s.relname AS table_name, s.indexrelname AS index_name,
               s.idx_scan, pg_size_pretty(pg_relation_size(s.indexrelid)) AS index_size
        FROM pg_stat_user_indexes s
        JOIN pg_index i ON i.indexrelid = s.indexrelid
        WHERE s.schemaname = %(schema)s
          AND s.idx_scan = 0
          AND NOT i.indisunique
          AND NOT i.indisprimary
        ORDER BY pg_relation_size(s.indexrelid) DESC
        """,
        {"schema": schema},
    )


def get_database_stats(_):
    return _query(
        """
        SELECT datname, numbackends, xact_commit, xact_rollback,
               blks_read, blks_hit,
               tup_returned, tup_fetched, tup_inserted, tup_updated, tup_deleted,
               conflicts, deadlocks, temp_files, temp_bytes,
               stats_reset
        FROM pg_stat_database
        WHERE datname = current_database()
        """
    )


def get_replication_lag(_):
    return _query(
        """
        SELECT state,
               sync_state,
               pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS send_lag_bytes,
               pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS replay_lag_bytes,
               replay_lag
        FROM pg_stat_replication
        """
    )


TOOLS = {
    "check_extensions": check_extensions,
    "get_activity_summary": get_activity_summary,
    "get_blocking_sessions": get_blocking_sessions,
    "get_slow_queries": get_slow_queries,
    "get_top_statements": get_top_statements,
    "get_wait_events": get_wait_events,
    "get_lock_summary": get_lock_summary,
    "get_index_usage": get_index_usage,
    "get_unused_indexes": get_unused_indexes,
    "get_database_stats": get_database_stats,
    "get_replication_lag": get_replication_lag,
}


def lambda_handler(event, context):
    name = ""
    client = getattr(context, "client_context", None)
    custom = getattr(client, "custom", None) if client else None
    if isinstance(custom, dict):
        name = custom.get("bedrockAgentCoreToolName", "")
    if not isinstance(name, str):
        return {"ok": False, "error": "invalid tool name"}
    if "___" in name:
        name = name.split("___", 1)[1]
    if not name and isinstance(event, dict):
        name = event.get("tool") or event.get("name") or ""
    args = {}
    if isinstance(event, dict):
        raw = event.get("arguments") or event.get("args")
        if raw is None:
            args = {k: v for k, v in event.items() if k not in ("tool", "name")}
        elif isinstance(raw, str):
            try:
                args = json.loads(raw)
            except ValueError:
                return {"ok": False, "error": "invalid arguments"}
        else:
            args = raw
    if not isinstance(name, str) or not isinstance(args, dict):
        return {"ok": False, "error": "invalid tool name or arguments"}
    fn = TOOLS.get(name)
    if fn is None:
        return {"ok": False, "error": "unknown tool", "tools": sorted(TOOLS)}
    try:
        return {"ok": True, "tool": name, "rows": fn(args)}
    except Exception:
        return {"ok": False, "tool": name, "error": "diagnostic failed; contact the operator"}
