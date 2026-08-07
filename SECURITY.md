# Security policy

## Reporting a vulnerability

Please report security issues through a private
[GitHub security advisory](https://github.com/CodingFeng101/UniGraph/security/advisories/new).
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
- `AUTH_AES_SECRET_KEY` is browser-visible protocol compatibility data, not a
  substitute for TLS. Do not treat the client-side encryption layer as a
  credential boundary.
- Set `COOKIE_SECURE=true` in production. Keep private LLM endpoints disabled
  unless the deployment network is explicitly isolated.
- Set and back up a dedicated `LLM_API_KEY_ENCRYPTION_KEY`. Model API keys are
  encrypted at rest and masked in API responses; losing this key makes stored
  credentials unrecoverable.
- Public password reset is disabled by default because CAPTCHA plus a known
  email address is not sufficient account verification.
- Rotate any credential that has ever been committed, even if the file was
  later deleted.
