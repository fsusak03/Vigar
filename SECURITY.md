# Security Configuration

This repository includes automated security scanning using [Semgrep](https://semgrep.dev/) as part of the CI/CD pipeline.

## Overview

The security workflow automatically scans the codebase for:
- Security vulnerabilities
- Code quality issues
- Django-specific security patterns
- Python best practices
- Docker configuration security
- Secrets and sensitive information

## How it works

### GitHub Actions Workflow
The security scan runs automatically on:
- Pull requests to `main`, `dev`, or `develop` branches
- Pushes to `main`, `dev`, or `develop` branches  
- Manual triggers via GitHub Actions UI

### Ruleset Configuration
The scan uses multiple rulesets:
- **p/security-audit**: General security vulnerability patterns
- **p/python**: Python-specific security and quality rules
- **p/django**: Django framework security patterns
- **p/docker**: Docker configuration security
- **p/secrets**: Detection of hardcoded secrets

### Custom Rules
Additionally, custom rules in `.semgrep.yml` check for:
- Django DEBUG mode enabled
- Hardcoded Django SECRET_KEY
- Wildcard ALLOWED_HOSTS configuration
- Hardcoded passwords
- Docker security best practices

## Security Findings

When security issues are found:
1. The workflow will fail and block the PR
2. Results are uploaded to GitHub Security tab
3. A comment is added to the PR with details
4. SARIF reports are generated for detailed analysis

## Local Testing

To run security scans locally:

```bash
# Install semgrep
pip install semgrep

# Run with local configuration
semgrep --config=.semgrep.yml .

# Run with remote rulesets (requires internet)
semgrep --config=p/security-audit --config=p/python --config=p/django .
```

## Configuration Files

- `.github/workflows/security.yml`: GitHub Actions workflow
- `.semgrep.yml`: Custom semgrep rules and configuration

## Required Secrets

For enhanced features in private repositories, add `SEMGREP_APP_TOKEN` to your repository secrets. This is optional for public repositories.

## Troubleshooting

- If scans fail due to network issues, the workflow will still run local rules
- Check the Actions logs for detailed error information
- Review the Security tab for findings and recommendations