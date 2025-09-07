.PHONY: dev test fmt lint typecheck build up down seed hooks

DEV_BACKEND=apps/backend
DEV_FRONTEND=apps/frontend

.dev-venv:
	poetry install >/dev/null 2>&1 || true

dev:
        pnpm -C $(DEV_FRONTEND) dev

fmt:
	pre-commit run --all-files

test:
        pytest -q

lint:
        ruff check apps packages
        pnpm -C $(DEV_FRONTEND) lint

typecheck:
        mypy $(DEV_BACKEND)
        pnpm -C $(DEV_FRONTEND) typecheck

build:
	pnpm -C $(DEV_FRONTEND) build

up:
	docker compose up -d

down:
	docker compose down

seed:
        python ops/seed.py

hooks:
        pre-commit install
        pre-commit install --hook-type commit-msg
