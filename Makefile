SHELL := powershell.exe
.ONESHELL:

.DEFAULT_GOAL := help

help: 
	@echo "Targets: dev, prod, stop, logs, logs-web, logs-db, ps, rebuild, downv"
	@echo "  migrate     - Run Django migrations"
	@echo "  makemigrations - Create migrations"
	@echo "  test        - Run Django tests in container"
	@echo "  collectstatic - Collect static files"
	@echo "  shell       - Open Django shell"
	@echo "  sh          - Open a shell in the web container"
	@echo "  manage      - Run arbitrary manage.py command (use: make manage CMD=...)"
	@echo "  superuser   - Create Django superuser in running container"
	@echo "  seed        - Seed sample data"
	@echo "  roles       - Create default roles (admin, manager, member)"
	@echo "  psql        - Open psql against the db container"
	@echo "  lint        - Run ruff lint locally"
	@echo "  format      - Run ruff --fix locally"

DEV_FILES := -f Docker-compose.yml -f docker-compose.override.yml

.PHONY: dev
dev: 
	docker compose $(DEV_FILES) --profile dev up --build

.PHONY: prod
prod: 
	docker compose -f Docker-compose.yml --profile prod up --build -d
	@echo "App running at http://localhost:8000"

.PHONY: stop
stop: 
	docker compose -f Docker-compose.yml -f docker-compose.override.yml down --remove-orphans

.PHONY: logs
logs: 
	docker compose -f Docker-compose.yml logs -f

.PHONY: logs-web
logs-web:
	docker compose -f Docker-compose.yml logs -f web

.PHONY: logs-db
logs-db:
	docker compose -f Docker-compose.yml logs -f db

.PHONY: ps
ps:
	docker compose -f Docker-compose.yml ps

.PHONY: rebuild
rebuild:
	docker compose -f Docker-compose.yml build --no-cache

.PHONY: superuser
superuser:
	docker compose -f Docker-compose.yml up -d db web
	docker compose -f Docker-compose.yml exec web python manage.py createsuperuser

.PHONY: seed
seed:
	docker compose -f Docker-compose.yml up -d db web
	docker compose -f Docker-compose.yml exec web python manage.py seed_data

.PHONY: roles
roles:
	docker compose -f Docker-compose.yml up -d db web
	docker compose -f Docker-compose.yml exec web python manage.py create_roles
.PHONY: psql
psql:
	docker compose -f Docker-compose.yml exec db psql -U vigar -d vigar

.PHONY: migrate
migrate:
	docker compose -f Docker-compose.yml up -d db web
	docker compose -f Docker-compose.yml exec web python manage.py migrate

.PHONY: makemigrations
makemigrations:
	docker compose -f Docker-compose.yml up -d db web
	docker compose -f Docker-compose.yml exec web python manage.py makemigrations

.PHONY: test
test:
	docker compose -f Docker-compose.yml up -d db web
	docker compose -f Docker-compose.yml exec web python manage.py test

.PHONY: collectstatic
collectstatic:
	docker compose -f Docker-compose.yml up -d web
	docker compose -f Docker-compose.yml exec web python manage.py collectstatic --noinput

.PHONY: shell
shell:
	docker compose -f Docker-compose.yml exec web python manage.py shell

.PHONY: sh
sh:
	docker compose -f Docker-compose.yml exec web sh

.PHONY: manage
manage:
	docker compose -f Docker-compose.yml up -d db web
	docker compose -f Docker-compose.yml exec web python manage.py $(CMD)

.PHONY: downv
downv:
	docker compose -f Docker-compose.yml -f docker-compose.override.yml down -v --remove-orphans

.PHONY: lint
lint:
	ruff check .

.PHONY: format
format:
	ruff check --fix .