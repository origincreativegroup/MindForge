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
3. Set up pre-commit hooks: `make install-precommit`
4. Use `make dev` to run the frontend, `make test` for tests.

### Pre-commit Hooks
This repository uses pre-commit hooks for code quality:
- **ruff**: Python linting and formatting
- **eslint**: JavaScript/TypeScript linting  
- **prettier**: Code formatting
- **conventional-pre-commit**: Commit message linting

To install pre-commit hooks:
```bash
make install-precommit
```

To run pre-commit on all files:
```bash
make precommit
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License
[MIT](LICENSE)
