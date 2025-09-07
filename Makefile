.PHONY: dev test lint typecheck build up down seed

DEV_BACKEND=apps/backend
DEV_FRONTEND=apps/frontend

.dev-venv:
	poetry install >/dev/null 2>&1 || true

dev:
	pnpm -C $(DEV_FRONTEND) dev

test:
	poetry run pytest -q

lint:
	poetry run ruff check apps packages

typecheck:
	poetry run mypy $(DEV_BACKEND)

build:
	pnpm -C $(DEV_FRONTEND) build

up:
	docker compose up -d

down:
	docker compose down

seed:
	python ops/seed.py
