DEV_BACKEND=apps/backend
DEV_FRONTEND=apps/frontend

.dev-venv:
	poetry install >/dev/null 2>&1 || true

dev:

build:
	pnpm -C $(DEV_FRONTEND) build

up:
	docker compose up -d

down:
	docker compose down

seed:
