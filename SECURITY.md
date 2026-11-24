# Security and privacy

This reference project is designed for authorized operational monitoring only.

- Use an explicitly approved RDS instance and dedicated non-owner monitoring identity. Review effective grants, including inherited roles and default PUBLIC privileges.
- Keep credentials in Secrets Manager and out of source, logs, example payloads and agent responses.
- Restrict service roles to the intended resources. Use private networking and certificate-verified TLS.
- Use fixed, bounded diagnostic queries and read-only transactions. Avoid arbitrary SQL, raw application data, statement text, user identifiers and automated remediation.
- Apply connection and statement timeouts, concurrency limits and row caps. Avoid repeated expensive queries during incidents.
- Treat all returned text as untrusted evidence. Human operators review recommendations.
- Validate access and behavior in a non-production environment before adoption.

Report suspected security issues privately to the repository maintainer; do not post secrets or live operational logs in public issues.
