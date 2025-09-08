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
