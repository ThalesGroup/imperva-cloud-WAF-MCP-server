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
