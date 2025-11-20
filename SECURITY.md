# Security Policy

## Supported Versions

We actively support the following versions of Ardour MCP with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

We take the security of Ardour MCP seriously. If you believe you have found a security vulnerability, please report it to us responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:

- **Email**: security@raibid-labs.com
- **Subject**: [SECURITY] Ardour MCP Vulnerability Report

### What to Include

Please include the following information in your report:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** of the vulnerability
4. **Affected versions** (if known)
5. **Suggested fix** (if you have one)
6. **Your contact information** for follow-up

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 7-14 days
  - High: 14-30 days
  - Medium: 30-60 days
  - Low: Next release cycle

### Security Update Process

1. We will acknowledge receipt of your vulnerability report
2. We will investigate and validate the issue
3. We will develop and test a fix
4. We will notify you before public disclosure
5. We will release a security update
6. We will publicly disclose the vulnerability with credit to the reporter (unless you prefer to remain anonymous)

### Security Best Practices

When using Ardour MCP:

1. **Keep Updated**: Always use the latest version
2. **Network Security**: Ardour MCP communicates with Ardour via OSC (UDP port 3819). Ensure this port is not exposed to untrusted networks
3. **Input Validation**: While MCP tools validate inputs, be cautious when using untrusted AI assistants
4. **Permissions**: Run Ardour MCP with the minimum required permissions
5. **Session Security**: Protect your Ardour sessions and audio files with appropriate file permissions

### Known Security Considerations

- **Local Communication**: Ardour MCP communicates with Ardour on localhost via OSC protocol
- **No Authentication**: OSC communication with Ardour has no built-in authentication
- **File Access**: Ardour MCP can read session information but does not directly access audio files
- **AI Context**: Information about your Ardour session is shared with the AI assistant

### Security Hall of Fame

We appreciate the security research community. Researchers who responsibly disclose vulnerabilities will be acknowledged here (with permission):

- _None yet - help us improve security!_

## Questions?

If you have questions about this security policy, please contact:
- **Email**: contact@raibid-labs.com
- **Discussions**: [GitHub Discussions](https://github.com/raibid-labs/ardour-mcp/discussions)
