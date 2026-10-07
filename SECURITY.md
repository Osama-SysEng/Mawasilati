# Security Policy

## Reporting

Report suspected vulnerabilities privately to the repository maintainers with:
release/commit, operating system, Python/Flutter versions, reproduction steps,
and impact. Do not include secrets, credentials, or personal data.

## Scope and safe defaults

- Secrets stay out of git: use `.env` locally, `.env.example` for structure.
- No real credentials or patient/user data in issues, logs, or test fixtures.
- Least privilege for service accounts; review dependencies before production.

## Before production use

Operators must configure a secret manager, enable authentication and
authorization, isolate service accounts, define retention and backup policies,
run static and dynamic security testing, and validate rollback in staging.
Full service tests require postgres (see `docker-compose.yml`).
