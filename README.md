# Vigar

[![Security Scan](https://github.com/fsusak03/Vigar/actions/workflows/security.yml/badge.svg)](https://github.com/fsusak03/Vigar/actions/workflows/security.yml)

A Django web application with automated security scanning.

## Development

Use the provided Makefile for common development tasks:

```bash
make dev      # Start development environment
make prod     # Start production environment  
make stop     # Stop all services
make logs     # View logs
make rebuild  # Rebuild containers
```

## Security

This project includes automated security scanning via Semgrep in CI/CD. See [SECURITY.md](SECURITY.md) for details.