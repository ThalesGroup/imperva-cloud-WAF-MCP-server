# Security Policy

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### How to Report

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Email your findings to: **oss@thalesgroup.com**
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Initial Response**: Within 48 hours of your report
- **Status Updates**: Every 7 days until the issue is resolved
- **Resolution Timeline**: Security fixes are prioritized and typically released within 30 days
- **Credit**: We will acknowledge your contribution in the release notes (if desired)

## Disclosure Policy

We follow responsible disclosure practices and work with reporters through the following process:

1. Report the vulnerability privately via email
2. Allow us time to investigate and develop a fix
3. We will notify you when a fix is ready for testing
4. Public disclosure will occur after the fix is released
5. You will be credited for the discovery (unless you prefer to remain anonymous)

## Security Best Practices

### Credentials Management

:warning: **NEVER store credentials in source code or configuration files**

- Use environment variables for API credentials (`API_ID`, `API_KEY`)
- Store sensitive data in secure secret managers
- Enable pre-commit hooks to prevent credential leaks:
  ```bash
  uv run pre-commit install
  ```
- Use GitHub Secrets for CI/CD credentials

### API Security

When using this MCP server:

1. **Protect API Credentials**: Store `API_ID` and `API_KEY` securely
2. **Use HTTPS**: All API communications use HTTPS by default
3. **Environment Isolation**: Use separate credentials for staging and production
4. **Rotate Credentials**: Regularly rotate API keys
5. **Least Privilege**: Grant only necessary permissions to API credentials

### Docker Security

When running the MCP server via Docker:

- Always pull the latest image for security updates
- Use the `--rm` flag to automatically remove containers after use
- Never log or expose environment variables containing secrets
- Run containers with minimal privileges

## Security Configuration

### Required Environment Variables

```bash
API_ID=<your-api-id>          # Required for authentication
API_KEY=<your-api-key>        # Required for authentication
```

## Security Updates

- Security patches are released as soon as possible after verification
- All security updates are documented in release notes
- Critical vulnerabilities receive immediate patch releases
- Subscribe to repository releases to receive notifications

## Known Security Considerations

### Unauthenticated `streamable-http` transport (Resolved 2026-09-02)

Reported 2026-09-01 by **Syed Anas Mohiuddin**, maintainer of
[mcp-safeguard](https://github.com/search?q=mcp-safeguard) (open-source MCP security scanner):
when run with `STDIO=false` (`streamable-http` transport), the server binds all network
interfaces and performs no authentication of the calling MCP client — the default
`AUTH_MODE=api_key` strategy only attaches this server's own outbound Imperva credentials to
each upstream call, it never verifies the caller. Any network caller that can reach the port
gets every tool with the operator's credentials silently attached.

Resolved 2026-09-02:
- Fail closed at startup when `streamable-http` is selected with the default `api_key` auth
  mode, or when an `AUTH_MODE=plugin` `AuthStrategy` returns no middlewares (opt-out via an
  explicit env var), instead of silently starting an open listener — deployers must set
  `AUTH_MODE=plugin` with a real caller-verifying `AuthStrategy` that registers at least one
  middleware. This narrows, but doesn't fully eliminate, the inherent limitation of a
  pluggable-strategy design: we can check that a middleware was registered, not that it
  actually verifies callers correctly — that's still on the plugin author.
- Default the HTTP bind address to `127.0.0.1` instead of `0.0.0.0`, requiring an explicit
  opt-in to bind all interfaces. The same default now also applies to the Prometheus metrics
  listener (`PROMETHEUS_CLIENT_ENABLED=true`), which previously bound `0.0.0.0`
  unconditionally regardless of this fix's other settings.
- Anyone currently running `STDIO=false` in Docker (`-p 8050:8050`) or Kubernetes must
  explicitly set `HTTP_HOST=0.0.0.0` to preserve connectivity — see the "Advanced: Running as
  a Remote HTTP Server" section in the README for details.

We're grateful to Syed Anas Mohiuddin for the detailed, responsible report and reproduction
steps, and are crediting him here per his request.

### Recommended Enhancements

We welcome contributions for:
- Secret scanning tools integration
- Enhanced credential validation
- Security audit logging
- Rate limiting mechanisms

## Security Scanning

This project uses:
- **BlackDuck**: Dependency vulnerability scanning
- **Pylint**: Code quality and security checks
- **Pre-commit hooks**: Prevent common security issues

## Contact

For security-related questions or concerns:
- Email: oss@thalesgroup.com
- For general support: Open a GitHub issue (non-security related only)
