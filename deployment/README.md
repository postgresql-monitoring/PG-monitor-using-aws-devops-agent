# Deployment plan

This guide describes the intended two-stage design; the infrastructure templates and deployed Lambda/Gateway wiring are not yet included or validated.

## Prerequisites

- Authorized non-production RDS PostgreSQL database and approved AWS account.
- Private network path for the diagnostic function, approved monitoring identity and a scoped Secret Manager secret.
- Region support for AWS DevOps Agent and Bedrock AgentCore Gateway; verify current service documentation.
- CloudWatch and Database Insights available for the chosen database.

## Stage 1: Monitoring layer

Review the database role and effective grants. Configure the approved diagnostic service with fixed catalog queries, read-only transactions, verified TLS, bounded result sizes and timeouts. Collect CloudWatch metrics and review appropriate alarm thresholds with the database owner.

## Stage 2: Agent integration

Once the diagnostic Lambda is implemented and reviewed, register its approved tool schemas in AgentCore Gateway, configure the authorized Agent Space integration, and confirm the skill is enabled. Begin with on-demand health checks; enable approved alarm delivery only after verifying the integration.

## Skill packaging

From the repository root:

    python3 scripts/package_skill.py

This creates the local skill archive under build/. Upload it through the authorized Agent Space workflow. Review the current AWS service documentation before deployment.

## Validation and cleanup

Complete the checklist in [tests/README.md](../tests/README.md). Remove only project-owned resources after confirming dependencies and retention requirements. Record actual region, database version, sanitized test evidence and measured cost before describing the deployment as validated.

## AWS references

- [AWS DevOps Agent documentation](https://docs.aws.amazon.com/devopsagent/latest/userguide/)
- [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-add-target-lambda.html)
