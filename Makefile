SHELL := powershell.exe
.ONESHELL:

.DEFAULT_GOAL := help

help: 
	@echo "Targets: dev, prod, stop, logs, rebuild"

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

.PHONY: rebuild
rebuild:
	docker compose -f Docker-compose.yml build --no-cache
