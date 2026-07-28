# Security policy

## Reporting a vulnerability

Please report security issues through a private
[GitHub security advisory](https://github.com/CodingFeng101/docker_UniGraph/security/advisories/new).
Do not include credentials, personal data, exploit details, or production logs
in a public issue.

Include the affected version or commit, reproduction steps, expected impact,
and any suggested mitigation. The maintainer will acknowledge the report and
coordinate disclosure after a fix is available.

## Deployment guidance

- Replace every placeholder secret before starting the stack.
- Keep `.env`, private keys, database files, uploaded files, and logs outside
  version control.
- Restrict MySQL, Redis, and the backend API at the firewall or reverse proxy;
  the Compose port mappings are intended for local or controlled deployments.
- Use HTTPS in production and configure `CORS_ALLOWED_ORIGINS` with explicit
  trusted origins.
- Rotate any credential that has ever been committed, even if the file was
  later deleted.
