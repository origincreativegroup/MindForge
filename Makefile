.PHONY: dev test lint typecheck build up down seed install-precommit precommit

DEV_BACKEND=apps/backend
DEV_FRONTEND=apps/frontend

.dev-venv:
	poetry install >/dev/null 2>&1 || true

dev:
	pnpm -C $(DEV_FRONTEND) dev

test:
	pytest -q

lint:
	ruff check apps packages
	pnpm -C $(DEV_FRONTEND) lint

typecheck:
	mypy $(DEV_BACKEND)

build:
	pnpm -C $(DEV_FRONTEND) build

up:
	docker compose up -d

down:
	docker compose down

seed:
	python ops/seed.py

install-precommit:
	pre-commit install
	pre-commit install --hook-type commit-msg

precommit:
	pre-commit run --all-files
