# Lambda source and packaging

Two independent functions are included:

- diagnostics/handler.py — fixed, read-only PostgreSQL monitoring tools, using a dedicated monitoring identity.
- webhook/lambda_function.py — signed forwarding of authorized alarm events to the configured Agent Space webhook.

## Configuration

For diagnostics, configure DB_SECRET_ID, RDS_CA_BUNDLE (path to the approved RDS CA bundle), and optionally SECRETS_ENDPOINT, STATEMENT_TIMEOUT_MS and MAX_ROWS. The secret must specify host, port, dbname, username and password. Use verified TLS; keep values out of Git. For the webhook, use WEBHOOK_SECRET_ARN and APPROVED_WEBHOOK_HOST. Scope secret access and invocation permissions to the intended resources. Review the event payload for sensitive content before enabling forwarding. The current event format and signature have not been validated against a live Agent Space.

Illustrative instance identifier: **pgmonitor-test**.

The supplied build archive included Python 3.12 Linux arm64 wheels, a top-level build/ directory and macOS metadata. Rebuild the archive for the selected Lambda runtime and architecture, placing handler.py and dependencies at the ZIP root; include only necessary files. Keep generated ZIPs out of source control. The existing skill packaging script regenerates the skill archive from the reviewed Markdown files.

## Validation status

Python syntax checks passed for both source files. Live database queries, webhook delivery, IAM, TLS, and Lambda integration have not been tested. The initial release intentionally excludes dynamic EXPLAIN and raw query text. No AWS resources were modified.
