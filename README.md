# MindForge

MindForge is a monorepo for creative workflow intelligence.

## Structure
- `apps/backend` – FastAPI + Pydantic API
- `apps/frontend` – React + Vite + Tailwind client
- `packages/ai_core` – LLM orchestration, prompt libs, extraction
- `packages/integrations` – connectors for Jobber, Slack, Teams, Email and Drive
- `packages/ui` – shared React components (Mermaid, ReactFlow, Markov Explorer)
- `infra` – docker, devcontainer, Kubernetes and Terraform configs
- `ops` – runbooks, scripts, DB seeds, data tooling
- `docs` – product, architecture, API and security docs

## Getting Started
1. Install JS deps: `pnpm install`
2. Install Python deps: `poetry install`
3. Use `make dev` to run the frontend, `make test` for tests.

## Database

MindForge can persist data to Postgres when a connection string is provided.
Set `DATABASE_URL` (or Vercel's `POSTGRES_URL`) to point at your database. If
neither is set, the application falls back to a local `mindforge.db` SQLite
file for development.

```
export DATABASE_URL="$POSTGRES_URL"  # supplied by the Vercel/Supabase addon
```

## Vercel Storage

If you have connected Vercel Blob or Edge Config stores, expose their credentials
to the backend via environment variables:

```
export VERCEL_BLOB_RW_TOKEN="<token>"  # allows uploading to the Blob store
export VERCEL_EDGE_CONFIG_URL="<config url>"  # full URL including token
```

When `VERCEL_BLOB_RW_TOKEN` is set, uploaded files will automatically be stored
in the Vercel Blob store. `VERCEL_EDGE_CONFIG_URL` lets services fetch
configuration data from Edge Config.

## Docker

The backend can be run inside a container with Docker:

```bash
docker compose up --build
```

This starts the FastAPI app on port `8000` with live reloading. Edit the code
locally and the container will pick up changes automatically.

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License
[MIT](LICENSE)
