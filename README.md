# Vigar

A Dockerized Django REST API for clients, projects, tasks, and time entries. Comes with JWT auth, role scaffolding, API docs (drf-spectacular), hardened Docker setup, and CI.

## Features
- Django 5 + DRF
- JWT auth (login/refresh) and user registration
- Entities: Clients, Projects, Tasks, Time Entries
- API docs: /api/docs (Swagger UI), /api/redoc
- Docker: multi-stage build, non-root runtime, hardened compose
- Dev UX: compose override with hot reload, Makefile helpers
- CI: Lint (ruff) + checks/tests on dev; Docker publish split into follow-up workflow
- Renovate: updates for Python, Docker, and GitHub Actions

## Quick start

- Local (Docker dev profile):
  - make dev (or docker compose -f Docker-compose.yml -f docker-compose.override.yml --profile dev up --build)
  - Open http://localhost:8000/api/docs

- Production-like (gunicorn):
  - make prod (or docker compose -f Docker-compose.yml --profile prod up --build -d)
  - Open http://localhost:8000

Stop/clean:
- make stop (down containers)
- make downv (down + remove volumes)

## Environment
Create a .env file in repo root (used by Docker Compose) with at least:

Notes:
- CI uses SQLite by setting USE_SQLITE=True.
- DEBUG can be toggled with DJANGO_DEBUG=True in dev override.

## Makefile cheatsheet
- dev: Run dev stack (hot reload)
- prod: Run prod-like stack (gunicorn)
- stop: Stop services
- logs / logs-web / logs-db: Tail logs
- ps: List services
- rebuild: Build without cache
- downv: Down and remove volumes
- migrate / makemigrations: DB migrations
- test: Run Django tests
- collectstatic: Collect static files
- superuser: Create Django superuser
- seed: Seed sample data
- roles: Ensure default roles (admin, manager, member)
- shell: Django shell; sh: container shell
- manage: Pass-through manage.py command (make manage CMD="showmigrations")
- lint / format: Ruff lint and auto-fix

## API
Base path: /api

Auth
- POST /api/auth/register/ — create user, returns JWT pair
- POST /api/auth/login/ — obtain access/refresh
- POST /api/auth/refresh/ — refresh access
- POST /api/auth/verify/ — verify token

Health
- GET /api/health/

Resources (router)
- /api/clients/ — public CRUD
- /api/projects/ — public CRUD
- /api/tasks/ — CRUD (project membership rules apply)
- /api/time-entries/ — CRUD (project membership rules apply)
  - GET /api/time-entries/report/by-project — report with optional date_from/date_to

Docs
- Swagger: /api/docs/
- ReDoc: /api/redoc/
- OpenAPI schema: /api/schema/

## Development tips
- Assign roles: make roles
- Seed sample data: make seed
- Create superuser: make superuser
- SQLite for quick local runs: set USE_SQLITE=True in environment and run manage commands outside Docker.

## CI/CD
- Workflow CI (dev): Lint + checks/tests on push/PR to dev.
- Workflow Publish Docker (dev): Triggers only after CI (dev) succeeds on push to dev; publishes ghcr.io/<owner>/vigar:dev-latest and dev-<sha>.

## Security
- Hardened container: read-only FS, dropped caps, no-new-privileges, tmpfs /tmp.
- JWT auth enabled. Swagger persists authorization.
- Renovate runs on every push, with a pre-step Trivy scan failing on CRITICAL vulns.

## License
MIT
# Vigar