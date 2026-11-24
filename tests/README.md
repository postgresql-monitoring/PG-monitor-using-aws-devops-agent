# Validation checklist

Python syntax checks passed for both Lambda source files. The maintainer supplied evidence from a controlled non-production test, not a deployment certification of this repository revision.

- [x] Observe a real high-CPU CloudWatch alarm.
- [x] Complete a user-triggered AWS DevOps Agent investigation.
- [x] Observe three PostgreSQL MCP tool invocations in the investigation timeline.

See the [sanitized observed case study](../docs/blog-postgresql.html#validated-cpu). The test does not establish automatic webhook delivery or individual tool response payloads.

- [ ] Run the skill packaging script and check archive filenames.
- [ ] Test fixed catalog queries on an approved non-production instance.
- [ ] Check effective monitoring grants and absence of write privileges.
- [ ] Verify TLS, IAM scope, network access and secret redaction.
- [ ] Test timeout, row cap and concurrency behavior.
- [ ] Verify the Gateway tool schemas and invocation boundaries.
- [ ] Confirm on-demand investigations use current evidence.
- [ ] Verify alarm delivery with an approved non-production event.
- [ ] Review sanitized results and distinguish missing data from an observed absence of incidents.
- [ ] Collect actual tested AWS region, PostgreSQL version, evidence and cost measurements.
